"""
IT Agent orchestrator.

Drives a Claude Opus 4.7 agentic loop with tool-calling.
The system prompt is cached via prompt caching to reduce costs on repeated calls.
"""

import logging
from typing import Any

import anthropic

import config
from agent.prompts import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, execute_tool
from tools.handlers import close_all

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 30  # safety cap — prevents infinite loops


class ITAgent:
    """
    Stateless agent runner. Each call to handle_ticket() runs a fresh
    agentic loop for the given ticket.
    """

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def handle_ticket(self, ticket_id: int) -> str:
        """
        Run the full IT workflow for a single AutoTask ticket.

        Returns a summary of actions taken.
        """
        logger.info("Starting agent loop for ticket #%d", ticket_id)
        user_message = (
            f"Please handle AutoTask ticket #{ticket_id}. "
            "Follow the standard workflow: read the ticket, gather context from ITGlue "
            "and Passportal, check devices in VSA if relevant, add an internal note "
            "with your findings, reply to the client professionally, and update the "
            "ticket status."
        )
        return self._run_loop(user_message)

    def handle_new_tickets(
        self,
        status: int = 1,
        queue_id: int | None = None,
        max_tickets: int = 5,
    ) -> str:
        """
        Fetch and process a batch of tickets from a queue.

        Returns a summary of all tickets processed.
        """
        queue_hint = f" from queue {queue_id}" if queue_id else ""
        user_message = (
            f"Retrieve up to {max_tickets} tickets with status={status}{queue_hint} "
            "from AutoTask using autotask_list_tickets, then handle each one "
            "following the standard workflow."
        )
        return self._run_loop(user_message)

    def ask(self, question: str) -> str:
        """
        Free-form query — the agent will use whatever tools it needs to answer.

        Example: "What is the patch status of all online VSA agents?"
        """
        return self._run_loop(question)

    # ------------------------------------------------------------------
    # Core agentic loop
    # ------------------------------------------------------------------

    def _run_loop(self, user_message: str) -> str:
        """
        Run a Claude tool-calling loop until stop_reason == 'end_turn'
        or MAX_TOOL_ROUNDS is reached.

        Prompt caching:
          • The system prompt gets cache_control so its tokens are cached
            across repeated calls (saves ~90% on the cached portion).
        """
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_message}
        ]

        for round_num in range(MAX_TOOL_ROUNDS):
            logger.debug("Agent round %d", round_num + 1)

            response = self._client.messages.create(
                model="claude-opus-4-7",