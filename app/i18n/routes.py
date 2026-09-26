"""i18n API routes for serving translation files."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/i18n", tags=["i18n"])

I18N_DIR = Path(__file__).parent
SUPPORTED_LOCALES = ["en", "th", "zh", "ja", "ko", "vi"]


@router.get("/{locale}.json")
async def get_translations(locale: str):
    """Get translation file for a specific locale."""
    if locale not in ["en", "th", "zh", "ja", "ko", "vi"]:
        raise HTTPException(status_code=404, detail="Locale not supported")

    file_path = Path(__file__).parent / f"{locale}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Translation file not found")

    return FileResponse(
        file_path,
        media_type="application/json",
        headers={"Cache-Control": "public, max-age=86400"},  # Cache for 24 hours
    )


@router.get("/locales")
async def get_supported_locales():
    """Get list of supported locales."""
    return {"supported": ["en", "th", "zh", "ja", "ko", "vi"], "default": "en"}
