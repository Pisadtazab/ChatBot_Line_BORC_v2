from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.helpers.flex import flex_row, send_flex_notifications


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
    delivery = send_flex_notifications([data.AdvisorId, data.StudentId], "มีนักศึกษาขอจองคิว 📋", "#FFB100", [
        flex_row("👤 ชื่อ", data.StudentName, wrap=True),
        flex_row("📝 หัวข้อ", data.ResearchTopic, wrap=True),
        flex_row("📅 วันที่", data.Date),
        flex_row("⏰ เวลา", data.Time),
        {"type": "separator"},
        flex_row("🟡 สถานะ", "รอการอนุมัติ", value_color="#FFB100", value_weight="bold"),
    ])
    return {"status": "success", "notification": delivery}
