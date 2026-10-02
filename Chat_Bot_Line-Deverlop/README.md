# LINE Chatbot — Research Advisor

FastAPI service สำหรับ LINE chatbot แบบ RAG, รับ PDF เพื่อค้นหาข้อมูลอาจารย์ และส่ง LINE Flex notifications สำหรับการจองนัดหมาย

## ภาพรวมระบบ

```text
PDF upload ──▶ PyMuPDF ──▶ text chunks + embeddings ──▶ MongoDB Atlas
                  │                                      ▲
                  └── image bytes ──▶ Cloudinary ── URL ─┘

LINE message ──▶ /callback ──▶ BAAI/bge-m3 (Hugging Face)
                                      │
                                      ▼
                              MongoDB Vector Search
                                      │
                                      ▼
                                Typhoon API
                                      │
                         text + Cloudinary image URLs
                                      ▼
                                  LINE Push

Booking system ──▶ notification POST routes ──▶ LINE Flex Push API
```

## โครงสร้างโปรเจกต์

```text
app/
├── main.py                       # FastAPI app, router registration, LINE webhook
├── DB/database.py                # MongoDB chatbot connection and PDF deletion
├── routers/
│   ├── extractPDF.py              # PDF upload, extraction, summary and indexing
│   ├── getData.py                 # PDF listing and image redirect
│   └── deleteFile.py              # Delete indexed PDF records
├── services/
│   ├── line_bot.py                # LINE webhook processing and message delivery
│   └── cloudinary.py              # Cloudinary configuration and image upload
├── retriever.py                   # Embedding search and Typhoon response
├── promrt_typhoon.py              # Chat system prompt
└── notification/
    ├── DB/database_noti.py        # BORC notification database
    ├── helpers/flex.py            # Shared Flex message and push helper
    ├── routers/                   # Login, LINE push and reschedule helpers
    └── users/
        ├── Advisor/               # Booking, cancellation and reschedule
        └── Student/               # Approval, reschedule and URL alerts
Dockerfile
docker-compose.yml
requirements.txt
extractpdf-flow.txt                # Detailed PDF and RAG flow
```

## การเก็บ PDF และรูปภาพ

`POST /upload_pdf` รับ PDF ขนาดไม่เกิน 50 MB และบันทึกเป็นไฟล์ชั่วคราวระหว่างประมวลผล จากนั้นลบไฟล์ชั่วคราวเมื่อทำงานเสร็จ

- ข้อความแต่ละหน้าและ embedding ถูกบันทึกใน MongoDB collection `employee_research_db_V2.employees_profiles`
- รูปต้นฉบับถูกอัปโหลดไปยัง Cloudinary; MongoDB เก็บ `image_url`, คำอธิบาย, metadata และ embedding เท่านั้น
- คำอธิบายรูปปัจจุบันสร้างจากเลขหน้าและข้อความใกล้เคียงใน PDF ไม่ได้วิเคราะห์เนื้อหาจาก pixels
- `GET /image/{file_id}` redirect ไปยัง `image_url` ของเอกสารรูปใน MongoDB และรองรับอ่าน GridFS สำหรับข้อมูลเก่า
- Chatbot ใช้ `image_url` จาก MongoDB ส่งให้ LINE โดยตรง จึงไม่ได้เรียก `/image/{file_id}` ใน flow ปกติ
- `DELETE /delete_file` ลบเอกสาร PDF ใน MongoDB และ GridFS เก่า แต่ยังไม่ได้ลบ asset เดิมออกจาก Cloudinary

## Chat และ RAG

1. LINE ส่ง webhook มาที่ `POST /callback`; ระบบตรวจ `X-Line-Signature`
2. ระบบสร้าง embedding ของคำถามด้วย BAAI/bge-m3 ผ่าน Hugging Face Inference API
3. ค้นเอกสารด้วย MongoDB Vector Search index `vector_index2`
4. ส่งคำถามและบริบทให้ Typhoon API สร้างคำตอบและเลือกรูปจาก URL ที่พบในผลค้นหา
5. ตรวจว่า URL รูปอยู่ในผลค้นหาจริง แล้วส่งข้อความและรูปผ่าน LINE Push API

การสรุป PDF ด้วย Typhoon เกิดตอน upload และส่งกลับใน API response; summary ยังไม่ถูก index เข้า Vector Search

## API routes

