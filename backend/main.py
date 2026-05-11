from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from backend.models import engine
from backend.routers import auth, menu, orders

app = FastAPI()


@app.on_event("startup")
def startup():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as exc:
        print(f"DB startup check failed: {exc}")
        raise
    except Exception as exc:
        print(f"DB startup failed: {exc}")
        raise


@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


app.include_router(menu.router, prefix="/api", tags=["Menu"])
app.include_router(orders.router, prefix="/api", tags=["Orders"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
