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
    delivery = push_reschedule_notifications([data.UserId, data.AdvisorId], "อาจารย์เลื่อนคิว", data.StudentName, "เลื่อนคิว", data.Date, data.Time)
    return {"status": "success", "notification": delivery}
