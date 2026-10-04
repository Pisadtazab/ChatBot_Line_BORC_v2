from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.helpers.flex import flex_row, send_flex_request_notifications


class BookingData(BaseModel):
    AdvisorId: str | None = None
    StudentId: str | None = None
    StudentName: str
    ResearchTopic: str
    Date: str
    Time: str
    Status: str


router = APIRouter()


@router.post("/BookingStudent")
def notifyqueue(data: BookingData):
    details = [
        flex_row("👤 ชื่อ", data.StudentName, wrap=True),
        flex_row("📝 หัวข้อ", data.ResearchTopic, wrap=True),
        flex_row("📅 วันที่", data.Date),
        flex_row("⏰ เวลา", data.Time),
        {"type": "separator"},
        flex_row(" สถานะ", "รอการอนุมัติ", value_color="#FFB100", value_weight="bold"),
    ]
    confirmation = [
        flex_row("👤 ชื่อ", data.StudentName, wrap=True),
        flex_row("📝 หัวข้อ", data.ResearchTopic, wrap=True),
        flex_row("📅 วันที่", data.Date),
        flex_row("⏰ เวลา", data.Time),
        {"type": "separator"},
        flex_row("สถานะ", "ส่งคำขอแล้ว รอการอนุมัติ", value_color="#FFB100", value_weight="bold", wrap=True),
    ]
    delivery = send_flex_request_notifications(data.StudentId, data.AdvisorId, "ส่งคำขอจองคิวสำเร็จ", "มีนักศึกษาขอจองคิว 📋", "#FFB100", confirmation, details)
    return {"status": delivery["status"], "notification": delivery}
