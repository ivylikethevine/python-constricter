# Next up: what `--fix` can't type yet

Every untyped binding (`LVA001`, `LVA002`) in the ten corpora that `--fix` offers nothing for, not
even a guess, by the statement that binds it (`assign`, `unpack`, `loop`, `with`, `walrus`) and the
shape of its value. [Findings](#findings) says what's behind the biggest categories and what could
type more of them; the [raw list](#raw-list) is at the end.

Measured 2026-09-22 on 0.2.4-rc.2 with Python 3.14.7, at the default level, over the standard
library, `requests`, `flask`, `django`, `sqlalchemy`, `fastapi`, `pydantic`, `rich`, `sentry_sdk`
and Twisted 12.3.0: 145,707 untyped bindings, 111,694 of them with no fix at all.

How to read a category: `call: module.func()` is a call to a function of an imported module
(`os.path.join(...)`); `call: module function (unannotated)` one to a function this module defines
without a return annotation; `self.method()` / `local.method()` / `param.method()` a method on
`self`, a local or an (unannotated) parameter; `chained` anything longer (`a.b.c()`); `copy` a plain
name whose type isn't known.

## Findings

**Most of it is unannotated code, which nothing can anchor.** In the standard library, Django,
Twisted and sentry-sdk, 95–100% of the bindings `--fix` can't type are in functions with no
annotations at all: an unannotated parameter's type is unknown, and so is everything computed from
it. Only a type checker's whole-program inference reaches that (the roadmap's type-checker-backed
inference, a Large item).

| Corpus           | Untyped |       No fix | No fix, in a function with no annotations |
| ---------------- | ------: | -----------: | ----------------------------------------: |
| standard library | 101,206 | 75,537 (75%) |                              74,466 (99%) |
| requests         |     365 |    295 (81%) |                                    6 (2%) |
| flask            |     308 |    256 (83%) |                                    0 (0%) |
| django           |  12,077 | 10,963 (91%) |                             10,963 (100%) |
| sqlalchemy       |  10,069 |  8,776 (87%) |                               4,979 (57%) |
| fastapi          |     614 |    487 (79%) |                                    0 (0%) |
| pydantic         |   2,457 |  1,942 (79%) |                                   62 (3%) |
| rich             |   1,856 |  1,414 (76%) |                                    0 (0%) |
| sentry_sdk       |   2,119 |  1,979 (93%) |                               1,885 (95%) |
| twisted          |  14,636 | 10,045 (69%) |                             10,045 (100%) |

**Annotated code is where more inference pays.** `requests`, `flask`, `fastapi`, `pydantic` and
`rich` still leave 77% (4,303 of 5,600) untyped, even with the CLI's cross-module return types
(which type only about 140 more). Sampling those, by likely gain in annotated code:

1. **Classes from other checked modules.** A local or parameter annotated with an imported class
   gets nothing from its attributes or methods (`field_info.get_constraints()`,
   `prepared_request.headers`, `Text.from_markup(...)`, `Table.grid(...)`): `project.Index` holds
   only functions. Indexing each class's annotated attributes, `@property` returns, and methods' and
   classmethods' declared returns, as `classes` and `method_returns` already do within a module,
   reaches the `local.method()`, `param.method()`, `param.x`, `local.x` and chained categories: up
   to ~900 of the 4,303 (a category-level upper bound). The largest item; certain fixes, under the
   rules the same-module ones follow.
2. **Done: `@property` returns as attributes**, in the same module too (`layout = self.layout`,
   where `layout` is a property declaring its return). Small, certain, and the first half of 1.
3. **Done: `cls` in a classmethod**, typed as its class the way `self` is (`cls.max_digits`,
   `cls.apply_default_parts(...)`). Small and certain for attributes and declared returns;
   `cls(...)` itself is `Self`, not the class, so it stays out.
4. **Done: `typing.cast(T, x)`** is `T`, by definition: 117 across the corpus (pydantic uses it
   most). Tiny and certain: the annotation is the first argument as written (or a string's
   contents).
5. **Standard-library functions with a builtin result**, resolved by import as the builtins table is
   (`time.time`, `time.monotonic` → `float`; `textwrap.dedent`, `os.getcwd` → `str`; `os.open`,
   `random.randrange` → `int`; `struct.pack` → `bytes`; `os.environ.get(k)` → `str | None`). 8,242
   untyped bindings call a standard-library function; the 100 most-called cover 5,434, of which
   those with a builtin, non-generic result are roughly 900. Small: a curated table, as `str`
   methods have. `AnyStr` functions (`os.path.join`, `re.escape`) only when their arguments' types
   are known.
6. **Fixes that add an import.** Many results need a name the file doesn't import:
   `with open(path, "rb") as f` is an `io.BufferedReader` (813 `open` calls with a literal mode, 125
   more with none), `logging.getLogger()` a `logging.Logger`, `datetime(...)` a `datetime`, and
   LVA012's fix would be `Final`. Adding (or extending) an import safely enables all of them.
   Medium: where to put it, `from __future__` and `TYPE_CHECKING` blocks, an alias already taken.
7. **Empty containers filled later**: `x = []` then `x.append(v)` in the same function, every `v`
   known and agreeing, gives `list[T]` (likewise `{}` with `x[k] = v`, and `set()` with `.add`). At
   least 558 of the 4,180 empty containers (counting only values typed on their own; more with the
   scope's types); 961 are never filled where they're made. A guess: something else may add to it.
8. **Return types of unannotated functions**, from their `return` statements, when every one is
   typed and they agree (and the function can't fall off its end): at least 656 calls to same-file
   functions and methods, mostly in unannotated code. A guess for a method (a subclass may override
   it); medium effort, since the callee's scope must be checked before the caller's.
9. **`x = None`, later rebound**: `T | None` when every other binding's type is known, from value
   flow. At least 100 of 971. Small.

Left alone on purpose: `getattr(...)` (881), bound-method aliases (`append = parts.append`, a `rich`
idiom whose type is a long `Callable`), `dict.get` on a `dict[str, Any]` (it's `Any`), and `a or b`
or conditionals whose sides differ (a union, better left to the author).

## Raw list

| Count | Share | Binding: value                                 |
| ----: | ----: | ---------------------------------------------- |
| 8,360 |  7.5% | assign: call: module.func()                    |
| 8,337 |  7.5% | assign: call: chained attr.method()            |
| 7,765 |  7.0% | assign: call: self.method()                    |
| 6,434 |  5.8% | assign: call: local.method()                   |
| 3,602 |  3.2% | assign: binop (unknown operand)                |
| 3,554 |  3.2% | assign: call: imported function                |
| 3,550 |  3.2% | loop: copy: other name                         |
| 3,066 |  2.7% | assign: empty list                             |
| 2,933 |  2.6% | unpack: call: self.method()                    |
| 2,866 |  2.6% | assign: attr: self.x                           |
| 2,607 |  2.3% | assign: attr: chained                          |
| 2,486 |  2.2% | assign: call: other name (local/param/nested)  |
| 2,157 |  1.9% | assign: attr: local.x                          |
| 2,022 |  1.8% | loop: tuple (mixed/unknown elements)           |
| 2,013 |  1.8% | assign: subscript: other                       |
| 1,957 |  1.8% | assign: None literal                           |
| 1,729 |  1.5% | assign: call: param.method()                   |
| 1,648 |  1.5% | unpack: call: module.func()                    |
| 1,627 |  1.5% | assign: subscript: local[...]                  |
| 1,618 |  1.4% | assign: call: module function (unannotated)    |
| 1,435 |  1.3% | with: call: module.func()                      |
| 1,330 |  1.2% | unpack: call: local.method()                   |
| 1,284 |  1.1% | unpack: call: chained attr.method()            |
| 1,241 |  1.1% | with: call: self.method()                      |
| 1,200 |  1.1% | loop: copy: param (unannotated)                |
| 1,134 |  1.0% | assign: attr: module.x                         |
| 1,131 |  1.0% | assign: list (mixed/unknown elements)          |
| 1,065 |  1.0% | unpack: call: imported function                |
| 1,019 |  0.9% | assign: ListComp (unknown elements)            |
| 1,011 |  0.9% | loop: call: chained attr.method()              |
|   999 |  0.9% | loop: attr: self.x                             |
|   946 |  0.8% | unpack: tuple (mixed/unknown elements)         |
|   938 |  0.8% | with: call: builtin open()                     |
|   935 |  0.8% | unpack: call: module function (unannotated)    |
|   902 |  0.8% | assign: attr: param.x                          |
|   892 |  0.8% | assign: empty dict                             |
|   884 |  0.8% | assign: call: builtin getattr()                |
|   850 |  0.8% | assign: copy: other name                       |
|   797 |  0.7% | loop: call: local.method()                     |
|   792 |  0.7% | unpack: copy: other name                       |
|   772 |  0.7% | assign: dict (mixed/unknown elements)          |
|   766 |  0.7% | loop: call: builtin enumerate()                |
|   689 |  0.6% | assign: conditional (sides differ/unknown)     |
|   671 |  0.6% | assign: boolop (a or b)                        |
|   659 |  0.6% | with: call: imported function                  |
|   608 |  0.5% | unpack: copy: param (unannotated)              |
|   564 |  0.5% | assign: tuple (mixed/unknown elements)         |
|   518 |  0.5% | loop: list (mixed/unknown elements)            |
|   516 |  0.5% | assign: call: builtin list()                   |
|   486 |  0.4% | assign: call: builtin set()                    |
|   458 |  0.4% | loop: call: param.method()                     |
|   452 |  0.4% | loop: call: builtin zip()                      |
|   440 |  0.4% | loop: call: module.func()                      |
|   415 |  0.4% | assign: subscript: param[...]                  |
|   413 |  0.4% | unpack: call: param.method()                   |
|   398 |  0.4% | loop: call: self.method()                      |
|   395 |  0.4% | with: call: local.method()                     |
|   376 |  0.3% | unpack: subscript: other                       |
|   342 |  0.3% | assign: compare                                |
|   303 |  0.3% | assign: call: builtin object()                 |
|   289 |  0.3% | loop: call: imported function                  |
|   287 |  0.3% | assign: await (unknown)                        |
|   286 |  0.3% | unpack: call: other name (local/param/nested)  |
|   284 |  0.3% | with: call: chained attr.method()              |
|   282 |  0.3% | loop: call: module function (unannotated)      |
|   276 |  0.2% | assign: call: module function (class)          |
|   273 |  0.2% | assign: call: builtin dict()                   |
|   259 |  0.2% | assign: copy: param (unannotated)              |
|   257 |  0.2% | assign: call: other callee                     |
|   243 |  0.2% | assign: lambda                                 |
|   238 |  0.2% | assign: other constant                         |
|   229 |  0.2% | assign: call: builtin bytearray()              |
|   229 |  0.2% | other binding (match capture, ...)             |
|   225 |  0.2% | unpack: subscript: local[...]                  |
|   223 |  0.2% | loop: attr: local.x                            |
|   214 |  0.2% | loop: attr: param.x                            |
|   212 |  0.2% | unpack: await (unknown)                        |
|   212 |  0.2% | loop: attr: chained                            |
|   210 |  0.2% | assign: DictComp (unknown elements)            |
|   185 |  0.2% | assign: call: builtin type()                   |
|   183 |  0.2% | unpack: attr: self.x                           |
|   173 |  0.2% | unpack: attr: local.x                          |
|   169 |  0.2% | assign: call: builtin open()                   |
|   166 |  0.1% | unpack: call: builtin divmod()                 |
|   165 |  0.1% | assign: call: builtin iter()                   |
|   158 |  0.1% | assign: call: builtin memoryview()             |
|   155 |  0.1% | assign: call: builtin next()                   |
|   138 |  0.1% | loop: subscript: local[...]                    |
|   126 |  0.1% | assign: call: builtin tuple()                  |
|   126 |  0.1% | with: call: module function (class)            |
|   124 |  0.1% | loop: call: builtin list()                     |
|   124 |  0.1% | loop: call: builtin sorted()                   |
|   120 |  0.1% | assign: call: builtin compile()                |
|   120 |  0.1% | assign: call: builtin sorted()                 |
|   119 |  0.1% | assign: SetComp (unknown elements)             |
|   111 |  0.1% | loop: subscript: other                         |
|   110 |  0.1% | unpack: call: builtin map()                    |
|   106 |  0.1% | loop: binop (unknown operand)                  |
|   104 |  0.1% | loop: call: other name (local/param/nested)    |
|    97 |  0.1% | assign: GeneratorExp (unknown elements)        |
|    97 |  0.1% | assign: call: builtin max()                    |
|    91 |  0.1% | with: call: other name (local/param/nested)    |
|    86 |  0.1% | assign: call: builtin range()                  |
|    81 |  0.1% | assign: call: module function (annotated)      |
|    79 |  0.1% | unpack: call: builtin next()                   |
|    75 |  0.1% | unpack: ListComp (unknown elements)            |
|    75 |  0.1% | assign: call: builtin min()                    |
|    74 |  0.1% | loop: call: builtin reversed()                 |
|    74 |  0.1% | loop: attr: module.x                           |
|    73 |  0.1% | unpack: call: module function (annotated)      |
|    69 |  0.1% | loop: subscript: param[...]                    |
|    69 |  0.1% | assign: call: capitalised                      |
|    65 |  0.1% | with: call: module function (unannotated)      |
|    62 |  0.1% | walrus: call: local.method()                   |
|    60 |  0.1% | unpack: attr: chained                          |
|    54 |  0.0% | assign: yield                                  |
|    52 |  0.0% | assign: call: builtin eval()                   |
|    48 |  0.0% | assign: empty tuple                            |
|    47 |  0.0% | loop: call: builtin dir()                      |
|    46 |  0.0% | walrus: call: self.method()                    |
|    46 |  0.0% | assign: call: builtin sum()                    |
|    45 |  0.0% | with: copy: other name                         |
|    40 |  0.0% | unpack: subscript: param[...]                  |
|    39 |  0.0% | assign: call: builtin **import**()             |
|    38 |  0.0% | with: call: param.method()                     |
|    37 |  0.0% | unpack: GeneratorExp (unknown elements)        |
|    36 |  0.0% | walrus: call: builtin getattr()                |
|    36 |  0.0% | walrus: call: param.method()                   |
|    32 |  0.0% | walrus: call: chained attr.method()            |
|    31 |  0.0% | assign: unaryop                                |
|    31 |  0.0% | assign: set (mixed/unknown elements)           |
|    30 |  0.0% | with: call: capitalised                        |
|    28 |  0.0% | with: call: builtin memoryview()               |
|    27 |  0.0% | unpack: attr: param.x                          |
|    26 |  0.0% | loop: call: module function (annotated)        |
|    26 |  0.0% | unpack: call: capitalised                      |
|    25 |  0.0% | loop: boolop (a or b)                          |
|    25 |  0.0% | assign: call: builtin map()                    |
|    24 |  0.0% | loop: call: builtin iter()                     |
|    23 |  0.0% | unpack: call: builtin range()                  |
|    22 |  0.0% | assign: call: builtin slice()                  |
|    21 |  0.0% | loop: call: builtin map()                      |
|    21 |  0.0% | walrus: other constant                         |
|    20 |  0.0% | assign: call: builtin frozenset()              |
|    20 |  0.0% | loop: ListComp (unknown elements)              |
|    19 |  0.0% | walrus: call: module.func()                    |
|    19 |  0.0% | assign: call: builtin reversed()               |
|    18 |  0.0% | unpack: call: other callee                     |
|    17 |  0.0% | assign: call: builtin any()                    |
|    17 |  0.0% | loop: call: capitalised                        |
|    16 |  0.0% | walrus: call: other name (local/param/nested)  |
|    16 |  0.0% | unpack: conditional (sides differ/unknown)     |
|    16 |  0.0% | assign: call: builtin dir()                    |
|    16 |  0.0% | assign: call: builtin input()                  |
|    16 |  0.0% | unpack: call: builtin zip()                    |
|    15 |  0.0% | assign: call: builtin zip()                    |
|    14 |  0.0% | assign: call: builtin filter()                 |
|    14 |  0.0% | assign: call: builtin abs()                    |
|    14 |  0.0% | assign: TemplateStr                            |
|    13 |  0.0% | unpack: binop (unknown operand)                |
|    13 |  0.0% | assign: call: builtin locals()                 |
|    12 |  0.0% | assign: call: builtin pow()                    |
|    12 |  0.0% | assign: call: builtin globals()                |
|    12 |  0.0% | assign: call: builtin vars()                   |
|    11 |  0.0% | walrus: attr: self.x                           |
|    11 |  0.0% | walrus: call: imported function                |
|    10 |  0.0% | assign: call: builtin super()                  |
|    10 |  0.0% | loop: call: builtin filter()                   |
|    10 |  0.0% | unpack: call: builtin eval()                   |
|     9 |  0.0% | unpack: call: builtin list()                   |
|     9 |  0.0% | unpack: attr: module.x                         |
|     9 |  0.0% | assign: call: builtin OSError()                |
|     9 |  0.0% | walrus: copy: other name                       |
|     8 |  0.0% | walrus: binop (unknown operand)                |
|     8 |  0.0% | assign: call: builtin all()                    |
|     7 |  0.0% | loop: call: builtin getattr()                  |
|     7 |  0.0% | assign: call: builtin enumerate()              |
|     7 |  0.0% | walrus: attr: param.x                          |
|     7 |  0.0% | loop: GeneratorExp (unknown elements)          |
|     7 |  0.0% | assign: call: builtin (typed, args?)           |
|     7 |  0.0% | walrus: attr: local.x                          |
|     7 |  0.0% | unpack: boolop (a or b)                        |
|     7 |  0.0% | unpack: other constant                         |
|     7 |  0.0% | assign: call: builtin property()               |
|     6 |  0.0% | walrus: call: module function (unannotated)    |
|     6 |  0.0% | unpack: call: builtin sorted()                 |
|     6 |  0.0% | walrus: subscript: local[...]                  |
|     5 |  0.0% | loop: call: builtin tuple()                    |
|     5 |  0.0% | assign: call: builtin anext()                  |
|     5 |  0.0% | assign: call: builtin RuntimeError()           |
|     5 |  0.0% | walrus: call: module function (annotated)      |
|     4 |  0.0% | walrus: attr: chained                          |
|     4 |  0.0% | walrus: call: builtin (typed, args?)           |
|     4 |  0.0% | loop: set (mixed/unknown elements)             |
|     4 |  0.0% | assign: call: builtin format()                 |
|     4 |  0.0% | assign: call: builtin classmethod()            |
|     4 |  0.0% | assign: call: builtin staticmethod()           |
|     4 |  0.0% | loop: conditional (sides differ/unknown)       |
|     4 |  0.0% | walrus: list (mixed/unknown elements)          |
|     4 |  0.0% | walrus: subscript: other                       |
|     3 |  0.0% | assign: call: builtin round()                  |
|     3 |  0.0% | loop: call: builtin vars()                     |
|     3 |  0.0% | loop: call: builtin set()                      |
|     3 |  0.0% | assign: call: builtin aiter()                  |
|     3 |  0.0% | assign: call: builtin ConnectionAbortedError() |
|     3 |  0.0% | assign: call: builtin ConnectionResetError()   |
|     3 |  0.0% | assign: call: builtin divmod()                 |
|     3 |  0.0% | assign: call: builtin hex()                    |
|     3 |  0.0% | loop: call: module function (class)            |
|     2 |  0.0% | walrus: call: builtin next()                   |
|     2 |  0.0% | with: copy: param (unannotated)                |
|     2 |  0.0% | with: subscript: other                         |
|     2 |  0.0% | unpack: dict (mixed/unknown elements)          |
|     2 |  0.0% | loop: empty tuple                              |
|     2 |  0.0% | unpack: call: builtin iter()                   |
|     2 |  0.0% | walrus: tuple (mixed/unknown elements)         |
|     2 |  0.0% | walrus: walrus                                 |
|     2 |  0.0% | unpack: list (mixed/unknown elements)          |
|     2 |  0.0% | unpack: set (mixed/unknown elements)           |
|     2 |  0.0% | walrus: subscript: param[...]                  |
|     2 |  0.0% | loop: walrus                                   |
|     2 |  0.0% | walrus: call: builtin type()                   |
|     2 |  0.0% | with: call: module function (annotated)        |
|     2 |  0.0% | unpack: call: builtin min()                    |
|     1 |  0.0% | with: attr: local.x                            |
|     1 |  0.0% | with: conditional (sides differ/unknown)       |
|     1 |  0.0% | unpack: SetComp (unknown elements)             |
|     1 |  0.0% | with: subscript: local[...]                    |
|     1 |  0.0% | walrus: call: capitalised                      |
|     1 |  0.0% | assign: call: builtin exec()                   |
|     1 |  0.0% | unpack: call: module function (class)          |
|     1 |  0.0% | walrus: call: builtin tuple()                  |
|     1 |  0.0% | walrus: ListComp (unknown elements)            |
|     1 |  0.0% | assign: call: builtin ascii()                  |
|     1 |  0.0% | loop: empty list                               |
|     1 |  0.0% | walrus: await (unknown)                        |
|     1 |  0.0% | loop: await (unknown)                          |
|     1 |  0.0% | unpack: call: builtin tuple()                  |
|     1 |  0.0% | walrus: call: builtin list()                   |
|     1 |  0.0% | walrus: call: module function (class)          |
|     1 |  0.0% | loop: SetComp (unknown elements)               |
