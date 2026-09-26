"""Official TikTok OAuth and Content Posting API transport. Never log tokens or upload URLs."""

import re
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from app.config import Settings


# TikTok Media Transfer Guide: 64 MB maximum for a regular chunk, 128 MB
# for the final merged chunk, 1,000 chunks maximum, 4 GB total.
MAX_VIDEO_SIZE = 4_000_000_000
SINGLE_UPLOAD_LIMIT = 64_000_000
MULTIPART_CHUNK_SIZE = 32_000_000


def plan_video_chunks(size: int) -> tuple[int, int]:
    """Return (declared chunk_size, total_chunk_count) following TikTok's floor rule."""
    if size < 1 or size > MAX_VIDEO_SIZE:
        raise HTTPException(422, "TikTok video size must be between 1 byte and 4 GB")
    if size <= SINGLE_UPLOAD_LIMIT:
        return size, 1
    count = size // MULTIPART_CHUNK_SIZE
    if count > 1000:
        raise HTTPException(422, "Too many TikTok upload chunks")
    return MULTIPART_CHUNK_SIZE, count


class TikTokClient:
    API = "https://open.tiktokapis.com"
    AUTHORIZE = "https://www.tiktok.com/v2/auth/authorize/"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.transport = transport

    async def _request(self, method: str, url: str, *, token: str | None = None, form=None, data=None) -> dict:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(60.0), follow_redirects=False, trust_env=False, transport=self.transport
            ) as client:
                response = await client.request(method, url, headers=headers, data=form, json=data)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise HTTPException(502, "TikTok service temporarily unavailable") from exc
        if not isinstance(payload, dict):
            raise HTTPException(502, "Unexpected TikTok response")
        error = payload.get("error")
        if isinstance(error, dict) and error.get("code") not in (None, "", "ok"):
            raise HTTPException(502, "TikTok rejected request: " + str(error.get("code", "unknown"))[:70])
        if isinstance(error, str) and error:
            raise HTTPException(502, "TikTok OAuth rejected request")
        return payload

    async def exchange(self, code: str) -> dict:
        s = self.settings
        return await self._request(
            "POST",
            self.API + "/v2/oauth/token/",
            form={
                "client_key": s.client_key,
                "client_secret": s.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": s.redirect_uri,
            },
        )

    async def refresh(self, refresh_token: str) -> dict:
        s = self.settings
        return await self._request(
            "POST",
            self.API + "/v2/oauth/token/",
            form={
                "client_key": s.client_key,
                "client_secret": s.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

    async def revoke(self, access_token: str) -> None:
        s = self.settings
        await self._request(
            "POST",
            self.API + "/v2/oauth/revoke/",
            form={
                "client_key": s.client_key,
                "client_secret": s.client_secret,
                "token": access_token,
            },
        )

    async def user_info(self, access_token: str) -> dict:
        """Fetch only the basic profile fields authorized by user.info.basic."""
        payload = await self._request(
            "GET",
            self.API + "/v2/user/info/?fields=open_id,avatar_url,display_name",
            token=access_token,
        )
        data = payload.get("data")
        user = data.get("user") if isinstance(data, dict) else None
        if not isinstance(user, dict):
            raise HTTPException(502, "TikTok returned invalid basic profile data")
        return user

    async def creator_info(self, access_token: str) -> dict:
        payload = await self._request(
            "POST", self.API + "/v2/post/publish/creator_info/query/", token=access_token, data={}
        )
        return payload.get("data", {})

    async def init_video(
        self,
        access_token: str,
        *,
        mode: str,
        media_size: int,
        caption: str,
        privacy: str | None,
        disable_comment: bool,
        disable_duet: bool,
        disable_stitch: bool,
        brand_content_toggle: bool = False,
        brand_organic_toggle: bool = False,
        is_aigc: bool = False,
    ) -> tuple[str, str]:
        if mode == "direct":
            endpoint = "/v2/post/publish/video/init/"
            post_info = {
                "title": caption,
                "privacy_level": privacy,
                "disable_comment": disable_comment,
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
                "brand_content_toggle": brand_content_toggle,
                "brand_organic_toggle": brand_organic_toggle,
                "is_aigc": is_aigc,
            }
            request = {"post_info": post_info}
        elif mode == "draft":
            endpoint, request = "/v2/post/publish/inbox/video/init/", {}
        else:
            raise HTTPException(422, "Unsupported mode")
        chunk_size, chunk_count = plan_video_chunks(media_size)
        request["source_info"] = {
            "source": "FILE_UPLOAD",
            "video_size": media_size,
            "chunk_size": chunk_size,
            "total_chunk_count": chunk_count,
        }
        payload = await self._request("POST", self.API + endpoint, token=access_token, data=request)
        result = payload.get("data", {})
        publish_id, upload_url = result.get("publish_id"), result.get("upload_url")
        if not isinstance(publish_id, str) or not isinstance(upload_url, str):
            raise HTTPException(502, "TikTok did not provide upload details")
        self.validate_upload_url(upload_url)
        return publish_id, upload_url

    @staticmethod
    def validate_upload_url(url: str) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        official_upload_host = host == "open-upload.tiktokapis.com" or bool(
            re.fullmatch(r"upload\.[a-z0-9-]{2,16}\.tiktokapis\.com", host)
        )
        try:
            port = parsed.port
        except ValueError as exc:
            raise HTTPException(502, "TikTok supplied an invalid upload URL") from exc
        if (
            parsed.scheme != "https"
            or not official_upload_host
            or port not in (None, 443)
            or parsed.username
            or parsed.password
            or parsed.fragment
            or parsed.path not in ("/video/", "/upload/")
            or not parsed.query
        ):
            raise HTTPException(502, "TikTok supplied an unexpected upload destination")

    async def upload_video(self, url: str, path: str, size: int) -> None:
        self.validate_upload_url(url)
        chunk_size, chunk_count = plan_video_chunks(size)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(180.0), follow_redirects=False, trust_env=False, transport=self.transport
        ) as client:
            with open(path, "rb") as stream:
                for index in range(chunk_count):
                    offset = stream.tell()
                    # Merge the trailing remainder into the last chunk, as required by TikTok.
                    length = size - offset if index == chunk_count - 1 else chunk_size

                    async def content():
                        remaining = length
                        while remaining:
                            part = stream.read(min(1024 * 1024, remaining))
                            if not part:
                                raise HTTPException(502, "Media file changed during TikTok transfer")
                            remaining -= len(part)
                            yield part

                    try:
                        response = await client.put(
                            url,
                            headers={
                                "Content-Type": "video/mp4",
                                "Content-Length": str(length),
                                "Content-Range": f"bytes {offset}-{offset + length - 1}/{size}",
                            },
                            content=content(),
                        )
                        # 206 confirms a nonfinal part; 201 means all parts were received.
                        expected = 201 if index == chunk_count - 1 else 206
                        if response.status_code != expected:
                            response.raise_for_status()
                            raise HTTPException(502, "Unexpected TikTok chunk acknowledgement; reconcile status")
                    except httpx.HTTPError as exc:
                        # Never restart from byte zero after an ambiguous provider response.
                        raise HTTPException(502, "TikTok transfer is uncertain; reconcile before retry") from exc

    async def status(self, access_token: str, publish_id: str) -> dict:
        payload = await self._request(
            "POST", self.API + "/v2/post/publish/status/fetch/", token=access_token, data={"publish_id": publish_id}
        )
        return payload.get("data", {})
