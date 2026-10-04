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
)

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
        NANA_COMMANDS = {
            "hello": ["こんにちは～", "ナナが挨拶します"],
            "good_night": ["みんなおやすみ～！", "ナナが挨拶します"],
            "good_morning": ["おはよう～", "ナナが挨拶します"],
            "go_to_bed": ["まだ寝てないの～？", "ナナが注意します"],
            "nice_picture": ["すごいきれい…", "ナナが絵を褒めます"],
            "nice_food": ["", "ナナが食事を褒めます"],
            "bye": ["さよなら～またね～", "ナナが挨拶します"],
            "turn_off": ["えぇ………", "ナナがドン引きします"],
            "sad": ["やめてよ…！", "ナナが悲しみます"],
            "happy": ["いえーい！", "ナナが喜びます"],
            "angry": ["ちょっと！", "ナナが怒ります"],
            "feel_shy": ["てへへへ…", "ナナが照れます"],
            "surprised": ["うわっ！！", "ナナが驚きます"],
            "sorry": ["ごめんね…", "ナナが謝ります"],
            "smile": ["ふふふ～", "ナナが笑います"],
            "cry": ["うぁわーん！", "ナナが泣きます"],
            "panic": ["どうしよう…", "ナナが慌てます"],
            "worry": ["どうしたの…？", "ナナが心配します"],
            "what": ["なんだろう…？", "ナナが疑問に思います"],
            "hurry_up": ["早く早く～", "ナナが急かします"],
            "good_luck": ["頑張って！", "ナナが応援します"],
            "wait": ["待ってて～", "ナナが待って欲しそうにします"],
            "hungry": ["何か食べた～い", "ナナがお腹を空かせます"],
            "think": ["う～ん", "ナナが考え込みます"],
            "sleep": ["すやすや…", "ナナが寝ます"],
            "silent": ["…", "ナナが黙ります"],
            "confused": ["え？？", "ナナが混乱します"],
            "tired": ["はー疲れた！", "ナナが疲れます"],
            "bored": ["つまんな～い", "ナナがつまらなさそうにします"],
            "sneeze": ["くしゅっ！", "ナナがくしゃみをします"],
            "agree": ["いいじゃん！", "ナナが賛成します"],
            "disagree": ["ええ～？", "ナナが反対します"],
            "failure": ["うぅ…", "ナナが落ち込みます"],
            "success": ["やった！", "ナナが喜びます"],
            "nod": ["うんうん！", "ナナが頷きます"],
            "eating": ["もぐもぐ…", "ナナが食事をします"],
            "drinking": ["ごくごく…", "ナナが飲み物を飲みます"],
            "singing": ["ふんふふ～ん♪", "ナナが鼻歌を歌います"],
            "studying": ["勉強しよう！", "ナナが勉強に誘ってきます"],
            "disappointed": ["そんな…", "ナナががっかりします"],
            "stubborn": ["でも…", "ナナが我儘を言います"],
            "scared": ["本当に何でもないからさ…", "ナナが強がります"],
            "relieved": ["ふぅ…", "ナナがホッとします"],
            "suspicious": ["変だなぁ…", "ナナが疑います"],
            "suiseininaretanara": ["日が沈んだ後の～", "ナナとマカロンが歌います※長いので注意"],
            "saikai": ["どんな声か覚えてるかな～", "リリとナナが歌います※長いので注意"],
            "the_promise": ["遠い夏の～小さな記憶は～", "リリとナナが歌います※長いので注意"],
            "nana": ["あなたになりたくて～", "ナナが歌います※長いので注意"]
        }

        for cmd_name, data in NANA_COMMANDS.items():
            response_text = data[0]
            description_text = data[1]

            def make_callback(resp: str):
                async def create_callback(interaction: discord.Interaction):
                    if interaction.user.id in BLACKLIST:
                        await interaction.response.send_message("……。", ephemeral=True)
                        return

                    if is_in_target_area(interaction.channel):
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
                await ch.send("…")
                bot_nana.last_human_msg_times[cid] = now


@bot_nana.event
async def on_ready():
    print(f"Nana online: {bot_nana.user}")
    if not bell_nana.is_running():
        bell_nana.start()
    if not yoma_nana.is_running():
        yoma_nana.start()
    if not lonely_check_nana.is_running():
        lonely_check_nana.start()


# ==================================================================================================================================================================
# メッセージへの反応 (対ボット / 対人間)
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


@bot_nana.event
async def on_message(message):
    if message.author.id == bot_nana.user.id or message.author.id in BLACKLIST:
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
