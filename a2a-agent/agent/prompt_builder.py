# prompt_builder.py
"""
Prompt builder for the A2UI UI Generator agent.

This module provides the A2UI JSON schema and example templates
that the LLM uses to generate declarative UI responses for any type of UI.
"""

# The A2UI schema defines the structure of A2UI messages for rendering dynamic UIs.
# This schema supports text-only components (no images) for flexibility.
A2UI_SCHEMA = r'''
{
  "title": "A2UI Message Schema",
  "description": "Describes a JSON payload for an A2UI (Agent to UI) message, which is used to dynamically construct and update user interfaces. A message MUST contain exactly ONE of the action properties: 'beginRendering', 'surfaceUpdate', 'dataModelUpdate', or 'deleteSurface'.",
  "type": "object",
  "properties": {
    "beginRendering": {
      "type": "object",
      "description": "Signals the client to begin rendering a surface with a root component and specific styles.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface to be rendered."
        },
        "root": {
          "type": "string",
          "description": "The ID of the root component to render."
        },
        "styles": {
          "type": "object",
          "description": "Styling information for the UI.",
          "properties": {
            "font": {
              "type": "string",
              "description": "The primary font for the UI."
            },
            "primaryColor": {
              "type": "string",
              "description": "The primary UI color as a hexadecimal code (e.g., '#00BFFF').",
              "pattern": "^#[0-9a-fA-F]{6}$"
            }
          }
        }
      },
      "required": ["root", "surfaceId"]
    },
    "surfaceUpdate": {
      "type": "object",
      "description": "Updates a surface with a new set of components.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface to be updated."
        },
        "components": {
          "type": "array",
          "description": "A list containing all UI components for the surface.",
          "minItems": 1,
          "items": {
            "type": "object",
            "description": "Represents a single component in a UI widget tree.",
            "properties": {
              "id": {
                "type": "string",
                "description": "The unique identifier for this component."
              },
              "weight": {
                "type": "number",
                "description": "The relative weight of this component within a Row or Column (CSS flex-grow)."
              },
              "component": {
                "type": "object",
                "description": "A wrapper object containing exactly one component type key.",
                "properties": {
                  "Text": {
                    "type": "object",
                    "properties": {
                      "text": {
                        "type": "object",
                        "description": "Text content - literal string or data model path.",
                        "properties": {
                          "literalString": { "type": "string" },
                          "path": { "type": "string" }
                        }
                      },
                      "usageHint": {
                        "type": "string",
                        "enum": ["h1", "h2", "h3", "h4", "h5", "caption", "body"]
                      }
                    },
                    "required": ["text"]
                  },
                  "Icon": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "object",
                        "properties": {
                          "literalString": {
                            "type": "string",
                            "enum": ["accountCircle", "add", "arrowBack", "arrowForward", "calendarToday", "call", "check", "close", "delete", "edit", "error", "favorite", "help", "home", "info", "locationOn", "mail", "menu", "notifications", "person", "phone", "search", "send", "settings", "share", "star", "starHalf", "starOff", "warning"]
                          },
                          "path": { "type": "string" }
                        }
                      }
                    },
                    "required": ["name"]
                  },
                  "Row": {
                    "type": "object",
                    "properties": {
                      "children": {
                        "type": "object",
                        "properties": {
                          "explicitList": { "type": "array", "items": { "type": "string" } },
                          "template": {
                            "type": "object",
                            "properties": {
                              "componentId": { "type": "string" },
                              "dataBinding": { "type": "string" }
                            },
                            "required": ["componentId", "dataBinding"]
                          }
                        }
                      },
                      "distribution": {
                        "type": "string",
                        "enum": ["center", "end", "spaceAround", "spaceBetween", "spaceEvenly", "start"]
                      },
                      "alignment": {
                        "type": "string",
                        "enum": ["start", "center", "end", "stretch"]
                      }
                    },
                    "required": ["children"]
                  },
                  "Column": {
                    "type": "object",
                    "properties": {
                      "children": {
                        "type": "object",
                        "properties": {
                          "explicitList": { "type": "array", "items": { "type": "string" } },
                          "template": {
                            "type": "object",
                            "properties": {
                              "componentId": { "type": "string" },
                              "dataBinding": { "type": "string" }
                            },
                            "required": ["componentId", "dataBinding"]
                          }
                        }
                      },
                      "distribution": {
                        "type": "string",
                        "enum": ["start", "center", "end", "spaceBetween", "spaceAround", "spaceEvenly"]
                      },
                      "alignment": {
                        "type": "string",
                        "enum": ["center", "end", "start", "stretch"]
                      }
                    },
                    "required": ["children"]
                  },
                  "List": {
                    "type": "object",
                    "properties": {
                      "children": {
                        "type": "object",
                        "properties": {
                          "explicitList": { "type": "array", "items": { "type": "string" } },
                          "template": {
                            "type": "object",
                            "properties": {
                              "componentId": { "type": "string" },
                              "dataBinding": { "type": "string" }
                            },
                            "required": ["componentId", "dataBinding"]
                          }
                        }
                      },
                      "direction": {
                        "type": "string",
                        "enum": ["vertical", "horizontal"]
                      },
                      "alignment": {
                        "type": "string",
                        "enum": ["start", "center", "end", "stretch"]
                      }
                    },
                    "required": ["children"]
                  },
                  "Card": {
                    "type": "object",
                    "properties": {
                      "child": { "type": "string" }
                    },
                    "required": ["child"]
                  },
                  "Divider": {
                    "type": "object",
                    "properties": {
                      "axis": {
                        "type": "string",
                        "enum": ["horizontal", "vertical"]
                      }
                    }
                  },
                  "Button": {
                    "type": "object",
                    "properties": {
                      "child": { "type": "string" },
                      "primary": { "type": "boolean" },
                      "action": {
                        "type": "object",
                        "properties": {
                          "name": { "type": "string" },
                          "context": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "key": { "type": "string" },
                                "value": {
                                  "type": "object",
                                  "properties": {
                                    "path": { "type": "string" },
                                    "literalString": { "type": "string" },
                                    "literalNumber": { "type": "number" },
                                    "literalBoolean": { "type": "boolean" }
                                  }
                                }
                              },
                              "required": ["key", "value"]
                            }
                          }
                        },
                        "required": ["name"]
                      }
                    },
                    "required": ["child", "action"]
                  },
                  "TextField": {
                    "type": "object",
                    "properties": {
                      "label": {
                        "type": "object",
                        "properties": {
                          "literalString": { "type": "string" },
                          "path": { "type": "string" }
                        }
                      },
                      "text": {
                        "type": "object",
                        "properties": {
                          "literalString": { "type": "string" },
                          "path": { "type": "string" }
                        }
                      },
                      "textFieldType": {
                        "type": "string",
                        "enum": ["date", "longText", "number", "shortText", "obscured"]
                      }
                    },
                    "required": ["label"]
                  },
                  "DateTimeInput": {
                    "type": "object",
                    "properties": {
                      "value": {
                        "type": "object",
                        "properties": {
                          "literalString": { "type": "string" },
                          "path": { "type": "string" }
                        }
                      },
                      "enableDate": { "type": "boolean" },
                      "enableTime": { "type": "boolean" }
                    },
                    "required": ["value"]
                  }
                }
              }
            },
            "required": ["id", "component"]
          }
        }
      },
      "required": ["surfaceId", "components"]
    },
    "dataModelUpdate": {
      "type": "object",
      "description": "Updates the data model for a surface.",
      "properties": {
        "surfaceId": { "type": "string" },
        "path": { "type": "string" },
        "contents": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "key": { "type": "string" },
              "valueString": { "type": "string" },
              "valueNumber": { "type": "number" },
              "valueBoolean": { "type": "boolean" },
              "valueMap": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "key": { "type": "string" },
                    "valueString": { "type": "string" },
                    "valueNumber": { "type": "number" },
                    "valueBoolean": { "type": "boolean" }
                  },
                  "required": ["key"]
                }
              }
            },
            "required": ["key"]
          }
        }
      },
      "required": ["contents", "surfaceId"]
    },
    "deleteSurface": {
      "type": "object",
      "description": "Signals the client to delete the surface identified by 'surfaceId'.",
      "properties": {
        "surfaceId": { "type": "string" }
      },
      "required": ["surfaceId"]
    }
  }
}
'''

