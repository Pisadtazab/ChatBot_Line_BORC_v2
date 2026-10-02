import os
import requests
from fastapi import APIRouter
from dotenv import load_dotenv
from app.notification.DB.database_noti import collection as notify_collection
from linebot.v3.webhooks import MessageEvent

load_dotenv()

router = APIRouter()

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")


# ─────────────────────────────────────────────
# Push: Flex Message แจ้งเตือน
# ─────────────────────────────────────────────
def push_flex_notification(user_id: str, title: str, message: str, color: str = "#00B900") -> dict:
    if not ACCESS_TOKEN:
        return {"status": "error", "message": "Missing ACCESS_TOKEN"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "flex",
                "altText": title,
                "contents": {
                    "type": "bubble",
                    "size": "mega",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🔔 การแจ้งเตือน",
                                "color": "#ffffff",
                                "size": "sm",
                                "weight": "bold"
                            }
                        ],
                        "backgroundColor": color,
                        "paddingAll": "15px"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": title,
                                "weight": "bold",
                                "size": "lg",
                                "wrap": True,
                                "color": "#1a1a1a"
                            },
                            {"type": "separator"},
                            {
                                "type": "text",
                                "text": message,
                                "size": "sm",
                                "wrap": True,
                                "color": "#555555"
                            }
                        ],
                        "paddingAll": "20px"
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ระบบแจ้งเตือนอัตโนมัติ",
                                "size": "xs",
                                "color": "#aaaaaa",
                                "align": "center"
                            }
                        ],
                        "paddingAll": "10px"
                    }
                }
            }
        ]
    }
    try:
        response = requests.post(LINE_PUSH_URL, headers=headers, json=payload, timeout=5.0)
        response.raise_for_status()
        return {"status": "success", "http_status": response.status_code}
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}



# ─────────────────────────────────────────────
# Test endpoint
# ─────────────────────────────────────────────
# @router.get("/test-push/{user_id}")
# def test_push(user_id: str):
#     user = notify_collection.find_one({"userId": user_id})
#     if not user:
#         return {"status": "user not found"}

#     name = user.get("Firstname", "คุณ")
#     push_flex_notification(
#         user_id=user_id,
#         title=f"สวัสดีคุณ {name}! 🎉",
#         message="ระบบแจ้งเตือนพร้อมแล้ว ✅",
#         color="#00B900"
#     )
#     return {"status": "ok", "name": name}


