# ai-writing-tells

A Claude skill for writing and editing prose without the habits that make text read as machine-made. It catalogs the signs of AI writing from Wikipedia's field guide, adds findings from recent research, and includes a scanner script.

It does not try to make AI-drafted text pass AI detectors. For work that readers expect you to write yourself (assignments, reports, papers), it runs in copyedit mode: you write the draft, it fixes errors and shows each change, and your wording stays yours.

## What's in it

| Path | Contents |
|---|---|
| `SKILL.md` | The instructions Claude follows: writing workflow, copyedit mode, disclosure guidance, traps, review format |
| `references/patterns.md` | All 53 signs from Wikipedia's "Signs of AI writing" page, with its words-to-watch lists (as of Nov 2026) |
| `references/research.md` | Findings from about 20 papers on AI vs. human writing: vocabulary shifts, grammar ratios, rhetoric, argument structure, what expert readers notice, detector reliability |
| `scripts/scan_tells.py` | A scanner that flags the measurable patterns and reports sentence-length spread, punctuation variety, participial-clause rate and nominalization density |

## Install

**Claude apps:** download [`dist/ai-writing-tells.skill`](dist/ai-writing-tells.skill) and add it from the Skills section of Claude's settings.

**Claude Code:** copy the folder into `~/.claude/skills/`:

```bash
git clone https://github.com/Adithya407/ai-writing-tells_humanizer ~/.claude/skills/ai-writing-tells
```

The skill triggers on its own when you draft or edit prose, ask whether something "sounds AI", or mention AI writing tells. You can also call it by name.

## Using the scanner on its own

Python 3.8+, no dependencies.

```bash
python scripts/scan_tells.py draft.txt
python scripts/scan_tells.py --stdin < draft.md
python scripts/scan_tells.py draft.md --json
```

Sample output:

```
Verdict: several strong signs  (score 12.6, 84.0 per 1k words)
Grammar: participial clauses 5 (39.7/1k) | nominalizations 23.8/100 words | X, Y and Z lists 1 | questions 0
[54] dense present-participle clauses (', enabling...', ', highlighting...'): 1
[55] very noun-heavy prose (nominalizations): 1
```

Pattern numbers match `references/patterns.md` (1–53) and `references/research.md` (54–55).

## Limits

- Hits are signs, not proof. People use every one of these patterns, and detector studies show high false-positive rates on human writing, especially for non-native English writers.
- The grammar thresholds were set on a small set of samples. Nominalization density depends heavily on genre: engineering and legal prose is naturally noun-heavy.
- Word lists go stale as models change. The Wikipedia page keeps an era table, and this copy reflects it as of November 2026.
- Literal uses get flagged too ("landscape" meaning terrain, "underscore" meaning the `_` character). Read the context.

## Sources and attribution

`references/patterns.md` and parts of `SKILL.md` are adapted from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) by Wikipedia contributors (WikiProject AI Cleanup), licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Descriptions are paraphrased; the words-to-watch lists are quoted.

`references/research.md` summarizes published papers and preprints, cited in full at the end of that file.

## License

- `scripts/`: MIT, see `LICENSE`.
- `SKILL.md` and `references/`: CC BY-SA 4.0, see `LICENSE-CONTENT`, because they adapt Wikipedia text.
