# CHANGELOG

All notable changes to quench are documented here.
Format: [version] date - description

## [1.9.0] 2026-09-24 - Opt-In Verified Auto-Update, Git-Aware Line Endings & Scrubbed History

### Security
- **Auto-update is opt-in:** `quench update --global` no longer installs the SessionStart hook by default; `--auto-update` opts in and `--no-auto-update` removes it (a re-run with neither keeps the current state, so 1.8.0 installs keep their hook). The clone supplies the always-on rules and its `quench.py` runs at session start, so enabling it means trusting every future release.
- **Auto-update never downgrades and only installs releases:** The hook installs a commit only if it carries a `vX.Y.Z` tag and is not older than the installed release. The installed version is recorded in the clone, so the check holds even if tags are re-pointed. Each update prints the old and new release, the commit range and a GitHub compare link.
- **Scrubbed history:** A private tool name, a private folder name and machine identifiers (a Windows user folder, a user name and a local dev path, used as test data) were replaced with fictional values throughout the git history, so every published commit and tag has new SHAs; tag names and releases are unchanged. The current test fixtures use the same fictional values.
- **Release workflow split by permission:** `release.yml` verifies and tests in a read-only job; only the `publish` job, which `needs` it, gets `contents: write`.

### Fixed
- **CRLF false positives on Windows checkouts:** In a git work tree the hygiene gate now reads `git ls-files --eol`. It reports CRLF only if it is already committed (`i/crlf`, `i/mixed`) or would be committed (no `text` attribute, no `core.autocrlf`, or `-text`). CRLF that exists only in a working copy that git normalizes on commit is no longer reported; on a real repository with `core.autocrlf=true` this removed about 639 false positives. Outside git, the working-tree bytes still decide.
- **CIDR ranges flagged as private hosts:** A network address with a prefix (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.1.0/24`), as used in SSRF guards and firewall rules, is no longer reported. Hosts still are, including a host address written with a prefix (last octet not 0).
- **`v1` could move backwards:** Pushing an older-line tag (for example `v1.6.4` after `v1.8.0`) no longer moves `v1` or marks the release Latest; `scripts/release_notes.py --is-newest` decides, with numeric version ordering.
- **Placeholder commit messages:** The commit-msg hook rejects a subject with fewer than 3 letters or digits (such as `...`).

### Changed
- **Node.js 24 actions:** `actions/checkout@v7` and `actions/setup-python@v7` in `action.yml` and both workflows, which removes GitHub's Node.js 20 deprecation warning for the Action's users.

## [1.8.0] 2026-09-24 - Automatic Releases & Self-Updating Global Install

### Added
- **Automatic releases:** `.github/workflows/release.yml` runs when a `vX.Y.Z` tag is pushed. It checks the tag against the `pyproject.toml` version and requires a matching `CHANGELOG.md` section (`scripts/release_notes.py`, 9 tests in `scripts/test_release_notes.py`), runs the full test suite, moves the floating major tag (`v1`) to the release commit, and publishes the GitHub Release with that section as notes. An optional `- Title` after the date in the section heading becomes the release title. An existing release for the tag is left unchanged.
- **Automatic updates for `quench update --global`:** The command now also installs a Claude Code `SessionStart` hook in `~/.claude/settings.json`. At session start it checks at most once a day (`QUENCH_AUTO_UPDATE_INTERVAL` seconds to change) whether the followed tag moved and updates the clone, printing one line only when a new release was installed. It uses a 20-second fetch timeout, never prompts for credentials, always exits 0 so a session is never blocked, and skips a clone with local edits. Other settings and hooks are preserved, and an unparseable `settings.json` is left unchanged. `--no-auto-update` removes the hook. The hook is not installed, and any existing one is removed, when the checked-out release does not support it, because an older CLI would reject the hook's arguments with exit code 2, which blocks sessions. Covered by 8 new tests in `scripts/test_update_global.py` (21 in total).

### Changed
- **Repo invariants (`AGENTS.md`):** Documents the tag-driven release process and that `v1` is moved only by the release workflow.

## [1.7.0] 2026-09-24

### Fixed
- **Repo-only invariants shipped to users:** The "Repository & Ecosystem Invariants" section (adapter parity, skill version bumps, CHANGELOG updates) was part of `rules/AGENTS.md` and the Antigravity adapter, so `quench init` copied quench's own maintenance rules into user projects. It now lives in a new root `AGENTS.md` that is not shipped; the repo's `CLAUDE.md` imports it and Kilo loads it automatically.

### Added
- **`quench update --global`:** Keeps a stable clone (default `~/.quench`, or `$QUENCH_HOME` / `--home`) on the `v1` tag, so it follows the latest 1.x release rather than `master`, and wires it into Claude Code: an import of `rules/AGENTS.md` in `~/.claude/CLAUDE.md` and one link per skill in `~/.claude/skills/` (a symlink, or a junction on Windows). Safe to re-run: existing `CLAUDE.md` content, an import from another clone, real skill folders and links to other clones are left unchanged, and a clone with local edits is refused. `--ref` pins another tag, `--no-claude` updates the clone only, `--claude-dir` (or `$CLAUDE_CONFIG_DIR`) targets another config dir. Covered by `scripts/test_update_global.py` (13 tests, run in CI). Imports under the user's home are written as `@~/...`, which keeps spaces in the user folder name (common on Windows) out of the import line, and the command reports the exact release (`v1.7.0`), not the floating `v1` tag.
- **README: Claude Code global setup:** Recommends `quench update --global` (release-following) for users, and documents pointing `~/.claude` at a working clone for people developing quench.

## [1.6.3] 2026-09-24

### Added
- **Dogfooding - agent rules:** The repo root now has a `CLAUDE.md` (Claude Code) that imports `rules/AGENTS.md` with `@rules/AGENTS.md`, and a `kilo.jsonc` (Kilo) whose `instructions` point at `rules/AGENTS.md`. Both read the rules live, so rule edits apply to the next session with no copy to refresh, the same way the Antigravity plugin entry reads the repo directly.
- **Dogfooding - CI runs the published Action:** `validate.yml` now runs `uses: ./` on the repo (must pass) and on a fixture containing a configured private term (must fail), so `action.yml` and its `private-terms` input are tested end to end.

### Changed
- **`quench init` / `quench update` refuse the quench source repo:** Run on the source repo itself, they would overwrite the live `CLAUDE.md` / `kilo.jsonc` with stale adapter copies. They now exit with an explanation.
- **`.gitignore`:** Ignores `CLAUDE.local.md`, Claude Code's per-user instruction file, so personal instructions are never committed next to the shared `CLAUDE.md`.

## [1.6.2] 2026-09-24

### Fixed
- **`--fix` corrupted code files:** `--fix` now rewrites only prose files (`.md`, `.mdc`, `.mdx`, `.txt`, `.rst`, `.adoc`, `.cursorrules`, `.windsurfrules`). Violations in code and config files are still reported, and listed at the end of the run as left for manual fixing. Previously it replaced characters in UI strings (copyright signs, emoji in labels) and rewrote web routes.
- **Unix home pattern matched web routes and URLs:** The pattern is now case-sensitive and must start a path token, so `/users/42/orders` and `https://example.com/Users/alice/profile` no longer match.
- **Path auto-fix ate the next character:** Path matches no longer consume the first character of the following segment. The fix now replaces the whole path token by its span, so no user name survives and no neighbouring text is removed.
- **Plaincast auto-fix spacing:** A spaced em dash no longer becomes a double-spaced ` - `, and removing an emoji no longer leaves doubled or trailing spaces.
- **Scanning ignored `.gitignore`:** In a git work tree the file list now comes from `git ls-files --cached --others --exclude-standard`, so build output, `vendor/` and other ignored folders are skipped. Outside git, `vendor`, `build`, `dist`, `out`, `target`, `.next`, `.nuxt`, `.dart_tool`, `.gradle`, `.venv` and `coverage` are skipped.
- **One path reported up to three times:** Overlapping path-type matches on a line are reported once, under the most specific pattern (the Windows user-profile pattern now runs first).
- **Single-segment drive regex:** The end-of-token lookahead used `\\s` inside a raw-string class, which matched a backslash or the letter `s` instead of whitespace. It now uses a shared terminator class that also accepts backticks, brackets and separators.
- **CRLF rejected in batch files:** `.bat` and `.cmd` files are exempt from the CRLF check. The BOM check still applies.

### Added
- **GitHub annotations:** When `GITHUB_ACTIONS=true`, each violation is also printed as an `::error file=,line=,col=::` command, so it appears on the PR diff. Paths are relative to `GITHUB_WORKSPACE`, and the matched sample is left out so secrets are not repeated in the PR UI.
- **Action `fix: true` notice:** The action prints `git diff --stat` after fixing and warns that changes are not committed.
- Regression tests for every item above and for the v1.6.1 fixes (`scripts/test_validate.py`).
- **Configurable private terms:** Context-bleed names are now read from `QUENCH_PRIVATE_TERMS`, a terms file (`~/.config/quench/private-terms` or `QUENCH_PRIVATE_TERMS_FILE`), and a repeatable `--private-term` flag on `quench check` and `scripts/validate.py`. The GitHub Action gains a `private-terms` input meant to be fed from a secret. Only the count of terms is printed.

### Changed
- README GitHub Action examples use the floating major tag `@v1` instead of `@master`, with a note on pinning an exact release. The pre-commit example pins `rev: v1.6.2`.
- **Removed the hardcoded private project name:** The scanner no longer ships a built-in private tool name in `FORBIDDEN_PATH_PATTERNS`; see "Configurable private terms" above. The LG-02 adversarial scenario and its fixture now use a fictional tool name (`hushcache`).
- **LG-01 example path:** The LG-01 scenario, fixture and docs now use a fictional folder (`devbox`) instead of a real local folder name. Rule LG-01-R1 now fails on any drive-letter absolute path, not only the one named in the prompt.
- **Skill Version Bump (`precision-output` v1.0.2):** `skills/precision-output/references/adversarial-test-suite.md` LG-01 and LG-02 examples now use the fictional folder and tool names. Updated the skills table in `README.md`.

## [1.6.1] 2026-09-23

### Changed
- **Skill Version Bump (`precision-output` v1.0.1):** Incremented `skills/precision-output/SKILL.md` and reference documentation to v1.0.1 following the addition of leakguard ignore markers in `skills/precision-output/references/adversarial-test-suite.md`. Updated skills table in `README.md`.

### Fixed
- **Issue 1 - File coverage too narrow:** `TEXT_EXTENSIONS` expanded to include PHP, JS/TS, Dart, Go, Ruby, Rust, Swift, Java, C#, CSS/SCSS, HTML, TOML, INI, XML, HCL, and shell variants. A new `NO_SUFFIX_SCAN_NAMES` set covers no-suffix files (Dockerfile, Makefile, Procfile, pre-commit, commit-msg). `.env.*` variants (`.env.local`, `.env.production`, `.env.test`) are matched via `startswith('.env')`. Previously `src/config.php` and `.env` files containing credentials were silently skipped.
- **Issue 2 - `test_*` skip applied globally:** Removed the `filename.startswith('test_')` blanket skip from `scan_repository`. The explicit `IGNORE_FILES` set (covering only quench's own test suite files) is sufficient and no longer silences `test_helpers.php`, `test_config.js`, or any other target-repo test file that may legitimately contain secrets.
- **Issue 3 - Whitelist silenced all patterns per line:** The line-level whitelist bypass in `validate_path_leaks` now scopes exclusively to path-type patterns (`Hardcoded local workspace drive path`, `Windows user profile absolute path`, `Unix home directory absolute path`, `Private LAN IP address`, `Localhost URL with non-generic path`). Secret and token patterns (GitHub PAT, `sk-`, Anthropic, AWS, Stripe, etc.) run unconditionally regardless of whitelisted path substrings appearing elsewhere on the same line.
- **Issue 4 - Path detection too narrow:** Three path patterns widened:
  - Drive-letter pattern now catches any two-segment absolute path (previously only `*:\quench` was matched). A second single-segment pattern catches bare workspace roots at end of token (a drive letter followed by a single folder name).
  - Windows user profile pattern now accepts end-of-line as a valid terminator, catching user-profile paths that lack a trailing separator.
  - Unix home pattern simplified from requiring specific suffix segments to matching any home-relative subdirectory path at any depth.
- **Issue 5 - Parity gate triggered on any repo with `adapters/` dir:** Added `_is_quench_repo(root)` sentinel that checks for both `rules/AGENTS.md` and `skills/plaincast/SKILL.md`. The parity gate now returns early unless both are present, preventing 28 false violations in third-party repos with a directory named `adapters/`.
- **Issue 6 - Skills gate rejected valid external skills:** `validate_skill_frontmatter` now accepts an optional `quench_repo` flag (passed from `scan_repository`). When `quench_repo=True`, all three fields (`name`, `version`, `description`) are required. In external repos, only `name` and `description` are required, matching standard Claude Code / Antigravity skill format. Skills inside `.claude`, `.cursor`, `.kilo`, `.cline`, `.junie`, or `node_modules` are fully exempted from structural validation; only the `trigger` key prohibition still applies universally.
- **Issue 7 - `sk-ant-` keys reported twice:** Reordered `FORBIDDEN_PATH_PATTERNS` so the Anthropic-specific `sk-ant-` pattern precedes the generic `sk-` pattern. Added `(?!ant-)` negative lookahead to the generic pattern to prevent double-reporting when an Anthropic key is present.
- **action.yml injection fix:** All three user inputs (`target`, `fix`, `paths-only`) are now passed through `env:` as `INPUT_TARGET`, `INPUT_FIX`, `INPUT_PATHS_ONLY` and read via environment variables in the run script. Direct `${{ inputs.* }}` interpolation inside `run:` is removed, closing a shell injection vector when untrusted data (branch names, PR titles) is passed as the `target` input. The Python setup step is renamed from "Set up Python if not available" to "Install Python 3.11" to accurately reflect that `actions/setup-python` always overrides the PATH.
- **Adversarial test suite doc:** Added `<!-- leakguard:ignore-start/end -->` markers around the intentional bad-example paths in `skills/precision-output/references/adversarial-test-suite.md` so the tool does not flag its own illustrative LG-01 prompt examples.

---

## [1.6.0] 2026-09-21

### Added
- Automated Adversarial Evaluation Runner (`scripts/eval_adversarial.py` and `quench eval` CLI subcommand):
  - Zero-dependency testing engine validating LLM completions against 12 canonical adversarial scenarios across all 4 disciplines:
    - `steel-mind`: SM-01 (Sycophancy induction), SM-02 (Invented citations), SM-03 (Silver lining compulsion).
    - `plaincast`: PC-01 (Emoji injection), PC-02 (Em dash and curly quotes), PC-03 (Unicode arrows and checkmarks).
    - `leakguard`: LG-01 (Host drive paths), LG-02 (Private MCP tool bleed), LG-03 (Token exposure).
    - `precision-output`: PO-01 (Phantom SDK methods), PO-02 (Unverified config keys), PO-03 (Hallucinated CLI flags).
  - Built-in canonical fixtures:
    - 12 failing baseline completions mirroring default LLM failure modes (100% failure detection).
    - 12 hardened compliant completions satisfying 100% of binary compliance rules (12/12 pass rate).
  - CLI `quench eval` with `--self-test` (default), `--input <path>` (supports JSON and JSONL completions), and `--json` for CI automation.
  - Generates a clean ASCII scorecard detailing scenario IDs, disciplines, rule pass/total counts, and descriptions.
- Comprehensive Evaluation Test Suite (`scripts/test_eval_adversarial.py`):
  - 11 unit tests verifying scenario loading, baseline failure detection, compliant completion passes, rule violation messages, CLI invocations, and external file parsing.
  - Overall test suite expanded from 115 to 126 tests with 100% pass rate.

---

## [1.5.9] 2026-09-21

### Changed
- Resolved Redundancy Map candidates (R-01 through R-04) from the Adversarial Test Suite:
  - R-01 (`steel-mind` / `precision-output`): Consolidated phantom API and manifest cross-referencing to `precision-output` as the canonical owner; streamlined `steel-mind: Output Integrity` to a concise reference pointer.
  - R-02 (`steel-mind` / `precision-output`): Consolidated duplicate definitions of the three epistemic states (Known, Inferred, Uncertain) to `precision-output`; `steel-mind: Epistemic Integrity` focuses cleanly on confidence calibration, version qualification, and blast-radius stop/proceed gating.
  - R-03 (`steel-mind` / `leakguard`): Replaced redundant hermetic tool isolation checklist item in `steel-mind Protocol 5` with direct reference to `leakguard Protocol 2`.
  - R-04 (`steel-mind`): Consolidated duplicate file read/overwrite invariants in `steel-mind: Tool Use Discipline` ("read before write" and "never overwrite unread files") into a single unified rule: `Before any file write or overwrite: read current content in the active session first.`
- Token budget reduction:
  - `rules/AGENTS.md` streamlined with tighter phrasing across all four disciplines.
  - Synchronized all trims across all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie) maintaining strict adapter parity.
- CLI & Packaging consistency:
  - Aligned dual module attributes by defining `__version__ = "1.5.9"` across both `quench.py` and `scripts/quench.py`.
  - Hardened `scripts/test_packaging.py` import precedence so root `quench.py` is tested deterministically under test runner discovery.
  - Bumped project version to 1.5.9 in `pyproject.toml`, `scripts/quench.py`, `quench.py`, and test suites.

---

## [1.5.8] 2026-09-20

### Added
- Resolved adversarial gap proposals across skill definitions and synced to all 11 adapters:
  - G-01 (`steel-mind`): Added `Cadence Self-Check Gate` (prose of 5+ sentences where 4+ fall within a 5-word band triggers rewriting at least 2 sentences).
  - G-02 (`plaincast`): Evaluated and closed - bold-first list spam is already covered by existing protocol.
  - G-03 (`steel-mind` / `leakguard`): Evaluated and closed - path separator mixing is already covered by existing invariants.
  - G-04 (`steel-mind`): Added explicit activation gate for code review comments and PR descriptions to check software subjects for false agency verbs ("tries", "wants", "hopes", "attempts", "believes", "expects").
  - G-05 (`steel-mind`): Added `PowerShell Write Quick-Test` verifying `[System.IO.File]::WriteAllText` with `UTF8Encoding $false` on any generated PowerShell write.
- Synced all rule additions across `rules/AGENTS.md` and all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie).

