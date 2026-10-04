from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.helpers.flex import flex_row, send_flex_notifications


class BookingData(BaseModel):
    AdvisorId: str | None = None
    StudentId: str | None = None
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
    student_id = data.StudentId.strip() if data.StudentId else ""
    if not student_id:
        return {"status": "error", "reason": "missing_student_id"}

    delivery = send_flex_notifications([student_id], "ส่งคำขอจองคิวสำเร็จ", "#00B900", confirmation)
    if delivery["status"] != "success":
        failure = send_flex_notifications([student_id], "ส่งคำขอไม่สำเร็จ", "#FF4444", [
            flex_row("สถานะ", "ส่งคำขอจองคิวไม่สำเร็จ", value_color="#FF4444", value_weight="bold"),
        ])
        return {"status": "error", "notification": delivery, "failure_notification": failure}
    return {"status": "success", "notification": {"student": delivery}}
