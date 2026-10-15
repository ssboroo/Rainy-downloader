import unittest, tempfile
from pathlib import Path
from host.core import normalize_url, build_args
from host.storage import Store

class CoreTests(unittest.TestCase):
    def test_urls(self):
        self.assertEqual(normalize_url(' https://youtu.be/abc '), 'https://youtu.be/abc')
        for url in ['file:///x','javascript:alert(1)','https://user:pass@example.com/v','http://127.0.0.1/a','https://localhost/a','https://youtube.com.evil.test/a','https://example.com:123/a']:
            with self.subTest(url=url), self.assertRaises(ValueError): normalize_url(url)
    def test_args(self):
        args=build_args({'url':'https://youtu.be/a','folder':'C:/Монгол хавтас','quality':720,'format':'mp4'}, {'yt_dlp':['python','-m','yt_dlp']})
        self.assertIn('--no-playlist',args)
        self.assertIn('--progress',args)
        self.assertIn('C:/Монгол хавтас', args)
        self.assertEqual(args[-2:],['--','https://youtu.be/a'])
        self.assertIn('height<=?720', ' '.join(args))
    def test_audio(self):
        args=build_args({'url':'https://youtu.be/a','folder':'C:/x','quality':1080,'format':'mp3'}, {'yt_dlp':['python','-m','yt_dlp']})
        self.assertIn('--extract-audio',args)
        self.assertIn('mp3',args)
    def test_queue_durable_duplicate_cancel(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'q.db')
            a=s.enqueue({'url':'https://youtu.be/a','folder':d,'quality':720,'format':'mp4'})
            with self.assertRaises(ValueError): s.enqueue({'url':a['url'],'folder':d})
            self.assertEqual(Store(Path(d)/'q.db').snapshot()['jobs'][0]['id'],a['id'])
            s.update(a['id'],{'status':'downloading'})
            s.recover()
            self.assertEqual(s.snapshot()['jobs'][0]['status'],'interrupted')
            s.update(a['id'],{'status':'cancelled'})
            self.assertTrue(s.enqueue({'url':a['url'],'folder':d}))
    def test_settings_validation(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'q.db')
            with self.assertRaises(ValueError): s.settings({'quality':-1})
            self.assertEqual(s.settings({'quality':720})['quality'],720)

if __name__=='__main__': unittest.main()

class RaceTests(unittest.TestCase):
    def test_cancelled_is_terminal(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'q.db'); j=s.enqueue({'url':'https://youtu.be/x','folder':d})
            s.update(j['id'],{'status':'cancelled'})
            for state in ['downloading','processing','done','error']:
                s.update(j['id'],{'status':state,'progress':100})
                self.assertEqual(s.get(j['id'])['status'],'cancelled')
    def test_old_active_jobs_remain_addressable(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'q.db'); first=s.enqueue({'url':'https://youtu.be/first','folder':d})
            s.update(first['id'],{'status':'downloading'})
            for i in range(205):
                j=s.enqueue({'url':f'https://youtu.be/{i}','folder':d});s.update(j['id'],{'status':'done'})
            self.assertEqual(s.get(first['id'])['status'],'downloading')
            s.recover();self.assertEqual(s.get(first['id'])['status'],'interrupted')
            self.assertIn(first['id'],[j['id'] for j in s.snapshot()['jobs']])

class SnapshotSizeTests(unittest.TestCase):
    def test_large_history_snapshot_stays_below_frame_limit(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'q.db')
            for i in range(200):
                j=s.enqueue({'url':'https://example.com/'+str(i)+'x'*3900,'folder':d,'title':'Я'*300})
                s.update(j['id'],{'status':'error','error':'Я'*1400})
            snap=s.snapshot()
            self.assertLess(len(json.dumps(snap,ensure_ascii=False).encode()),900000)
            self.assertGreater(snap['omitted'],0)

class AudioQualityTests(unittest.TestCase):
 def test_mp3_selected_bitrate(self):
  for rate in [128,192,256,320]:
   args=build_args({'url':'https://youtu.be/a','folder':'C:/x','format':'mp3','audio_quality':rate},{'yt_dlp':['yt-dlp']})
   self.assertEqual(args[args.index('--audio-quality')+1],str(rate)+'K')
 def test_audio_quality_is_saved_and_validated(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/'q.db');s.settings({'audio_quality':320,'showFloating':False})
   j=s.enqueue({'url':'https://youtu.be/audio','folder':d,'format':'mp3'})
   self.assertEqual(j['audio_quality'],320)
   self.assertFalse(s.settings()['showFloating'])
   with self.assertRaises(ValueError):s.settings({'audio_quality':999})

class FacebookFormatTests(unittest.TestCase):
 def test_unknown_height_formats_have_fallback(self):
  args=build_args({'url':'https://www.facebook.com/reel/123','folder':'C:/x','format':'mp4'},{'yt_dlp':['yt-dlp']})
  selector=args[args.index('--format')+1]
  self.assertIn('height<=?1080',selector)
  self.assertIn('--recode-video',args)

class OutputQualityTests(unittest.TestCase):
 def test_video_quality_outputs_do_not_collide(self):
  outputs=[]
  for quality in [360,1080]:
   args=build_args({'url':'https://youtu.be/a','folder':'C:/x','quality':quality,'format':'mp4'},{'yt_dlp':['yt-dlp']})
   outputs.append(args[args.index('--output')+1])
  self.assertNotEqual(*outputs)
