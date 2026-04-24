\# IT Workflow Agent



A practical command-line agent for day-to-day IT operations.



It helps you:

\- Triage and troubleshoot tickets quickly

\- Prioritize work based on impact and urgency

\- Build a focused daily execution plan

\- Proofread and improve internal/external communication notes

A Claude-powered IT help desk agent that connects AutoTask, ITGlue, Passportal, and Kaseya VSA into a single agentic workflow. When a ticket arrives, the agent autonomously gathers context from your documentation and credential systems, checks device status, documents its findings, replies to the client professionally, and updates the ticket — all without manual hand-offs.



---



\## Run location (important)



You must run commands \*\*inside the folder where this repo is downloaded\*\* (the folder containing `it\_workflow\_agent.py`).



> The path `/workspace/studious-umbrella` is for this hosted Linux environment only.

> On your Windows PC, use the path where \*you\* cloned or unzipped this project.



\### Windows PowerShell example



```powershell

\# 1) Go to the folder where this repo exists on your machine

cd "C:\\Users\\Christopher\\Desktop\\studious-umbrella"

\## Architecture



\# 2) Confirm files are present

Get-ChildItem



\# 3) Run the tool

python .\\it\_workflow\_agent.py --help

python .\\it\_workflow\_agent.py triage --ticket-file .\\examples\\ticket.json

```



\### If you don't have the repo folder yet



```powershell

cd "C:\\Users\\Christopher\\Desktop"

git clone <REPO\_URL> studious-umbrella

cd .\\studious-umbrella

python .\\it\_workflow\_agent.py --help

main.py  ──►  agent/orchestrator.py  ──►  Claude Opus 4.7 (tool-calling loop)

&nbsp;                                              │

&nbsp;                       ┌──────────────────────┼──────────────────────┐

&nbsp;                       ▼                      ▼                      ▼

&nbsp;             tools/handlers.py        tools/handlers.py       tools/handlers.py

&nbsp;                       │                      │                      │

&nbsp;             integrations/             integrations/          integrations/

&nbsp;             autotask.py               itglue.py              passportal.py

&nbsp;                                       vsa.py

```



\### macOS/Linux example



```bash

cd /path/to/studious-umbrella

python it\_workflow\_agent.py --help

```

\*\*Claude Opus 4.7\*\* drives the workflow with adaptive thinking and tool-calling. The system prompt is cached (prompt caching) to reduce API cost on every call. The agent runs a tool-calling loop — reading data, taking actions, and deciding what to do next — until the ticket is fully handled.



---



\## 1) How to utilize it (fast path)

\## Setup



\### 1. Prerequisites



\- Python 3.11+

\- An Anthropic API key

\- Credentials for AutoTask, ITGlue, Passportal, and/or Kaseya VSA



From the repository root:

\### 2. Install dependencies



```bash

python it\_workflow\_agent.py triage --ticket-file examples/ticket.json

python it\_workflow\_agent.py plan --tickets-file examples/tickets.json --max-items 6

python it\_workflow\_agent.py proofread --text "Please fix VPN ASAP!!!" --audience external

pip install -r requirements.txt

```



If you want to see all available commands/options:

\### 3. Configure credentials



```bash

python it\_workflow\_agent.py --help

python it\_workflow\_agent.py triage --help

python it\_workflow\_agent.py plan --help

python it\_workflow\_agent.py proofread --help

```

cp .env.example .env

\# Edit .env and fill in all required values

```



Required:

| Variable | Description |

|---|---|

| `ANTHROPIC\_API\_KEY` | Your Anthropic API key |

| `AUTOTASK\_USERNAME` | AutoTask API user email |

| `AUTOTASK\_INTEGRATION\_CODE` | AutoTask integration code (Admin → API) |

| `ITGLUE\_API\_KEY` | ITGlue API key |



Optional (enable for full functionality):

| Variable | Description |

|---|---|

| `ITGLUE\_BASE\_URL` | `https://api.itglue.com` (EU: `https://api.eu.itglue.com`) |

| `PASSPORTAL\_API\_KEY` | N-able Passportal API key |

| `PASSPORTAL\_BASE\_URL` | Passportal instance URL |

| `VSA\_BASE\_URL` | Kaseya VSA hostname |

| `VSA\_USERNAME` | VSA API username |

| `VSA\_PASSWORD` | VSA API password |

| `AUTOTASK\_ZONE\_URL` | Override AutoTask zone URL (auto-discovered by default) |

| `AUTOTASK\_QUEUE\_ID` | Default queue ID for batch processing |



---



\## 2) Typical daily workflow



\### Morning intake (triage new tickets)

1\. Export/prepare a ticket JSON file (or use your own).

2\. Run `triage`.

3\. Use the returned `priority\_level`, `recommended\_sla`, and `first\_30\_min\_actions` to start response.

\## Usage



Example:

\### Handle a specific ticket



```bash

python it\_workflow\_agent.py triage --ticket-file examples/ticket.json

python main.py ticket 98765

```



\### Prioritize your work block (plan)

1\. Put all active tickets into a JSON array.

2\. Run `plan` to get an ordered queue.

3\. Work top-down and send checkpoint updates at each timebox.

The agent will:

1\. Read ticket #98765 from AutoTask

2\. Look up the client in ITGlue

3\. Pull relevant configs, contacts, and documentation

4\. Check Passportal for credentials (if needed)

5\. Check VSA device status (if device-related)

6\. Add an internal note documenting findings

7\. Reply to the client professionally

8\. Update the ticket status



Example:

\### Process a batch of new tickets



