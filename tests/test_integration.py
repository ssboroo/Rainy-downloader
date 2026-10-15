import io,json,os,shutil,struct,subprocess,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
from host.storage import Store
from host.worker import download,acquire_lock
from host.native import inspect
from host.protocol import write_frame,read_frame

class IntegrationTests(unittest.TestCase):
    def test_worker_real_child_produces_file(self):
        with tempfile.TemporaryDirectory(prefix='rainy Монгол ') as d:
            fake=Path(d)/'fake.py'
            fake.write_text("import pathlib,sys\np=pathlib.Path(sys.argv[sys.argv.index('--paths')+1])/'Монгол файл.mp4'\np.write_bytes(b'test-media')\nprint('RAINY_PROGRESS:{\"downloaded_bytes\":100,\"total_bytes\":100,\"speed\":5,\"eta\":0}',flush=True)\nprint('RAINY_FILE:'+str(p),flush=True)\n",encoding='utf-8')
            s=Store(Path(d)/'q.db');j=s.enqueue({'url':'https://youtu.be/x','folder':d})
            with patch('host.worker.tools',return_value={'yt_dlp':[sys.executable,str(fake)]}): download(s,j)
            r=s.get(j['id']);self.assertEqual(r['status'],'done');self.assertTrue(Path(r['output_path']).is_file())
    def test_worker_cancel_real_process(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)/'fake.py';fake.write_text('import time\ntime.sleep(20)\n',encoding='utf-8')
            s=Store(Path(d)/'q.db');j=s.enqueue({'url':'https://youtu.be/x','folder':d});errors=[]
            def go():
                try:
                    with patch('host.worker.tools',return_value={'yt_dlp':[sys.executable,str(fake)]}):download(s,j)
                except Exception as e:errors.append(e)
            t=threading.Thread(target=go);t.start()
            deadline=time.monotonic()+5
            while s.get(j['id'])['status']!='downloading' and time.monotonic()<deadline:time.sleep(.01)
            self.assertEqual(s.get(j['id'])['status'],'downloading')
            s.update(j['id'],{'status':'cancelled'});t.join(timeout=5)
            self.assertFalse(t.is_alive());self.assertEqual(errors,[]);self.assertEqual(s.get(j['id'])['status'],'cancelled')
    def test_inspection_timeout_is_explained(self):
        with patch('host.native.subprocess.run',side_effect=subprocess.TimeoutExpired('yt-dlp',65)):
            with self.assertRaisesRegex(ValueError,'хугацаа'):inspect('https://youtu.be/x')
    def test_single_worker_lock(self):
        with tempfile.TemporaryDirectory() as d:
            lock=acquire_lock(Path(d)/'worker.lock');self.assertIsNotNone(lock)
            try:self.assertIsNone(acquire_lock(Path(d)/'worker.lock'))
            finally:lock.close()
    def test_native_process_roundtrip_and_origin(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree('host',root/'host',ignore=shutil.ignore_patterns('__pycache__'))
            (root/'native-config.json').write_text(json.dumps({'extension_id':'a'*32}),encoding='utf-8')
            env={**os.environ,'LOCALAPPDATA':str(root/'user')}
            f=io.BytesIO();write_frame(f,{'id':1,'action':'snapshot','payload':{}})
            p=subprocess.run([sys.executable,'-m','host.native','chrome-extension://'+'a'*32+'/'],input=f.getvalue(),capture_output=True,cwd=root,env=env,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr.decode());r=read_frame(io.BytesIO(p.stdout));self.assertTrue(r['ok']);self.assertEqual(r['data']['jobs'],[])
            p=subprocess.run([sys.executable,'-m','host.native','chrome-extension://'+'b'*32+'/'],input=f.getvalue(),capture_output=True,cwd=root,env=env,timeout=10)
            self.assertEqual(p.stdout,b'')
