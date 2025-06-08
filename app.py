"""
Production ASGI application entry point for gunicorn.
"""

import logging
import os
import sys
from pathlib import Path

import httpx
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

# ルートディレクトリを Python パスに追加
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from agent_executor import ResearchAgentExecutor

# 環境変数をロード
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """アプリケーションを作成して返す"""

    # 必要な環境変数をチェック
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is required")

    # 設定
    host = os.environ.get("HOST", "localhost")
    port = os.environ.get("PORT", "8080")

    capabilities = AgentCapabilities(streaming=True, pushNotifications=True)

    research_skill = AgentSkill(
        id="web_research",
        name="Web Research Agent",
        description="Performs comprehensive web research on any topic using LangGraph and Google Search API",
        tags=["research", "web search", "analysis", "information gathering"],
        examples=[
            "最新のAI技術動向について調べてください",
            "気候変動に関する最新の研究について教えてください",
            "Pythonの最新バージョンの新機能について調査してください",
            "What are the latest developments in quantum computing?",
            "Research the impact of social media on mental health",
        ],
    )

    # エージェントカード
    agent_card = AgentCard(
        name="Deep Research Agent",
        description="Comprehensive web research agent powered by LangGraph and Google Search API",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[research_skill],
        supportsAuthenticatedExtendedCard=False,
    )

    # HTTPクライアントとリクエストハンドラー
    httpx_client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=ResearchAgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(httpx_client),
    )

    # A2Aアプリケーション
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    logger.info(f"Deep Research Agent server created for {host}:{port}")
    return server.build()


# gunicorn用のアプリケーションインスタンス
app = create_app()
