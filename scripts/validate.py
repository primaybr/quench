#!/usr/bin/env python3
"""
quench Validation Engine
A zero-dependency integrity scanner for the quench ecosystem.

Checks:
  Gate 1: plaincast - Character boundary & Unicode hygiene
  Gate 2: leakguard - Local environment & absolute path leak prevention
  Gate 3: parity    - Multi-tool adapter synchronization across all 11 adapters
  Gate 4: skills    - Skill frontmatter schema & SemVer compliance
  Gate 5: hygiene   - UTF-8 no BOM & LF line-ending verification
"""

import argparse
import functools
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

# ---------------------------------------------------------------------------
# Plaincast Character Taxonomy & Replacements
# ---------------------------------------------------------------------------

REPLACEMENTS: List[Tuple[str, str, str]] = [
    # (char, replacement, category)
    # Dashes
    ('\u2014', ' - ', 'em-dash'),
    ('\u2013', '-', 'en-dash'),
    ('\u2012', '-', 'figure-dash'),
    ('\u2011', '-', 'non-breaking-hyphen'),
    ('\u2010', '-', 'unicode-hyphen'),
    ('\u2015', ' - ', 'horizontal-bar'),
    ('\u2212', '-', 'minus-sign'),
    # Quotes
    ('\u2018', "'", 'left-single-quote'),
    ('\u2019', "'", 'right-single-quote'),
    ('\u201c', '"', 'left-double-quote'),
    ('\u201d', '"', 'right-double-quote'),
    ('\u201a', "'", 'single-low-quote'),
    ('\u201e', '"', 'double-low-quote'),
    ('\u201b', "'", 'single-high-reversed'),
    ('\u201f', '"', 'double-high-reversed'),
    ('\u2032', "'", 'prime'),
    ('\u2033', '"', 'double-prime'),
    # Ellipsis
    ('\u2026', '...', 'horizontal-ellipsis'),
    ('\u2025', '..', 'two-dot-leader'),
    # Spaces & Invisible
    ('\u00a0', ' ', 'no-break-space'),
    ('\u202f', ' ', 'narrow-nbsp'),
    ('\u2009', ' ', 'thin-space'),
    ('\u200a', ' ', 'hair-space'),
    ('\u200b', '', 'zero-width-space'),
    ('\u200c', '', 'zero-width-non-joiner'),
    ('\u200d', '', 'zero-width-joiner'),
    ('\ufeff', '', 'bom-character'),
    ('\u2028', '\n', 'line-separator'),
    ('\u2029', '\n\n', 'paragraph-separator'),
    # Arrows
    ('\u2192', '->', 'rightwards-arrow'),
    ('\u2190', '<-', 'leftwards-arrow'),
    ('\u2191', '^', 'upwards-arrow'),
    ('\u2193', 'v', 'downwards-arrow'),
    ('\u21d2', '=>', 'double-right-arrow'),
    ('\u21d0', '<=', 'double-left-arrow'),
    ('\u2794', '->', 'heavy-right-arrow'),
    ('\u27f6', '->', 'long-right-arrow'),
    # Bullets & Dingbats
    ('\u2022', '-', 'bullet'),
    ('\u25e6', '-', 'white-bullet'),
    ('\u2023', '>', 'triangular-bullet'),
    ('\u25b6', '>', 'black-right-triangle'),
    ('\u25ba', '>', 'black-right-pointer'),
    ('\u2043', '-', 'hyphen-bullet'),
    ('\u2605', '*', 'black-star'),
    ('\u2606', '*', 'white-star'),
    # Checkmarks & Crosses
    ('\u2713', '[x]', 'checkmark'),
    ('\u2714', '[x]', 'heavy-checkmark'),
    ('\u2717', '[ ]', 'ballot-x'),
    ('\u2718', '[ ]', 'heavy-ballot-x'),
    # Typographic Symbols
    ('\u00a9', '(c)', 'copyright'),
    ('\u00ae', '(R)', 'registered'),
    ('\u2122', '(TM)', 'trademark'),
    ('\u00b0', 'deg', 'degree'),
    ('\u00d7', 'x', 'multiplication'),
    ('\u00f7', '/', 'division'),
    ('\u00b1', '+/-', 'plus-minus'),
]

CHAR_MAP = {char: (replacement, category) for char, replacement, category in REPLACEMENTS}

# Files permitted to contain illustrative Unicode tables
TAXONOMY_EXEMPTIONS = {
    'character-taxonomy.md',
    'style-guide-comparison.md',
    'why-it-matters.md',
}

# ---------------------------------------------------------------------------
# Path & Secret Leak Patterns
# ---------------------------------------------------------------------------

# Characters that end a path token (lookahead only, never consumed).
_PATH_END = r'(?=[/\\"\'`\s,;:)\]}>|]|$)'

