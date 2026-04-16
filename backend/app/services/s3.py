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
        # Автоматическое создание бакета при запуске, если его нет
        try:
            _client.head_bucket(Bucket=settings.minio_bucket)
        except:
            try:
                _client.create_bucket(Bucket=settings.minio_bucket)
                # Делаем бакет публичным для чтения (так как мы отдаем прямые ссылки)
                # Это упрощенная политика для хакатона
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Sid": "PublicRead",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{settings.minio_bucket}/*"]
                    }]
                }
                import json
                _client.put_bucket_policy(Bucket=settings.minio_bucket, Policy=json.dumps(policy))
            except Exception as e:
                print(f"Failed to create bucket: {e}")
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
