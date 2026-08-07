from datetime import timezone, timedelta

# タイムゾーン
JST = timezone(timedelta(hours=9))

# 対象チャンネル
TARGET_CHANNELS = [
    1478494656437424189,
    1481902889109553223,
]

# ブラックリスト
BLACKLIST = [
    123456789012345678,
    987654321098765432,
]

# 反応しない単語
IGNORE_WORDS = [
    "納豆",
    "ぺろ",
    "ペロ",
]

# BotのID
LILI_USER_ID = 1480173387728031906
NANA_USER_ID = 1480176910771294308
MAKARON_USER_ID = 1481291325079949483
