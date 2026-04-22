# Bootstrap files for IT Workflow Agent when repository checkout is empty.
# Run in PowerShell from the project folder.

$script = @'
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from dataclasses import dataclass
from datetime import datetime, timezone

SEVERITY_SCORE={"critical":100,"high":75,"medium":45,"low":20}
BUSINESS_IMPACT_SCORE={"all_hands_blocked":100,"multiple_teams":80,"single_team":50,"single_user":20}

@dataclass
class Ticket:
    title:str
    description:str
    severity:str="medium"
    business_impact:str="single_team"
    requester:str="unknown"
    system:str="unspecified"
    @classmethod
    def from_dict(cls,d):
        return cls(str(d.get("title","Untitled ticket")),str(d.get("description","No description provided.")),str(d.get("severity","medium")).lower(),str(d.get("business_impact","single_team")).lower(),str(d.get("requester","unknown")),str(d.get("system","unspecified")))

class WorkflowAgent:
    def _heuristic_priority(self,t:Ticket):
        severity=SEVERITY_SCORE.get(t.severity,45)
        impact=BUSINESS_IMPACT_SCORE.get(t.business_impact,50)
        text=f"{t.title} {t.description}".lower()
        boost=min(10,sum(5 for k in ["outage","down","security","blocked","production","unable","failed"] if k in text))
        score=round(severity*0.45+impact*0.45+boost,1)
        if score>=85: level,sla="P1","Respond in 15 min, update every 30 min"
        elif score>=65: level,sla="P2","Respond in 30 min, update every 1 hour"
        elif score>=40: level,sla="P3","Respond in 2 hours, update every 4 hours"
        else: level,sla="P4","Respond same business day"
        return {"priority_score":score,"priority_level":level,"recommended_sla":sla}

    def triage_ticket(self,t:Ticket):
        return {"ticket":t.__dict__,"priority":self._heuristic_priority(t),"first_30_min_actions":["Acknowledge requester and scope","Check monitoring and recent deploys","Review logs and reproduce","Mitigate and communicate status"]}

    def build_daily_plan(self,tickets,max_items=8):
        rows=[self.triage_ticket(t) for t in tickets]
        rows=sorted(rows,key=lambda r:r["priority"]["priority_score"],reverse=True)[:max_items]
        return {"generated_at_utc":datetime.now(timezone.utc).isoformat(),"items":[{"slot":i+1,"task":r["ticket"]["title"],"priority":r["priority"]["priority_level"],"timebox_minutes":45 if r["priority"]["priority_level"] in {"P1","P2"} else 30} for i,r in enumerate(rows)]}

    def proofread(self,text,audience="internal"):
        clean=re.sub(r"\s+"," ",text).strip()
        tips=[]
        if "!!!" in clean: tips.append("Reduce excessive punctuation")
        if re.search(r"\bASAP\b",clean): tips.append("Replace ASAP with a concrete deadline")
        opener="Hi team," if audience=="internal" else "Hello,"
        return {"cleaned":clean,"rewrite_suggestion":f"{opener} {clean} Please confirm owner and ETA.","improvements":tips or ["Looks clear"]}


def read_json(path):
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def out(data):
    print(json.dumps(data,indent=2,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser(description="IT Workflow Agent")
    sp=p.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("triage"); a.add_argument("--ticket-file",required=True)
    b=sp.add_parser("plan"); b.add_argument("--tickets-file",required=True); b.add_argument("--max-items",type=int,default=8)
    c=sp.add_parser("proofread"); c.add_argument("--text",required=True); c.add_argument("--audience",choices=["internal","external"],default="internal")
    args=p.parse_args(); agent=WorkflowAgent()
    if args.cmd=="triage": out(agent.triage_ticket(Ticket.from_dict(read_json(args.ticket_file))))
    elif args.cmd=="plan": out(agent.build_daily_plan([Ticket.from_dict(x) for x in read_json(args.tickets_file)],args.max_items))
    else: out(agent.proofread(args.text,args.audience))

if __name__=="__main__": main()
'@

$ticket = @'
{
  "title": "VPN authentication failures for finance users",
  "description": "Multiple finance users report being unable to connect since 08:10 UTC. Error: invalid SAML response.",
  "severity": "high",
  "business_impact": "multiple_teams",
  "requester": "maria.chen",
  "system": "vpn-gateway"
}
'@

$tickets = @'
[
  {
    "title": "Email delivery delay for onboarding notifications",
    "description": "New hires are not receiving day-1 onboarding emails.",
    "severity": "medium",
    "business_impact": "single_team",
    "requester": "hr-ops",
    "system": "email-service"
  },
  {
    "title": "Production API outage in customer portal",
    "description": "Portal is down for all users. 500 errors started after deploy.",
    "severity": "critical",
    "business_impact": "all_hands_blocked",
    "requester": "noc",
    "system": "customer-portal"
  }
]
'@

New-Item -ItemType Directory -Force -Path .\examples | Out-Null
Set-Content -Path .\it_workflow_agent.py -Value $script -Encoding UTF8
Set-Content -Path .\examples\ticket.json -Value $ticket -Encoding UTF8
Set-Content -Path .\examples\tickets.json -Value $tickets -Encoding UTF8

Write-Host "Bootstrapped files created:" -ForegroundColor Green
Get-ChildItem .\it_workflow_agent.py, .\examples\ticket.json, .\examples\tickets.json
Write-Host "Run: python .\\it_workflow_agent.py triage --ticket-file .\\examples\\ticket.json" -ForegroundColor Yellow
