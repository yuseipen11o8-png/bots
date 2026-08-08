print("MAIN.PY START")

import os
import asyncio

from keep_alive import keep_alive
from lili import bot_lili
from nana import bot_nana
from makaron import bot_maka

# ==================================================================================================================
# 統合実行セクション
# ==================================================================================================================


async def start_bot_safe(bot, token, name):
    if not token:
        print(f"[{name}] トークンが設定されていません。")
        return
    try:
        await bot.start(token)
    except Exception as e:
        print(f"[{name}] 起動エラー: {e}")


async def start_all():
    print("START_ALL 実行開始")

    keep_alive()

    tokens = {
        "LILI": os.getenv("TOKEN_LILI"),
        "NANA": os.getenv("TOKEN_NANA"),
        "MAKARON": os.getenv("TOKEN_MAKARON"),
    }

    print("TOKEN_LILI:", tokens["LILI"] is not None)
    print("TOKEN_NANA:", tokens["NANA"] is not None)
    print("TOKEN_MAKARON:", tokens["MAKARON"] is not None)

    # 各Botを独立したタスクとして起動
    bot_tasks = [
        asyncio.create_task(start_bot_safe(bot_lili, tokens["LILI"], "Lili")),
        asyncio.create_task(start_bot_safe(bot_nana, tokens["NANA"], "Nana")),
        asyncio.create_task(start_bot_safe(bot_maka, tokens["MAKARON"], "Makaron")),
    ]

    await asyncio.gather(*bot_tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        pass
