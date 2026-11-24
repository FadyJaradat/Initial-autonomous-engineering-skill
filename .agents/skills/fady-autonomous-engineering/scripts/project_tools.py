#!/usr/bin/env python3
"""Small, offline, best-effort project bootstrap/index/ownership audit."""
import argparse
import ast
import json
import os
import socket
from pathlib import Path
import subprocess
import sys

SKIP = {'.git', '.codex', '.venv', 'venv', 'node_modules', 'dist', 'build', 'target', '__pycache__', '.next', 'vendor', 'coverage', '.tox', '.pytest_cache'}
EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.kt', '.php', '.rb', '.cs', '.html', '.css', '.scss', '.vue', '.svelte', '.sql', '.sh', '.yaml', '.yml', '.toml', '.json', '.md', '.dockerfile'}
MAX_FILES = 12000
MAX_SYMBOL_BYTES = 350000
OWNER_REL = '.codex/LOCAL_OWNER.json'

def invoking_identity(require_non_root=False):
    """Resolve the interactive user's POSIX identity, including a sudo caller."""
    try:
        import grp
        import pwd
    except ImportError as exc:
        raise ValueError('POSIX account lookup is unavailable on this host') from exc
    is_root = os.geteuid() == 0
    uid = int(os.environ.get('SUDO_UID', os.getuid())) if is_root else os.getuid()
    gid = int(os.environ.get('SUDO_GID', os.getgid())) if is_root else os.getgid()
    if uid <= 0 or gid <= 0:
        raise ValueError('ambiguous root-only session; run as the intended non-root host user')
    try:
        user = pwd.getpwuid(uid)
        group = grp.getgrgid(gid)
    except (KeyError, ImportError) as exc:
        raise ValueError('cannot resolve the invoking POSIX user/group') from exc
    if require_non_root and is_root:
        raise ValueError('refusing project writes as root; rerun as the intended non-root host user')
    return {'username': user.pw_name, 'group': group.gr_name, 'uid': uid, 'gid': gid,
            'host': socket.gethostname()}

def owner_record(root):
    path = safe_path(root, OWNER_REL)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('invalid local owner record; inspect it before reinitializing') from exc
    required = {'username', 'group', 'uid', 'gid', 'host'}
    if not isinstance(data, dict) or not required.issubset(data):
        raise ValueError('incomplete local owner record; inspect it before reinitializing')
    return data

def assert_owner(root):
    current = invoking_identity(require_non_root=True)
    recorded = owner_record(root)
    if recorded is None:
        raise ValueError('local owner not initialized; run project_tools.py init as the intended user')
    keys = ('uid', 'gid', 'host')
    if any(recorded[k] != current[k] for k in keys):
        raise ValueError('invoking host identity differs from .codex/LOCAL_OWNER.json; inspect and reinitialize deliberately')
    return current

def root_dir(raw):
    r = Path(raw).expanduser().resolve(strict=True)
    if not r.is_dir():
        raise ValueError('root must be a directory')
    if r == Path('/'):
        raise ValueError('refusing to use filesystem root')
    return r

def safe_path(root, rel):
    p = root / rel
    if not p.resolve().is_relative_to(root):
        raise ValueError(f'path escapes project root: {rel}')
    return p

def discover(root):
    """Prefer Git paths; otherwise bounded os.walk. Do not follow symlink files."""
    items = []
    try:
        result = subprocess.run(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], capture_output=True, timeout=10, check=True)
        candidates = [Path(os.fsdecode(x)) for x in result.stdout.split(b'\0') if x]
    except (FileNotFoundError, subprocess.SubprocessError):
        candidates = []
        for base, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in sorted(dirs) if d not in SKIP and not (Path(base)/d).is_symlink()]
            for fname in sorted(files):
                candidates.append((Path(base)/fname).relative_to(root))
                if len(candidates) >= MAX_FILES:
                    break
            if len(candidates) >= MAX_FILES:
                break
    for rel in candidates:
        if len(items) >= MAX_FILES:
            break
        if any(part in SKIP for part in rel.parts):
            continue
        if len(rel.parts) == 0:
            continue
        p = root/rel
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):
            continue
        if p.suffix.lower() not in EXTENSIONS and p.name not in {'Dockerfile', 'Makefile', 'Procfile', '.env.example'}:
            continue
        try:
            size=p.stat().st_size
        except OSError:
            continue
        if size > 2_000_000:
            continue
        items.append((rel.as_posix(),p,size))
    return sorted(items)

def create_missing(root):
    asset = Path(__file__).resolve().parent.parent/'assets/templates'
    mapping = {'HANDOFF.md':'HANDOFF.md','PROJECT_MAP.md':'PROJECT_MAP.md','RUNNING.md':'RUNNING.md','.codex/PROJECT_MEMORY.md':'PROJECT_MEMORY.md','.codex/DECISIONS.md':'DECISIONS.md','.codex/SKILLS_REGISTRY.md':'SKILLS_REGISTRY.md'}
    created=[]
    for dst,src in mapping.items():
        target=safe_path(root,dst)
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            with target.open('x',encoding='utf-8') as out:
                out.write((asset/src).read_text(encoding='utf-8'))
            created.append(dst)
        except FileExistsError:
            pass
    return created