FORBIDDEN_PATH_PATTERNS = [
    # Literal workspace drives or user home folders.
    # Path patterns are ordered most-specific first: overlapping path matches on the
    # same line are reported once, under the first pattern that matched.
    # Windows user profile: drive:\Users\name with or without trailing separator.
    (re.compile(r'(?<![A-Za-z0-9_])[a-zA-Z]:[/\\]Users[/\\][A-Za-z0-9_.-]+' + _PATH_END, re.IGNORECASE), 'Windows user profile absolute path'),
    # Two-segment pattern: catches drive-letter paths with at least two directory levels.
    # The whitelist for C:/path/... and C:/new/file.txt prevents doc example FPs.
    (re.compile(r'(?<![A-Za-z0-9_])[a-zA-Z]:[/\\](?!path[/\\]|new[/\\])[A-Za-z0-9_.-]+[/\\](?=[A-Za-z0-9_.-])', re.IGNORECASE), 'Hardcoded local workspace drive path'),
    # Single-segment drive-root workspace at end of token, e.g. a bare project-name-only path.
    (re.compile(r'(?<![A-Za-z0-9_])[a-zA-Z]:[/\\](?!path\b|new\b)[A-Za-z][A-Za-z0-9_.-]{2,}' + _PATH_END, re.IGNORECASE), 'Hardcoded local workspace drive path'),
    # Unix home: /home/<user>/subpath or /Users/<user>/subpath at any depth; CI runner paths whitelisted separately.
    # Case-sensitive and must start a token, so web routes (/users/42/orders) and URL
    # paths (https://host/Users/alice/profile) do not match.
    (re.compile(r'(?<![A-Za-z0-9_.~-])/(?:home|Users)/[A-Za-z0-9_.-]+/(?=[A-Za-z0-9_.-])'), 'Unix home directory absolute path'),

    # GitHub tokens
    (re.compile(r'\bghp_[A-Za-z0-9]{36}\b'), 'GitHub Personal Access Token'),
    (re.compile(r'\bgithub_pat_[A-Za-z0-9_]{82}\b'), 'GitHub Fine-grained PAT'),

    # AI / LLM API keys - specific prefix first, then generic (avoids double-reporting sk-ant-)
    (re.compile(r'\bsk-ant-[A-Za-z0-9_-]{20,}\b'), 'Anthropic API key'),
    (re.compile(r'\bsk-(?!ant-)[A-Za-z0-9_-]{20,}\b'), 'OpenAI/LLM secret key (sk- prefix)'),

    # AWS credentials
    (re.compile(r'\bAKIA[A-Z0-9]{16}\b'), 'AWS Access Key ID'),
    (re.compile(r'\bAKIAS[A-Z0-9]{16}\b'), 'AWS STS temporary Access Key ID'),
    (re.compile(r'(?i)aws.{0,20}secret.{0,20}=\s*[A-Za-z0-9+/]{40}\b'), 'AWS Secret Access Key assignment'),

    # Generic high-entropy bearer / API tokens
    (re.compile(r'\bBearer\s+[A-Za-z0-9\-._~+/]{20,}\b'), 'Raw Bearer token in content'),
    (re.compile(r'(?i)api[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9\-._~+/]{20,}["\']?'), 'Generic API key assignment'),

    # Stripe tokens
    (re.compile(r'\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{24,}\b'), 'Stripe secret/publishable/restricted key'),

    # Slack tokens
    (re.compile(r'\bxox[bpa]-[a-z0-9-]+'), 'Slack API token (xoxb/xoxp/xoxa)'),

    # Twilio credentials
    (re.compile(r'\bAC[a-f0-9]{32}\b'), 'Twilio Account SID'),
    (re.compile(r'\bTWILIO_AUTH_TOKEN\s*=\s*[\'"][0-9a-fA-F]{32}[\'"]'), 'Twilio Auth Token inline assignment'),

    # SendGrid API key
    (re.compile(r'\bSG\.[A-Za-z0-9]{67}\b'), 'SendGrid API key (SG. prefix)'),

    # GCP service account private key fragment
    (re.compile(r'"private_key"\s*:\s*"[^"]*-----BEGIN (?:RSA )?PRIVATE KEY-----'), 'GCP service account private key fragment'),

    # Database connection strings with embedded credentials
    (re.compile(r'(?i)(?:postgres|postgresql|mysql|mariadb|mongodb|redis|mssql)://[^:@\s]+:[^@\s]+@[^\s"\']+'), 'Database URI with embedded credentials'),

    # .env file content bleed - key=value with a real secret value (non-placeholder)
    (re.compile(r'(?im)^(?:DB_PASSWORD|DATABASE_PASSWORD|SECRET_KEY|APP_KEY|JWT_SECRET|AUTH_SECRET)\s*=\s*(?!["\'"]?\s*$|["\']?<|["\']?your|["\']?change|["\']?placeholder)[^\s\n]{8,}'), '.env secret assignment bleed'),

    # Private/internal hostnames and IPs
    # 10.x.y.z requires all four octets to avoid matching semver/version strings (e.g. 10.0.0 in package.json).
    # Negative lookbehind for version-prefix chars (>=<~^'"@) prevents matches inside version constraints.
    (re.compile(
        r'(?<![>=<~^\'\"@])'
        r'\b(?:'
        r'10\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
        r'|192\.168\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
        r'|172\.(?:1[6-9]|2[0-9]|3[01])\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
        r')(?::\d+)?(?:/\S+)?\b'
    ), 'Private LAN IP address'),
    # Negative lookahead excludes: generic doc placeholders (path/, your-, example),
    # and well-known development API path prefixes that appear legitimately in monorepo
    # example READMEs and dev tool scripts (api, graphql, graph, webhook, stripe,
    # health, docs, metrics, mf-manifest, mf-). Private service paths (e.g.
    # localhost:PORT/internal-dashboard) are still flagged.
    (re.compile(r'(?i)\b(?:localhost|127\.0\.0\.1):\d{4,5}/(?!path/|your-|example|api\b|graphql\b|graph\b|webhook\b|stripe\b|health\b|docs\b|metrics\b|mf-)[a-zA-Z0-9_-]{3,}\b'), 'Localhost URL with non-generic path'),
]

# ---------------------------------------------------------------------------
# Private Terms (cross-project context bleed)
# ---------------------------------------------------------------------------
# Names of private tools, sibling projects or internal hosts that must never
# appear in this repo. They are configured outside the repo on purpose: a term
# list committed to a public repo would itself leak the names it protects.
#
# Sources, merged in order:
#   1. QUENCH_PRIVATE_TERMS       comma- or newline-separated terms (e.g. a CI secret)
#   2. QUENCH_PRIVATE_TERMS_FILE  path to a file, one term per line, '#' comments
#      (defaults to ~/.config/quench/private-terms when that file exists)
#   3. --private-term TERM        CLI flag, repeatable