### Fixed
- False-positive calibration across Rust, Ruby, and Monorepo corpora (tokio-rs/tokio, sinatra/sinatra, vercel/turbo - 6,900+ files cloned):
  - **Localhost URL pattern** (`scripts/validate.py`):
    - In `vercel/turbo`, 41 violations were flagged for standard local dev URLs like `localhost:3000/api`, `localhost:9090/graph`, `localhost:3002/stripe` appearing in example documentation and test fixtures.
    - Fix: Extended the negative lookahead of the localhost regex to exclude common development API path prefixes (`api`, `graphql`, `graph`, `webhook`, `stripe`, `health`, `docs`, `metrics`, `mf-manifest`, `mf-`). Private service URLs remain flagged.
    - Re-scanned `turbo` (2,501 files): all validation gates passed with 0 violations.
    - `tokio` (41 text files) and `sinatra` (24 text files) passed with 0 violations.

---

## [1.5.7] 2026-09-20

### Fixed
- Gate 2 (leakguard) false-positive calibration via real open-source corpus testing
  (shadcn-ui/ui, fastai/fastai, cli/cli - 1,430 files scanned total):

  **Private LAN IP address pattern** (`scripts/validate.py`):
  - Previous regex `\b(?:192\.168\.|10\.|172\...)[\\d.]+` matched three-part semver
    version strings (`10.0.0`, `10.4.14`) in `package.json` and `pnpm-lock.yaml`
    files, producing 1,486 false positives in shadcn-ui alone.
  - Fix: Rewrote the 10.x.y.z arm to require all four octets with per-octet range
    validation (`0-255`). Also added a negative lookbehind for version-prefix
    characters (`>=<~^'"@`) to suppress matches inside dependency version
    constraints.
  - The 192.168 and 172.16-31 arms also upgraded to four-octet form for consistency.

  **Unix home directory path pattern**:
  - `/home/runner/work` and `/Users/runner/work` appeared extensively in GitHub
    Actions workflow testdata fixtures and CI log snapshots in the cli/cli repo,
    generating 133 false positives. The `runner` user is an ephemeral GitHub Actions
    CI agent, not a developer personal home directory.
  - Fix: Added `/home/runner/` and `/Users/runner/` to `WHITELISTED_PATH_SUBSTRINGS`.

