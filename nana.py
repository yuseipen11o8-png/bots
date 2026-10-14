import asyncio
import random
import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, datetime, timedelta

from config import (
    JST,
    TARGET_CHANNELS,
    BLACKLIST,
    IGNORE_WORDS,
    LILI_USER_ID,
    MAKARON_USER_ID,
    is_in_target_area,
    can_use_slash,
)
from lines import (
    NANA_TO_LILI,
    NANA_TO_MAKARON,
    NANA_TO_HUMAN,
    NANA_TO_HUMAN_MULTI,
    NANA_FUTARINO_REPLIES,
    NANA_CALL_WORDS,
    NANA_CALL_REPLY,
    NANA_LOLI_REPLY,
    LOLI_NANA_WORDS,
    NANA_DM_TO_HUMAN,
    NANA_DM_DEFAULT,
)
from roles import ensure_bot_role
from slash_data import NANA_COMMANDS

# Bot専用ロールの設定
NANA_ROLE_NAME = "ナナ"
NANA_ROLE_COLOUR = discord.Colour(0x2066B3)

# ==================================================================================================================================================================
# ナナ (Nana) の構成
# ==================================================================================================================================================================
intents_nana = discord.Intents.default()
intents_nana.message_content = True


class NanaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ナナ", intents=intents_nana)
        self.last_human_msg_times = {}

    async def setup_hook(self):
        for cmd_name, data in NANA_COMMANDS.items():
            response_text = data[0]
            description_text = data[1]

            def make_callback(resp: str):
                async def create_callback(interaction: discord.Interaction):
                    if interaction.user.id in BLACKLIST:
                        await interaction.response.send_message("……。", ephemeral=True)
                        return

                    # 対象エリア または DM なら返事をする
                    if can_use_slash(interaction.channel):
                        await interaction.response.send_message(resp)
                    else:
                        await interaction.response.send_message(
                            "ここではお話しできないよ。",
                            ephemeral=True
                        )

                return create_callback

            self.tree.add_command(
                app_commands.Command(
                    name=cmd_name,
                    description=description_text,
                    callback=make_callback(response_text),
                )
            )

        await self.tree.sync()


bot_nana = NanaBot()


@tasks.loop(time=time(hour=17, minute=0, tzinfo=JST))
async def bell_nana():
    for cid in TARGET_CHANNELS:
        ch = bot_nana.get_channel(cid)
        if ch:
            await asyncio.sleep(1.0)
            await ch.send("タイムリミットの鐘が鳴る…")

@tasks.loop(time=time(hour=3, minute=0, tzinfo=JST))
async def yoma_nana():
    for cid in TARGET_CHANNELS:
        ch = bot_nana.get_channel(cid)
        if ch:
            await asyncio.sleep(1.0)
            await ch.send("届かぬ手紙を書いている…")


@tasks.loop(minutes=30)
async def lonely_check_nana():
    now = datetime.now(JST)
    for cid in TARGET_CHANNELS:
        last_at = bot_nana.last_human_msg_times.get(cid)
        if last_at and now - last_at > timedelta(hours=24):
            ch = bot_nana.get_channel(cid)
            if ch:
                await ch.send("これほどの時間が経って世界はずっと止まっている…")
                bot_nana.last_human_msg_times[cid] = now


@bot_nana.event
async def on_ready():
    print(f"Nana online: {bot_nana.user}")
    # 参加済みの全サーバーでBot専用ロールを作成・付与
    for guild in bot_nana.guilds:
        await ensure_bot_role(guild, NANA_ROLE_NAME, NANA_ROLE_COLOUR)
    if not bell_nana.is_running():
        bell_nana.start()
    if not yoma_nana.is_running():
        yoma_nana.start()
    if not lonely_check_nana.is_running():
        lonely_check_nana.start()


@bot_nana.event
async def on_guild_join(guild):
    # 新しくサーバーに招待されたときにBot専用ロールを作成・付与
    await ensure_bot_role(guild, NANA_ROLE_NAME, NANA_ROLE_COLOUR)


# ==================================================================================================================================================================
# メッセージへの反応 (対ボット / 対人間 / DM)
# ==================================================================================================================================================================
async def handle_bot(message):
    """Botからのメッセージへの反応(リリとの掛け合い・マカロンの記念日通知)"""
    content = message.content

    if message.author.id == LILI_USER_ID:
        reply = NANA_TO_LILI.get(content)
        if reply:
            await asyncio.sleep(2.0 if "だれもいない" in content else 1.0)
            await message.reply(reply)
        elif content == "てことは今日は私たちの誕生日みたいなものなのかなぁ…":
            await asyncio.sleep(1.0)
            await message.reply(f"たしかにね～\nもう{datetime.now(JST).year-2019}年も経つのかぁ…")

    elif message.author.id == MAKARON_USER_ID:
        for key, reply in NANA_TO_MAKARON.items():
            if key in content:
                await asyncio.sleep(1.0)
                await message.reply(reply)
                break


async def handle_human(message):
    """人間からのメッセージへの反応"""
    content = message.content
    bot_nana.last_human_msg_times[message.channel.id] = datetime.now(JST)

    # 「たしかに」リアクションは人間のみ
    if "たしかに" in content:
        try:
            await message.add_reaction("<:kani:1488576524381847663>")
        except Exception:
            pass

    # 「ロリなな」系(文字数に関係なく反応)
    if any(ki in content for ki in LOLI_NANA_WORDS):
        await message.reply(NANA_LOLI_REPLY)
        return

    # 長文(100文字以上)
    if len(content) >= 100:
        await message.reply(f"{len(content)}文字もあるよ～")
        return

    # 短文(30文字以下)のみ、キーワードに反応
    if len(content) <= 30:
        # 1キーワード → 1返事
        for k, v in NANA_TO_HUMAN.items():
            if k in content:
                await message.reply(v)
                return

        # 複数キーワード → 1返事(最初に一致したものだけ。返事のあとも下の判定は続く)
        for words, reply in NANA_TO_HUMAN_MULTI:
            if any(w in content for w in words):
                await message.reply(reply)
                break

        # 「ふたりの」だけ言われたらランダムで返す
        if content == "ふたりの":
            await message.reply(random.choice(NANA_FUTARINO_REPLIES))

        # 「7」系ワード(メンションなしの時のみ)
        if not message.mentions and any(ke in content for ke in NANA_CALL_WORDS):
            await message.reply(NANA_CALL_REPLY)


async def handle_dm(message):
    """DM専用の会話(セリフは lines.py の NANA_DM_* に書く)"""
    content = message.content
    for k, v in NANA_DM_TO_HUMAN.items():
        if k in content:
            await message.channel.send(v)
            return
    if NANA_DM_DEFAULT:
        await message.channel.send(random.choice(NANA_DM_DEFAULT))


@bot_nana.event
async def on_message(message):
    if message.author.id == bot_nana.user.id or message.author.id in BLACKLIST:
        return

    # DMは専用処理だけ行って終了(通常の返事・プレフィックスコマンドは動かさない)
    if message.guild is None:
        if not message.author.bot:
            await handle_dm(message)
        return

    if any(word in message.content for word in IGNORE_WORDS):
        return
    if not is_in_target_area(message.channel):
        return
    await bot_nana.process_commands(message)

    if message.author.bot:
        await handle_bot(message)
    else:
        await handle_human(message)
