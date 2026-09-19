# Character Taxonomy - Full Non-Standard Unicode Reference

Every character AI models commonly generate that does not appear on a standard
US QWERTY keyboard. Organized by category with replacements.

---

## Dashes (8 variants, only hyphen-minus is standard)

| Char | U+ | Name | Replace with | Notes |
|------|----|------|-------------|-------|
| - | 002D | Hyphen-minus | Keep | The only correct dash |
| - | 2010 | Hyphen | `-` | Looks identical, different byte |
| - | 2011 | Non-breaking hyphen | `-` | Prevents line break - invisible trap |
| - | 2012 | Figure dash | `-` | Same width as digits |
| - | 2013 | En dash | `-` | Used for ranges |
| - | 2014 | Em dash | ` - ` | Most common AI violation |
| - | 2015 | Horizontal bar | ` - ` | Rare variant of em dash |
| - | 2212 | Minus sign | `-` | Math symbol, not a dash |

## Quotes (16 variants, only 2 are standard)

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| ' | 0027 | Apostrophe / Straight single | Keep |
| " | 0022 | Quotation mark / Straight double | Keep |
| ' | 2018 | Left single quotation mark | `'` |
| ' | 2019 | Right single quotation mark | `'` |
| " | 201C | Left double quotation mark | `"` |
| " | 201D | Right double quotation mark | `"` |
| , | 201A | Single low-9 quotation mark | `'` |
| " | 201E | Double low-9 quotation mark | `"` |
| ' | 201B | Single high-reversed-9 quotation mark | `'` |
| " | 201F | Double high-reversed-9 quotation mark | `"` |
| ' | 2032 | Prime | `'` |
| " | 2033 | Double prime | `"` |
| ''' | 2034 | Triple prime | `'''` |
| ' | 2035 | Reversed prime | `'` |
| " | 2036 | Reversed double prime | `"` |
| ''' | 2037 | Reversed triple prime | `'''` |

## Ellipsis

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| ... | 2026 | Horizontal ellipsis | `...` |
| .. | 2025 | Two dot leader | `..` |
| ... | 22EF | Midline horizontal ellipsis | `...` |

## Spaces and Invisible Characters

| Char | U+ | Name | Action |
|------|----|------|--------|
| (nbsp) | 00A0 | No-break space | Replace with space |
| (nbsp narrow) | 202F | Narrow no-break space | Replace with space |
| (thin) | 2009 | Thin space | Replace with space |
| (hair) | 200A | Hair space | Replace with space |
| (zwsp) | 200B | Zero-width space | Remove |
| (zwnj) | 200C | Zero-width non-joiner | Remove |
| (zwj) | 200D | Zero-width joiner | Remove |
| (BOM) | FEFF | BOM / Zero-width no-break space | Remove |
| (lsep) | 2028 | Line separator | Replace with `\n` |
| (psep) | 2029 | Paragraph separator | Replace with `\n\n` |

## Arrows

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| -> | 2192 | Rightwards arrow | `->` |
| <- | 2190 | Leftwards arrow | `<-` |
| ^ | 2191 | Upwards arrow | `^` or "up" |
| v | 2193 | Downwards arrow | `v` or "down" |
| <-> | 2194 | Left-right arrow | `<->` |
| => | 21D2 | Rightwards double arrow | `=>` |
| <= | 21D0 | Leftwards double arrow | `<=` |
| <=> | 21D4 | Left-right double arrow | `<=>` |
| --> | 27F6 | Long rightwards arrow | `->` |
| ->| | 21A6 | Rightwards arrow from bar | `->` |
| -> (heavy) | 2794 | Heavy rightwards arrow | `->` |

## Bullets and List Markers

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| * | 2022 | Bullet | `-` or `*` |
| o | 25E6 | White bullet | `-` or `*` |
| > | 2023 | Triangular bullet | `>` |
| * | 2605 | Black star | `*` |
| * | 2606 | White star | `*` |
| > | 25B6 | Black right-pointing triangle | `>` |
| > | 25BA | Black right-pointing pointer | `>` |
| - | 2043 | Hyphen bullet | `-` |

## Check Marks and Crosses

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| [x] | 2713 | Check mark | `[x]` or "yes" |
| [ ] | 2717 | Ballot x | `[ ]` or "no" |
| [x] | 2714 | Heavy check mark | `[x]` |
| [ ] | 2718 | Heavy ballot x | `[ ]` |
| [x] | 2705 | White heavy check mark (emoji) | `[x]` |
| [ ] | 274C | Cross mark (emoji) | `[ ]` |

