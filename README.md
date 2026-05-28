# CareerScout

A Claude Code agent that manages your job search end-to-end. Paste your resume once — it handles fit assessment, resume tailoring, cover letters, application tracking, and a daily job feed.

---

## How it works

CareerScout has two loops: the feed loop surfaces roles worth applying to, and the application loop helps you apply for them well.

### Feed loop

The feed finds and scores roles daily so you're not manually searching job boards.

```mermaid
flowchart LR
    A[fetch.py\nruns daily at 8am] -->|scrapes LinkedIn\nIndeed, ATS endpoints| B[today.json\nfiltered roles]
    B --> C[/feed\nscores each role]
    C -->|Recommended\nStretch\nSkipped| D[feed.md\nyour shortlist]
    D --> E{your reaction}
    E -->|felt off| F[/calibrate]
    E -->|worth applying| G[application loop]
    F -->|updates| H[(sources.md\nlearnings.md\ndifferentiators.md)]
    H -->|read on next run| A
```

**fetch.py** scrapes LinkedIn, Indeed, Glassdoor, and direct ATS endpoints (Greenhouse, Lever, Ashby). It filters out staffing agencies, wrong locations, and roles matching your avoid list. Results go to `feed-agent/today.json`.

**`/feed`** reads today.json and scores each role on four dimensions (0–3 each, 0–12 total):
   - **Match** — is this the right domain?
   - **Requirements** — do you meet the stated requirements?
   - **Edge** — do your differentiators give you a specific advantage?
   - **Sustain** — does the comp and location work?

Roles above the threshold go into Recommended or Stretch. Everything else is explained in a collapsed Skipped section. Results are written to `feed/feed.md`.

**`/calibrate`** turns your reaction to the feed into config changes. After each run, it asks what felt off — wrong domain, level too high, requirements you don't have — and updates the right files so the next run is cleaner.

**Expect the first few feeds to need calibration.** The feed starts from your resume and a set of reasonable defaults, but every job search is different. It takes a few runs of feedback with Claude — flagging roles that felt wrong, confirming hard gaps, adjusting the avoid list — before the feed reliably surfaces roles that match your specific situation. This is normal and expected. Run `/calibrate` after each of your first few feeds; once the signal stabilises, you'll rarely need to.

The feed gets better over time. Roles you've already seen won't resurface. Patterns you reject get written to the avoid list. Hard gaps you identify get flagged automatically in future scoring.

| Command | What it does |
|---------|--------------|
| `/feed` | Score today's fetched roles and write the shortlist |
| `/calibrate` | Tune scoring, avoid list, and edge profile from your feed reactions |
| `/feed reject` | Log a specific role rejection and route the signal to the right file |
| `/feed add` | Manually inject a role you found into the feed |
| `/retro` | Periodic pipeline review — staleness sweep, rejection patterns, hypotheses |

---

### Application loop

Once you have roles worth pursuing, the application loop takes over.

```mermaid
flowchart LR
    A[feed.md\nshortlist] -->|pick a role| B[/assess\nfit verdict + concerns]
    Z[paste a JD] --> B
    B --> C[/tailor\nresume bullets]
    C --> D[/coverletter\nin your voice]
    D --> E[apply]
    E --> F{outcome}
    F -->|interview| G[/concerns\nprep + drill]
    G --> H[/update\nlog the event]
    F -->|rejection| H
    F -->|offer| H
    H --> I[/track\npipeline view]
```

| Command | What it does |
|---------|--------------|
| `/assess` | Fit verdict, dimension scores, recruiter concerns ranked by severity |
| `/tailor` | Tailor your resume summary and bullets to the JD |
| `/coverletter` | Write a cover letter in your voice |
| `/concerns` | Anticipate recruiter concerns with counter-framings and a drill offer |
| `/notes` | Capture recruiter feedback or call notes against an application |
| `/update` | Log an event — interview, rejection, offer — and get a suggested next step |
| `/track` | View and manage your full application pipeline |

The agent keeps state between sessions. It reads `context/state.md` at the start of each session and picks up where you left off.

---

## How context works

Everything lives in `context/`. The agent reads these at the start of sessions — you don't need to re-explain your background each time.

| File | What it is | Auto-updated? |
|------|------------|---------------|
| `resume.md` | Master resume — source of truth for all tailoring | No |
| `profile.md` | Off-resume context: positioning, stories, gaps, comp targets | Yes |
| `bank.md` | Cover letter style, talking points, Q&A | Yes |
| `state.md` | Live application pipeline | Yes — every session |
| `sources.md` | Feed search criteria: roles, locations, comp, deal-breakers, target companies | Yes — by `/calibrate` |
| `differentiators.md` | Your key edges and hard gaps — used to score Edge dimension in the feed | Yes — by `/assess` and `/calibrate` |

Copy the `*.example.md` files to get started. Each one has a purpose header.

---

## Feed files

| File | What it is |
|------|------------|
| `feed-agent/fetch.py` | Scrapes job boards and ATS endpoints, writes today.json |
| `feed-agent/today.json` | Roles fetched today — input to `/feed` |
| `feed-agent/seen.json` | All role IDs ever fetched — prevents re-surfacing old roles |
| `feed-agent/dismissed.json` | Role IDs you've seen in the feed — won't resurface until re-posted |
| `feed-agent/learnings.md` | Rejected patterns and injected roles — read by fetch.py on every run |
| `feed/feed.md` | Latest scored feed output |
| `feed/archive/` | Previous feed runs saved by date |

---

## Setup

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.x (for the job feed only — all other commands work without it)

### 1. Clone and run setup

```bash
git clone <repo>
cd career-coach
bash setup.sh
```

This creates the `.claude/commands` and `.claude/skills` symlinks that Claude Code needs to recognise the slash commands. Run it once after cloning.

### 2. Add your resume

Paste your resume into Claude Code. The agent will save it to `context/resume.md` — this is the foundation for everything.

### 3. Set up your context files

```bash
cp context/profile.example.md context/profile.md
cp context/bank.example.md context/bank.md
cp context/state.example.md context/state.md
cp context/sources.example.md context/sources.md
cp context/differentiators.example.md context/differentiators.md
```

### 4. Calibrate your writing voice

Run `/voice-setup` in Claude Code. Paste 3-5 pieces of your own writing — emails, messages, anything that sounds like you. The agent drafts your voice profile from them. Takes 5-10 minutes and makes every written output significantly more accurate.

### 5. Set up the job feed (optional)

```bash
cd feed-agent
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install python-jobspy certifi
```

Then run `/feed-setup` in Claude Code. It reads your resume, drafts your search criteria, asks targeted questions about comp and deal-breakers, and optionally sets up a daily scheduler so today.json is fresh every morning.

### 6. Start using it

Paste a job description to run `/assess`, or run `python3 feed-agent/fetch.py` followed by `/feed` to get your first scored feed.

---

## The feedback loop

CareerScout gets better as you use it. Here's how:

- **`/assess`** identifies structural gaps (requirements you genuinely don't have) and asks whether to add them to `differentiators.md`. Once added, they auto-flag in future feed scoring.
- **`/calibrate`** turns feed reactions into config changes — avoid patterns, hard gaps, edge scoring adjustments. Run it after any feed that felt off.
- **`/retro`** spots rejection patterns across the pipeline and writes testable hypotheses to `feed-agent/learnings.md`. Run it every 2-3 weeks.
- **`/feed reject`** logs a specific role rejection with a signal tag and routes it to the right file automatically.

The goal is a feed that's accurate enough you don't need to calibrate it — just scan, pick, and apply.

---

## Contributing

See `CLAUDE.md` for the full agent instructions and file index.
