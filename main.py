import discord
import os
import asyncio
import random
from flask import Flask
from threading import Thread
from discord.ext import tasks, commands
from discord import app_commands
from datetime import time, timezone, timedelta, datetime

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

# --- 共通設定・定数 ---
JST = timezone(timedelta(hours=9))
TARGET_CHANNELS = [1478494656437424189, 1481902889109553223]
BLACKLIST = [123456789012345678, 987654321098765432]
IGNORE_WORDS = ["納豆", "ぺろ", "ペロ"]

LILI_USER_ID = 1480173387728031906
NANA_USER_ID = 1480176910771294308
MAKARON_USER_ID = 1481291325079949483

def is_in_target_area(channel):
    if channel.id in TARGET_CHANNELS:
        return True
    if isinstance(channel, discord.Thread) and channel.parent_id in TARGET_CHANNELS:
        return True
    return False

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
            "hello": "こんにちは！", 
            "good_night": "おやすみ～",
            "go_to_bed": "みんなそろそろ寝ようよ～",
            "good_morning": "おはよー！",
            "nice_picture": "かわいい！ありがとう！",
            "bye": "ばいばーい！",
            "turn_off": "うわぁ………",
            "sad": "ひどいよー", 
            "happy": "やったー！", 
            "angry": "もう知らない！",
            "feel_shy": "えへへ…",
            "surprised": "キャー！",
            "sorry": "ごめんなさい…", 
            "smile": "うふふ～～",
            "cry": "ぅうっ…",
            "panic": "あわわわわ…", 
            "worry": "大丈夫…？", 
            "shout": "あああーーーーーーーーーーーーーーーーーーーーーーーー！！！"
        }
        
        # エラー修正箇所：引数 r に型指定 : str を追加
        for name, resp in LILI_COMMANDS.items():
            def make_callback(res_text: str):
                async def cb(interaction: discord.Interaction):
                    if interaction.user.id in BLACKLIST:
                        await interaction.response.send_message("……。", ephemeral=True)
                        return
                    if is_in_target_area(interaction.channel):
                        await interaction.response.send_message(res_text)
                    else:
                        await interaction.response.send_message("ここではお話しできないよ。", ephemeral=True)
                return cb
            
            self.tree.add_command(app_commands.Command(name=name, description="リリのアクション", callback=make_callback(resp)))
        await self.tree.sync()

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
        else:
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
                if k in content: await message.reply(v); break
            if any(w in content for w in ['藍', '青色','青い髪','桃色']): await message.reply('？ナナの話…？')
            elif any(w in content for w in ['好き', 'スキ','ｽｷ','すき']): await message.reply('大好きだった～狂いそうなほど～')

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
            "hello": "こんにちは～", 
            "good_night": "みんなおやすみ～！",
            "good_morning": "おはよう～",
            "go_to_bed": "まだ寝てないの～？", 
            "nice_picture": "すごいきれい…",
            "bye": "さよなら～またね～",
            "turn_off": "えぇ………", 
            "sad": "やめてよ…！", 
            "happy": "いえーい！", 
            "angry": "ちょっと！",
            "feel_shy": "てへへへ…",
            "surprised": "うわっ！！", 
            "sorry": "ごめんね…",
            "smile": "ふふふ～",
            "cry": "うぁわーん！", 
            "panic": "どうしよう…", 
            "worry": "どうしたの…？",
            "saikai": "どんな声か覚えてるかな～",
            "yakusoku": "遠い夏の～小さな記憶は～",
            "nana": "あなたになりたくて"
        }
        
        # エラー修正箇所：引数 r に型指定 : str を追加
        for name, resp in NANA_COMMANDS.items():
            def make_callback(res_text: str):
                async def cb(interaction: discord.Interaction):
                    if interaction.user.id in BLACKLIST:
                        await interaction.response.send_message("……。", ephemeral=True)
                        return
                    if is_in_target_area(interaction.channel):
                        await interaction.response.send_message(res_text)
                    else:
                        await interaction.response.send_message('ここでは使えないみたい。', ephemeral=True)
                return cb
            
            self.tree.add_command(app_commands.Command(name=name, description="ナナのアクション", callback=make_callback(resp)))
        await self.tree.sync()

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
        else:
            simple = {
                "彗星": "彗星になれたならいいのに…",
                "水星": "水星にもなりたいなぁ…",
                "翠星": "翠の星に乗って～",
                "後悔": "徒然な後悔も言わないで～",
                "約束": "藍の鐘で", 
                "信じ": "信じてなんてないかもね～",
                "夢": "ふたりの～夢を夢を見せよう～",
                "帰": "帰ったほうがいいかもしれない気がしなくもないわ～",
                "普通": "普通に笑って普通に泣いて生きてみたかった～", 
                "空想": "空想でも信じればいつか叶うからと～言ってた～",
                "また": "またか～また現れたのか～",
                "怖": "お前なんて怖くないよ～"
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

# ==========================================================================================================================================================
# 統合実行セクション
# ==========================================================================================================================================================
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
