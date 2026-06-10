# /feed-setup — Job Feed Calibration

Builds `context/sources.md` by reading the user's resume first, drafting a spec from it, then filling in the gaps through targeted questions.

---

## When to use

Run once before using `/feed` for the first time. Takes 10-15 minutes. The result is a complete `sources.md` that the feed agent uses to find and score roles.

---

## Protocol

### Step 1 — Read the resume

Read `context/resume.md`. If it doesn't exist, stop and say:

> "I need your resume before I can set up the feed. Go back to setup step 1 — paste your resume into Claude Code and ask me to save it to `context/resume.md`."

### Step 2 — Draft the spec

From the resume, infer:

- **Titles**: what roles they've held and what logical next titles would be
- **Seniority**: current level and whether they're looking to stay level, step up, or are open to both
- **Domains**: industries and product areas they have experience in
- **Location**: where they're based (if listed)
- **Work authorisation**: whether they require sponsorship (if listed)

Also draft **5–8 search queries** directly from these inferences. Queries should combine title + domain/keyword + location signal. Examples:
- "Senior Product Manager fintech Seattle"
- "Senior PM payments remote"
- "Senior Product Manager consumer lending Seattle"

Also draft a **Domain Preferences** section with four buckets inferred from the resume:

- **Proven**: industries and product types the resume demonstrates clearly — where they'll clear screening
- **Adjacent**: industries where their skills plausibly transfer but the resume doesn't prove it yet
- **Curious**: leave blank — you can't infer interest from a resume. Ask the user to fill this in.
- **Hard no**: leave blank — ask the user.

Show the draft to the user. Say:

> "Here's what I pulled from your resume — including a first set of search queries and a domain map for scoring. The Proven and Adjacent buckets are inferred from your background. Two quick questions before we continue: anything in the Curious column — domains you'd explore even without a track record? And any hard no's — things you'd never consider regardless of comp or company?"

Wait for their answers. Apply to the Domain Preferences draft. The user can add, remove, or move items between buckets freely.

### Step 3 — Fill in the gaps with structured questions

Use the **AskUserQuestion tool** for each group below. Send each group as a single tool call — don't ask one question at a time.

---

**Group 1 — Location**

Ask:
- "Where are you based, and what's your work setup preference?" — Options: Fully remote / Hybrid (few days/week) / Open to on-site / Flexible
- "Are you open to relocating for the right role?" — Options: Yes / No / Possibly

If hybrid or on-site: follow up with a single free-text question asking maximum commute distance or time.

If remote or hybrid: follow up with a single free-text question: "Any cities or states to exclude from remote results? (e.g. you wouldn't consider roles based in New York or Chicago)" — leave blank to skip.

---

**Group 2 — Employment & authorisation**

Ask (skip visa question if already confirmed from resume):
- "What type of work are you looking for?" — Options: Full-time only / Open to contract / Open to fractional / Any
- "Do you require visa sponsorship?" — Options: Yes, required / No, not required

---

**Group 3 — Compensation**

Ask:
- "What's your base salary floor — the minimum you'd accept?" — Options: Under $100k / $100k–$130k / $130k–$160k / $160k–$200k / $200k+ / Other
- "What's your target base?" — same options
- "Any comp structure preferences?" — Options: Base-heavy / Equity-heavy / Balanced / No preference
- "Any benefits that are must-haves?" — multiSelect: Health coverage / 401k match / Parental leave / Generous PTO / Visa sponsorship / None / Other

---

**Group 4 — Companies & targeting**

Ask:
- "Any stage or size preference?" — Options: Early stage / Growth / Public / No preference
- "Are you actively looking or passively exploring?" — Options: Actively looking / Passively exploring

Then ask two free-text follow-ups (separately, not bundled):
1. "Any specific companies you want to watch directly? List them and I'll add them to your priority list."
2. "Any deal-breakers — role types, domains, or company types to exclude entirely?" Add these to the Hard no bucket in Domain Preferences and to the What to Avoid section.

---

**Group 5 — Feed settings**

Ask:
- "How many results per feed run?" — Options: 10 / 25 (recommended) / 50
- "How fresh should roles be?" — Options: Last 24 hours / Last 48 hours / Last 72 hours (recommended) / Last week

---

**Group 6 — Mnookin doc (optional)**

Use the AskUserQuestion tool:
- "Do you have a Mnookin doc — a personal preferences doc that captures the kind of company, culture, and working environment you thrive in?" — Options: **Yes, I'll paste it** / **No, skip this**