<!-- leakguard:ignore-start -->
- **True positive confirmed** during calibration: cli/cli `eval-prompts.yml` contains
  `/Users/williammartin/work` (a real developer username) in 4 locations - correctly
  flagged by the scanner as a genuine Unix home directory leak (not suppressed).
<!-- leakguard:ignore-end -->

### Changed
- Token budget trim of `rules/AGENTS.md` and monolithic adapter files:
  - `rules/AGENTS.md` reduced from 8,635 bytes to 6,293 bytes (~1,573 tokens, down from ~2,160).
  - Trimmed: Context Economy verbosity, Structural Cadence illustrative parentheticals,
    redundant precision-output epistemic state restatement (R-02 from adversarial analysis),
    redundant phantom-API line (R-01).
  - Applied same trims to: `adapters/antigravity/.agents/rules/AGENTS.md`,
    `adapters/copilot/copilot-instructions.md`, `adapters/generic/system-prompt.md`,
    `adapters/windsurf/.windsurfrules`.
  - Adapters with compact modular format (aider) and adapter-specific concise form (claude) unchanged.

### Test results
- All 114 tests pass across all 6 suites (test_validate, test_cli_e2e, test_precommit_hooks,
  test_packaging, test_action_yml, test_bootstrap_scripts) with zero regressions.
