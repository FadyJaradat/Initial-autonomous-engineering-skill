#!/usr/bin/env python3
"""Append one concise, explicit handoff entry without replacing existing content."""
import argparse
from datetime import datetime, timezone
import re
import sys
from pathlib import Path
from project_tools import root_dir, safe_path, assert_owner

SECTIONS=('Goal','Current state','Active files','Changes made','Failed attempts / pitfalls','Next steps','Other carry-over details')
SECRET_PATTERNS=(
    re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),
    re.compile(r'\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}'),
    re.compile(r'\bsk-[A-Za-z0-9_-]{20,}'),
    re.compile(r'https?://[^/\s:@]+:[^/\s@]+@'),
    re.compile(r'(?i)\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|password|passwd)\s*[:=]\s*[^\s,;]+'),
)


def add(root,section,entry):
    assert_owner(root)
    target=safe_path(root,'HANDOFF.md')
    if not target.exists():
        raise ValueError('HANDOFF.md missing; run project_tools.py init first')
    if not entry.strip():
        raise ValueError('entry cannot be empty')
    if len(entry)>8000:
        raise ValueError('entry too long; summarize before updating')
    if any(pattern.search(entry) for pattern in SECRET_PATTERNS):
        raise ValueError('entry appears to contain a credential; remove it before updating')
    text=target.read_text(encoding='utf-8')
    # Match top-level and numbered headings with exact section names.
    lines=text.splitlines(keepends=True)
    start=None
    for i,line in enumerate(lines):
        candidate=line.strip().lstrip('#').strip()
        if candidate==section or (candidate[:2] in [str(n)+'.' for n in range(1,8)] and candidate[3:].strip()==section):
            start=i
            break
    if start is None:
        raise ValueError('section missing from existing HANDOFF.md; refuse to alter unknown structure')
    end=len(lines)
    for i in range(start+1,len(lines)):
        if lines[i].lstrip().startswith('#') and lines[i].lstrip().startswith('# '):
            end=i
            break
    stamp=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    bullet='- '+stamp+' — '+entry.strip().replace('\n','\n  ')+'\n'
    if bullet in text:
        return False
    lines.insert(end, '\n'+bullet)
    target.write_text(''.join(lines),encoding='utf-8')
    return True


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',default='.')
    ap.add_argument('--section',required=True,choices=SECTIONS)
    ap.add_argument('--entry',required=True)
    args=ap.parse_args()
    try:
        print('updated' if add(root_dir(args.root),args.section,args.entry) else 'unchanged')
        return 0
    except (OSError,ValueError) as exc:
        print('error: '+str(exc),file=sys.stderr)
        return 1
if __name__=='__main__':sys.exit(main())
