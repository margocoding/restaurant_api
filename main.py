from fastapi import FastAPI
from app.routers import menu, orders

app = FastAPI(title="Restaurant API")

app.include_router(menu.router, prefix="/api", tags=["Menu"])
app.include_router(orders.router, prefix="/api", tags=["Orders"])


@app.get("/")
async def root():
    return {"message": "Restaurant API"}