PRIVATE_TERMS_ENV = 'QUENCH_PRIVATE_TERMS'
PRIVATE_TERMS_FILE_ENV = 'QUENCH_PRIVATE_TERMS_FILE'
DEFAULT_PRIVATE_TERMS_FILE = Path('~/.config/quench/private-terms')
PRIVATE_TERM_DESC = 'Cross-project context bleed / private environment tool'


def _split_terms(text: str) -> List[str]:
    terms = []
    for line in text.splitlines():
        line = line.split('#', 1)[0]
        terms.extend(t.strip() for t in line.split(','))
    return [t for t in terms if t]


def load_private_terms(extra: Optional[Sequence[str]] = None) -> List[str]:
    """Collect private terms from the environment, the terms file and extra (CLI) values."""
    terms = _split_terms(os.environ.get(PRIVATE_TERMS_ENV, ''))

    file_setting = os.environ.get(PRIVATE_TERMS_FILE_ENV)
    terms_file = Path(file_setting).expanduser() if file_setting else DEFAULT_PRIVATE_TERMS_FILE.expanduser()
    if terms_file.is_file():
        terms.extend(_split_terms(terms_file.read_text(encoding='utf-8-sig')))
    elif file_setting:
        print(f"Warning: {PRIVATE_TERMS_FILE_ENV} points to a missing file: {terms_file}", file=sys.stderr)

    for value in extra or []:
        terms.extend(_split_terms(value))

    # Keep order, drop case-insensitive duplicates
    seen: Set[str] = set()
    unique = []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    return unique


@functools.lru_cache(maxsize=32)
def _private_term_patterns(terms: Tuple[str, ...]) -> List[Tuple['re.Pattern[str]', str]]:
    """Compile each term as a whole word, also matching tool-style suffixes (term_ask)."""
    return [
        (re.compile(r'(?<![A-Za-z0-9_])' + re.escape(t) + r'(?:_[A-Za-z0-9_]+)?(?![A-Za-z0-9_])', re.IGNORECASE),
         PRIVATE_TERM_DESC)
        for t in terms
    ]

# Illustrative documentation examples allowed
WHITELISTED_PATH_SUBSTRINGS = [
    'C:/path',
    'C:\\path',
    'C:/Users/...',
    'C:\\Users\\...',
    'C:/new/file.txt',
    'C:\\new\\file.txt',
    'C:\\Users/name\\file',
    '/path/to/quench',
    '/your-project/',
    '~/.config/kilo/',
    '~/.gemini/config/',
    '~/.claude/',
    # GitHub Actions ephemeral CI runner paths - not real user home directories
    '/home/runner/',
    '/Users/runner/',
]

# ---------------------------------------------------------------------------
# Required Adapters & Structure
# ---------------------------------------------------------------------------

REQUIRED_ADAPTERS = [
    Path('adapters/antigravity/.agents/rules/AGENTS.md'),
    Path('adapters/cursor/.cursorrules'),
    Path('adapters/cursor/.cursor/rules/steel-mind.mdc'),
    Path('adapters/cursor/.cursor/rules/plaincast.mdc'),
    Path('adapters/cursor/.cursor/rules/leakguard.mdc'),
    Path('adapters/cursor/.cursor/rules/precision-output.mdc'),
    Path('adapters/copilot/copilot-instructions.md'),
    Path('adapters/kilo/kilo.jsonc'),
    Path('adapters/kilo/.kilo/rules/steel-mind.md'),
    Path('adapters/kilo/.kilo/rules/plaincast.md'),
    Path('adapters/kilo/.kilo/rules/leakguard.md'),
    Path('adapters/kilo/.kilo/rules/precision-output.md'),
    Path('adapters/cline/.clinerules/steel-mind.md'),
    Path('adapters/cline/.clinerules/plaincast.md'),
    Path('adapters/cline/.clinerules/leakguard.md'),
    Path('adapters/cline/.clinerules/precision-output.md'),
    Path('adapters/windsurf/.windsurfrules'),
    Path('adapters/claude/CLAUDE.md'),
    Path('adapters/generic/system-prompt.md'),
    Path('adapters/aider/CONVENTIONS.md'),
    Path('adapters/zed/.zedprompts/steel-mind.md'),
    Path('adapters/zed/.zedprompts/plaincast.md'),
    Path('adapters/zed/.zedprompts/leakguard.md'),
    Path('adapters/zed/.zedprompts/precision-output.md'),
    Path('adapters/junie/.junie/rules/steel-mind.md'),
    Path('adapters/junie/.junie/rules/plaincast.md'),
    Path('adapters/junie/.junie/rules/leakguard.md'),
    Path('adapters/junie/.junie/rules/precision-output.md'),
]

# ---------------------------------------------------------------------------
# Result Reporting Structures
# ---------------------------------------------------------------------------

class Violation:
    def __init__(self, gate: str, file_path: Path, line: int, col: int, message: str, sample: str = ''):
        self.gate = gate
        self.file_path = file_path
        self.line = line
        self.col = col
        self.message = message
        self.sample = sample

    def __str__(self) -> str:
        loc = f"{self.file_path}:{self.line}:{self.col}" if self.line > 0 else f"{self.file_path}"
        msg = f"[{self.gate}] {loc} - {self.message}"
        if self.sample:
            codepoints = " ".join(f"U+{ord(c):04X}" for c in self.sample)
            msg += f" (found: {self.sample!r} [{codepoints}])"
        return msg


