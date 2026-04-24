"""
Tool execution dispatcher.

Each function wraps one integration call and returns a plain string result
that Claude can read. Errors are caught and returned as descriptive strings
so Claude can reason about the failure and adapt.
"""

import json
import logging
from typing import Any

from integrations import AutoTaskClient, ITGlueClient, PassportalClient, VSAClient

logger = logging.getLogger(__name__)

# Singletons — instantiated once per agent session
_autotask: AutoTaskClient | None = None
_itglue: ITGlueClient | None = None
_passportal: PassportalClient | None = None
_vsa: VSAClient | None = None


def _at() -> AutoTaskClient:
    global _autotask
    if _autotask is None:
        _autotask = AutoTaskClient()
    return _autotask


def _ig() -> ITGlueClient:
    global _itglue
    if _itglue is None:
        _itglue = ITGlueClient()
    return _itglue


def _pp() -> PassportalClient:
    global _passportal
    if _passportal is None:
        _passportal = PassportalClient()
    return _passportal


def _vsa() -> VSAClient:
    global _vsa
    if _vsa is None:
        _vsa = VSAClient()
    return _vsa


def _json(obj: Any) -> str:
    return json.dumps(obj, indent=2, default=str)


def _safe(fn, *args, **kwargs) -> str:
    """Execute fn and return its JSON result, or an error string on failure."""
    try:
        return _json(fn(*args, **kwargs))
    except Exception as exc:
        logger.error("Tool call failed: %s", exc)
        return f"ERROR: {type(exc).__name__}: {exc}"


# ======================================================================
# AutoTask handlers
# ======================================================================

def handle_autotask_get_ticket(ticket_id: int) -> str:
    return _safe(_at().get_ticket, ticket_id)


def handle_autotask_list_tickets(
    status: int | None = None,
    queue_id: int | None = None,
    assigned_resource_id: int | None = None,
    max_results: int = 25,
) -> str:
    return _safe(
        _at().list_tickets,
        status=status,
        queue_id=queue_id,
        assigned_resource_id=assigned_resource_id,
        max_results=max_results,
    )


def handle_autotask_add_note(
    ticket_id: int,
    title: str,
    description: str,
    internal: bool = True,
) -> str:
    return _safe(_at().add_ticket_note, ticket_id, title, description, internal)


def handle_autotask_reply_to_ticket(ticket_id: int, message: str) -> str:
    return _safe(_at().reply_to_ticket, ticket_id, message)

