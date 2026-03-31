import os
import requests
from crewai.tools import BaseTool


class LinkedInPublisherTool(BaseTool):
    name: str = "LinkedIn Publisher"
    description: str = """
    Publishes a post to the Komet LinkedIn company page.
    For image posts: provide image_url (from Nano Banana) and post_text.
    For carousel posts: provide pdf_url (from Contentdrips) and post_text.
    For text-only posts: provide post_text only.
    Returns: LinkedIn post URL on success.
    """

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {os.getenv('LINKEDIN_ACCESS_TOKEN')}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    def _upload_image(self, image_url: str) -> str:
        """Download image from URL and upload to LinkedIn. Returns asset URN."""
        org_id = os.getenv("LINKEDIN_ORG_ID")
        headers = self._get_headers()

        # Step 1: Initialise upload
        init_resp = requests.post(
            "https://api.linkedin.com/rest/images?action=initializeUpload",
            headers=headers,
            json={"initializeUploadRequest": {"owner": f"urn:li:organization:{org_id}"}}
        )
        upload_data = init_resp.json().get("value", {})
        upload_url = upload_data.get("uploadUrl", "")
        asset_urn = upload_data.get("image", "")

        # Step 2: Upload binary
        img_data = requests.get(image_url).content
        requests.put(upload_url, data=img_data,
                     headers={"Content-Type": "image/png"})

        return asset_urn

    def _upload_pdf(self, pdf_url: str) -> str:
        """Download PDF carousel and upload to LinkedIn. Returns asset URN."""
        org_id = os.getenv("LINKEDIN_ORG_ID")
        headers = self._get_headers()

        init_resp = requests.post(
            "https://api.linkedin.com/rest/documents?action=initializeUpload",
            headers=headers,
            json={"initializeUploadRequest": {"owner": f"urn:li:organization:{org_id}"}}
        )
        upload_data = init_resp.json().get("value", {})
        upload_url = upload_data.get("uploadUrl", "")
        asset_urn = upload_data.get("document", "")

        pdf_data = requests.get(pdf_url).content
        requests.put(upload_url, data=pdf_data,
                     headers={"Content-Type": "application/pdf"})

        return asset_urn

    def _run(self, post_text: str, image_url: str = None, pdf_url: str = None) -> str:
        org_id = os.getenv("LINKEDIN_ORG_ID")
        headers = self._get_headers()

        post_body = {
            "author": f"urn:li:organization:{org_id}",
            "commentary": post_text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        if image_url:
            asset_urn = self._upload_image(image_url)
            post_body["content"] = {
                "media": {"id": asset_urn}
            }
        elif pdf_url:
            asset_urn = self._upload_pdf(pdf_url)
            post_body["content"] = {
                "media": {"id": asset_urn, "title": ""}
            }

        response = requests.post(
            "https://api.linkedin.com/rest/posts",
            headers=headers,
            json=post_body
        )

        if response.status_code in (200, 201):
            post_id = response.headers.get("x-restli-id", "")
            return f"Published: https://www.linkedin.com/feed/update/{post_id}"
        else:
            return f"LinkedIn error {response.status_code}: {response.text[:300]}"
