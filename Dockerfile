# Pythonのイメージを使う
FROM python:3.10
 
# 作業ディレクトリを作成
WORKDIR /app
 
# 必要なファイルをコピー
COPY . .
 
# 音声再生に必要なffmpegをインストール
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
 
# ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt
 
# Botを実行
CMD ["python", "main.py"]
 
