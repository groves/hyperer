`hyperer` adds [terminal hyperlinks] to the output of other commands.
For example, `hyperer-rg` runs [ripgrep] and links to the files it finds.

[terminal hyperlinks]: https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
[ripgrep]: https://github.com/BurntSushi/ripgrep


Installation
============
Install Python 3.9 or later and run `pip install hyperer` to install the hyperer commands into your system Python.
Alternatively, if you're using the [Nix package manager], depend on the flake.nix in this repo.

[Nix package manager]: https://nixos.org/manual/nix/stable/introduction.html

Commands
========
* hyperer-rg - wraps [ripgrep] and links to files it finds
* hyperer-cargo - wraps [cargo] and links to compilation failures, test failures, and backtraces

[cargo]: https://doc.rust-lang.org/cargo/

Credit
======
The basic idea and `hyperer-rg` comes from [kitty].
[hyperlinked_grep] is kitty's version of `hyperer-rg`.
If you only want ripgrep links and you already have kitty installed, you can run `kitty +kitten hyperlinked_grep` and you don't need to install `hyperer`.
I created this project to have a home for `hyperer-cargo` and to be able to hyperlink ripgrep without installing all of kitty.

[kitty]: https://sw.kovidgoyal.net/kitty/
[hyperlinked_grep]: https://sw.kovidgoyal.net/kitty/kittens/hyperlinked_grep/

Many thanks to the kitty project!
Consider [sponsoring its creator][sponsor Kovid] to help move the terminal forward.

[sponsor Kovid]: https://github.com/sponsors/kovidgoyal