If yes: ask them to paste it. Once received:
- Save it to `context/profile.md` under a `## Mnookin Doc` section
- Do not use it to change search queries or differentiators — it's about personal fit, not positioning
- Explain: "This will be used by `/assess` to flag whether a company looks Mnookin-friendly — i.e. whether the role and company style match your preferences. It won't change what gets surfaced in the feed, but it'll add a fit signal when you're evaluating specific roles."

If no: proceed without it. Users can add it later by pasting into Claude Code and asking to save it to `context/profile.md`.

### Step 3b — Draft differentiators.md

From `resume.md` and the Mnookin doc (if provided), extract:

1. **Key edges** — what this candidate has that most candidates don't. Look for: scale signals, cross-functional complexity, ownership depth, domain intersections, unusual credentials. Write 3–4 bullets, each with a "why it matters" clause.
2. **Target level** — infer from their most recent title and trajectory
3. **Positioning summary** — one paragraph: who they are, what makes them a distinct candidate, what they're targeting
4. **Notes for scoring** — explicit Edge triggers for the feed to use when scoring. Generate two lists:
   - `Edge = 3 if the role involves any of:` — 3–5 specific product types, named partners, domains, or scale signals from the candidate's background
   - `Edge = 1 or below if the role is primarily:` — 2–4 known thin-transfer areas or hard gap domains

Show the draft to the user:

> "Here's your differentiators profile — this is what `/feed` will use to score the Edge dimension. Does this reflect how you'd position yourself? The 'Notes for scoring' section is the trigger list the feed reads directly — the more specific it is, the more consistent your Edge scores will be."

Wait for confirmation or edits. Apply changes. Write to `context/differentiators.md`.

The differentiators.md file should include these sections in order: `## Key edges`, `## Target level`, `## Positioning summary`, `## Notes for scoring`, `## Hard gaps`.

### Step 3c — Capture hard gaps

Ask:

> "Are there any domains, technical areas, or role types where you know you don't have the experience — things that would come up as gaps if you got to an interview loop?"

Accept any answer. Examples: "I've never worked on payment rails infrastructure", "I don't have ML/recommendation systems experience", "I've never managed external developer APIs."

From the answer, write a `## Hard gaps` section to `context/differentiators.md`:

```markdown
## Hard gaps — drop Requirements to 1 if JD requires any of these

- [gap 1 — stated plainly, with the JD signal that would trigger it]
- [gap 2]
...

_This section is auto-updated by `/assess` when structural gaps are identified._
```

If the user says "none" or "I'm not sure", write the section header with a comment:

```markdown
## Hard gaps — drop Requirements to 1 if JD requires any of these

<!-- None identified at setup. Will be populated by /assess and /calibrate over time. -->

_This section is auto-updated by `/assess` when structural gaps are identified._
```

Explain briefly:

> "These are used to automatically flag roles where you'd hit a wall at interview — so the feed surfaces them as lower-scoring rather than hiding them entirely."

---

### Step 4 — Write sources.md

Incorporate all answers into `context/sources.md`. The sections below must use these exact headings — fetch.py parses them directly.

```markdown
> **Purpose:** Your search criteria for the daily job feed. fetch.py reads this file to know what to fetch, filter, and score.

# Job Feed — Search Criteria

---

## Search Queries (run these)

[Confirmed queries from Step 2 — one per line]
1. [query]
2. [query]

---

## Feed Settings

results_wanted: [from Q15]
hours_old: [from Q16]

---

## Target Titles

[Title keywords a role must contain — any match accepts it]
- product manager
- pm
[add others based on role targets, e.g. "head of product" if above-target is in scope]

---

## Target Level

[Derived from seniority discussion in Step 2 and Q answers]
**Target:** [e.g. senior, sr, staff, lead, principal]
**Above target:** [e.g. director, vp, head of, vice president, chief]
**Below target:** [e.g. associate, junior, jr, entry level]

---

## Location

**Primary city:** [from Q1, e.g. Seattle, WA — or leave blank if fully remote]
**Accept remote:** [yes / no — from Q1]
**Reject if clearly located in:** [from Q4, comma-separated, or leave blank]

---

## Priority Companies

[From Q11 — companies worth watching directly]

| Company | Why |
|---------|-----|
| [Company] | [reason] |

---

## ATS Endpoints

[Add manually if company uses a supported ATS — Greenhouse, Lever, or Ashby]

| Company | Type | Slug |
|---------|------|------|

---

## Domain Preferences

[From resume inference + user answers in Step 2 — defines the Match dimension. Feed maps these to scores internally.]

**Proven** — domains the resume positions them strongly in:
- [inferred from resume]

**Adjacent** — skills transfer, less proven:
- [inferred from resume]

**Curious** — open to exploring, no strong background:
- [from user input — leave blank if none provided]

**Hard no** — never, regardless of comp or company:
- [from user input — leave blank if none provided]

---

## What to Avoid

[From Q13 — deal-breakers. Use AND: prefix for multi-keyword rules]
- [rule]
- AND: [word1] [word2]

---

## Context (not parsed by fetch.py)

### Employment Type
[from Q4]

### Work Authorisation
[from Q5]

### Compensation
Floor: [from Q6]
Target: [from Q7]
Reach: [from Q8]
Structure: [from Q9]
Benefits: [from Q10]

### Company Preferences
[from Q12 — stage, size, culture]

### Timeline
[from Q14]

### Scoring Documents
[paths or inline content for Mnookin / CMF if provided]
```

