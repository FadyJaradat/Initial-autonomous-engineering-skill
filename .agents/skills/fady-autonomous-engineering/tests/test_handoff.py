from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/handoff.py'
INIT=Path(__file__).resolve().parents[1]/'scripts/project_tools.py'
class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        subprocess.run([sys.executable,str(INIT),'init','--root',str(self.root)],check=True,capture_output=True)
    def test_update_preserves_sections(self):
        before=(self.root/'HANDOFF.md').read_text()
        p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--section','Changes made','--entry','Validated a targeted fix'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        after=(self.root/'HANDOFF.md').read_text()
        self.assertIn('Validated a targeted fix',after)
        self.assertIn('Other carry-over details',after)
        self.assertGreater(len(after),len(before))
    def test_reject_missing_section(self):
        (self.root/'HANDOFF.md').write_text('# Unknown\n')
        p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--section','Next steps','--entry','x'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual((self.root/'HANDOFF.md').read_text(),'# Unknown\n')
    def test_rejects_credential_like_entry(self):
        before=(self.root/'HANDOFF.md').read_text()
        p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--section','Changes made','--entry','api_key=example-secret'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual((self.root/'HANDOFF.md').read_text(),before)
if __name__=='__main__':unittest.main()
