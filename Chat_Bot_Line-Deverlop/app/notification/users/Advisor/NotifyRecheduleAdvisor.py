from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    AdvisorId: str | None = None
    StudentId: str | None = None
    StudentName: str
    ResearchTopic: str = "-"
    Date: str
    Time: str
    Status: str


@router.post("/RecheduleAdvisor")
def notify_Rechedule(data: RecheduleData):
    if data.Status != "Rescheduled":
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    delivery = push_reschedule_notifications(
        sender_id=data.StudentId,
        recipient_id=data.AdvisorId,
        sender_title="ส่งคำขอเลื่อนคิวสำเร็จ",
        recipient_title="นักศึกษาเลื่อนคิว",
        student_name=data.StudentName,
        research_topic=data.ResearchTopic,
        date=data.Date,
        time=data.Time,
    )
    return {"status": delivery["status"], "notification": delivery}
