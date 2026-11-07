# Research findings on AI writing patterns

Read this when you need to explain *why* something reads as AI, or when the scanner flags grammar-level patterns (54–55). These are peer-reviewed or preprint findings, gathered 7 Nov 2026. Pattern numbers continue from `patterns.md`.

The main lesson of this literature: the deepest AI signals are in grammar, rhetoric and argument structure, not in individual words. Instruction tuning (chat training) produces them. Base models write close to human style. Larger models do not fix it. Prompting a model to "sound human" barely moves them.

## Contents
- Words
- Grammar (patterns 54–55)
- Rhythm and variation
- Rhetoric and stance
- Argument structure
- What expert readers look at
- What converting AI drafts does
- Detectors
- Pangram blog (vendor source, use with care)
- Sources

## Words
- GPT-4o uses certain words at more than 100 times the human rate: camaraderie, tapestry, intricate, underscore, unspoken, amidst, palpable, solace, fleeting, unravel. "Tapestry" appeared in 23% of GPT-4o outputs and "amidst" in 27% (Reinhart et al.).
- PubMed 2000–2024: 103 of 135 suspected AI terms rose sharply in 2024. The leaders were delve, underscore, primarily, meticulous and boast. The rise began in 2020, so LLMs amplified existing trends (Matsui).
- Whole groups of near-synonyms rise together, so swapping one AI word for its synonym often lands on another AI word. "Important" declined (Galpin et al.).
- "Delve" fell after it became a known tell in early 2024, while "significant" kept rising. Authors edit LLM output, so word lists go stale (Geng & Trotta).
- Verbs meaning "emphasize" are overused in 24 of 34 languages (Juzek 2026). In arXiv titles "beyond" and "via" are rising, and in abstracts "the" and "of" are falling (Geng et al. 2026).
- AI cycles synonyms (notes, explains, emphasizes) where human journalists repeat "says." In one study, 63% of GPT-4o articles and 70% of Claude-3.5 articles used a character named Emily or Sarah (Russell et al.).

