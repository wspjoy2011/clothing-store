from typing import Optional

from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.services import CatalogServiceInterface


class CatalogService(CatalogServiceInterface):
    def __init__(
            self,
            product_repository: ProductRepositoryInterface,
    ):
        self._product_repository = product_repository

    async def get_paginated_products(self, page: int, per_page: int) -> Optional[list[ProductDTO]]:
        offset = (page - 1) * per_page
        products = await self._product_repository.get_products_with_pagination(offset, per_page)

        if not products:
            return None

        return products

    async def get_products_count(self) -> int:
        return await self._product_repository.get_products_count()
