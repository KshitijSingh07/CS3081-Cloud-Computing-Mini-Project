import json
import os
import threading
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from model_runner import ModelRunner

app = FastAPI(title="CS3081 Command Parser", version="1.0.0")
runner = ModelRunner()
ready = False
POD_NAME = os.getenv("POD_NAME", "local")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")

class ParseBody(BaseModel):
    text: str = Field(min_length=1, max_length=500)

from validation import validate_model_text as validate

def _load_model():
    global ready
    try:
        runner.load()
        ready = True
    except Exception:
        # Keep readiness false; container logs preserve the underlying traceback.
        import logging
        logging.exception("model download/load failed")

@app.on_event("startup")
def startup():
    threading.Thread(target=_load_model, daemon=True).start()

@app.get("/healthz")
def healthz():
    return {"status": "alive"}

@app.get("/readyz")
def readyz():
    if not ready:
        raise HTTPException(status_code=503, detail="model_not_loaded")
    return {"status": "ready"}

@app.post("/parse")
def parse(body: ParseBody, response: Response):
    if not ready:
        raise HTTPException(status_code=503, detail="model_not_ready")
    raw = "not json" if os.getenv("FAULT_INJECT", "0") == "1" else runner.predict(
        body.text, int(os.getenv("MAX_NEW_TOKENS", "96"))
    )
    try:
        result = validate(raw)
    except (ValueError, json.JSONDecodeError):
        return JSONResponse(status_code=500, content={"error": "invalid_model_output"})
    response.headers["X-Model-Version"] = MODEL_VERSION
    response.headers["X-Served-By"] = POD_NAME
    return result
