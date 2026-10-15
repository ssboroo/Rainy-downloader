import unittest
from desktop.browser_capture import address_url,is_browser_executable
class BrowserCaptureTests(unittest.TestCase):
 def test_address_urls(self):
  self.assertEqual(address_url('www.youtube.com/watch?v=abc'),'https://www.youtube.com/watch?v=abc')
  self.assertEqual(address_url('https://x.com/user/status/123'),'https://x.com/user/status/123')
  for value in ['search words here','chrome://settings','file:///C:/x','localhost:8000','https://user:pass@example.com']:
   with self.subTest(value=value),self.assertRaises(ValueError):address_url(value)
 def test_browser_executables(self):
  for name in ['chrome.exe','msedge.exe','brave.exe','opera.exe','firefox.exe','vivaldi.exe']:self.assertTrue(is_browser_executable(name))
  self.assertFalse(is_browser_executable('notepad.exe'))

class NativeAddressTests(unittest.TestCase):
 def test_web_form_address_is_never_trusted(self):
  from desktop.browser_capture import trusted_address_control
  self.assertTrue(trusted_address_control('Address and search bar','',['ToolBar','Pane','Window']))
  self.assertFalse(trusted_address_control('Address','',['Group','Document','Pane','Window']))
  self.assertFalse(trusted_address_control('Address','',['Pane','Window']))
  self.assertTrue(trusted_address_control('Search','urlbar-input',['Pane','Window']))
  self.assertFalse(trusted_address_control('Search','urlbar-input',['Document','Window']))