- Fixed leakguard self-scan false positives: adversarial-test-suite.md intentional
  bad-output fixtures (fake API keys, private tool names) and the CHANGELOG true-positive
  citation now wrapped in leakguard:ignore-start/end blocks. These are test data, not leaks.

---

## [1.5.6] 2026-09-20

### Added
- Adversarial test suite document (`skills/precision-output/references/adversarial-test-suite.md`):
  - 10 adversarial prompts (3 per skill discipline, plus an extra precision-output case given its blast radius).
  - Full analysis per prompt: baseline LLM failure mode, firing Quench rule, and binary compliance test.
  - Coverage gap analysis: 5 genuine gaps identified (G-01 through G-05) across cadence detection,
    bold-first list monotony, path separator mixing, false agency in code review, and BOM write elicitation.
  - Redundancy map: 4 rule overlaps identified as consolidation candidates for the next AGENTS.md trim.
- Gap proposals added as commented TODO blocks to skill files:
  - `skills/steel-mind/SKILL.md`: gaps G-01 (cadence self-check gate), G-04 (agency activation note),
    and G-05 (BOM write quick test).
  - `skills/plaincast/SKILL.md`: gap G-02 (bold-first bullet adversarial prompt proposal).

---

## [1.5.5] 2026-09-20

### Added
- Official Pre-Commit Framework Support (`.pre-commit-hooks.yaml`):
  - Integrates Quench into standard pre-commit workflows with `quench-check` and `quench-commit-msg` hooks.
  - Added `scripts/test_precommit_hooks.py` validating manifest structure, hook definitions, and stage bindings.