## Math and Technical Symbols

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| != | 2260 | Not equal to | `!=` |
| >= | 2265 | Greater than or equal to | `>=` |
| <= | 2264 | Less than or equal to | `<=` |
| ~= | 2248 | Almost equal to | `~=` or "approximately" |
| +/- | 00B1 | Plus-minus sign | `+/-` |
| x | 00D7 | Multiplication sign | `x` or `*` |
| / | 00F7 | Division sign | `/` |
| 1/2 | 00BD | Vulgar fraction one half | `1/2` |
| 1/4 | 00BC | Vulgar fraction one quarter | `1/4` |
| 3/4 | 00BE | Vulgar fraction three quarters | `3/4` |
| ^ | 00B2 | Superscript two | `^2` |
| ^ | 00B3 | Superscript three | `^3` |
| sqrt | 221A | Square root | `sqrt()` |
| inf | 221E | Infinity | "infinity" |
| pi | 03C0 | Greek small letter pi | "pi" or `PI` |
| sum | 2211 | N-ary summation | "sum" |

## Typographic Symbols

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| (C) | 00A9 | Copyright sign | `(c)` or "Copyright" |
| (R) | 00AE | Registered sign | `(R)` |
| (TM) | 2122 | Trade mark sign | `(TM)` |
| deg | 00B0 | Degree sign | `deg` or "degrees" |
| ' | 00B4 | Acute accent | `'` |
| * | 00B7 | Middle dot | `*` or `.` |
| # | 00A7 | Section sign | "#" or "Section" |
| P | 00B6 | Pilcrow (paragraph) | Remove or "paragraph" |
| ... | 2026 | Ellipsis | `...` |

## Ligatures (generated from OCR or typeset source)

| Char | U+ | Name | Replace with |
|------|----|------|-------------|
| fi | FB01 | Latin small ligature fi | `fi` |
| fl | FB02 | Latin small ligature fl | `fl` |
| ff | FB00 | Latin small ligature ff | `ff` |
| ffi | FB03 | Latin small ligature ffi | `ffi` |
| ffl | FB04 | Latin small ligature ffl | `ffl` |

---

## Detection Reference (Byte Sequences)

The five most common violations and their UTF-8 byte sequences for grep/regex:

| Character | UTF-8 bytes | Regex pattern |
|-----------|-------------|---------------|
| Em dash | E2 80 94 | `\xe2\x80\x94` or `\u2014` |
| Left double quote | E2 80 9C | `\xe2\x80\x9c` or `\u201c` |
| Right double quote | E2 80 9D | `\xe2\x80\x9d` or `\u201d` |
| Right single quote | E2 80 99 | `\xe2\x80\x99` or `\u2019` |
| Ellipsis | E2 80 A6 | `\xe2\x80\xa6` or `\u2026` |
| No-break space | C2 A0 | `\xc2\xa0` or `\u00a0` |
| Zero-width space | E2 80 8B | `\xe2\x80\x8b` or `\u200b` |

## Quick Normalization Script (Python)

```python
import re

REPLACEMENTS = [
    # Em and en dashes
    ('\u2014', ' - '),   # em dash
    ('\u2013', '-'),     # en dash
    ('\u2012', '-'),     # figure dash
    ('\u2011', '-'),     # non-breaking hyphen
    ('\u2010', '-'),     # hyphen
    ('\u2212', '-'),     # minus sign
    # Quotes
    ('\u2018', "'"),     # left single
    ('\u2019', "'"),     # right single
    ('\u201c', '"'),     # left double
    ('\u201d', '"'),     # right double
    ('\u201a', "'"),     # single low-9
    ('\u201e', '"'),     # double low-9
    ('\u2032', "'"),     # prime
    ('\u2033', '"'),     # double prime
    # Ellipsis
    ('\u2026', '...'),
    ('\u2025', '..'),
    # Spaces
    ('\u00a0', ' '),     # nbsp
    ('\u202f', ' '),     # narrow nbsp
    ('\u2009', ' '),     # thin space
    ('\u200a', ' '),     # hair space
    ('\u200b', ''),      # zero-width space
    ('\u200c', ''),      # zero-width non-joiner
    ('\u200d', ''),      # zero-width joiner
    ('\ufeff', ''),      # BOM
    # Arrows
    ('\u2192', '->'),
    ('\u2190', '<-'),
    ('\u21d2', '=>'),
    ('\u2794', '->'),
    # Bullets
    ('\u2022', '-'),
    ('\u2023', '>'),
    ('\u2605', '*'),
    # Marks
    ('\u2713', '[x]'),
    ('\u2717', '[ ]'),
    ('\u2714', '[x]'),
    ('\u2718', '[ ]'),
    # Typographic
    ('\u00a9', '(c)'),
    ('\u00ae', '(R)'),
    ('\u2122', '(TM)'),
    ('\u00b0', 'deg'),
    ('\u00d7', 'x'),
    ('\u00f7', '/'),
    ('\u00b1', '+/-'),
]

def normalize(text: str) -> str:
    # Remove emoji (all chars above U+FFFF via surrogates, plus emoji ranges)
    text = re.sub(
        '['
        '\U00010000-\U0010ffff'  # Supplementary planes (most emoji)
        '\u2600-\u27BF'          # Misc symbols and dingbats
        '\uFE00-\uFE0F'          # Variation selectors
        ']',
        '', text
    )
    for src, dst in REPLACEMENTS:
        text = text.replace(src, dst)
    return text
```
