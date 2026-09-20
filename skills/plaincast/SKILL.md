---
name: plaincast
version: 1.1.0
description: >-
  Text formatting discipline. Normalizes AI output to standard keyboard
  characters only. Eliminates emoji, typographic dashes, curly quotes,
  Unicode decorative symbols, invisible characters, and colon/bullet inflation.
  Use when writing documentation, articles, news content, commit messages,
  code comments, or any text that must survive encoding pipelines, search
  indexing, copy-paste, screen readers, and version control diffs without corruption.
---

# plaincast: Text Normalization Discipline

AI models are trained on typeset books, PDFs, and professionally formatted web
pages. They naturally reproduce typographic conventions - curly quotes, em dashes,
ellipsis characters, Unicode arrows, and decorative bullets - that look correct
in rendered contexts but silently corrupt plain text pipelines.

This skill casts output into its plainest, most portable form.
The rule is simple: if a human cannot type it on a standard US keyboard in
one keystroke without a special key combination, it does not belong in the output.

---

## The Standard Keyboard Boundary

Permitted characters are exactly what appears on a US QWERTY keyboard:

- Letters: a-z, A-Z
- Digits: 0-9
- Basic punctuation: `. , : ; ! ? ' " ( ) [ ] { } / \ | @ # $ % ^ & * + = - _ ~
- Control characters in code: newline `\n`, tab `\t`
- Regular space

Everything outside this set requires explicit justification.
When in doubt, substitute. When substitution is not possible, spell it out in words.

---

## Protocol 1 - Emoji Prohibition

**Never use emoji in any output.**

Emoji are not characters. They are pictograms. They have no place in:
- Documentation (README, API docs, changelogs, wikis)
- Articles, news content, blog posts
- Code comments
- Commit messages
- Emails
- Any plain text pipeline

### Why

- Screen readers announce emoji by their CLDR name ("thumbs up sign") - noisy and disruptive
- Many CMS and legacy mail servers truncate content at the first emoji character
- Emoji above U+FFFF are 4-byte sequences that break systems expecting 3-byte max UTF-8
- Git diffs show emoji as byte sequences, inflating noise
- Ad networks, spam filters, and content classifiers penalize emoji-heavy content
- Emoji meaning is locale and platform dependent - the same emoji renders differently on iOS vs Android vs Windows

### Replacement

Never replace an emoji with another symbol. Remove it entirely.
If the intent was emphasis, use words:

<!-- plaincast:ignore-start -->
```
Wrong:  The build passed successfully! 🚀
Right:  The build passed successfully.

Wrong:  Warning: do not delete this file ⚠️
Right:  Warning: do not delete this file.

Wrong:  New feature ✨ Dark mode support
Right:  New feature: dark mode support
```
<!-- plaincast:ignore-end -->

---

## Protocol 2 - Dash Discipline

There are eight dash characters in Unicode. Only one belongs in plain text output.

| Character | Unicode | Name | Replace with |
|-----------|---------|------|-------------|
| - | U+002D | Hyphen-minus | Keep - this is the only correct dash |
| -- | (two hyphens) | Double hyphen convention | Use for em dash replacement in plain text |
| - | U+2010 | Hyphen | Replace with `-` |
| - | U+2011 | Non-breaking hyphen | Replace with `-` |
| - | U+2012 | Figure dash | Replace with `-` |
| - | U+2013 | En dash | Replace with `-` |
| - | U+2014 | Em dash | Replace with ` - ` (space hyphen space) |
| - | U+2015 | Horizontal bar | Replace with ` - ` |
| - | U+2212 | Minus sign (math) | Replace with `-` in prose; keep in code math |

### Em Dash Rule (most common violation)

The em dash (U+2014) is the character AI models generate most aggressively.
It appears after phrases like "however", "but", and "note that".

<!-- plaincast:ignore-start -->
```
Wrong:  The process completed—but with errors.
Right:  The process completed - but with errors.

Wrong:  There are three options—each with tradeoffs.
Right:  There are three options, each with tradeoffs.

Wrong:  Note: this feature is experimental—use with caution.
Right:  Note: this feature is experimental. Use with caution.
```
<!-- plaincast:ignore-end -->

**When rewriting em dashes:** prefer restructuring the sentence over mechanical
substitution. A comma, colon, period, or parentheses often reads more naturally
than ` - `.

### Range Notation

En dashes (U+2013) are used for numeric ranges. Replace with a hyphen:

<!-- plaincast:ignore-start -->
```
Wrong:  Pages 10–20
Right:  Pages 10-20

Wrong:  2020–2024
Right:  2020-2024
```
<!-- plaincast:ignore-end -->

---

## Protocol 3 - Quote Discipline

There are sixteen quote characters in Unicode. Only two belong in plain text.

| Keep | Unicode | Name |
|------|---------|------|
| `'` | U+0027 | Apostrophe / Straight single quote |
| `"` | U+0022 | Straight double quote |