After writing `context/sources.md`, **delete `context/sources.example.md`** — it's no longer needed.

### Step 4b — Generate my_filters.json

Create `feed-agent/my_filters.json` from what you now know about the user. This file controls the fast pre-filter that runs before Claude scores anything — it removes clearly out-of-scope roles by title pattern, location, and company.

Generate four sections. All text matching is **plain case-insensitive substring** — no regex. Commas and hyphens are ignored when matching, so `"pm infrastructure"` also matches "PM, Infrastructure" and "PM – Infrastructure".

1. **`non_role_patterns`** — plain strings that identify the wrong role type for this user. For a PM searcher, this means software engineers, recruiters, data scientists, interns, etc. For an engineering manager, it means PM roles. Infer from the user's target role. Each entry is just a string, e.g. `"software engineer"`, `"data scientist"`, `"recruiter"`.

2. **`hard_no_title_patterns`** — the "Hard no" domains from Step 2 (Domain Preferences), converted to plain-text entries. Each entry needs `"text"` and `"reason"`. Example: if "fraud" is a hard no, add `{"text": "fraud", "reason": "fraud domain"}`. Use the most specific phrase that captures the pattern without over-filtering — prefer `"infrastructure pm"` over `"infrastructure"`.

3. **`skip_companies`** — start empty `[]`. The user hasn't seen any feeds yet, so there are no known-bad companies. `/calibrate` will populate this over time.

4. **`exclude_locations`** — plain location strings to exclude. Derive from the user's location config:
   - If US-only (primary city in the US, accept remote = yes): add standard international exclusions (e.g. `"united kingdom"`, `"london"`, `"canada"`, `"ireland"`, `"emea"`, `"australia"`, `"singapore"`)
   - If UK-only: add US states, APAC, etc.
   - If open to international: leave empty `[]`

Show the generated file to the user:

> "I've created your personal filter rules at `feed-agent/my_filters.json`. This file is gitignored — it lives on your machine only. It removes clearly out-of-scope roles before Claude scores them, so the feed focuses on viable candidates. `/calibrate` will add to it as you react to roles over time."

Use `feed-agent/my_filters.example.json` as a reference for the file format, then **delete it** — it's no longer needed once `my_filters.json` exists.

### Step 5 — First fetch

Tell the user:

> "Feed configured. Run these three commands now to fetch, filter, and enrich today's roles — then come back and run `/feed` to score them:"

```bash
python3 feed-agent/fetch.py && python3 feed-agent/filter_roles.py && python3 feed-agent/enrich.py
```

Explain briefly:
- `fetch.py` scrapes the job boards and writes raw results
- `filter_roles.py` removes out-of-scope roles using your personal rules from `my_filters.json`
- `enrich.py` fetches full job descriptions for roles that need them

Wait for them to confirm all three ran before moving on. If any step fails, help them debug before continuing.

### Step 6 — Set up the daily scheduler

Ask:

> "Want to schedule fetch.py to run automatically each morning at 8am? It takes about a minute to set up — you'd wake up to fresh roles every day without having to run the script manually."

If yes, first detect the OS by running `uname -s`. Then follow the appropriate path below.

---

#### macOS (`uname -s` returns `Darwin`)

1. Ask the user what time they want the feed to run:

> "The feed runs at **8am by default**. On macOS, if your Mac is asleep at that time it'll run automatically when you wake it — so you'll always get fresh roles, just maybe a bit later. Want to keep 8am or set a different time?"

