import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
from .config import get_settings

_firebase_app: firebase_admin.App | None = None
_firebase_configured = False

DEV_TOKEN = "dev-demo-token"
DEV_CLAIMS = {
    "uid": "demo-user-001",
    "email": "demo@travelai.dev",
    "name": "Demo Traveler",
    "picture": None,
}


def _is_firebase_configured(settings) -> bool:
    return bool(
        settings.FIREBASE_PROJECT_ID
        and settings.FIREBASE_CLIENT_EMAIL
        and settings.FIREBASE_PRIVATE_KEY
        and settings.FIREBASE_CLIENT_EMAIL != "your_firebase_client_email"
        and settings.FIREBASE_PRIVATE_KEY != "your_firebase_private_key"
    )


def initialize_firebase_app() -> None:
    global _firebase_app, _firebase_configured
    if _firebase_app is not None:
        return
    settings = get_settings()
    if _is_firebase_configured(settings):
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        _firebase_app = firebase_admin.initialize_app(cred)
        _firebase_configured = True
    else:
        # Firebase not configured — dev mode only, no real token verification
        _firebase_configured = False


def verify_firebase_token(token: str) -> dict:
    settings = get_settings()

    # Dev mode: accept the demo token without Firebase
    if settings.DEV_MODE or not _firebase_configured:
        if token == DEV_TOKEN or not _firebase_configured:
            return DEV_CLAIMS
        # Still allow any token in DEV_MODE — use token as uid
        return {"uid": token[:64], "email": f"{token[:8]}@dev.local", "name": "Dev User", "picture": None}

    try:
        decoded = auth.verify_id_token(token, check_revoked=True)
        return decoded
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
