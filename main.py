import discord
import os
import asyncio
import random
from flask import Flask
from threading import Thread
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, timezone, timedelta, datetime
from config import *

# --- Render用：Webサーバー設定 ---
app = Flask('')

@app.route('/')
def home():
    return "Lili, Nana, and Makaron are online!", 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


# ==================================================================================================================================================
# 1. リリ (Lili) の構成
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
            "be_quiet":["静かにして！","リリが静かにしてほしそうにします"],
            "good_morning": ["おはよー！", "リリが挨拶します"],
            "nice_picture": ["かわいい！", "リリが褒めます"],
            "nice_food":["おいしそ～～","リリが食事を褒めます"],
            "thank_you":["ありがとう！","リリが感謝します"],
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
            "what":["なにそれ？","リリが不思議そうにします"],
            "hurry_up":["早くしてよ～","リリが急かします"],
            "good_luck":["頑張ってね！","リリが応援します"],
            "wait":["ちょっと待ってね…","リリが待って欲しそうにします"],
            "hungry":["お腹へった～","リリがお腹を空かせます"],
            "think":["えーっと…","リリが考え込みます"],
            "sleep":["すー…すー…","リリが寝ます"],
            "silent":["…","リリが黙ります"],
            "confused":["？？？？","リリが混乱します"],
            "tired":["もう疲れたぁ…","リリが疲れます"],
            "bored":["つまんない…","リリがつまらなさそうにします"],
            "sneeze":["っしゅん！","リリがくしゃみをします"],
            "agree":["それいいね！！","リリが賛成します"],
            "disagree":["それはダメだよ！","リリが反対します"],
            "failure":["失敗しちゃった…","リリが落ち込みます"],
            "success":["やったー！大成功！！","リリが成功を喜びます"],
            "nod":["わかる～","リリが頷きます"],
            "eating":["おいしー！","リリが食事をします"],
            "drinking":["ごくごく…","リリが飲み物を飲みます"],
            "singing":["ふんふふ～ん♪","リリが鼻歌を歌います"],
            "studying":["勉強しようよ～","リリが勉強に誘ってきます"],
            "disappointed":["そんなぁ…","リリががっかりします"],
            "stubborn":["やだやだ！","リリが我儘を言います"],
            "scared":["これくらい平気だよ…","リリが強がります"],
            "relieved":["よかった～","リリがホッとします"],
            "cold":["寒いよー…","リリが寒がります"],
            "hot":["あつい…","リリが暑がります"],
            "suspicious":["怪しい…","リリが疑います"]
            
           
}

for cmd_name, data in LILI_COMMANDS.items():
    response_text = data[0]
    description_text = data[1]

    async def create_callback(interaction: discord.Interaction, resp: str = response_text):
        if interaction.user.id in BLACKLIST:
            await interaction.response.send_message("……。", ephemeral=True)
            return
            
        if is_in_target_area(interaction.channel):
            await interaction.response.send_message(resp)
        else:
            await interaction.response.send_message("ここではお話しできないよ。", ephemeral=True)

    bot.tree.add_command(
        app_commands.Command(
            name=cmd_name,
            description=description_text,
            callback=create_callback
        )
    )

bot_lili = LiliBot()

@tasks.loop(time=time(hour=17, minute=0, tzinfo=JST))
async def bell_lili():
    for cid in TARGET_CHANNELS:
        ch = bot_lili.get_channel(cid)
        if ch: await ch.send("藍の鐘は午後五時に響く…")

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
    if not bell_lili.is_running(): bell_lili.start()
    if not lonely_check_lili.is_running(): lonely_check_lili.start()

@bot_lili.event
async def on_message(message):
    if message.author.id == bot_lili.user.id or message.author.id in BLACKLIST: return
    if any(word in message.content for word in IGNORE_WORDS): return
    await bot_lili.process_commands(message)
    if not is_in_target_area(message.channel): return
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
            "深い青だった":"少女の鮮血は～\n海よりも\n涙よりも\n深い青だっつぁ～～～～",
            "手を繋いだまななら～": "二度と～",
            "来ない～": "さいか～～～～～～～～～～い！",
            "誕生": "翠の星に乗って～", 
            "深い青だった": "少女の鮮血は～\n海よりも\n涙よりも\n深い青だっつぁ～～～～～～",
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
        if len(content) >= 100: await message.reply("長すぎるよ～")
        elif any(ki in content for ki in ['ロリなな', 'ろりなな','ななロリ','ななろり','ナナロリ','ナナろり','おねリリ','おねりり']):
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
            for k, v in simple.items():
    if k in content:
        await message.reply(v)
        break
