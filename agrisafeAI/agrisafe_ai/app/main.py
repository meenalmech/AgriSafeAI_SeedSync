from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import Base, engine
from .api import router

BASE = Path(__file__).resolve().parent.parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0", description="AI-assisted farm task safety decision support")
app.include_router(router)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE / "static" / "index.html")
