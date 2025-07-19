INVENTORY_EXAMPLE1 = {
    "id": 1,
    "product_id": 1,
    "base_price": "99.99",
    "sale_price": "79.99",
    "currency": "USD",
    "stock_quantity": 50,
    "reserved_quantity": 5,
    "available_quantity": 45,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-12-01T10:30:00",
    "updated_at": "2023-12-15T14:20:00"
}

INVENTORY_EXAMPLE2 = {
    "id": 2,
    "product_id": 2,
    "base_price": "49.99",
    "sale_price": None,
    "currency": "USD",
    "stock_quantity": 25,
    "reserved_quantity": 2,
    "available_quantity": 23,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-11-20T09:15:00",
    "updated_at": "2023-12-10T16:45:00"
}

INVENTORY_EXAMPLE3 = {
    "id": 3,
    "product_id": 3,
    "base_price": "35.99",
    "sale_price": "29.99",
    "currency": "USD",
    "stock_quantity": 100,
    "reserved_quantity": 10,
    "available_quantity": 90,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-10-15T11:00:00",
    "updated_at": "2023-12-05T13:30:00"
}

INVENTORY_EXAMPLE5 = {
    "id": 5,
    "product_id": 5,
    "base_price": "89.99",
    "sale_price": "69.99",
    "currency": "USD",
    "stock_quantity": 30,
    "reserved_quantity": 3,
    "available_quantity": 27,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-09-10T08:20:00",
    "updated_at": "2023-11-25T10:15:00"
}

INVENTORY_EXAMPLE8 = {
    "id": 8,
    "product_id": 8,
    "base_price": "79.99",
    "sale_price": None,
    "currency": "USD",
    "stock_quantity": 15,
    "reserved_quantity": 1,
    "available_quantity": 14,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-08-05T12:45:00",
    "updated_at": "2023-12-01T09:30:00"
}

INVENTORY_EXAMPLE14 = {
    "id": 14,
    "product_id": 14,
    "base_price": "199.99",
    "sale_price": "149.99",
    "currency": "USD",
    "stock_quantity": 8,
    "reserved_quantity": 2,
    "available_quantity": 6,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-07-20T14:00:00",
    "updated_at": "2023-11-30T11:20:00"
}

INVENTORY_EXAMPLE17 = {
    "id": 17,
    "product_id": 17,
    "base_price": "159.99",
    "sale_price": "129.99",
    "currency": "USD",
    "stock_quantity": 20,
    "reserved_quantity": 4,
    "available_quantity": 16,
    "is_active": True,
    "is_in_stock": True,
    "created_at": "2023-06-15T16:30:00",
    "updated_at": "2023-12-08T15:10:00"
}

PRODUCT_EXAMPLE1 = {
    "product_id": 1,
    "gender": "Men",
    "year": 2023,
    "product_display_name": "Running Shoes",
    "image_url": "https://example.com/product1.jpg",
    "slug": "running-shoes-1",
    "inventory": INVENTORY_EXAMPLE1
}

PRODUCT_EXAMPLE2 = {
    "product_id": 2,
    "gender": "Women",
    "year": 2022,
    "product_display_name": "Comfortable Sandals",
    "image_url": "https://example.com/product2.jpg",
    "slug": "comfortable-sandals-2",
    "inventory": INVENTORY_EXAMPLE2
}

PRODUCT_EXAMPLE3 = {
    "product_id": 3,
    "gender": "Women",
    "year": 2023,
    "product_display_name": "Floral Blouse",
    "image_url": "https://example.com/product3.jpg",
    "slug": "floral-blouse-3",
    "inventory": INVENTORY_EXAMPLE3
}

PRODUCT_EXAMPLE5 = {
    "product_id": 5,
    "gender": "Men",
    "year": 2020,
    "product_display_name": "Classic Denim Jeans",
    "image_url": "https://example.com/product5.jpg",
    "slug": "classic-denim-jeans-5",
    "inventory": INVENTORY_EXAMPLE5
}

PRODUCT_EXAMPLE8 = {
    "product_id": 8,
    "gender": "Women",
    "year": 2020,
    "product_display_name": "Summer Dress",
    "image_url": "https://example.com/product8.jpg",
    "slug": "summer-dress-8",
    "inventory": INVENTORY_EXAMPLE8
}

PRODUCT_EXAMPLE14 = {
    "product_id": 14,
    "gender": "Men",
    "year": 2021,
    "product_display_name": "Leather Jacket",
    "image_url": "https://example.com/product14.jpg",
    "slug": "leather-jacket-14",
    "inventory": INVENTORY_EXAMPLE14
}

PRODUCT_EXAMPLE17 = {
    "product_id": 17,
    "gender": "Men",
    "year": 2020,
    "product_display_name": "Winter Coat",
    "image_url": "https://example.com/product17.jpg",
    "slug": "winter-coat-17",
    "inventory": INVENTORY_EXAMPLE17
}

PRODUCT_EXAMPLE_NO_INVENTORY = {
    "product_id": 99,
    "gender": "Unisex",
    "year": 2024,
    "product_display_name": "Out of Stock Item",
    "image_url": "https://example.com/product99.jpg",
    "slug": "out-of-stock-item-99",
    "inventory": None
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
                        {"id": 5, "name": "T-shirts"},
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
