import random
from discord.ext import tasks, commands
import discord
from datetime import time, datetime

from config import JST, TARGET_CHANNELS, BLACKLIST, IGNORE_WORDS, is_in_target_area

# ===================================================================================================================================================================
# マカロン (Makaron) の構成
# ===================================================================================================================================================================
intents_maka = discord.Intents.default()
intents_maka.message_content = True
bot_maka = commands.Bot(command_prefix="マカロン", intents=intents_maka)

ANNIVERSARIES = {
    (6, 29): "再会のリリース日",
    (9, 14): "約束のリリース日",
    (4, 26): "秘密のリリース日",
    (6, 18): "彗星になれたならのリリース日",
    (8, 26): "ふたりのアルバム＆誕生のリリース日",
    (10, 28): "深い青だったのリリース日",
    (4, 8): "ナナ＆リリ＆夜魔の一般公開記念日"
}


@tasks.loop(time=time(hour=0, minute=0, tzinfo=JST))
async def check_anniversary_maka():
    now = datetime.now(JST)
    date_key = (now.month, now.day)
    if date_key in ANNIVERSARIES:
        for cid in TARGET_CHANNELS:
            ch = bot_maka.get_channel(cid)
            if ch:
                await ch.send(f"ピコピコ！(今日は{ANNIVERSARIES[date_key]}なんだって！おめでとう！！)")


@bot_maka.event
async def on_ready():
    print(f"Makaron online: {bot_maka.user}")
    if not check_anniversary_maka.is_running():
        check_anniversary_maka.start()


@bot_maka.event
async def on_message(message):
    if message.author.id == bot_maka.user.id or message.author.id in BLACKLIST:
        return
    if any(word in message.content for word in IGNORE_WORDS):
        return
    await bot_maka.process_commands(message)


@bot_maka.command()
async def ping(ctx):
    if is_in_target_area(ctx.channel):
        await ctx.reply('ピポピポ')


@bot_maka.command()
async def サイコロ(ctx):
    if not is_in_target_area(ctx.channel):
        return
    await ctx.send("ピコピコピ？(どれくらい振ればいい？『1d6』みたいに教えてね)")
    try:
        msg = await bot_maka.wait_for(
            'message',
            timeout=60.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        if 'd' not in msg.content:
            await ctx.send("形式が違うよー")
            return
        n, s = map(int, msg.content.lower().split('d'))
        if n > 100:
            await ctx.send("多すぎるよー")
            return
        rolls = [random.randint(1, s) for _ in range(n)]
        await ctx.reply(f"ピポパ！ 合計：**{sum(rolls)}**\n🎲 {rolls}")
    except Exception:
        await ctx.send("ピ？(エラーか時間切れだよ)")