class ValidationReport:
    def __init__(self):
        self.violations: List[Violation] = []
        self.files_scanned = 0
        # Files with violations that --fix left untouched because they are code, not prose.
        self.fix_skipped: List[Path] = []

    def add(self, violation: Violation):
        self.violations.append(violation)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _escape_annotation(value: str, is_property: bool = False) -> str:
    """Escape text for a GitHub Actions workflow command."""
    value = value.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    if is_property:
        value = value.replace(':', '%3A').replace(',', '%2C')
    return value


def github_annotation(violation: Violation, root: Path) -> str:
    """Format a violation as a GitHub Actions ::error command so it shows on the PR diff.

    File paths are made relative to GITHUB_WORKSPACE (the repo root), because the
    scan root may be a subdirectory. The matched sample is left out on purpose: an
    annotation must not repeat a secret in the PR UI.
    """
    file_path = Path(violation.file_path)
    if not file_path.is_absolute():
        file_path = root / file_path
    workspace = os.environ.get('GITHUB_WORKSPACE')
    try:
        shown = file_path.resolve().relative_to(Path(workspace).resolve()) if workspace else file_path
    except ValueError:
        shown = file_path
    props = [f"file={_escape_annotation(shown.as_posix(), True)}"]
    if violation.line > 0:
        props.append(f"line={violation.line}")
        props.append(f"col={max(violation.col, 1)}")
    props.append(f"title={_escape_annotation('quench ' + violation.gate, True)}")
    return f"::error {','.join(props)}::{_escape_annotation(violation.message)}"


def print_violations(report: ValidationReport, root: Path) -> None:
    """Print each violation, plus a GitHub annotation when running in GitHub Actions."""
    in_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    for v in report.violations:
        print(f"  {v}")
        if in_actions:
            print(github_annotation(v, root))
    if report.fix_skipped:
        print(f"\n--fix left {len(report.fix_skipped)} code/config file(s) unchanged; "
              "only prose files (.md, .mdc, .mdx, .txt, .rst, .adoc) are rewritten. Fix these by hand:")
        for p in report.fix_skipped:
            print(f"  {Path(p).as_posix()}")


# ---------------------------------------------------------------------------
# Validation Gate Implementations
# ---------------------------------------------------------------------------

def is_emoji(char: str) -> bool:
    cp = ord(char)
    # Supplementary Multilingual Plane & Emoji blocks
    if 0x1F000 <= cp <= 0x1FAFF:
        return True
    # Miscellaneous Symbols and Dingbats
    if 0x2600 <= cp <= 0x27BF:
        return True
    # Miscellaneous Symbols and Arrows
    if 0x2B00 <= cp <= 0x2BFF:
        return True
    # Variation Selectors
    if 0xFE00 <= cp <= 0xFE0F:
        return True
    # Enclosed Alphanumeric Supplement
    if 0x1F100 <= cp <= 0x1F1FF:
        return True
    return False


def validate_plaincast(path: Path, content: str, report: ValidationReport, auto_fix: bool = False) -> Optional[str]:
    """Gate 1: Verify plaincast character boundary and Unicode cleanliness."""
    if path.name in TAXONOMY_EXEMPTIONS:
        return None

    lines = content.split('\n')
    fixed_lines = []
    has_changes = False
    in_ignore_block = False

    for line_idx, line in enumerate(lines, 1):
        if '<!-- plaincast:ignore-start -->' in line:
            in_ignore_block = True
        if '<!-- plaincast:ignore-end -->' in line:
            in_ignore_block = False
            fixed_lines.append(line)
            continue

        if in_ignore_block or '<!-- plaincast:ignore-line -->' in line:
            fixed_lines.append(line)
            continue

        new_chars: List[str] = []
        # Set after an emoji is removed so the space it leaves behind is not doubled.
        collapse_space = False
        for col_idx, ch in enumerate(line, 1):
            if ch in CHAR_MAP:
                rep, cat = CHAR_MAP[ch]
                report.add(Violation(
                    gate='plaincast',
                    file_path=path,
                    line=line_idx,
                    col=col_idx,
                    message=f"Banned typographic character '{ch}' ({cat}) -> replace with '{rep}'",
                    sample=ch
                ))
                # ' - ' must not double the spaces already around a spaced em dash.
                if rep.startswith(' ') and new_chars and new_chars[-1].endswith(' '):
                    rep = rep[1:]
                if rep.endswith(' ') and line[col_idx:col_idx + 1] == ' ':
                    rep = rep[:-1]
                new_chars.append(rep)
                has_changes = True
                collapse_space = False
            elif is_emoji(ch):
                report.add(Violation(
                    gate='plaincast',
                    file_path=path,
                    line=line_idx,
                    col=col_idx,
                    message=f"Banned emoji character (U+{ord(ch):04X}) -> remove completely",
                    sample=ch
                ))
                has_changes = True
                collapse_space = True
                # do not append emoji when fixing
            elif ch == ' ' and collapse_space and (not new_chars or new_chars[-1].endswith(' ')):
                continue
            else:
                new_chars.append(ch)
                collapse_space = False

        fixed_line = ''.join(new_chars)
        # Removing a trailing emoji ("Sale 50% X") must not leave trailing whitespace behind.
        if fixed_line != line and line == line.rstrip():
            fixed_line = fixed_line.rstrip()
        fixed_lines.append(fixed_line)

    if auto_fix and has_changes:
        return '\n'.join(fixed_lines)
    return None


# Patterns whose matches are local paths and safe to auto-replace
_PATH_AUTOFIX_PATTERNS = {
    'Hardcoded local workspace drive path',
    'Windows user profile absolute path',
    'Unix home directory absolute path',
}

# Patterns that describe path or host references (not secrets).
# The whitelist is consulted ONLY for these - never for secret/token patterns.
_PATH_PATTERN_DESCS = {
    'Hardcoded local workspace drive path',
    'Windows user profile absolute path',
    'Unix home directory absolute path',
    'Private LAN IP address',
    'Localhost URL with non-generic path',
}

