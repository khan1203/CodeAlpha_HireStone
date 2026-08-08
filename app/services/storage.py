import boto3
from botocore.exceptions import ClientError

from app.config import settings

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
    return _s3_client


def upload_file_to_s3(file_bytes: bytes, s3_key: str, content_type: str = "application/octet-stream") -> None:
    client = get_s3_client()
    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {e}")


def delete_file_from_s3(s3_key: str) -> None:
    client = get_s3_client()
    try:
        client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
    except ClientError as e:
        raise RuntimeError(f"S3 delete failed: {e}")


def get_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    client = get_s3_client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": s3_key},
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise RuntimeError(f"Presigned URL generation failed: {e}")