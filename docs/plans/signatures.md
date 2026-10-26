# Signatures from the project's own inference: how to build it

The roadmap's "Signatures from the project's own inference". Today `returned` decides an
unannotated function's return where its `return`s agree (`Returned.calls`, certain;
`Returned.methods`, guesses), `callers` a parameter every call passes one type, `fixture` a test's;
each types only the locals bound to them. No edit writes `-> T` on the `def` or `: T` on a parameter
(`Edit` is `annotate`, `replace`, `declare`).

## The pieces

1. **Two opt-in codes**, as LVA012 and LVA013 are (`OPT_IN`, `Checks.final`/`attributes`):
   LVA014, a function with no return annotation; LVA015, a parameter with none. Reported only when
   selected by full code, since ruff's ANN201/ANN001 report them already; their point is the fix.
   Messages in `MESSAGES`, levels in `LEVELS` (strict, as LVA013), each written up in the README's
   rules table and FIXES.md.
2. **An edit kind for the header**, `Edit.SIGNATURE`: `-> T` inserted before the `:` that ends
   the header (the colon found by tokens past the parameters' closing parenthesis, as
   `scratch/righttyper_added.py` does), or `: T` after a parameter's name. `fixes.replacement`
   gains the case; `Fix.span` holds the colon's line and column. Imports as any fix's
   (`Fix.imports`, `guarded`).
3. **What decides them**, all already computed in a check:
   - return: `Returned.calls[name]` (certain for a plain function), `Returned.methods[C][m]` (a
     guess: a subclass may return another), `-> None` where no `return` gives a value and the body
     doesn't end in a `raise` only (`returned` knows); a generator's `Generator[...]`/`Iterator[...]`
     from its `yield`s where `returned` types them.
   - parameter: `Seeded.callers` (a guess, kind `callers`), `fixture` (a guess).
   - kinds: `returned` for the return, `callers`/`fixture` for parameters; certain only where the
     return is a plain function's.
4. **The knock-on**: a module whose function now declares `-> T` turns its callers' `returned`
   guesses in other files into `Known.calls` (certain) on the next run: nothing to build, but the
   measure (step 6) reads it.
5. **Tests**: `tests/fix/values/test_signature_fixes.py`: `-> int` from agreeing returns,
   `-> None`, a method's as a guess, a generator, a parameter by its callers, the colon found past
   a default with a `:` in a lambda or a dict, a multi-line header, a header with a comment, and no
   fix where the `def` is a stub (`...` body) or decorated `@overload`.
6. **Measure** (the done criterion): on the corpora, `--select LVA014 --fix` alone, then each
   package's own type checker (the `types` step) for new errors; and `--fix` on pandas twice, the
   second after the first's signatures, counting the callers' fixes that become certain.

## Order and size

Codes and the header edit with returns only (steps 1, 2, 3's return), tests, then a pydantic and
pandas measure: about 6 hours. Parameters (`callers`, `fixture`) after: about 4. The roadmap's 10
hours stands.
