from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv(override=True)


# MongoDB configuration MONGO_URI
mogo_uri = os.getenv("MONGO_URI")
client = MongoClient(mogo_uri )

# Name entity db
db = client["employee_research_db_V2"]
collection = db["employees_profiles"]  

# def get_db():
#      # return collection ตรงๆ เลย ไม่ต้องสร้าง function แยก
#     return db


def delete_pdf_from_db(db, pdf_name: str):
    """ ฟังก์ชั่นการจัดการลบไฟล์ pdf ทั้งข้อความและรูปภาพ """
    any_doc = collection.find_one({"metadata.source": pdf_name})
    if not any_doc:
        raise ValueError(f"ไม่พบไฟล์ '{pdf_name}' ใน database")

    actual_source = any_doc["metadata"]["source"]

    # ลบ document ทั้งหมด (ทั้ง text และ image) ออกจาก employees_profiles
    db["employees_profiles"].delete_many({"metadata.source": actual_source})
