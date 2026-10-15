import unittest, tempfile
from pathlib import Path
from host.worker import parse_progress, safe_output, stop_process
from host.native import summarize_info, check_origin
class WorkerTests(unittest.TestCase):
    def test_progress(self):
        self.assertEqual(parse_progress('RAINY_PROGRESS:{"downloaded_bytes":500,"total_bytes":1000,"speed":30,"eta":7}')['progress'],50)
        self.assertIsNone(parse_progress('something else'))
        self.assertIsNone(parse_progress('RAINY_PROGRESS:garbage'))
    def test_file_paths(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(safe_output(str(Path(d)/'Монгол видео.mp4'),d),str((Path(d)/'Монгол видео.mp4').resolve()))
            with self.assertRaises(ValueError): safe_output(str(Path(d)/'../escape.mp4'),d)
    def test_inspect_playlist(self):
        r=summarize_info({'_type':'playlist','title':'Playlist','entries':[{'id':'a','url':'https://youtu.be/a','title':'A'},None]})
        self.assertTrue(r['playlist']); self.assertEqual(r['count'],1); self.assertEqual(r['entries'][0]['url'],'https://youtu.be/a')
    def test_untrusted_thumbnail(self):
        self.assertEqual(summarize_info({'title':'x','thumbnail':'file:///x'})['thumbnail'],'')
    def test_origin(self):
        with self.assertRaises(ValueError): check_origin('chrome-extension://'+'a'*32+'/', 'b'*32)
        check_origin('chrome-extension://'+'a'*32+'/', 'a'*32)
