import codecs, io, encodings
import traceback
from encodings import utf_8
from .tokenizer import pyxl_tokenize, pyxl_untokenize

def pyxl_transform(stream):
    try:
        output = pyxl_untokenize(pyxl_tokenize(stream.readline))
    except Exception as ex:
        print(ex)
        traceback.print_exc()
        raise

    return output.rstrip()

def pyxl_transform_string(input):
    stream = io.StringIO(bytes(input).decode('utf-8'))
    return pyxl_transform(stream)

def pyxl_decode(input, errors='strict'):
    return pyxl_transform_string(input), len(input)

class PyxlIncrementalDecoder(utf_8.IncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b''
            return super().decode(
                pyxl_transform_string(buff).encode('utf-8'), final=True)
        else:
            return ''

class PyxlStreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = io.StringIO(pyxl_transform(self.stream))

def search_function(encoding):
    if encoding != 'mixt': return None
    # Assume utf8 encoding
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name = 'mixt',
        encode = utf8.encode,
        decode = pyxl_decode,
        incrementalencoder = utf8.incrementalencoder,
        incrementaldecoder = PyxlIncrementalDecoder,
        streamreader = PyxlStreamReader,
        streamwriter = utf8.streamwriter)

# This import will do the actual registration with codecs
import mixt.codec.fast_register
