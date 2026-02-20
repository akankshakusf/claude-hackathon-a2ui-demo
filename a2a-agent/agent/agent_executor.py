# agent_executor.py
import json
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError

from .a2ui_extension import create_a2ui_part, try_activate_a2ui_extension
from .agent import UIGeneratorAgent

logger = logging.getLogger(__name__)


class UIGeneratorExecutor(AgentExecutor):

    def __init__(self, base_url: str):
        self.ui_agent = UIGeneratorAgent(base_url=base_url, use_ui=True)
        self.text_agent = UIGeneratorAgent(base_url=base_url, use_ui=False)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = ""
        ui_event_part = None
        action = None

        logger.info(f"Client requested extensions: {context.requested_extensions}")
        use_ui = try_activate_a2ui_extension(context)
        agent = self.ui_agent if use_ui else self.text_agent

        # Extract conversation history from metadata
        conversation_history = []
        try:
            metadata = getattr(context.message, "metadata", None) or {}
            # Also check params-level metadata passed via configuration
            if not metadata and hasattr(context, "params"):
                metadata = getattr(context.params, "metadata", {}) or {}
            conversation_history = metadata.get("conversationHistory", [])
            if conversation_history:
                logger.info(f"Received {len(conversation_history)} history turns")
        except Exception as e:
            logger.warning(f"Could not extract conversation history: {e}")

        # Process incoming message parts
        if context.message and context.message.parts:
            for i, part in enumerate(context.message.parts):
                if isinstance(part.root, DataPart):
                    if "userAction" in part.root.data:
                        ui_event_part = part.root.data["userAction"]
                elif isinstance(part.root, TextPart):
                    pass

        # Handle A2UI ClientEvents
        if ui_event_part:
            action = ui_event_part.get("actionName")
            ctx = ui_event_part.get("context", {})
            if action == "submit_form":
                form_data = ", ".join(f"{k}: {v}" for k, v in ctx.items())
                query = f"User submitted a form with the following data: {form_data}"
            else:
                query = f"User action: {action} with data: {ctx}"
        else:
            query = context.get_user_input()

        logger.info(f"Final query: '{query}', history turns: {len(conversation_history)}")

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # Stream agent response — pass history for context retention
        async for item in agent.stream(query, task.context_id, conversation_history=conversation_history):
            is_task_complete = item["is_task_complete"]

            if not is_task_complete:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            final_state = (
                TaskState.completed if action == "submit_form" else TaskState.input_required
            )

            content = item["content"]
            final_parts = []

            if "---a2ui_JSON---" in content:
                text_content, json_string = content.split("---a2ui_JSON---", 1)
                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))
                if json_string.strip():
                    try:
                        json_string_cleaned = (
                            json_string.strip().lstrip("```json").rstrip("```").strip()
                        )
                        json_data = json.loads(json_string_cleaned)
                        if isinstance(json_data, list):
                            for message in json_data:
                                final_parts.append(create_a2ui_part(message))
                        else:
                            final_parts.append(create_a2ui_part(json_data))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse UI JSON: {e}")
                        final_parts.append(Part(root=TextPart(text=json_string)))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            await updater.update_status(
                final_state,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=(final_state == TaskState.completed),
            )
            break

    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())


RestaurantAgentExecutor = UIGeneratorExecutor
