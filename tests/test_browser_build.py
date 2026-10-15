import unittest,tempfile,json
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('browser_build','build-tools/browser_extensions.py');module=module_from_spec(spec);spec.loader.exec_module(module)
class BrowserBuildTests(unittest.TestCase):
 def test_browser_outputs(self):
  with tempfile.TemporaryDirectory() as d:
   module.build(Path(d))
   chrome=json.loads((Path(d)/'chromium/manifest.json').read_text(encoding='utf-8'))
   firefox=json.loads((Path(d)/'firefox/manifest.json').read_text(encoding='utf-8'))
   self.assertIn('service_worker',chrome['background'])
   self.assertEqual(firefox['browser_specific_settings']['gecko']['id'],'downloader@rainy.local')
   self.assertIn('scripts',firefox['background'])
   self.assertNotIn('import ',(Path(d)/'firefox/background-firefox.js').read_text(encoding='utf-8'))
   self.assertTrue((Path(d)/'chromium/video-controls.js').is_file())