# Generic UI examples for the A2UI agent
# These templates show how to build forms, lists, cards, and confirmations
UI_EXAMPLES = """
---BEGIN FORM_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "form-surface", "root": "form-column", "styles": {{ "primaryColor": "#9B8AFF", "font": "Plus Jakarta Sans" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "form-surface",
    "components": [
      {{ "id": "form-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["form-title", "name-field", "email-field", "message-field", "submit-button"] }} }} }} }},
      {{ "id": "form-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "literalString": "Contact Us" }} }} }} }},
      {{ "id": "name-field", "component": {{ "TextField": {{ "label": {{ "literalString": "Your Name" }}, "text": {{ "path": "name" }}, "textFieldType": "shortText" }} }} }},
      {{ "id": "email-field", "component": {{ "TextField": {{ "label": {{ "literalString": "Email Address" }}, "text": {{ "path": "email" }}, "textFieldType": "shortText" }} }} }},
      {{ "id": "message-field", "component": {{ "TextField": {{ "label": {{ "literalString": "Message" }}, "text": {{ "path": "message" }}, "textFieldType": "longText" }} }} }},
      {{ "id": "submit-button", "component": {{ "Button": {{ "child": "submit-text", "primary": true, "action": {{ "name": "submit_form", "context": [ {{ "key": "name", "value": {{ "path": "name" }} }}, {{ "key": "email", "value": {{ "path": "email" }} }}, {{ "key": "message", "value": {{ "path": "message" }} }} ] }} }} }} }},
      {{ "id": "submit-text", "component": {{ "Text": {{ "text": {{ "literalString": "Send Message" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "form-surface",
    "path": "/",
    "contents": [
      {{ "key": "name", "valueString": "" }},
      {{ "key": "email", "valueString": "" }},
      {{ "key": "message", "valueString": "" }}
    ]
  }} }}
]
---END FORM_EXAMPLE---

---BEGIN LIST_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "list-surface", "root": "list-column", "styles": {{ "primaryColor": "#9B8AFF", "font": "Plus Jakarta Sans" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "list-surface",
    "components": [
      {{ "id": "list-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["list-title", "item-list"] }} }} }} }},
      {{ "id": "list-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "literalString": "Todo List" }} }} }} }},
      {{ "id": "item-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "item-row-template", "dataBinding": "/items" }} }} }} }} }},
      {{ "id": "item-row-template", "component": {{ "Row": {{ "alignment": "center", "children": {{ "explicitList": ["item-icon", "item-text"] }} }} }} }},
      {{ "id": "item-icon", "component": {{ "Icon": {{ "name": {{ "path": "icon" }} }} }} }},
      {{ "id": "item-text", "weight": 1, "component": {{ "Text": {{ "text": {{ "path": "text" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "list-surface",
    "path": "/",
    "contents": [
      {{ "key": "items", "valueMap": [
        {{ "key": "item1", "valueMap": [ {{ "key": "icon", "valueString": "check" }}, {{ "key": "text", "valueString": "First item" }} ] }},
        {{ "key": "item2", "valueMap": [ {{ "key": "icon", "valueString": "check" }}, {{ "key": "text", "valueString": "Second item" }} ] }},
        {{ "key": "item3", "valueMap": [ {{ "key": "icon", "valueString": "check" }}, {{ "key": "text", "valueString": "Third item" }} ] }}
      ] }}
    ]
  }} }}
]
---END LIST_EXAMPLE---

---BEGIN CARD_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "card-surface", "root": "profile-card", "styles": {{ "primaryColor": "#9B8AFF", "font": "Plus Jakarta Sans" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "card-surface",
    "components": [
      {{ "id": "profile-card", "component": {{ "Card": {{ "child": "card-content" }} }} }},
      {{ "id": "card-content", "component": {{ "Column": {{ "alignment": "center", "children": {{ "explicitList": ["profile-icon", "profile-name", "profile-title", "divider1", "contact-row"] }} }} }} }},
      {{ "id": "profile-icon", "component": {{ "Icon": {{ "name": {{ "literalString": "accountCircle" }} }} }} }},
      {{ "id": "profile-name", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "name" }} }} }} }},
      {{ "id": "profile-title", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "title" }} }} }} }},
      {{ "id": "divider1", "component": {{ "Divider": {{}} }} }},
      {{ "id": "contact-row", "component": {{ "Column": {{ "children": {{ "explicitList": ["email-row", "phone-row"] }} }} }} }},
      {{ "id": "email-row", "component": {{ "Row": {{ "alignment": "center", "children": {{ "explicitList": ["email-icon", "email-text"] }} }} }} }},
      {{ "id": "email-icon", "component": {{ "Icon": {{ "name": {{ "literalString": "mail" }} }} }} }},
      {{ "id": "email-text", "component": {{ "Text": {{ "text": {{ "path": "email" }} }} }} }},
      {{ "id": "phone-row", "component": {{ "Row": {{ "alignment": "center", "children": {{ "explicitList": ["phone-icon", "phone-text"] }} }} }} }},
      {{ "id": "phone-icon", "component": {{ "Icon": {{ "name": {{ "literalString": "phone" }} }} }} }},
      {{ "id": "phone-text", "component": {{ "Text": {{ "text": {{ "path": "phone" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "card-surface",
    "path": "/",
    "contents": [
      {{ "key": "name", "valueString": "John Doe" }},
      {{ "key": "title", "valueString": "Software Engineer" }},
      {{ "key": "email", "valueString": "john.doe@example.com" }},
      {{ "key": "phone", "valueString": "+1 (555) 123-4567" }}
    ]
  }} }}
]
---END CARD_EXAMPLE---

---BEGIN CONFIRMATION_EXAMPLE---
[
  {{ "beginRendering": {{ "surfaceId": "confirmation-surface", "root": "confirmation-card", "styles": {{ "primaryColor": "#9B8AFF", "font": "Plus Jakarta Sans" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "confirmation-surface",
    "components": [
      {{ "id": "confirmation-card", "component": {{ "Card": {{ "child": "confirmation-column" }} }} }},
      {{ "id": "confirmation-column", "component": {{ "Column": {{ "alignment": "center", "children": {{ "explicitList": ["confirm-icon", "confirm-title", "divider1", "confirm-message", "confirm-details"] }} }} }} }},
      {{ "id": "confirm-icon", "component": {{ "Icon": {{ "name": {{ "literalString": "check" }} }} }} }},
      {{ "id": "confirm-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "literalString": "Success!" }} }} }} }},
      {{ "id": "divider1", "component": {{ "Divider": {{}} }} }},
      {{ "id": "confirm-message", "component": {{ "Text": {{ "text": {{ "path": "message" }} }} }} }},
      {{ "id": "confirm-details", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "details" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "confirmation-surface",
    "path": "/",
    "contents": [
      {{ "key": "message", "valueString": "Your request has been processed successfully." }},
      {{ "key": "details", "valueString": "Reference: ABC-123456" }}
    ]
  }} }}
]
---END CONFIRMATION_EXAMPLE---
"""

