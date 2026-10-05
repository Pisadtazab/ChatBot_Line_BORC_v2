from fastapi import APIRouter
from pydantic import AliasChoices, BaseModel, Field

from app.notification.routers.reschedule import push_reschedule_notifications

router = APIRouter()


class RecheduleData(BaseModel):
    StudentId: str = Field(validation_alias=AliasChoices("StudentId", "studentId", "userId", "UserId"))
    AdvisorId: str
    AdvisorName: str
    StudentName: str
    ResearchTopic: str = "-"
    Date: str
    Time: str
    Status: str

# flex รับ
@router.post("/RecheduleStudent")
def notify_Rechedule(data: RecheduleData):
    if data.Status.strip().casefold() != "rescheduled":
        return {"status": "skip", "message": "ไม่รู้จัก Status"}
    delivery = push_reschedule_notifications(
        sender_id=data.AdvisorId,
        recipient_id=data.StudentId,
        sender_title="ส่งคำขอเลื่อนคิวสำเร็จ",
        recipient_title="อาจารย์เลื่อนคิว",
        student_name=data.StudentName,
        research_topic=data.ResearchTopic,
        date=data.Date,
        time=data.Time,
        advisor_name=data.AdvisorName,
        sender_is_advisor=True,
    )
    return {"status": delivery["status"], "notification": delivery}
