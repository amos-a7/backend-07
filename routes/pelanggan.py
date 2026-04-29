from fastapi import APIRouter, HTTPException
from database import SessionLocal
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

router = APIRouter()


class Pelanggan(BaseModel):
    nama: str
    email: str
    no_hp: str
    alamat: str

@router.get("/pelanggan")
def get_pelanggan():
    db = SessionLocal()
    result = db.execute(text("SELECT * FROM pelanggan"))
    
    columns = result.keys()  # ambil nama kolom
    data = []

    for row in result.fetchall():
        data.append(dict(zip(columns, row)))

    db.close()
    return {"data": data}

@router.post("/pelanggan")
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
        

@router.put("/pelanggan/{id}")
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

@router.delete("/pelanggan/{id}")
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