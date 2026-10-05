import os

import requests
from dotenv import load_dotenv


LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
FOOTER = {"type": "text", "text": "ระบบแจ้งเตือนอัตโนมัติ", "size": "xs", "color": "#aaaaaa", "align": "center"}

load_dotenv()


def flex_row(label: str, value: str, *, value_color: str = "#1a1a1a", value_weight: str = "regular", wrap: bool = False, label_color: str = "#aaaaaa") -> dict:
    return {"type": "box", "layout": "horizontal", "contents": [
        {"type": "text", "text": label, "size": "sm", "color": label_color, "flex": 2},
        {"type": "text", "text": value, "size": "sm", "color": value_color, "weight": value_weight, "wrap": wrap, "flex": 4},
    ]}


def send_flex_notification(user_id: str, title: str, color: str, body: list[dict], *, header_text: str | None = None, footer: list[dict] | None = None) -> dict:
    token = os.getenv("ACCESS_TOKEN")
    if not token:
        return {"status": "error", "message": "Missing ACCESS_TOKEN"}
    payload = {"to": user_id, "messages": [{"type": "flex", "altText": title, "contents": {
        "type": "bubble", "size": "mega",
        "header": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": header_text or f"{'🚀' if 'สำเร็จ' in title else '🔔'} {title}", "color": "#ffffff", "size": "md", "weight": "bold"}], "backgroundColor": color, "paddingAll": "15px"},
        "body": {"type": "box", "layout": "vertical", "spacing": "md", "contents": body, "paddingAll": "20px"},
        "footer": {"type": "box", "layout": "vertical", "contents": footer or [FOOTER], "paddingAll": "10px"},
    } }]}
    try:
        response = requests.post(LINE_PUSH_URL, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, json=payload, timeout=5.0)
        response.raise_for_status()
        return {"status": "success", "http_status": response.status_code}
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


def send_flex_notifications(user_ids: list[str | None], title: str, color: str, body: list[dict]) -> dict:
    recipients = list(dict.fromkeys(user_id for user_id in user_ids if user_id))
    skipped = sum(not user_id for user_id in user_ids)
    results = []

    for user_id in recipients:
        try:
            result = send_flex_notification(user_id, title, color, body)
        except Exception as exc:
            result = {"status": "error", "message": str(exc)}
        results.append(result)

    sent = sum(result["status"] == "success" for result in results)
    failed = len(results) - sent
    status = "success" if not skipped and not failed else "partial" if sent else "error" if failed else "skipped"
    return {"status": status, "sent": sent, "failed": failed, "skipped": skipped, "results": results}


def send_flex_request_notifications(sender_id: str | None, recipient_id: str | None, sender_title: str, recipient_title: str, color: str, sender_body: list[dict], recipient_body: list[dict], sender_color: str = "#00B900") -> dict:
    sender_id = sender_id.strip() or None if sender_id else None #ผู้ส่ง
    recipient_id = recipient_id.strip() or None if recipient_id else None #ผู้รับปลายทาง

    recipient_delivery = send_flex_notifications([recipient_id], recipient_title, color, recipient_body)
    if recipient_id and recipient_delivery["status"] != "success":
        return {"status": "error", "recipient": recipient_delivery}

    sender_delivery = send_flex_notifications([sender_id], sender_title, sender_color, sender_body)
    if sender_id and sender_delivery["status"] != "success":
        return {"status": "error", "recipient": recipient_delivery, "sender": sender_delivery}

    status = "success" if sender_id and recipient_id else "partial" if sender_id or recipient_id else "skipped"
    return {"status": status, "sender": sender_delivery, "recipient": recipient_delivery}
