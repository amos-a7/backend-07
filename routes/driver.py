from fastapi import APIRouter, HTTPException
from database import SessionLocal
from sqlalchemy import text

router = APIRouter()

# 🔥 ASSIGN DRIVER
@router.post("/assign-driver/{pesanan_id}")
def assign_driver(pesanan_id: int):
    db = SessionLocal()

    try:
        # ✅ CEK PESANAN ADA
        pesanan = db.execute(
            text("SELECT driver_id FROM pesanan WHERE id=:id"),
            {"id": pesanan_id}
        ).fetchone()

        if not pesanan:
            raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")

        # ✅ CEK SUDAH ADA DRIVER ATAU BELUM
        if pesanan[0]:
            raise HTTPException(status_code=400, detail="Pesanan sudah punya driver")

        # 🔎 CARI DRIVER TERBAIK
        driver = db.execute(
            text("""
            SELECT * FROM driver
            WHERE status='available'
            ORDER BY rating DESC
            LIMIT 1
            """)
        ).fetchone()

        if not driver:
            raise HTTPException(status_code=404, detail="Tidak ada driver tersedia")

        driver_id = driver[0]

        # 📝 UPDATE PESANAN
        db.execute(
            text("""
            UPDATE pesanan
            SET driver_id=:driver_id, status='driver_ditugaskan'
            WHERE id=:id
            """),
            {"driver_id": driver_id, "id": pesanan_id}
        )

        # 🚗 UPDATE DRIVER JADI BUSY
        db.execute(
            text("""
            UPDATE driver
            SET status='busy'
            WHERE id=:id
            """),
            {"id": driver_id}
        )

        db.commit()

        return {
            "message": "Driver berhasil ditugaskan",
            "driver_id": driver_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


#  LIHAT DRIVER AVAILABLE
@router.get("/driver/available")
def get_driver_available():
    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT * FROM driver WHERE status='available'")
        ).fetchall()

        return [dict(r._mapping) for r in result]

    finally:
        db.close()


#  TAMBAH DRIVER
@router.post("/driver")
def tambah_driver(nama: str, kendaraan: str, plat: str):
    db = SessionLocal()

    try:
        db.execute(
            text("""
            INSERT INTO driver (nama, kendaraan, no_plat, status, rating)
            VALUES (:nama, :kendaraan, :plat, 'available', 5)
            """),
            {
                "nama": nama,
                "kendaraan": kendaraan,
                "plat": plat
            }
        )

        db.commit()

        return {"message": "Driver berhasil ditambahkan"}

    finally:
        db.close()