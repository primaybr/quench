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
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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

FORBIDDEN_PATH_PATTERNS = [
    # Literal workspace drives or user home folders
    (re.compile(r'(?<![A-Za-z0-9_])[a-zA-Z]:[/\\]quench\b', re.IGNORECASE), 'Hardcoded local workspace drive path'),
    (re.compile(r'[a-zA-Z]:[/\\]Users[/\\][A-Za-z0-9_.-]+[/\\]', re.IGNORECASE), 'Windows user profile absolute path'),
    (re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+/(?:projects|work|quench|code)', re.IGNORECASE), 'Unix home directory absolute path'),

    # GitHub tokens
    (re.compile(r'\bghp_[A-Za-z0-9]{36}\b'), 'GitHub Personal Access Token'),
    (re.compile(r'\bgithub_pat_[A-Za-z0-9_]{82}\b'), 'GitHub Fine-grained PAT'),

    # AI / LLM API keys
    (re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'), 'OpenAI/LLM secret key (sk- prefix)'),
    (re.compile(r'\bsk-ant-[A-Za-z0-9_-]{20,}\b'), 'Anthropic API key'),

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
    (re.compile(r'\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)[\d.]+(?::\d+)?(?:/\S+)?\b'), 'Private LAN IP address'),
    (re.compile(r'(?i)\b(?:localhost|127\.0\.0\.1):\d{4,5}/(?!path/|your-|example)[a-zA-Z0-9_-]{3,}\b'), 'Localhost URL with non-generic path'),

    # Cross-project context bleed & ungrounded private tools
    (re.compile(r'\b' + 'hush' + 'cache' + r'(?:_[a-z0-9_]+)?\b', re.IGNORECASE), 'Cross-project context bleed / private environment tool'),
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

    def add(self, violation: Violation):
        self.violations.append(violation)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


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

        new_chars = []
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
                new_chars.append(rep)
                has_changes = True
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
                # do not append emoji when fixing
            else:
                new_chars.append(ch)

        fixed_lines.append(''.join(new_chars))

    if auto_fix and has_changes:
        return '\n'.join(fixed_lines)
    return None


# Patterns whose matches are local paths and safe to auto-replace
_PATH_AUTOFIX_PATTERNS = {
    'Hardcoded local workspace drive path',
    'Windows user profile absolute path',
    'Unix home directory absolute path',
}


def validate_path_leaks(path: Path, content: str, report: ValidationReport, auto_fix: bool = False) -> Optional[str]:
    """Gate 2: Detect environment path leaks and local credentials.

    When auto_fix=True:
    - Local drive/home path matches are replaced with /path/to/<project>
    - Secret/token matches are NOT replaced; their violation message gains
      ' (manual rotation required)' to prompt the committer
    Returns the fixed content string when auto_fix=True and edits were made,
    or None otherwise.
    """
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

        # Skip whitelisted sample illustrations in documentation
        if any(w in line for w in WHITELISTED_PATH_SUBSTRINGS):
            continue

        for pattern, desc in FORBIDDEN_PATH_PATTERNS:
            for match in pattern.finditer(line):
                matched_str = match.group(0)
                is_path_violation = desc in _PATH_AUTOFIX_PATTERNS
                violation_msg = f"Potential local path or secret leak: {desc}"
                if auto_fix and not is_path_violation:
                    violation_msg += ' (manual rotation required)'
                report.add(Violation(
                    gate='leakguard',
                    file_path=path,
                    line=line_idx,
                    col=match.start() + 1,
                    message=violation_msg,
                    sample=matched_str
                ))
                if auto_fix and is_path_violation:
                    fixed_lines[line_idx - 1] = fixed_lines[line_idx - 1].replace(matched_str, '/path/to/<project>', 1)
                    has_changes = True

    if auto_fix and has_changes:
        return '\n'.join(fixed_lines)
    return None


def validate_encoding_and_endings(path: Path, raw_bytes: bytes, report: ValidationReport):
    """Gate 5: Verify no UTF-8 BOM and strictly LF line endings."""
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        report.add(Violation(
            gate='hygiene',
            file_path=path,
            line=1,
            col=1,
            message="File starts with UTF-8 BOM (EF BB BF); must be UTF-8 no BOM"
        ))

    if b'\r\n' in raw_bytes:
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


def validate_skill_frontmatter(path: Path, content: str, report: ValidationReport):
    """Gate 4: Verify skill SKILL.md YAML frontmatter format and fields."""
    if not path.name == 'SKILL.md' or 'skills' not in path.parts:
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

    # Check required fields
    for req in ['name', 'version', 'description']:
        if req not in fm_dict:
            report.add(Violation('skills', path, 1, 1, f"Missing required frontmatter key: '{req}'"))

    # Check prohibited fields
    if 'trigger' in fm_dict:
        report.add(Violation(
            'skills',
            path,
            1,
            1,
            "Prohibited frontmatter key 'trigger' found (trigger is rules-only; skills use progressive disclosure)"
        ))

    # Check SemVer
    if 'version' in fm_dict:
        ver = fm_dict['version']
        if not re.match(r'^\d+\.\d+\.\d+$', ver):
            report.add(Violation('skills', path, 1, 1, f"Version '{ver}' does not adhere to SemVer format (X.Y.Z)"))


def validate_adapter_parity(root: Path, report: ValidationReport):
    """Gate 3: Ensure all 11 adapters exist and represent active skills."""
    # Gate 3 parity check applies to Quench repository source tree
    if not (root / 'adapters').exists():
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

TEXT_EXTENSIONS = {'.md', '.mdc', '.json', '.jsonc', '.txt', '.py', '.sh', '.yml', '.yaml'}
IGNORE_DIRS = {'.git', '__pycache__', '.pytest_cache', '.vscode', '.idea', 'venv', 'env', 'node_modules', '.kilo', 'worktrees'}
IGNORE_FILES = {'test_validate.py', 'test_cli_e2e.py'}


def scan_repository(root: Path, check_paths_only: bool = False, auto_fix: bool = False) -> ValidationReport:
    report = ValidationReport()

    # Run adapter parity check first
    if not check_paths_only:
        validate_adapter_parity(root, report)

    # Walk repository files
    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if filename in IGNORE_FILES:
                continue

            file_path = Path(dirpath) / filename
            rel_path = file_path.relative_to(root)

            # Skip binaries / non-text files
            if file_path.suffix.lower() not in TEXT_EXTENSIONS and filename not in {'pre-commit', '.windsurfrules', '.cursorrules'}:
                continue

            report.files_scanned += 1

            try:
                raw_bytes = file_path.read_bytes()
            except Exception as e:
                report.add(Violation('io', rel_path, 0, 0, f"Failed to read file: {e}"))
                continue

            # Gate 5: Encoding & Endings
            if not check_paths_only:
                validate_encoding_and_endings(rel_path, raw_bytes, report)

            # Decode text
            try:
                content = raw_bytes.decode('utf-8')
            except UnicodeDecodeError as e:
                report.add(Violation('encoding', rel_path, 0, 0, f"Invalid UTF-8 sequence: {e}"))
                continue

            # Gate 2: Path & Leak Validation
            gate2_fixed = validate_path_leaks(rel_path, content, report, auto_fix=auto_fix)
            if auto_fix and gate2_fixed is not None and gate2_fixed != content:
                file_path.write_text(gate2_fixed, encoding='utf-8', newline='\n')
                content = gate2_fixed

            if not check_paths_only:
                # Gate 1: Plaincast
                fixed_content = validate_plaincast(rel_path, content, report, auto_fix=auto_fix)
                if auto_fix and fixed_content is not None and fixed_content != content:
                    file_path.write_text(fixed_content, encoding='utf-8', newline='\n')

                # Gate 4: Skill Frontmatter
                validate_skill_frontmatter(rel_path, content, report)

    return report


def validate_commit_message(msg_path: Path, report: ValidationReport):
    """Validate a commit message for leaks, banned characters, and encoding."""
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

    # Gate 1: Plaincast
    validate_plaincast(Path('COMMIT_MSG'), effective_msg, report, auto_fix=False)

    # Gate 2: Leakguard
    validate_path_leaks(Path('COMMIT_MSG'), effective_msg, report)


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
    parser.add_argument('--verbose', action='store_true', help="Show verbose scan information")
    args = parser.parse_args()

    if args.check_commit_msg:
        msg_file = Path(args.check_commit_msg)
        report = ValidationReport()
        validate_commit_message(msg_file, report)
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

    report = scan_repository(repo_root, check_paths_only=args.check_paths_only, auto_fix=args.fix)

    print(f"\nScanned {report.files_scanned} files across repository.")

    if report.passed:
        print("\n[PASS] All validation gates passed with zero violations.")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Found {len(report.violations)} violation(s):\n")
        for v in report.violations:
            print(f"  {v}")
        print("\nPlease resolve all violations before committing or publishing.")
        sys.exit(1)


if __name__ == '__main__':
    main()
