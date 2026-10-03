# plaincast - Text Normalization
# quench | Source: skills/plaincast/SKILL.md

NEVER use emoji - remove entirely, never replace with other symbols.
NEVER use em dash (U+2014) - use " - " or restructure with comma/colon/period.
NEVER use curly/smart quotes or curly apostrophes (U+2018 U+2019 U+201C U+201D) - for all quotes, apostrophes, and contractions (it's, don't, user's), strictly use ASCII single quote ' (0x27) and ASCII double quote " (0x22).
NEVER use Unicode ellipsis (U+2026) - use three periods ... instead.
NEVER use Unicode arrows in prose - use -> <- => instead.
NEVER use Unicode bullets (U+2022) - use - or * instead.
NEVER use Unicode check marks - use [x] and [ ] instead.
NEVER use en dash (U+2013) or non-breaking hyphen (U+2011) anywhere - use plain hyphen-minus '-' (0x2D) for all hyphens, compound words, ranges, and list markers.
NEVER write words in ALL CAPS for emphasis - restructure the sentence.
Remove invisible characters: U+200B U+200C U+200D U+00A0 U+FEFF.
Do not overuse bold - max two bolded phrases per paragraph.
Avoid bold-first list spam (**Key:** Value on every line). Use prose or plain bullets.
Limit colons in prose to formal definitions; keep semicolons rare.
