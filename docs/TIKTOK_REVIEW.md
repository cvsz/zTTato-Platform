# TikTok App Review Evidence

## Portal configuration
- Web/Desktop URL: https://zttato.zeaz.dev/
- Redirect URI: https://zttato.zeaz.dev/tiktok/callback
- Requested scopes: user.info.basic, video.upload, video.publish
- Products implemented by this web app: Login Kit and Content Posting API.
- Share Kit is not implemented by this repository; remove it from the app configuration unless a separate supported client demonstrates it.

## Required reviewer recording
Record a real TikTok Sandbox session, not /review-preview:
1. Open the live HTTPS app and show favicon/app icon.
2. Open Privacy Policy and Terms of Service from the same origin.
3. Start Login Kit authorization and show the TikTok consent surface.
4. Return through /tiktok/callback and show connected state.
5. Upload a representative MP4.
6. Demonstrate Upload as Draft (video.upload), including the resulting TikTok inbox continuation.
7. Query creator info immediately before Direct Post.
8. Show only current privacy options returned by TikTok and creator-disabled controls.
9. Explicitly confirm Direct Post (video.publish), then show status polling/result.
10. Disconnect and demonstrate deletion/control surfaces.

Never expose Client Secret, access tokens, refresh tokens, upload URLs or production credentials in the recording.

## Current external constraints
TikTok states that unaudited clients' Direct Post content is restricted to private viewing. Keep TIKTOK_APP_AUDITED=false until the client has actually passed the applicable audit. Do not describe the app as TikTok-approved before confirmation.

## Real creator UI
Use /dashboard to perform the actual authenticated flow. /review-preview remains a deliberately non-posting mockup. The dashboard queries creator choices and requires a separate explicit consent checkbox. For unaudited clients only SELF_ONLY is selectable. Review commercial disclosure and AI-generated content controls against latest TikTok UX requirements and evidence before resubmission.