def initialize_owner(root):
    ident = invoking_identity(require_non_root=True)
    prior = owner_record(root)
    if prior and any(prior[k] != ident[k] for k in ('uid', 'gid', 'host')):
        raise ValueError('existing local owner belongs to another host identity; inspect before replacing it')
    owner_path = safe_path(root, OWNER_REL)
    owner_path.parent.mkdir(parents=True, exist_ok=True)
    if prior is None:
        temp = owner_path.with_name(owner_path.name + '.tmp')
        temp.write_text(json.dumps(ident, indent=2) + '\n', encoding='utf-8')
        os.replace(temp, owner_path)
    ignore_path = safe_path(root, '.codex/.gitignore')
    existing = ignore_path.read_text(encoding='utf-8') if ignore_path.exists() else ''
    additions = []
    for line in ('/LOCAL_OWNER.json', '/cache/'):
        if line not in existing.splitlines(): additions.append(line)
    if additions:
        with ignore_path.open('a', encoding='utf-8') as out:
            if existing and not existing.endswith('\n'): out.write('\n')
            out.write('\n'.join(additions) + '\n')
    cache = safe_path(root, '.codex/cache')
    cache.mkdir(parents=True, exist_ok=True)
    env_path = safe_path(root, '.codex/cache/owner.env')
    env_path.write_text(f"PUID={ident['uid']}\nPGID={ident['gid']}\n", encoding='utf-8')
    return ident

def index(root):
    assert_owner(root)
    file_rows=[]; symbols=[]; skipped=0
    for rel,p,size in discover(root):
        file_rows.append({'path':rel,'bytes':size,'type':p.suffix.lower() or p.name})
        if p.suffix.lower() != '.py' or size>MAX_SYMBOL_BYTES:
            continue
        try:
            tree=ast.parse(p.read_text(encoding='utf-8'),filename=rel)
        except (SyntaxError, UnicodeError, OSError, ValueError):
            skipped+=1;continue
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                kind='class' if isinstance(node,ast.ClassDef) else 'function'
                symbols.append({'file':rel,'line':node.lineno,'name':node.name,'kind':kind})
    output=safe_path(root,'.codex');output.mkdir(exist_ok=True)
    for fname,obj in [('FILE_INDEX.json',{'note':'Navigation-only. Not a complete dependency index.', 'files':file_rows}),('SYMBOL_INDEX.json',{'note':'Top-level Python AST symbols only. Verify against source.', 'symbols':symbols})]:
        dst=safe_path(root,'.codex/'+fname)
        tmp=dst.with_name(dst.name+'.tmp')
        with tmp.open('w',encoding='utf-8') as f:
            json.dump(obj,f,ensure_ascii=False,indent=2)
            f.write('\n')
        os.replace(tmp,dst)
    return {'files':len(file_rows),'python_symbols':len(symbols),'python_parse_errors':skipped}

def ownership(root):
    recorded=owner_record(root)
    if recorded is None:
        return {'status':'unavailable','reason':'run init as the intended host user before ownership audit'}
    uid=recorded['uid']; gid=recorded['gid']
    mismatches=[];scanned=0
    # audit excludes external mounted dirs by device ID, never follows symlink dirs
    dev=root.stat().st_dev
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if (Path(base)/d).is_symlink() is False and (Path(base)/d).stat().st_dev == dev and d != '.git']
        for name in dirs+files:
            p=Path(base)/name
            if p.is_symlink():continue
            try: s=p.stat()
            except OSError:continue
            if s.st_dev!=dev:continue
            scanned+=1
            if (s.st_uid,s.st_gid)!=(uid,gid) and len(mismatches)<100:
                mismatches.append(p.relative_to(root).as_posix())
    return {'status':'pass' if not mismatches else 'mismatch','scanned':scanned,'first_100_mismatches':mismatches,'truncated':len(mismatches)==100,'required_uid':uid,'required_gid':gid,'recorded_host':recorded['host']}

def status(root):
    docs=['HANDOFF.md','PROJECT_MAP.md','RUNNING.md','.codex/PROJECT_MEMORY.md','.codex/FILE_INDEX.json','.codex/SYMBOL_INDEX.json']
    return {'root':str(root),'docs':{name:safe_path(root,name).is_file() for name in docs}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['owner','init','index','status','ownership'])
    parser.add_argument('--root',default='.')
    args=parser.parse_args()
    try:
        root=root_dir(args.root)
        if args.command=='owner': result={'owner':invoking_identity()}
        elif args.command=='init':
            ident=initialize_owner(root)
            created=create_missing(root)
            result={'owner':ident,'created':created}
        elif args.command=='index': result=index(root)
        elif args.command=='ownership':result=ownership(root)
        else:result=status(root)
        print(json.dumps(result,indent=2))
        return 0 if result.get('status') not in {'mismatch','unavailable'} else 2
    except (OSError,ValueError) as e:
        print(f'error: {e}',file=sys.stderr)
        return 1

if __name__=='__main__':
    sys.exit(main())
