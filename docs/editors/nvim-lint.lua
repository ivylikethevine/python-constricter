-- nvim-lint: register constricter, then list it for Python, e.g. in your init.lua.
-- Reads the buffer from standard input; the offences carry the buffer's name.
-- path:line:col: severity: CODE message
local pattern = '[^:]+:(%d+):(%d+): (%a+): (%w+) (.+)'
local groups = { 'lnum', 'col', 'severity', 'code', 'message' }
local severities = {
  error = vim.diagnostic.severity.ERROR,
  warning = vim.diagnostic.severity.WARN,
}

require('lint').linters.constricter = {
  cmd = 'constricter',
  stdin = true,
  args = {
    '--quiet',
    '--stdin-filename',
    function() return vim.api.nvim_buf_get_name(0) end,
    '-',
  },
  ignore_exitcode = true, -- 1 means "offences found"
  parser = require('lint.parser').from_pattern(pattern, groups, severities, { source = 'constricter' }),
}

require('lint').linters_by_ft.python = { 'constricter' }
