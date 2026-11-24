import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import shutil

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/code_index.py'
INIT=Path(__file__).resolve().parents[1]/'scripts/project_tools.py'

class CodeIndexTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'pkg').mkdir()
        (self.root/'pkg/core.py').write_text('def work():\n    return 42\n\nclass A:\n    def action(self):\n        return work()\n')
        (self.root/'consumer.py').write_text('from pkg import core\n')
        (self.root/'web').mkdir()
        (self.root/'web/app.ts').write_text('import { run } from "./utils";\nexport function app() {}\n')
        (self.root/'web/utils.ts').write_text('export function run() {}\n')
        (self.root/'node_modules').mkdir()
        (self.root/'node_modules/no.py').write_text('def ignored(): pass')
        subprocess.run([sys.executable,str(INIT),'init','--root',str(self.root)],check=True,capture_output=True)
    def tool(self,*args):
        proc=subprocess.run([sys.executable,str(SCRIPT),*args,'--root',str(self.root)],capture_output=True,text=True)
        return proc, json.loads(proc.stdout) if proc.stdout else None
    def test_incremental_and_lookup(self):
        p,d=self.tool('build');self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(d['changed'],4)
        p,d=self.tool('build');self.assertEqual(d['changed'],0);self.assertEqual(d['unchanged'],4)
        p,d=self.tool('find','--query','action');self.assertEqual(d['symbols'][0]['name'],'A.action')
        p,d=self.tool('find','--query','ignored');self.assertEqual(d['symbols'],[])
        (self.root/'pkg/core.py').write_text('def new(): pass\n')
        p,d=self.tool('build');self.assertEqual(d['changed'],1);self.assertEqual(d['unchanged'],3)
        p,d=self.tool('find','--query','action');self.assertEqual(d['symbols'],[])
        (self.root/'pkg/core.py').unlink()
        p,d=self.tool('build');self.assertEqual(d['deleted'],1)
    def test_impact(self):
        self.tool('build')
        p,d=self.tool('impact','--path','web/utils.ts');self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([r['file'] for r in d['possible_importers']],['web/app.ts'])
        p,d=self.tool('impact','--path','pkg/core.py');self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([r['file'] for r in d['possible_importers'] if r['via']=='pkg.core'],['consumer.py'])
    def test_invalid_path(self):
        self.tool('build')
        p,d=self.tool('impact','--path','../etc/passwd');self.assertNotEqual(p.returncode,0)
    def test_parse_failure_drops_stale_content(self):
        self.tool('build')
        (self.root/'pkg/core.py').write_text('def broken(:\n')
        p,d=self.tool('build');self.assertEqual(p.returncode,2);self.assertEqual(d['skipped'],1)
        p,d=self.tool('find','--query','work');self.assertEqual(d['symbols'],[])

    def test_included_sample_fixture(self):
        fixture=Path(__file__).parent/'fixtures'/'sample_project'
        shutil.copytree(fixture,self.root,dirs_exist_ok=True)
        subprocess.run([sys.executable,str(INIT),'init','--root',str(self.root)],check=True,capture_output=True)
        p,d=self.tool('build');self.assertEqual(p.returncode,0,p.stderr)
        p,d=self.tool('find','--query','authenticate');self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(any(row['name']=='authenticate' for row in d['symbols']))
        p,d=self.tool('impact','--path','web/view.ts');self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([row['file'] for row in d['possible_importers']],['web/app.ts'])

if __name__=='__main__':unittest.main()
