"""Official TikTok OAuth and Content Posting API transport. Never log tokens or upload URLs."""
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from app.config import Settings


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
                timeout=httpx.Timeout(60.0), follow_redirects=False,
                trust_env=False, transport=self.transport
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
        return await self._request("POST", self.API + "/v2/oauth/token/", form={
            "client_key": s.client_key, "client_secret": s.client_secret, "code": code,
            "grant_type": "authorization_code", "redirect_uri": s.redirect_uri,
        })

    async def refresh(self, refresh_token: str) -> dict:
        s = self.settings
        return await self._request("POST", self.API + "/v2/oauth/token/", form={
            "client_key": s.client_key, "client_secret": s.client_secret,
            "grant_type": "refresh_token", "refresh_token": refresh_token,
        })

    async def revoke(self, access_token: str) -> None:
        s = self.settings
        await self._request("POST", self.API + "/v2/oauth/revoke/", form={
            "client_key": s.client_key, "client_secret": s.client_secret, "token": access_token,
        })

    async def creator_info(self, access_token: str) -> dict:
        payload = await self._request(
            "POST", self.API + "/v2/post/publish/creator_info/query/", token=access_token, data={}
        )
        return payload.get("data", {})

    async def init_video(
        self, access_token: str, *, mode: str, media_size: int,
        caption: str, privacy: str | None, disable_comment: bool,
        disable_duet: bool, disable_stitch: bool
    ) -> tuple[str, str]:
        if mode == "direct":
            endpoint = "/v2/post/publish/video/init/"
            post_info = {
                "title": caption, "privacy_level": privacy,
                "disable_comment": disable_comment, "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
            }
            request = {"post_info": post_info}
        elif mode == "draft":
            endpoint, request = "/v2/post/publish/inbox/video/init/", {}
        else:
            raise HTTPException(422, "Unsupported mode")
        request["source_info"] = {
            "source": "FILE_UPLOAD", "video_size": media_size,
            "chunk_size": media_size, "total_chunk_count": 1,
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
        if (
            parsed.scheme != "https" or parsed.hostname != "open-upload.tiktokapis.com"
            or parsed.port not in (None, 443) or parsed.username or parsed.password
        ):
            raise HTTPException(502, "TikTok supplied an unexpected upload destination")

    async def upload_video(self, url: str, path: str, size: int) -> None:
        self.validate_upload_url(url)

        async def content():
            with open(path, "rb") as stream:
                while part := stream.read(1024 * 1024):
                    yield part

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(180.0), follow_redirects=False,
                trust_env=False, transport=self.transport
            ) as client:
                result = await client.put(
                    url,
                    headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}"},
                    content=content(),
                )
                result.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(502, "TikTok upload failed; status must be reconciled before retry") from exc

    async def status(self, access_token: str, publish_id: str) -> dict:
        payload = await self._request(
            "POST", self.API + "/v2/post/publish/status/fetch/",
            token=access_token, data={"publish_id": publish_id}
        )
        return payload.get("data", {})
