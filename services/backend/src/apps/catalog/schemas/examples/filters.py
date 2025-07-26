FILTERS_FULL_EXAMPLE = {
    "gender": {
        "values": ["men", "women"],
        "type": "checkbox"
    },
    "year": {
        "min": 2020,
        "max": 2023,
        "type": "range"
    },
    "price": {
        "min": 29.99,
        "max": 299.99,
        "type": "price_range"
    },
    "is_available": {
        "available_count": 150,
        "unavailable_count": 25,
        "type": "boolean",
        "default": False
    }
}
