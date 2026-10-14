import random
import re
from discord.ext import tasks, commands
import discord
from datetime import time, datetime

from config import (
    JST,
    TARGET_CHANNELS,
    BLACKLIST,
    IGNORE_WORDS,
    LILI_USER_ID,
    NANA_USER_ID,
    is_in_target_area,
    can_use_slash,
)
from lines import MAKARON_TO_BOT, MAKARON_TO_HUMAN, MAKARON_DM_TO_HUMAN, MAKARON_DM_DEFAULT
from quiz_data import QUIZ_DATA
from voice import register_voice_commands
from roles import ensure_bot_role

# Bot専用ロールの設定
MAKARON_ROLE_NAME = "マカロン"
MAKARON_ROLE_COLOUR = discord.Colour(0x02ECA6)

# ===================================================================================================================================================================
# マカロン (Makaron) の構成
# ===================================================================================================================================================================
intents_maka = discord.Intents.default()
intents_maka.message_content = True


class MakaronBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="マカロン", intents=intents_maka)

    async def setup_hook(self):
        # ボイスチャンネル関連コマンド (/join, /leave, /play, /stop, /volume, /soundlist) を登録
        # 対象エリア または DM で使える判定(can_use_slash)を渡す
        register_voice_commands(self, "makaron", "マカロン", BLACKLIST, can_use_slash)
        await self.tree.sync()


bot_maka = MakaronBot()

ANNIVERSARIES = {
    (6, 29): "再会のリリース日",
    (9, 14): "約束のリリース日",
    (4, 26): "秘密のリリース日",
    (6, 18): "彗星になれたならのリリース日",
    (8, 26): "ふたりのアルバム＆誕生のリリース日",
    (10, 28): "深い青だったのリリース日",
    (4, 8): "ナナ＆リリ＆夜魔の一般公開記念日"
}


# ===================================================================================================================================================================
# クイズ ミニゲーム (問題データは quiz_data.py)
# ===================================================================================================================================================================
# ユーザーごとの成績を記録(Bot起動中のみ保持、再起動でリセット)
quiz_scores = {}


def normalize_answer(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    return text


class DifficultyView(discord.ui.View):
    """マカロンクイズの難易度選択ボタン"""

    def __init__(self, author: discord.Member):
        super().__init__(timeout=30)
        self.author = author
        self.level = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("ﾋﾞｯ(これはあなたのクイズじゃないよー)", ephemeral=True)
            return False
        return True

    async def _select(self, interaction: discord.Interaction, level: int):
        self.level = level
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=f"ピコッ！難易度{level}だね！", view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary)
    async def level1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._select(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary)
    async def level2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._select(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary)
    async def level3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._select(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary)
    async def level4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._select(interaction, 4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary)
    async def level5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._select(interaction, 5)


