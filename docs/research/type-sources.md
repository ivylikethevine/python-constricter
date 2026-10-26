# New type sources for `--fix`, and how the top 100 PyPI packages ship their types

Research of 2026-10-23, from the 0.4.3-rc.1 mega run's `census.rows.jsonl` (103,514 calls with no
fix) and the installed environments. Reach figures are estimates.

## Two findings before any new source

1. **Installed stub packages shadowed in the corpus runs.** `installed.search_path()` lists
   constricter's own `sys.path` before `VIRTUAL_ENV`'s, and `locate()` stops at the first directory
   with the package, untyped there. `local/.venv` holds untyped `docutils`, `pandas` 3.0.6,
   `pygments`, `yaml`, `dateutil` and `six` (confirmed), while the corpus environments have
   `docutils-stubs` and `pygments-stubs` (sphinx), `pandas-stubs` (altair, narwhals, seaborn),
   `yaml-stubs` (litestar, optuna, starlette, strawberry, uvicorn), `dateutil-stubs` (pandas,
   strawberry). sphinx has 102 `docutils.nodes.*` and 6 `docutils.utils.*` calls of reason
   `imported` (`nodes.fully_normalize_name(...)`, declared `-> str` in the stubs); only capitalised
   names were typed, by the constructor guess. PEP 561 puts a `-stubs` package ahead of an inline or
   untyped one wherever it is on the path.
2. **A namespace package's `py.typed` in a subpackage is missed.** `_package(directory, top)` looks
   for `top/py.typed` alone: `google/auth/py.typed` (google-auth, #75) is never read, nor would
   `google.cloud.*` or `azure.*` be. A stub package is tried first with no fall-back for a module it
   lacks (`types-protobuf`'s `google-stubs` has no `auth`). Tiny in the corpora (5 calls into
   `google`), large elsewhere.

## Part 1: sources not yet used, ranked

Of the `imported` calls: 11,830 into the corpus's own package, 5,751 third-party, 741 standard
library, 279 other. The third-party ones (6,042 with those of no reason) by how the package stands in
that corpus's environment:

| Package in the environment | Calls | Main ones                                                                        |
| -------------------------- | ----: | -------------------------------------------------------------------------------- |
| typed                      | 5,977 | numpy and pytest, mostly                                                         |
| absent                     |   978 | pyarrow (pandas, 137), zope (twisted, 70), matplotlib (xarray, 57)               |
| untyped                    |   822 | pandas (dask 297, xarray 200), kombu 52, tlz 47, fsspec 40, scipy (networkx, 39) |
| stubs installed            |   265 | docutils (sphinx, 119), pyarrow (narwhals, 102)                                  |

Of the typed, numpy is mostly `np.array` of arguments of no known type (1,611) and pytest mostly
`pytest.importorskip` (723): argument types or `vague = 0`, not more stubs.

1. **The stub order and namespace `py.typed`** (the findings above): about 145 direct calls
   (docutils 119, dateutil 11, pandas 9, yaml 3, pygments 2) and the chains they start (sphinx 491
   `receiver`/`member` calls, seaborn 383: a few hundred, estimated); pandas's constructor guesses in
   seaborn, altair and narwhals become certain. No cost; certain.
2. **Declared types of installed packages with no `py.typed`, as guesses** (pyright's
   `useLibraryCodeForTypes`, held to what the source declares; mypy reads them as `Any`). Returns
   declared: pandas/core 73%, wheel 86%, pycparser 55%, setuptools 54%, grpc 51%, jsonschema 25%,
   kombu 8%, fsspec 10%. About 400 of the 822 untyped direct calls (pandas `date_range` →
   `DatetimeIndex`, `MultiIndex.from_product`), and dask's and xarray's chains on their frames, series,
   datasets and indexes (2,314 and 1,078 `receiver`/`member` calls, a third to a half pandas values). No cost; a
   guess of its own kind, held to the witness.
3. **typeshed's third-party stubs, not installed.** basedpyright 1.40.2 ships
   `dist/typeshed-fallback/stubs/` (201 sets, 27 MB, typeshed `289e5d3`): 18 of the top 100 typed only
   there (pyyaml, python-dateutil, six, cffi, pygments, protobuf, grpcio, jmespath, jsonschema, tqdm,
   pytz, regex, greenlet, ...). About 60 to 100 direct calls in the corpora (0.1%); its reach is users'
   code. Certain where the installed version matches `METADATA.toml`'s, a guess where not.
4. **pyrefly's `stubgen`** for untyped installed packages (experimental; `Incomplete` where unresolved):
   item 2's calls plus undeclared returns (tlz, botocore, kombu), perhaps 600 direct calls. A guess;
   measure first.
5. **Returns seen at run time** (RightTyper, MonkeyType, PyAnnotate, or `constricter.trace`'s return
   events): `member` 20,975, `untyped` 7,919, `local` 6,324, the largest pool; on the roadmap already.
   MonkeyType is slow (`sys.setprofile`, up to 270×) and needs libcst; RightTyper samples (about 27%)
   but crashed on pydantic. Best as returns the project's own tracer records.
6. **numpydoc Returns sections** (docstub, docs2stubs): of defs with no return annotation, networkx
   2,301 (868 with Returns, 485 one plain name), pandas 1,787 (360, 108), dask 3,912 (181, 56), xarray
   1,088 (60, 38); many names vague (`dictionary`, `graph`); `nx.path_graph`, the top callee (460
   calls), has none. Under 1,000 usable; a guess.
7. **Stub generators for compiled code** (`stubgen --inspect-mode`, pybind11-stubgen, nanobind,
   Cython `embedsignature`, mypy-protobuf, `__text_signature__`): returns rare, needs an import; next
   to no reach (lxml 8, grpc 3, greenlet 3).
8. **ML and LLM inference** (Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5, TypeGen; TypyBench,
   TypeEvalPy): not deterministic, a model or an API; only as an external `--infer-from`-style file
   through the hint filter and the witness.
9. **Framework plugins** (django-stubs', pydantic's mypy plugins): types only inside mypy runs; about 0
   corpus reach.

Already covered by `--infer-with`: pyrefly bundles stubs for boto3, botocore, pandas, matplotlib,
scikit-learn, scikit-image, sympy, vispy, conans.

## Part 2: the top 100

hugovk's list (`https://hugovk.dev/top-pypi-packages/top-pypi-packages.min.json`, `last_update`
2026-10-01). Totals: 64 inline (6 partial), 18 typeshed, 8 third-party stubs, 2 stubs in the
package, 8 none.