| Method | Path | หน้าที่ |
| --- | --- | --- |
| `POST` | `/callback` | LINE webhook สำหรับข้อความและ follow events |
| `GET` | `/health` | Health check |
| `POST` | `/upload_pdf` | อัปโหลดและ index PDF (สูงสุด 50 MB) |
| `GET` | `/files` | รายชื่อ source PDF ที่มีใน MongoDB |
| `GET` | `/image/{file_id}` | Redirect ไป Cloudinary หรืออ่าน GridFS เก่า |
| `DELETE` | `/delete_file?pdf_name=...` | ลบ PDF records จาก MongoDB |
| `POST` | `/NotifyFristLogin/UserLine_id` | แจ้งเตือนเมื่อผูก LINE; ส่งเมื่อ UserProfile มีสถานะ `Approved` |
| `POST` | `/NotifyQueueAdivsor/BookingStudent` | แจ้งเมื่อมีการจองคิว |
| `POST` | `/NotifyCancelled/CancelBooking` | แจ้งเมื่อนักศึกษายกเลิก |
| `POST` | `/NotifyQueueAdivsor/RecheduleAdvisor` | แจ้งเมื่อมีการเลื่อนคิว |
| `POST` | `/NotifyQueueStudent/NotifyStudent` | แจ้งเมื่อตอบรับหรือยกเลิกการจอง (`Approved`/`Cancelled`) |
| `POST` | `/NotifyQueueStudent/RecheduleStudent` | แจ้งนักศึกษาเมื่ออาจารย์เลื่อนคิว |
| `POST` | `/NotifyChat/send_url/notification` | ส่งลิงก์นัดหมายให้นักศึกษา |

ไม่มี route หน้า Admin UI ที่ `/` ใน FastAPI app ปัจจุบัน

### Notification recipients

ใน 5 booking notification endpoints ฟิลด์ LINE ID ของ Advisor และ Student รับ string, `null`, หรือไม่ส่ง field ได้ เฉพาะ ID ที่มีค่าจะถูกลองส่ง; ความล้มเหลวของผู้รับคนหนึ่งไม่หยุดการส่งให้อีกคน ผลอยู่ใน `notification`. Endpoint ผูก LINE และส่ง URL ยังต้องมี ID ของผู้รับตาม model ของตัวเอง:

```json
{"status":"success|partial|error|skipped","sent":1,"failed":0,"skipped":1}
```

เพื่อแจ้งทั้งสองฝ่าย ให้ส่ง `AdvisorId` กับ `StudentId` ใน endpoint ฝั่ง Advisor หรือส่ง `userId`/`UserId` กับ `AdvisorId` ใน endpoint ฝั่ง Student ตัวอย่าง field เพิ่มเติม:

```json
{
  "AdvisorId": "Uadvisor...",
  "StudentId": "Ustudent...",
  "StudentName": "สมชาย ใจดี",
  "ResearchTopic": "หัวข้องานวิจัย",
  "Date": "2026-10-02",
  "Time": "10:00",
  "Status": "Pending"
}
```

ค่าฟิลด์อื่นของแต่ละ endpoint ยังคงเป็นไปตาม model ในไฟล์ router นั้น เช่น `CancelReason`, `AdvisorName` และ `Status`

## Environment variables

ตั้งค่าใน `.env` ที่ root หรือ environment ของ container:

| Variable | ใช้โดย |
| --- | --- |
| `ACCESS_TOKEN` | LINE Channel Access Token สำหรับส่งข้อความและ Flex notification |
| `CHANNEL_SECRET` | LINE Channel Secret สำหรับตรวจ webhook signature |
| `HUGGINGFACE_TOKEN` | Hugging Face Inference API สำหรับ BAAI/bge-m3 embeddings |
| `Typhoon_api_key` | Typhoon API สำหรับสรุป PDF และสร้างคำตอบแชท |
| `MONGO_URI` | MongoDB chatbot database (`employee_research_db_V2`) |
| `MONGO_URI_BORC` | MongoDB notification database (`BORC`, collection `UserProfile`) |
| `CLOUD_IMAGE` | Cloudinary cloud name |
| `API_KEY` | Cloudinary API key |
| `API_SECRET` | Cloudinary API secret |
| `NGROK_TOKEN` | จำเป็นเมื่อใช้ Compose profile `ngrok` เท่านั้น |
| `Frontend_BORC_URL` | เพิ่ม origin ให้ CORS (ไม่บังคับ) |
| `Backend_BORC_URL` | เพิ่ม origin ให้ CORS (ไม่บังคับ) |
| `ChatBot_URL` | เพิ่ม origin ให้ CORS (ไม่บังคับ) |

`MONGO_URI_BORCL`, `MONGO_URI_LOCAL` และ `NGROK_URL` ไม่ใช่ชื่อตัวแปรที่โค้ดปัจจุบันอ่าน

ตัวอย่าง `.env`:

```env
ACCESS_TOKEN=your_line_channel_access_token
CHANNEL_SECRET=your_line_channel_secret
HUGGINGFACE_TOKEN=your_huggingface_token
Typhoon_api_key=your_typhoon_api_key
MONGO_URI=your_chatbot_mongodb_uri
MONGO_URI_BORC=your_borc_mongodb_uri
CLOUD_IMAGE=your_cloudinary_cloud_name
API_KEY=your_cloudinary_api_key
API_SECRET=your_cloudinary_api_secret
NGROK_TOKEN=your_ngrok_token
```

## การติดตั้งและรัน

Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

หรือใช้ Docker Compose:

```bash
docker compose up -d
# เลือก tunnel เมื่อจำเป็น โดยเปิดเพียง profile เดียว
docker compose --profile cloudflared up -d
# หรือ
docker compose --profile ngrok up -d
```

ตรวจ app ที่ `http://localhost:5000/health`; ngrok dashboard อยู่ที่ `http://localhost:4040`
