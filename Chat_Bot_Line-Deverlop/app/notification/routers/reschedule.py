from app.notification.helpers.flex import flex_row, send_flex_request_notifications


def push_reschedule_notifications(
    sender_id: str ,
    recipient_id: str ,
    sender_title: str,
    recipient_title: str,
    student_name: str,
    research_topic: str,
    date: str,
    time: str,
    advisor_name: str,
    sender_is_advisor: bool,
    color: str = "#445DFF",
) -> dict:
    def contents(status: str, status_color: str, name: str, label: str) -> list[dict]:
        rows = [
            flex_row(label, name, wrap=True),
            flex_row("📝 หัวข้อ", research_topic, wrap=True),
            flex_row("📅 วันที่", date),
            flex_row("⏰ เวลา", time),
        ]
        return rows + [
            {"type": "separator"},
            flex_row("สถานะ", status, value_color=status_color, value_weight="bold", wrap=True),
        ]

    return send_flex_request_notifications(
        sender_id, recipient_id, sender_title, recipient_title, color,
        contents(
            "ส่งคำขอเลื่อนคิวสำเร็จ", "#00B900",
            student_name if sender_is_advisor else advisor_name,
            "👤 นักศึกษา" if sender_is_advisor else "👨‍🏫 อาจารย์",
        ),
        contents(
            "เลื่อนคิว", color,
            advisor_name if sender_is_advisor else student_name,
            "👨‍🏫 อาจารย์" if sender_is_advisor else "👤 นักศึกษา",
        ),
    )