_CIDR_NETWORK_RE = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.0)/(\d{1,2})$')


def _is_cidr_network(sample: str) -> bool:
    """True for a range definition such as 10.0.0.0/8 or 192.168.1.0/24 (SSRF guards,
    firewall rules), which names a network rather than a host. A host address written
    with a prefix (last octet not 0) is still reported."""
    m = _CIDR_NETWORK_RE.match(sample)
    return bool(m) and int(m.group(2)) <= 32


# Characters that continue a path token past the matched prefix (used by --fix).
_PATH_TOKEN_CHAR = re.compile(r'[A-Za-z0-9_.~/\\-]')


def validate_path_leaks(path: Path, content: str, report: ValidationReport, auto_fix: bool = False,
                        private_terms: Sequence[str] = ()) -> Optional[str]:
    """Gate 2: Detect environment path leaks and local credentials.

    private_terms are extra names (private tools, sibling projects) flagged as
    context bleed; see load_private_terms() for where callers get them.

    When auto_fix=True:
    - Local drive/home path matches are replaced with /path/to/<project>
    - Secret/token matches are NOT replaced; their violation message gains
      ' (manual rotation required)' to prompt the committer
    Returns the fixed content string when auto_fix=True and edits were made,
    or None otherwise.
    """
    patterns = FORBIDDEN_PATH_PATTERNS + _private_term_patterns(tuple(private_terms))
    lines = content.split('\n')
    fixed_lines = list(lines)
    has_changes = False
    in_ignore_block = False

    for line_idx, line in enumerate(lines, 1):
        if '<!-- leakguard:ignore-start -->' in line:
            in_ignore_block = True
        if '<!-- leakguard:ignore-end -->' in line:
            in_ignore_block = False
            continue

        if in_ignore_block or '<!-- leakguard:ignore-line -->' in line:
            continue

        # Skip whitelisted sample illustrations in documentation (only for path-type patterns;
        # secret/token patterns always run regardless of whitelist matches on the line).
        line_is_whitelisted = any(w in line for w in WHITELISTED_PATH_SUBSTRINGS)
        # Spans already reported by a path-type pattern on this line. One Windows
        # user-profile path matches several path patterns; it is reported once.
        path_spans: List[Tuple[int, int]] = []
        fix_spans: List[Tuple[int, int]] = []

        for pattern, desc in patterns:
            is_path_type = desc in _PATH_PATTERN_DESCS
            is_path_violation = desc in _PATH_AUTOFIX_PATTERNS
            # Whitelist only suppresses path/host patterns, not secret patterns
            if is_path_type and line_is_whitelisted:
                continue
            for match in pattern.finditer(line):
                start, end = match.span()
                if desc == 'Private LAN IP address' and _is_cidr_network(match.group(0)):
                    continue
                if is_path_type:
                    if any(start < s_end and s_start < end for s_start, s_end in path_spans):
                        continue
                    path_spans.append((start, end))
                violation_msg = f"Potential local path or secret leak: {desc}"
                if auto_fix and not is_path_violation:
                    violation_msg += ' (manual rotation required)'
                report.add(Violation(
                    gate='leakguard',
                    file_path=path,
                    line=line_idx,
                    col=start + 1,
                    message=violation_msg,
                    sample=match.group(0)
                ))
                if auto_fix and is_path_violation:
                    # Replace the whole path token, not just the matched prefix, so no
                    # user name or project segment survives and no neighbouring text is eaten.
                    token_end = end
                    while token_end < len(line) and _PATH_TOKEN_CHAR.match(line[token_end]):
                        token_end += 1
                    fix_spans.append((start, token_end))

        if fix_spans:
            merged: List[Tuple[int, int]] = []
            for start, token_end in sorted(fix_spans):
                if merged and start <= merged[-1][1]:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], token_end))
                else:
                    merged.append((start, token_end))
            fixed = line
            for start, token_end in reversed(merged):
                fixed = fixed[:start] + '/path/to/<project>' + fixed[token_end:]
            fixed_lines[line_idx - 1] = fixed
            has_changes = True

    if auto_fix and has_changes:
        return '\n'.join(fixed_lines)
    return None


# Windows batch files legitimately need CRLF (commonly `*.bat text eol=crlf` in .gitattributes).
CRLF_ALLOWED_SUFFIXES = {'.bat', '.cmd'}


def _crlf_reaches_commit(git_eol: Tuple[str, str, str], autocrlf: str) -> Optional[bool]:
    """Decide from `git ls-files --eol` data whether CRLF would be committed.

    git_eol is (index, worktree, attr), e.g. ('lf', 'crlf', 'text=auto eol=lf').
    Returns True/False when git settles it, None when only the working-tree bytes can tell.
    """
    index_eol, work_eol, attr = git_eol
    if index_eol in ('crlf', 'mixed'):
        return True                      # already committed with CRLF
    if work_eol not in ('crlf', 'mixed'):
        return False
    attrs = attr.split()
    if '-text' in attrs or 'binary' in attrs:
        return True                      # git stores the bytes as they are
    if any(a == 'text' or a.startswith('text=') or a.startswith('eol=') for a in attrs):
        return False                     # normalized to LF on commit
    if autocrlf in ('true', 'input'):
        return False                     # core.autocrlf converts CRLF to LF on commit
    return True