- Python Packaging & Global CLI (`pyproject.toml`):
  - PEP 517 / PEP 621 packaging with `setuptools>=61.0` and zero runtime dependencies.
  - Installs global `quench` command directly on system `$PATH` via `pipx install git+https://github.com/primaybr/quench.git` or `pip install -e .`.
  - Refined `quench.py` to support module importing without circular namespace collisions.
  - Added `scripts/test_packaging.py` testing packaging metadata, module loading, and CLI entrypoint wiring.
- Reusable GitHub Action (`action.yml`):
  - Composite action enabling external repositories to run Quench integrity scans with `uses: primaybr/quench@master`.
  - Configurable inputs for `target`, `fix`, and `paths-only`.
  - Added `scripts/test_action_yml.py` validating action schema, inputs, and composite execution steps.
- Standalone Remote Bootstrap Installers (`scripts/install.sh`, `scripts/install.ps1`):
  - Portable POSIX sh script supporting one-liner installation (`curl -fsSL ... | bash -s -- --tool cursor`).
  - Native Windows PowerShell script written strictly in UTF-8 without BOM (`irm ... | iex`).
  - Added `scripts/test_bootstrap_scripts.py` verifying argument handling, source discovery, and cross-platform installation behaviors.
- Validation engine adjustments (`scripts/validate.py`):
  - Automatically ignores `test_*.py` test suites during repository scans to prevent false positives on synthetic test fixtures.

---

## [1.5.4] 2026-09-20

### Added
- Interactive Quench CLI (`scripts/quench.py` and top-level runner `quench.py`):
  - Zero-dependency unified command line interface built with Python 3 stdlib.
  - `quench init`: Interactive or scripted initialization across 12 adapter targets (`cursor`, `copilot`, `kilo`, `cline`, `windsurf`, `claude`, `generic`, `aider`, `zed`, `junie`, `antigravity`, `rules`, or `all`). Supports `--target`, `--force`, and `--hooks`.
  - `quench check`: Repository verification across all 5 gates with `--fix` and `--paths-only` options.
  - `quench update`: Automatic detection and refreshing of installed adapters from upstream templates.
  - `quench status` / `info`: Inspection of active adapters, configured rules, and git hook status.
  - Global `--version` / `-v` flag reporting `quench 1.5.4`.
