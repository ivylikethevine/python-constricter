-- none-ls (null-ls): a diagnostics source for constricter, reading the buffer from standard input.
-- path:line:col: severity: CODE message
local null_ls = require('null-ls')
local h = require('null-ls.helpers')

local constricter = h.make_builtin({
  name = 'constricter',
  method = null_ls.methods.DIAGNOSTICS,
  filetypes = { 'python' },
  generator_opts = {
    command = 'constricter',
    args = { '--quiet', '--stdin-filename', '$FILENAME', '-' },
    to_stdin = true,
    format = 'line',
    check_exit_code = function(code) return code <= 1 end, -- 1 means "offences found"
    on_output = h.diagnostics.from_pattern(
      '[^:]+:(%d+):(%d+): (%a+): (%w+) (.+)',
      { 'row', 'col', 'severity', 'code', 'message' },
      { severities = { error = h.diagnostics.severities.error, warning = h.diagnostics.severities.warning } }
    ),
  },
  factory = h.generator_factory,
})

null_ls.setup({ sources = { constricter } })
