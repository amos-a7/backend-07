from fastapi import FastAPI, HTTPException
from database import engine, SessionLocal
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from routes import pesanan

app = FastAPI()
app.include_router(pesanan.router)


class Pelanggan(BaseModel):
    nama: str
    email: str
    no_hp: str
    alamat: str

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
    
    
@app.get("/pelanggan")
def get_pelanggan():
    db = SessionLocal()
    result = db.execute(text("SELECT * FROM pelanggan"))
    
    columns = result.keys()  # ambil nama kolom
    data = []

    for row in result.fetchall():
        data.append(dict(zip(columns, row)))

    db.close()
    return {"data": data}

@app.post("/pelanggan")
def tambah_pelanggan(data: Pelanggan):
    db = SessionLocal()
    try:
        db.execute(
            text("""
            INSERT INTO pelanggan (nama, email, no_hp, alamat)
            VALUES (:nama, :email, :no_hp, :alamat)
            """),
            data.dict()
        )
        db.commit()
        return {"message": "Pelanggan berhasil ditambah"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
        

@app.put("/pelanggan/{id}")
def update_pelanggan(id: int, data: Pelanggan):
    db = SessionLocal()
    try:
        db.execute(
            text("""
            UPDATE pelanggan
            SET nama=:nama, email=:email, no_hp=:no_hp, alamat=:alamat
            WHERE id=:id
            """),
            {"id": id, **data.dict()}
        )
        db.commit()
        return {"message": "Pelanggan berhasil diupdate"}

    finally:
        db.close()

@app.delete("/pelanggan/{id}")
def delete_pelanggan(id: int):
    db = SessionLocal()
    try:
        db.execute(
            text("DELETE FROM pelanggan WHERE id=:id"),
            {"id": id}
        )
        db.commit()
        return {"message": "Pelanggan berhasil dihapus"}

    finally:
        db.close()