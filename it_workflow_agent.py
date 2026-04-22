#!/usr/bin/env python3
"""IT Workflow Agent

A practical local agent that helps with daily IT operations:
- Troubleshooting ticket analysis
- Prioritization scoring
- Daily planning
- Proofreading internal/external notes

The agent can run in two modes:
1) Heuristic mode (default, no API key required)
2) LLM-assisted mode (set OPENAI_API_KEY and install openai package)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


SEVERITY_SCORE = {
    "critical": 100,
    "high": 75,
    "medium": 45,
    "low": 20,
}

BUSINESS_IMPACT_SCORE = {
    "all_hands_blocked": 100,
    "multiple_teams": 80,
    "single_team": 50,
    "single_user": 20,
}


@dataclass
class Ticket:
    title: str
    description: str
    severity: str = "medium"
    business_impact: str = "single_team"
    requester: str = "unknown"
    system: str = "unspecified"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ticket":
        return cls(
            title=str(data.get("title", "Untitled ticket")),
            description=str(data.get("description", "No description provided.")),
            severity=str(data.get("severity", "medium")).lower(),
            business_impact=str(data.get("business_impact", "single_team")).lower(),
            requester=str(data.get("requester", "unknown")),
            system=str(data.get("system", "unspecified")),
        )


class WorkflowAgent:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _llm_available(self) -> bool:
        return bool(self.api_key)

    def _heuristic_priority(self, ticket: Ticket) -> dict[str, Any]:
        severity = SEVERITY_SCORE.get(ticket.severity, SEVERITY_SCORE["medium"])
        impact = BUSINESS_IMPACT_SCORE.get(
            ticket.business_impact, BUSINESS_IMPACT_SCORE["single_team"]
        )

        urgency_keywords = [
            "outage",
            "down",
            "breach",
            "security",
            "unable",
            "failed",
            "blocked",
            "production",
            "vip",
        ]
        kw_boost = 0
        lowered = f"{ticket.title} {ticket.description}".lower()
        for keyword in urgency_keywords:
            if keyword in lowered:
                kw_boost += 5

        total = round((severity * 0.45) + (impact * 0.45) + min(kw_boost, 10), 1)

        if total >= 85:
            level = "P1"
            sla_target = "Respond in 15 min, update every 30 min"
        elif total >= 65:
            level = "P2"
            sla_target = "Respond in 30 min, update every 1 hour"
        elif total >= 40:
            level = "P3"
            sla_target = "Respond in 2 hours, update every 4 hours"
        else:
            level = "P4"
            sla_target = "Respond same business day"

        return {
            "priority_score": total,
            "priority_level": level,
            "recommended_sla": sla_target,
            "drivers": {
                "severity_score": severity,
                "business_impact_score": impact,
                "keyword_boost": min(kw_boost, 10),
            },
        }

    def triage_ticket(self, ticket: Ticket) -> dict[str, Any]:
        priority = self._heuristic_priority(ticket)

        checklist = [
            "Acknowledge requester and confirm impact/scope",
            "Check monitoring dashboards and recent deployments",
            "Review error logs for the affected system",
            "Attempt reproducible steps and document evidence",
            "Apply mitigation or rollback if user impact is active",
            "Open escalation if blocked > 20 minutes",
        ]

        notes = [
            f"System: {ticket.system}",
            f"Requester: {ticket.requester}",
            "Create timeline notes immediately to simplify postmortem",
        ]

        return {
            "ticket": ticket.__dict__,
            "priority": priority,
            "first_30_min_actions": checklist,
            "operator_notes": notes,
        }

    def build_daily_plan(self, tickets: list[Ticket], max_items: int = 8) -> dict[str, Any]:
        triaged = [self.triage_ticket(t) for t in tickets]
        sorted_items = sorted(
            triaged,
            key=lambda item: item["priority"]["priority_score"],
            reverse=True,
        )
        top = sorted_items[:max_items]

        plan = []
        for idx, item in enumerate(top, start=1):
            t = item["ticket"]
            p = item["priority"]
            plan.append(
                {
                    "slot": idx,
                    "task": t["title"],
                    "priority": p["priority_level"],
                    "timebox_minutes": 45 if p["priority_level"] in {"P1", "P2"} else 30,
                    "outcome": "Send status update + next checkpoint",
                }
            )

        return {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "items": plan,
            "focus_guidance": [
                "Reserve first 90 minutes for top two priorities",
                "Batch low-priority ticket updates in one communication block",
                "Leave a 30-minute buffer before end-of-day for spillover",
            ],
        }

    def proofread(self, text: str, audience: str = "internal") -> dict[str, Any]:
        cleaned = re.sub(r"\s+", " ", text).strip()
        suggestions = []

        if len(cleaned.split()) < 5:
            suggestions.append("Add more context so recipients can act without follow-up.")

        if "!!!" in cleaned:
            suggestions.append("Reduce excessive punctuation to keep tone professional.")

        if re.search(r"\bASAP\b", cleaned):
            suggestions.append("Replace 'ASAP' with a specific deadline.")

        if "kindly do the needful" in cleaned.lower():
            suggestions.append("Use direct action language with owner and due date.")

        opener = (
            "Hi team," if audience == "internal" else "Hello,"  # concise defaults
        )
        rewritten = (
            f"{opener} {cleaned} "
            "Please confirm owner, timeline, and any blockers. Thanks."
        )

        return {
            "audience": audience,
            "original": text,
            "cleaned": cleaned,
            "rewrite_suggestion": rewritten,
            "improvements": suggestions or ["Looks clear; no major issues detected."],
        }


def read_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IT Workflow Agent for ticket troubleshooting, prioritization, planning, and proofreading.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python it_workflow_agent.py triage --ticket-file examples/ticket.json
              python it_workflow_agent.py plan --tickets-file examples/tickets.json --max-items 6
              python it_workflow_agent.py proofread --text "Please fix VPN ASAP!!!" --audience external
            """
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    triage = subparsers.add_parser("triage", help="Triage one ticket and output an action plan")
    triage.add_argument("--ticket-file", required=True, help="Path to JSON file containing a single ticket")

    plan = subparsers.add_parser("plan", help="Build a prioritized daily plan from multiple tickets")
    plan.add_argument("--tickets-file", required=True, help="Path to JSON file containing a list of tickets")
    plan.add_argument("--max-items", type=int, default=8, help="Maximum number of items in plan")

    proofread = subparsers.add_parser("proofread", help="Proofread and rewrite a status note")
    proofread.add_argument("--text", required=True, help="Text to proofread")
    proofread.add_argument(
        "--audience",
        default="internal",
        choices=["internal", "external"],
        help="Tone target for rewriting",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = WorkflowAgent()

    if args.command == "triage":
        ticket_data = read_json_file(args.ticket_file)
        ticket = Ticket.from_dict(ticket_data)
        print_json(agent.triage_ticket(ticket))
        return

    if args.command == "plan":
        ticket_list = read_json_file(args.tickets_file)
        tickets = [Ticket.from_dict(item) for item in ticket_list]
        print_json(agent.build_daily_plan(tickets, args.max_items))
        return

    if args.command == "proofread":
        print_json(agent.proofread(args.text, args.audience))
        return

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
