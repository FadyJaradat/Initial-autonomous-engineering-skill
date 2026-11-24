import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/project_tools.py'

class ProjectToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def run_tool(self,cmd):
        return subprocess.run([sys.executable,str(SCRIPT),cmd,'--root',str(self.root)],capture_output=True,text=True)
    def test_init_idempotent_and_preserves_docs(self):
        (self.root/'HANDOFF.md').write_text('CUSTOM')
        self.assertEqual(self.run_tool('init').returncode,0)
        self.assertEqual((self.root/'HANDOFF.md').read_text(),'CUSTOM')
        self.assertEqual(json.loads(self.run_tool('init').stdout)['created'],[])
        self.assertTrue((self.root/'RUNNING.md').exists())
        self.assertEqual(json.loads((self.root/'.codex/LOCAL_OWNER.json').read_text())['uid'],os.getuid())
        self.assertIn('/LOCAL_OWNER.json',(self.root/'.codex/.gitignore').read_text())
        self.assertIn(f'PUID={os.getuid()}',(self.root/'.codex/cache/owner.env').read_text())

    def test_owner_command_reports_current_user(self):
        result=self.run_tool('owner')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['owner']['uid'],os.getuid())
    def test_index_and_exclusions(self):
        self.assertEqual(self.run_tool('init').returncode,0)
        (self.root/'main.py').write_text('def hello():\n  return 1\nclass Thing:\n  pass\n')
        (self.root/'node_modules').mkdir();(self.root/'node_modules'/'bad.py').write_text('def bad(): pass')
        result=self.run_tool('index'); self.assertEqual(result.returncode,0,result.stderr)
        ix=json.loads((self.root/'.codex/FILE_INDEX.json').read_text())
        sy=json.loads((self.root/'.codex/SYMBOL_INDEX.json').read_text())
        self.assertEqual(set(row['path'] for row in ix['files']),{'HANDOFF.md','PROJECT_MAP.md','RUNNING.md','main.py'})
        self.assertEqual({row['name'] for row in sy['symbols']},{'hello','Thing'})
    def test_status(self):
        res=self.run_tool('status');self.assertEqual(res.returncode,0)
        self.assertFalse(json.loads(res.stdout)['docs']['HANDOFF.md'])
    def test_reject_filesystem_root(self):
        res=subprocess.run([sys.executable,str(SCRIPT),'init','--root','/'],capture_output=True,text=True)
        self.assertNotEqual(res.returncode,0)
    def test_ownership_is_audit_only(self):
        self.assertEqual(self.run_tool('init').returncode,0)
        before=sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        res=self.run_tool('ownership'); self.assertIn(res.returncode,(0,2))
        after=sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        self.assertEqual(after,before)

    def test_write_guard_rejects_different_recorded_uid(self):
        self.assertEqual(self.run_tool('init').returncode,0)
        owner_path=self.root/'.codex/LOCAL_OWNER.json'
        owner=json.loads(owner_path.read_text())
        owner['uid']+=10000
        owner_path.write_text(json.dumps(owner))
        result=self.run_tool('index')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.root/'.codex/FILE_INDEX.json').exists())

if __name__=='__main__':unittest.main()
