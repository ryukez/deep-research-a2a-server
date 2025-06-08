import logging
import os
import sys

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv
from agent_executor import (
    ResearchAgentExecutor,  # type: ignore[import-untyped]
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=9999)
def main(host, port):
    """Starts the Deep Research Agent server."""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise MissingAPIKeyError("GEMINI_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)

        research_skill = AgentSkill(
            id="web_research",
            name="Web Research Agent",
            description="Performs comprehensive web research on any topic using LangGraph and Google Search API",
            tags=["research", "web search", "analysis", "information gathering"],
            examples=[
                "Research the latest developments in climate change",
                "Research the latest developments in Python",
                "What are the latest developments in quantum computing?",
                "Research the impact of social media on mental health",
            ],
        )

        # This will be the public-facing agent card
        public_agent_card = AgentCard(
            name="Deep Research Agent",
            description="Comprehensive web research agent powered by LangGraph and Google Search API",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=capabilities,
            skills=[research_skill],  # Research skill for the public card
            supportsAuthenticatedExtendedCard=False,
        )

        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=ResearchAgentExecutor(),  # 新しいResearchAgentExecutorを使用
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )

        server = A2AStarletteApplication(
            agent_card=public_agent_card,
            http_handler=request_handler,
        )

        logger.info(f"Starting Deep Research Agent server on {host}:{port}")
        uvicorn.run(server.build(), host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
