def format_property_details(property_details: list[dict]) -> str:
    """
    Formats a list of property details into a clean, minimal string.

    Args:
        property_details (list[dict]): List of property dictionaries.

    Returns:
        str: Formatted property summaries.
    """
    fields_to_show = [
        ("Property ID", "id"),
        ("Total Area (sqft)", "total_area"),
        ("Carpet Area (sqft)", "carpet_area"),
        ("Bedrooms", "no_of_bedrooms"),
        ("Bathrooms", "no_of_bathrooms"),
        ("Asking Price (₹)", "asking_price"),
        ("Building", "building_name"),
        ("Community", "community_name"),
        ("City", "city"),
    ]

    def format_value(value):
        if isinstance(value, (int, float)):
            return f"{value:,}"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value) if value is not None else "N/A"

    formatted_list = []

    for prop in property_details:
        lines = []
        for label, key in fields_to_show:
            value = format_value(prop.get(key))
            lines.append(f"{label}: {value}")
        formatted_list.append("\n".join(lines))

    return "\n\n" + ("\n" + "-" * 30 + "\n\n").join(formatted_list)