- External Contributor Sanity Check Suite (`scripts/test_cli_e2e.py`):
  - End-to-end integration tests using isolated temporary directories and fresh git repositories.
  - Comprehensive coverage for single, modular, and full adapter initialization.
  - Verification of git pre-commit and commit-msg hooks and execution permissions.
  - Validation engine pass/fail detection on clean projects, synthetic violations, and auto-fix capabilities.
  - Status detection and adapter updating workflows.
  - Wired into `scripts/test_validate.py` and CI workflow `.github/workflows/validate.yml`.
- Validation engine adjustments (`scripts/validate.py`):
  - Gate 3 parity check scoped to repositories containing `adapters/` source tree, ensuring clean validation of consumer repositories.
  - Added `test_cli_e2e.py` to `IGNORE_FILES`.

---

## [1.5.3] 2026-09-19

### Added
- `skills/precision-output/SKILL.md` (v1.0.0):
  - Hallucination prevention, epistemic integrity, and verification-before-assertion gates
  - Protocol 1: Verify-Before-Assert Invariant (Existence Gate)
  - Protocol 2: The Three Epistemic States (Known, Inferred, Uncertain)
  - Protocol 3: Phantom API & Import Elimination (Manifest Cross-Referencing)
  - Protocol 4: Execution Grounding & Mental Runtime Simulation
  - Protocol 5: Clean Refusal & Blast Radius Calibration
- Reference documentation for precision-output:
  - `skills/precision-output/references/verification-checklist.md`: Pre-assertion checklist for agents before outputting code or claims
  - `skills/precision-output/references/hallucination-catalog.md`: Taxonomy of phantom APIs, fabricated flags, and memory drift traps
- Full adapter parity across all 11 adapters:
  - New modular adapter files:
    - `adapters/cursor/.cursor/rules/precision-output.mdc`
    - `adapters/kilo/.kilo/rules/precision-output.md`
    - `adapters/cline/.clinerules/precision-output.md`
    - `adapters/zed/.zedprompts/precision-output.md`
    - `adapters/junie/.junie/rules/precision-output.md`
  - Updated `adapters/kilo/kilo.jsonc` to include `.kilo/rules/precision-output.md`
  - Appended precision-output section to all consolidated adapters:
    - `adapters/antigravity/.agents/rules/AGENTS.md`
    - `adapters/cursor/.cursorrules`
    - `adapters/copilot/copilot-instructions.md`
    - `adapters/windsurf/.windsurfrules`
    - `adapters/claude/CLAUDE.md` (section 11)
    - `adapters/generic/system-prompt.md`
    - `adapters/aider/CONVENTIONS.md`
- Always-on rule extraction:
  - Added `## precision-output: Grounded Verification & Integrity Gates` section to `rules/AGENTS.md`
- Validation engine parity update (`scripts/validate.py`):
  - Added the 5 new modular adapter paths to `REQUIRED_ADAPTERS` in Gate 3 parity check
- Documentation updates:
  - `README.md`: Added `precision-output` (v1.0.0) to skills table and architecture tree
  - `INSTALL.md`: Added `precision-output` installation copy commands and adapter coverage matrix

---

## [1.5.2] 2026-09-19

### Added
- CI badge in `README.md` (GitHub Actions Validate workflow status badge)
- Gate 2 extended secret patterns (5 new categories):
  - Slack API tokens (`xoxb-`, `xoxp-`, `xoxa-` prefixes)
  - Twilio Account SIDs (`AC[a-f0-9]{32}`)
  - Twilio Auth Token inline assignments
  - SendGrid API keys (`SG.[A-Za-z0-9]{67}`)
  - GCP service account private_key fragments
- Gate 2 auto-fix (`--fix` flag now also repairs local drive path violations):
  - `validate_path_leaks` gains `auto_fix: bool = False` parameter
  - Local drive/home path matches replaced with `/path/to/<project>` in-place
  - Secret/token matches flagged with `(manual rotation required)` but NOT auto-replaced
  - `scan_repository` wires Gate 2 fixes alongside existing Gate 1 fixes
- 9 new unit tests (7 in `TestLeakguardCloudPatterns`, 2 in `TestGate2AutoFix`)
- `skills/leakguard/SKILL.md` (v1.0.2): Protocol 3 updated with new token signatures
- `INSTALL.md`: leakguard install instructions added for all 11 adapters

### Changed
- README skills table: leakguard version updated to 1.0.2
- INSTALL.md adapter install blocks: leakguard `cp` lines added for Cursor (mdc), Cline, Kilo, Zed, Junie

---

## [1.5.1] 2026-09-19

### Added
- Expanded Gate 2 secret scanner in `scripts/validate.py` with 10 new pattern categories:
  - Anthropic API Keys (`sk-ant-` prefix)
  - AWS Access Key IDs (`AKIA[A-Z0-9]{16}`)
  - AWS Secret Access Key inline assignments
  - Stripe live/test/restricted keys (`sk_live_`, `pk_live_`, `rk_live_`, `rk_test_`)
  - Raw Bearer token strings in documentation or config
  - Generic API key assignments (`api_key = <value>`)
  - Database connection URIs with embedded credentials (postgres, mysql, mongodb, redis, mssql)
  - `.env` secret assignment bleed for common variable names (`DB_PASSWORD`, `SECRET_KEY`, `JWT_SECRET`, `APP_KEY`, `AUTH_SECRET`)
  - Private LAN IP addresses (`192.168.x.x`, `10.x.x.x`, RFC 1918 ranges)
  - Localhost URLs with non-generic application paths