# Backward compatibility alias
RESTAURANT_UI_EXAMPLES = UI_EXAMPLES


def get_ui_prompt(base_url: str, examples: str) -> str:
    return f"""
    ABSOLUTE OUTPUT FORMAT — YOU MUST FOLLOW THIS EXACTLY:

    Your response MUST have exactly two parts separated by ---a2ui_JSON---

    PART 1: One sentence of conversational text (e.g. "Here is your contact form.")
    PART 2: The raw A2UI JSON array — NO markdown, NO code fences, NO ```json

    Example of correct output format:
    Here is your contact form.
    ---a2ui_JSON---
    [
      {{"beginRendering": {{"surfaceId": "s1", "root": "col1"}}}},
      {{"surfaceUpdate": {{"surfaceId": "s1", "components": []}}}}
    ]

    RULES — VIOLATION WILL CAUSE THE UI TO FAIL:
    1. The delimiter ---a2ui_JSON--- MUST appear exactly once
    2. NEVER wrap the JSON in ```json or ``` or any markdown
    3. The JSON MUST be a valid array starting with [ and ending with ]
    4. ALWAYS start with a beginRendering message
    5. ALWAYS follow with a surfaceUpdate message
    6. ALWAYS end with a dataModelUpdate message

    --- UI TEMPLATE DEFAULTS ---
    Use these examples as starting patterns for common UI types:
    - For forms (contact, signup, survey, settings): Start with FORM_EXAMPLE
    - For lists (todo, shopping, search results, notifications): Start with LIST_EXAMPLE
    - For cards (profile, product, info, stats): Start with CARD_EXAMPLE
    - For confirmations (success, error, status updates): Start with CONFIRMATION_EXAMPLE

    --- DYNAMIC UI GENERATION ---
    Templates are starting points, not strict requirements. Modify them based on user requests:

    Adding fields:
    - Add new TextField, DateTimeInput, or other appropriate components
    - Add the field to the Column children explicitList
    - Add a corresponding key in dataModelUpdate contents
    - For forms with submit buttons, add the field path to button action context array

    Adding list items: Populate the dataModelUpdate with the requested items.

    Changing layouts:
    - Use Row for horizontal arrangements
    - Use Column for vertical arrangements
    - Use List with template for repeating items

    Changing labels and text: Update literalString values as needed.

    Available components:
    - Text: Display text with optional usageHint (h1, h2, h3, h4, h5, caption, body)
    - Icon: accountCircle, add, check, close, delete, edit, error, favorite, help,
            home, info, locationOn, mail, menu, notifications, person, phone,
            search, send, settings, share, star, warning
    - Row/Column: Layout containers with children
    - List: Repeating items with template binding
    - Card: Container with shadow/border
    - Divider: Visual separator
    - Button: Interactive button with action
    - TextField: shortText, longText, number, date, obscured
    - DateTimeInput: Date and/or time picker

    {examples}

    ---BEGIN A2UI JSON SCHEMA---
    {A2UI_SCHEMA}
    ---END A2UI JSON SCHEMA---
    """


def get_text_prompt() -> str:
    """
    Constructs the prompt for a text-only agent response.
    """
    return """
    You are a helpful UI assistant. Your final output MUST be a text response.

    You can help users with:
    - Describing UI layouts and components
    - Explaining how to structure forms, lists, cards, and other UI elements
    - Providing guidance on UI/UX best practices

    Keep your responses clear, helpful, and conversational.
    """


if __name__ == "__main__":
    # Example usage
    my_base_url = "http://localhost:10002"
    ui_prompt = get_ui_prompt(my_base_url, UI_EXAMPLES)
    print(ui_prompt[:500] + "...")
