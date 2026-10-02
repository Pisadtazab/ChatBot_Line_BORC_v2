import os

import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv


load_dotenv(override=True)


cloudinary.config(
    cloud_name=os.getenv("CLOUD_IMAGE"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True,
)


def upload_image(
    image_bytes: bytes,
    public_id: str,
    folder: str = "hms-rag",
) -> str:
    """
    Upload image bytes to Cloudinary
    and return the secure URL.
    """

    result = cloudinary.uploader.upload(
        image_bytes,
        folder=folder,
        public_id=public_id,
        resource_type="image",
    )

    return result["secure_url"]