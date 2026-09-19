# Why It Matters - Real Pipeline Failures from Non-Standard Characters

Concrete failures caused by non-standard Unicode characters in each context.
Use this to justify the plaincast discipline to skeptical teams.

---

## Technical Documentation (README, API docs, wikis)

| Failure | Cause | Example |
|---------|-------|---------|
| Markdown mis-parsed | Em dash or smart quote breaks token boundary | `Run the command "make build"` - curly quotes make the HTML encode as `&ldquo;`; the copy-pasted command fails with "command not found" |
| Shell command broken | En dash in code block | `curl -X POST https://api.example.com --data` with U+2013 before `data` - the command fails silently |
| Search returns no results | Unicode hyphen U+2011 in identifier | `My-Function` not found because source has `My-Function` with non-breaking hyphen |
| Git diff inflated | Unicode replacement creates byte-level diff | A "typo fix" shows 20 lines changed because quotes were normalized differently per branch |

## Journalism and News

| Failure | Cause | Example |
|---------|-------|---------|
| CMS truncates article | Emoji at 4-byte codepoint | Article body with emoji truncated at that point; story publishes incomplete |
| RSS feed shows garbage | Em dash in headline | `Mayor's "Bold" Plan - A New Vision` shows as `Mayor's ?Bold? Plan ? A New Vision` in RSS aggregators |
| SEO penalty | Em dash creates different search token | "climate-change" with Unicode dash never matches the query "climate change" |
| Legal citation mismatch | Curly quote in citation | Automated citation checker flags mismatch; requires manual correction |

## Blog Posts and Web Content

| Failure | Cause | Example |
|---------|-------|---------|
| Rendering glitch on old Android | Em dash not supported | Paragraph shows U+FFFD replacement character on Android < 5 WebView |
| Comment system double-escapes | Non-ASCII in third-party widget | "I'm excited - really!" becomes "I'm excited&amp;#x2014;really!" in Disqus |
| Tweet truncated unexpectedly | Emoji counted as 2 codepoints | Excerpt with emoji exceeds 280-char limit by 2-3 characters |
| Ad network rejection | Emoji in content | Page with thumbs-up emoji rejected by ad server for policy violation |

## Code Comments and Commit Messages

| Failure | Cause | Example |
|---------|-------|---------|
| Compiler syntax error | En dash in comment treated as identifier | Rust comment `// TODO - handle overflow` with U+2013 causes unexpected token error |
| `git log --grep` returns nothing | Em dash in commit message | Message `refactor - improve` with em dash not matched by `--grep="refactor"` |
| CI log loses context | Non-ASCII stripped by Jenkins | Build step prints rocket emoji; log shows `? Build succeeded` |
| JIRA import broken | Curly quote breaks markdown parser | Description displays stray `<p>` tags; quote shown as `â€œ` |

## Internationalization (i18n) Pipelines

| Failure | Cause | Example |
|---------|-------|---------|
| Translation file import fails | Em dash in ISO-8859-1 pipeline | `.po` file rejects 0xE2 0x80 0x94 bytes; release halted |
| Dropdown sort broken | Em dash alters collation | Product "Cafe-" sorts after "Z" because trailing em dash is a different character |
| Font fallback shows boxes | Curly quote missing from console font | CLI tool output shows `?Error:` instead of `"Error:"` |
| Duplicate translation entries | Emoji combined sequence split | Same emoji appears twice in translation memory; doubles cost |

## Search Engine Indexing

| Failure | Cause | Example |
|---------|-------|---------|
| Page not found for target keyword | Em dash merges two words into one token | "high-performance" with Unicode hyphen indexed as single token; "high performance" query gets no hits |
| Ugly URL slug | Smart quote in heading | Heading with curly quote generates slug `what%E2%80%99s-new` |
| Duplicate content penalty | Different quote types create different URLs | `/guide/using-quotes` vs `/guide/using-quotes` treated as separate pages |
| Rich snippet dropped | Non-ASCII in JSON-LD | Smart quote inside JSON-LD string breaks parser; author markup removed from SERP |

## Accessibility and Screen Readers

| Failure | Cause | Example |
|---------|-------|---------|
| Awkward pause breaks reading flow | Em dash announced as "dash dash dash" | "The study - conducted over five years - shows" loses the intended rhythm |
| Confusing quote announcements | Smart quotes announced as "open quote" / "close quote" | Blind users hear "He said, open quote Hello close quote" |
| Emoji overloads the reading | Every emoji announced by CLDR name | News headline ending with alert emoji causes a long spoken pause |
| Focus order breaks | Non-breaking space breaks line-wrap | Bullet list appears as one long line; keyboard navigation skips it |

## Version Control (git diff)

| Failure | Cause | Example |
|---------|-------|---------|
| Entire line shows as changed | Smart quote substitution | `-printf("Hello");` `+printf("Hello");` - one quote changed, whole line marked different |
| False merge conflict | Two branches normalize differently | Branch A: `speed-up` (U+2011) vs Branch B: `speed-up` (U+002D) = unresolvable conflict |
| Patch apply fails | Non-UTF-8 byte in patch | Release script patching README fails with `error: patch does not apply` |
| Blame mis-attribution | Unicode character adds bytes | Re-typed paragraph attributes credit to latest editor, not original author |

## Plain Text Email

| Failure | Cause | Example |
|---------|-------|---------|
| Email rejected by server | Em dash in 7-bit ASCII gateway | Notification email silently dropped; recipient never notified |
| Mobile renders garbage | Curly quote unknown to older mail client | Bug report email shows garbled quote on recipient's phone |
| Spam filter flags content | Non-ASCII raises suspicion score | Legitimate newsletter flagged as spam due to decorative Unicode |
| SMTP 8-bit restriction | Any byte > 0x7F in legacy mail server | Email truncated at first non-ASCII character |

## Database Storage

| Failure | Cause | Example |
|---------|-------|---------|
| Encoding mismatch on insert | Em dash in Latin-1 column | `INSERT` fails with "Incorrect string value" for U+2014 in utf8 (3-byte) column |
| Unique constraint violated | Two "identical" strings differ by quote type | Same product name with different quotes creates two records; duplicates appear in UI |
| Index miss on search | Unicode character not matched by ASCII-only collation | Full-text search for the product name returns nothing |
| Storage inflation | Multi-byte Unicode in VARCHAR(255) counts bytes not chars | Field truncated because 255 bytes < 255 characters when Unicode present |
