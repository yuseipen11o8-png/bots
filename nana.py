import asyncio
import random
import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, datetime

from config import (
    JST,
    TARGET_CHANNELS,
    BLACKLIST,
    IGNORE_WORDS,
    LILI_USER_ID,
    MAKARON_USER_ID,
    is_in_target_area,
)

# ==================================================================================================================================================================
# ナナ (Nana) の構成
# ==================================================================================================================================================================
intents_nana = discord.Intents.default()
intents_nana.message_content = True


class NanaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ナナ", intents=intents_nana)

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


@bot_nana.event
async def on_ready():
    print(f"Nana online: {bot_nana.user}")
    if not bell_nana.is_running():
        bell_nana.start()
    if not yoma_nana.is_running():
        yoma_nana.start()


@bot_nana.event
async def on_message(message):
    if message.author.id == bot_nana.user.id or message.author.id in BLACKLIST:
        return
    if any(word in message.content for word in IGNORE_WORDS):
        return
    if not is_in_target_area(message.channel):
        return
    await bot_nana.process_commands(message)

    content = message.content
    if "たしかに" in content:
        try:
            await message.add_reaction("<:kani:1488576524381847663>")
        except Exception:
            pass

    if any(ki in content for ki in ['ロリなな', 'ろりなな', 'ななロリ', 'ななろり', 'ナナロリ', 'ナナろり', 'おねリリ', 'おねりり']):
        await message.reply('最低…')
        return

    if message.author.id == LILI_USER_ID:
        responses = {
            "ふたりのことが知りたいのなら～": "君もどんな人生だったか話してほしい～",
            "こんな物語をわわすれるくらいなら～": "大人のオの字も知りたくもないのさ～",
            "約束したのだ～": "流れ星の下で…",
            "宇宙が～ふたりきり食べたおにぎりの～": "海苔とかならいいのにね～～",
            "君の青い髪が僕のイノセンスだった": "リリ…！",
            "さんざめくこの世界にさよならを～": "手を繋いだまななら～",
            "二度と～": "来ない～",
            "翠の星に乗って～": "ふたりは一つの愛になる～",
            "大人になれば～": "全部忘れられると思うけど…",
            "約束を": "果たそう",
            "夢のように愛して～\n愛のように夢をみて～": "空想でも信じればいつか叶うからと～\n言ってた～～",
            "普通に笑って普通に泣いて生きてみたかった～": "そんなこと今更叶わないから\n今日も眠りにつく～",
            "冒険しよう～": "ふ～たりは～",
        }
        if content in responses:
            await asyncio.sleep(2.0 if "だれもいない" in content else 1.0)
            await message.reply(responses[content])
        elif content == "てことは今日は私たちの誕生日みたいなものなのかなぁ…":
            await asyncio.sleep(1.0)
            await message.reply(f"たしかにね～\nもう{datetime.now(JST).year-2019}年も経つのかぁ…")
    elif message.author.id == MAKARON_USER_ID:
        if "再会のリリース日なんだって！" in content:
            await asyncio.sleep(1.0)
            await message.reply("再会と言えばふたりのシリーズで一番最初の曲だよね～！")
        elif "約束のリリース日なんだって！" in content:
            await asyncio.sleep(1.0)
            await message.reply("約束を、果たしに来たんだね…！")
        elif "一般公開記念日なんだって！" in content:
            await asyncio.sleep(1.0)
            await message.reply("この曲たちはアルバムが公開されてから2年ほどたってから一般公開されたんだよね～")
    else:
        if len(content) >= 100:
            await message.reply(f"{len(content)}文字もあるよ～")
        elif len(content) <= 30:
            simple = {
                "彗星": "彗星になれたならいいのに…",
                "水星": "水星にもなりたいなぁ…",
                "水棲": "水には住みたくないなぁ…",
                "翠星": "翠の星に乗って～",
                "水性": "海に溶けちゃう…",
                "後悔": "徒然な後悔も言わないで～",
                "約束": "藍の鐘で",
                "信じ": "信じてなんてないかもね～",
                "夢": "ふたりの～夢を夢を見せよう～",
                "帰": "帰ったほうがいいかもしれない気がしなくもないわ～",
                "普通": "普通に笑って普通に泣いて生きて見たかった～",
                "空想": "空想でも信じればいつか叶うからと～言ってた～",
                "また": "またか～また現れたのか～",
                "怖": "お前なんて怖くないよ",
                "真似": "無理して笑って～無理して泣いて～普通の真似をした～"
            }
            for k, v in simple.items():
                if k in content:
                    await message.reply(v)
                    return
            if any(w in content for w in ['いい', 'よい', '良い']):
                await message.reply('そりゃそうだ～\nあなたが選んだんだから～')
            elif any(w in content for w in ['金色', '黄金色', '藍']):
                await message.reply('なにー？リリの話…？')
            if content == "ふたりの":
                await message.reply(random.choice(["ふたりの", "約束", "秘密", "深い青だった", "彗星になれたなら", "夜魔", "ナナ\nあなたは金色のシャンデリー", "リリ", "再会", "誕生"]))
            if not message.mentions and any(ke in content for ke in ['”7”', '七', '7', '７']):
                await message.reply('呼んだ？')
