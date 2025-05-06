from pathlib import Path
from typing import Tuple

import pandas as pd
from etl.models.dto import (
    MasterCategoryDTO,
    SubCategoryDTO,
    ArticleTypeDTO,
    BaseColourDTO,
    SeasonDTO,
    UsageTypeDTO,
    ProductDTO,
    ImageDTO,
    ETLResultDTO,
)


class ProductCSVTransformer:
    """Extract & Transform pipeline for products and images CSV files."""

    def __init__(self, styles_path: str, images_path: str) -> None:
        self._styles_path = Path(styles_path)
        self._images_path = Path(images_path)

    def execute(self) -> ETLResultDTO:
        """Run extract + transform and return an ETLResultDTO."""
        styles_dataframe, images_dataframe = self._extract()
        return self._transform(styles_dataframe, images_dataframe)

    def _extract(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Read raw CSV files and clean column names."""
        styles_dataframe = pd.read_csv(self._styles_path, skipinitialspace=True)
        images_dataframe = pd.read_csv(self._images_path, skipinitialspace=True)

        return styles_dataframe, images_dataframe

    def _transform(
        self, styles_dataframe: pd.DataFrame, images_dataframe: pd.DataFrame
    ) -> ETLResultDTO:
        """Normalize data and build DTO collections."""

        master_categories = [
            MasterCategoryDTO(name=master_category_name)
            for master_category_name in sorted(
                styles_dataframe["master_category"].dropna().unique()
            )
        ]

        sub_categories = [
            SubCategoryDTO(
                master_category=styles_row.master_category,
                name=styles_row.sub_category,
            )
            for styles_row in (
                styles_dataframe[["master_category", "sub_category"]]
                .drop_duplicates()
                .dropna()
                .itertuples(index=False)
            )
        ]

        article_types = [
            ArticleTypeDTO(
                sub_category=styles_row.sub_category,
                name=styles_row.article_type,
            )
            for styles_row in (
                styles_dataframe[["sub_category", "article_type"]]
                .drop_duplicates()
                .dropna()
                .itertuples(index=False)
            )
        ]

        base_colours = [
            BaseColourDTO(name=base_colour_name)
            for base_colour_name in sorted(
                styles_dataframe["base_colour"].dropna().unique()
            )
        ]

        seasons = [
            SeasonDTO(name=season_name)
            for season_name in sorted(styles_dataframe["season"].dropna().unique())
        ]

        usage_types = [
            UsageTypeDTO(name=usage_type_name)
            for usage_type_name in sorted(styles_dataframe["usage"].dropna().unique())
        ]

        products = [
            ProductDTO(
                product_id=styles_row.product_id,
                gender=styles_row.gender,
                year=int(styles_row.year) if pd.notna(styles_row.year) else None,
                product_display_name=styles_row.product_display_name or None,
                article_type=styles_row.article_type,
                base_colour=styles_row.base_colour or None,
                season=styles_row.season or None,
                usage=styles_row.usage or None,
            )
            for styles_row in styles_dataframe.itertuples(index=False)
        ]

        images_dataframe["product_id"] = (
            images_dataframe["filename"].str.split(".").str[0].astype(int)
        )

        images = [
            ImageDTO(product_id=images_row.product_id, image_url=images_row.link)
            for images_row in images_dataframe.itertuples(index=False)
        ]

        return ETLResultDTO(
            master_categories=master_categories,
            sub_categories=sub_categories,
            article_types=article_types,
            base_colours=base_colours,
            seasons=seasons,
            usage_types=usage_types,
            products=products,
            images=images,
        )


if __name__ == '__main__':
    from settings.config import config

    product_transformer = ProductCSVTransformer(
        styles_path=config.STYLES_CSV,
        images_path=config.IMAGES_CSV
    )