else:
    if any(w in content for w in ['藍', '青色', '青い髪', '桃色']):
        await message.reply('？ナナの話…？')
    elif any(w in content for w in ['好き', 'スキ', 'ｽｷ', 'すき']):
        await message.reply('大好きだった～狂いそうなほど～')

# ==================================================================================================================================================================
# 2. ナナ (Nana) の構成
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
            "nice_food":["","ナナが食事を褒めます"],
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
            "what":["なんだろう…？","ナナが疑問に思います"],
            "hurry_up":["早く早く～","ナナが急かします"],
            "good_luck":["頑張って！","ナナが応援します"],
            "wait":["待ってて～","ナナが待って欲しそうにします"],
            "hungry":["何か食べた～い","ナナがお腹を空かせます"],
            "think":["う～ん","ナナが考え込みます"],
            "sleep":["すやすや…","ナナが寝ます"],
            "silent":["…","ナナが黙ります"],
            "confused":["え？？","ナナが混乱します"],
            "tired":["はー疲れた！","ナナが疲れます"],
            "bored":["つまんな～い","ナナがつまらなさそうにします"],
            "sneeze":["くしゅっ！","ナナがくしゃみをします"],
            "agree":["いいじゃん！","ナナが賛成します"],
            "disagree":["ええ～？","ナナが反対します"],
            "failure":["うぅ…","ナナが落ち込みます"],
            "success":["やった！","ナナが喜びます"],
            "nod":["うんうん！","ナナが頷きます"],
            "eating":["もぐもぐ…","ナナが食事をします"],
            "drinking":["ごくごく…","ナナが飲み物を飲みます"],
            "singing":["ふんふふ～ん♪","ナナが鼻歌を歌います"],
            "studying":["勉強しよう！","ナナが勉強に誘ってきます"],
            "disappointed":["そんな…","ナナががっかりします"],
            "stubborn":["でも…","ナナが我儘を言います"],
            "scared":["本当に何でもないからさ…","ナナが強がります"],
            "relieved":["ふぅ…","ナナがホッとします"],
            "suspicious":["変だなぁ…","ナナが疑います"],
            "suiseininaretanara":["日が沈んだ後の～","ナナとマカロンが歌います※長いので注意"],
            "saikai":["どんな声か覚えてるかな～","リリとナナが歌います※長いので注意"],
            "The_promise":["遠い夏の～小さな記憶は～","リリとナナが歌います※長いので注意"],
            "nana":["あなたになりたくて～","ナナが歌います※長いので注意"]
}

for cmd_name, data in NANA_COMMANDS.items():
    def make_callback(res_text):
        async def create_callback(interaction: discord.Interaction):
            if interaction.user.id in BLACKLIST:
                await interaction.response.send_message("……。", ephemeral=True)
                return

            if is_in_target_area(interaction.channel):
                await interaction.response.send_message(res_text)
            else:
                await interaction.response.send_message('ここでは使えないみたい。', ephemeral=True)
        return create_callback

    bot.tree.add_command(
        app_commands.Command(
            name=cmd_name,
            description=data[1],
            callback=make_callback(data[0])
        )
    )
bot_nana = NanaBot()

@tasks.loop(time=time(hour=17, minute=0, tzinfo=JST))
async def bell_nana():
    for cid in TARGET_CHANNELS:
        ch = bot_nana.get_channel(cid)
        if ch:
            await asyncio.sleep(1.0)
            await ch.send("タイムリミットの鐘が鳴る…")

@bot_nana.event
async def on_ready():
    print(f"Nana online: {bot_nana.user}")
    if not bell_nana.is_running(): bell_nana.start()

