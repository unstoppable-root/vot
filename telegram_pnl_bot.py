import os
import json
from datetime import datetime, timedelta
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from vot.fetchers.Finance import AsyncFinanceRealizationList
from vot.fetchers.Performance import OzonPerformanceAPI


def calculate_pnl(operations) -> float:
    return sum(float(op.get('amount', 0)) for op in operations)


async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    headers = {
        "Client-Id": os.getenv("OZON_CLIENT_ID", ""),
        "Api-Key": os.getenv("OZON_API_KEY", ""),
    }
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    start_str = start.strftime("%Y.%m.%d")
    end_str = end.strftime("%Y.%m.%d")

    finance = AsyncFinanceRealizationList(headers, start_str, end_str)
    await finance.run_in_jupyter()
    pnl_value = calculate_pnl(finance.data)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"PNL за неделю: {pnl_value}")


async def ads_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client_id = os.getenv("OZON_PERF_CLIENT_ID", "")
    client_secret = os.getenv("OZON_PERF_CLIENT_SECRET", "")
    campaigns = os.getenv("OZON_PERF_CAMPAIGNS", "123456789").split(",")

    end = datetime.utcnow()
    start = end - timedelta(days=7)
    start_iso = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = end.strftime("%Y-%m-%dT%H:%M:%SZ")

    api = OzonPerformanceAPI(client_id, client_secret)

    def fetch_stats() -> dict:
        token = api.obtain_token()
        return api.get_statistics(campaigns, start_iso, end_iso, token=token)

    result = await asyncio.to_thread(fetch_stats)
    uuid = result.get("UUID")
    with open("ozon_statistics.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("ozon_statistics.json", "rb"),
        filename="ozon_statistics.json",
        caption=f"Статистика получена. UUID: {uuid}",
    )


def main() -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler("pnl", pnl_command))
    application.add_handler(CommandHandler("ads_stats", ads_stats_command))
    application.run_polling()


if __name__ == "__main__":
    main()

