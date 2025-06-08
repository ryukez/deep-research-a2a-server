#!/bin/bash

# Deep Research Agent 本番起動スクリプト

set -e  # エラーが発生したら停止

echo "Deep Research Agent を起動しています..."

# 環境変数の確認
if [ -z "$GEMINI_API_KEY" ]; then
    echo "エラー: GEMINI_API_KEY 環境変数が設定されていません"
    exit 1
fi

# デフォルト設定
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8080"}
export PYTHONPATH=${PYTHONPATH:-"."}

echo "設定:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")"

# 依存関係のインストール確認
echo "依存関係を確認中..."
if command -v uv &> /dev/null; then
    uv sync
else
    pip install -e .
fi

# gunicornで起動
echo "サーバーを起動中..."
exec gunicorn app:app -c gunicorn.conf.py 