#!/usr/bin/env python3
"""
IT Workflow Agent — CLI entry point.

Usage examples:

  # Handle a specific ticket by ID
  python main.py ticket 12345

  # Fetch and handle all new tickets from the default queue
  python main.py queue

  # Fetch new tickets from a specific queue (up to 10)
  python main.py queue --queue-id 8 --max 10

  # Free-form question / ad-hoc query
  python main.py ask "What is the patch status of ACME Corp's servers?"

  # Enable verbose logging
  python main.py -v ticket 12345
"""

import argparse
import logging
import sys

import config
from agent import ITAgent


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=level,
        stream=sys.stderr,
    )
    # Quiet down httpx connection noise unless verbose
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def _check_config() -> list[str]:
    """Return a list of missing required env-var names."""
    required = {
        "ANTHROPIC_API_KEY": config.ANTHROPIC_API_KEY,
        "AUTOTASK_USERNAME": config.AUTOTASK_USERNAME,
        "AUTOTASK_INTEGRATION_CODE": config.AUTOTASK_INTEGRATION_CODE,
        "ITGLUE_API_KEY": config.ITGLUE_API_KEY,
    }
    return [k for k, v in required.items() if not v]


def cmd_ticket(args: argparse.Namespace, agent: ITAgent) -> None:
    print(f"[agent] Handling ticket #{args.ticket_id} …\n", flush=True)
    result = agent.handle_ticket(args.ticket_id)
    print(result)


def cmd_queue(args: argparse.Namespace, agent: ITAgent) -> None:
    queue_info = f" (queue {args.queue_id})" if args.queue_id else ""
    print(f"[agent] Fetching up to {args.max} new tickets{queue_info} …\n", flush=True)
    result = agent.handle_new_tickets(
        status=1,
        queue_id=args.queue_id,
        max_tickets=args.max,
    )
    print(result)


def cmd_ask(args: argparse.Namespace, agent: ITAgent) -> None:
    print(f"[agent] {args.question}\n", flush=True)
    result = agent.ask(args.question)
    print(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IT Workflow Agent — Claude-powered help desk automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ticket <id>
    p_ticket = sub.add_parser("ticket", help="Handle a specific AutoTask ticket")
    p_ticket.add_argument("ticket_id", type=int, help="AutoTask ticket ID")

    # queue
    p_queue = sub.add_parser("queue", help="Process new tickets from a queue")
    p_queue.add_argument(
        "--queue-id", type=int, default=None,
        dest="queue_id",
        help="AutoTask queue ID (default: all queues)",
    )
    p_queue.add_argument(
        "--max", type=int, default=5,
        help="Maximum tickets to process in one run (default: 5)",
    )

    # ask <question>
    p_ask = sub.add_parser("ask", help="Free-form question answered using live data")
    p_ask.add_argument("question", help="The question to ask the agent")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    _setup_logging(args.verbose)

    missing = _check_config()
    if missing:
        print(
            f"ERROR: Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your credentials.",
            file=sys.stderr,
        )
        sys.exit(1)

    agent = ITAgent()
    try:
        dispatch = {
            "ticket": cmd_ticket,
            "queue": cmd_queue,
            "ask": cmd_ask,
        }
        dispatch[args.command](args, agent)
    except KeyboardInterrupt:
        print("\n[agent] Interrupted.", file=sys.stderr)
        sys.exit(130)
    finally:
        agent.close()


if __name__ == "__main__":
    main()