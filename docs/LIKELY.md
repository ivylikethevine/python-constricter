# Likely guesses (`--likely`)

A guess is a fix `--fix` can't vouch for: `--unsafe-fixes` applies every one. `--likely` applies
those measured to hold as often as a certain fix does, and no other:

```console
constricter --fix .                            # certain fixes
constricter --fix --likely .                   # and the likely guesses
constricter --fix --unsafe-fixes .             # and every guess
```

`--fix --likely --unsafe-fixes` is `--fix --unsafe-fixes`. `--diff` takes `--likely` as `--fix`
does. `--show-fixes` marks a likely guess `(a guess: --likely)`, `--format=json` gives each fix a
`likely` beside its `unsafe`, and `--fix`'s summary counts them
(`12 more with --unsafe-fixes (9 with --likely)`).

A guess is likely by its mechanisms alone: the whole set `--show-fixes` lists in brackets
(`[constructor, rebound]`) is one of the sets below, `constricter.offences.LIKELY`. Not by any one
of them: `rebound` with `constructor` is likely, with `copy` it isn't.

What rests on a likely guess and on no other is certain once that guess is declared:
`--fix --likely` checks a file again in the same run once it has written a guess there, and indexes
it again: every other file whose view of it changed is checked again too (`f = defer.fail()`, once
`fail`'s `d: Deferred = Deferred()` is declared), so a second run finds nothing more to fix.

## The measure

Every guess `--fix --unsafe-fixes` makes on 42 packages' own sources (pandas, SQLAlchemy, pydantic,
Django and 38 of the [mega corpora](RUNS.md#mega-corpora)'s), constricter 0.3.6+dev: 45,922 guesses
beside 61,029 certain fixes. Two things are held against each:

- **Its package's own type checker**, run after `--fix --unsafe-fixes` as the corpora runs do: each
  new error is traced to the fix on the line that brought it. 24 of the packages have one.
- **Its tests**, traced: as a statement that binds a fixed name ends, its value is held to the fix's
  annotation, evaluated where the statement is: an instance of the class it names, or of one of a
  union's (a subscripted class is held to the class alone, not its arguments). A fix a test could
  tell of held where every such value was one, and differed where one wasn't. The corpora runs do
  this for every suite whose tests they can trace, and RUNS.md gives each package's fixes by tier
  with those told, held and differing.

A set of mechanisms is likely where all three hold:

1. a traced test could tell of at least 20 of its guesses;
2. more than 95% of those held;
3. fewer than 0.1 of each 100 of its guesses a type checker read were blamed for an error.

95% and not the certain fixes' own share, which is higher: another corpus brings classes and test
doubles these packages don't have, and a set is to stay likely on it.

By tier, what the tests told of: a certain fix held 99.5% of the time (42,146 of 42,365), a likely
guess 99.7% (29,794 of 29,883), another guess 97.4% (3,663 of 3,761). A checker blamed one certain
fix of the 42,073 it read, 14 likely guesses of 29,550 (0.05 in each 100) and 8 other guesses of
4,534 (0.18).

## The likely sets

61 sets, 36,777 of the 45,922 guesses (80.1%): each passes the three bars. Checked: the guesses in a
package with a type checker; blamed: those of them an error was traced to. Told and held: as above.

| Mechanisms                            | Guesses | Packages | Checked | Blamed |   Told |   Held |  Share |
| ------------------------------------- | ------: | -------: | ------: | -----: | -----: | -----: | -----: |
| `constructor`                         |  28,597 |       42 |  23,397 |     14 | 23,520 | 23,487 |  99.9% |
| `method`                              |   1,278 |       33 |     983 |      0 |  1,101 |  1,080 |  98.1% |
| `copy`                                |     604 |       33 |     500 |      0 |    371 |    365 |  98.4% |
| `constructor+rebound`                 |     602 |       19 |     512 |      0 |    541 |    540 |  99.8% |
| `constructor+method`                  |     549 |       21 |     435 |      0 |    393 |    389 |  99.0% |
| `call`                                |     449 |       14 |     427 |      0 |    340 |    339 |  99.7% |
| `assigned`                            |     307 |       32 |     187 |      0 |    177 |    174 |  98.3% |
| `copy+loop`                           |     265 |       29 |     167 |      0 |    206 |    199 |  96.6% |
| `copy+filled`                         |     227 |       28 |     137 |      0 |    183 |    183 | 100.0% |
| `call+constructor`                    |     217 |        9 |     213 |      0 |    192 |    191 |  99.5% |
| `assigned+method`                     |     212 |       24 |     122 |      0 |    153 |    152 |  99.3% |
| `attribute`                           |     211 |       25 |     169 |      0 |    149 |    148 |  99.3% |
| `call+rebound`                        |     208 |       18 |     185 |      0 |    162 |    159 |  98.1% |
| `container+joined+literal`            |     189 |       19 |     143 |      0 |    144 |    144 | 100.0% |
| `constructor+container`               |     184 |       15 |     115 |      0 |    154 |    154 | 100.0% |
| `arithmetic+copy+literal`             |     179 |       14 |     139 |      0 |    123 |    123 | 100.0% |
| `constructor+joined`                  |     162 |        7 |     158 |      0 |    142 |    142 | 100.0% |
| `assigned+loop`                       |     145 |       23 |     120 |      0 |    109 |    109 | 100.0% |
| `call+copy`                           |     125 |       11 |     116 |      0 |     92 |     91 |  98.9% |
| `call+container+copy`                 |     108 |        2 |     108 |      0 |     99 |     99 | 100.0% |
| `call+constructor+container+literal`  |      93 |        1 |      93 |      0 |     86 |     86 | 100.0% |
| `filled+literal`                      |      85 |       27 |      43 |      0 |     70 |     70 | 100.0% |
| `constructor+container+literal`       |      83 |       10 |      37 |      0 |     66 |     66 | 100.0% |
| `method+unpack`                       |      80 |       15 |      44 |      0 |     66 |     64 |  97.0% |
| `constructor+returned`                |      80 |       10 |      27 |      0 |     64 |     64 | 100.0% |
| `returned+unpack`                     |      78 |        8 |       8 |      0 |     33 |     33 | 100.0% |
| `copy+stdlib`                         |      72 |       29 |      47 |      0 |     54 |     54 | 100.0% |
| `constructor+fixture`                 |      68 |        4 |      66 |      0 |     61 |     60 |  98.4% |
| `constructor+filled`                  |      67 |       12 |      14 |      0 |     54 |     54 | 100.0% |
| `container+copy+literal`              |      67 |        9 |      57 |      0 |     43 |     43 | 100.0% |
| `attribute+rebound`                   |      66 |       16 |      55 |      0 |     44 |     42 |  95.5% |
| `container+literal+rebound`           |      61 |       13 |      50 |      0 |     51 |     51 | 100.0% |
| `rebound+stdlib`                      |      60 |       22 |      29 |      0 |     46 |     46 | 100.0% |
| `constructor+optional`                |      55 |       16 |      38 |      0 |     46 |     46 | 100.0% |
| `call+container+literal`              |      53 |        3 |      52 |      0 |     47 |     47 | 100.0% |
| `comprehension+constructor+copy+loop` |      52 |        8 |      11 |      0 |     46 |     46 | 100.0% |
| `assigned+stdlib`                     |      47 |       15 |      26 |      0 |     31 |     31 | 100.0% |
| `conditional+literal`                 |      45 |       19 |      35 |      0 |     38 |     38 | 100.0% |
| `container+copy+loop`                 |      45 |        7 |      32 |      0 |     35 |     34 |  97.1% |
| `builtin+copy`                        |      43 |       14 |      14 |      0 |     24 |     24 | 100.0% |
| `loop+member`                         |      40 |        9 |       9 |      0 |     32 |     32 | 100.0% |
| `assigned+method+unpack`              |      39 |        7 |      31 |      0 |     32 |     32 | 100.0% |
| `arithmetic+copy`                     |      39 |       15 |      24 |      0 |     31 |     31 | 100.0% |
| `constructor+method+rebound`          |      39 |        4 |      36 |      0 |     25 |     25 | 100.0% |
| `copy+literal`                        |      37 |       17 |      22 |      0 |     33 |     33 | 100.0% |
| `literal+rebound+unpack`              |      37 |        6 |      24 |      0 |     34 |     34 | 100.0% |
| `attribute+loop`                      |      37 |       14 |      30 |      0 |     24 |     24 | 100.0% |
| `attribute+subscript`                 |      35 |       11 |      24 |      0 |     26 |     26 | 100.0% |
| `assigned+subscript`                  |      35 |       11 |      31 |      0 |     20 |     20 | 100.0% |
| `comprehension+constructor`           |      34 |        9 |      20 |      0 |     28 |     28 | 100.0% |
| `attribute+constructor`               |      31 |        5 |      29 |      0 |     23 |     23 | 100.0% |
| `constructor+copy`                    |      31 |        7 |      20 |      0 |     24 |     24 | 100.0% |
| `arithmetic+literal`                  |      30 |        3 |      17 |      0 |     21 |     21 | 100.0% |
| `constructor+unpack`                  |      29 |        4 |      16 |      0 |     29 |     29 | 100.0% |
| `loop+rebound`                        |      28 |       11 |      14 |      0 |     24 |     24 | 100.0% |
| `copy+unpack`                         |      25 |       11 |      12 |      0 |     20 |     20 | 100.0% |
| `container+joined+literal+loop`       |      25 |        4 |      11 |      0 |     21 |     21 | 100.0% |
| `method+rebound+unpack`               |      24 |       10 |      16 |      0 |     20 |     20 | 100.0% |
| `rebound+returned`                    |      23 |        5 |      15 |      0 |     20 |     20 | 100.0% |
| `arithmetic+literal+stdlib`           |      21 |        5 |      18 |      0 |     20 |     20 | 100.0% |
| `call+constructor+container+copy`     |      20 |        1 |      20 |      0 |     20 |     20 | 100.0% |

`constructor` (a call taken to construct its class) is 62% of all guesses. Its 14 blamed are mypy's
own, typed by `lxml`'s classes, which its checker's environment doesn't follow. Of the 33 that
differed, 21 are a class the trace couldn't name (one a function or a test defines again at each
call), 9 a pandas scalar whose constructor gave `NaT` (`Timestamp("NaT")`), and 3 a class of the
same name as the value's.

A set that passes still holds wrong guesses. `copy+loop`: `actual_key: tuple[str, int]`, a `list`
each of 233 times (dask's `_expr.py`). `assigned`, `attribute` and `attribute+rebound`: a declared
type its package's tests contradict (`prop: Optional[QueryableAttribute[_T_co]]`, a `Synonym`, in
SQLAlchemy; `f_type: FieldType`, a `type[int]`, in strawberry). `call+rebound` and `method+unpack`:
pandas's tests' scalars (`res: float`, a `Timestamp`; `s_start: int`, a `numpy.int64`).

## What isn't likely

Short of a bar, with what it missed:

| Mechanisms           | Guesses | Blamed, per 100 checked | Told | Held |  Share | Misses                 |
| -------------------- | ------: | ----------------------: | ---: | ---: | -----: | ---------------------- |
| `returned`           |     786 |                    0.00 |  612 |  573 |  93.6% | the share              |
| `literal+rebound`    |     482 |                    0.33 |  380 |  380 | 100.0% | a type checker's blame |
| `stdlib`             |     183 |                    0.95 |  124 |  124 | 100.0% | a type checker's blame |
| `copy+loop+rebound`  |     121 |                    2.38 |   93 |   90 |  96.8% | a type checker's blame |
| `method+rebound`     |     100 |                    1.16 |   83 |   81 |  97.6% | a type checker's blame |
| `copy+rebound`       |      97 |                    1.56 |   73 |   72 |  98.6% | a type checker's blame |
| `subscript`          |      82 |                    0.00 |   67 |   47 |  70.1% | the share              |
| `cast`               |      70 |                    0.00 |   38 |   36 |  94.7% | the share              |
| `assigned+attribute` |      61 |                    0.00 |   37 |   35 |  94.6% | the share              |
| `builtin+rebound`    |      42 |                    4.35 |   30 |   29 |  96.7% | a type checker's blame |

`returned`'s 39 that differed are 21 of Django's, 9 of pandas's and 9 more, among them
`signature: bytes`, a `str` each of 82 times (botocore's `auth.py`); `subscript`'s 20 are pandas's
tests' (`drop: str`, an `Index`). Each of the six blamed sets but `stdlib` has `rebound`: a name
typed by its first values and bound again to another.

And a traced test reaches next to nothing these bind (a class body's variable, a name bound once at
import: 13 bindings of them all), so nothing says how often they hold; no type checker blamed one:

| Mechanisms                 | Guesses | Checked |
| -------------------------- | ------: | ------: |
| `literal+member`           |   2,816 |     840 |
| `container+literal+member` |     669 |     187 |
| `final+literal`            |     429 |     188 |
| `alias`                    |     164 |     161 |
| `member+stdlib`            |      65 |      32 |

Every other set has fewer than 20 guesses a test told of. A checker's hint (`--infer-with`) and a
traced type (`--infer-from`) weren't measured: neither is likely.

## Measuring again

A super and a mega corpora run (`tests/corpus/runs/super.toml`, `mega.toml`) list, for each suite,
every fix of its `fix-unsafe` step with its tier, the type errors traced to it, and what its traced
tests saw of its binding (the run folder's `guesses.jsonl`); RUNS.md's sections give each package's
fixes by tier with those told and those that held. `scratch/guess_report.py --from FOLDER` prints
these tables, and with `--likely` the sets that pass, as `LIKELY` is written. A set joins or leaves
`LIKELY` by that listing alone.
