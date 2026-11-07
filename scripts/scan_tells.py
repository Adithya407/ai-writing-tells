#!/usr/bin/env python3
"""Scan prose for signs of AI writing (Wikipedia: Signs of AI writing, Nov 2026).

Usage:
    python scan_tells.py draft.txt
    python scan_tells.py --stdin < draft.txt
    python scan_tells.py draft.md --json

Pattern numbers match references/patterns.md. Hits are *signs*, not proof:
one or two vocabulary words are coincidence; clusters are the signal.
Fenced code blocks (```...```) and inline code (`...`) are skipped.
"""
import argparse
import json
import re
import statistics
import sys
from collections import defaultdict

FLAGS = re.IGNORECASE


def words(*ws):
    """Build a word-boundary alternation from phrases."""
    return r"\b(?:" + "|".join(ws) + r")\b"


# (pattern number, short label, regex, weight). Weight ~ how diagnostic one hit is.
CHECKS = [
    # 1 significance / legacy
    (1, "inflated significance/legacy", words(
        r"stands as", r"serves as a (?:testament|reminder)", r"is a testament", r"a testament to",
        r"is a reminder", r"(?:crucial|pivotal|vital|significant|key) (?:role|moment)",
        r"(?:underscores|highlights|underscoring|highlighting) (?:its|their|the) (?:importance|significance)",
        r"reflects? (?:a )?broader", r"symboli[sz]ing (?:its|their|the) (?:ongoing|enduring|lasting)",
        r"setting the stage for", r"(?:marks|marking|represents|representing) a (?:significant )?shift",
        r"(?:marking|shaping) the", r"key turning point", r"evolving landscape", r"focal point",
        r"indelible mark", r"deeply rooted", r"broader (?:movement|trend|context|debates?)",
        r"enduring legacy", r"lasting (?:legacy|impact|influence)",
        r"distinction (?:matters|is important)", r"public discussions?"), 2),
    # 2 notability / media coverage
    (2, "canned notability/coverage", words(
        r"independent coverage", r"(?:local|regional|national|international) (?:media|press) (?:outlets|coverage)",
        r"(?:music|business|tech|technology|trade) (?:outlets|publications)", r"trade publications",
        r"(?:has been )?(?:featured|profiled|cited) in", r"written by a leading expert",
        r"(?:active|strong) (?:social media|digital) presence", r"prominent media outlets"), 2),
    # 3 identification by primary sources
    (3, "'source identifies X as'", r"\b(?:databases?|records?|listings?|filings?|materials?|websites?|profiles?)\s+"
        r"(?:identif(?:y|ies)|lists?|describes?)\s+\w+(?:\s+\w+)?\s+as\b|\bwas identified by\b|\bis listed in\b|"
        r"\bprofessional profile lists\b", 2),
    # 4 trailing -ing analysis clause
    (4, "trailing -ing analysis clause", r",\s+(?:further\s+)?(?:highlighting|underscoring|emphasi[sz]ing|ensuring|"
        r"reflecting|symboli[sz]ing|contributing to|cultivating|fostering|encompassing|enhancing|showcasing|"
        r"solidifying|reinforcing|demonstrating|illustrating|cementing)\b", 2),
    (4, "superficial-analysis phrase", words(r"valuable insights?", r"resonates? with", r"aligns? with"), 1),
    # 5 vague connection
    (5, "vague connection/association", words(
        r"in connection with", r"in connection to", r"connected (?:with|to)", r"in association with",
        r"(?:widely |particularly |closely )?associated with"), 1),
    # 6 weasel attributions
    (6, "vague attribution", words(
        r"industry reports", r"observers have (?:cited|noted)", r"experts (?:argue|say|note|believe)",
        r"some critics (?:argue|say|note)", r"several (?:sources|publications|outlets)",
        r"(?:scholars|researchers|critics) (?:have )?(?:noted|argued|described)", r"widely (?:interpreted|regarded|seen)",
        r"is described in scholarship"), 2),
    # 7 challenges formula
    (7, "challenges/future-outlook formula", words(
        r"despite (?:its|their|these|the) [\w\s,-]{0,40}?(?:faces|face) (?:several |numerous |many )?challenges",
        r"faces? (?:several|numerous|many) challenges", r"despite these challenges",
        r"challenges and (?:legacy|future directions|opportunities)", r"future (?:outlook|prospects|directions)"), 3),
    # 8 awards & recognition
    (8, "'Awards and recognition' heading", r"^#{1,6}\s*(?:awards and recognition|recognition)\s*$|^\s*awards and recognition\s*$", 2),
    # 9 AI vocabulary
    (9, "AI vocabulary", words(
        r"delv(?:e|es|ed|ing)", r"tapestry", r"testament", r"pivotal", r"crucial", r"vibrant", r"meticulous(?:ly)?",
        r"intricate", r"intricacies", r"interplay", r"underscor(?:e|es|ed|ing)", r"showcas(?:e|es|ed|ing)",
        r"highlight(?:s|ed|ing)?", r"garner(?:s|ed|ing)?", r"bolster(?:s|ed|ing)?", r"enduring",
        r"enhanc(?:e|es|ed|ing)", r"foster(?:s|ed|ing)?", r"emphasi[sz]ing", r"align(?:s|ed)? with",
        r"boasts?", r"robust", r"landscape", r"valuable", r"deep dive", r"multifaceted", r"leverag(?:e|es|ed|ing)",
        r"seamless(?:ly)?", r"realm", r"navigat(?:e|es|ing) the"), 1),
    (9, "'Additionally,' opening a sentence", r"(?:^|[.!?]\s+)Additionally,", 1),
    (9, "mid-2026 (GPT-6) vocabulary", words(
        r"dependable", r"echoed", r"matters", r"practical", r"prioriti[sz](?:e|es|ed|ing)", r"quietly",
        r"steady", r"universally", r"clearer"), 0.5),
    (9, "Grok vocabulary", words(r"causal", r"empirical(?:ly)?", r"correlat(?:e|es|ed|ing)"), 0.5),
    # 10 copula avoidance
    (10, "copula avoidance (serves as / boasts / refers to)", words(
        r"serves as", r"stands as", r"functions as", r"operates as", r"acts as", r"boasts an?",
        r"features an?", r"refers to", r"began (?:his|her|their) career as", r"ventured into"), 1),
    # 11 negative parallelism
    (11, "negative parallelism: not only/just X but Y", r"\bnot only\b[^.!?\n]{0,120}?\bbut\b|"
        r"\b(?:is|was|it's|it is|isn't|wasn't)\s+not\s+just\b|\bnot just\b[^.!?\n]{0,80}?[,;—-]\s*(?:it'?s|but)\b|"
        r"\bdoesn'?t just\b|\bisn'?t just\b", 2),
    (11, "negative parallelism: not X, but Y / no X, just Y", r"\b(?:it'?s|this is|that'?s|is)\s+not\s+[^.!?\n]{1,60}?[,;—–-]\s*(?:it'?s|but)\b|"
        r"\bno [\w\s]{1,25}, no [\w\s]{1,25},? just\b|\bisn'?t\b[^.!?\n]{1,60}?[—–]\s*it'?s\b", 2),
    (11, "negative parallelism: Y rather than X", r"\brather than\b", 1),
    # 12 list title as proper noun (only checks first line)
    # 13 rule of three -> handled in stats
    # 17 heading levels -> stats
    # 20 collaborative leftovers
    (20, "chatbot-to-user leftover", r"I hope this helps|\bCertainly!|\bOf course!|\bAbsolutely!|"
        r"you(?:'re| are) absolutely right|great question|\bWould you like\b|is there anything else|"
        r"\blet me know\b|more detailed breakdown|\bhere(?:'s| is) an? (?:\w+ ){0,3}(?:version|draft|template|overview|breakdown|summary)\b|"
        r"Wikipedia-style article|(?:check|verify|confirm)[^.\n]{0,40}before (?:publishing|publication|submitting|submission)|"
        r"I hope this (?:message|email) finds you well|feel free to", 4),
    # 21 hedging disclaimers
    (21, "hedging disclaimer (2023-24 didactic)", r"\bit(?:'s| is) (?:important|crucial|worth) (?:to note|to remember|noting)\b", 2),
    (21, "hedging disclaimer (2024-25 source gap)", r"\b(?:specific )?(?:details|information) (?:about [^.]{0,60})?(?:is|are) (?:limited|scarce)\b|"
        r"\bnot (?:widely|extensively|publicly) (?:available|documented|disclosed|transcribed)\b|"
        r"\bin (?:the )?(?:provided|available) (?:sources|search results)\b|\bbased on (?:the )?available information\b|"
        r"\bmaintains a low profile\b|\bkeeps? (?:his|her|their) personal (?:life|details) private\b|\breadily available sources\b", 3),
    (21, "hedging disclaimer (mid-2026 corrective framing)", r"\bshould be (?:treated|presented|read|understood|regarded) as\b[^.]{0,80}\brather than\b|"
        r"\bdoes not (?:by itself |on its own )?establish\b|\bshould not be confused with\b", 3),
    # 22 placeholders
    (22, "placeholder text", r"\[(?:Your|Insert|Add|Describe|Article|Company|Name|Date|Link|Entertainer|Award|Another)[^\]\n]{0,60}\]|"
        r"\b\d{4}-(?:XX|xx)-(?:XX|xx)\b|INSERT_[A-Z_]+|PASTE_[A-Z_]+_HERE|SOURCE_PUBLISHER|example\.com/\w+|"
        r"\((?:Add|Insert) [^)]{0,40} here\)|<!--\s*Add if available", 5),
    # 23-24 markup leaks
    (24, "citation internals leaked", r"contentReference\[oaicite|oaicite:\d+|\bturn\d+(?:search|view)\d+", 5),
    (31, "chatbot tracking parameter", r"utm_source=(?:chatgpt\.com|openai|copilot\.com)|referrer=grok\.com", 5),
    (30, "footnote back-arrow", r"↩", 2),
    # 34-36 edit-summary / procedural language
    (34, "procedural compliance assurance", words(
        r"in compliance with", r"complies with", r"adheres? to (?:the )?(?:wikipedia|style|guidelines)",
        r"encyclopedic tone", r"neutral tone", r"improved (?:clarity|flow|readability)", r"refined (?:the )?tone",
        r"streamlined"), 2),
    (35, "'preserved/retained/avoided' procedural note", r"\bwhile (?:preserving|retaining|maintaining|keeping)\b|"
        r"\b(?:preserved|retained) (?:the )?(?:original|existing|references|structure|meaning)\b", 2),
    # 46 promo
    (46, "promotional/travel-guide language", words(
        r"nestled", r"in the heart of", r"groundbreaking", r"renowned", r"diverse array", r"natural beauty",
        r"commitment to", r"rich (?:cultural |)(?:heritage|history|culture|tradition)", r"profound", r"exemplif(?:y|ies)",
        r"breathtaking", r"stunning", r"captivat(?:e|es|ing)", r"must-visit", r"hidden gem"), 2),
    # 47 cutoff, 49 refusal
    (47, "knowledge-cutoff statement", r"as of my last (?:knowledge |training )?update|up to my last training", 5),
    (49, "prompt refusal", r"as an AI(?: language model)?|as a large language model|I cannot offer (?:medical|legal|financial) advice", 5),
    # 48 summaries
    (48, "section summary opener", r"(?:^|[.!?]\s+)(?:In summary|In conclusion|Overall|To summari[sz]e|Ultimately|In essence),", 2),
    (48, "'Conclusion' heading", r"^#{1,6}\s*conclusion\b|^\s*conclusion:?\s*$", 2),
]

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\u2B50\u2705\u274C\u2728]")
SMALL_WORDS = {"a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to", "for", "by", "with", "vs", "from", "as", "is"}


