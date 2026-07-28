from fastapi import FastAPI
from src.preflight.engine import run_preflight
from src.config.health_config import HEALTH_CHECKS

app = FastAPI()


@app.get("/")
def health():
   return {"Service":"Running"}


@app.get("/healthCheck")
def healthcheck():
    return run_preflight(HEALTH_CHECKS)
