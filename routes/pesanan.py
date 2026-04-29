from fastapi import APIRouter, HTTPException
from database import SessionLocal
from sqlalchemy import text
from pydantic import BaseModel
from typing import List


class Item(BaseModel):
    menu_id: int
    qty: int

class Pesanan(BaseModel):
    pelanggan_id: int
    restoran_id: int
    alamat_pengiriman: str
    catatan: str
    items: List[Item]
    
router = APIRouter()

@router.post("/pesanan")
def buat_pesanan(data: Pesanan):
    db = SessionLocal()

    try:
        # 1. insert pesanan
        result = db.execute(
            text("""
            INSERT INTO pesanan 
            (pelanggan_id, restoran_id, status, total_harga, alamat_pengiriman, catatan)
            VALUES (:pelanggan_id, :restoran_id, 'menunggu_konfirmasi', 0, :alamat, :catatan)
            """),
            {
                "pelanggan_id": data.pelanggan_id,
                "restoran_id": data.restoran_id,
                "alamat": data.alamat_pengiriman,
                "catatan": data.catatan
            }
        )

        pesanan_id = result.lastrowid
        total = 0

        # 2. detail pesanan
        for item in data.items:
            menu_id = item.menu_id
            qty = item.qty

            menu = db.execute(
                text("SELECT harga FROM menu WHERE id=:id"),
                {"id": menu_id}
            ).fetchone()

            if not menu:
                raise HTTPException(status_code=404, detail=f"Menu {menu_id} tidak ditemukan")

            harga = menu[0]
            subtotal = harga * qty
            total += subtotal

            db.execute(
                text("""
                INSERT INTO detail_pesanan 
                (pesanan_id, menu_id, qty, harga_saat_pesan, subtotal)
                VALUES (:pesanan_id, :menu_id, :qty, :harga, :subtotal)
                """),
                {
                    "pesanan_id": pesanan_id,
                    "menu_id": menu_id,
                    "qty": qty,
                    "harga": harga,
                    "subtotal": subtotal
                }
            )

        # 3. update total
        db.execute(
            text("UPDATE pesanan SET total_harga=:total WHERE id=:id"),
            {"total": total, "id": pesanan_id}
        )

        db.commit()

        return {
            "message": "Pesanan berhasil dibuat",
            "pesanan_id": pesanan_id,
            "total": total
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
        

@router.get("/pesanan/{id}")
def get_pesanan(id: int):
    db = SessionLocal()

    try:
        pesanan = db.execute(
            text("SELECT * FROM pesanan WHERE id=:id"),
            {"id": id}
        ).fetchone()

        if not pesanan:
            raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")

        detail = db.execute(
            text("""
            SELECT dp.*, m.nama 
            FROM detail_pesanan dp
            JOIN menu m ON dp.menu_id = m.id
            WHERE dp.pesanan_id = :id
            """),
            {"id": id}
        ).fetchall()

        return {
            "pesanan": dict(pesanan._mapping),
            "detail": [dict(d._mapping) for d in detail]
        }

    finally:
        db.close()
        

@router.get("/tracking/{id}")
def tracking_pesanan(id: int):
    db = SessionLocal()

    try:
        # 1. pesanan
        pesanan = db.execute(
            text("""
            SELECT p.*, pl.nama AS pelanggan_nama, r.nama_restoran
            FROM pesanan p
            JOIN pelanggan pl ON p.pelanggan_id = pl.id
            JOIN restoran r ON p.restoran_id = r.id
            WHERE p.id = :id
            """),
            {"id": id}
        ).fetchone()

        if not pesanan:
            raise HTTPException(404, "Pesanan tidak ditemukan")

        # 2. detail menu
        detail = db.execute(
            text("""
            SELECT m.nama, dp.qty, dp.subtotal
            FROM detail_pesanan dp
            JOIN menu m ON dp.menu_id = m.id
            WHERE dp.pesanan_id = :id
            """),
            {"id": id}
        ).fetchall()

        # 3. driver + pengiriman
        pengiriman = db.execute(
            text("""
            SELECT d.nama AS driver_nama, d.no_hp,
                   pg.status_pengiriman,
                   pg.waktu_ditugaskan,
                   pg.waktu_pickup,
                   pg.waktu_sampai
            FROM pengiriman pg
            JOIN driver d ON pg.driver_id = d.id
            WHERE pg.pesanan_id = :id
            """),
            {"id": id}
        ).fetchone()

        return {
            "pesanan": dict(pesanan._mapping),
            "menu": [dict(d._mapping) for d in detail],
            "pengiriman": dict(pengiriman._mapping) if pengiriman else None
        }

    finally:
        db.close()
        
@router.get("/pesanan")
def get_pesanan_by_pelanggan(pelanggan_id: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
            SELECT id, restoran_id, status, total_harga, created_at
            FROM pesanan
            WHERE pelanggan_id = :pelanggan_id
            ORDER BY created_at DESC
            """),
            {"pelanggan_id": pelanggan_id}
        ).fetchall()

        data = [dict(r._mapping) for r in result]

        return {
            "pelanggan_id": pelanggan_id,
            "total_pesanan": len(data),
            "data": data
        }

    finally:
        db.close()