"""
Mapping of New Relic condition IDs to their documentation URLs.
This allows the agent to include relevant documentation links in Slack notifications.
"""

# Map conditionId to documentation URL
CONDITION_DOCUMENTATION = {
    "27856185": {
        "condition_name": "jhire Null Pointer Anomaly",
        "doc_url": "https://employinc.atlassian.net/wiki/spaces/ENG/pages/4633165861/TransactionError+query+deviated+from+the+baseline+for+at+least+5+minutes+on+jhire+Null+Pointer+Anomaly",
        "doc_title": "TransactionError NPE Baseline Deviation - jhire"
    },
    "29840004": {
        "condition_name": "Jhire Error Percentage - With exclusions",
        "doc_url": "https://employinc.atlassian.net/wiki/spaces/ENG/pages/4601544769/Jhire+Error+Percentage+-+With+exclusions",  # Add documentation URL when available
        "doc_title": ""
    },
    "29840110": {
        "condition_name": "Jhire JSP Error Percentage",
        "doc_url": "",  # Add documentation URL when available
        "doc_title": ""
    },
    "25363002": {
        "condition_name": "TeamAlpha-Jhire-Action",
        "doc_url": "",  # Add documentation URL when available
        "doc_title": ""
    },
    "25339360": {
        "condition_name": "TeamAlpha-jhire BTResponseTime",
        "doc_url": "",  # Add documentation URL when available
        "doc_title": ""
    },
    "24890919": {
        "condition_name": "TeamAlpha-Jhire-ResponseTime",
        "doc_url": "",  # Add documentation URL when available
        "doc_title": ""
    },
    # Add more condition mappings here as you document them
}


def get_condition_documentation(condition_id):
    """
    Get documentation information for a given condition ID.

    Args:
        condition_id: The New Relic condition ID (as string)

    Returns:
        Dictionary with doc_url and doc_title, or None if not found
    """
    condition_id_str = str(condition_id)
    return CONDITION_DOCUMENTATION.get(condition_id_str)


def has_documentation(condition_id):
    """
    Check if a condition has documentation available.

    Args:
        condition_id: The New Relic condition ID

    Returns:
        Boolean indicating if documentation exists and has a URL
    """
    doc_info = get_condition_documentation(condition_id)
    return doc_info is not None and doc_info.get('doc_url', '').strip() != ''


def add_condition_documentation(condition_id, condition_name, doc_url, doc_title=""):
    """
    Helper function to add a new condition documentation mapping.
    This is for reference - actual mappings should be added to CONDITION_DOCUMENTATION dict.

    Args:
        condition_id: The New Relic condition ID
        condition_name: Human-readable condition name
        doc_url: URL to the documentation page
        doc_title: Optional title for the documentation
    """
    print(f"""
Add this to CONDITION_DOCUMENTATION in condition_docs_mapping.py:

    "{condition_id}": {{
        "condition_name": "{condition_name}",
        "doc_url": "{doc_url}",
        "doc_title": "{doc_title}"
    }},
    """)