def validate_encoding_and_endings(path: Path, raw_bytes: bytes, report: ValidationReport,
                                  git_eol: Optional[Tuple[str, str, str]] = None, autocrlf: str = ''):
    """Gate 5: Verify no UTF-8 BOM and LF line endings in what gets committed.

    With git_eol (from `git ls-files --eol`), CRLF that exists only in a Windows working
    copy and that git normalizes to LF on commit (core.autocrlf, a text attribute) is not
    reported. Without it, the working-tree bytes decide. Batch files may use CRLF.
    """
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        report.add(Violation(
            gate='hygiene',
            file_path=path,
            line=1,
            col=1,
            message="File starts with UTF-8 BOM (EF BB BF); must be UTF-8 no BOM"
        ))

    crlf_committed = _crlf_reaches_commit(git_eol, autocrlf) if git_eol else None
    if crlf_committed is False:
        return
    if b'\r\n' in raw_bytes and path.suffix.lower() not in CRLF_ALLOWED_SUFFIXES:
        # report first CRLF occurrence
        lines = raw_bytes.split(b'\n')
        for i, l in enumerate(lines, 1):
            if l.endswith(b'\r'):
                report.add(Violation(
                    gate='hygiene',
                    file_path=path,
                    line=i,
                    col=len(l),
                    message="CRLF line ending detected; must use standard LF line endings"
                ))
                break


def _is_quench_repo(root: Path) -> bool:
    """Return True only when root is the quench repository itself.

    Prevents the parity gate and strict skills schema from triggering in
    other people's repos that happen to have an adapters/ or skills/ directory.
    """
    return (
        (root / 'rules' / 'AGENTS.md').exists()
        and (root / 'skills' / 'plaincast' / 'SKILL.md').exists()
    )


def validate_skill_frontmatter(path: Path, content: str, report: ValidationReport, quench_repo: bool = False):
    """Gate 4: Verify skill SKILL.md YAML frontmatter format and fields.

    When quench_repo=True (scanning the quench repo itself), all three fields
    name/version/description are required and version must be SemVer.
    In external repos only name and description are required, matching the
    standard Claude Code / Antigravity skill format.

    Skills inside hidden tool dirs (.claude, .cursor, etc.) are exempted entirely
    from structural validation; only the trigger-key prohibition still applies.
    """
    if not path.name == 'SKILL.md' or 'skills' not in path.parts:
        return

    # Skills inside third-party tool config dirs use their own schemas
    EXEMPT_PARENTS = {'.claude', '.cursor', '.kilo', '.cline', '.junie', 'node_modules'}
    if any(part in EXEMPT_PARENTS for part in path.parts):
        # Still parse enough to flag the trigger key
        content_lower = content
        if 'trigger:' in content_lower:
            lines_check = content.splitlines()
            for lidx, lline in enumerate(lines_check, 1):
                if re.match(r'^\s*trigger\s*:', lline):
                    report.add(Violation(
                        'skills', path, lidx, 1,
                        "Prohibited frontmatter key 'trigger' found (trigger is rules-only; skills use progressive disclosure)"
                    ))
                    break
        return

    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        report.add(Violation('skills', path, 1, 1, "SKILL.md must begin with '---' YAML frontmatter"))
        return

    fm_lines = []
    end_idx = -1
    for idx, line in enumerate(lines[1:], 2):
        if line.strip() == '---':
            end_idx = idx
            break
        fm_lines.append((idx, line))

    if end_idx == -1:
        report.add(Violation('skills', path, 1, 1, "Unterminated YAML frontmatter in SKILL.md"))
        return

    fm_dict: Dict[str, str] = {}
    for idx, line in fm_lines:
        match = re.match(r'^([a-zA-Z0-9_-]+):\s*(.*)$', line)
        if match:
            key, val = match.groups()
            fm_dict[key.strip()] = val.strip()

    # version is mandatory only in the quench repo; external skills need only name + description
    required_fields = ['name', 'version', 'description'] if quench_repo else ['name', 'description']
    for req in required_fields:
        if req not in fm_dict:
            report.add(Violation('skills', path, 1, 1, f"Missing required frontmatter key: '{req}'"))

    # Check prohibited fields (universal)
    if 'trigger' in fm_dict:
        report.add(Violation(
            'skills',
            path,
            1,
            1,
            "Prohibited frontmatter key 'trigger' found (trigger is rules-only; skills use progressive disclosure)"
        ))

    # Check SemVer (only relevant when version field is expected)
    if 'version' in fm_dict:
        ver = fm_dict['version']
        if not re.match(r'^\d+\.\d+\.\d+$', ver):
            report.add(Violation('skills', path, 1, 1, f"Version '{ver}' does not adhere to SemVer format (X.Y.Z)"))


def validate_adapter_parity(root: Path, report: ValidationReport):
    """Gate 3: Ensure all 11 adapters exist and represent active skills.

    This gate only runs when scanning the quench repo itself. It must not
    fire in other repos that happen to have a directory named adapters/.
    """
    if not _is_quench_repo(root):
        return

    # 1. Verify existence of all adapter files
    for adapter in REQUIRED_ADAPTERS:
        full_path = root / adapter
        if not full_path.exists():
            report.add(Violation('parity', adapter, 0, 0, f"Missing required adapter file: {adapter}"))

    # 2. Discover active skills
    skills_dir = root / 'skills'
    active_skills: Set[str] = set()
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir() and (skill_folder / 'SKILL.md').exists():
                active_skills.add(skill_folder.name)

    # 3. Check rules/AGENTS.md covers all active skills
    agents_rule = root / 'rules' / 'AGENTS.md'
    if agents_rule.exists():
        agents_content = agents_rule.read_text(encoding='utf-8')
        for skill in active_skills:
            if skill not in agents_content:
                report.add(Violation(
                    'parity',
                    Path('rules/AGENTS.md'),
                    0,
                    0,
                    f"Active skill '{skill}' is not referenced in rules/AGENTS.md"
                ))


# ---------------------------------------------------------------------------
# Main Scan Coordinator
# ---------------------------------------------------------------------------