@bot_maka.command(name="クイズ")
async def quiz(ctx, level: int = None):
    if not is_in_target_area(ctx.channel):
        return

    if level is None:
        view = DifficultyView(ctx.author)
        prompt_msg = await ctx.send("ピコピコ！(難易度を選んでね(30秒以内))", view=view)
        await view.wait()

        if view.level is None:
            await prompt_msg.edit(content="ピ…(時間切れだよー)", view=view)
            return

        level = view.level

    if level not in QUIZ_DATA:
        await ctx.send("ピー！(その難易度はないよー(１～５の数字で選んでね))")
        return

    q = random.choice(QUIZ_DATA[level])

    if q["type"] == "choice":
        choices_text = "\n".join(f"{k}：{v}" for k, v in q["choices"].items())
        await ctx.send(f"【難易度{level}】{q['question']}\n{choices_text}\n(記号で答えてね／30秒以内)")
    else:
        await ctx.send(f"【難易度{level}】{q['question']}\n(30秒以内に答えてね)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot_maka.wait_for('message', timeout=30.0, check=check)
    except Exception:
        await ctx.send("ピ…(時間切れだよー)")
        return

    user_answer = normalize_answer(msg.content)

    if q["type"] == "choice":
        is_correct = user_answer.upper() == q["answer"]
        correct_text = f"{q['answer']}：{q['choices'][q['answer']]}"
    else:
        is_correct = user_answer in [normalize_answer(a) for a in q["answer"]]
        correct_text = q["answer"][0]

    stats = quiz_scores.setdefault(ctx.author.id, {"correct": 0, "total": 0})
    stats["total"] += 1

    if is_correct:
        stats["correct"] += 1
        await ctx.reply(f"ピコーン！(正解！)【現在 {stats['correct']}/{stats['total']} 問正解】")
    else:
        await ctx.reply(f"ﾋﾞﾋﾞｰｯ！(残念…)【現在 {stats['correct']}/{stats['total']} 問正解】")


@bot_maka.command(name="クイズ成績")
async def quiz_score(ctx):
    if not is_in_target_area(ctx.channel):
        return

    stats = quiz_scores.get(ctx.author.id)
    if not stats or stats["total"] == 0:
        await ctx.send("ﾋﾞﾋﾞｯ(まだクイズに挑戦してないよー)")
        return

    rate = stats["correct"] / stats["total"] * 100
    await ctx.send(f"ピコン！(これまで {stats['total']} 問中 {stats['correct']} 問正解！(正解率 {rate:.0f}%))")


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
    # 参加済みの全サーバーでBot専用ロールを作成・付与
    for guild in bot_maka.guilds:
        await ensure_bot_role(guild, MAKARON_ROLE_NAME, MAKARON_ROLE_COLOUR)
    if not check_anniversary_maka.is_running():
        check_anniversary_maka.start()


@bot_maka.event
async def on_guild_join(guild):
    # 新しくサーバーに招待されたときにBot専用ロールを作成・付与
    await ensure_bot_role(guild, MAKARON_ROLE_NAME, MAKARON_ROLE_COLOUR)


# ===================================================================================================================================================================
# メッセージへの反応 (対ボット / 対人間 / DM)
# ===================================================================================================================================================================
async def handle_bot(message):
    """Botからのメッセージへの反応"""
    # リリ・ナナ以外のBotには反応しない
    if message.author.id not in (LILI_USER_ID, NANA_USER_ID):
        return

    for k, v in MAKARON_TO_BOT.items():
        if k in message.content:
            await message.reply(v)
            return


async def handle_human(message):
    """人間からのメッセージへの反応"""
    for k, v in MAKARON_TO_HUMAN.items():
        if k in message.content:
            await message.reply(v)
            return


async def handle_dm(message):
    """DM専用の会話(セリフは lines.py の MAKARON_DM_* に書く)"""
    content = message.content
    for k, v in MAKARON_DM_TO_HUMAN.items():
        if k in content:
            await message.channel.send(v)
            return
    if MAKARON_DM_DEFAULT:
        await message.channel.send(random.choice(MAKARON_DM_DEFAULT))


@bot_maka.event
async def on_message(message):
    if message.author.id == bot_maka.user.id or message.author.id in BLACKLIST:
        return

    # DMは専用処理だけ行って終了(通常の返事・プレフィックスコマンドは動かさない)
    if message.guild is None:
        if not message.author.bot:
            await handle_dm(message)
        return

    if any(word in message.content for word in IGNORE_WORDS):
        return
    await bot_maka.process_commands(message)
    if not is_in_target_area(message.channel):
        return

    if message.author.bot:
        await handle_bot(message)
    else:
        await handle_human(message)


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
            await ctx.send("ピーー(形式が違うよー)")
            return
        n, s = map(int, msg.content.lower().split('d'))
        if n > 100:
            await ctx.send("ピピーー(多すぎるよー)")
            return
        rolls = [random.randint(1, s) for _ in range(n)]
        await ctx.reply(f"ピポパ！ 合計：**{sum(rolls)}**\n🎲 {rolls}")
    except Exception:
        await ctx.send("ピ？(エラーか時間切れだよ)")
