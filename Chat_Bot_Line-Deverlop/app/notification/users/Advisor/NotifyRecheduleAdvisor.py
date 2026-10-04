from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    AdvisorId: str | None = None
    StudentId: str | None = None
    StudentName: str
    Date: str
    Time: str
    Status: str


@router.post("/RecheduleAdvisor")
def notify_Rechedule(data: RecheduleData):
    if data.Status != "Rescheduled":
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    delivery = push_reschedule_notifications(data.StudentId, data.AdvisorId, "ส่งคำขอเลื่อนคิวสำเร็จ", "นักศึกษาเลื่อนคิว", data.StudentName, data.Date, data.Time)
    return {"status": delivery["status"], "notification": delivery}
