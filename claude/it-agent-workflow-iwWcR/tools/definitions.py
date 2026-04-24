"""
Claude tool schemas for every integration.

Each tool maps 1-to-1 with a handler in tools/handlers.py.
Keep descriptions detailed — Claude relies on them to decide when to call each tool.
"""

TOOL_DEFINITIONS = [
    # ================================================================
    # AutoTask — Ticket Management
    # ================================================================
    {
        "name": "autotask_get_ticket",
        "description": (
            "Retrieve full details for a single AutoTask ticket by its numeric ID. "
            "Returns title, description, status, priority, account name, contact, "
            "queue, assigned resource, and timestamps."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer",
                    "description": "The AutoTask ticket ID.",
                }
            },
            "required": ["ticket_id"],
        },
    },
    {
        "name": "autotask_list_tickets",
        "description": (
            "Query AutoTask for open tickets. Optionally filter by status code, "
            "queue ID, or assigned resource ID. Status codes: 1=New, 8=In Progress, "
            "11=Waiting on Customer, 5=Complete. Returns up to max_results tickets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "integer",
                    "description": "Filter by status code (1=New, 8=In Progress, 11=Waiting, 5=Complete).",
                },
                "queue_id": {
                    "type": "integer",
                    "description": "Filter by AutoTask queue ID.",
                },
                "assigned_resource_id": {
                    "type": "integer",
                    "description": "Filter tickets assigned to a specific technician resource ID.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of tickets to return (default 25).",
                    "default": 25,
                },
            },
            "required": [],
        },
    },
    {
        "name": "autotask_add_note",
        "description": (
            "Add a note to an AutoTask ticket. "
            "Set internal=true for technician-only notes (not visible to client). "
            "Set internal=false for notes that are also sent/visible to the client. "
            "Always add an internal note documenting your findings before replying to the client."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "AutoTask ticket ID."},
                "title": {"type": "string", "description": "Short title for the note (≤50 chars)."},
                "description": {
                    "type": "string",
                    "description": "Full note body. May include findings, steps taken, or next actions.",
                },
                "internal": {
                    "type": "boolean",
                    "description": "True = internal only; False = visible to client. Default true.",
                    "default": True,
                },
            },
            "required": ["ticket_id", "title", "description"],
        },
    },
    {
        "name": "autotask_reply_to_ticket",
        "description": (
            "Post a client-facing reply on an AutoTask ticket. "
            "This creates a public note visible to the client. "
            "Use professional, empathetic language. "
            "Always add an internal note with findings BEFORE replying to the client."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "AutoTask ticket ID."},
                "message": {
                    "type": "string",