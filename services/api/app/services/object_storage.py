import asyncio
import boto3
from botocore.config import Config
from app.core.config import settings

class ObjectStorage:
    def __init__(self):
        required = (settings.object_storage_bucket, settings.object_storage_access_key, settings.object_storage_secret_key)
        if not all(required):
            raise RuntimeError("Private object storage is not configured")
        self.client = boto3.client(
            "s3", endpoint_url=settings.object_storage_endpoint or None,
            region_name=settings.object_storage_region,
            aws_access_key_id=settings.object_storage_access_key,
            aws_secret_access_key=settings.object_storage_secret_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        self.bucket = settings.object_storage_bucket

    async def put(self, key: str, data: bytes, content_type: str):
        await asyncio.to_thread(self.client.put_object, Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    async def signed_get(self, key: str, expires: int = 300) -> str:
        return await asyncio.to_thread(self.client.generate_presigned_url, "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=expires)

    async def delete(self, key: str):
        await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket, Key=key)
