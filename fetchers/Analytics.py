import requests
from datetime import datetime, timedelta
from typing import Dict

from ..tools.json_utils import json_dumps
from ..tools.exceptions import APIError, APIConnectionError


class TurnoverStocks:
    """Get stock turnover analytics."""

    def __init__(self, headers: Dict, date_since: str, date_to: str) -> None:
        self.headers = headers
        self.url = "https://api-seller.ozon.ru/v1/analytics/turnover/stocks"
        self.date_since = date_since
        self.date_to = date_to
        self.data = None

    def _request_body(self) -> str:
        body = {
            "date_from": self.date_since,
            "date_to": self.date_to,
        }
        return json_dumps(body)

    def run(self) -> None:
        try:
            result = requests.post(self.url, headers=self.headers, data=self._request_body())
        except ConnectionError:
            raise APIConnectionError()
        if result.status_code != 200:
            raise APIError(result.json().get("message", ""), result.status_code, self.url)
        self.data = result.json()
