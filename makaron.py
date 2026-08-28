import random
import re
from discord.ext import tasks, commands
import discord
from datetime import time, datetime

from config import JST, TARGET_CHANNELS, BLACKLIST, IGNORE_WORDS, is_in_target_area
from voice import register_voice_commands

# ===================================================================================================================================================================
# マカロン (Makaron) の構成
# ===================================================================================================================================================================
intents_maka = discord.Intents.default()
intents_maka.message_content = True


class MakaronBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="マカロン", intents=intents_maka)

    async def setup_hook(self):
        # ボイスチャンネル関連コマンド (/join, /leave, /play, /soundlist) を登録
        register_voice_commands(self, "makaron", "マカロン", BLACKLIST, is_in_target_area)
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
# クイズ ミニゲーム
# ===================================================================================================================================================================
# type: "choice"(選択式) or "text"(記述式)
QUIZ_DATA = {
    1: [
        {"type": "choice", "question": "ピコピコ(約束におけるリリとナナの年齢は？)",
         "choices": {"A": "十歳", "B": "八歳", "C": "六歳", "D": "七歳"}, "answer": "D"},
        {"type": "text", "question": "ﾋﾟﾋﾟｯ(リリのローマ字表記は？)",
         "answer": ["lili"]},
        {"type": "text", "question": "ピピー(黄金色は？)",
         "answer": ["リリ", "lili"]},
        {"type": "text", "question": "ピコ！(リリの好きなものは？)",
         "answer": ["おにぎり"]},
        {"type": "text", "question": "ピコﾋﾟ(マカロンの好きなものは？)",
         "answer": ["ハッピーエンド"]},
    ],
    2: [
        {"type": "choice", "question": "ピピー(リリースが一番遅いのは？)",
         "choices": {"A": "再会", "B": "彗星になれたなら", "C": "秘密", "D": "約束"}, "answer": "B"},
        {"type": "choice", "question": "ﾋﾟｺﾋﾟｰｺ(リリとナナ、初期デザインで身長が高いのは？)",
         "choices": {"A": "リリ", "B": "ナナ"}, "answer": "A"},
        {"type": "text", "question": "ピコピコ(アルバムには合計で何曲入ってる？(半角数字で))",
         "answer": ["22"]},
    ],
    3: [
        {"type": "text", "question": "ピピー(ふたりのの特設サイトのURLの末尾四文字は？)",
         "answer": ["ftr/"]},
        {"type": "choice", "question": "ピーー(再会のリリース日は？)",
         "choices": {
             "A": "2019/3/14",
             "B": "2019/6/29",
             "C": "2020/9/14",
             "D": "2020/6/29"
         }, "answer": "B"},
        {"type": "text", "question": "ピピピッ(彗星になれたならのトラック番号は何番？(半角数字で))",
         "answer": ["5"]},
    ],
    4: [
        {"type": "choice", "question": "ピピピ(幻影APの約束のディスクを欲しがってるスピカの名前は？)",
         "choices": {"A": "じゅんしんなスピカ", "B": "やくそくのスピカ", "C": "じゅんぼくなスピカ", "D": "じゅんすいなスピカ"}, "answer": "C"},
        {"type": "choice", "question": "ピピー(アートブックの再会のページ、右側は？)",
         "choices": {"A": "リリ", "B": "ナナ"}, "answer": "A"},
        {"type": "choice", "question": "ピッピッ(アートブックのリリとナナのページ、クロスフェードと一致しているのは？)",
         "choices": {"A": "リリ", "B": "ナナ"}, "answer": "A"},
        {"type": "choice", "question": "ピピピ(アートブックの誕生のページの左側には何が描かれている？)",
         "choices": {"A": "グランドピアノ", "B": "彗星", "C": "鯨", "D": "なにも描かれていない"}, "answer": "D"},
        {"type": "choice", "question": "ピー(はるまきごはん10周年イベントでのナナの担当は次のうちどれ？)",
         "choices": {"A": "ラインスタンプ", "B": "デジタルカード", "C": "わたしたちの足跡", "D": "担当していない"}, "answer": "A"},
        {"type": "text", "question": "ﾋﾟｺ！(約束のテーマは？)",
         "answer": ["純粋"]},
    ],
    5: [
        {"type": "text", "question": "ﾋﾟｺﾋﾟｰｺ(アートブック11ページ目の絵のタイトルは？正式名称で答えてね)",
         "answer": ["夜長のピクニック"]},
        {"type": "choice", "question": "ピピピー(幻影APで合言葉をリリに教える時の選択肢として正しくないのはどれ？)",
         "choices": {"A": "数年前のヒットソング", "B": "309へ集合", "C": "ダークマター", "D": "案外そんなフューチャー"}, "answer": "A"},
        {"type": "text", "question": "ピピピッ！(幻影APの再会のディスクを欲しがっているスピカの名前は？正式名称で答えてね)",
         "answer": ["めぐりあうスピカ"]},
        {"type": "text", "question": "ピｺーﾝ！(アートブックの正式名称は？)",
         "answer": ["スペシャル絵本アートブック「ふたりの」"]},
        {"type": "text", "question": "ピピ(歌詞中に出てくる「！」の数は？)",
         "answer": ["3", "３"]},
    ],
}

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
