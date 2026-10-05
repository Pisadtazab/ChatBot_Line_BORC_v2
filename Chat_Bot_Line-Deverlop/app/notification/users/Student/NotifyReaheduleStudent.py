from fastapi import APIRouter
from pydantic import AliasChoices, BaseModel, Field

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    UserId: str | None = Field(default=None, validation_alias=AliasChoices("userId", "UserId"))
    AdvisorId: str | None = None
    AdvisorName: str
    StudentName: str
    ResearchTopic: str = "-"
    Date: str
    Time: str
    Status: str


@router.post("/RecheduleStudent")
def notify_Rechedule(data: RecheduleData):
    if data.Status != "Rescheduled":
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    delivery = push_reschedule_notifications(
        sender_id=data.AdvisorId,
        recipient_id=data.UserId,
        sender_title="ส่งคำขอเลื่อนคิวสำเร็จ",
        recipient_title="อาจารย์เลื่อนคิว",
        student_name=data.StudentName,
        advisor_name=data.AdvisorName,
        research_topic=data.ResearchTopic,
        date=data.Date,
        time=data.Time,
        recipient_advisor_name=data.AdvisorName,
    )
    return {"status": delivery["status"], "notification": delivery}
