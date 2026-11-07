---
name: ai-writing-tells
description: Signs of AI-generated writing from Wikipedia's "Signs of AI writing" field guide (WikiProject AI Cleanup, as of Nov 2026), with a scanner script and a copyedit mode for the user's own drafts. Use whenever drafting or revising prose that should read plainly (emails, posts, articles), when copyediting a user's own draft of a report, assignment, journal article or other submission, when the user asks to clean AI-sounding phrasing out of a draft, when they ask whether a text looks AI-written, or when they mention AI tells, AI slop, em dashes, "delve", or Wikipedia's AI-writing list, even if they don't name this skill.
---

# AI writing tells

This skill packages Wikipedia's field guide to AI-generated text (page: Wikipedia:Signs_of_AI_writing, read 7 Nov 2026) and the research literature on AI writing into three things you can use:
- `references/patterns.md`: the full catalog of the page's 53 patterns.
- `references/research.md`: findings from peer-reviewed and preprint studies, with grammar-level patterns 54–55, rhetoric, argument structure, and what expert readers actually notice.
- `scripts/scan_tells.py`: a scanner that flags the patterns a script can measure, including participial-clause density, nominalization density and three-part lists.

It supports two jobs:
- **Writing or revising** text so it doesn't carry the tells.
- **Reviewing** someone's text for tells, for example when the user asks whether a draft "sounds AI."

## Read this before you scrub anything

The page itself warns that the tells are symptoms. Its editors say that removing them while leaving the underlying problems in place just makes AI text harder to catch. The underlying problems are invented or unverifiable sources, synthesis the sources don't support, inflated significance, and filler. A paragraph can pass every check below and still be bad AI writing.

So the order of work is **substance first, surface second**. Most of the content-level tells (items 1–7 in the reference) disappear once every sentence states a specific, checkable fact. The page's own illustration: "inventor of the first train-coupling device" turns into "a revolutionary titan of industry" when a model smooths specifics into generic praise. Put the specific fact back and the puffery has nothing left to attach to.

## Workflow: writing or revising

1. **Pin down the facts.** For every claim, know where it comes from: the user's material, a source you actually read, or general knowledge you can stand behind. Cut claims about significance, legacy, or "broader trends" that no source makes. If a source is missing, say so plainly once instead of hedging around it.
2. **Draft plainly.**
   - Use "is", "are" and "has".
   - Use plain verbs: wrote, used, moved, died.
   - State relationships directly: "was CEO of X," never "was associated with leadership of X."
   - Say each thing once and stop. No closing summary paragraph.
3. **Scan the draft.**
   `python scripts/scan_tells.py draft.txt`, or pipe text in with `--stdin`. Use `--json` if you want to post-process the output. The report groups hits by pattern number and gives line numbers.
4. **Rewrite each flagged sentence around its fact.** Don't swap synonyms. Replacing "crucial" with "vital" only moves the tell, and cycling synonyms is itself a tell (item 53). Usually the fix is deleting the evaluative clause or replacing it with the concrete detail it was standing in for.
   The report includes a "Grammar" line. A high participial-clause rate (pattern 54) or a high nominalization rate (pattern 55) is fixed by restructuring the sentence: give it a person as subject and a finite verb ("the team reduced spoilage to 6%," not "contributing to the reduction of spoilage"). Nominalization density depends on genre, so compare it against the field's normal prose.
5. **Check what a regex can't.** Look over `references/patterns.md` and the argument-structure section of `references/research.md` for structural patterns:
   - a "Challenges" or "Future outlook" ending
   - an "Awards and recognition" section
   - leads that treat a list title as a proper noun
   - citation problems
   - rule-of-three rhythm throughout

## Copyedit mode: the person writes, you correct

Use this mode for anything going to readers who expect the person's own writing: graded assignments, lab and project reports, journal or conference articles, applications, online submissions. In these cases the person drafts and you edit. The text stays theirs, and the result reads as theirs because it is.

1. **Get their words first.** Ask for their draft, or at least rough notes in their own phrasing. If they only give a topic, don't write the piece. Give them an outline instead: the points to cover, the order, and the questions each section should answer. They write the prose.
2. **Fix what is wrong, keep what is theirs.**
   - Correct spelling, grammar and punctuation errors.
   - Correct wrong facts, units, equations and figure references.
   - Fix broken or unverifiable citations. Check each against its source, and never invent one to fill a gap.
   - Clarify sentences a reader would misread.
   - Keep their word choices, sentence order, paragraph structure and voice, including plain or slightly informal phrasing that isn't an error.
3. **Show every change.** List edits as before → after with a short reason, or mark them inline, so the person accepts or rejects each one. Don't silently rewrite paragraphs into your own phrasing: at that point the text is yours, not theirs.
4. **Flag tells in their draft too.** People pick up AI phrasing from reading it. Run the scanner on their draft and point out hits, but let them reword; suggest a fix only when they ask.
5. **"No mistakes" means correct, not polished.** Correct grammar and accurate content are the goal. Smoothing every sentence into the most standard phrasing erases the person's voice and is not required for correctness.

