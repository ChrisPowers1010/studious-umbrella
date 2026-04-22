# IT Workflow Agent

A practical command-line agent for day-to-day IT operations.

It helps you:
- Triage and troubleshoot tickets quickly
- Prioritize work based on impact and urgency
- Build a focused daily execution plan
- Proofread and improve internal/external communication notes

---

## Run location (important)

You must run commands **inside the folder where this repo is downloaded** (the folder containing `it_workflow_agent.py`).

> The path `/workspace/studious-umbrella` is for this hosted Linux environment only.
> On your Windows PC, use the path where *you* cloned or unzipped this project.

### Windows PowerShell example

```powershell
# 1) Go to the folder where this repo exists on your machine
cd "C:\Users\Christopher\Desktop\studious-umbrella"

# 2) Confirm files are present
Get-ChildItem

# 3) Run the tool
python .\it_workflow_agent.py --help
python .\it_workflow_agent.py triage --ticket-file .\examples\ticket.json
```

### If you don't have the repo folder yet

```powershell
cd "C:\Users\Christopher\Desktop"
git clone <REPO_URL> studious-umbrella
cd .\studious-umbrella
python .\it_workflow_agent.py --help
```

### macOS/Linux example

```bash
cd /path/to/studious-umbrella
python it_workflow_agent.py --help
```

---

## 1) How to utilize it (fast path)

From the repository root:

```bash
python it_workflow_agent.py triage --ticket-file examples/ticket.json
python it_workflow_agent.py plan --tickets-file examples/tickets.json --max-items 6
python it_workflow_agent.py proofread --text "Please fix VPN ASAP!!!" --audience external
```

If you want to see all available commands/options:

```bash
python it_workflow_agent.py --help
python it_workflow_agent.py triage --help
python it_workflow_agent.py plan --help
python it_workflow_agent.py proofread --help
```

---

## 2) Typical daily workflow

### Morning intake (triage new tickets)
1. Export/prepare a ticket JSON file (or use your own).
2. Run `triage`.
3. Use the returned `priority_level`, `recommended_sla`, and `first_30_min_actions` to start response.

Example:

```bash
python it_workflow_agent.py triage --ticket-file examples/ticket.json
```

### Prioritize your work block (plan)
1. Put all active tickets into a JSON array.
2. Run `plan` to get an ordered queue.
3. Work top-down and send checkpoint updates at each timebox.

Example:

```bash
python it_workflow_agent.py plan --tickets-file examples/tickets.json --max-items 8
```

### Clean up communications (proofread)
1. Paste a draft note into `--text`.
2. Set `--audience internal` or `--audience external`.
3. Use rewrite suggestions before sending updates.

Example:

```bash
python it_workflow_agent.py proofread --text "VPN is still broken ASAP!!!" --audience internal
```

---

## 3) Ticket JSON format

### Single ticket (`triage`)

```json
{
  "title": "Production API outage",
  "description": "All users getting 500 errors after deployment",
  "severity": "critical",
  "business_impact": "all_hands_blocked",
  "requester": "noc",
  "system": "customer-portal"
}
```

### Ticket list (`plan`)

Pass a JSON array of ticket objects with the same fields.

---

## 4) Priority model

The agent calculates a `priority_score` from:
- `severity`
- `business_impact`
- urgency keyword detection in title/description

Then maps to `P1`-`P4` with a recommended response target.

---

## 5) Tips for real-world use

- Keep one `tickets_today.json` file and refresh it throughout the day.
- Re-run `plan` after major incident changes.
- Save command outputs to files for handoff notes:

```bash
python it_workflow_agent.py plan --tickets-file tickets_today.json > plan_output.json
python it_workflow_agent.py triage --ticket-file incident_1042.json > incident_1042_triage.json
```

---

## Notes

- Works locally with no external dependencies.
- Safe fallback for teams that cannot send ticket data to external services.
- You can extend this script to integrate with Jira/ServiceNow APIs.

## Troubleshooting path errors (Windows)

If you see errors like:
- `Cannot find path 'C:\workspace\studious-umbrella'`
- `can't open file 'C:\Users\...\it_workflow_agent.py'`

It means PowerShell is not in the project folder. Run:

```powershell
cd "C:\\path\\to\\studious-umbrella"
Get-ChildItem .\it_workflow_agent.py
Get-ChildItem .\examples\ticket.json
python .\it_workflow_agent.py triage --ticket-file .\examples\ticket.json
```


## First-time setup on Windows (if folder does not exist)

If `cd "C:\Users\Christopher\Desktop\studious-umbrella"` fails, the project is not on your machine yet.

### Option A: Clone with Git (recommended)

```powershell
cd "C:\Users\Christopher\Desktop"
git clone <REPO_URL> studious-umbrella
cd .\studious-umbrella
python .\it_workflow_agent.py --help
```

### Option B: Download ZIP from your Git host

1. Download the repository ZIP from your Git web page.
2. Extract it to: `C:\Users\Christopher\Desktop\studious-umbrella`.
3. Run:

```powershell
cd "C:\Users\Christopher\Desktop\studious-umbrella"
python .\it_workflow_agent.py triage --ticket-file .\examples\ticket.json
```

### Quick path sanity check

```powershell
Test-Path "C:\Users\Christopher\Desktop\studious-umbrella"
Test-Path "C:\Users\Christopher\Desktop\studious-umbrella\it_workflow_agent.py"
Test-Path "C:\Users\Christopher\Desktop\studious-umbrella\examples\ticket.json"
```

All three should return `True` before running the CLI.


## If `it_workflow_agent.py` is still not found

Your output indicates the folder exists but the script file is missing from that exact path.
This usually means the ZIP extracted into a nested directory like:

- `C:\Users\Christopher\Desktop\studious-umbrella\studious-umbrella\it_workflow_agent.py`
- or a branch suffix folder, e.g. `studious-umbrella-main`

Use this PowerShell search to locate the script:

```powershell
cd "C:\Users\Christopher\Desktop"
Get-ChildItem -Path . -Filter it_workflow_agent.py -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

Then `cd` into the parent directory shown and run:

```powershell
python .\it_workflow_agent.py triage --ticket-file .\examples\ticket.json
```

### No GitHub CLI required

You do **not** need `gh repo clone`.
The `HTTP 401` error is from unauthenticated GitHub CLI and can be ignored for now.
Use one of these instead:

```powershell
# Option 1: Standard Git (no gh needed)
git clone https://github.com/ChrisPowers1010/studious-umbrella.git

# Option 2: Download ZIP from browser and extract
```
