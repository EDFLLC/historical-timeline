# Historical Timeline Website — Build Guide

Version 1.4 · October 2026 · For a coding novice using Claude Cowork, Cursor, and GitHub

> **What's new in v1.4:** Zoom density is now *adaptive per lane*. Instead of fixed importance thresholds per zoom level, each lane shows the lowest importance tier that keeps its dots in the current view at or below a cap (6 dots fully zoomed out, rising smoothly to 14 at ~20 years or less). Search-jump targets are always shown. See "How zoom works".

> **What's new in v1.3:** (1) Data now lives in its own file, `data/events.json`, loaded by `index.html` at startup — the code file no longer grows as you add events. (2) The top-tier (importance-5) events now show even when fully zoomed out, so the timeline is never empty on load. (3) Added label collision-skipping: a dot is always drawn, but its text label appears only when there's room, so no two labels overlap at any zoom level. See Part 2 (data location and loading) and Part 2's zoom section.
>
> **What's new in v1.2:** Categories revised to nine swimlanes (added Religion & Belief; renamed Geography to Exploration & Discovery). Added an optional `tags` field to the data schema so fine-grained topics (specific sports, religions, "AI", "space", wars, etc.) are searchable and filterable *without* creating more lanes. Search now matches tags as well as summaries. See the Appendix and Part 2 for the updated schema and category list.

---

## Part 1 — Analysis of Your Concept

### What is strong

Your spec is unusually precise for a first concept: exact hex codes, defined categories, a clear zoom hierarchy, and a hard 40-character limit on summaries. That precision makes the site buildable and keeps the design honest. The two-color scheme (pure black/white on black or cream) is a proven editorial aesthetic and costs nothing to implement. The concept also fits a **static website** — no server, no database, no login — which means it can be hosted free on GitHub Pages and built by one person.

### Where your assumptions need pressure-testing

**1. Data curation is the real project — not the code.**
The code for this site is perhaps 1,500 lines. The dataset is the hard part. Wikipedia does not organize events into your nine categories, and its summaries are never 40 characters. Every event needs a human (or Claude-assisted) pass to: verify the date, assign one category, add a few tags, and write a compliant summary. Budget your time accordingly: roughly 20% code, 80% data. This is why the curated-JSON approach you chose is right — but go in with eyes open.

**2. "More events appear as you zoom" requires a ranking you haven't specified.**
For the timeline to reveal events progressively, every event needs an **importance score** (e.g., 1–5). Fully zoomed to months → show only importance 5; zoom to days → show 4–5; deepest zoom → show all. Without this field, the feature is unbuildable. It has been added to the data schema below. Assigning importance is subjective — decide your rubric early (e.g., 5 = changed world history; 1 = notable trivia).

**3. Label collision is your hardest UI problem.**
Dots on a line are easy. Forty-character labels connected by thin lines are not: at month zoom, dozens of labels compete for the same pixels. The prototype mitigates this with category swimlanes (each category gets its own parallel lane, so categories never collide with each other), alternating label placement within each lane, and the importance filter thinning the field as you zoom out. Expect to iterate on this more than anything else.

**4. Nine categories × one B/W color is a legibility risk.**
You specified monochrome, so category cannot be encoded by color. The swimlane layout largely solves this: each category lives on its own labeled lane (draggable to reorder), so position identifies category without color. The side-panel filters and tooltips reinforce it. If lanes ever feel insufficient, distinct dot shapes per category remain an option that preserves the aesthetic.

**5. Wikipedia licensing.**
Wikipedia text is CC BY-SA 4.0. Your 40-character summaries are your own writing (facts are not copyrightable), but if you copy phrasing or link out, attribution is good practice. The prototype already includes a site footer — "Some source material from Wikipedia, CC BY-SA 4.0." — with links to Wikipedia and the license. Keep it.

**6. Scope discipline for v1.**
You chose 1900–present: correct. 126 years × day-level zoom is already ~46,000 day positions. Start the dataset at ~150–300 events (one or two per year, spread across categories), get the interactions right, then grow the data. Do not attempt "every day has events" in v1.

### Requirements decisions made for you (change if you disagree)

Dates are stored as YYYY.MM.DD and displayed as YYYY.MMM.DD (e.g., 1969.JUL.20) for legibility. Events sharing a date within the same category share one dot; its tooltip lists all events at that date. Zoom is driven by the primary mouse wheel / pinch, +/− buttons, and ⌘↑/⌘↓ (Ctrl on Windows); the secondary (tilt) wheel and arrow keys traverse. The year→month→day thresholds are based on pixels-per-day, so they feel the same in horizontal and vertical modes. The theme, orientation, direction, lane order, and filter choices persist while the page is open (no accounts, no cookies in v1).

