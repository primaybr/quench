# plaincast - Text Normalization
# quench | Source: skills/plaincast/SKILL.md

NEVER use emoji in any output - remove entirely, never replace with other symbols.

NEVER use the em dash character (U+2014). Replace with:
- " - " (space-hyphen-space) as a direct substitute
- a comma, colon, period, or parentheses when restructuring reads better

NEVER use curly/smart quotes (U+2018 U+2019 U+201C U+201D).
Use straight apostrophe ' (U+0027) and straight double quote " (U+0022) everywhere.

NEVER use the Unicode ellipsis character (U+2026). Use three periods ... instead.

NEVER use Unicode arrows in prose. Use ASCII: -> <- => <-.
NEVER use Unicode bullets (U+2022) in prose. Use - or * instead.
NEVER use Unicode check marks or ballot boxes. Use [x] and [ ] instead.

NEVER use en dash (U+2013) for ranges. Use a plain hyphen: 2020-2024.

NEVER write words in ALL CAPS for emphasis. Restructure the sentence instead.

Remove invisible characters entirely:
- Zero-width space U+200B, zero-width non-joiner U+200C, zero-width joiner U+200D
- No-break space U+00A0 - replace with regular space
- BOM U+FEFF - remove entirely

Do not overuse bold. More than two bolded phrases per paragraph is inflation.