@bot_nana.event
async def on_message(message):
    if message.author.id == bot_nana.user.id or message.author.id in BLACKLIST: return
    if any(word in message.content for word in IGNORE_WORDS): return
    if not is_in_target_area(message.channel): return
    await bot_nana.process_commands(message)

    content = message.content
    if "たしかに" in content:
        try: await message.add_reaction("<:kani:1488576524381847663>")
        except: pass

    if any(ki in content for ki in ['ロリなな', 'ろりなな','ななロリ','ななろり','ナナロリ','ナナろり','おねリリ','おねりり']):
        await message.reply('最低…'); return

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
            "……だれもいないの？": "もう丸一日ふたりだけ…",
            "ちょっとさみしいね…": "……リリがいるだけで嬉しいよ…",
            "大人になれば～": "全部忘れられると思うけど…",
            "約束を": "果たそう", 
            "夢のように愛して～\n愛のように夢をみて～": "空想でも信じればいつか叶うからと～\n言ってた～～",
            "普通に笑って普通に泣いて生きてみたかった～":"そんなこと今更叶わないから\n今日も眠りにつく～",
            "冒険しよう～": "ふ～たりは～",
            "リリはわたしの心の中に秘めた気持ちをを歌った曲\nザラザラなギターの音がわたしのナナに対する思いを表していて素敵！": "ナナもわたしの内面を歌った曲だよ！\n優しい感じでリリの細やかな描写があってナナのリリへの思いが伝わってくるね\n夜魔はリリに長いこと会えないでいた私の曲だよ\n明るい曲調とは裏腹にちょっと悲しい歌詞がいいよね～"
        }
        if content in responses:
            await asyncio.sleep(2.0 if "だれもいない" in content else 1.0)
            await message.reply(responses[content])
        elif content == "てことは今日は私たちの誕生日みたいなものなのかなぁ…":
            await asyncio.sleep(1.0)
            await message.reply(f"たしかにね～\nもう{datetime.now(JST).year-2019}年も経つのかぁ…")
    elif message.author.id == MAKARON_USER_ID:
        if "再会のリリース日" in content:
            await asyncio.sleep(1.0); await message.reply("再会と言えばふたりのシリーズで一番最初の曲だよね～！")
        elif "約束のリリース日" in content:
            await asyncio.sleep(1.0); await message.reply("約束を、果たしに来たんだね…！")
        elif "一般公開記念日" in content:
            await asyncio.sleep(1.0); await message.reply("この曲たちはアルバムが公開されてから2年ほどたってから一般公開されたんだよね～")
    else:
        if len(content) >= 100: await message.reply(f"{len(content)}文字もあるよ～")
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
                if k in content: await message.reply(v); return
            if any(w in content for w in ['いい', 'よい','良い']): await message.reply('そりゃそうだ～\nあなたが選んだんだから～')
            elif any(w in content for w in ['金色', '黄金色','藍']): await message.reply('なにー？リリの話…？')
            if content == "ふたりの": await message.reply(random.choice(["ふたりの", "約束", "秘密","深い青だった", "彗星になれたなら", "夜魔", "ナナ\nあなたは金色のシャンデリー", "リリ", "再会", "誕生"]))
            if not message.mentions and any(ke in content for ke in ['”7”', '七', '7', '７']): await message.reply('呼んだ？')

# ===================================================================================================================================================================
# 3. マカロン (Makaron) の構成
# ===================================================================================================================================================================
intents_maka = discord.Intents.default()
intents_maka.message_content = True
bot_maka = commands.Bot(command_prefix="マカロン", intents=intents_maka)

ANNIVERSARIES = {
    (6, 29): "再会のリリース日",
    (9, 14): "約束のリリース日", 
    (4, 26): "秘密のリリース日",
    (6, 18): "彗星になれたならのリリース日", 
    (8, 26):"ふたりのアルバム＆誕生のリリース日",
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
            if ch: await ch.send(f"ピコピコ！(今日は{ANNIVERSARIES[date_key]}なんだって！おめでとう！！)")

@bot_maka.event
async def on_ready():
    print(f"Makaron online: {bot_maka.user}")
    if not check_anniversary_maka.is_running(): check_anniversary_maka.start()

@bot_maka.event
async def on_message(message):
    if message.author.id == bot_maka.user.id or message.author.id in BLACKLIST: return
    if any(word in message.content for word in IGNORE_WORDS): return
    await bot_maka.process_commands(message)

@bot_maka.command()
async def ping(ctx):
    if is_in_target_area(ctx.channel): await ctx.reply('ピポピポ')

@bot_maka.command()
async def サイコロ(ctx):
    if not is_in_target_area(ctx.channel): return
    await ctx.send("ピコピコピ？(どれくらい振ればいい？『1d6』みたいに教えてね)")
    try:
        msg = await bot_maka.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        if 'd' not in msg.content: await ctx.send("形式が違うよー"); return
        n, s = map(int, msg.content.lower().split('d'))
        if n > 100: await ctx.send("多すぎるよー"); return
        rolls = [random.randint(1, s) for _ in range(n)]
        await ctx.reply(f"ピポパ！ 合計：**{sum(rolls)}**\n🎲 {rolls}")
    except: await ctx.send("ピ？(エラーか時間切れだよ)")

# =============================================================================================================================================================
# 統合実行セクション
# =============================================================================================================================================================
async def start_all():
    keep_alive()
    tokens = {
        "LILI": os.getenv('TOKEN_LILI'),
        "NANA": os.getenv('TOKEN_NANA'),
        "MAKARON": os.getenv('TOKEN_MAKARON')
    }
    
    for k, v in tokens.items():
        if not v: print(f"警告: {k} のトークンが設定されていません。")

    await asyncio.gather(
        bot_lili.start(tokens["LILI"]),
        bot_nana.start(tokens["NANA"]),
        bot_maka.start(tokens["MAKARON"])
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        pass
