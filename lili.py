import asyncio
import discord
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, timedelta, datetime

from config import JST, TARGET_CHANNELS, BLACKLIST, IGNORE_WORDS, NANA_USER_ID, is_in_target_area

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
    if not lonely_check_lili.is_running():
        lonely_check_lili.start()


@bot_lili.event
async def on_message(message):
    if message.author.id == bot_lili.user.id or message.author.id in BLACKLIST:
        return
    if any(word in message.content for word in IGNORE_WORDS):
        return
    await bot_lili.process_commands(message)
    if not is_in_target_area(message.channel):
        return
    if message.author.id != NANA_USER_ID:
        bot_lili.last_human_msg_times[message.channel.id] = datetime.now(JST)

    content = message.content
    if message.author.id == NANA_USER_ID:
        responses = {
            "呼んだ？": "呼ばれてないよ…",
            "ふたりの": "ふたりのことが知りたいのなら～",
            "約束": "こんな物語をわわすれるくらいなら～",
            "大人のオの字も知りたくもないのさ～": "約束したのだ～",
            "秘密": "宇宙が～ふたりきり食べたおにぎりの～",
            "リリ": "君の青い髪が僕のイノセンスだった",
            "ナナ\nあなたは金色のシャンデリー": "ナナ…！",
            "彗星になれたなら": "夢のように愛して～\n愛のように夢をみて～",
            "夜魔": "普通に笑って普通に泣いて生きてみたかった～",
            "再会": "さんざめくこの世界にさよならを～",
            "深い青だった": "少女の鮮血は～\n海よりも\n涙よりも\n深い青だっつぁ～～～～～～",
            "手を繋いだまななら～": "二度と～",
            "来ない～": "さいか～～～～～～～～～～い！",
            "誕生": "翠の星に乗って～",
            "もう丸一日ふたりだけ…": "ちょっとさみしいね…",
            "……リリがいるだけで嬉しいよ…": "うん…私も……",
            "翠の星に乗って～": "あの日のふたりを見に行こう～",
            "やめたほうがいいのに～": "大人達は笑うけど～",
            "藍の鐘で": "また会おう",
            "再会と言えばふたりのシリーズで一番最初の曲だよね～！": "てことは今日は私たちの誕生日みたいなものなのかなぁ…",
            "この曲たちはアルバムが公開されてから2年ほどたってから一般公開されたんだよね～": "リリはわたしの心の中に秘めた気持ちをを歌った曲\nザラザラなギターの音がわたしのナナに対する思いを表していて素敵！",
            "ナナもわたしの内面を歌った曲だよ！\n優しい感じでリリの細やかな描写があってナナのリリへの思いが伝わってくるね\n夜魔はリリに長いこと会えないでいた私の曲だよ\n明るい曲調とは裏腹にちょっと悲しい歌詞がいいよね～": "この曲たちは全部MVはないけれどとてもいい曲だから皆もいっぱい聴いてね！"
        }
        if content in responses:
            await asyncio.sleep(1.5 if "…リリ" in content else 1.0)
            await message.reply(responses[content])
    else:
        if len(content) >= 100:
            await message.reply("長すぎるよ～")
        elif any(ki in content for ki in ['ロリなな', 'ろりなな', 'ななロリ', 'ななろり', 'ナナロリ', 'ナナろり', 'おねリリ', 'おねりり']):
            await message.reply('イノセンスなさそう')
        elif len(content) <= 30:
            simple = {
                "スープ": "そのスープ温かいうちに飲むのがいいよ",
                "知りたい": "ふたりのことが知りたいのなら～",
                "大人": "大人になれば～",
                "再会": "約束を",
                "おにぎり": "宇宙が～ふたりきり食べたおにぎりの～",
                "宇宙": "宇宙が～ふたりきり食べたおにぎりの～",
                "信じ": "信じていいと思った～\n信じていいと思った～",
                "イノセンス": "ボロボロになったイノセンスで～\n僕を認めてよ…",
                "夕焼け": "夕焼けに～染まったなら～\n息を止めてくれ",
                "本": "その本が気になるならば読んでもいいよ",
                "銀河": "遥か遠い銀河のなんでもない話だ",
                "瞳": "ただこの冷めた瞳を溶かすのは～\n君のイノセンスが僕を知る時だ～",
                "邪魔": "例えば誰かが僕らの邪魔をしていて",
                "例えば": "例えば\n僕らが\n例えば\n僕らが\n例えば\n例えば\n例えば\n例えば",
                "馬鹿": "あの日大人のふりして逃げた馬鹿な僕を～～\n許して欲しかった～～"
            }

            found = False

            for k, v in simple.items():
                if k in content:
                    await message.reply(v)
                    found = True
                    break

            if not found:
                if any(w in content for w in ['藍', '青色', '青い髪', '桃色']):
                    await message.reply('？ナナの話…？')
                elif any(w in content for w in ['好き', 'スキ', 'ｽｷ', 'すき']):
                    await message.reply('大好きだった～狂いそうなほど～')
