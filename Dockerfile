# Pythonのイメージを使う
FROM python:3.10

# 作業ディレクトリを作成
WORKDIR /app

# 必要なファイルをコピー
COPY . .

# ライブラリをインストール
RUN pip install --no-cache-dir discord.py flask

# Botを実行
CMD ["python", "main.py"]
