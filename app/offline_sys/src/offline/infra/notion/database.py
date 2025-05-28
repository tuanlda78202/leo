import json
from typing import Any

import requests
from loguru import logger

from offline.config import settings
from offline.domain import DocumentMetaData


class NotionDatabaseClient:
    """Client for interacting with Notion databases (GET metadata)"""

    def __init__(self, api_key: str | None = settings.NOTION_SECRET_KEY) -> None:
        assert api_key is not None, "Notion API key is required"
        self.api_key = api_key

    def query_notion_db(
        self, database_id: str, query_json: str | None = None
    ) -> list[DocumentMetaData]:
        """Query a Notion database"""

        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

        # query_json is optional string containing query parameters
        query_payload = {}
        if query_json and query_json.strip():
            try:
                query_payload = json.loads(query_json)
            except json.JSONDecodeError:
                logger.opt(exception=True).debug("Invalid JSON format for query")
                return []

        try:
            response = requests.post(
                url, headers=headers, json=query_payload, timeout=10
            )
            response.raise_for_status()
            results = response.json()
            results = results["results"]
        except requests.exceptions.RequestException:
            logger.opt(exception=True).debug("Error querying Notion database")
            return []
        except KeyError:
            logger.opt(exception=True).debug(
                "Unexpected response format from Notion API"
            )
            return []
        except Exception:  # noqa: BLE001
            logger.opt(exception=True).debug("Error querying Notion database")
            return []

        return [self.__build_page_metadata(page) for page in results]

    def __build_page_metadata(self, page: dict[str, Any]) -> DocumentMetaData:
        """Build a PageMetadata from a Notion page"""

        properties = self.__flatten_properties(page.get("properties", {}))
        title = properties.pop("Name")

        if page.get("parent"):
            properties["parent"] = {
                "id": page["parent"]["database_id"],
                "url": "",
                "title": "",
                "properties": {},
            }

        return DocumentMetaData(
            id=page["id"], url=page["url"], title=title, properties=properties
        )

    def __flatten_properties(self, properties: dict) -> dict:
        """Flatten Notion properties dictionary into a simpler key-value format.

        Example:
            Input: {
                'Type': {'type': 'select', 'select': {'name': 'Leaf'}},
                'Name': {'type': 'title', 'title': [{'plain_text': 'Merging'}]}
            }
            Output: {
                'Type': 'Leaf',
                'Name': 'Merging'
            }
        """
        flattened = {}

        for key, value in properties.items():
            prop_type = value.get("type")

            if prop_type == "select":
                select_value = value.get("select", {}) or {}
                flattened[key] = select_value.get("name")
            elif prop_type == "multi_select":
                flattened[key] = [
                    item.get("name") for item in value.get("multi_select", [])
                ]
            elif prop_type == "title":
                flattened[key] = "\n".join(
                    item.get("plain_text", "") for item in value.get("title", [])
                )
            elif prop_type == "rich_text":
                flattened[key] = " ".join(
                    item.get("plain_text", "") for item in value.get("rich_text", [])
                )
            elif prop_type == "number":
                flattened[key] = value.get("number")
            elif prop_type == "checkbox":
                flattened[key] = value.get("checkbox")
            elif prop_type == "date":
                date_value = value.get("date", {})
                if date_value:
                    flattened[key] = {
                        "start": date_value.get("start"),
                        "end": date_value.get("end"),
                    }
            elif prop_type == "database_id":
                flattened[key] = value.get("database_id")
            else:
                flattened[key] = value

        return flattened
