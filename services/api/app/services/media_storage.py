import asyncio
import boto3
from botocore.config import Config
from app.core.config import settings


def _client():
    if not all([settings.media_s3_bucket, settings.media_s3_access_key, settings.media_s3_secret_key]):
        raise RuntimeError("Private S3-compatible media storage is not configured")
    return boto3.client(
        "s3",
        endpoint_url=settings.media_s3_endpoint or None,
        region_name=settings.media_s3_region,
        aws_access_key_id=settings.media_s3_access_key,
        aws_secret_access_key=settings.media_s3_secret_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


async def store_object(*, key: str, body: bytes, content_type: str) -> None:
    client = _client()
    await asyncio.to_thread(
        client.put_object,
        Bucket=settings.media_s3_bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
        ServerSideEncryption="AES256",
    )


async def signed_object_url(key: str, expires_seconds: int = 900) -> str:
    client = _client()
    return await asyncio.to_thread(
        client.generate_presigned_url,
        "get_object",
        Params={"Bucket": settings.media_s3_bucket, "Key": key},
        ExpiresIn=expires_seconds,
    )


async def delete_object(key: str) -> None:
    client = _client()
    await asyncio.to_thread(client.delete_object, Bucket=settings.media_s3_bucket, Key=key)
