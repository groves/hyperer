from hyperer.rg import link_match

multimatch = b'\x1b[0m\x1b[32m87\x1b[0m:\x1b[0m\x1b[1m\x1b[31mearlier\x1b[0m work or a work "based on" the \x1b[0m\x1b[1m\x1b[31mearlier\x1b[0m work.\n'

def test_multimatch():
    output = link_match(multimatch, b'LICENSE', b'87', 3)
    assert output.startswith(b'\x1b]8;line=87:column=1;file://')
    assert b';line=87:column=1;' in output
    assert output.endswith(b' work.\n\x1b]8;;\x1b\\')

separable = b'\x1b[0m\x1b[32m293\x1b[0m:  A \x1b[0m\x1b[1m\x1b[31mseparable\x1b[0mportion of the object code, whose source code is excluded\n'

def test_single():
    output = link_match(separable, b'LICENSE', b'293', 4)
    assert output.startswith(b'\x1b]8;line=293:column=5;file://')
    assert b';line=293:column=5;' in output
    
no_color = b'\x1b[0m\x1b[32m293\x1b[0m:  A \x1b[0m\x1b[1mseparable\x1b[0mportion of the object code, whose source code is excluded\n'

def test_no_color():
    output = link_match(no_color, b'LICENSE', b'293', 4)
    assert output.startswith(b'\x1b]8;line=293;')
    assert b'column' not in output
