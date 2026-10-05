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
    color: str = "#445DFF",
) -> dict:
    def contents(status: str) -> list[dict]:
        rows = [
            flex_row("👤 ชื่อ", student_name, wrap=True),
            flex_row("📝 หัวข้อ", research_topic, wrap=True),
            flex_row("📅 วันที่", date),
            flex_row("⏰ เวลา", time),
        ]
        rows.insert(0, flex_row("👨‍🏫 อาจารย์", advisor_name, wrap=True))
        return rows + [
            {"type": "separator"},
            flex_row("สถานะ", status, value_color=color, value_weight="bold", wrap=True),
        ]

    return send_flex_request_notifications(
        sender_id, recipient_id, sender_title, recipient_title, color,
        contents("ส่งคำขอเลื่อนคิวสำเร็จ"), contents("เลื่อนคิว"),
    )