TEXT_EXTENSIONS = {
    # Markup / Docs
    '.md', '.mdc', '.mdx', '.txt', '.rst', '.adoc',
    # Data / Config
    '.json', '.jsonc', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml', '.env',
    # Web
    '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.svelte',
    '.html', '.htm', '.css', '.scss', '.sass',
    # Backend
    '.php', '.rb', '.go', '.java', '.kt', '.kts', '.cs', '.py', '.dart', '.rs', '.swift',
    # Shell / CI
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    # Infra
    '.tf', '.hcl',
}

# Filenames with no suffix (or dotfiles) that must always be scanned
NO_SUFFIX_SCAN_NAMES: Set[str] = {
    'Dockerfile', 'Makefile', 'Procfile',
    'pre-commit', 'commit-msg',
    '.cursorrules', '.windsurfrules',
}

IGNORE_DIRS = {'.git', '__pycache__', '.pytest_cache', '.vscode', '.idea', 'venv', 'env', 'node_modules', '.kilo', 'worktrees'}
# Build output and dependency folders, skipped only when the target is not a git
# work tree. In a git work tree, .gitignore decides instead (see _list_files).
GENERATED_DIRS = {'vendor', 'build', 'dist', 'out', 'target', '.next', '.nuxt', '.dart_tool', '.gradle', '.venv', 'coverage'}
# Only skip quench's own test suite files; do NOT use startswith('test_') - that silences
# test_*.py/js/php files in target repos, which may legitimately contain secrets.
IGNORE_FILES = {'test_validate.py', 'test_cli_e2e.py', 'test_eval_adversarial.py', 'test_packaging.py'}

# --fix rewrites only prose files. In code, a "banned" character may be UI text
# (a copyright sign in a footer, an emoji in a label) and a path-like string may be
# a route, so code-file violations are reported but never rewritten.
FIXABLE_EXTENSIONS = {'.md', '.mdc', '.mdx', '.txt', '.rst', '.adoc'}
FIXABLE_NAMES = {'.cursorrules', '.windsurfrules'}


def _should_scan(filename: str, suffix: str) -> bool:
    """Return True if the file should be read and passed through the gates."""
    if suffix in TEXT_EXTENSIONS:
        return True
    if filename in NO_SUFFIX_SCAN_NAMES:
        return True
    # .env.local, .env.production, .env.test etc.
    if filename.startswith('.env'):
        return True
    return False


def _is_fixable(filename: str, suffix: str) -> bool:
    """Return True if --fix may rewrite this file (prose/docs only)."""
    return suffix in FIXABLE_EXTENSIONS or filename in FIXABLE_NAMES


def _git_list_files(root: Path) -> Optional[List[Path]]:
    """List tracked plus untracked-but-not-ignored files under root, relative to root.

    Returns None when root is not inside a git work tree or git is unavailable,
    so the caller falls back to walking the filesystem.
    """
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
            capture_output=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    names = result.stdout.decode('utf-8', errors='surrogateescape').split('\0')
    return sorted({Path(n) for n in names if n})


def _git_eol_info(root: Path) -> Tuple[Dict[Path, Tuple[str, str, str]], str]:
    """Return ({path: (index_eol, worktree_eol, attr)}, core.autocrlf) for a git work tree.

    Parses `git ls-files --eol`, whose lines look like
    'i/lf    w/crlf  attr/text=auto eol=lf<TAB>path'. Empty when not in a git work tree.
    """
    info: Dict[Path, Tuple[str, str, str]] = {}
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'ls-files', '-z', '--eol', '--cached', '--others', '--exclude-standard'],
            capture_output=True, timeout=120,
        )
        autocrlf = subprocess.run(['git', '-C', str(root), 'config', '--get', 'core.autocrlf'],
                                  capture_output=True, text=True, timeout=30).stdout.strip().lower()
    except (OSError, subprocess.SubprocessError):
        return info, ''
    if result.returncode != 0:
        return info, ''
    for entry in result.stdout.decode('utf-8', errors='surrogateescape').split('\0'):
        meta, sep, name = entry.partition('\t')
        if not sep or not name:
            continue
        fields = meta.split(None, 2)
        values = {f.split('/', 1)[0]: (f.split('/', 1)[1] if '/' in f else '').strip() for f in fields}
        info[Path(name)] = (values.get('i', ''), values.get('w', ''), values.get('attr', ''))
    return info, autocrlf


def _list_files(root: Path) -> List[Path]:
    """Return candidate files relative to root, honouring .gitignore in git work trees."""
    git_files = _git_list_files(root)
    if git_files:
        # --cached still lists files deleted from the work tree; skip them and submodule dirs.
        return [p for p in git_files
                if not any(part in IGNORE_DIRS for part in p.parts[:-1]) and (root / p).is_file()]

    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and d not in GENERATED_DIRS]
        for filename in filenames:
            files.append((Path(dirpath) / filename).relative_to(root))
    return files


