import os
from datetime import datetime, timedelta
from vot.fetchers.Analytics import TurnoverStocks
from vot.tools.json_utils import json_dumps


def main() -> None:
    headers = {
        "Client-Id": os.getenv("OZON_CLIENT_ID", ""),
        "Api-Key": os.getenv("OZON_API_KEY", ""),
    }
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")

    stocks = TurnoverStocks(headers, start_str, end_str)
    stocks.run()

    os.makedirs("mock", exist_ok=True)
    with open(os.path.join("mock", "turnover_stocks.json"), "w", encoding="utf-8") as f:
        f.write(json_dumps(stocks.data))


if __name__ == "__main__":
    main()

