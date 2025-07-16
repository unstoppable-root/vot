import os
from datetime import datetime, timedelta
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from vot.fetchers.Finance import AsyncFinanceRealizationList


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


def main() -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler("pnl", pnl_command))
    application.run_polling()


if __name__ == "__main__":
    main()

