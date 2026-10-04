from app.notification.helpers.flex import send_flex_notification as send_flex


def push_flex_notification(user_id: str, title: str, message: str, color: str = "#00B900") -> dict:
    return send_flex(
        user_id,
        title,
        color,
        [
            {"type": "text", "text": title, "weight": "bold", "size": "lg", "wrap": True, "color": "#1a1a1a"},
            {"type": "separator"},
            {"type": "text", "text": message, "size": "sm", "wrap": True, "color": "#555555"},
        ],
        header_text="🔔 การแจ้งเตือน",
    )
