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

## The measure

Every guess `--fix --unsafe-fixes` makes on 42 packages' own sources (pandas, SQLAlchemy, pydantic,
Django and 38 of the [mega corpora](RUNS.md#mega-corpora)'s), constricter 0.3.6+dev: 45,936 guesses
beside 61,034 certain fixes. Two things are held against each:

- **Its package's own type checker**, run after `--fix --unsafe-fixes` as the corpora runs do: each
  new error is traced to the fix on the line that brought it. 41 of the packages have one.
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

The tables below were measured before the tests' values were held to the annotations themselves: on
pandas, SQLAlchemy, pydantic and Django, by the name of each value's class against the names in the
annotation, which a subclass (`DatetimeIndex` for an `Index`) or an alias (`ArrayLike` for an
`ndarray`) doesn't fit. Certain fixes, which are right, fit 88.4% of the time by it (13,914 of the
15,739 a test reached), and the sets below are those whose share by it was over that of the certain
fixes. The next corpora runs replace them with the sets that pass the bars above.

## The likely sets

22 sets, 34,009 of the 45,936 guesses (74.0%). Checked: the guesses in a package with a type
checker; blamed: those of them an error was traced to. Seen: the guesses a traced test reached.

| Mechanisms                           | Guesses | Packages | Checked | Blamed |   Seen |    Fit |  Share |
| ------------------------------------ | ------: | -------: | ------: | -----: | -----: | -----: | -----: |
| `constructor`                        |  28,603 |       42 |  23,403 |     16 | 16,839 | 16,555 |  98.3% |
| `method`                             |   1,279 |       34 |     983 |      0 |    824 |    731 |  88.7% |
| `constructor+rebound`                |     606 |       19 |     516 |      0 |    417 |    409 |  98.1% |
| `copy`                               |     604 |       33 |     500 |      0 |    331 |    315 |  95.2% |
| `constructor+method`                 |     549 |       21 |     435 |      0 |    290 |    256 |  88.3% |
| `call`                               |     449 |       14 |     427 |      0 |    317 |    309 |  97.5% |
| `copy+loop`                          |     265 |       29 |     167 |      0 |     59 |     53 |  89.8% |
| `call+constructor`                   |     217 |        9 |     213 |      0 |    182 |    181 |  99.5% |
| `container+joined+literal`           |     189 |       19 |     143 |      0 |     66 |     66 | 100.0% |
| `constructor+container`              |     184 |       15 |     115 |      0 |     93 |     89 |  95.7% |
| `arithmetic+copy+literal`            |     179 |       14 |     139 |      0 |     32 |     32 | 100.0% |
| `constructor+joined`                 |     162 |        7 |     158 |      0 |    135 |    135 | 100.0% |
| `call+copy`                          |     125 |       11 |     116 |      0 |     75 |     73 |  97.3% |
| `call+container+copy`                |     108 |        2 |     108 |      0 |     96 |     96 | 100.0% |
| `call+constructor+container+literal` |      93 |        1 |      93 |      0 |     86 |     86 | 100.0% |
| `constructor+container+literal`      |      83 |       10 |      37 |      0 |     28 |     28 | 100.0% |
| `constructor+fixture`                |      68 |        4 |      66 |      0 |     58 |     57 |  98.3% |
| `container+copy+literal`             |      67 |        9 |      57 |      0 |     26 |     26 | 100.0% |
| `container+literal+rebound`          |      61 |       13 |      50 |      0 |     23 |     23 | 100.0% |
| `call+container+literal`             |      53 |        3 |      52 |      0 |     46 |     46 | 100.0% |
| `container+copy+loop`                |      45 |        7 |      32 |      0 |     29 |     28 |  96.6% |
| `call+constructor+container+copy`    |      20 |        1 |      20 |      0 |     20 |     20 | 100.0% |

`constructor` (a call taken to construct its class) is 62% of all guesses. Its 16 blamed are 14 of
mypy's own, typed by `lxml`'s classes, which its checker's environment doesn't follow, and two bare
generic classes on mcp (`TypeAdapter` for a `TypeAdapter[...]`), no fix since). Of its 284 that
don't fit, 28 were read: 27 a subclass its class's own constructor returns (`Index(...)` giving a
`DatetimeIndex`), a class local to a test, or an alias; one wrong (`multiprocessing.Value(...)`, a
function).

## What isn't likely

Short of a bar, with what it missed:

| Mechanisms             | Guesses | Blamed, per 100 checked | Seen | Fit |  Share | Misses                 |
| ---------------------- | ------: | ----------------------: | ---: | --: | -----: | ---------------------- |
| `returned`             |     786 |                    0.00 |  238 | 190 |  79.8% | the share              |
| `literal+rebound`      |     482 |                    0.33 |   64 |  64 | 100.0% | a type checker's blame |
| `assigned`             |     307 |                    0.00 |   43 |  22 |  51.2% | the share              |
| `attribute`            |     211 |                    0.00 |   93 |  62 |  66.7% | the share              |
| `call+rebound`         |     208 |                    0.00 |  124 | 109 |  87.9% | the share              |
| `stdlib`               |     183 |                    0.95 |   23 |  22 |  95.7% | a type checker's blame |
| `copy+loop+rebound`    |     121 |                    2.38 |   20 |  16 |  80.0% | both                   |
| `method+rebound`       |     100 |                    1.16 |   46 |  40 |  87.0% | both                   |
| `copy+rebound`         |      97 |                    1.56 |   28 |  22 |  78.6% | both                   |
| `subscript`            |      82 |                    0.00 |   22 |   2 |   9.1% | the share              |
| `attribute+rebound`    |      66 |                    0.00 |   26 |   7 |  26.9% | the share              |
| `constructor+returned` |      80 |                    0.00 |   27 |  22 |  81.5% | the share              |

And a traced test reaches next to nothing these bind (a class body's variable, a name bound once at
import: one binding of them all), so nothing says how often they hold; no type checker blamed one:

| Mechanisms                 | Guesses | Checked |
| -------------------------- | ------: | ------: |
| `literal+member`           |   2,816 |     840 |
| `container+literal+member` |     669 |     187 |
| `final+literal`            |     429 |     188 |
| `copy+filled`              |     227 |     137 |
| `alias`                    |     164 |     161 |

Every other set has fewer than 20 guesses a test reached. A checker's hint (`--infer-with`) and a
traced type (`--infer-from`) weren't measured: neither is likely.

## Measuring again

A super and a mega corpora run keep, for each suite, every fix of its one fixed run with its tier,
the type errors traced to each, and what its traced tests saw of each binding; RUNS.md's sections
give each package's fixes by tier with those seen and those that fit. `scratch/guess_census.py`
lists every fix from what the runs kept, and `scratch/guess_report.py` prints these tables, and with
`--likely` the sets that pass, as `LIKELY` is written. A set joins or leaves `LIKELY` by that
listing alone.
