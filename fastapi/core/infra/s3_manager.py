"""AWS S3 클라이언트 — 자격 증명은 .env(AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_REGION)에서 로드."""

from __future__ import annotations

import boto3

from core.infra.secret_manager import secret_manager


class S3Manager:
    """boto3 S3 클라이언트 — core 레이어 공용 인프라 유틸."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            aws_access_key_id=secret_manager.get_secret("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=secret_manager.get_secret("AWS_SECRET_ACCESS_KEY"),
            region_name=secret_manager.get_secret("AWS_DEFAULT_REGION"),
        )

    def list_bucket_names(self) -> list[str]:
        response = self._client.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]


s3_manager = S3Manager()


if __name__ == "__main__":
    for name in s3_manager.list_bucket_names():
        print(name)