---

## Part 2 — Architecture (what you are building)

A **static site**: three files, no backend.

```
timeline-website/
├── index.html      ← page structure, controls, side panel
├── (styles inline or style.css)
├── (logic inline or app.js)
└── data/
    └── events.json ← your curated dataset (the crown jewel)
```

The prototype keeps all the **code** in `index.html` and all the **data** in `data/events.json`. `index.html` loads that JSON at startup, so the code file stays a fixed size and only the data file grows as you add events. This separation is the whole point: you edit data without ever touching code.

**Important consequence — local preview.** Because the page now *fetches* a separate file, double-clicking `index.html` straight from your hard drive will show an on-screen "couldn't load data" message: browsers block a local file from fetching another local file for security reasons. Two ways to preview: view your live GitHub Pages URL (a real web server, works normally), or ask Cursor to "start a local preview server for this folder" and open the address it gives you. This only affects local double-clicking; the live site is unaffected.

If you later want to tidy the code itself, you can ask Cursor to split `index.html` into `index.html` / `style.css` / `app.js` — a five-minute, zero-risk refactor — but it's optional and separate from the data split, which is already done.

### The data schema (memorize this)

Every event in `events.json` looks like:

```json
{
  "date": "1969.07.20",
  "category": "science",
  "importance": 5,
  "tags": ["space", "nasa"],
  "summary": "Apollo 11 lands humans on the Moon",
  "source": "https://en.wikipedia.org/wiki/Apollo_11"
}
```

Rules: `date` is YYYY.MM.DD; `category` is exactly one of the nine keys `history`, `politics`, `religion`, `science`, `tech`, `arts`, `pop`, `sport`, `exploration` (full names in the Appendix) — this is what places the event on its swimlane; `importance` is 1–5 (5 = shown first when zooming in); `tags` is an optional list of lowercase keywords (see below); `summary` is ≤ 40 characters — count them; `source` is the Wikipedia URL you verified against.

**About `tags` (the key to staying simple but searchable).** Each event sits on exactly one swimlane (its `category`). Everything finer-grained lives in `tags` instead of becoming its own lane: a specific sport (`football`, `olympics`), a specific religion (`christianity`, `islam`), a sub-field (`ai`, `physics`, `space`), an event type (`war`, `disaster`, `assassination`, `birth`, `death`), or a theme (`cold-war`, `economics`). Tags are searchable and don't clutter the layout, so you can be as granular as you like without adding lanes. Keep them lowercase and hyphenated (`cold-war`, `natural-disaster`); reuse existing tags rather than inventing near-duplicates (`film` not `films`/`movie`). Tags are optional, but a couple per event makes search far more useful.

### How zoom works (so you can direct Cursor intelligently)

The timeline tracks one number: **pixels per day (ppd)**.

- ppd < ~0.15 → year mode: year gridlines/labels
- ppd ~0.15–2 → month mode: month labels appear
- ppd > ~2 → day mode: day labels appear

*Which events appear* is independent of these label modes. Each lane runs `laneThreshold()`: it counts the lane's events in the visible window (±60 days) and picks the lowest importance tier whose cumulative count stays within a cap. The cap = clamp(round(300 / spanYears + 4), 6, 14), so it grows smoothly as you zoom in. A search-jump target is always shown regardless of tier.

Zooming multiplies ppd; panning shifts the visible date window. Only events inside the visible window are drawn (this keeps it fast). Every zoom bug you ever report to Cursor will be about the lane cap or the visible-window math — knowing these two concepts lets you describe bugs precisely.

**Dots vs. labels.** Two separate rules govern what you see. *Which events qualify* is set by importance and zoom (above). *Whether a qualifying event also gets a text label* is decided per lane by available space: the dot is always drawn, but the 40-char label appears only if it doesn't overlap the previous label in that lane. So a crowded lane shows mostly dots (hover for the tooltip), and labels fill in as you zoom and space opens up. If the zoomed-out view ever feels too busy or too bare, these are the two knobs to ask Cursor to adjust: the per-lane dot cap (`LANE_CAP` and the cap formula), and the minimum spacing between labels.

---

## Part 3 — Tool Roles (who does what)

| Tool | Role | You use it to… |
|---|---|---|
| **Claude Cowork** | Researcher & data factory | Generate and verify batches of events.json entries from Wikipedia; write the 40-char summaries; draft new feature specs before you take them to Cursor |
| **Cursor** | Builder | Edit the actual code files; add features; fix bugs — by chatting in plain English |
| **GitHub** | Safety net & publisher | Version history (undo anything), and free hosting via GitHub Pages |

