from fastapi import FastAPI, HTTPException
from database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from routes import pesanan
from routes import driver
from routes import pengiriman
from routes import pelanggan

app = FastAPI()
app.include_router(pesanan.router)
app.include_router(driver.router)
app.include_router(pengiriman.router)
app.include_router(pelanggan.router)


@app.get("/")
def root():
    return {"message": "yeahhh"}


@app.get("/test-db")
def test_db():
    try:
        conn = engine.connect()
        return {"message": "Database connected!"}
    except Exception as e:
        return {"error": str(e)}
    
    
