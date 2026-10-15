import unittest,tempfile,sqlite3,importlib.util
from pathlib import Path
from unittest.mock import patch
from host.storage import Store
class WindowsRegressionTests(unittest.TestCase):
 def test_context_closes_connection_even_if_reference_retained(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(Path(d)/'q.db')
   with store.db() as connection:connection.execute('SELECT 1').fetchone()
   try:
    with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
   finally:connection.close()
 def test_context_closes_connection_on_exception(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(Path(d)/'q.db')
   try:
    with store.db() as connection:raise ValueError('rollback')
   except ValueError:pass
   try:
    with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
   finally:connection.close()
 def test_browser_build_uses_utf8_under_legacy_windows_locale(self):
  spec=importlib.util.spec_from_file_location('windows_browser_build','build-tools/browser_extensions.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  original_read=Path.read_text;original_write=Path.write_text
  def legacy_read(path,*args,**kwargs):
   kwargs.setdefault('encoding','cp1252');return original_read(path,*args,**kwargs)
  def legacy_write(path,data,*args,**kwargs):
   kwargs.setdefault('encoding','cp1252');return original_write(path,data,*args,**kwargs)
  with tempfile.TemporaryDirectory() as d,patch.object(Path,'read_text',legacy_read),patch.object(Path,'write_text',legacy_write):
   module.build(Path(d))
