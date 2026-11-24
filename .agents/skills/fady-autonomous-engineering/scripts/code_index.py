#!/usr/bin/env python3
"""Offline, bounded, incremental NAVIGATION index. No external dependencies.

AST parsing is exact for Python top-level/nested definitions and imports. Other languages
use deliberately conservative text heuristics; imports are not a complete call graph.
Never use index results alone to make a security or behavior conclusion.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import sys
import time

from project_tools import root_dir, discover, safe_path, assert_owner

SCHEMA_VERSION = 2
DB_REL = '.codex/cache/code_index.sqlite3'
SOURCE_EXT = {'.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.kt', '.php', '.rb', '.cs', '.vue', '.svelte'}
JS_EXT = {'.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'}
# Purposefully only common declarations, not semantic identifiers.
PATTERNS = {
    'js': re.compile(r'^\s*(?:(?:export|default|declare|async|public|private|protected|static|abstract)\s+)*(?:function|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)|^\s*(?:(?:export|declare)\s+)*(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=', re.M),
    'go': re.compile(r'^\s*(?:func\s+(?:\([^\n]*?\)\s*)?|type\s+)([A-Za-z_]\w*)\b', re.M),
    'rs': re.compile(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:fn|struct|enum|trait|mod)\s+([A-Za-z_]\w*)\b', re.M),
    'generic': re.compile(r'^\s*(?:(?:public|private|protected|static|final|abstract|internal|async)\s+)*(?:class|interface|enum|struct)\s+([A-Za-z_]\w*)\b', re.M),
}
JS_IMPORT = re.compile(r'\b(?:import\s+(?:[^;\n]*?\s+from\s+)?|export\s+[^;\n]*?\s+from\s+|require\s*\(\s*)[\'\"](\.[^\'\"]+)[\'\"]', re.M)
GO_IMPORT = re.compile(r'^\s*import\s+(?:\(\s*)?[\'\"]([^\'\"]+)[\'\"]', re.M)


def connect(root, create=True):
    target = safe_path(root, DB_REL)
    if not create and not target.exists():
        raise FileNotFoundError('index missing; run build first')
    if create:
        target.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(target))
    db.execute('PRAGMA busy_timeout=5000')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, bytes INTEGER, language TEXT);
    CREATE TABLE IF NOT EXISTS symbols (path TEXT NOT NULL, line INTEGER NOT NULL, name TEXT NOT NULL, kind TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS imports (path TEXT NOT NULL, target TEXT NOT NULL, kind TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS symbols_by_name ON symbols(name);
    CREATE INDEX IF NOT EXISTS imports_by_target ON imports(target);
    ''')
    prior = db.execute('SELECT value FROM meta WHERE key="schema"').fetchone()
    if prior and int(prior[0]) != SCHEMA_VERSION:
        db.close()
        raise ValueError('schema mismatch: delete the disposable .codex/cache/code_index.sqlite3 and rebuild')
    db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ('schema', str(SCHEMA_VERSION)))
    return db


def lang(path):
    ext = Path(path).suffix.lower()
    return {'.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript', '.py':'python'}.get(ext, ext[1:])


def python_items(text, path):
    tree = ast.parse(text, filename=path)
    symbols = []
    imports = []
    def walk(nodes, prefix=''):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + node.name
                symbols.append((path, node.lineno, name, 'class' if isinstance(node, ast.ClassDef) else 'function'))
                walk(node.body, name + '.')
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((path, alias.name, 'python-module'))
                else:
                    dots = '.' * node.level
                    base = dots + (node.module or '')
                    imports.append((path, base, 'python-module'))
                    for alias in node.names:
                        imports.append((path, (base + '.' + alias.name) if base else alias.name, 'python-module'))
    walk(tree.body)
    return symbols, imports


def generic_items(text, path):
    ext=Path(path).suffix.lower()
    pattern=PATTERNS['js'] if ext in JS_EXT else PATTERNS['go'] if ext=='.go' else PATTERNS['rs'] if ext=='.rs' else PATTERNS['generic']
    symbols=[]
    for match in pattern.finditer(text):
        name=next((x for x in match.groups() if x), None)
        if name:
            symbols.append((path, text.count('\n',0,match.start())+1, name, 'heuristic-declaration'))
    imports=[]
    if ext in JS_EXT:
        for match in JS_IMPORT.finditer(text):
            imports.append((path,match.group(1),'js-relative'))
    return symbols, imports


def build(root, force=False):
    assert_owner(root)
    started=time.perf_counter()
    db=connect(root)
    changed=0; unchanged=0; deleted=0; skipped=0; errors=[]
    candidates=[(name,path,size) for name,path,size in discover(root) if Path(name).suffix.lower() in SOURCE_EXT]
    known={row[0]:row[1] for row in db.execute('SELECT path,sha256 FROM files')}
    current=set()
    for name,path,size in candidates:
        current.add(name)
        try:
            raw=path.read_bytes()
            h=hashlib.sha256(raw).hexdigest()
            if not force and known.get(name)==h:
                unchanged+=1
                continue
            text=raw.decode('utf-8')
            symbols, imports = python_items(text,name) if path.suffix.lower()=='.py' else generic_items(text,name)
            with db:
                db.execute('DELETE FROM symbols WHERE path=?',(name,))
                db.execute('DELETE FROM imports WHERE path=?',(name,))
                db.execute('INSERT OR REPLACE INTO files VALUES (?,?,?,?)',(name,h,size,lang(name)))
                db.executemany('INSERT INTO symbols VALUES (?,?,?,?)', symbols)
                db.executemany('INSERT INTO imports VALUES (?,?,?)', imports)
            changed+=1
        except (SyntaxError, UnicodeError, OSError, ValueError) as exc:
            skipped+=1
            if len(errors)<20: errors.append({'path':name,'error':str(exc)[:150]})
            # Remove stale map for changed files that can no longer be parsed.
            with db:
                db.execute('DELETE FROM files WHERE path=?',(name,))
                db.execute('DELETE FROM symbols WHERE path=?',(name,))
                db.execute('DELETE FROM imports WHERE path=?',(name,))
    for name in known.keys()-current:
        with db:
            db.execute('DELETE FROM files WHERE path=?',(name,))
            db.execute('DELETE FROM symbols WHERE path=?',(name,))
            db.execute('DELETE FROM imports WHERE path=?',(name,))
        deleted+=1
    result={'changed':changed,'unchanged':unchanged,'deleted':deleted,'skipped':skipped,
            'total':len(candidates),'seconds':round(time.perf_counter()-started,4),
            'errors':errors,'coverage':'Python AST + heuristic non-Python declarations/imports; navigation only'}
    db.close()
    return result


def lookup(root, query, limit=30):
    db=connect(root,False)
    q='%'+query.lower().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
    rows=db.execute('SELECT path,line,name,kind FROM symbols WHERE lower(name) LIKE ? ESCAPE "\\" ORDER BY name,path,line LIMIT ?', (q,limit)).fetchall()
    files=db.execute('SELECT path,language FROM files WHERE lower(path) LIKE ? ESCAPE "\\" ORDER BY path LIMIT ?', (q,limit)).fetchall()
    db.close()
    return {'symbols':[dict(zip(('path','line','name','kind'),r)) for r in rows], 'files':[dict(zip(('path','language'),r)) for r in files], 'note':'Source is authoritative; verify before edits.'}


def impact(root, path):
    path=PurePosixPath(path).as_posix()
    if path.startswith('/') or '..' in PurePosixPath(path).parts:
        raise ValueError('path must be repository-relative')
    db=connect(root,False)
    tracked={x[0] for x in db.execute('SELECT path FROM files')}
    if path not in tracked:
        raise ValueError('file not in index; run build and check path')
    stem=path.rsplit('.',1)[0]
    package=stem.replace('/','.')
    direct=[]
    for source,target,kind in db.execute('SELECT path,target,kind FROM imports WHERE path != ?', (path,)):
        matches=False
        if kind=='python-module':
            matches=(target==package or target.startswith(package+'.'))
        elif kind=='js-relative':
            base=(PurePosixPath(source).parent / target)
            stack=[]
            for part in base.parts:
                if part=='..':
                    if stack: stack.pop()
                elif part!='.': stack.append(part)
            normalized='/'.join(stack)
            matches=normalized in (stem,path,stem+'/index') or path.startswith(normalized+'/index.')
        if matches:
            direct.append({'file':source,'via':target,'kind':kind})
    db.close()
    return {'target':path,'possible_importers':direct[:100], 'truncated':len(direct)>100,
            'limitations':'Import-level approximation; not call graph. Python package resolution, aliases, dynamic imports, and JS aliases may be missing.'}


def stats(root):
    db=connect(root,False)
    result={name:db.execute(f'SELECT count(*) FROM {name}').fetchone()[0] for name in ['files','symbols','imports']}
    result['database_bytes']=safe_path(root,DB_REL).stat().st_size
    db.close()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['build','find','impact','stats'])
    parser.add_argument('--root',default='.')
    parser.add_argument('--query')
    parser.add_argument('--path')
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args()
    try:
        root=root_dir(args.root)
        if args.command=='build': result=build(root,args.force)
        elif args.command=='find':
            if not args.query: parser.error('--query is required for find')
            result=lookup(root,args.query)
        elif args.command=='impact':
            if not args.path: parser.error('--path is required for impact')
            result=impact(root,args.path)
        else: result=stats(root)
        print(json.dumps(result,indent=2))
        return 0 if not (args.command=='build' and result['skipped']) else 2
    except (OSError,ValueError,sqlite3.Error) as exc:
        print(f'error: {exc}',file=sys.stderr)
        return 1

if __name__=='__main__': sys.exit(main())
