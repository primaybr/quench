# Style Guide Comparison

How major writing style guides handle non-standard characters.
Used as reference for the plaincast skill.

---

## At a Glance

| Character | AP Style | Chicago (CMOS) | Microsoft Writing | Google Dev |
|-----------|----------|----------------|-------------------|------------|
| Em dash (U+2014) | Use, no spaces | Use, no spaces | Avoid - use comma/colon/parens | Avoid in code; limited in prose |
| En dash (U+2013) | Use for ranges | Use for ranges and pairs | Use for ranges | Use for ranges |
| Ellipsis (U+2026) | Three periods with spaces: `. . .` | Ellipsis symbol `...` | Ellipsis symbol `...` | Ellipsis symbol `...` |
| Curly quotes | Required in prose | Required in prose | Straight in UI/code; curly in body | Straight quotes strongly preferred |
| Emoji | Not addressed | Not addressed | Not in technical content | Not in technical content |
| Non-breaking space | Not addressed | Not addressed | Avoid, use regular space | Not addressed |
| Unicode symbols | Not addressed | Not addressed | Discouraged; ASCII preferred | Discouraged; UTF-8 for content |

---

## AP Stylebook

**Target audience:** Journalists, news writers.
**Authority level:** Standard for North American news media.

### Dashes
- Em dash: Use with no surrounding spaces. "The committee - all five members - voted yes." 
  Wait: AP changed guidance in 2019 to allow spaces around em dashes for readability.
  Current: "The committee - all five members - voted yes." (spaces OK)
- En dash: Use for ranges. "Pages 1-10." (AP uses hyphen-minus, not en dash)
- Hyphen: Standard use for compound modifiers before a noun.

### Quotes
- Opening and closing quotation marks should be typographic (curly) in published text.
- Apostrophes should be right single quotation mark (curly).
- In practice: AP wire copy uses straight quotes for transmission compatibility;
  final published versions use curly quotes.

### ellipsis
- Use three periods with a space before each: ` . . .`
- This is unusual - most other guides use `...` without spaces.

### plaincast verdict on AP
AP was designed for human journalists, not AI agents. Its guidelines assume
human typesetting and editorial processes that include a final copy-editing step.
For AI-generated content going directly into pipelines, apply the stricter
plaincast standard over AP conventions.

---

## Chicago Manual of Style (CMOS)

**Target audience:** Book publishers, academic writers.
**Authority level:** Standard for book publishing and academic journals.

### Dashes
- Em dash: Preferred for strong breaks. No spaces. "The cat - a tabby - sat down."
- En dash: For ranges, connections. "the Chicago-New York flight", "pages 1-10"
- Hyphen: Compound adjectives, word division.

### Quotes
- Curly/smart quotes required in all published prose.
- Straight quotes only in code samples and technical content.

### Ellipsis
- Three dots with spaces: ". . ." (within a sentence)
- ". . . ." (when end of sentence is omitted)

### plaincast verdict on CMOS
CMOS is the least compatible guide with plaincast. It was designed for
professionally typeset books where curly quotes and em dashes are rendered
correctly by the printing system. These conventions do not survive plain
text pipelines, email, or technical tooling.

---

## Microsoft Writing Style Guide

**Target audience:** Technical writers, software documentation teams.
**Authority level:** Standard for Microsoft products and widely adopted in tech.
**Available free at:** docs.microsoft.com/style-guide

### Dashes
- Em dash: **Actively discouraged.** Replace with comma, colon, or parentheses.
  "The tool (version 3.x) supports Windows" not "The tool - version 3.x - supports Windows"
- En dash: For ranges only. No spaces.
- Hyphen: Standard compound modifiers.

### Quotes
- Straight quotes in UI text, code, command-line content: always.
- Curly quotes in body copy: acceptable but not required.
- Recommendation: be consistent. Straight quotes everywhere is safer for localization.

### Emoji
- Not recommended in technical documentation.
- Exception: if documenting an interface that uses emoji, show them.

### Non-standard Unicode
- Avoid decorative Unicode symbols.
- Use ASCII alternatives where they exist.

### plaincast verdict on Microsoft
The Microsoft Writing Style Guide is the most aligned with plaincast principles.
Its advice on em dashes, quote consistency, and Unicode restraint directly
supports AI output normalization. Use it as the authority when justification
is needed.

---

## Google Developer Documentation Style Guide

**Target audience:** Developers writing technical docs, API references.
**Authority level:** Standard for Google developer content and widely adopted.
**Available free at:** developers.google.com/style

### Dashes
- Em dash: Acceptable in prose but prefer commas or restructure the sentence.
- En dash: For ranges.
- Hyphen: Standard use.

### Quotes
- **Straight double quotes strongly recommended** for code, commands, UI text.
- Smart/curly quotes cause encoding issues in code contexts.
- Consistent straight quotes throughout a document is preferred over mixing.

### Emoji
- Not addressed directly but implicitly excluded from technical content.
- "Don't use cute language" in documentation.

### Symbols
- Avoid decorative Unicode symbols.
- Use UTF-8 encoding for content but prefer ASCII characters where they suffice.

### Links and identifiers
- Keep identifiers, slugs, and URLs ASCII-only.
- Non-ASCII in URLs requires percent-encoding which hurts readability.

### plaincast verdict on Google Dev Style Guide
Second most aligned with plaincast after Microsoft. Its strong stance on
straight quotes and restraint around decorative symbols directly supports
the plaincast goal. For developer-facing content, follow Google's guide
as the minimum standard and plaincast as the hardened version.

---

## Summary: What the Guides Agree On

All four major style guides agree on these points:

1. En dashes are acceptable for ranges (but a hyphen-minus is an acceptable
   substitute that works in all contexts)
2. Straight quotes are preferred or required in code and technical content
3. Decorative Unicode symbols are discouraged in technical writing
4. Emoji have no place in professional technical documentation

The disagreements (em dash in prose, curly vs. straight quotes in body copy)
are all resolved in plaincast by defaulting to the more portable option.

**plaincast rule:** When style guides disagree, the most portable, ASCII-compatible
option wins. Technical correctness beats typographic elegance.
