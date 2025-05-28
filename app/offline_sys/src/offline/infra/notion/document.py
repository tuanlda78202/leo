import requests
from loguru import logger

from offline.config import settings
from offline.domain import Document, DocumentMetaData


class NotionDocumentClient:
    """Client for interacting with Notion API to extract document content.

    This class handles retrieving and parsing Notion pages, including their blocks,
    rich text content, and embedded URLs.
    """

    def __init__(self, api_key: str | None = settings.NOTION_SECRET_KEY):
        assert api_key is not None, (
            "NOTION_SECRET_KEY environment variable is required. Set it in your .env file."
        )
        self.api_key = api_key

    def extract_docs(self, document_metadata: DocumentMetaData) -> Document:
        """Extract content from a Notion document.

        Args:
            document_metadata: Metadata about the document to extract.

        Returns:
            Document: A Document object containing the extracted content and metadata.
        """

        blocks = self.__retrieve_child_blocks(document_metadata.id)
        content, urls = self.__parse_blocks(blocks)

        parent_metadata = document_metadata.properties.pop("parent", None)

        if parent_metadata:
            parent_metadata = DocumentMetaData(
                id=parent_metadata["id"],
                url=parent_metadata["url"],
                title=parent_metadata["title"],
                properties=parent_metadata["properties"],
            )

        return Document(
            id=document_metadata.id,
            metadata=document_metadata,
            parent_metadata=parent_metadata,
            content=content,
            child_urls=urls,
        )

    def __retrieve_child_blocks(
        self, block_id: str, page_size: int = 100
    ) -> list[dict]:
        """Retrieve child blocks from a Notion block.

        Args:
            block_id: The ID of the block to retrieve children from.
            page_size: Number of blocks to retrieve per request.

        Returns:
            list[dict]: List of block data.
        """

        blocks_url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size={page_size}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
        }
        try:
            blocks_response = requests.get(blocks_url, headers=headers, timeout=10)
            blocks_response.raise_for_status()
            blocks_data = blocks_response.json()
            return blocks_data.get("results", [])
        except requests.exceptions.RequestException as e:
            error_message = f"Error: Failed to retrieve Notion page content. {e}"
            if hasattr(e, "response") and e.response is not None:
                error_message += f" Status code: {e.response.status_code}, Response: {e.response.text}"
            logger.exception(error_message)
            return []
        except Exception:
            logger.exception("Error retrieving Notion page content")
            return []

    def __parse_blocks(
        self, blocks: list[dict], depth: int = 0
    ) -> tuple[str, list[str]]:
        """Parse Notion blocks into text content and extract URLs.

        Args:
            blocks: List of Notion block objects to parse.
            depth: Current recursion depth for parsing nested blocks.

        Returns:
            tuple[str, list[str]]: A tuple containing:
                - Parsed text content as a string
                - List of extracted URLs
        """
        content = ""
        urls = []
        for block in blocks:
            block_type = block.get("type")
            block_id = block.get("id")

            if block_type in {
                "heading_1",
                "heading_2",
                "heading_3",
            }:
                content += f"# {self.__parse_rich_text(block[block_type].get('rich_text', []))}\n\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type in {
                "paragraph",
                "quote",
            }:
                content += f"{self.__parse_rich_text(block[block_type].get('rich_text', []))}\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type in {"bulleted_list_item", "numbered_list_item"}:
                content += f"- {self.__parse_rich_text(block[block_type].get('rich_text', []))}\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type == "toggle":
                content += f"▸ {self.__parse_rich_text(block['toggle'].get('rich_text', []))}\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type == "to_do":
                content += f"[] {self.__parse_rich_text(block['to_do'].get('rich_text', []))}\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type == "code":
                content += f"```\n{self.__parse_rich_text(block['code'].get('rich_text', []))}\n```\n"
                urls.extend(self.__extract_urls(block[block_type].get("rich_text", [])))
            elif block_type == "image":
                content += f"[Image]({block['image'].get('external', {}).get('url', 'No URL')})\n"
            elif block_type == "divider":
                content += "---\n\n"
            elif block_type == "child_page" and depth < 3:
                child_id = block["id"]
                child_title = block.get("child_page", {}).get("title", "Untitled")
                content += f"\n\n<child_page>\n# {child_title}\n\n"

                child_blocks = self.__retrieve_child_blocks(child_id)
                child_content, child_urls = self.__parse_blocks(child_blocks, depth + 1)
                content += child_content + "\n</child_page>\n\n"
                urls += child_urls

            elif block_type == "link_preview":
                url = block.get("link_preview", {}).get("url", "")
                content += f"[Link Preview]({url})\n"

                urls.append(self.__normalize_url(url))
            else:
                logger.warning(f"Unknown block type: {block_type}")

            # Parse child pages that are bullet points, toggles or similar structures.
            # Sub-pages (child_page) are parsed individually as a block.
            if (
                block_type != "child_page"
                and "has_children" in block
                and block["has_children"]
            ):
                child_blocks = self.__retrieve_child_blocks(block_id)
                child_content, child_urls = self.__parse_blocks(child_blocks, depth + 1)
                content += (
                    "\n".join("\t" + line for line in child_content.split("\n"))
                    + "\n\n"
                )
                urls += child_urls

        urls = list(set(urls))

        return content.strip("\n "), urls

    def __parse_rich_text(self, rich_text: list[dict]) -> str:
        """Parse Notion rich text blocks into plain text with markdown formatting.

        Args:
            rich_text: List of Notion rich text objects to parse.

        Returns:
            str: Formatted text content.
        """
        text = ""
        for segment in rich_text:
            if segment.get("href"):
                text += f"[{segment.get('plain_text', '')}]({segment.get('href', '')})"
            else:
                text += segment.get("plain_text", "")
        return text

    def __extract_urls(self, rich_text: list[dict]) -> list[str]:
        """Extract URLs from Notion rich text blocks.

        Args:
            rich_text: List of Notion rich text objects to extract URLs from.

        Returns:
            list[str]: List of normalized URLs found in the rich text.
        """
        urls = []
        for text in rich_text:
            url = None
            if text.get("href"):
                url = text["href"]
            elif "url" in text.get("annotations", {}):
                url = text["annotations"]["url"]

            if url:
                urls.append(self.__normalize_url(url))

        return urls

    def __normalize_url(self, url: str) -> str:
        """Normalize a URL by ensuring it ends with a forward slash.

        Args:
            url: URL to normalize.

        Returns:
            str: Normalized URL with trailing slash.
        """
        if not url.endswith("/"):
            url += "/"
        return url
