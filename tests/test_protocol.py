import io, json, struct, unittest
from host.protocol import read_frame, write_frame
class ProtocolTests(unittest.TestCase):
    def test_round_trip(self):
        f=io.BytesIO(); write_frame(f,{'ok':True,'title':'Монгол бичлэг'}); f.seek(0)
        self.assertEqual(read_frame(f)['title'],'Монгол бичлэг')
    def test_bad_frames(self):
        for b in [b'x',struct.pack('<I',2000000),struct.pack('<I',20)+b'{}',struct.pack('<I',2)+b'[]']:
            with self.subTest(b=b),self.assertRaises(ValueError): read_frame(io.BytesIO(b))
        self.assertIsNone(read_frame(io.BytesIO()))

class DeepFrameTests(unittest.TestCase):
    def test_deep_json_is_controlled_error(self):
        b=b'{"x":'+b'['*2000+b'0'+b']'*2000+b'}'
        with self.assertRaises(ValueError): read_frame(io.BytesIO(struct.pack('<I',len(b))+b))
    def test_invalid_utf8(self):
        with self.assertRaises(ValueError):read_frame(io.BytesIO(struct.pack('<I',1)+b'\xff'))
