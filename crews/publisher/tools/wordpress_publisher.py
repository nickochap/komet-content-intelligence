import os
from crewai.tools import BaseTool


class WordPressPublisherTool(BaseTool):
    name: str = "WordPress Publisher"
    description: str = """
    Creates a WordPress DRAFT post on gokomet.com using the WordPress REST API.
    Input: JSON with fields: title, content, excerpt, status (always "draft"), tags.
    Returns: Draft post URL for Nick's final visual review.
    Never publishes live — always creates as draft.
    """

    def _run(self, title: str, content: str, excerpt: str, tags: list = None) -> str:
        import requests
        from base64 import b64encode

        domain = os.getenv("WORDPRESS_DOMAIN", "gokomet.com")
        username = os.getenv("WORDPRESS_USERNAME")
        app_password = os.getenv("WORDPRESS_APP_PASSWORD")

        credentials = b64encode(f"{username}:{app_password}".encode()).decode()

        response = requests.post(
            f"https://{domain}/wp-json/wp/v2/posts",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json"
            },
            json={
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": "draft",   # Always draft — never publish directly
                "tags": tags or [],
            }
        )

        if response.status_code in (200, 201):
            data = response.json()
            return f"Draft created: {data.get('link', '')} (ID: {data.get('id', '')})"
        else:
            return f"WordPress error {response.status_code}: {response.text[:300]}"
