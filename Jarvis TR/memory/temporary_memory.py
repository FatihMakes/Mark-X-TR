# memory/temporary_memory.py
from typing import Any


class TemporaryMemory:
    """
    Temporary runtime memory (session-only).
    Resets when program restarts.

    Purpose:
      - Track multi-step intents
      - Keep short conversation context
      - Store last actions (search / open_app)
      - Support follow-up questions like:
          "why did he executed?"
    """

    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.reset()


    def reset(self):
        self.pending_intent: str | None = None
        self.parameters: dict[str, Any] = {}
        self.current_question: str | None = None

        self.last_user_text: str | None = None
        self.last_ai_response: str | None = None

        # --- Action memory ---
        self.last_search: dict | None = None   
        self.last_opened_app: str | None = None

        # --- Conversation ---
        self.conversation_history: list[dict[str, str]] = []


    def set_pending_intent(self, intent: str):
        self.pending_intent = intent

    def clear_pending_intent(self):
        self.pending_intent = None
        self.parameters = {}
        self.current_question = None

    def has_pending_intent(self) -> bool:
        return self.pending_intent is not None


    def update_parameters(self, new_params: dict):
        if not isinstance(new_params, dict):
            return
        for k, v in new_params.items():
            if v not in (None, ""):
                self.parameters[k] = v

    def get_parameters(self) -> dict:
        return self.parameters.copy()

    def get_parameter(self, key: str):
        return self.parameters.get(key)

    def set_current_question(self, param_name: str):
        self.current_question = param_name

    def get_current_question(self) -> str | None:
        return self.current_question

    def clear_current_question(self):
        self.current_question = None

    def set_last_user_text(self, text: str):
        self.last_user_text = text
        self._add_to_history("user", text)

    def set_last_ai_response(self, text: str):
        self.last_ai_response = text
        self._add_to_history("ai", text)

    def get_last_user_text(self):
        return self.last_user_text

    def get_last_ai_response(self):
        return self.last_ai_response


    def set_last_search(self, query: str, answer: str):
        self.last_search = {
            "query": query,
            "answer": answer
        }

    def get_last_search(self):
        return self.last_search

    def set_open_app(self, app_name: str):
        self.last_opened_app = app_name

    def get_last_opened_app(self):
        return self.last_opened_app

    def _add_to_history(self, role: str, text: str):
        if role not in ("user", "ai"):
            return

        self.conversation_history.append({
            "role": role,
            "text": text
        })

        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

    def get_history_for_prompt(self) -> str:
        """
        Returns compact history for LLM prompt.
        """
        return "\n".join(
            f"{m['role'].capitalize()}: {m['text']}"
            for m in self.conversation_history
        )


    def get_context_summary(self) -> dict:
        """
        Useful for debugging or smarter LLM prompts.
        """
        return {
            "pending_intent": self.pending_intent,
            "parameters": self.parameters,
            "last_search": self.last_search,
            "last_opened_app": self.last_opened_app,
            "last_user_text": self.last_user_text,
            "last_ai_response": self.last_ai_response,
        }