|   # | Package                   | Kind             | Extent  | Types from                |
| --: | ------------------------- | ---------------- | ------- | ------------------------- |
|   1 | boto3                     | third-party      | —       | boto3-stubs / types-boto3 |
|   2 | packaging                 | inline           | whole   | py.typed                  |
|   3 | typing-extensions         | typeshed         | whole   | typeshed stdlib           |
|   4 | idna                      | inline           | whole   | py.typed                  |
|   5 | urllib3                   | inline           | whole   | py.typed                  |
|   6 | certifi                   | inline           | whole   | py.typed                  |
|   7 | requests                  | inline           | whole   | py.typed (2.34)           |
|   8 | charset-normalizer        | inline           | whole   | py.typed                  |
|   9 | cryptography              | inline           | whole   | py.typed + pyi            |
|  10 | setuptools                | typeshed         | partial | types-setuptools          |
|  11 | cffi                      | typeshed         | —       | types-cffi                |
|  12 | pygments                  | typeshed         | —       | types-Pygments            |
|  13 | pyyaml                    | typeshed         | —       | types-PyYAML              |
|  14 | python-dateutil           | typeshed         | —       | types-python-dateutil     |
|  15 | six                       | typeshed         | —       | types-six                 |
|  16 | pluggy                    | inline           | whole   | py.typed                  |
|  17 | botocore                  | third-party      | —       | botocore-stubs            |
|  18 | pydantic                  | inline           | whole   | py.typed                  |
|  19 | pycparser                 | none             | partial | —                         |
|  20 | click                     | inline           | whole   | py.typed                  |
|  21 | pydantic-core             | inline           | whole   | py.typed + pyi            |
|  22 | anyio                     | inline           | whole   | py.typed                  |
|  23 | numpy                     | inline           | whole   | py.typed + pyi            |
|  24 | pytest                    | inline           | whole   | py.typed                  |
|  25 | iniconfig                 | inline           | whole   | py.typed                  |
|  26 | annotated-types           | inline           | whole   | py.typed                  |
|  27 | h11                       | inline           | whole   | py.typed                  |
|  28 | typing-inspection         | inline           | whole   | py.typed                  |
|  29 | attrs                     | inline           | whole   | py.typed + pyi            |
|  30 | s3transfer                | third-party      | —       | types-s3transfer          |
|  31 | aiobotocore               | third-party      | —       | types-aiobotocore         |
|  32 | protobuf                  | typeshed         | —       | types-protobuf            |
|  33 | httpx                     | inline           | whole   | py.typed                  |
|  34 | markupsafe                | inline           | whole   | py.typed + pyi            |
|  35 | httpcore                  | inline           | whole   | py.typed                  |
|  36 | python-dotenv             | inline           | whole   | py.typed                  |
|  37 | pyjwt                     | inline           | whole   | py.typed                  |
|  38 | platformdirs              | inline           | whole   | py.typed                  |
|  39 | fsspec                    | none             | partial | —                         |
|  40 | pandas                    | third-party      | partial | pandas-stubs              |
|  41 | jinja2                    | inline           | whole   | py.typed                  |
|  42 | jmespath                  | typeshed         | —       | types-jmespath            |
|  43 | pathspec                  | inline           | whole   | py.typed                  |
|  44 | filelock                  | inline           | whole   | py.typed                  |
|  45 | starlette                 | inline           | whole   | py.typed                  |
|  46 | uvicorn                   | inline           | whole   | py.typed                  |
|  47 | multidict                 | inline           | whole   | py.typed                  |
|  48 | jsonschema                | typeshed         | partial | types-jsonschema          |
|  49 | rpds-py                   | inline           | whole   | py.typed + pyi            |
|  50 | yarl                      | inline           | whole   | py.typed                  |
|  51 | aiohttp                   | inline           | whole   | py.typed                  |
|  52 | rich                      | inline           | whole   | py.typed                  |
|  53 | tomlkit                   | inline           | whole   | py.typed                  |
|  54 | markdown-it-py            | inline           | whole   | py.typed                  |
|  55 | propcache                 | inline           | whole   | py.typed                  |
|  56 | referencing               | inline           | whole   | py.typed                  |
|  57 | jsonschema-specifications | none             | —       | —                         |
|  58 | mdurl                     | inline           | whole   | py.typed                  |
|  59 | pillow                    | inline           | whole   | py.typed + pyi            |
|  60 | opentelemetry-api         | inline           | partial | py.typed                  |
|  61 | frozenlist                | inline           | whole   | py.typed + pyi            |
|  62 | tqdm                      | typeshed         | —       | types-tqdm                |
|  63 | pip                       | inline           | whole   | py.typed                  |
|  64 | googleapis-common-protos  | stubs-in-package | whole   | pyi, no py.typed          |
|  65 | pyasn1                    | typeshed         | —       | types-pyasn1              |
|  66 | aiosignal                 | inline           | whole   | py.typed                  |
|  67 | aiohappyeyeballs          | inline           | whole   | py.typed                  |
|  68 | websockets                | inline           | whole   | py.typed + pyi            |
|  69 | annotated-doc             | inline           | whole   | py.typed                  |
|  70 | wrapt                     | stubs-in-package | whole   | wrapt-stubs in the wheel  |
|  71 | pytz                      | typeshed         | —       | types-pytz                |
|  72 | sniffio                   | inline           | whole   | py.typed                  |
|  73 | tzdata                    | typeshed         | —       | types-tzdata              |
|  74 | fastapi                   | inline           | whole   | py.typed                  |
|  75 | google-auth               | inline           | partial | py.typed (namespace)      |
|  76 | zipp                      | none             | —       | —                         |
|  77 | greenlet                  | typeshed         | —       | types-greenlet            |
|  78 | importlib-metadata        | inline           | partial | py.typed                  |
|  79 | pydantic-settings         | inline           | whole   | py.typed                  |
|  80 | wheel                     | none             | partial | —                         |
|  81 | tenacity                  | inline           | whole   | py.typed                  |
|  82 | trove-classifiers         | inline           | whole   | py.typed                  |
|  83 | python-multipart          | inline           | whole   | py.typed                  |
|  84 | pyasn1-modules            | none             | —       | —                         |
|  85 | grpcio-status             | typeshed         | —       | types-grpcio-status       |
|  86 | pyarrow                   | third-party      | —       | pyarrow-stubs             |
|  87 | sqlalchemy                | inline           | whole   | py.typed                  |
|  88 | hatchling                 | inline           | whole   | py.typed                  |
|  89 | grpcio                    | typeshed         | partial | types-grpcio              |
|  90 | pyparsing                 | inline           | partial | py.typed                  |
|  91 | lxml                      | third-party      | —       | lxml-stubs / types-lxml   |
|  92 | jiter                     | inline           | whole   | py.typed + pyi            |
|  93 | regex                     | typeshed         | —       | types-regex               |
|  94 | watchfiles                | inline           | whole   | py.typed + pyi            |
|  95 | s3fs                      | none             | —       | —                         |
|  96 | ruff                      | none             | —       | CLI only                  |
|  97 | scipy                     | third-party      | partial | scipy-stubs               |
|  98 | soupsieve                 | inline           | whole   | py.typed                  |
|  99 | beautifulsoup4            | inline           | whole   | py.typed                  |
| 100 | openai                    | inline           | whole   | py.typed                  |

