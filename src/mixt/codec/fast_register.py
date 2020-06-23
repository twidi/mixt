import codecs

def search_function(encoding):
    if encoding != 'mixt':
        return None
    import mixt.codec.register
    return mixt.codec.register.search_function(encoding)

codecs.register(search_function)
