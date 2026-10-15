import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from desktop.controller import Controller
from host.runtime import executable_command,tool_command
from host.browser_install import manifests
class DesktopTests(unittest.TestCase):
 def test_frozen_and_source_command(self):
  self.assertEqual(executable_command('worker',frozen=True,exe='C:/RAINY/RAINY.exe'),['C:/RAINY/RAINY.exe','--worker'])
  self.assertEqual(executable_command('worker',frozen=False,exe='python'),['python','-m','host.worker'])
 def test_external_tool(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'tools';p.mkdir();(p/'yt-dlp.exe').touch()
   self.assertEqual(tool_command(Path(d),'python'),[str(p/'yt-dlp.exe')])
 def test_browser_manifests(self):
  m=manifests(Path('C:/RAINY'), 'a'*32)
  self.assertEqual(m['chromium']['allowed_origins'],['chrome-extension://'+'a'*32+'/'])
  self.assertEqual(m['firefox']['allowed_extensions'],['downloader@rainy.local'])
  self.assertIn('RAINY.Native.exe',m['chromium']['path'])
 def test_enqueue_and_settings(self):
  with tempfile.TemporaryDirectory() as d:
   c=Controller(Path(d)/'q.db')
   c.save_settings({'folder':d,'quality':720,'format':'mp4','oneClick':False})
   with patch('desktop.controller.health',return_value={'ready':True}),patch('desktop.controller.ensure_worker'):
    r=c.enqueue('https://youtu.be/abc','Монгол видео')
   self.assertEqual(c.snapshot()['jobs'][0]['id'],r['id'])
   c.cancel(r['id']);self.assertEqual(c.snapshot()['jobs'][0]['status'],'cancelled')

class MissingToolTests(unittest.TestCase):
 def test_frozen_missing_ytdlp_never_spawns_gui(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileNotFoundError):tool_command(Path(d),'C:/RAINY/RAINY.exe',frozen=True)

class AsyncTests(unittest.TestCase):
 def test_non_submission_completion_cannot_unlock_submission(self):
  from desktop.tasks import TaskRunner
  runner=TaskRunner();self.assertTrue(runner.begin_submission());self.assertFalse(runner.begin_submission())
  runner.completed(None,{},None,submission=False)
  runner.drain(lambda c,v,e:None)
  self.assertTrue(runner.submission_active)
  runner.completed(None,None,None,submission=True);runner.drain(lambda c,v,e:None)
  self.assertFalse(runner.submission_active)

class DatabaseResponsivenessTests(unittest.TestCase):
 def test_locked_writer_does_not_block_task_runner_drain(self):
  import threading,time
  from desktop.tasks import TaskRunner
  with tempfile.TemporaryDirectory() as d:
   controller=Controller(Path(d)/'q.db');runner=TaskRunner();started=threading.Event()
   connection=controller.store.db();connection.execute('BEGIN IMMEDIATE')
   def write():started.set();return controller.save_settings({'quality':720})
   thread=runner.submit(write)
   self.assertTrue(started.wait(2));time.sleep(.03)
   begin=time.monotonic();runner.drain(lambda c,v,e:None)
   self.assertLess(time.monotonic()-begin,.15)
   self.assertTrue(thread.is_alive())
   connection.rollback();connection.close();thread.join(timeout=3)
   self.assertFalse(thread.is_alive());self.assertEqual(controller.store.settings()['quality'],720)