Workflow for every change, forever: **describe in Cursor → test in browser → commit to GitHub**. Data batches: **generate in Cowork → paste into events.json via Cursor → test → commit**.

---

## Part 4 — Step-by-Step Build Instructions

### Stage 0 — Accounts and installs (once, ~30 min)

1. Create a free account at **github.com**. Choose a username you don't mind being public.
2. Download and install **Cursor** from cursor.com (free tier is fine to start).
3. Download and install **Git**: git-scm.com → Downloads → your OS → accept all default options in the installer.
4. Download and install **GitHub Desktop** from desktop.github.com and sign in with your GitHub account. (This gives you buttons instead of terminal commands — recommended for a novice.)

### Stage 1 — Create the project on GitHub (~10 min)

1. On github.com, click the **+** (top right) → **New repository**.
2. Name: `historical-timeline`. Set to **Public** (required for free GitHub Pages). Tick **Add a README file**. Click **Create repository**.
3. Open **GitHub Desktop** → File → **Clone repository** → select `historical-timeline` → choose where it lives on your computer (e.g., Documents) → **Clone**. You now have a synced local folder.

### Stage 2 — Install the prototype (~10 min)

1. Copy both `index.html` **and** the `data` folder (containing `events.json`) into your `historical-timeline` folder. You need both — `index.html` loads its events from `data/events.json`, so without the data folder the timeline is empty.
2. Double-click `index.html` — it opens in your browser and works immediately. Play with every toggle: theme, orientation, direction, zoom, filters, swimlane dragging, search.
3. In **GitHub Desktop** you'll see the new file listed. Type a summary in the box bottom-left, e.g., `Add timeline prototype` → click **Commit to main** → click **Push origin** (top bar). Your code is now safely on GitHub.

> This commit-and-push ritual is your undo button for life. Do it after every working change. If you ever break something, GitHub Desktop → History → right-click the last good commit → "Revert" gets you back.

### Stage 3 — Publish the site (~5 min)

1. On github.com, open your repository → **Settings** → **Pages** (left sidebar).
2. Under "Build and deployment": Source = **Deploy from a branch**; Branch = **main**, folder **/ (root)** → **Save**.
3. Wait 1–2 minutes. Your site is live at `https://YOUR-USERNAME.github.io/historical-timeline/`. Every future push updates the live site automatically within a couple of minutes.

### Stage 4 — Learn the Cursor loop (~30 min, your most important skill)

1. Open Cursor → **File → Open Folder** → your `historical-timeline` folder.
2. Open the chat panel (Cmd+L on Mac / Ctrl+L on Windows).
3. Practice with a harmless change. Type: *"In index.html, make the zoom buttons slightly larger and add a tooltip that says 'Zoom in' and 'Zoom out'."*
4. Cursor proposes edits; click **Accept**. Save. Refresh `index.html` in your browser. See the change.
5. Commit and push in GitHub Desktop.

How to prompt Cursor well as a novice: one change per request; describe what the user should see, not how to code it ("when I hover a dot, the label should turn bold"); paste any browser error messages verbatim (open the browser console with F12 → Console); if a change breaks things, say "undo that last change" or revert in GitHub Desktop. Never accept edits you haven't tested in the browser before committing.

### Stage 5 — Build the real dataset with Cowork (ongoing)

This is the 80%. Work in **batches of 20–30 events** per Cowork session. Give Cowork this exact prompt (save it somewhere):

> "Using Wikipedia as the source, generate 25 historical events from [YEAR RANGE] for the category [CATEGORY] as JSON objects with this schema: {date: 'YYYY.MM.DD', category: '[category-key]', importance: 1–5, tags: ['lowercase','keywords'], summary: '≤40 characters', source: 'Wikipedia URL'}. Use only these category keys: history, politics, religion, science, tech, arts, pop, sport, exploration. Verify each date against the Wikipedia article. Summaries must be 40 characters or fewer — count them. Importance: 5 = world-changing, 3 = nationally significant, 1 = notable trivia. Add 1–3 lowercase hyphenated tags per event for fine-grained topics (e.g. specific sport, religion, sub-field, or event type like war/disaster/birth/death), reusing common tags rather than inventing near-duplicates. Return only the JSON array."

Then spot-check 3–5 entries yourself against Wikipedia (trust, but verify — dates are where errors hide). Paste the batch into `events.json` via Cursor ("add these events to the data array, keeping it sorted by date"), refresh, confirm they appear, commit.

Suggested curation order: (1) importance-5 events across the whole 1900–present range in all categories — this makes the fully zoomed-out view immediately compelling; (2) then deepen decade by decade.

### Stage 6 — Iterate on features

Take each item to Cursor one at a time, test, commit. A sensible order:

