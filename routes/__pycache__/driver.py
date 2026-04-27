from fastapi import APIRouter, HTTPException
from database import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.post("/assign-driver/{pesanan_id}")
def assign_driver(pesanan_id: int):
    db = SessionLocal()

    try:
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

        # update pesanan
        db.execute(
            text("""
            UPDATE pesanan 
            SET driver_id=:driver_id, status='driver_ditugaskan'
            WHERE id=:id
            """),
            {"driver_id": driver.id, "id": pesanan_id}
        )

        # insert pengiriman
        db.execute(
            text("""
            INSERT INTO pengiriman 
            (pesanan_id, driver_id, waktu_ditugaskan, status_pengiriman)
            VALUES (:pesanan_id, :driver_id, NOW(), 'menuju_restoran')
            """),
            {
                "pesanan_id": pesanan_id,
                "driver_id": driver.id
            }
        )

        # update driver jadi busy
        db.execute(
            text("UPDATE driver SET status='busy' WHERE id=:id"),
            {"id": driver.id}
        )

        db.commit()

        return {
            "message": "Driver berhasil ditugaskan",
            "driver_id": driver.id
        }

    finally:
        db.close()