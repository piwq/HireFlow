import asyncio
import boto3
from fastapi import UploadFile
from uuid import uuid4

from app.config import settings

_client = None


def get_s3_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name="us-east-1",
        )
    return _client


def _put_object(bucket: str, key: str, body: bytes, content_type: str) -> None:
    get_s3_client().put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


async def upload_file(file: UploadFile) -> str:
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    key = f"{uuid4().hex}.{ext}"
    content = await file.read()
    await asyncio.to_thread(
        _put_object, settings.minio_bucket, key, content, file.content_type
    )
    return f"{settings.minio_public_url}/{settings.minio_bucket}/{key}"