### Replace all of these

| Character | Unicode | Name | Replace with |
|-----------|---------|------|-------------|
| ' | U+2018 | Left single quotation mark | `'` |
| ' | U+2019 | Right single quotation mark | `'` |
| " | U+201C | Left double quotation mark | `"` |
| " | U+201D | Right double quotation mark | `"` |
| , | U+201A | Single low-9 quotation mark | `'` |
| ,, | U+201E | Double low-9 quotation mark | `"` |
| ' | U+201B | Single high-reversed-9 quotation mark | `'` |
| " | U+201F | Double high-reversed-9 quotation mark | `"` |
| ' | U+2032 | Prime | `'` |
| " | U+2033 | Double prime | `"` |

### Context rule

In code, code blocks, and inline code: always straight quotes, no exceptions.
In prose: straight quotes throughout - do not use curly quotes even in
contexts where a style guide might permit them. Consistency beats typography here.

```
Wrong:  He said, "the function returns null."
Right:  He said, "the function returns null."

Wrong:  Don't use it.
Right:  Don't use it.
```

---

## Protocol 4 - Ellipsis Discipline

The ellipsis character (U+2026) is a single Unicode glyph that AI models use
instead of three separate periods.

<!-- plaincast:ignore-start -->
```
Wrong:  The list continues… and so on.
Right:  The list continues... and so on.

Wrong:  Loading…
Right:  Loading...
```
<!-- plaincast:ignore-end -->

**Why it matters:** The ellipsis character (U+2026) is a single token.
Grep, search indexers, and many text parsers do not match it against `...`.
It breaks word-wrap calculations in monospaced environments and is invisible
in some terminal fonts.

The two-dot leader (U+2025) has no legitimate use in plain text. Remove it.

---

## Protocol 5 - Invisible and Space Characters

These are the most dangerous non-standard characters because they are invisible
in most editors but cause real pipeline failures.

| Character | Unicode | Name | Action |
|-----------|---------|------|--------|
| (nbsp) | U+00A0 | No-break space | Replace with regular space |
| (narrow nbsp) | U+202F | Narrow no-break space | Replace with regular space |
| (thin space) | U+2009 | Thin space | Replace with regular space |
| (hair space) | U+200A | Hair space | Replace with regular space |
| (zwsp) | U+200B | Zero-width space | Remove entirely |
| (zwnj) | U+200C | Zero-width non-joiner | Remove entirely |
| (zwj) | U+200D | Zero-width joiner | Remove entirely |
| (BOM) | U+FEFF | Zero-width no-break space / BOM | Remove entirely |
| (lsep) | U+2028 | Line separator | Replace with `\n` |
| (psep) | U+2029 | Paragraph separator | Replace with `\n\n` |

**Never generate these characters.** They are produced by copy-paste from PDFs,
typeset documents, and word processors. They cause:
- Invisible line-break points that corrupt data streams
- Hidden bugs in string matching and search
- BOM at start of file breaking shebangs and script headers
- "Illegal character" errors in strict parsers

---

## Protocol 6 - Arrow and Symbol Characters

AI models use Unicode arrows, bullets, and decorative symbols as shortcuts
for readability. These are not plain text.

### Arrows - replace with ASCII equivalents

| Wrong | Right |
|-------|-------|
| -> (U+2192) | `->` |
| <- (U+2190) | `<-` |
| => (U+21D2) | `=>` |
| -> (heavy, U+2794) | `->` |
| -> (long, U+27F6) | `->` |
| ^ (U+2191 upward arrow) | `^` or the word "up" |
| v (U+2193 downward arrow) | `v` or the word "down" |

### Bullets - replace with ASCII equivalents

| Wrong | Right |
|-------|-------|
| - (U+2022 bullet) | `-` or `*` |
| o (U+25E6 white bullet) | `-` or `*` |
| > (U+2023 triangular bullet) | `-` or `>` |
| * (U+2605 star) | `*` |
| > (U+25B6 right-pointing triangle) | `>` |

### Check marks and crosses - use words

| Wrong | Right |
|-------|-------|
| - (U+2713 check mark) | `[x]` or "yes" or "done" |
| x (U+2717 ballot x) | `[ ]` or "no" or "fail" |
| - (U+2714 heavy check mark) | `[x]` |
| x (U+2718 heavy ballot x) | `[ ]` |

### Other common symbols