Partial inline: google-auth 8%, importlib-metadata 40%, pyparsing 68%, opentelemetry 75% of
functions with a declared return. Annotated with no `py.typed`: pycparser 55%, wheel 86%, fsspec 10%,
jsonschema 25%. Stubs that lag: pyarrow-stubs 20.0 for pyarrow 26; protobuf's for 7.35 (7.36.2 out);
python-dateutil's for 2.9 (3.0.0 out). requests ships inline types since 2.34. googleapis-common-protos'
63 `*_pb2.pyi` have no `py.typed`. Verified from local installs' RECORD, the corpus checkouts, the
newest wheel's file list, typeshed's `stubs/` (main `e4a2f22725`) and PyPI.

### What matters to the corpora

16 of the 47 corpora are on the list themselves. Direct calls into others with no fix:

| Package           | Kind        | Calls with no fix | Calls fixed |
| ----------------- | ----------- | ----------------: | ----------: |
| numpy             | inline      |             4,466 |         936 |
| pytest            | inline      |             1,078 |           — |
| pandas            | third-party |               508 |       1,045 |
| pyarrow           | third-party |               272 |           — |
| sqlalchemy        | inline      |               169 |           — |
| scipy             | third-party |                67 |           — |
| typing_extensions | typeshed    |                51 |           — |
| fsspec            | none        |                48 |           — |
| yaml              | typeshed    |                14 |           — |
| dateutil          | typeshed    |                14 |           — |