## Grammar
**54. Dense present-participle clauses.** Examples: ", enabling...", ", highlighting...", "Leaning on his agility, he...". GPT-4o used them at 5.3 times the human rate (Cohen's d = 1.38, the largest effect in the study). Instruction-tuned Llama 3 used them at 2 to 5 times the human rate. The scanner counts -ing words after a comma and -ing sentence openers, excluding common -ing nouns and prepositions.

**55. Noun-heavy, information-dense prose.**
- Nominalizations ("the implementation of" for "implement"): 2.1 times the human rate in GPT-4o, and 1.5 to 2 times in instruction-tuned Llama.
- "That" clauses as sentence subjects: 2.6 times. Phrase-level coordination ("X and Y" inside a clause): 1.9 times.
- Agentless passive: about half the human rate in GPT-4o.
- Downtoners ("barely," "nearly") are underused by every model tested (Rallapalli et al.).
- ChatGPT maximizes nouns and adjectives. It underuses pronouns, adverbs, passives and function words, joins phrases with "and" but rarely joins clauses, avoids narration (past tense, third-person storytelling), and flattens the differences between genres. Its essays read like its encyclopedia entries (Dentella et al.). The authors' explanation: tense, aspect and mood are what tie a statement to checkable facts, and models avoid them.
- The scanner measures -tion, -sion, -ment, -ness and -ity words per 100 words. This rate depends heavily on genre: legal and engineering prose is naturally noun-heavy. Compare against the genre, not an absolute threshold. A plain human report scored about 0–2.5, and an AI-style abstract about 24.

## Rhythm and variation
- Human text has more scattered sentence lengths, more varied vocabulary, shorter phrases, and more negative emotion (fear, disgust, anger). LLM text skews toward joy (Muñoz-Ortiz et al., news). Note that those models were base and older chat models. Instruction-tuned models show the noun-heavy profile above.
- Human writing varies more on almost every feature. Newer models are converging on one homogenized style (Zanotto & Aroyehun).
- Expert readers called AI grammar "perfect" and noted that human text has small errors and mixed punctuation (Russell et al.). Don't add errors on purpose. Keep the writer's natural ones that aren't actual mistakes.

## Rhetoric and stance (Bakhshi 2026, argumentative essays)
Mean counts per document:

| Device | LLM | Human expert | Human non-expert |
|---|---|---|---|
| Three-part lists (tricolon) | 7.13 | 3.73 | 4.87 |
| Rhetorical questions (erotema) | 2.28 | 5.55 | 5.11 |
| Self-correction (correctio, "or rather...") | 0.17 | 0.40 | 0.45 |

- "Performed" hedging (hesitancy that isn't tied to real uncertainty in the evidence) has twice the human density: 0.114 against 0.057 for experts and 0.058 for non-experts. Experts and non-experts don't differ from each other, so this is specific to LLMs.
- LLMs spread rhetorical devices evenly through the text. Humans cluster them at points where the argument needs force.

## Argument structure (Sadallah et al. 2026, research-paper introductions)
- Generated introductions follow the textbook order: territory, then gap, then "this paper." None of 608 opened with the paper's purpose, which human authors sometimes do.
- One "go back" move accounted for 89% of returns in generated introductions, against 57% for humans.
- Giving models the structural framework made them more rigid.
- A blind reader told original from generated introductions 90% of the time. They cited argument structure for 118 of 120 decisions and style for only 15.

## What expert readers look at (Russell et al. 2025)
Five annotators who use LLMs heavily misclassified 1 of 300 articles by majority vote, beating most automatic detectors. Share of explanations citing each clue:

| Clue | Share |
|---|---|
| Vocabulary | 53% |
| Sentence structure ("not just X, it's Y," lists of three) | 36% |
| Grammar ("too perfect") | 25% |
| Originality (safe, no surprises or humor) | 24% |
| Quotes (all sources speak in the article's own voice) | 22% |
| Clarity (over-explaining, telling instead of showing) | 20% |

Wang et al. 2025: 19 annotators reached 87.6% accuracy across 9 languages. The biggest gaps between human and AI text were in concreteness, cultural detail and diversity.

## What converting AI drafts does
- Russell et al. built a "humanizer" from their own experts' clue list. It degraded many automatic detectors. The expert majority vote was still correct on all 60 articles, though confidence dropped.
- Clues survived humanization. For example, the humanized articles overused titles like "Dr." and "Prof."
- "Generate, then make it sound human" behaved like paraphrasing.
- Iterating several LLM rewriting passes added more AI traits. The strongest traits came from the original generation.
- Prompting models to write like humans, or giving them human text to continue, leaves the grammar profile largely intact (Reinhart; Rallapalli; Dentella: "marginally mitigated").

**Implication for this skill:** text reads as human-written when a person writes it. Use the copyedit mode in SKILL.md, and don't rewrite AI drafts for readers who expect the person's own work.

## Detectors
- Detectors misclassify non-native English writing (Liang et al. 2023). A 2026 review found 50–61% of non-native writing flagged, against under 5% for native writers.
- Across 13 detectors, false-positive rates on human text ranged from 0% to 100%, and professional editing moved scores in opposite directions on different detectors (Park et al. 2026, 135,389 manuscripts).
- Counterpoint: for Czech, newer detectors no longer rely on perplexity and showed no non-native bias (Al Ali et al. 2026).
- Detectors break down under paraphrasing and on unfamiliar models: RAID; Wang et al. 2024 (a 35% average drop); ARB 2026. In ARB, detectors that caught 91–93% of raw LLM text caught only 15–31% of human text an LLM had revised. They cannot reliably separate LLM-polished human work from human work.

## Pangram blog (vendor source, use with care)
Pangram sells AI detectors. Its guide lists about 600 words and phrases, including everyday words like "health," "life," "community" and "support," and gives no frequency data, so don't scan against it. Its non-vocabulary claims mostly agree with the research above:
- monotonous sentence length
- rare semicolons and parentheses
- American spelling, few contractions, Oxford commas
- uniform paragraphs, long "Overall" conclusions
- vague generalities that fit any prompt, and a formal, positive tone
- avoidance of proper nouns
- no personal reflection, and restating the prompt

Its "AI can't produce original thought" claim is opinion, not a finding.

## Sources
- Reinhart et al., Do LLMs write like humans? Variation in grammatical and rhetorical styles. PNAS 2025. arXiv:2410.16107
- Rallapalli et al., Interpretable Stylistic Variation in Human and LLM Writing. 2026. arXiv:2604.14111
- Dentella et al., ChatGPT-generated texts show authorship traits that identify them as non-human. 2025. arXiv:2508.16385
- Muñoz-Ortiz et al., Contrasting Linguistic Patterns in Human and LLM-Generated News Text. 2024. arXiv:2308.09067
- Zanotto & Aroyehun, Linguistic and Embedding-Based Profiling of Texts. 2025. arXiv:2507.13614
- Bakhshi, Saying More Than They Know. 2026. arXiv:2604.19768
- Sadallah et al., Does AI-Generated Scientific Text Follow Human Argumentation Patterns? 2026. arXiv:2610.01353
- Russell, Karpinska & Iyyer, People who frequently use ChatGPT for writing tasks are accurate and robust detectors. ACL 2025. arXiv:2501.15654
- Wang et al., Is Human-Like Text Liked by Humans? 2025. arXiv:2502.11614
- Juzek & Ward, Why Does ChatGPT "Delve" So Much? COLING 2025. arXiv:2412.11385
- Matsui, Delving Into PubMed Records. Perspectives on Medical Education. PMC12679996
- Galpin, Anderson & Juzek, Exploring the Structure of AI-Induced Language Change. 2025. arXiv:2506.21817
- Geng & Trotta, Human-LLM Coevolution. 2025. arXiv:2502.09606
- Geng, Dong & Poibeau, Beyond Via. 2026. arXiv:2603.25638
- Juzek, AI-Associated Lexical Shifts Across 34 Languages. 2026. arXiv:2605.25358
- Liang et al., GPT detectors are biased against non-native English writers. 2023. arXiv:2304.02819
- Park, Jeong & Kim, Style as a Confound. 2026. arXiv:2608.26710
- Ndacyayisenga et al., systematic review on non-native medical students. 2026. PMC13277128
- Al Ali, Helcl & Libovický, Different Time, Different Language. 2026. arXiv:2602.05769
- Dugan et al., RAID. 2024. arXiv:2405.07940
- Wang et al., Stumbling Blocks. 2024. arXiv:2402.11638
- Perrone & Romano, ARB. 2026. arXiv:2607.29539
- Pangram, Comprehensive Guide to Spotting AI Writing Patterns (blog). pangram.com
