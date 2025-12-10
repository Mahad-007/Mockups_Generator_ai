import boto3
from botocore.config import Config
from typing import Optional
import uuid
from datetime import datetime

from app.config import settings


class StorageClient:
    """Handles file storage operations with S3/R2."""

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket_name

    async def upload_file(
        self,
        file_bytes: bytes,
        content_type: str,
        folder: str = "uploads",
        filename: Optional[str] = None,
    ) -> str:
        """
        Upload a file to storage.

        Args:
            file_bytes: File content as bytes
            content_type: MIME type of the file
            folder: Folder path in bucket
            filename: Optional custom filename

        Returns:
            URL of the uploaded file
        """
        # Generate filename if not provided
        if not filename:
            ext = content_type.split("/")[-1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"

        key = f"{folder}/{filename}"

        # Upload to S3/R2
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )

        # Return public URL
        if settings.s3_endpoint_url:
            # Cloudflare R2 or custom endpoint
            return f"{settings.s3_endpoint_url}/{self.bucket}/{key}"
        else:
            # AWS S3
            return f"https://{self.bucket}.s3.amazonaws.com/{key}"

    async def delete_file(self, url: str) -> bool:
        """
        Delete a file from storage.

        Args:
            url: URL of the file to delete

        Returns:
            True if successful
        """
        # Extract key from URL
        key = url.split(f"{self.bucket}/")[-1]

        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key,
            )
            return True
        except Exception:
            return False

    async def get_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate a presigned URL for temporary access.

        Args:
            key: File key in bucket
            expires_in: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )


# Singleton instance
storage_client = StorageClient()
