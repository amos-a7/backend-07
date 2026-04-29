from fastapi import APIRouter, HTTPException
from database import SessionLocal
from sqlalchemy import text


router = APIRouter()

# assign driver → sekaligus buat pengiriman
@router.post("/pengiriman/{pesanan_id}")
def mulai_pengiriman(pesanan_id: int):
    db = SessionLocal()

    try:
        pesanan = db.execute(
            text("SELECT driver_id FROM pesanan WHERE id=:id"),
            {"id": pesanan_id}
        ).fetchone()

        if not pesanan or not pesanan[0]:
            raise HTTPException(status_code=400, detail="Pesanan belum ada driver")

        driver_id = pesanan[0]

        db.execute(
            text("""
            INSERT INTO pengiriman 
            (pesanan_id, driver_id, waktu_ditugaskan, status_pengiriman)
            VALUES (:pesanan_id, :driver_id, NOW(), 'menuju_restoran')
            """),
            {"pesanan_id": pesanan_id, "driver_id": driver_id}
        )

        db.commit()

        return {"message": "Pengiriman dimulai"}

    finally:
        db.close()


# update status pengiriman
@router.put("/pengiriman/{pesanan_id}/status")
def update_status(pesanan_id: int, status: str):
    db = SessionLocal()

    try:
        # update status pengiriman
        db.execute(
            text("""
            UPDATE pengiriman
            SET status_pengiriman=:status
            WHERE pesanan_id=:id
            """),
            {"status": status, "id": pesanan_id}
        )

        #  kalau selesai → driver balik available
        if status == "selesai":
            driver = db.execute(
                text("SELECT driver_id FROM pengiriman WHERE pesanan_id=:id"),
                {"id": pesanan_id}
            ).fetchone()

            if driver:
                db.execute(
                    text("""
                    UPDATE driver
                    SET status='available'
                    WHERE id=:id
                    """),
                    {"id": driver[0]}
                )

        db.commit()

        return {"message": "Status pengiriman diupdate"}

    finally:
        db.close()
        