Accept any hour (e.g. "7am", "9", "7:30"). Default to 8:00 if they say yes/keep/default. Parse to Hour and Minute integers for the plist.

2. Make the run script executable:

```bash
chmod +x feed-agent/run-daily.sh
```

3. Set up your local config. Run `which claude` to find your claude binary path, then:

```bash
cp feed-agent/config.sh.template feed-agent/config.sh
```

Open `feed-agent/config.sh` and set `CLAUDE_BIN` to the path from `which claude`. This file is gitignored — it stays on your machine only.

4. Get the username: `whoami`. Create `~/Library/LaunchAgents/com.careercoachai.feed.plist` using the Hour and Minute from step 1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.careercoachai.feed</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/[username]/CareerScout/feed-agent/run-daily.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/[username]/CareerScout/feed-agent/run.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/[username]/CareerScout/feed-agent/run.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

5. Load it: `launchctl load ~/Library/LaunchAgents/com.careercoachai.feed.plist`

6. **Grant Full Disk Access to bash** — required for launchd to read/write files in ~/Documents. Do this *before* the first scheduled run, or the feed will silently fail:
   - Open **System Settings → Privacy & Security → Full Disk Access**
   - Click **+**, then press **⌘⇧G**, type `/bin/bash`, and click Open
   - You'll see bash added to the list — toggle it on if it isn't already

   > **What to expect:** When the scheduler first runs, macOS may still show a dialog saying "bash wants to access files in your Documents folder." That's normal — click **Allow**. It's the job feed scheduler, not anything suspicious.

7. Confirm: `launchctl list | grep careercoachai` — should show the job listed.

> The scheduler fires at [chosen time] daily. If your Mac is asleep at that time, it runs automatically when you wake it — no manual trigger needed.

---

#### Linux (`uname -s` returns `Linux`)

Ask the user what time they want the feed to run (default 8am). Note:

> "On Linux, cron runs at the exact scheduled time only — if your machine is off or sleeping at that time, the run is skipped (unlike macOS, which catches up on wake)."

1. Check if `feed-agent/run-daily.sh` exists. If not, create it (same content as macOS above but remove the `osascript` trap line — it won't work on Linux).

Make it executable: `chmod +x feed-agent/run-daily.sh`

2. Open the crontab editor: `crontab -e`

3. Add this line using the chosen hour/minute (replacing the path with the actual absolute path):

```
[MINUTE] [HOUR] * * * /bin/bash /home/[username]/Documents/Claude/agents/career-coach/feed-agent/run-daily.sh
```

4. Save and exit. Confirm: `crontab -l` — should show the entry.

---

#### Windows

1. Check if `feed-agent/run-daily.ps1` exists. If not, create it:

```powershell
$AgentDir = Split-Path -Parent $PSScriptRoot
$Python = "$AgentDir\feed-agent\.venv\Scripts\python.exe"
$Log = "$AgentDir\feed-agent\run.log"
Add-Content $Log "--- $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ---"
& $Python "$AgentDir\feed-agent\fetch.py" >> $Log 2>&1
Add-Content $Log "Done."
```

2. Open Task Scheduler and create a new basic task:
   - **Trigger**: Daily at 8:00 AM
   - **Action**: Start a program
   - **Program**: `powershell.exe`
   - **Arguments**: `-ExecutionPolicy Bypass -File "C:\Users\[username]\Documents\Claude\agents\career-coach\feed-agent\run-daily.ps1"`

3. Or via command line (run as Administrator):

```cmd
schtasks /create /tn "JobFeedFetch" /tr "powershell.exe -ExecutionPolicy Bypass -File \"C:\Users\[username]\Documents\Claude\agents\career-coach\feed-agent\run-daily.ps1\"" /sc daily /st 08:00
```

4. Confirm: `schtasks /query /tn "JobFeedFetch"`

---

If no or skipped, tell them:

> "No problem — just run `python3 feed-agent/fetch.py` manually each morning before opening Claude Code. You can set up the scheduler any time by asking me."

### Step 7 — Confirm and set expectations

Say:

> "All set. Here's what to expect:
> - fetch.py runs at 8am daily (or manually with `python3 feed-agent/fetch.py`)
> - Open Claude Code and run `/feed` to score the results
> - After your first few feeds, run `/calibrate` — the first runs will have noise that calibration clears up
> - Run `/retro` every 2-3 weeks to review pipeline health and refine positioning"