| Wrong | Right |
|-------|-------|
| ... (U+2026 ellipsis) | `...` |
| (TM) (U+2122 trademark) | `(TM)` or `(tm)` |
| (C) (U+00A9 copyright) | `(c)` or `Copyright` |
| (R) (U+00AE registered) | `(R)` |
| deg (U+00B0 degree) | `deg` or spell out "degrees" |
| x (U+00D7 multiplication) | `x` or `*` |
| / (U+00F7 division) | `/` |
| != (U+2260 not equal) | `!=` |
| >= (U+2265 greater than or equal) | `>=` |
| <= (U+2264 less than or equal) | `<=` |
| +/- (U+00B1 plus-minus) | `+/-` |

---

## Protocol 7 - Heading and Structure Discipline

These are formatting patterns, not character issues, but they degrade plain
text output in the same way.

### Heading hierarchy

Use markdown heading levels only when:
- The output is explicitly markdown
- The content has genuine hierarchical sections (not just 3 short paragraphs)
- Do not use H4 or H5 - if nesting goes that deep, restructure the content

### Bold and italic abuse

```
Wrong:  The **most important** thing to **remember** is that you **must** always...
Right:  The most important thing to remember is that you must always...
```

Bold is for genuinely critical terms and UI labels, not emphasis inflation.
Italic is for titles, technical terms on first use, and genuine emphasis.
Both become noise when overused.

### All-caps

NEVER write words in all caps for emphasis. Write them normally or restructure
the sentence to convey importance through position and wording.

```
Wrong:  NEVER delete this file manually.
Right:  Do not delete this file manually. Deleting it manually will corrupt the database.
```

---

## Protocol 8 - Numerals and Units

### Number formatting

Use plain digits and ASCII separators:

```
Wrong:  1,000,000 (using unicode thin-space or nbsp as thousands separator)
Right:  1,000,000 (using ASCII comma)
Right:  1000000 (no separator for numbers in code contexts)
```

### Units

Spell out or use standard ASCII abbreviations:

```
Wrong:  100 deg (U+00B0) C
Right:  100 degrees C
Right:  100C (in code or compact contexts)

Wrong:  5 x 10^3 (U+00D7 multiplication sign)
Right:  5 * 10^3
Right:  5e3
```

---

## Protocol 9 - Punctuation Density & List Restraint

### Colon and Semicolon Density Gate

Models often over-index on colons (`:`) and semicolons (`;`) to attach
additive thoughts, explanations, or subordinate clauses without committing
to a new sentence.

- Limit colons in prose: use a colon only when introducing a formal code block,
  definition, or verbatim quote.
- If a sentence ends in a colon leading to a one-line thought, split into
  two sentences ending with periods.
- Semicolons should be rare in technical documentation. If two clauses can
  stand alone, use a period.

### Bold-First List Monotony

Never default to generating vertical lists where every single bullet begins
with bolded text followed by a colon:
- Wrong:
  - **Scalability:** Handles large user loads effortlessly.
  - **Reliability:** Built with automatic failover mechanisms.
  - **Maintainability:** Modular architecture ensures easy updates.
- Right: Prefer running technical prose that explains relationships, or
  simple unbolded bullet points when listing discrete items.

---

## Quick Self-Check Before Output

Run this mental scan before finalizing any prose output:

- [ ] Any emoji? Remove them
- [ ] Any em dash (-)? Replace with ` - ` or restructure
- [ ] Any curly quotes (" " ' ')? Replace with `"` and `'`
- [ ] Any Unicode ellipsis (...)? Replace with `...`
- [ ] Any Unicode arrows (->, <-, =>)? Replace with ASCII
- [ ] Any Unicode bullets or check marks? Replace with `- * > [x] [ ]`
- [ ] Any bold used more than twice per paragraph? Reduce
- [ ] Any ALL CAPS word? Rewrite
- [ ] Any non-breaking or invisible spaces? Remove

If 3 or more of these trigger, rewrite from the top.

---

## When Non-Standard Characters ARE Acceptable

This skill is not absolutist. There are legitimate exceptions:

| Exception | When allowed |
|-----------|-------------|
| Curly quotes | Only in explicitly typeset/print contexts (a PDF, a book manuscript) |
| Math symbols | Only inside LaTeX blocks or in content explicitly about mathematics |
| Unicode arrows | Only in rendered diagram tools (Mermaid, PlantUML) never in prose |
| Degree symbol | Acceptable in scientific content when space is constrained |
| Copyright/trademark | In formal legal or branding contexts where the symbol is required |
| Non-ASCII in code | Legitimate identifiers, string literals containing user-facing text |

The activation condition: the non-standard character must have no
functional ASCII substitute AND the output format explicitly supports it.

---

## References

- [Character Taxonomy](./references/character-taxonomy.md) - Full Unicode character list with replacements
- [Why It Matters](./references/why-it-matters.md) - Real pipeline failures caused by non-standard characters
- [Style Guide Comparison](./references/style-guide-comparison.md) - AP, Chicago, Microsoft, Google positions