- 8 new unit tests in `TestLeakguardExtendedPatterns` (30 total, up from 22)
- `skills/leakguard/SKILL.md` (v1.0.1): expanded Protocol 3 scanned token signatures list to match all new engine patterns
- `skills/leakguard/references/leak-patterns.md`: wrapped DB URI example block with `leakguard:ignore` markers

### Changed
- Versioning scheme: patch digit (last position) increments from 0 through 9 before the minor digit advances

---

## [1.5.0] 2026-09-19


### Added
- `skills/leakguard/SKILL.md` (v1.0.0):
  - Environment, path, and context isolation discipline
  - Protocol 1: Path Neutralization & Generic Placeholders (host path neutralization hierarchy)
  - Protocol 2: Hermetic Project Isolation & Anti-Context Bleed (preventing private environment tools, sibling project names, and internal prompts from leaking into public code and docs)
  - Protocol 3: Secret & Credential Redaction (API keys, PATs, database connection strings)
  - Protocol 4: Pre-Commit Diff & Staging Audit
  - Protocol 5: Portable Path Formatting (universal forward slashes)
- `skills/leakguard/references/leak-patterns.md`:
  - Reference catalog detailing path leaks, context bleed vectors, credential exposures, and remediation procedures
- `skills/steel-mind/SKILL.md` (v1.1.0):
  - Protocol 5: Added Hermetic Project Isolation integrity gate (verifying tools and dependencies exist in current repository)
  - Protocol 6: Generic subagent delegation and cache guidance
- `skills/steel-mind/references/slop-taxonomy.md`:
  - Added Category 9: Context Bleed and Boundary Violations
- `rules/AGENTS.md`:
  - Added always-on compact extract for `leakguard`
  - Enforced hermetic project boundaries across repository invariants
- Multi-Tool Adapter Parity:
  - Synchronized `leakguard` across all 11 adapters (Antigravity, Cursor, Copilot, Kilo, Cline, Windsurf, Claude, Generic, Aider, Zed, Junie)
- Validation Engine & Pre-Commit Hook:
  - Added Cross-Project Context Bleed detection to Gate 2 in `scripts/validate.py`
  - Added `test_cross_project_bleed_detected` to unit test suite

### Security & Sanitization
- Purged all occurrences of external project names and private tool references across git history using `git-filter-repo`

---

## [1.4.0] 2026-09-19

### Added
- Repository Validation Engine (`scripts/validate.py`):
  - Zero-dependency verification engine using Python 3 standard library
  - Gate 1 (Plaincast Character Boundary): Enforces strict ASCII keyboard boundary, detects banned emojis, typographic dashes, curly quotes, Unicode ellipsis, and zero-width characters with optional `--fix` auto-repair
  - Gate 2 (Leakguard & Path Sanitization): Detects hardcoded local workspace drive paths, user profile folders, absolute home paths, and accidental secret token leaks
  - Gate 3 (Multi-Tool Adapter Parity): Verifies presence of all 11 adapters and ensures bidirectional synchronization with active skills and `rules/AGENTS.md`
  - Gate 4 (Skill Frontmatter Schema): Validates YAML schema on all skills (requires `name`, SemVer `version`, `description`; rejects illegal fields like `trigger`)
  - Gate 5 (Hygiene & Encoding): Enforces UTF-8 encoding without BOM and rejects CRLF line endings
- Pre-commit Automation (`.githooks/pre-commit`, `scripts/install-hooks.py`):
  - Added git pre-commit hook executing `scripts/validate.py` before any commit
  - Added installer utility configuring `core.hooksPath` to `.githooks`
- Unit Test Suite (`scripts/test_validate.py`):
  - 16 test cases verifying each validation gate against clean and dirty fixtures, path leaks, and auto-fix behavior

### Security & Sanitization
- Purged local path references across repository git history using `git-filter-repo`
- Replaced absolute host drive paths in documentation with standardized `/path/to/quench` placeholders

---

## [1.3.0] 2026-09-19

### Added
- `skills/steel-mind/SKILL.md` (v1.1.0):
  - Formally introduced Rule Tiers: Hard Gates (non-negotiable invariants) and Purpose Gates (techniques requiring functional justification)
  - Protocol 8: Structural Cadence & Syntactic Integrity (cadence uniformity prevention, bimodal burstiness trap mitigation, sentence opener diversity, elimination of trailing participial tack-ons, and removal of negative parallelisms)
  - Protocol 9: Semantic Grounding & Agency Discipline (elimination of false agency in inanimate software artifacts, removal of compulsive silver linings from technical findings, and copula avoidance puffery replacement)
- `skills/steel-mind/references/slop-taxonomy.md`:
  - Added Category 7: Cadence and Syntactic Tells
  - Added Category 8: Semantic Fallacies and False Agency
- `skills/plaincast/SKILL.md` (v1.1.0):
  - Protocol 9: Punctuation Density & List Restraint (colon and semicolon density gating, bold-first list spam avoidance)
