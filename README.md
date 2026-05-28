# CareerScout

A Claude Code agent for your job search. Paste your resume once — it finds roles, scores fit, tailors your resume, writes cover letters, and tracks applications.

You don't need to memorise commands. Paste a job description and it runs `/assess`. Paste recruiter feedback and it files it. Mention an outcome ("got rejected", "interview tomorrow") and it logs it and tells you what to do next. Type `/help` any time for a command reference.

---

## How it works

Two loops: the **feed** finds roles worth applying to, the **application loop** helps you apply well.

### Feed loop

`fetch.py` runs daily (or manually) and scrapes LinkedIn, Indeed, and direct ATS boards for roles matching your criteria. It filters by title, level, location, and your avoid list — then saves the results to `today.json`. Run `/feed` in Claude Code to score and rank them against your profile, producing a shortlist in `feed.md`. React to the results with `/calibrate` and the feed gets sharper over time.

| Command | What it does |
|---------|--------------|
| `/feed` | Score today's fetched roles and write the shortlist |
| `/calibrate` | Tune scoring from your feed reactions — updates sources.md, differentiators.md, and learnings.md |
| `/feed reject` | Log a role rejection |
| `/feed add` | Manually add a role to the feed |
| `/retro` | Periodic review — rejection patterns, pipeline health |

> The first few feeds will need calibration. Run `/calibrate` after each early run until the signal feels right — usually 3-5 runs.

### Application loop

Paste a job description and `/assess` gives you a fit verdict, ranked recruiter concerns, and a cover letter angle. From there, `/tailor-resume` adjusts your resume bullets for the role and `/cover-letter` writes the letter in your voice. Every outcome — interview, rejection, offer — gets logged to your pipeline so nothing falls through.

| Command | What it does |
|---------|--------------|
| `/improve-resume` | Review and strengthen your master resume _(untested — use with caution)_ |
| `/assess` | Fit verdict, recruiter concerns, and Mnookin fit — feedback updates bank.md, profile.md, and differentiators.md |
| `/tailor-resume` | Tailor your resume to the JD |
| `/cover-letter` | Write a cover letter in your voice |
| `/notes` | Capture recruiter feedback or call notes |
| `/update` | Log an event — interview, rejection, offer |
| `/track` | View and manage your full pipeline |

---

## Setup

**Prerequisites:** [Claude Code](https://claude.ai/code) installed. Python 3.x only needed for the job feed.

### 1. Clone and open

```bash
git clone https://github.com/a-n-jelly/careerscout.git
cd career-coach
```

Open Claude Code in this directory.

### 2. Run `/setup`

Type `/setup` in Claude Code. It walks you through everything in one flow:

- Saves your resume
- Creates your context files from templates
- Calibrates your writing voice (optional)
- Configures the job feed (optional)

Each step can be skipped and done later.

---

## Context files

The agent reads `context/` at session start — you don't re-explain your background each time.

| File | What it is | Auto-updated? |
|------|------------|---------------|
| `resume.md` | Master resume | No |
| `profile.md` | Off-resume context, Mnookin preferences | Yes — by `/feed-setup` (Mnookin doc), `/assess` (Mnookin calibration) |
| `bank.md` | Cover letter style, talking points, Q&A, assess calibration | Yes — by `/voice-setup`, `/assess`, `/tailor-resume` |
| `state.md` | Live application pipeline | Yes |
| `sources.md` | Feed criteria: roles, locations, comp, deal-breakers | Yes — by `/calibrate` |
| `differentiators.md` | Your edges and hard gaps — used in feed scoring | Yes — by `/assess` and `/calibrate` |

---

## Contributing

See `CLAUDE.md` for the full agent instructions and file index.
