import pytest

def test_rg():
    from hyperer.rg import main
    output = []
    # Search for the one copy of the word 'INCIDENTAL' in the license file
    main(['hyperer-rg', '--pretty', 'INCIDENTAL', 'LICENSE'], output.append)

    assert not output[0].startswith(b'\x1b]8;'), "Header line doesn't start with a link to the file"
    assert b'hyperer/LICENSE#605:19\x1b\\\x1b' in output[1], "The match line links to the line"

    assert b'INCIDENTAL' in output[1], "The match line contains the searched word INCIDENTAL"
    assert output[1].endswith(b'THE\n\x1b]8;;\x1b\\')

def test_no_format_altering_flags_rg():
    from hyperer.rg import main
    output = []
    # Search for the one copy of the word 'INCIDENTAL' in the license file
    with pytest.raises(SystemExit):
        main(['hyperer-rg', '--column', 'INCIDENTAL', 'LICENSE'], output.append)

def test_rg_multimatch():
    from hyperer.rg import main
    output = []
    # Search for the two copies of the word 'earlier' in the license file. They're on the same line.
    main(['hyperer-rg', '--pretty', 'earlier', 'LICENSE'], output.append)

    assert not output[0].startswith(b'\x1b]8;'), "Header line doesn't start with a link to the file"
    assert b'hyperer/LICENSE#87:1\x1b\\\x1b' in output[1], "The match line links to the line"

    assert b'earlier' in output[1], "The match line contains the searched word earlier"
    assert output[1].endswith(b'work.\n\x1b]8;;\x1b\\')

def test_cargo_compile_failure(monkeypatch):
    from hyperer.cargo import main
    output = []
    monkeypatch.chdir('test_rust_projects/compile_fails')
    import re
    main(['hyperer-cargo', 'check'], output.append)
    assert output[2].startswith(b'\x1b]8;line=3:column=2;file://')
    assert output[2].endswith(b'/hyperer/test_rust_projects/compile_fails/src/main.rs#3:2\x1b\\ --> src/main.rs:3:2\n\x1b]8;;\x1b\\')