def strip_code(text):
    """Blank out fenced and inline code, keeping line numbers intact."""
    def blank(m):
        return "\n" * m.group(0).count("\n")
    text = re.sub(r"```.*?```", blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", " ", text)
    return text


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def snippet(text, start, end, pad=40):
    s = max(0, start - pad)
    e = min(len(text), end + pad)
    return ("…" if s > 0 else "") + text[s:e].replace("\n", " ").strip() + ("…" if e < len(text) else "")


def split_sentences(prose):
    # drop headings, list markers and markup, then split on sentence-ending punctuation
    lines = []
    for ln in prose.splitlines():
        if re.match(r"^\s*#", ln) or not ln.strip():
            lines.append("\n")
            continue
        lines.append(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", ln))
    body = " ".join(lines)
    parts = re.split(r"(?<=[.!?])\s+(?=[\"'“‘(]?[A-Z0-9])|\n", body)
    return [p.strip() for p in parts if len(p.split()) >= 3]


def style_checks(text):
    hits = []
    lines = text.splitlines()
    h1 = 0
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", ln)
        if m:
            level, title = len(m.group(1)), m.group(2)
            if level == 1:
                h1 += 1
            toks = [t for t in re.findall(r"[A-Za-z][\w'-]*", title)]
            content = [t for t in toks if t.lower() not in SMALL_WORDS]
            if len(content) >= 3 and sum(t[0].isupper() for t in content) >= len(content) - 0 and \
                    sum(t[0].isupper() for t in content[1:]) >= 2:
                hits.append((14, "title-case heading", i, ln.strip(), 1))
            if EMOJI_RE.search(title[:3]):
                hits.append((18, "emoji at start of heading", i, ln.strip(), 2))
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*\n]{1,60}\*\*\s*:", ln) or \
                re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*\n]{1,60}:\*\*", ln):
            hits.append((16, "inline-header list item (bold label + colon)", i, ln.strip()[:90], 1))
        bm = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.{0,3})", ln)
        if bm and EMOJI_RE.search(bm.group(1)):
            hits.append((18, "emoji at start of list item", i, ln.strip()[:90], 2))
    if h1 > 1:
        hits.append((17, f"{h1} level-1 headings", 0, "", 1))
    return hits


