from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from pathlib import Path
from .api.routes import router as api_router
from .core.config import get_settings
from .db.session import SessionLocal
from .core.expiry import expire_stale_donations
import threading
import time

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(api_router)

# Allow browser clients during MVP
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Serve minimal static UI at /ui
root_dir = Path(__file__).resolve().parents[2]
static_dir = root_dir / "frontend"
if static_dir.exists():
	app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

@app.get("/health")
def health():
	return {"status": "ok"}


def _expiry_loop(interval: int):
	while True:
		try:
			db = SessionLocal()
			updated = expire_stale_donations(db)
			db.commit()
		except Exception:
			pass
		finally:
			try:
				db.close()
			except Exception:
				pass
		time.sleep(interval)


@app.on_event("startup")
def start_background_tasks():
	thread = threading.Thread(target=_expiry_loop, args=(settings.expiry_interval_seconds,), daemon=True)
	thread.start()
