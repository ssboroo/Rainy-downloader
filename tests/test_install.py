import unittest,json,hashlib,base64,re
from pathlib import Path
from host.install_config import native_manifest,extension_id
class InstallTests(unittest.TestCase):
 def test_manifest(self):
  m=native_manifest('a'*32,'C:/Монгол хавтас/start-host.cmd')
  self.assertEqual(m['allowed_origins'],['chrome-extension://'+'a'*32+'/'])
  self.assertEqual(m['type'],'stdio')
  with self.assertRaises(ValueError):native_manifest('bad','x')
 def test_extension_has_stable_id(self):
  m=json.loads(Path('extension/manifest.json').read_text(encoding='utf-8'))
  id=extension_id(m['key'])
  self.assertRegex(id,r'^[a-p]{32}$')
  self.assertIn(id,Path('windows/install.ps1').read_text(encoding='utf-8-sig'))
