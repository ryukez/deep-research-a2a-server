# LangGraph API Server - curl アクセスサンプル集

このドキュメントは、backend の LangGraph API サーバーに curl を使ってアクセスするためのサンプル集です。

## サーバー起動

```bash
# バックエンドディレクトリで実行
cd backend
uv run langgraph dev --port 8124 --no-browser
```

## 基本情報

- **ベース URL**: http://localhost:8124
- **Content-Type**: application/json
- **認証**: ローカル環境では不要（本番環境では X-Api-Key ヘッダーが必要）

## API エンドポイント例

### 1. アシスタント検索

利用可能なアシスタント（エージェント）を検索します。

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/assistants/search \
  -d '{
    "limit": 10,
    "offset": 0,
    "metadata": {}
  }'
```

**レスポンス例**:

```json
[
  {
    "assistant_id": "fe096781-5601-53d2-b2f6-0d3403f7e9ca",
    "graph_id": "agent",
    "config": {},
    "metadata": { "created_by": "system" },
    "name": "pro-search-agent",
    "created_at": "2025-06-08T07:45:35.410967+00:00",
    "updated_at": "2025-06-08T07:45:35.410967+00:00",
    "version": 1,
    "description": null
  }
]
```

### 2. エージェント実行（ストリーミング）

メッセージを送信してエージェントを実行し、結果をストリーミングで受信します。

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "Hello, how are you?"
        }
      ]
    },
    "stream_mode": "messages-tuple"
  }'
```

### 3. 質問応答例

研究エージェントに質問をする例：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "Tell me about the latest developments in AI"
        }
      ]
    },
    "stream_mode": "messages-tuple"
  }'
```

### 4. 日本語での質問例

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "最新のテクノロジートレンドについて教えてください"
        }
      ]
    },
    "stream_mode": "messages-tuple"
  }'
```

### 5. 非ストリーミング実行

結果を一度に受信する場合：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "What is LangGraph?"
        }
      ]
    }
  }'
```

## ストリームモード

ストリーミング実行では以下のストリームモードが利用できます：

- `messages-tuple`: メッセージのタプル形式
- `messages`: メッセージのみ
- `values`: 状態の値
- `updates`: 状態の更新

例：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "human", "content": "Hello"}]
    },
    "stream_mode": "values"
  }'
```

## エラーハンドリング

API 呼び出しでエラーが発生した場合、以下のような形式で返されます：

```json
{
  "error": "AttributeError",
  "message": "'Configuration' object has no attribute 'reasoning_model'"
}
```

## スレッド管理

特定のスレッド ID を指定して実行することも可能です：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/threads/{thread_id}/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "Continue our conversation"
        }
      ]
    },
    "stream_mode": "messages-tuple"
  }'
```

## 設定カスタマイズ

カスタム設定でエージェントを実行：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8124/runs/stream \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {
          "role": "human",
          "content": "Research about quantum computing"
        }
      ]
    },
    "config": {
      "configurable": {
        "max_research_loops": 3,
        "number_of_initial_queries": 2
      }
    },
    "stream_mode": "messages-tuple"
  }'
```

## API ドキュメント

詳細な API 仕様は以下の URL で確認できます：
http://localhost:8124/docs

## 注意事項

1. サーバーが起動していることを確認してください
2. 環境変数（GEMINI_API_KEY 等）が適切に設定されていることを確認してください
3. ストリーミングレスポンスは Server-Sent Events (SSE) 形式で返されます
4. エラーが発生した場合は、ログを確認して設定や API キーをチェックしてください