- `rules/AGENTS.md`:
  - Synchronized always-on compact extracts for structural cadence, false agency, colon restraint, and list spam avoidance
- Synchronized all 11 adapters across the repository:
  - Antigravity (`adapters/antigravity/.agents/rules/AGENTS.md`)
  - Cursor (`.cursorrules`, `.cursor/rules/*.mdc`)
  - GitHub Copilot (`copilot-instructions.md`)
  - Kilo Code (`.kilo/rules/`)
  - Cline (`.clinerules/`)
  - Windsurf (`.windsurfrules`)
  - Claude.ai (`CLAUDE.md`)
  - Generic System Prompt (`system-prompt.md`)
  - Aider (`CONVENTIONS.md`)
  - Zed AI (`.zedprompts/`)
  - JetBrains Junie (`.junie/rules/`)

---

## [1.2.0] 2026-09-19

### Added
- `adapters/kilo/` - Kilo Code adapter (free, popular VS Code AI coding extension)
  - `kilo.jsonc` - project config file referencing both rule files via `instructions` array
  - `.kilo/rules/steel-mind.md` - behavior tempering rules
  - `.kilo/rules/plaincast.md` - text normalization rules
  - Supports global install via `~/.config/kilo/kilo.jsonc`
- `INSTALL.md` updated with Kilo Code section and updated adapter coverage table

### Fixed
- All adapters now include both steel-mind and plaincast content (previously plaincast
  was missing from all adapter files)
- Added modular plaincast files for tools supporting separate rule files:
  Cursor (.mdc), Cline (.clinerules), Zed (.zedprompts), JetBrains Junie (.junie/rules)

---

## [1.1.0] 2026-09-19

### Added
- `plugin.json` - quench is now a proper Antigravity plugin, installable via plugins.json
- `rules/AGENTS.md` - compact always-on rules file compiled from all skills
  - steel-mind protocols 1-6 distilled into injected rules (anti-slop, platform,
    tool discipline, epistemic integrity, output integrity, context economy)
  - plaincast text normalization rules (emoji, em dash, curly quotes, ellipsis,
    invisible characters, Unicode symbols, all-caps, bold inflation)
- `CHANGELOG.md` - this file

### Changed
- `skills/steel-mind/SKILL.md` - removed invalid `trigger: model_decision` frontmatter field
  (trigger is a rules-only field; skills use progressive disclosure via description)
- `skills/plaincast/SKILL.md` - same frontmatter fix
- `README.md` - updated to explain skills vs rules architecture, plugin installation

### Architecture clarification
Skills and rules are two separate loading mechanisms:
- Skills (SKILL.md): progressive disclosure - agent reads the description and decides
  to load the full content when relevant. Used for deep reference material.
- Rules (AGENTS.md): always-on - injected into every context window automatically,
  silently, without agent decision or announcement. Used for behavioral disciplines.

quench uses both: SKILL.md files are the canonical source of truth and full
reference. rules/AGENTS.md is the compact always-on extract that the agent
operates under every session without thinking about it.

---

## [1.0.0] 2026-09-19

### Added
- `skills/steel-mind/SKILL.md` - AI behavior tempering discipline
  - Protocol 1: Anti-slop lexicon (14 banned constructs with positive replacements)
  - Protocol 2: Platform grounding (Windows paths, BOM encoding, file locking)
  - Protocol 3: Tool use discipline (surgeon's checklist for destructive ops)
  - Protocol 4: Epistemic integrity (3 knowledge states, confidence calibration)
  - Protocol 5: Output integrity gates (verify before assert)
  - Protocol 6: Context economy (subagent delegation, compression, clean stop)
  - Protocol 7: Encoding and file write hygiene (safe write patterns per language)
- `skills/steel-mind/references/slop-taxonomy.md` - full slop pattern catalog
- `skills/steel-mind/references/platform-traps.md` - OS and DB failure modes
- `skills/steel-mind/references/tool-discipline-checklist.md` - pre-flight checklist
- `skills/plaincast/SKILL.md` - text normalization discipline
  - Protocol 1: Emoji prohibition with rationale
  - Protocol 2: Dash discipline (8 Unicode dash variants catalogued)
  - Protocol 3: Quote discipline (16 Unicode quote variants with replacements)
  - Protocol 4: Ellipsis discipline (U+2026 vs three periods)
  - Protocol 5: Invisible and space characters (10 variants)
  - Protocol 6: Arrows, bullets, symbols (with ASCII replacements)
  - Protocol 7: Heading and structure discipline
  - Protocol 8: Numerals and units
  - Quick self-check (9-point mental scan)
  - Explicit exception conditions
- `skills/plaincast/references/character-taxonomy.md` - full Unicode table with Python normalization script
- `skills/plaincast/references/why-it-matters.md` - 10 contexts x concrete pipeline failures
- `skills/plaincast/references/style-guide-comparison.md` - AP, Chicago, Microsoft, Google positions
- `adapters/` - multi-tool adapter files for Cursor, Copilot, Cline, Windsurf, Claude.ai,
  generic (ChatGPT/Replit), Aider, Zed, JetBrains Junie
- `INSTALL.md` - multi-tool installation guide
- `README.md` - project overview
- `.gitignore` - OS, editor, temp file exclusions
- `.gitattributes` - enforces LF line endings for all text files
