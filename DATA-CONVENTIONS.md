# Data Conventions

Rules for every entry in `data/events.json`. Apply them identically in every batch so the dataset stays consistent. If a rule needs to change, change it here first.

## Entry format

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

## The nine lanes: what belongs where

Each event goes in exactly one lane: the one where its **primary significance** sits. Secondary themes go in `tags`. Enter an event twice (two lanes) only when each entry has a genuinely different framing, e.g. the Moon landing (science) and the global broadcast (pop).

| Key | Lane | Belongs here |
|---|---|---|
| `history` | Historical Events | Wars, outbreaks, crashes, assassinations, pandemics, disasters with human-history impact (e.g. Titanic) |
| `politics` | Politics | Governments, elections, treaties, independence, legislation, rights movements |
| `religion` | Religion & Belief | Religious leaders, institutions, doctrine, councils, schisms. If a religious leader or body is the actor, use this lane |
| `science` | Science & Nature | Discoveries, theories, experiments, natural phenomena and natural disasters |
| `tech` | Technology | Inventions, products, computing, engineering, spacecraft hardware |
| `arts` | Arts & Literature | Literature, visual art, classical and art music, theatre, architecture, philosophy |
| `pop` | Pop Culture & Leisure | Film, TV, popular music, games, celebrity, mass entertainment |
| `sport` | Sport | Competitions, athletes, records, sporting milestones |
| `exploration` | Exploration & Discovery | Expeditions, firsts (ascents, voyages, flights, spaceflight), archaeological discoveries, exploration of the deep sea |

## Importance rubric

Ask: *within this lane, across 1900 to today, how defining is this event?*

| Score | Test | Target share |
|---|---|---|
| 5 | One of the roughly 10 most defining events of the lane. A well-informed person would name it unprompted. Shown on first load. | ~15% |
| 4 | Major. Belongs in a 50-event summary of the lane. | ~25% |
| 3 | Notable. A well-informed generalist recognizes it. | ~35% |
| 2 | Significant within a field or region. | ~20% |
| 1 | Niche, trivia, or illustrative detail. | ~5% |

Score against the lane, not the world. The best Sport event is a 5 even though it is smaller than a world war. Do not inflate: if every lane shows 15 five-star events on load, the zoomed-out view becomes cluttered.

## Date rules

The timeline is day-precise. **If the exact day cannot be verified, do not add the event.**

| Event type | Use this date |
|---|---|
| War | Outbreak or first major hostilities |
| Armistice / treaty | Signing date (unless entry into force is the conventional date) |
| Election | Day of the vote (final day if multi-day) |
| Publication | First publication of the first edition |
| Premiere / release | First public performance or screening |
| Discovery / theory | Date announced or published, unless a specific moment is documented (e.g. tomb found) |
| Disaster | Date of onset |
| "First" achievement | Date it was achieved |
| Sporting tournament | Opening day or first match |
| Birth / death | Use sparingly; importance 4 or higher; tag `birth` or `death` |

Dates use calendar dates as Wikipedia gives them, in the Gregorian calendar.

## Summary rules

- 40 characters or fewer, counted by the validator.
- Present tense, active voice, no trailing period.
- Name the specific thing ("Apollo 11 lands humans on the Moon", not "Moon landing").
- Neutral wording. State what happened, not who was right. No loaded adjectives.
- Abbreviations only when universally known (US, UK, WHO).

## Tags

1 to 3 per event, lowercase, hyphenated. Reuse tags from `tools/tags.txt`. Add a new tag to that file only when no existing tag fits. Check the file first: `film`, not `movie`; `world-cup`, not `worldcup`.

## Sources and verification

1. `source` is the English Wikipedia article for the event.
2. The date is checked against that article before the event is added.
3. If Wikipedia is ambiguous or conflicts with another source, check a second source (Britannica or an official source). If still unclear, drop the event.
4. Run `python3 tools/validate_events.py` before every commit. It must report no errors.
5. A human spot-checks 3 to 5 entries per batch against Wikipedia.
6. One commit per batch.

## Tools

```
python3 tools/validate_events.py            # check the data; exits non-zero on errors
python3 tools/validate_events.py --sort     # also rewrite the file sorted by date
python3 tools/coverage_report.py            # lane x decade counts and importance mix
python3 tools/coverage_report.py --min-imp 4
```
