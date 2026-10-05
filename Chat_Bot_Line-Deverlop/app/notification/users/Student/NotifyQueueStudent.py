from fastapi import APIRouter
from pydantic import AliasChoices, BaseModel, Field

from app.notification.helpers.flex import flex_row, send_flex_request_notifications


class StudentNotifyData(BaseModel):
    userId: str = Field(validation_alias=AliasChoices("userId", "UserId"))
    AdvisorId: str
    StudentName: str
    AdvisorName: str
    Date: str
    Time: str
    Status: str


router = APIRouter()


@router.post("/NotifyStudent")
def notify_student(data: StudentNotifyData):
    statuses = {
        "Approved": ("การจองได้รับการยืนยัน ✅", "ยืนยันแล้ว", "#00B900"),
        "Cancelled": ("การจองถูกยกเลิก ❌", "ยกเลิกแล้ว", "#FF4444"),
    }
    if data.Status not in statuses:
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    title, status_text, color = statuses[data.Status]
    details = [
        flex_row("👤 ชื่อ", data.StudentName),
        flex_row("👨‍🏫 อาจารย์", data.AdvisorName),
        flex_row("📅 วันที่", data.Date),
        flex_row("⏰ เวลา", data.Time),
        {"type": "separator"},
        flex_row("🔖 สถานะ", status_text, value_color=color, value_weight="bold"),
    ]
    confirmation = [
        flex_row("👤 นักศึกษา", data.StudentName, wrap=True),
        flex_row("🔖 ผลการจอง", status_text, value_color=color, value_weight="bold"),
    ]
    delivery = send_flex_request_notifications(data.AdvisorId, data.userId, "ส่งผลการจองสำเร็จ", title, color, confirmation, details)
    message = (
        f"แจ้งเตือนนักศึกษา {data.StudentName} แล้ว"
        if delivery["status"] == "success"
        else f"ส่งแจ้งเตือนนักศึกษา {data.StudentName} ไม่สำเร็จ"
    )
    return {"status": delivery["status"], "message": message, "notification": delivery}