1. Tooltip/detail card on dot click, listing all events at that date with links to their Wikipedia sources
2. Label collision refinements at month zoom (this will need several rounds)
3. URL sharing: encode zoom position and filters in the address so a view can be shared
4. Mobile pinch-zoom polish and touch-friendly swimlane dragging
5. "Jump to date" input box refinements (basic version is built into search)
6. Category dot shapes, if monochrome dots prove ambiguous (see analysis §4)

### Stage 7 — Verification habits

Before every commit: both themes render with correct hex values (#000000 / #FFF1E0 / #FFFFFF); both orientations and both directions work at all three zoom levels; filters actually hide lanes; search finds and jumps to events; no red errors in the browser console (F12). Once a month, ask Cowork to audit `events.json`: summaries over 40 characters, invalid dates, duplicate entries, category typos.

---

## Part 5 — Costs and Constraints

Everything above is $0: GitHub Pages hosting is free for public repositories, Cursor has a workable free tier, and the site has no server costs ever. Constraints to remember: GitHub Pages is public (anyone can view your code and data — fine for this project); the site is static, so features like user accounts or user-submitted events would require a real backend later; and a single events.json stays fast up to roughly 10,000–20,000 events, after which ask Cursor to split it by decade and load lazily.

---

## Part 6 — Going Live With Ads (do this only when the site is final)

You want a single fixed ad bar at the bottom of the page. This is achievable, but the binding constraints are Google's, not the code's. Do none of this until your real dataset is in place and the site feels finished — an empty ad slot on a half-built site both looks bad and hurts approval.

### The three things Google controls

**1. AdSense must approve the site.** Approval requires "sufficient" original, high-value content. A timeline that is mostly data points risks rejection as "low value content" — a common outcome for single-purpose tools. Your curated dataset (the 80% work) is what makes the site substantial enough to pass. Apply only once you have a meaningful body of events, not before.

**2. You need a custom domain.** AdSense approval on a raw `username.github.io` subdomain is unreliable; Google generally wants a domain you own. Buy one (~€10/year), then point GitHub Pages at it (repository → Settings → Pages → Custom domain). Budget this as the one unavoidable cost of running ads.

**3. Privacy and consent are mandatory, not optional.** Ads use cookies, so before ads serve you must have: a **privacy policy** page, a **cookie-consent banner** (for EU/EEA visitors this is a GDPR/ePrivacy requirement — consent must be collected *before* ad cookies load), and an **`ads.txt`** file at the site root declaring your AdSense publisher ID. Treat these as prerequisites, not afterthoughts.

### The layout change (the easy part)

When ready, ask Cursor for this in plain English: *"Reserve a fixed 90px bar across the bottom of the page for an ad. Shrink the timeline area to sit above it, and move the zoom controls and the Wikipedia footer up so they sit above the ad bar, not behind it."* The timeline currently fills the whole viewport, so the only real work is reserving that strip and relocating the three bottom-anchored elements (zoom buttons, footer, and the on-screen hint).

### Manual bar vs. Auto ads — a choice

Google offers two routes. **Auto ads** place an anchored bottom ad for you from a single script tag — least work, but Google controls the look, which fights your minimalist black/cream aesthetic. A **manually placed ad unit** in your own fixed bar gives you full styling control. For this site, lean manual. Either way, Google permits a sticky/anchored bottom ad, but placement rules apply (don't crowd content; some formats must be dismissible; one anchor ad per page).

### Before you apply

AdSense content, policy, and placement rules change. Verify the current requirements on Google's own AdSense site at the time you apply rather than relying on this summary.

---

## Appendix — Category Keys

The nine swimlanes, in display order. `category` must be exactly one of these keys; anything more specific goes in `tags` instead.

| Display name | JSON key |
|---|---|
| Historical Events | `history` |
| Politics | `politics` |
| Religion & Belief | `religion` |
| Science & Nature | `science` |
| Technology | `tech` |
| Arts & Literature | `arts` |
| Pop Culture & Leisure | `pop` |
| Sport | `sport` |
| Exploration & Discovery | `exploration` |

**Common tags to reuse** (grow this list as you curate, but prefer an existing tag over a new near-duplicate): event types — `war`, `disaster`, `natural-disaster`, `assassination`, `terrorism`, `treaty`, `birth`, `death`; themes — `cold-war`, `economics`, `finance`, `pandemic`, `independence`, `civil-rights`, `social-movement`; sports — `olympics`, `football`, `athletics`, `running`; religions — `christianity`, `catholic`, `islam`, `judaism`, `buddhism`; science/tech — `physics`, `biology`, `genetics`, `space`, `nasa`, `computing`, `internet`, `web`, `ai`; arts/media — `literature`, `music`, `film`, `television`, `animation`.
