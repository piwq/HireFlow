import boto3
from botocore.exceptions import ClientError
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


async def upload_file(file: UploadFile) -> str:
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    key = f"{uuid4().hex}.{ext}"

    content = await file.read()
    client = get_s3_client()
    client.put_object(
        Bucket=settings.minio_bucket,
        Key=key,
        Body=content,
        ContentType=file.content_type,
    )

    return f"{settings.minio_public_url}/{settings.minio_bucket}/{key}"