## Disclosure

Many universities and most journals have AI-use policies. Some require disclosure of any AI assistance, and some ban AI-drafted text outright. For anything going to such readers:
- Remind the person once to check the policy that applies (course syllabus, department rules, the journal's author guidelines).
- When AI help went beyond spelling and grammar, give a disclosure line they can adapt to what actually happened. For example: "I used Claude (Anthropic) to check grammar and suggest wording edits; the content, analysis and final wording are my own."
- This skill does not help make AI-drafted text pass detectors for readers who would object to AI drafting. Detectors can't be reliably beaten anyway (QuillBot's false-positive rate on human writing alone is around 13%), and the copyedit route above is both honest and the thing that actually reads as the person's own work.

## Traps: fixes that create new tells

These come straight from the page, and they are why "never use any pattern" can't be followed literally.

- **Zero em dashes.** Spaced em dashes were a tell through 2026. The newest models are now hard-coded to avoid them, and the page reports that the resulting sameness (only commas and periods) is now a tell of its own. Vary your punctuation: an occasional semicolon, colon, parenthesis, or unspaced em dash reads as human.
- **Uniform short sentences.** The mid-2026 (GPT-6) signature includes sentences held between 8 and 20 words. Let some sentences run long and some be very short.
- **The late-2026 word list includes ordinary words:** challenge, clearer, practical, matters, steady, quietly, prioritize. One occurrence is noise; clusters are the signal. Don't contort a sentence to avoid a single "practical."
- **Context matters.** Literal uses are fine: "underscore" for the underline character, "landscape" for terrain, "key" for a physical key, "challenge" for an actual competition.
- **Negative parallelism** ("not X but Y," "Y rather than X") is fine when it corrects a misconception the reader really holds. The tell is the reflexive, rhetorical version.

## Which categories apply where

- **Chat replies, emails, essays, reports:** content (1–8), language (9–13), style (14–19), user-directed leftovers (20–22), and the historical items (46–50, 53).
- **Wikipedia or wiki editing:** all of the above, plus markup (23–25), citations (26–32), talk-page comments (33), edit summaries (34–38), and miscellaneous (39–45).
- **Any document with references:** citations (26–32) apply. Fabricated or unsupported references are the most damaging failure here, so verify each one against its source instead of trusting format.

## What human writing tends to have

The research (see `references/research.md`) finds that the strongest differences are grammatical and structural, and that prompting a model to "sound human" barely changes them. In a person's own draft, protect these features and don't edit them away:
- **Verbs and people as subjects:** "we measured," "she argued," in place of noun stacks like "the measurement of" or "the implementation of". AI prose runs about twice as heavy in nominalizations (pattern 55).
- **Clauses joined plainly** with and, but or because. AI attaches ", enabling...", ", highlighting..." clauses at about five times the human rate (pattern 54).
- **Uneven sentence lengths** and some passives where the actor doesn't matter.
- **Rhetorical devices only where the argument needs them:** a real question the writer then answers, a correction of their own point, three items only when there are three.
- **Hedges that track the evidence:** "probably" where the writer is unsure, plain statement where they are sure. LLMs produce twice the human rate of hedging that isn't tied to any real uncertainty.
- **Concrete particulars:** the writer's own data, names, places, numbers and mistakes, and criticism or frustration where it's earned.
- **Structure that follows the argument,** not a template. A report can open with its result.

The Wikipedia page adds these features of human Wikipedia text:
- simple is/has sentences ("there is a," "it has a")
- plain verbs over stiff ones: wrote, moved, used, tried, died (rather than authored, relocated, utilized, attempted, passed away)
- definite, sourced superlatives ("was the first," "is the only")
- ordinary qualifiers ("very," "perhaps," "tends to")
- the occasional wordy construction ("in order to," "the fact that")
- repeating the right word instead of reaching for a synonym

## Reviewing someone else's text

Report signs as signs, not proof. The page stresses that:
- humans who rarely use chatbots detect AI text at about chance level
- detector tools have real error rates
- text from before 30 Nov 2022 (ChatGPT's launch) can be ruled out

These are poor evidence and shouldn't count toward a verdict: perfect grammar, mixed casual and formal registers, bland or formal prose, transition words on their own, missing citations, and odd wikitext.

Use this output shape:

```
Signs found: <count> across <n> categories
Strongest: <the 2–3 most diagnostic hits, with the quoted span and pattern number>
Other hits: <list, quoted span + pattern number + one-line rewrite>
Not evidence: <anything the user might over-read, e.g. good grammar>
Verdict: <"several strong signs" / "a few weak signs" / "nothing notable">, never "this is AI-generated" as fact
```

The strongest signs on the page are:
- leaked chatbot phrases ("I hope this helps," "Would you like...")
- placeholders ([Your Name], 2025-XX-XX)
- citation internals such as oaicite or utm_source=chatgpt.com
- dense clusters of AI vocabulary
- the mid-2026 hedging pattern ("should be treated as X rather than Y," "does not by itself establish")
