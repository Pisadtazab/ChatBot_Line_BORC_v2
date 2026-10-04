from fastapi import APIRouter, HTTPException
from app.DB.database import delete_pdf_from_db,collection,db
from fastapi.responses import JSONResponse
import logging
import os
import re


router = APIRouter()
logger = logging.getLogger(__name__)

#ลบไฟล์ pdf  
@router.delete("/delete_file", response_class=JSONResponse)
def delete_file(pdf_name: str):
    try:
        normalized_name = pdf_name.replace("\\", "/")
        file = collection.find_one({"metadata.source": normalized_name})
        if not file:
            filename = os.path.basename(normalized_name)
            file = collection.find_one({"metadata.source": {"$regex": f"/{re.escape(filename)}$"}})

        if not file:
            raise HTTPException(status_code=404, detail=f"ไม่พบไฟล์ชื่อ '{pdf_name}'")

        # ดึง source จริงจาก DB ไปใช้ลบ (กรณี full path)
        actual_source = file["metadata"]["source"]
        delete_pdf_from_db(db, actual_source)
        
        return {"status": "success", "message": f"ลบไฟล์ '{pdf_name}' สำเร็จ"}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unable to delete PDF")
        raise HTTPException(status_code=500, detail="Unable to delete PDF")