# --- Research-based grammar measures (Reinhart et al. PNAS; Rallapalli et al. 2026; Bakhshi 2026) ---
# -ing words that are not participial clauses (nouns, prepositions, fixed forms)
ING_STOP = {
    "during", "nothing", "something", "anything", "everything", "thing", "things", "bring", "king", "spring",
    "morning", "evening", "string", "strings", "ceiling", "building", "buildings", "meaning", "meanings",
    "feeling", "feelings", "setting", "settings", "training", "beginning", "including", "according",
    "regarding", "concerning", "pending", "ring", "sing", "wing", "being", "earnings", "findings", "finding",
    "funding", "reading", "readings", "writing", "writings", "painting", "paintings", "ending", "wedding",
    "clothing", "housing", "pudding", "sibling", "siblings", "swing", "sting", "bearing", "spending", "living",
    "lightning", "opening", "openings", "warning", "warnings", "sampling", "processing",
    "learning", "engineering", "programming", "testing", "modeling", "modelling", "mapping", "timing", "routing",
    "shipping", "marketing", "accounting", "parking", "rating", "ratings", "recording", "recordings",
}
PARTICIPLE_AFTER_COMMA = re.compile(r",\s+(?:thereby\s+|further\s+|ultimately\s+|effectively\s+)?([A-Za-z]{3,}ing)\b")
PARTICIPLE_OPENER = re.compile(r"(?:^|(?<=[.!?]\s))\s*([A-Z][a-z]{2,}ing)\b[^.!?\n]{2,80}?,")
# Biber-style nominalizations: -tion/-sion/-ment/-ness/-ity endings on longer words
NOMINAL = re.compile(r"\b[a-z]{3,}(?:tions?|sions?|ments?|ness(?:es)?|ity|ities)\b", re.IGNORECASE)
NOMINAL_STOP = {"city", "cities", "pity", "entity", "entities", "moment", "moments", "comment", "comments",
                "element", "elements", "segment", "segments", "cement", "unity", "deity", "witness", "business",
                "businesses", "question", "questions", "station", "stations", "nation", "nations", "mention",
                "position", "section", "sections", "version", "versions", "lotion", "ocean", "mission", "vision",
                "television", "session", "sessions", "fashion", "passion", "commission", "university", "universities",
                "community", "communities", "quantity", "quantities", "electricity", "gravity", "humidity", "density",
                "velocity", "capacity", "equipment", "apartment", "department", "departments", "government",
                "governments", "document", "documents", "instrument", "instruments", "experiment", "experiments",
                "tournament", "garment", "fragment", "fragments", "pavement", "basement", "parliament", "sediment"}
