import json, struct
LIMIT=1024*1024

def read_exact(stream,n):
    result=bytearray()
    while len(result)<n:
        b=stream.read(n-len(result))
        if not b: raise ValueError('Дутуу мессеж.')
        result.extend(b)
    return bytes(result)

def read_frame(stream):
    header=stream.read(4)
    if not header: return None
    if len(header)!=4: raise ValueError('Мессежийн толгой буруу.')
    size=struct.unpack('<I',header)[0]
    if not 0<size<=LIMIT: raise ValueError('Мессежийн хэмжээ хэтэрсэн.')
    try: data=json.loads(read_exact(stream,size))
    except (json.JSONDecodeError,UnicodeDecodeError,RecursionError): raise ValueError('Мессежийн бүтэц буруу.')
    if not isinstance(data,dict): raise ValueError('Мессеж object байх ёстой.')
    stack=[(data,0)]
    while stack:
        node,depth=stack.pop()
        if depth>64: raise ValueError('Мессежийн бүтэц хэт гүн байна.')
        if isinstance(node,dict): stack.extend((v,depth+1) for v in node.values() if isinstance(v,(dict,list)))
        elif isinstance(node,list): stack.extend((v,depth+1) for v in node if isinstance(v,(dict,list)))
    return data

def write_frame(stream,message):
    data=json.dumps(message,ensure_ascii=False).encode('utf-8')
    if len(data)>LIMIT: raise ValueError('Хариу хэт том байна.')
    stream.write(struct.pack('<I',len(data))+data); stream.flush()
