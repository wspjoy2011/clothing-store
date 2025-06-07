PRODUCT_EXAMPLE1 = {
    "product_id": 1,
    "gender": "Men",
    "year": 2023,
    "product_display_name": "Running Shoes",
    "image_url": "https://example.com/product1.jpg",
    "slug": "running-shoes-1",
}

PRODUCT_EXAMPLE2 = {
    "product_id": 2,
    "gender": "Women",
    "year": 2022,
    "product_display_name": "Comfortable Sandals",
    "image_url": "https://example.com/product2.jpg",
    "slug": "comfortable-sandals-2",
}

PRODUCT_EXAMPLE3 = {
    "product_id": 3,
    "gender": "Women",
    "year": 2023,
    "product_display_name": "Floral Blouse",
    "image_url": "https://example.com/product3.jpg",
    "slug": "floral-blouse-3",
}

PRODUCT_EXAMPLE5 = {
    "product_id": 5,
    "gender": "Men",
    "year": 2020,
    "product_display_name": "Classic Denim Jeans",
    "image_url": "https://example.com/product5.jpg",
    "slug": "classic-denim-jeans-5",
}

PRODUCT_EXAMPLE8 = {
    "product_id": 8,
    "gender": "Women",
    "year": 2020,
    "product_display_name": "Summer Dress",
    "image_url": "https://example.com/product8.jpg",
    "slug": "summer-dress-8",
}

PRODUCT_EXAMPLE14 = {
    "product_id": 14,
    "gender": "Men",
    "year": 2021,
    "product_display_name": "Leather Jacket",
    "image_url": "https://example.com/product14.jpg",
    "slug": "leather-jacket-14",
}

PRODUCT_EXAMPLE17 = {
    "product_id": 17,
    "gender": "Men",
    "year": 2020,
    "product_display_name": "Winter Coat",
    "image_url": "https://example.com/product17.jpg",
    "slug": "winter-coat-17",
}

STANDARD_RESPONSE_VALUE = {
    "products": [PRODUCT_EXAMPLE1, PRODUCT_EXAMPLE2],
    "prev_page": "/api/v1.0/catalog/products?page=1",
    "next_page": "/api/v1.0/catalog/products?page=3",
    "total_pages": 10,
    "total_items": 100,
}

YEAR_FILTERED_VALUE = {
    "products": [PRODUCT_EXAMPLE5, PRODUCT_EXAMPLE8],
    "prev_page": "/api/v1.0/catalog/products?page=1&min_year=2020&max_year=2020",
    "next_page": "/api/v1.0/catalog/products?page=3&min_year=2020&max_year=2020",
    "total_pages": 3,
    "total_items": 25,
}

GENDER_FILTERED_VALUE = {
    "products": [PRODUCT_EXAMPLE3, PRODUCT_EXAMPLE8],
    "prev_page": "/api/v1.0/catalog/products?page=1&gender=women",
    "next_page": "/api/v1.0/catalog/products?page=3&gender=women",
    "total_pages": 5,
    "total_items": 45,
}

YEAR_DESCENDING_VALUE = {
    "products": [PRODUCT_EXAMPLE1, PRODUCT_EXAMPLE3],
    "prev_page": "/api/v1.0/catalog/products?page=1&ordering=-year",
    "next_page": "/api/v1.0/catalog/products?page=3&ordering=-year",
    "total_pages": 7,
    "total_items": 68,
}

COMBINED_FILTERS_VALUE = {
    "products": [PRODUCT_EXAMPLE14, PRODUCT_EXAMPLE17],
    "prev_page": "/api/v1.0/catalog/products?page=1&min_year=2020&max_year=2022&gender=men&ordering=-year",
    "next_page": "/api/v1.0/catalog/products?page=3&min_year=2020&max_year=2022&gender=men&ordering=-year",
    "total_pages": 4,
    "total_items": 32,
}

CATEGORY_MENU_EXAMPLE = {
    "categories": [
        {
            "id": 1,
            "name": "Accessories",
            "sub_categories": [
                {
                    "id": 29,
                    "name": "Accessories",
                    "article_types": [
                        {"id": 89, "name": "Accessory Gift Set"},
                        {"id": 133, "name": "Hair Accessory"},
                        {"id": 146, "name": "Key chain"}
                    ]
                },
                {
                    "id": 8,
                    "name": "Bags",
                    "article_types": [
                        {"id": 45, "name": "Backpacks"},
                        {"id": 43, "name": "Clutches"},
                        {"id": 10, "name": "Handbags"}
                    ]
                }
            ]
        },
        {
            "id": 2,
            "name": "Apparel",
            "sub_categories": [
                {
                    "id": 2,
                    "name": "Bottomwear",
                    "article_types": [
                        {"id": 2, "name": "Jeans"},
                        {"id": 24, "name": "Shorts"},
                        {"id": 38, "name": "Skirts"}
                    ]
                },
                {
                    "id": 1,
                    "name": "Topwear",
                    "article_types": [
                        {"id": 1, "name": "Shirts"},
                        {"id": 5, "name": "Tshirts"},
                        {"id": 15, "name": "Sweatshirts"}
                    ]
                }
            ]
        },
        {
            "id": 3,
            "name": "Footwear",
            "sub_categories": [
                {
                    "id": 5,
                    "name": "Shoes",
                    "article_types": [
                        {"id": 7, "name": "Casual Shoes"},
                        {"id": 17, "name": "Formal Shoes"},
                        {"id": 23, "name": "Sports Shoes"}
                    ]
                }
            ]
        }
    ]
}
