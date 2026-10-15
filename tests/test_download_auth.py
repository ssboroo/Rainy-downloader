import unittest,importlib.util
s=importlib.util.spec_from_file_location('download_auth','build-tools/download_tools.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class DownloadAuthTests(unittest.TestCase):
 def test_token_only_sent_to_github_api(self):
  self.assertEqual(m.request_headers('https://api.github.com/repos/x/y/releases/latest','test-token')['Authorization'],'Bearer test-token')
  self.assertNotIn('Authorization',m.request_headers('https://github.com/x/y/releases/download/a/b','test-token'))
  self.assertNotIn('Authorization',m.request_headers('https://evil.test/','test-token'))
