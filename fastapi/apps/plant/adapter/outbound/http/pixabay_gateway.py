from __future__ import annotations

import asyncio

from plant.adapter.outbound.http.pixabay_client import download_photo, search_first_photo
from plant.app.ports.output.pixabay_image_gateway import PixabayImageGateway, PixabayPhoto


class PixabayGateway(PixabayImageGateway):

    async def fetch_photo(self, query: str) -> PixabayPhoto | None:
        found = await asyncio.to_thread(search_first_photo, query)
        if "error" in found:
            return None

        downloaded = await asyncio.to_thread(download_photo, found["image_url"])
        if "error" in downloaded:
            return None

        return PixabayPhoto(
            source_id=found["source_id"],
            content_type=downloaded["content_type"],
            data=downloaded["data"],
        )
