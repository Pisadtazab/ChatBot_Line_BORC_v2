from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    UserId: str | None = None
    AdvisorId: str | None = None
    StudentName: str
    Date: str
    Time: str
    Status: str


@router.post("/RecheduleStudent")
def notify_Rechedule(data: RecheduleData):
    if data.Status != "Rescheduled":
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    delivery = push_reschedule_notifications(data.AdvisorId, data.UserId, "ส่งคำขอเลื่อนคิวสำเร็จ", "อาจารย์เลื่อนคิว", data.StudentName, data.Date, data.Time)
    return {"status": delivery["status"], "notification": delivery}
