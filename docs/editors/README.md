# Editors

Settings that show the `LVA` codes as you type, each a file here to copy into a project. Install
`python-constricter` in the environment the editor runs Python from (the project's virtualenv), and
put the level and other settings in `pyproject.toml`'s `[tool.constricter]`, which the CLI reads
too; the flake8 and pylint plugins take theirs as `constricter-*` options (README,
[Use](../../README.md#use)).

## VS Code

[`vscode-settings.json`](vscode-settings.json), merged into `.vscode/settings.json`, turns on both
plugins through Microsoft's
[Flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8) and
[Pylint](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) extensions (one is
enough). `"flake8.importStrategy": "fromEnvironment"` matters: the extension otherwise runs its own
bundled flake8, which can't see the plugin
([vscode-flake8#318](https://github.com/microsoft/vscode-flake8/issues/318)); pylint's needs
`--load-plugins`.

## Zed

Zed's Python support runs language servers only, and constricter doesn't have one yet (README,
Roadmap). Until it does, [`zed-tasks.json`](zed-tasks.json), as `.zed/tasks.json`, adds tasks that
run the CLI on the current file (with source lines: `--format=full`), on the project, or `--fix` the
file, from the command palette's `task: spawn`.

## Neovim

Both read the buffer from standard input, so a check doesn't wait for a save:

- [nvim-lint](https://github.com/mfussenegger/nvim-lint): [`nvim-lint.lua`](nvim-lint.lua) registers
  constricter and runs it for Python; trigger it as you do your other linters
  (`require('lint').try_lint()` on `BufWritePost`, say).
- [none-ls](https://github.com/nvimtools/none-ls.nvim): [`none-ls.lua`](none-ls.lua) is a
  diagnostics source for `null_ls.setup`.

Both parse the text output (`path:line:col: severity: CODE message`), so a path with a `:` in it (a
Windows drive letter) needs the pattern's `[^:]+` loosened.

## Checked

The Neovim patterns were checked against the CLI's output with Neovim's own Lua, and each file
parses; none of these has yet been tried end to end in its editor.
