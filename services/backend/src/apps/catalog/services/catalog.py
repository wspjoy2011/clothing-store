from typing import Optional, Callable

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.interfaces.specifications import PaginationSpecificationInterface, OrderingSpecificationInterface

PaginationSpecificationFactory = Callable[[int, int], PaginationSpecificationInterface]
OrderingSpecificationFactory = Callable[[Optional[str]], OrderingSpecificationInterface]


class CatalogService(CatalogServiceInterface):
    def __init__(
            self,
            product_repository: ProductRepositoryInterface,
            pagination_specification_factory: PaginationSpecificationFactory,
            ordering_specification_factory: OrderingSpecificationFactory,
    ):
        self._product_repository = product_repository
        self._pagination_specification_factory = pagination_specification_factory
        self._ordering_specification_factory = ordering_specification_factory

    async def get_paginated_products(
            self,
            page: int,
            per_page: int,
            ordering: Optional[str] = None
    ) -> Optional[list[ProductDTO]]:
        pagination_spec = self._pagination_specification_factory(page, per_page)
        ordering_spec = self._ordering_specification_factory(ordering)

        products = await self._product_repository.get_products_with_specifications(
            pagination_spec=pagination_spec,
            ordering_spec=ordering_spec
        )

        if not products:
            return None

        return products


    async def get_products_count(self) -> int:
        return await self._product_repository.get_products_count()
