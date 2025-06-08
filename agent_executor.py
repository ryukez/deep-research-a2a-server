from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError

import sys
import os
import logging
from pathlib import Path
from langchain_core.messages import HumanMessage

src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from agent.graph import graph
from agent.configuration import Configuration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """LangGraph Research Agent."""

    def __init__(self):
        """Initialize the research agent with the LangGraph graph."""
        self.graph = graph
        self.config = {"configurable": Configuration().model_dump()}

    async def invoke(self, query: str) -> str:
        """Invoke the research agent with a query."""
        try:
            # Wrap the query in HumanMessage
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "search_query": [],
                "web_research_result": [],
                "sources_gathered": [],
            }

            # Execute the graph
            result = await self.graph.ainvoke(initial_state, config=self.config)

            # Extract the content from the result message
            if result.get("messages") and len(result["messages"]) > 0:
                return result["messages"][-1].content
            else:
                return "Failed to get the research result."

        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise e

    async def stream(self, query: str, context_id: str):
        """Stream the research process."""
        try:
            # Wrap the query in HumanMessage
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "search_query": [],
                "web_research_result": [],
                "sources_gathered": [],
            }

            # Notify the research start
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Research is starting...",
            }

            # Execute the graph
            result = await self.graph.ainvoke(initial_state, config=self.config)

            # Return the result
            if result.get("messages") and len(result["messages"]) > 0:
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": result["messages"][-1].content,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": "Research is complete, but the result could not be obtained.",
                }

        except Exception as e:
            logger.error(f"Error during research streaming: {str(e)}")
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"Error during research streaming: {str(e)}",
            }


class ResearchAgentExecutor(AgentExecutor):
    """Research Agent Executor using LangGraph."""

    def __init__(self):
        self.agent = ResearchAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Validate the request
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        # Get the user input
        query = context.get_user_input()
        if not query:
            raise ServerError(error=InvalidParamsError())

        # Manage the task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.contextId)

        try:
            # Execute the agent streaming
            async for item in self.agent.stream(query, task.contextId):
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]

                if not is_task_complete and not require_user_input:
                    # Update the working state
                    updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item["content"],
                            task.contextId,
                            task.id,
                        ),
                    )
                elif require_user_input:
                    # Update the state with user input required
                    updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item["content"],
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    break
                else:
                    # Task complete
                    updater.add_artifact(
                        [Part(root=TextPart(text=item["content"]))],
                        name="research_result",
                    )
                    updater.complete()
                    break

        except Exception as e:
            logger.error(f"Error during research execution: {e}")
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        """Validate the request"""
        # Basic validation (expand as needed)
        return False

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        """Cancel the task (not supported)"""
        raise ServerError(error=UnsupportedOperationError())
