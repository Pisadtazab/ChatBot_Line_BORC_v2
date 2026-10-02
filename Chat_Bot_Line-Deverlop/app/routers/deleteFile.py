from fastapi import APIRouter, HTTPException
from app.DB.database import delete_pdf_from_db,collection,db
from fastapi.responses import JSONResponse
import os
import re


router = APIRouter()

#ลบไฟล์ pdf  
@router.delete("/delete_file", response_class=JSONResponse)
def delete_file(pdf_name: str):
    try:
        # print(f"[DELETE] pdf_name received: '{pdf_name}'")
        
        # all_sources = db["employees_profiles"].distinct("metadata.source")
        
        # print(f"[DEBUG] all sources in DB: {all_sources}")

        # count = db["employees_profiles"].count_documents({})
        # print(f"[DEBUG] total documents: {count}")

        # # ดู document ตัวแรกดิบๆ
        # sample = db["employees_profiles"].find_one()
        # print(f"[DEBUG] sample document: {sample}")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

