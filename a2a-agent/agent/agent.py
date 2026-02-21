# agent.py
import json
import logging
import os
from collections.abc import AsyncIterable
from typing import Any

import anthropic
import jsonschema

from .prompt_builder import A2UI_SCHEMA, UI_EXAMPLES

logger = logging.getLogger(__name__)

try:
    _single_schema = json.loads(A2UI_SCHEMA)
    A2UI_SCHEMA_OBJECT = {"type": "array", "items": _single_schema}
    logger.info("A2UI_SCHEMA successfully loaded for validation.")
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse A2UI_SCHEMA: {e}")
    A2UI_SCHEMA_OBJECT = None

SYSTEM_PROMPT = f"""You are a UI generation assistant. You output A2UI declarative JSON.

YOUR RESPONSE MUST FOLLOW THIS EXACT FORMAT — NO EXCEPTIONS:

One short sentence describing the UI.
---a2ui_JSON---
[A2UI JSON array here]

RULES:
RULES:
0. COMPANY NAME — MANDATORY: The very first component in EVERY UI must be an h1 Text with an invented fictional company name. Examples: "Synapse Labs", "Cortex AI", "Luminary Systems", "Apex Neural". NEVER use generic text like "AI Startup" or "Join Our Team" as the h1.
00. FORBIDDEN h1 values: "AI Startup", "Our Company", "Join Our Team", "Contact Us", "Application Form", "Dashboard". These are BANNED as h1 text.
1. The delimiter ---a2ui_JSON--- must appear exactly once
2. After the delimiter, output ONLY a raw JSON array — no markdown, no backticks, no ```json
3. The array must start with [ and end with ]
4. Always include these 3 messages in order: beginRendering, surfaceUpdate, dataModelUpdate
5. When refining an existing UI, keep the SAME surfaceId and modify/extend the components as requested.
   Re-output the COMPLETE updated UI — all components including unchanged ones.
6. ALWAYS invent a specific fictional company/brand name and use it prominently as the UI title. NEVER use generic titles like "Join Our Team" or "Contact Us" alone. Examples: "NeuralPath AI — Join Our Team", "Synapse Labs Application", "Vertex Mind — New York". Pick a creative name and make it the h1 heading.

CORRECT FORMAT EXAMPLE:
Here is the NeuralPath AI contact form.
---a2ui_JSON---
[
  {{"beginRendering": {{"surfaceId": "form-surface", "root": "form-col", "styles": {{"primaryColor": "#9B8AFF", "font": "Plus Jakarta Sans"}}}}}},
  {{"surfaceUpdate": {{"surfaceId": "form-surface", "components": [
    {{"id": "form-col", "component": {{"Column": {{"children": {{"explicitList": ["title", "subtitle", "name-field", "submit-btn"]}}}}}}}},
    {{"id": "title", "component": {{"Text": {{"usageHint": "h1", "text": {{"literalString": "NeuralPath AI"}}}}}}}},
    {{"id": "subtitle", "component": {{"Text": {{"usageHint": "h3", "text": {{"literalString": "Contact Us"}}}}}}}},
    {{"id": "name-field", "component": {{"TextField": {{"label": {{"literalString": "Name"}}, "text": {{"path": "name"}}, "textFieldType": "shortText"}}}}}},
    {{"id": "submit-btn", "component": {{"Button": {{"child": "submit-text", "primary": true, "action": {{"name": "submit_form", "context": [{{"key": "name", "value": {{"path": "name"}}}}]}}}}}}}},
    {{"id": "submit-text", "component": {{"Text": {{"text": {{"literalString": "Submit"}}}}}}}}
  ]}}}},
  {{"dataModelUpdate": {{"surfaceId": "form-surface", "path": "/", "contents": [{{"key": "name", "valueString": ""}}]}}}}
]

AVAILABLE COMPONENT TYPES (use ONLY these):
- Text: {{"Text": {{"text": {{"literalString": "..."}}, "usageHint": "h1|h2|h3|h4|h5|caption|body"}}}}
- TextField: {{"TextField": {{"label": {{"literalString": "..."}}, "text": {{"path": "..."}}, "textFieldType": "shortText|longText|number|date|obscured"}}}}
- MultipleChoice: Native dropdown/select. {{"MultipleChoice": {{"description": {{"literalString": "Years of Experience"}}, "selections": {{"path": "experience"}}, "options": [{{"label": {{"literalString": "0-1 years"}}}}, {{"label": {{"literalString": "1-3 years"}}}}, {{"label": {{"literalString": "3-5 years"}}}}, {{"label": {{"literalString": "5+ years"}}}}]}}}}
  Use this for ANY selection/dropdown field. It renders as a native select element.
- Button: {{"Button": {{"child": "btn-text-id", "primary": true, "action": {{"name": "action_name", "context": []}}}}}}
- Column: {{"Column": {{"children": {{"explicitList": ["id1", "id2"]}}}}}}
- Row: {{"Row": {{"children": {{"explicitList": ["id1", "id2"]}}, "alignment": "center"}}}}
- Card: {{"Card": {{"child": "content-id"}}}}
- Icon: {{"Icon": {{"name": {{"literalString": "check|mail|person|phone|search|settings|star|home|info|warning|error|favorite|send|accountCircle|add|close|delete|edit|notifications|share"}}}}}}
- Divider: {{"Divider": {{}}}}
- List: {{"List": {{"direction": "vertical", "children": {{"template": {{"componentId": "...", "dataBinding": "/items"}}}}}}}}

FULL EXAMPLES TO COPY FROM:
{UI_EXAMPLES}
"""


class UIGeneratorAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, base_url: str, use_ui: bool = True):
        self.base_url = base_url
        self.use_ui = use_ui
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("LITELLM_MODEL", "claude-sonnet-4-5").replace("anthropic/", "")
        self.a2ui_schema_object = A2UI_SCHEMA_OBJECT
        logger.info(f"UIGeneratorAgent initialized with model: {self.model}")

    def get_processing_message(self) -> str:
        return "Generating your UI..."

    def _extract_a2ui(self, text: str) -> list | None:
        if "---a2ui_JSON---" not in text:
            logger.warning("Delimiter ---a2ui_JSON--- not found in response")
            return None

        _, json_part = text.split("---a2ui_JSON---", 1)
        json_part = json_part.strip()

        if json_part.startswith("```"):
            lines = json_part.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            json_part = "\n".join(lines).strip()

        try:
            parsed = json.loads(json_part)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
            logger.warning("Parsed JSON is not a non-empty list")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {json_part[:300]}")
            return None

    def _build_messages(self, query: str, conversation_history: list) -> list:
        """Build Anthropic messages array including prior conversation context."""
        messages = []

        # Inject prior turns so Claude remembers what it built
        for turn in conversation_history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # Force company name invention at the query level — most reliable injection point
        enhanced_query = (
            f"{query}\n\n"
            f"IMPORTANT: You MUST invent a specific fictional company name and use it as the h1 heading. "
            f"Do NOT use 'AI Startup', 'Our Company', 'Join Our Team', or any generic title. "
            f"Pick something creative like 'Synapse Labs', 'Cortex AI', 'Luminary Systems', 'Apex Neural'. "
            f"The h1 MUST be the invented company name."
        )
        messages.append({"role": "user", "content": enhanced_query})
        return messages

    async def stream(self, query: str, session_id: str, conversation_history: list = None) -> AsyncIterable[dict[str, Any]]:
        if self.use_ui and self.a2ui_schema_object is None:
            yield {"is_task_complete": True, "content": "Schema not loaded."}
            return

        if conversation_history is None:
            conversation_history = []

        max_retries = 2
        messages = self._build_messages(query, conversation_history)

        for attempt in range(1, max_retries + 1):
            logger.info(f"Attempt {attempt}/{max_retries}, history turns: {len(conversation_history)}")
            yield {"is_task_complete": False, "updates": self.get_processing_message()}

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                )
                response_text = response.content[0].text
                logger.info(f"Claude response preview: {response_text[:200]}")
            except Exception as e:
                logger.error(f"Claude API error: {e}")
                if attempt < max_retries:
                    continue
                yield {"is_task_complete": True, "content": f"API error: {e}"}
                return

            if not self.use_ui:
                yield {"is_task_complete": True, "content": response_text}
                return

            extracted = self._extract_a2ui(response_text)

            if extracted is not None:
                try:
                    jsonschema.validate(instance=extracted, schema=self.a2ui_schema_object)
                    logger.info("A2UI JSON validated successfully")
                    text_part = response_text.split("---a2ui_JSON---")[0].strip()
                    yield {
                        "is_task_complete": True,
                        "content": f"{text_part}\n---a2ui_JSON---\n{json.dumps(extracted)}",
                    }
                    return
                except jsonschema.exceptions.ValidationError as e:
                    logger.warning(f"Schema validation failed: {e.message}")
                    error_detail = f"Schema error: {e.message}"
            else:
                error_detail = "Response missing ---a2ui_JSON--- delimiter or valid JSON array"

            # Retry with correction
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    f"WRONG FORMAT. {error_detail}\n\n"
                    f"Output EXACTLY:\nOne sentence.\n---a2ui_JSON---\n"
                    f"[{{\"beginRendering\": ...}}, {{\"surfaceUpdate\": ...}}, {{\"dataModelUpdate\": ...}}]\n\n"
                    f"No markdown. Raw JSON array only. Original request: {query}"
                ),
            })

        logger.error("All retries exhausted")
        yield {"is_task_complete": True, "content": "Unable to generate UI. Please try again."}


RestaurantAgent = UIGeneratorAgent