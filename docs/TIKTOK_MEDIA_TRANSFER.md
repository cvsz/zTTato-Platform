# TikTok Media Transfer Contract — 2026-09-25

Official reference: https://developers.tiktok.com/docs/en/content-posting-api-media-transfer-guide
Direct Post reference: https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post

## Implemented FILE_UPLOAD flow

- Draft: POST `/v2/post/publish/inbox/video/init/` with the `video.upload` scope. Creators must finish the post from their TikTok inbox.
- Direct Post: query fresh creator info, honor allowed privacy and disabled controls, obtain explicit consent, then POST `/v2/post/publish/video/init/` with `video.publish`.
- TikTok returns a `publish_id` and a short-lived `upload_url`. Treat both as sensitive operational identifiers; never log the upload URL or its query.
- Only HTTPS TikTok upload endpoints are permitted: `open-upload.tiktokapis.com` and regional `upload.<region>.tiktokapis.com`, with official `/video/` or `/upload/` paths and a query. HTTP redirects are disabled.
- For uploads of at most 64,000,000 bytes, send one complete PUT with `chunk_size=video_size` and `total_chunk_count=1`.
- For larger uploads, declare a 32,000,000-byte chunk size and `floor(video_size / chunk_size)` chunks. Merge all remaining bytes into the final chunk; send every chunk sequentially.
- Send the full returned URL, including its query, on each PUT. Use `Content-Type: video/mp4`, exact `Content-Length`, and `Content-Range: bytes START-END/TOTAL`.
- Require HTTP 206 for each non-final chunk and HTTP 201 for the last chunk. If a response is ambiguous or inconsistent, stop and reconcile using `/v2/post/publish/status/fetch/`; never blindly initialize a duplicate post.
- TikTok's published transfer limits are 5–64 MB per regular chunk, final chunk up to 128 MB, 1–1000 chunks, and 4 GB per video. Supported video format and creator-duration restrictions also apply.

## Important current application scope

The zTTato web application currently accepts local MP4 files up to **64 MiB** by design. Files between 64,000,001 and 67,108,864 bytes use the new multi-chunk transfer path. The 4 GB number is the TikTok API upper bound, **not** the supported web-app upload size. Larger uploads, resumability, background workers, managed object storage, media inspection, and durable upload reconciliation require separate architecture and resource-limit work.

The browser application does not expose `PULL_FROM_URL`. That mode requires a verified TikTok URL property, a publicly available HTTPS asset under the owned property, no redirects, an uninterrupted download window of up to one hour, and status reconciliation. Do not enable it until those requirements are tested against the exact developer application.

## Verification matrix

| Case | Test | Required remote evidence |
| --- | --- | --- |
| Whole-file size below 5 MB | Unit test of plan and MockTransport PUT | Real Sandbox upload |
| Exactly 64 MB | Unit test of declared single-chunk plan | Real Sandbox upload |
| Above 64 MB / remainder | Chunk plan + streamed ranges and 206→201 tests | Real Sandbox upload |
| TikTok regional destination | Allowlist regression | Confirm actual regional URLs from real Sandbox |
| Untrusted upload destination | SSRF-focused validation tests | Security review |
| Unexpected final 206 / network timeout | Fail closed and reconcile | Retry/timeout recovery drill |
| Draft inbox continuation | Existing app implementation | Reviewer recording from real TikTok account |
| Direct Post creator consent | Existing app implementation | Real Sandbox user-consent recording |
| PULL_FROM_URL | NOT IMPLEMENTED | Verified property and controlled E2E test |

MockTransport tests verify the local HTTP protocol implementation; they do **not** demonstrate successful TikTok upload or production approval.

## Production release prerequisites

Complete CI; real Sandbox recording of Login Kit, Direct Post and Draft; confirm actual upload host/domain and URL property; verify public legal pages and operator identity; execute isolated PostgreSQL restore, encrypted-token-key recovery, deployment rollback and observability evidence. See `docs/PRODUCTION_GATES.md`.

Never paste a real TikTok upload URL, token or secret into an issue, CI log, documentation or screenshot.
