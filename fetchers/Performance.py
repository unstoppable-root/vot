import requests
from typing import List, Dict, Any, Optional

from ..tools.exceptions import APIError, APIConnectionError


class OzonPerformanceAPI:
    """Client for Ozon Performance API."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://api-performance.ozon.ru/api/client/token"
        self.stats_url = "https://performance.ozon.ru/api/client/statistics/json"
        self.access_token: Optional[str] = None

    def obtain_token(self) -> str:
        """Retrieve access token using client credentials."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            result = requests.post(self.token_url, headers=headers, json=data)
        except ConnectionError:
            raise APIConnectionError()
        if result.status_code != 200:
            raise APIError(result.text, result.status_code, self.token_url)
        token = result.json().get("access_token")
        if not token:
            raise APIError("Token not found in response", result.status_code, self.token_url)
        self.access_token = token
        return token

    def get_statistics(
        self,
        campaigns: List[str],
        date_from: str,
        date_to: str,
        group_by: str = "NO_GROUP_BY",
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get statistics for campaigns."""
        if token is None:
            token = self.access_token or self.obtain_token()
        payload = {
            "campaigns": campaigns,
            "from": date_from,
            "to": date_to,
            "dateFrom": date_from.split("T")[0],
            "dateTo": date_to.split("T")[0],
            "groupBy": group_by,
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            result = requests.post(self.stats_url, headers=headers, json=payload)
        except ConnectionError:
            raise APIConnectionError()
        if result.status_code != 200:
            raise APIError(result.text, result.status_code, self.stats_url)
        return result.json()
