
import logging

from pydantic import BaseModel
from fastapi import APIRouter,HTTPException
from gridfs import GridFS
from fastapi.responses import RedirectResponse, StreamingResponse
from bson import ObjectId


from app.DB.database import collection,db

router = APIRouter()
logger = logging.getLogger(__name__)

# Model สำหรับแสดงข้อมูลในฐานข้อมูล
class FileData(BaseModel):
    file_name: str
    file_id: str

@router.get("/files", response_model=list[FileData])
def get_files():
    """
    ดึงข้อมูลไฟล์ทั้งหมดจาก MongoDB
    """
    try:
        files = collection.aggregate([
            {"$match": {"metadata.source": {"$exists": True}}},
            {"$sort": {"metadata.type": 1}},
            {"$group": {"_id": "$metadata.source", "file_id": {"$first": "$_id"}}},
            {"$sort": {"_id": 1}},
        ])
        return [{"file_name": file["_id"], "file_id": str(file["file_id"])} for file in files]
    except Exception:
        logger.exception("Unable to list PDF files")
        raise HTTPException(status_code=500, detail="Unable to list PDF files")


fs = GridFS(db)

# ค้นหารูปภาพ
@router.get("/image/{file_id}")
def get_image(file_id: str):
    """ เทสดึงรูปภาพ """
    try:
        oid = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")

    image = collection.find_one({"_id": oid, "metadata.type": "image"})
    if image and image.get("metadata", {}).get("image_url"):
        return RedirectResponse(image["metadata"]["image_url"])

    if not fs.exists(oid):
        raise HTTPException(status_code=404, detail="Image not found")

    grid_out = fs.get(oid)

    return StreamingResponse(
        grid_out,
        media_type=grid_out.content_type or "image/jpeg",
    )

