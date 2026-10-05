from fastapi import APIRouter
from pydantic import BaseModel

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    AdvisorId: str 
    StudentId: str 
    StudentName: str
    AdvisorName: str
    ResearchTopic: str
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
        advisor_name=data.AdvisorName,
        sender_is_advisor=False,
    )
    return {"status": delivery["status"], "notification": delivery}
