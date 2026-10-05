from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.helpers.flex import flex_row, send_flex_notifications


class BookingData(BaseModel):
    AdvisorId: str 
    StudentId: str 
    StudentName: str
    AdvisorName:str
    ResearchTopic: str
    Date: str
    Time: str
    Status: str


router = APIRouter()


@router.post("/BookingStudent")
def notifyqueue(data: BookingData):
    confirmation = [
        flex_row("👨‍🏫 อาจารย์", data.AdvisorName, wrap=True),
        flex_row("📝 หัวข้อ", data.ResearchTopic, wrap=True),
        flex_row("📅 วันที่", data.Date),
        flex_row("⏰ เวลา", data.Time),
        {"type": "separator"},
        flex_row("สถานะ", "ส่งคำขอแล้ว รอการอนุมัติ", value_color="#FFB100", value_weight="bold", wrap=True),
    ]
    delivery = send_flex_notifications([data.StudentId], "ส่งคำขอจองคิวสำเร็จ", "#00B900", confirmation)
    return {"status": delivery["status"], "notification": {"student": delivery}}