TRICOLON = re.compile(r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3},? (?:and|or) [\w'-]+")


def grammar_measures(prose, n_words):
    plain = re.sub(r"[*_#>`]", " ", prose)
    part_hits = []
    for rx in (PARTICIPLE_AFTER_COMMA, PARTICIPLE_OPENER):
        for m in rx.finditer(plain):
            w = m.group(1).lower()
            if w not in ING_STOP:
                part_hits.append(m.group(1))
    noms = [m.group(0) for m in NOMINAL.finditer(plain) if m.group(0).lower() not in NOMINAL_STOP]
    tricolons = len(TRICOLON.findall(plain))
    questions = len(re.findall(r"[A-Za-z)\"'”’]\?(?:\s|$)", plain))
    per1k = lambda x: round(x * 1000 / n_words, 1) if n_words else 0
    return {
        "participial_clauses": len(part_hits),
        "participial_per_1k_words": per1k(len(part_hits)),
        "participial_examples": part_hits[:8],
        "nominalizations": len(noms),
        "nominalizations_per_100_words": round(len(noms) * 100 / n_words, 1) if n_words else 0,
        "nominalization_examples": sorted({n.lower() for n in noms})[:12],
        "tricolons": tricolons,
        "tricolons_per_1k_words": per1k(tricolons),
        "questions": questions,
    }


def stats(text):
    prose = text
    n_words = len(re.findall(r"\b\w+\b", prose))
    sents = split_sentences(prose)
    lens = [len(s.split()) for s in sents]
    em = prose.count("—")
    spaced_em = len(re.findall(r"\s—\s", prose))
    curly = len(re.findall(r"[“”‘’]", prose))
    bold = len(re.findall(r"\*\*[^*\n]+\*\*", prose))
    semis = prose.count(";")
    parens = len(re.findall(r"\([^)]{3,}\)", prose))
    colons = len(re.findall(r"\w:\s", prose))
    triplets = len(re.findall(r"\b[\w-]+(?: [\w-]+){0,3}, [\w-]+(?: [\w-]+){0,3},? (?:and|or) [\w-]+", prose))
    out = {
        "words": n_words,
        "sentences": len(lens),
        "mean_sentence_len": round(statistics.mean(lens), 1) if lens else 0,
        "stdev_sentence_len": round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
        "share_8_to_20_words": round(sum(8 <= l <= 20 for l in lens) / len(lens), 2) if lens else 0,
        "em_dashes": em,
        "spaced_em_dashes": spaced_em,
        "em_dashes_per_1k_words": round(em * 1000 / n_words, 1) if n_words else 0,
        "curly_quotes": curly,
        "bold_spans": bold,
        "bold_per_100_words": round(bold * 100 / n_words, 2) if n_words else 0,
        "semicolons": semis,
        "parentheticals": parens,
        "colons": colons,
        "x_y_and_z_lists": triplets,
    }
    out.update(grammar_measures(prose, n_words))
    return out


def stat_flags(st):
    """Turn statistics into flagged patterns (pattern, label, weight, detail)."""
    flags = []
    w = st["words"]
    if w < 80:
        return flags
    if st["em_dashes_per_1k_words"] >= 6:
        flags.append((50, "heavy em-dash use", 2, f"{st['em_dashes']} em dashes ({st['em_dashes_per_1k_words']}/1k words)"))
    if st["spaced_em_dashes"] >= 2:
        flags.append((50, "spaced em dashes", 1, f"{st['spaced_em_dashes']} ' — ' with spaces"))
    if st["sentences"] >= 8:
        variety = st["em_dashes"] + st["semicolons"] + st["parentheticals"] + st["colons"]
        if st["share_8_to_20_words"] >= 0.8 and st["stdev_sentence_len"] < 5:
            flags.append((9, "uniform 8-20 word sentences (mid-2026 signature)", 2,
                          f"{int(st['share_8_to_20_words']*100)}% of sentences in 8-20 words, stdev {st['stdev_sentence_len']}"))
        if variety == 0:
            flags.append((50, "only commas and periods (post-em-dash-ban signature)", 1,
                          "no em dashes, semicolons, colons or parentheticals at all"))
    if st["curly_quotes"] >= 2:
        flags.append((19, "curly quotes/apostrophes", 0.5, f"{st['curly_quotes']} curly quote characters"))
    if st["bold_per_100_words"] >= 1.0:
        flags.append((15, "heavy boldface", 1, f"{st['bold_spans']} bold spans ({st['bold_per_100_words']}/100 words)"))
    if st["tricolons"] >= 2 and st["tricolons_per_1k_words"] >= 6:
        flags.append((13, "frequent 'X, Y, and Z' triplets (rule of three)", 1,
                      f"{st['tricolons']} triplet lists ({st['tricolons_per_1k_words']}/1k words); "
                      "LLMs use ~2x the expert rate (Bakhshi 2026)"))
    # Research-based grammar signals (patterns 54-55 in references/research.md)
    if st["participial_clauses"] >= 2 and st["participial_per_1k_words"] >= 6:
        flags.append((54, "dense present-participle clauses (', enabling...', ', highlighting...')", 2,
                      f"{st['participial_clauses']} ({st['participial_per_1k_words']}/1k words): "
                      f"{', '.join(st['participial_examples'])}; GPT-4o uses these at 5.3x the human rate"))
    if st["nominalizations_per_100_words"] >= 10:
        flags.append((55, "very noun-heavy prose (nominalizations)", 2,
                      f"{st['nominalizations_per_100_words']}/100 words, e.g. {', '.join(st['nominalization_examples'][:6])}; "
                      "rewrite with people as subjects and verbs ('we measured' not 'the measurement of')"))
    elif st["nominalizations_per_100_words"] >= 6:
        flags.append((55, "noun-heavy prose (nominalizations)", 1,
                      f"{st['nominalizations_per_100_words']}/100 words, e.g. {', '.join(st['nominalization_examples'][:6])}; "
                      "normal for some technical genres, check against the genre"))
    return flags


def scan(raw):
    text = strip_code(raw)
    hits = []
    taken = defaultdict(list)  # pattern number -> spans already counted (avoid double-counting one phrase)
    for num, label, rx, weight in CHECKS:
        for m in re.finditer(rx, text, FLAGS | re.MULTILINE):
            s, e = m.start(), m.end()
            if num != 9 and any(s < te and ts < e for ts, te in taken[num]):
                continue
            taken[num].append((s, e))
            hits.append({"pattern": num, "label": label, "line": line_of(text, s),
                         "match": m.group(0).strip(), "context": snippet(text, s, e), "weight": weight})
    for num, label, ln, ctx, weight in style_checks(text):
        hits.append({"pattern": num, "label": label, "line": ln, "match": "", "context": ctx, "weight": weight})
    st = stats(text)
    for num, label, weight, detail in stat_flags(st):
        hits.append({"pattern": num, "label": label, "line": 0, "match": "", "context": detail, "weight": weight})

    # AI vocabulary: single hits are noise; weight clusters
    vocab = [h for h in hits if h["pattern"] == 9 and h["label"] == "AI vocabulary"]
    distinct_vocab = {h["match"].lower() for h in vocab}
    score = sum(h["weight"] for h in hits if not (h["pattern"] == 9 and h["label"] == "AI vocabulary"))
    if st["words"]:
        density = len(vocab) * 1000 / st["words"]
        score += min(len(vocab), 3) * 0.3 + max(0, len(vocab) - 3) * 1.0
    else:
        density = 0
    # floor the denominator so two words in a 50-word snippet don't read as a dense cluster
    per_1k = score * 1000 / max(st["words"], 150) if st["words"] else 0
    if per_1k >= 25 or any(h["weight"] >= 5 for h in hits):
        verdict = "several strong signs"
    elif per_1k >= 10:
        verdict = "a few signs worth fixing"
    else:
        verdict = "nothing notable"
    return {
        "verdict": verdict,
        "score": round(score, 1),
        "score_per_1k_words": round(per_1k, 1),
        "ai_vocab_hits": len(vocab),
        "ai_vocab_distinct": sorted(distinct_vocab),
        "ai_vocab_per_1k_words": round(density, 1),
        "stats": st,
        "hits": sorted(hits, key=lambda h: (h["pattern"], h["line"])),
    }


def print_report(res):
    st = res["stats"]
    print(f"Verdict: {res['verdict']}  (score {res['score']}, {res['score_per_1k_words']} per 1k words)")
    print(f"Words {st['words']} | sentences {st['sentences']} | mean len {st['mean_sentence_len']} "
          f"(stdev {st['stdev_sentence_len']}, {int(st['share_8_to_20_words']*100)}% in 8-20)")
    print(f"Em dashes {st['em_dashes']} (spaced {st['spaced_em_dashes']}) | semicolons {st['semicolons']} | "
          f"parentheticals {st['parentheticals']} | colons {st['colons']} | bold {st['bold_spans']} | curly quotes {st['curly_quotes']}")
    print(f"Grammar: participial clauses {st['participial_clauses']} ({st['participial_per_1k_words']}/1k) | "
          f"nominalizations {st['nominalizations_per_100_words']}/100 words | "
          f"X, Y and Z lists {st['tricolons']} | questions {st['questions']}")
    print(f"AI vocabulary: {res['ai_vocab_hits']} hits, {len(res['ai_vocab_distinct'])} distinct "
          f"({res['ai_vocab_per_1k_words']}/1k words): {', '.join(res['ai_vocab_distinct']) or '-'}")
    print("Reminder: these are signs, not proof. Fix by rewriting around the fact, not by swapping synonyms.\n")
    grouped = defaultdict(list)
    for h in res["hits"]:
        grouped[(h["pattern"], h["label"])].append(h)
    if not grouped:
        print("No pattern hits.")
        return
    for (num, label), hs in sorted(grouped.items()):
        print(f"[{num}] {label}: {len(hs)}")
        for h in hs[:12]:
            loc = f"L{h['line']}" if h["line"] else "--"
            m = f"'{h['match']}'  " if h["match"] else ""
            print(f"    {loc:>5}  {m}{h['context']}")
        if len(hs) > 12:
            print(f"    ... {len(hs) - 12} more")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", help="text/markdown file to scan")
    ap.add_argument("--stdin", action="store_true", help="read text from stdin")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    if args.stdin or not args.path:
        raw = sys.stdin.read()
    else:
        with open(args.path, encoding="utf-8") as f:
            raw = f.read()
    res = scan(raw)
    if args.json:
        json.dump(res, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print_report(res)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # e.g. piped into `head`
        sys.stderr.close()
