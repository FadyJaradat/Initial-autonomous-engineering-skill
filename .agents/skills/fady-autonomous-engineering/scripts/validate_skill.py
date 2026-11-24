#!/usr/bin/env python3
"""Portable minimal skill validation. Does not replace host Codex discovery testing."""
import argparse
import re
from pathlib import Path
import sys

def validate(root):
    errors=[]
    text=(root/'SKILL.md').read_text(encoding='utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        errors.append('SKILL.md missing YAML frontmatter')
    else:
        header=text.split('---',2)[1]
        if not re.search(r'^name:\s*fady-autonomous-engineering\s*$',header,re.M): errors.append('invalid skill name')
        if not re.search(r'^description:\s*\S+',header,re.M): errors.append('description missing')
        if any(re.search(r'^'+key+r':',header,re.M) for key in ['version','author','tags']): errors.append('unsupported frontmatter fields')
    if not (root/'agents/openai.yaml').exists():errors.append('agents/openai.yaml missing')
    refs=set(re.findall(r'`(references/[A-Za-z0-9_.-]+\.md)`',text))
    for name in refs:
        if not (root/name).is_file(): errors.append('missing referenced file: '+name)
    if 'project_tools.py' not in text:errors.append('missing project tool instructions')
    return errors

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    args=ap.parse_args()
    try: errors=validate(args.root)
    except OSError as exc: errors=[str(exc)]
    if errors:
        for e in errors:print('ERROR '+e,file=sys.stderr)
        sys.exit(1)
    print('skill metadata and listed references valid')
