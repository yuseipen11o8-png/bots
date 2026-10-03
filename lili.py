import asyncio
import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, timedelta, datetime

from config import JST, TARGET_CHANNELS, BLACKLIST, IGNORE_WORDS, NANA_USER_ID, is_in_target_area
from lines import (
    LILI_TO_BOT,
    LILI_TO_HUMAN,
    LILI_TO_HUMAN_MULTI,
    LILI_LOLI_REPLY,
    LOLI_NANA_WORDS,
)

# ==================================================================================================================================================
# リリ (Lili) の構成
# ==================================================================================================================================================
intents_lili = discord.Intents.default()
intents_lili.message_content = True


class LiliBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="リリ", intents=intents_lili)
        self.last_human_msg_times = {}

    async def setup_hook(self):
        LILI_COMMANDS = {
            "hello": ["こんにちは！", "リリが挨拶します"],
            "good_night": ["おやすみ～", "リリが挨拶します"],
            "go_to_bed": ["そろそろ寝ようよ～", "リリが注意します"],
            "be_quiet": ["静かにして！", "リリが静かにしてほしそうにします"],
            "good_morning": ["おはよー！", "リリが挨拶します"],
            "nice_picture": ["かわいい！", "リリが褒めます"],
            "nice_food": ["おいしそ～～", "リリが食事を褒めます"],
            "thank_you": ["ありがとう！", "リリが感謝します"],
            "bye": ["ばいばーい！", "リリが挨拶します"],
            "turn_off": ["うわぁ………", "リリがドン引きします"],
            "sad": ["ひどいよー", "リリが悲しみます"],
            "happy": ["やったー！", "リリが喜びます"],
            "angry": ["もう知らない！", "リリが怒ります"],
            "feel_shy": ["えへへ…", "リリが照れます"],
            "surprised": ["キャー！", "リリが驚きます"],
            "sorry": ["ごめんなさい…", "リリが謝ります"],
            "smile": ["うふふ～～", "リリが笑います"],
            "cry": ["うぅっ…", "リリが泣きます"],
            "panic": ["あわわわわ…", "リリが慌てます"],
            "worry": ["大丈夫…？", "リリが心配します"],
            "shout": ["あああーーーーーーーーーーーーーーーーーーーーーーーー！！！", "リリが叫びます"],
            "what": ["なにそれ？", "リリが不思議そうにします"],
            "hurry_up": ["早くしてよ～", "リリが急かします"],
            "good_luck": ["頑張ってね！", "リリが応援します"],
            "wait": ["ちょっと待ってね…", "リリが待って欲しそうにします"],
            "hungry": ["お腹へった～", "リリがお腹を空かせます"],
            "think": ["えーっと…", "リリが考え込みます"],
            "sleep": ["すー…すー…", "リリが寝ます"],
            "silent": ["…", "リリが黙ります"],
            "confused": ["？？？？", "リリが混乱します"],
            "tired": ["もう疲れたぁ…", "リリが疲れます"],
            "bored": ["つまんない…", "リリがつまらなさそうにします"],
            "sneeze": ["っしゅん！", "リリがくしゃみをします"],
            "agree": ["それいいね！！", "リリが賛成します"],
            "disagree": ["それはダメだよ！", "リリが反対します"],
            "failure": ["失敗しちゃった…", "リリが落ち込みます"],
            "success": ["やったー！大成功！！", "リリが成功を喜びます"],
            "nod": ["わかる～", "リリが頷きます"],
            "eating": ["おいしー！", "リリが食事をします"],
            "drinking": ["ごくごく…", "リリが飲み物を飲みます"],
            "singing": ["ふんふふ～ん♪", "リリが鼻歌を歌います"],
            "studying": ["勉強しようよ～", "リリが勉強に誘ってきます"],
            "disappointed": ["そんなぁ…", "リリががっかりします"],
            "stubborn": ["やだやだ！", "リリが我儘を言います"],
            "scared": ["これくらい平気だよ…", "リリが強がります"],
            "relieved": ["よかった～", "リリがホッとします"],
            "cold": ["寒いよー…", "リリが寒がります"],
            "hot": ["あつい…", "リリが暑がります"],
            "suspicious": ["怪しい…", "リリが疑います"]
        }

        for cmd_name, data in LILI_COMMANDS.items():
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


bot_lili = LiliBot()


@tasks.loop(time=time(hour=17, minute=0, tzinfo=JST))
async def bell_lili():
    for cid in TARGET_CHANNELS:
        ch = bot_lili.get_channel(cid)
        if ch:
            await ch.send("藍の鐘は午後五時に響く…")


@tasks.loop(time=time(hour=3, minute=0, tzinfo=JST))
async def yoma_lili():
    for cid in TARGET_CHANNELS:
        ch = bot_lili.get_channel(cid)
        if ch:
            await ch.send("真夜中ひとり午前三時…")



@tasks.loop(minutes=30)
async def lonely_check_lili():
    now = datetime.now(JST)
    for cid in TARGET_CHANNELS:
        last_at = bot_lili.last_human_msg_times.get(cid)
        if last_at and now - last_at > timedelta(hours=24):
            ch = bot_lili.get_channel(cid)
            if ch:
                await ch.send("…")
                bot_lili.last_human_msg_times[cid] = now


@bot_lili.event
async def on_ready():
    print(f"Lili online: {bot_lili.user}")
    if not bell_lili.is_running():
        bell_lili.start()
    if not yoma_lili.is_running():
        yoma_lili.start()
    if not lonely_check_lili.is_running():
        lonely_check_lili.start()


# ==================================================================================================================================================
# メッセージへの反応 (対ボット / 対人間)
# ==================================================================================================================================================
async def handle_bot(message):
    """Botからのメッセージへの反応(ナナとの掛け合い)"""
    # ナナ以外のBot(マカロン等)には反応しない
    if message.author.id != NANA_USER_ID:
        return

    content = message.content
    reply = LILI_TO_BOT.get(content)
    if reply:
        await asyncio.sleep(1.5 if "…リリ" in content else 1.0)
        await message.reply(reply)


async def handle_human(message):
    """人間からのメッセージへの反応"""
    content = message.content
    bot_lili.last_human_msg_times[message.channel.id] = datetime.now(JST)

    # 長文(100文字以上)
    if len(content) >= 100:
        await message.reply("長すぎるよ～")
        return

    # 「ロリなな」系(文字数に関係なく反応)
    if any(ki in content for ki in LOLI_NANA_WORDS):
        await message.reply(LILI_LOLI_REPLY)
        return

    # 短文(30文字以下)のみ、キーワードに反応
    if len(content) <= 30:
        # 1キーワード → 1返事
        for k, v in LILI_TO_HUMAN.items():
            if k in content:
                await message.reply(v)
                return

        # 複数キーワード → 1返事(最初に一致したものだけ)
        for words, reply in LILI_TO_HUMAN_MULTI:
            if any(w in content for w in words):
                await message.reply(reply)
                return


@bot_lili.event
async def on_message(message):
    if message.author.id == bot_lili.user.id or message.author.id in BLACKLIST:
        return
    if any(word in message.content for word in IGNORE_WORDS):
        return
    await bot_lili.process_commands(message)
    if not is_in_target_area(message.channel):
        return

    if message.author.bot:
        await handle_bot(message)
    else:
        await handle_human(message)