pandas's in dask (297) and xarray (200), with pandas-stubs missing from their environments; pyarrow's
in pandas (137, not installed), narwhals (102, stubs installed, unfixed on arguments) and dask (21);
sqlalchemy's in optuna (120, mostly `Column` declined); scipy's in networkx (39) and dask (10).

## Recommendation

1. Fix the stub order (the environment's stubs before constricter's own path; a `-stubs` package
   first anywhere, as PEP 561 says; `py.typed` in a namespace subpackage; a partial stub package
   falling back to the package), then re-measure on the super set and sphinx, seaborn, altair,
   narwhals. Small.
2. Measure what stubs would add: install pandas-stubs, scipy-stubs, pyarrow-stubs and types-PyYAML in
   dask's, xarray's, networkx's and pandas's environments (`corpora.toml`), then measure declared types
   of untyped packages as a guess against that baseline.
3. Then typeshed's third-party stubs from basedpyright's `typeshed-fallback/stubs`, version-checked
   against `METADATA.toml`.

Not verified: which interpreter the census check ran in (confirmed afterwards: `local/.venv` holds
the untyped copies and its path comes first); whether pyright reads `.pyi` files without `py.typed`;
whether `pyright --createstub` writes inferred returns; which stubs `ty` bundles; partial extents of
numpy, scipy, pip and C extensions (file counts only); returns counts from a regex sample.
