from __future__ import annotations

from admin.app.dtos.s3_image_upload_dto import ImageUploadCommand
from admin.app.use_cases.s3_image_upload_interactor import S3ImageUploadInteractor


class _FakeImageStorageGateway:
    def __init__(self, url: str) -> None:
        self._url = url
        self.saved_calls: list[tuple[str, str, bytes]] = []

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        self.saved_calls.append((filename, content_type, data))
        return self._url


async def test_upload_delegates_to_storage_gateway_and_returns_url():
    gateway = _FakeImageStorageGateway(
        url="https://bucket.s3.ap-northeast-2.amazonaws.com/admin/abc.png"
    )
    interactor = S3ImageUploadInteractor(storage=gateway)

    result = await interactor.upload(
        ImageUploadCommand(filename="leaf.png", content_type="image/png", data=b"binary-data")
    )

    assert result.url == "https://bucket.s3.ap-northeast-2.amazonaws.com/admin/abc.png"
    assert gateway.saved_calls == [("leaf.png", "image/png", b"binary-data")]
