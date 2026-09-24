#!/usr/bin/env python3
"""
Release helper used by .github/workflows/release.yml.

Given a release tag (v1.7.1), it checks the tag matches the version in pyproject.toml
and that CHANGELOG.md has a section for it, then writes the release title and notes.

CHANGELOG section headings follow the documented format:
    ## [1.7.1] 2026-09-25
    ## [1.7.1] 2026-09-25 - Optional release title
The optional title becomes "v1.7.1 - Optional release title"; otherwise the title is the tag.

Usage:
    python scripts/release_notes.py v1.7.1 --notes-out notes.md --title-out title.txt
Exit code 1 with a message on any mismatch, so the release job stops before publishing.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r'^v(\d+\.\d+\.\d+)$')


class ReleaseError(Exception):
    pass


def version_from_tag(tag: str) -> str:
    m = TAG_RE.match(tag.strip())
    if not m:
        raise ReleaseError(f"Tag '{tag}' is not a release tag of the form vX.Y.Z")
    return m.group(1)


def pyproject_version(text: str) -> str:
    in_project = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('['):
            in_project = stripped == '[project]'
            continue
        m = re.match(r'^version\s*=\s*"([^"]+)"', stripped)
        if in_project and m:
            return m.group(1)
    raise ReleaseError("No version found in the [project] table of pyproject.toml")


def changelog_section(text: str, version: str) -> Tuple[Optional[str], str]:
    """Return (optional title, body) of the '## [version]' section."""
    heading = re.compile(r'^## \[' + re.escape(version) + r'\][^\n]*$', re.MULTILINE)
    m = heading.search(text)
    if not m:
        raise ReleaseError(f"CHANGELOG.md has no '## [{version}]' section")
    title_m = re.match(r'^## \[[^\]]+\]\s+\S+\s+-\s+(.+?)\s*$', m.group(0))
    rest = text[m.end():]
    nxt = re.search(r'^## \[', rest, re.MULTILINE)
    body = rest[:nxt.start()] if nxt else rest
    body = re.sub(r'\n-{3,}\s*$', '', body.strip()).strip()
    if not body:
        raise ReleaseError(f"CHANGELOG.md section [{version}] is empty")
    return (title_m.group(1) if title_m else None), body + '\n'


def is_newest(tag: str, all_tags) -> bool:
    """True when tag is the highest vX.Y.Z within its major version.

    Only then may the floating major tag (v1) move and the release be marked Latest;
    a hotfix for an older line (v1.6.4 after v1.8.0) must not move v1 backwards.
    """
    version = tuple(int(x) for x in version_from_tag(tag).split('.'))
    same_major = [tuple(int(x) for x in m.group(1).split('.'))
                  for m in (TAG_RE.match(t.strip()) for t in all_tags) if m]
    same_major = [v for v in same_major if v[0] == version[0]]
    return version >= max(same_major, default=version)


def build_release(tag: str, root: Path = REPO_ROOT) -> Tuple[str, str]:
    """Validate tag against the repo and return (title, notes)."""
    version = version_from_tag(tag)
    declared = pyproject_version((root / 'pyproject.toml').read_text(encoding='utf-8'))
    if declared != version:
        raise ReleaseError(f"Tag {tag} does not match pyproject.toml version {declared}; "
                           "bump the version before tagging")
    title, notes = changelog_section((root / 'CHANGELOG.md').read_text(encoding='utf-8'), version)
    return (f"{tag} - {title}" if title else tag), notes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('tag')
    parser.add_argument('--notes-out')
    parser.add_argument('--title-out')
    parser.add_argument('--root', default=str(REPO_ROOT))
    parser.add_argument('--is-newest', action='store_true',
                        help="Print 'true' if tag is the highest vX.Y.Z of its major version (reads git tags)")
    args = parser.parse_args(argv)
    if args.is_newest:
        try:
            tags = subprocess.run(['git', '-C', args.root, 'tag', '--list'], capture_output=True,
                                  text=True, check=True).stdout.split()
            print('true' if is_newest(args.tag, tags) else 'false')
        except (ReleaseError, OSError, subprocess.CalledProcessError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0
    if not (args.notes_out and args.title_out):
        parser.error('--notes-out and --title-out are required')
    try:
        title, notes = build_release(args.tag, Path(args.root))
    except ReleaseError as e:
        print(f"Error: {e}")
        return 1
    Path(args.notes_out).write_text(notes, encoding='utf-8', newline='\n')
    Path(args.title_out).write_text(title + '\n', encoding='utf-8', newline='\n')
    print(f"Release title: {title}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