def scan_repository(root: Path, check_paths_only: bool = False, auto_fix: bool = False,
                    private_terms: Optional[Sequence[str]] = None) -> ValidationReport:
    """Scan root with all gates. private_terms=None loads them via load_private_terms()."""
    report = ValidationReport()
    is_quench = _is_quench_repo(root)
    if private_terms is None:
        private_terms = load_private_terms()

    # Run adapter parity check first
    if not check_paths_only:
        validate_adapter_parity(root, report)

    eol_info, autocrlf = _git_eol_info(root) if not check_paths_only else ({}, '')

    for rel_path in _list_files(root):
        filename = rel_path.name
        if filename in IGNORE_FILES:
            continue

        file_path = root / rel_path
        suffix = file_path.suffix.lower()

        if not _should_scan(filename, suffix):
            continue

        report.files_scanned += 1
        fix_file = auto_fix and _is_fixable(filename, suffix)
        violations_before = len(report.violations)

        try:
            raw_bytes = file_path.read_bytes()
        except Exception as e:
            report.add(Violation('io', rel_path, 0, 0, f"Failed to read file: {e}"))
            continue

        # Gate 5: Encoding & Endings
        if not check_paths_only:
            validate_encoding_and_endings(rel_path, raw_bytes, report,
                                          git_eol=eol_info.get(rel_path), autocrlf=autocrlf)

        # Decode text
        try:
            content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            report.add(Violation('encoding', rel_path, 0, 0, f"Invalid UTF-8 sequence: {e}"))
            continue

        # Gate 2: Path & Leak Validation
        gate2_fixed = validate_path_leaks(rel_path, content, report, auto_fix=fix_file,
                                          private_terms=private_terms)
        if fix_file and gate2_fixed is not None and gate2_fixed != content:
            file_path.write_text(gate2_fixed, encoding='utf-8', newline='\n')
            content = gate2_fixed

        if not check_paths_only:
            # Gate 1: Plaincast
            fixed_content = validate_plaincast(rel_path, content, report, auto_fix=fix_file)
            if fix_file and fixed_content is not None and fixed_content != content:
                file_path.write_text(fixed_content, encoding='utf-8', newline='\n')

            # Gate 4: Skill Frontmatter
            validate_skill_frontmatter(rel_path, content, report, quench_repo=is_quench)

        if auto_fix and not fix_file and len(report.violations) > violations_before:
            report.fix_skipped.append(rel_path)

    return report


MIN_SUBJECT_ALNUM = 3


def validate_commit_message(msg_path: Path, report: ValidationReport,
                            private_terms: Optional[Sequence[str]] = None):
    """Validate a commit message for leaks, banned characters, and encoding.

    private_terms=None loads them via load_private_terms().
    """
    try:
        raw_bytes = msg_path.read_bytes()
    except Exception as e:
        report.add(Violation('io', msg_path, 0, 0, f"Cannot read commit message file: {e}"))
        return

    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        report.add(Violation('hygiene', msg_path, 1, 1, "Commit message starts with UTF-8 BOM"))

    try:
        content = raw_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        report.add(Violation('encoding', msg_path, 0, 0, f"Commit message is not valid UTF-8: {e}"))
        return

    # Filter out git comment lines starting with '#'
    non_comment_lines = [l for l in content.splitlines() if not l.strip().startswith('#')]
    effective_msg = '\n'.join(non_comment_lines).strip()
    if not effective_msg:
        report.add(Violation('commit-msg', msg_path, 1, 1, "Commit message is empty"))
        return

    # A placeholder such as "..." or "-" says nothing about the change
    subject = effective_msg.splitlines()[0]
    if sum(ch.isalnum() for ch in subject) < MIN_SUBJECT_ALNUM:
        report.add(Violation('commit-msg', msg_path, 1, 1,
                             f"Commit subject {subject.strip()!r} does not describe the change "
                             f"(needs at least {MIN_SUBJECT_ALNUM} letters or digits)"))

    # Gate 1: Plaincast
    validate_plaincast(Path('COMMIT_MSG'), effective_msg, report, auto_fix=False)

    # Gate 2: Leakguard
    if private_terms is None:
        private_terms = load_private_terms()
    validate_path_leaks(Path('COMMIT_MSG'), effective_msg, report, private_terms=private_terms)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="quench Validation Engine - Repository & Rule Integrity Checker")
    parser.add_argument('--root', type=str, default='.', help="Path to repository root")
    parser.add_argument('--fix', action='store_true', help="Automatically fix plaincast character violations")
    parser.add_argument('--check-paths-only', action='store_true', help="Only run Gate 2 (Path & Secret leak checks)")
    parser.add_argument('--check-commit-msg', type=str, help="Validate commit message file from git commit-msg hook")
    parser.add_argument('--private-term', action='append', default=[], metavar='TERM',
                        help=f"Private tool/project name to flag as context bleed (repeatable; "
                             f"also read from ${PRIVATE_TERMS_ENV} and ${PRIVATE_TERMS_FILE_ENV})")
    parser.add_argument('--verbose', action='store_true', help="Show verbose scan information")
    args = parser.parse_args()
    private_terms = load_private_terms(args.private_term)

    if args.check_commit_msg:
        msg_file = Path(args.check_commit_msg)
        report = ValidationReport()
        validate_commit_message(msg_file, report, private_terms=private_terms)
        if report.passed:
            print("[PASS] Commit message is clean.")
            sys.exit(0)
        else:
            print(f"\n[FAIL] Commit message contains {len(report.violations)} violation(s):\n")
            for v in report.violations:
                print(f"  {v}")
            print("\nCommit rejected: do not mention private project names, host paths, or tokens in commit messages.")
            sys.exit(1)

    repo_root = Path(args.root).resolve()
    print(f"Running quench Validation Engine on: {repo_root}")
    if args.fix:
        print("Auto-fix mode: ENABLED")
    if args.check_paths_only:
        print("Mode: Paths and secret leaks only")
    if private_terms:
        # Count only: printing the terms would leak them into CI logs.
        print(f"Private terms: {len(private_terms)} configured")

    report = scan_repository(repo_root, check_paths_only=args.check_paths_only, auto_fix=args.fix,
                             private_terms=private_terms)

    print(f"\nScanned {report.files_scanned} files across repository.")

    if report.passed:
        print("\n[PASS] All validation gates passed with zero violations.")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Found {len(report.violations)} violation(s):\n")
        print_violations(report, repo_root)
        print("\nPlease resolve all violations before committing or publishing.")
        sys.exit(1)


if __name__ == '__main__':
    main()
