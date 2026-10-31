# Basic corpora

The run `0.3.8-rc.1` (`python -m tests.corpus`) on original: constricter 0.3.8 (`4a20971934b8`),
Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the
CPUs it's expected to keep busy and the memory it's expected to hold are free. The run took 58
minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter    | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | -------------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14.7  | 0.3.8-rc.1+dev | 1,867 |          88,565 |        12,334 |         12,772 |         57 |         14 |         8 |        0 | 113,750 |
| django           | 5.2.18  | 0.3.8-rc.1+dev |   883 |           9,926 |         2,166 |          5,084 |          0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy       | 2.1.4   | 0.3.8-rc.1+dev |   258 |           8,825 |         1,636 |          2,501 |        572 |        128 |         2 |        1 |  13,665 |
| pydantic         | 2.14.0  | 0.3.8-rc.1+dev |   105 |           2,072 |           440 |            605 |        184 |         15 |         0 |        0 |   3,316 |
| pandas           | 3.0.6   | 0.3.8-rc.1+dev | 1,420 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | 0.3.8-rc.1+dev |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.3.8-rc.1+dev |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | 0.3.8-rc.1+dev | 5,718 | 201,967 (79.9%) | 21,853 (8.6%) | 27,697 (11.0%) | 947 (0.4%) | 159 (0.1%) | 12 (0.0%) | 2 (0.0%) | 252,637 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | -------------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | 0.3.8-rc.1+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,322 (32.8%) |   6,421 (5.6%) | 12,352 (10.9%) |      0 |    0 |            0 |
| django           | 0.3.8-rc.1+dev |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,614 (15.2%) |     631 (3.7%) |  2,702 (15.7%) |      0 |    0 |            0 |
| sqlalchemy       | 0.3.8-rc.1+dev |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |  1,880 (13.8%) |     341 (2.5%) |     838 (6.1%) |      0 |    0 |            0 |
| pydantic         | 0.3.8-rc.1+dev |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,179 (35.6%) |     146 (4.4%) |    408 (12.3%) |      0 |    0 |            0 |
| pandas           | 0.3.8-rc.1+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,910 (21.7%) | 23,812 (30.6%) | 24,643 (31.6%) |      0 |    0 |            0 |
| twisted          | 0.3.8-rc.1+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,433 (13.6%) |  3,656 (20.5%) |  4,676 (26.2%) |      0 |    0 |            0 |
| pip              | 0.3.8-rc.1+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,250 (25.2%) |     424 (4.8%) |  1,133 (12.7%) |      0 |    0 |            0 |
| **Total**        | 0.3.8-rc.1+dev | 0 / 251,529 | 229,664 / 22,973 | 251,529 / 1,108 | 252,637 / 0 | 64,588 (25.6%) | 35,431 (14.0%) | 46,752 (18.5%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.3.8-rc.1+dev |              1.2% |         33.6% |            39.2% |                  44.4% | +32.5 pts, 32.8% of untyped | +43.2 pts, 43.7% of untyped |
| django           | 0.3.8-rc.1+dev |              0.0% |         15.2% |            18.9% |                  31.0% | +15.2 pts, 15.2% of untyped | +30.9 pts, 31.0% of untyped |
| sqlalchemy       | 0.3.8-rc.1+dev |             15.3% |         27.5% |            29.8% |                  33.0% | +12.3 pts, 14.5% of untyped | +17.8 pts, 21.0% of untyped |
| pydantic         | 0.3.8-rc.1+dev |             22.4% |         51.8% |            55.4% |                  61.9% | +29.3 pts, 37.8% of untyped | +39.5 pts, 50.9% of untyped |
| pandas           | 0.3.8-rc.1+dev |              1.6% |         23.0% |            53.1% |                  54.2% | +21.4 pts, 21.7% of untyped | +52.6 pts, 53.4% of untyped |
| twisted          | 0.3.8-rc.1+dev |              0.0% |         13.6% |            34.1% |                  39.8% | +13.6 pts, 13.6% of untyped | +39.8 pts, 39.8% of untyped |
| pip              | 0.3.8-rc.1+dev |              1.5% |         26.3% |            31.0% |                  38.8% | +24.8 pts, 25.2% of untyped | +37.3 pts, 37.9% of untyped |
| **Total**        | 0.3.8-rc.1+dev |              2.3% |         27.4% |            41.2% |                  45.6% | +25.1 pts, 25.7% of untyped | +43.2 pts, 44.3% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus           | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ---------------- | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library | certain            | 37,322 |  37,322 |        |        |      0 |    0 | 38,651 |  115,001 |    58.8 |
| standard library | likely             | 43,743 |  37,532 |  6,211 |        |      0 |    0 | 45,072 |  115,001 |    96.7 |
| standard library | unsafe             | 49,674 |  37,330 |  6,203 |  6,141 |      0 |    0 | 51,003 |  115,001 |    66.6 |
| standard library | infer-basedpyright | 58,062 |  37,341 |  6,713 | 14,008 |      0 |    9 | 59,391 |  115,001 |   716.4 |
| standard library | infer-ty           | 55,809 |  37,345 |  6,678 | 11,786 |      0 |   38 | 57,138 |  115,001 |    72.9 |
| standard library | infer-pyrefly      | 58,427 |  37,341 |  6,845 | 14,241 |      0 |   35 | 59,756 |  115,001 |   120.1 |
| django           | certain            |  2,614 |   2,614 |        |        |      0 |    0 |  2,619 |   17,181 |    12.0 |
| django           | likely             |  3,245 |   2,618 |    627 |        |      0 |    0 |  3,250 |   17,181 |    13.5 |
| django           | unsafe             |  5,316 |   2,614 |    626 |  2,076 |      0 |    0 |  5,321 |   17,181 |     9.9 |
| django           | infer-basedpyright |  5,777 |   2,613 |    644 |  2,520 |      0 |    4 |  5,782 |   17,181 |    47.9 |
| django           | infer-ty           |  5,550 |   2,615 |    635 |  2,300 |      0 |    0 |  5,555 |   17,181 |    20.8 |
| django           | infer-pyrefly      |  6,037 |   2,605 |    651 |  2,781 |      0 |   36 |  6,042 |   17,181 |    22.5 |
| django           | infer-trace        |  5,861 |   2,618 |    659 |  2,584 |      0 |    0 |  5,866 |   17,181 |     9.9 |
| sqlalchemy       | certain            |  1,880 |   1,880 |        |        |      0 |    0 |  4,215 |   15,304 |     9.3 |
| sqlalchemy       | likely             |  2,221 |   1,887 |    334 |        |      0 |    0 |  4,556 |   15,304 |    15.3 |
| sqlalchemy       | unsafe             |  2,718 |   1,880 |    334 |    504 |      0 |    0 |  5,053 |   15,304 |     9.6 |
| sqlalchemy       | infer-basedpyright |  3,540 |   1,875 |    371 |  1,294 |      0 |    0 |  5,875 |   15,304 |    59.7 |
| sqlalchemy       | infer-ty           |  3,476 |   1,875 |    360 |  1,241 |      0 |    0 |  5,811 |   15,304 |    23.3 |
| sqlalchemy       | infer-pyrefly      |  3,212 |   1,874 |    351 |    987 |      0 |    0 |  5,547 |   15,304 |    17.4 |
| sqlalchemy       | infer-trace        |  2,886 |   1,880 |    334 |    672 |      0 |    0 |  5,221 |   15,304 |    11.4 |
| pydantic         | certain            |  1,179 |   1,179 |        |        |      0 |    0 |  2,081 |    4,019 |     2.1 |
| pydantic         | likely             |  1,325 |   1,187 |    138 |        |      0 |    0 |  2,227 |    4,019 |     3.2 |
| pydantic         | unsafe             |  1,587 |   1,179 |    137 |    271 |      0 |    0 |  2,489 |    4,019 |     7.8 |
| pydantic         | infer-basedpyright |  1,816 |   1,180 |    141 |    495 |      0 |    0 |  2,718 |    4,019 |    36.7 |
| pydantic         | infer-ty           |  1,728 |   1,179 |    136 |    413 |      0 |    0 |  2,630 |    4,019 |     4.0 |
| pydantic         | infer-pyrefly      |  1,789 |   1,179 |    137 |    473 |      0 |    0 |  2,691 |    4,019 |     9.0 |
| pydantic         | infer-trace        |  1,588 |   1,179 |    137 |    272 |      0 |    0 |  2,490 |    4,019 |     4.2 |
| pandas           | certain            | 16,910 |  16,910 |        |        |      0 |    0 | 18,179 |   79,062 |    50.9 |
| pandas           | likely             | 40,722 |  17,093 | 23,629 |        |      0 |    0 | 41,991 |   79,062 |    94.1 |
| pandas           | unsafe             | 41,553 |  16,906 | 23,410 |  1,237 |      0 |    0 | 42,822 |   79,062 |    52.3 |
| pandas           | infer-basedpyright | 47,291 |  16,898 | 23,431 |  6,962 |      0 |   25 | 48,560 |   79,062 |   429.8 |
| pandas           | infer-ty           | 47,043 |  16,906 | 23,460 |  6,677 |      0 |    5 | 48,312 |   79,062 |   175.0 |
| pandas           | infer-pyrefly      | 48,300 |  16,909 | 23,473 |  7,918 |      0 |    9 | 49,569 |   79,062 |   195.4 |
| pandas           | infer-trace        | 42,948 |  16,906 | 23,371 |  2,671 |      0 |    9 | 44,217 |   79,062 |    40.8 |
| twisted          | certain            |  2,433 |   2,433 |        |        |      0 |    0 |  2,433 |   17,874 |     5.8 |
| twisted          | likely             |  6,089 |   2,556 |  3,533 |        |      0 |    0 |  6,089 |   17,874 |    10.5 |
| twisted          | unsafe             |  7,109 |   2,432 |  3,533 |  1,144 |      0 |    0 |  7,109 |   17,874 |     7.3 |
| twisted          | infer-basedpyright |  8,551 |   2,437 |  3,563 |  2,551 |      0 |    2 |  8,551 |   17,874 |    62.3 |
| twisted          | infer-ty           |  7,541 |   2,432 |  3,576 |  1,533 |      0 |    0 |  7,541 |   17,874 |    15.8 |
| twisted          | infer-pyrefly      |  7,564 |   2,432 |  3,566 |  1,566 |      0 |    0 |  7,564 |   17,874 |    17.3 |
| pip              | certain            |  2,250 |   2,250 |        |        |      0 |    0 |  2,387 |    9,064 |     6.2 |
| pip              | likely             |  2,674 |   2,263 |    411 |        |      0 |    0 |  2,811 |    9,064 |     9.8 |
| pip              | unsafe             |  3,383 |   2,250 |    411 |    722 |      0 |    0 |  3,520 |    9,064 |     5.2 |
| pip              | infer-basedpyright |  4,178 |   2,255 |    465 |  1,458 |      0 |    7 |  4,315 |    9,064 |    28.1 |
| pip              | infer-ty           |  3,714 |   2,252 |    435 |  1,027 |      0 |    2 |  3,851 |    9,064 |    13.3 |
| pip              | infer-pyrefly      |  3,933 |   2,252 |    449 |  1,232 |      0 |    0 |  4,070 |    9,064 |    14.2 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 16,729 |  16,729 |        |        |
| certain            | stdlib                 | 13,248 |  13,248 |        |        |
| certain            | call                   |  5,105 |   5,105 |        |        |
| certain            | container+literal      |  3,917 |   3,917 |        |        |
| certain            | builtin                |  2,518 |   2,518 |        |        |
| certain            | loop                   |  2,442 |   2,442 |        |        |
| certain            | container+literal+loop |  1,581 |   1,581 |        |        |
| certain            | copy+loop              |  1,544 |   1,544 |        |        |
| certain            | method                 |  1,221 |   1,221 |        |        |
| certain            | open                   |  1,101 |   1,101 |        |        |
| certain            | literal+method         |    945 |     945 |        |        |
| certain            | returned               |    856 |     856 |        |        |
| likely             | constructor            | 27,110 |     235 | 26,875 |        |
| likely             | literal                | 16,730 |  16,730 |        |        |
| likely             | stdlib                 | 13,304 |  13,304 |        |        |
| likely             | call                   |  5,560 |   5,117 |    443 |        |
| likely             | container+literal      |  3,917 |   3,917 |        |        |
| likely             | builtin                |  2,518 |   2,518 |        |        |
| likely             | loop                   |  2,442 |   2,442 |        |        |
| likely             | method                 |  2,222 |   1,243 |    979 |        |
| likely             | copy+loop              |  1,805 |   1,552 |    253 |        |
| likely             | container+literal+loop |  1,581 |   1,581 |        |        |
| likely             | open                   |  1,101 |   1,101 |        |        |
| likely             | returned               |  1,073 |   1,073 |        |        |
| unsafe             | constructor            | 27,109 |     235 | 26,874 |        |
| unsafe             | literal                | 16,732 |  16,729 |        |      3 |
| unsafe             | stdlib                 | 13,554 |  13,250 |        |    304 |
| unsafe             | call                   |  5,523 |   5,105 |    418 |        |
| unsafe             | container+literal      |  3,917 |   3,917 |        |        |
| unsafe             | literal+member         |  3,689 |         |        |  3,689 |
| unsafe             | returned               |  3,269 |     858 |        |  2,411 |
| unsafe             | builtin                |  2,518 |   2,518 |        |        |
| unsafe             | loop                   |  2,442 |   2,442 |        |        |
| unsafe             | method                 |  2,161 |   1,221 |    940 |        |
| unsafe             | copy+loop              |  1,790 |   1,544 |    246 |        |
| unsafe             | container+literal+loop |  1,581 |   1,581 |        |        |
| infer-basedpyright | constructor            | 27,063 |     234 | 26,829 |        |
| infer-basedpyright | literal                | 16,733 |  16,730 |        |      3 |
| infer-basedpyright | checker                | 15,206 |         |        | 15,206 |
| infer-basedpyright | stdlib                 | 13,608 |  13,147 |        |    461 |
| infer-basedpyright | call                   |  5,619 |   5,103 |    516 |        |
| infer-basedpyright | container+literal      |  3,918 |   3,918 |        |        |
| infer-basedpyright | literal+member         |  3,688 |         |        |  3,688 |
| infer-basedpyright | returned               |  3,555 |     844 |        |  2,711 |
| infer-basedpyright | builtin                |  2,518 |   2,518 |        |        |
| infer-basedpyright | loop                   |  2,442 |   2,442 |        |        |
| infer-basedpyright | method                 |  2,291 |   1,220 |  1,071 |        |
| infer-basedpyright | copy+loop              |  2,139 |   1,547 |    592 |        |
| infer-ty           | constructor            | 27,063 |     235 | 26,828 |        |
| infer-ty           | literal                | 16,732 |  16,729 |        |      3 |
| infer-ty           | stdlib                 | 13,622 |  13,165 |        |    457 |
| infer-ty           | checker                | 11,315 |         |        | 11,315 |
| infer-ty           | call                   |  5,597 |   5,103 |    494 |        |
| infer-ty           | container+literal      |  3,920 |   3,920 |        |        |
| infer-ty           | literal+member         |  3,689 |         |        |  3,689 |
| infer-ty           | returned               |  3,496 |     858 |        |  2,638 |
| infer-ty           | builtin                |  2,518 |   2,518 |        |        |
| infer-ty           | loop                   |  2,442 |   2,442 |        |        |
| infer-ty           | method                 |  2,263 |   1,220 |  1,043 |        |
| infer-ty           | copy+loop              |  2,038 |   1,546 |    492 |        |
| infer-pyrefly      | constructor            | 27,048 |     234 | 26,814 |        |
| infer-pyrefly      | literal                | 16,732 |  16,729 |        |      3 |
| infer-pyrefly      | checker                | 15,292 |         |        | 15,292 |
| infer-pyrefly      | stdlib                 | 13,680 |  13,210 |        |    470 |
| infer-pyrefly      | call                   |  5,595 |   5,103 |    492 |        |
| infer-pyrefly      | container+literal      |  3,918 |   3,918 |        |        |
| infer-pyrefly      | literal+member         |  3,688 |         |        |  3,688 |
| infer-pyrefly      | returned               |  3,484 |     858 |        |  2,626 |
| infer-pyrefly      | builtin                |  2,518 |   2,518 |        |        |
| infer-pyrefly      | loop                   |  2,442 |   2,442 |        |        |
| infer-pyrefly      | method                 |  2,280 |   1,220 |  1,060 |        |
| infer-pyrefly      | copy+loop              |  2,097 |   1,546 |    551 |        |
| infer-trace        | constructor            | 19,787 |       3 | 19,784 |        |
| infer-trace        | literal                |  6,887 |   6,887 |        |        |
| infer-trace        | call                   |  5,159 |   4,740 |    419 |        |
| infer-trace        | traced                 |  2,004 |         |        |  2,004 |
| infer-trace        | literal+member         |  1,949 |         |        |  1,949 |
| infer-trace        | method                 |  1,763 |     840 |    923 |        |
| infer-trace        | container+literal      |  1,560 |   1,560 |        |        |
| infer-trace        | stdlib                 |  1,170 |   1,136 |        |     34 |
| infer-trace        | builtin                |    835 |     835 |        |        |
| infer-trace        | loop                   |    587 |     587 |        |        |
| infer-trace        | returned               |    583 |     224 |        |    359 |
| infer-trace        | copy+loop              |    470 |     375 |     95 |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus           | untyped | guessed | unfixed | unparsed |
| ---------------- | ------: | ------: | ------: | -------: |
| standard library | 113,671 |  12,345 |  64,004 |        0 |
| django           |  17,176 |   2,702 |  11,860 |        0 |
| sqlalchemy       |  12,962 |     838 |  10,244 |        0 |
| pydantic         |   3,117 |     408 |   1,530 |        0 |
| pandas           |  77,793 |  24,642 |  36,241 |        0 |
| twisted          |  17,874 |   4,676 |  10,765 |        0 |
| pip              |   8,924 |   1,133 |   5,541 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus           | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ---------------- | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library |    4 |       45.81 |     19.73 |    1 |                       630.2 |     656.1 | hyperfine |
| django           |    4 |         8.5 |      3.61 |    1 |                       117.5 |     125.5 | hyperfine |
| sqlalchemy       |    4 |        7.44 |      3.45 |    1 |                        96.7 |     101.7 | hyperfine |
| pydantic         |    4 |        1.52 |      0.71 |    1 |                        22.0 |      24.1 | hyperfine |
| pandas           |    4 |       54.66 |     17.67 |    1 |                       773.6 |     790.1 | hyperfine |
| twisted          |    4 |        6.23 |       2.6 |    1 |                        90.6 |      96.9 | hyperfine |
| pip              |    4 |        4.29 |      1.72 |    1 |                        65.1 |      69.2 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus     | tier    |   told |   held | differed | resting on the trace |                                                                             tests | seconds | untraced |
| ---------- | ------- | -----: | -----: | -------: | -------------------: | --------------------------------------------------------------------------------: | ------: | -------: |
| django     |         |        |        |          |                  466 | Ran 18191 tests: FAILED (failures=5, errors=4, skipped=1313, expected failures=5) |   604.8 |     63.9 |
| django     | certain |    926 |    925 |        1 |                      |                                                                                   |         |          |
| django     | likely  |    301 |    300 |        1 |                      |                                                                                   |         |          |
| django     | guess   |    306 |    290 |       16 |                      |                                                                                   |         |          |
| sqlalchemy |         |        |        |          |                  166 |                                    2 failed, 29523 passed, 971 skipped, 1 warning |    98.5 |    126.0 |
| sqlalchemy | certain |  1,098 |  1,081 |       17 |                      |                                                                                   |         |          |
| sqlalchemy | likely  |    176 |    173 |        3 |                      |                                                                                   |         |          |
| sqlalchemy | guess   |    118 |    116 |        2 |                      |                                                                                   |         |          |
| pydantic   |         |        |        |          |                    1 |                                              6965 passed, 350 skipped, 29 xfailed |    59.8 |     52.8 |
| pydantic   | certain |    518 |    513 |        5 |                      |                                                                                   |         |          |
| pydantic   | likely  |     47 |     47 |        0 |                      |                                                                                   |         |          |
| pydantic   | guess   |     32 |     32 |        0 |                      |                                                                                   |         |          |
| pandas     |         |        |        |          |                1,418 |                             165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   122.3 |    118.9 |
| pandas     | certain | 12,851 | 12,774 |       77 |                      |                                                                                   |         |          |
| pandas     | likely  | 20,116 | 20,058 |       58 |                      |                                                                                   |         |          |
| pandas     | guess   |    838 |    790 |       48 |                      |                                                                                   |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus     | run                | same as released | summary                                                    | new failures | gone | named |
| ---------- | ------------------ | ---------------- | ---------------------------------------------------------- | -----------: | ---: | ----: |
| django     | released           |                  | 5 expected failures, 1 failures, 18,191 ran, 1,313 skipped |              |      |       |
| django     | fix-certain        | False            | 5 expected failures, 2 failures, 17,585 ran, 1,129 skipped |            1 |    1 |     0 |
| django     | fix-likely         | True             | 5 expected failures, 2 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-basedpyright | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-trace        | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-ty           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| sqlalchemy | released           |                  | 29,523 passed, 973 skipped                                 |              |      |       |
| sqlalchemy | fix-certain        | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | fix-likely         | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | fix-unsafe         | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-basedpyright | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-pyrefly      | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-trace        | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-ty           | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| pydantic   | released           |                  | 6,965 passed, 350 skipped, 29 xfailed                      |              |      |       |
| pydantic   | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-unsafe         | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-basedpyright | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-pyrefly      | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-trace        | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-ty           | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pandas     | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |              |      |       |
| pandas     | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pandas     | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pandas     | fix-unsafe         | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-basedpyright | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-pyrefly      | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-trace        | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-ty           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus     | run                | errors | new | gone |                                                      change |
| ---------- | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy | released           |      0 |     |      |                                                             |
| sqlalchemy | fix-certain        |      0 |   0 |    0 |    175 files changed, 1954 insertions(+), 1534 deletions(-) |
| sqlalchemy | fix-likely         |      0 |   0 |    0 |    185 files changed, 2299 insertions(+), 1855 deletions(-) |
| sqlalchemy | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2805 insertions(+), 2319 deletions(-) |
| sqlalchemy | infer-basedpyright |      6 |   6 |    0 |    204 files changed, 3650 insertions(+), 3112 deletions(-) |
| sqlalchemy | infer-pyrefly      |     15 |  15 |    0 |    203 files changed, 3317 insertions(+), 2669 deletions(-) |
| sqlalchemy | infer-trace        |      6 |   6 |    0 |    200 files changed, 3009 insertions(+), 2473 deletions(-) |
| sqlalchemy | infer-ty           |      4 |   4 |    0 |    205 files changed, 3594 insertions(+), 2949 deletions(-) |
| pydantic   | released           |      0 |     |      |                                                             |
| pydantic   | fix-certain        |      0 |   0 |    0 |      76 files changed, 1237 insertions(+), 889 deletions(-) |
| pydantic   | fix-likely         |      0 |   0 |    0 |     78 files changed, 1390 insertions(+), 1020 deletions(-) |
| pydantic   | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1664 insertions(+), 1263 deletions(-) |
| pydantic   | infer-basedpyright |      3 |   3 |    0 |     79 files changed, 1905 insertions(+), 1490 deletions(-) |
| pydantic   | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1931 insertions(+), 1404 deletions(-) |
| pydantic   | infer-trace        |      0 |   0 |    0 |     79 files changed, 1665 insertions(+), 1264 deletions(-) |
| pydantic   | infer-ty           |      3 |   3 |    0 |     79 files changed, 1808 insertions(+), 1397 deletions(-) |
| pandas     | released           |    259 |     |      |                                                             |
| pandas     | fix-certain        |    259 |   0 |    0 | 1067 files changed, 18205 insertions(+), 15186 deletions(-) |
| pandas     | fix-likely         |    259 |   0 |    0 | 1199 files changed, 42285 insertions(+), 38650 deletions(-) |
| pandas     | fix-unsafe         |    260 |   1 |    0 | 1202 files changed, 43158 insertions(+), 39403 deletions(-) |
| pandas     | infer-basedpyright |    312 |  53 |    0 | 1213 files changed, 49415 insertions(+), 45029 deletions(-) |
| pandas     | infer-pyrefly      |    377 | 118 |    0 | 1209 files changed, 50335 insertions(+), 45703 deletions(-) |
| pandas     | infer-trace        |    261 |   2 |    0 | 1205 files changed, 44603 insertions(+), 40766 deletions(-) |
| pandas     | infer-ty           |    308 |  49 |    0 | 1214 files changed, 48953 insertions(+), 44609 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus           | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ---------------- | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library | check                    |    48.9 |        98.1 |  2.0 |    3.84 |          3 |     4.76 | False |
| standard library | fix-certain              |   121.5 |       267.5 |  2.2 |    5.19 |          3 |     6.44 | False |
| standard library | fix-likely               |   146.8 |       335.6 |  2.3 |    7.84 |          3 |      9.8 | False |
| standard library | fix-unsafe               |   121.9 |       279.2 |  2.3 |    5.89 |          3 |     7.35 | False |
| standard library | infer-basedpyright       |   869.8 |      1406.3 |  1.6 |   12.53 |          2 |     16.1 | False |
| standard library | infer-ty                 |   119.5 |       404.7 |  3.4 |   15.27 |          4 |    19.91 | False |
| standard library | infer-pyrefly            |   177.6 |       524.6 |  3.0 |   19.05 |          4 |     23.7 | False |
| standard library | census                   |    38.7 |        34.7 |  0.9 |    0.51 |          3 |     4.76 | False |
| standard library | coverage                 |     9.2 |        30.7 |  3.3 |    1.63 |          4 |     2.04 | False |
| standard library | timing                   |   128.1 |       195.0 |  1.5 |    3.78 |         16 |     4.71 | False |
| django           | check                    |     2.4 |         0.4 |  0.2 |    0.06 |          2 |     1.06 | False |
| django           | fix-certain              |    23.4 |        52.9 |  2.3 |    1.12 |          2 |     1.39 | False |
| django           | fix-likely               |    21.2 |        54.4 |  2.6 |    1.52 |          2 |     1.88 | False |
| django           | fix-unsafe               |    17.6 |        46.0 |  2.6 |    1.27 |          2 |     1.59 | False |
| django           | infer-basedpyright       |    66.3 |       296.9 |  4.5 |     7.8 |          5 |    10.01 | False |
| django           | infer-ty                 |    31.7 |        92.6 |  2.9 |    3.47 |          2 |     4.47 | False |
| django           | infer-pyrefly            |    33.1 |       101.4 |  3.1 |    4.17 |          3 |     4.99 | False |
| django           | census                   |    12.2 |        23.8 |  2.0 |    0.87 |          2 |     1.06 | False |
| django           | coverage                 |     2.0 |         5.1 |  2.5 |    0.34 |          3 |     0.44 | False |
| django           | timing                   |    24.4 |        37.2 |  1.5 |    0.85 |         16 |     1.06 | False |
| django           | traced                   |   620.8 |       499.6 |  0.8 |    1.35 |          1 |     1.61 | False |
| django           | tests-released           |    64.5 |       473.8 |  7.3 |    6.02 |          8 |      8.5 | False |
| django           | tests-fix-certain        |   112.3 |       500.2 |  4.5 |    5.39 |          1 |     0.04 | False |
| django           | tests-fix-likely         |    77.9 |       487.1 |  6.3 |    5.32 |          1 |     0.04 | False |
| django           | tests-fix-unsafe         |    85.3 |       459.1 |  5.4 |     3.8 |          8 |      4.2 | False |
| django           | tests-infer-basedpyright |    47.8 |       446.5 |  9.3 |    5.71 |          8 |     8.87 | False |
| django           | tests-infer-ty           |    59.9 |       456.3 |  7.6 |    4.86 |         12 |     6.18 | False |
| django           | tests-infer-pyrefly      |    67.1 |       482.5 |  7.2 |    5.43 |         10 |     6.79 | False |
| django           | tests-infer-trace        |    85.9 |       481.9 |  5.6 |    4.46 |          9 |     4.95 | False |
| django           | tests                    |   582.0 |      3775.6 |  6.5 |    5.67 |          1 |     0.04 | False |
| sqlalchemy       | check                    |     7.4 |        14.7 |  2.0 |    0.85 |          2 |     1.06 | False |
| sqlalchemy       | fix-certain              |    19.0 |        40.0 |  2.1 |    0.95 |          3 |     1.21 | False |
| sqlalchemy       | fix-likely               |    29.8 |        51.0 |  1.7 |    1.35 |          3 |     1.69 | False |
| sqlalchemy       | fix-unsafe               |    20.6 |        42.0 |  2.0 |     1.0 |          2 |     1.25 | False |
| sqlalchemy       | infer-basedpyright       |    84.8 |       326.9 |  3.9 |    7.55 |          4 |     9.24 | False |
| sqlalchemy       | infer-ty                 |    36.7 |        98.9 |  2.7 |    3.73 |          3 |     4.17 | False |
| sqlalchemy       | infer-pyrefly            |    29.3 |        84.4 |  2.9 |    3.36 |          3 |      4.2 | False |
| sqlalchemy       | census                   |     7.8 |         5.6 |  0.7 |    0.09 |          2 |     1.06 | False |
| sqlalchemy       | coverage                 |     2.0 |         5.7 |  2.9 |    0.39 |          3 |     0.47 | False |
| sqlalchemy       | timing                   |    21.6 |        29.8 |  1.4 |    0.85 |         16 |     1.07 | False |
| sqlalchemy       | traced                   |   114.7 |       953.0 |  8.3 |    5.05 |         10 |     5.72 | False |
| sqlalchemy       | tests-released           |   126.3 |      1121.9 |  8.9 |    5.72 |          9 |     7.44 | False |
| sqlalchemy       | tests-fix-certain        |   104.3 |      1059.0 | 10.2 |    5.75 |          9 |     6.59 | False |
| sqlalchemy       | tests-fix-likely         |   116.5 |      1082.0 |  9.3 |    5.75 |          8 |     6.59 | False |
| sqlalchemy       | tests-fix-unsafe         |    96.5 |       977.6 | 10.1 |    5.14 |         11 |      6.0 | False |
| sqlalchemy       | tests-infer-basedpyright |    99.9 |      1041.8 | 10.4 |    5.79 |         12 |     6.57 | False |
| sqlalchemy       | tests-infer-ty           |    92.1 |      1029.1 | 11.2 |    5.75 |          8 |     7.33 | False |
| sqlalchemy       | tests-infer-pyrefly      |   160.4 |      1116.4 |  7.0 |     5.8 |          7 |      7.4 | False |
| sqlalchemy       | tests-infer-trace        |   178.2 |       808.0 |  4.5 |    3.56 |          8 |     3.75 | False |
| sqlalchemy       | tests                    |   267.3 |      1741.5 |  6.5 |    4.55 |         11 |     5.18 | False |
| sqlalchemy       | types-released           |     9.2 |         8.1 |  0.9 |    0.43 |          1 |     0.37 | False |
| sqlalchemy       | types-fix-certain        |     7.6 |         6.7 |  0.9 |    0.31 |          1 |     0.37 | False |
| sqlalchemy       | types-fix-likely         |     8.2 |         7.1 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy       | types-fix-unsafe         |     7.0 |         6.6 |  0.9 |     0.3 |          1 |     0.37 | False |
| sqlalchemy       | types-infer-basedpyright |     7.2 |         7.0 |  1.0 |    0.33 |          1 |     0.39 | False |
| sqlalchemy       | types-infer-ty           |     8.4 |         7.1 |  0.8 |     0.3 |          1 |     0.36 | False |
| sqlalchemy       | types-infer-pyrefly      |     7.0 |         6.6 |  0.9 |    0.32 |          1 |     0.37 | False |
| sqlalchemy       | types-infer-trace        |     7.2 |         6.6 |  0.9 |    0.31 |          1 |      0.4 | False |
| sqlalchemy       | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | check                    |     3.0 |         4.2 |  1.4 |     0.3 |          2 |     0.92 | False |
| pydantic         | fix-certain              |     4.8 |        10.6 |  2.2 |    0.44 |          3 |     1.19 | False |
| pydantic         | fix-likely               |     5.8 |        13.3 |  2.3 |    0.49 |          4 |     1.49 | False |
| pydantic         | fix-unsafe               |    12.4 |        14.1 |  1.1 |    0.55 |          3 |     1.21 | False |
| pydantic         | infer-basedpyright       |    54.7 |       139.7 |  2.6 |    3.08 |          4 |     3.92 | False |
| pydantic         | infer-ty                 |     7.8 |        23.5 |  3.0 |    1.67 |          3 |     2.05 | False |
| pydantic         | infer-pyrefly            |    14.0 |        46.7 |  3.3 |    2.52 |          4 |     3.06 | False |
| pydantic         | census                   |     1.0 |         0.8 |  0.8 |    0.05 |          2 |     0.92 | False |
| pydantic         | coverage                 |     1.0 |         2.0 |  2.0 |     0.2 |          3 |     0.45 | False |
| pydantic         | timing                   |     4.8 |         6.9 |  1.4 |     0.3 |         16 |     0.37 | False |
| pydantic         | traced                   |    68.3 |        66.3 |  1.0 |    0.47 |          1 |     0.56 | False |
| pydantic         | tests-released           |    53.5 |        40.8 |  0.8 |    0.36 |          1 |     0.31 | False |
| pydantic         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic         | tests-fix-unsafe         |    47.3 |        37.5 |  0.8 |    0.28 |          1 |     0.35 | False |
| pydantic         | tests-infer-basedpyright |    44.5 |        36.7 |  0.8 |    0.28 |          1 |     0.31 | False |
| pydantic         | tests-infer-ty           |    42.1 |        36.9 |  0.9 |    0.28 |          1 |     0.35 | False |
| pydantic         | tests-infer-pyrefly      |    42.2 |        34.7 |  0.8 |    0.29 |          1 |     0.35 | False |
| pydantic         | tests-infer-trace        |    47.5 |        39.2 |  0.8 |    0.28 |          1 |     0.31 | False |
| pydantic         | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | types-released           |    15.6 |        19.5 |  1.2 |    0.53 |          1 |     0.65 | False |
| pydantic         | types-fix-certain        |    20.4 |        23.5 |  1.2 |    0.91 |          2 |     0.65 | False |
| pydantic         | types-fix-likely         |    16.0 |        19.6 |  1.2 |    0.53 |          1 |     0.67 | False |
| pydantic         | types-fix-unsafe         |    16.4 |        21.4 |  1.3 |    0.89 |          1 |     0.64 | False |
| pydantic         | types-infer-basedpyright |    20.8 |        23.7 |  1.1 |    0.57 |          2 |     0.69 | False |
| pydantic         | types-infer-ty           |    16.2 |        20.5 |  1.3 |    0.53 |          2 |     0.66 | False |
| pydantic         | types-infer-pyrefly      |    17.6 |        20.7 |  1.2 |    0.54 |          2 |      0.7 | False |
| pydantic         | types-infer-trace        |    14.6 |        18.8 |  1.3 |    0.53 |          2 |     0.66 | False |
| pydantic         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | check                    |    34.4 |       102.8 |  3.0 |    3.27 |          3 |     4.09 | False |
| pandas           | fix-certain              |   109.0 |       272.1 |  2.5 |    4.21 |          3 |     5.06 | False |
| pandas           | fix-likely               |   135.6 |       419.7 |  3.1 |    7.27 |          4 |     9.09 | False |
| pandas           | fix-unsafe               |    99.3 |       288.2 |  2.9 |     4.3 |          3 |     5.39 | False |
| pandas           | infer-basedpyright       |   530.2 |      1305.6 |  2.5 |   15.75 |          3 |    19.92 | False |
| pandas           | infer-ty                 |   240.1 |       758.2 |  3.2 |   13.79 |          3 |    18.29 | False |
| pandas           | infer-pyrefly            |   249.1 |       645.4 |  2.6 |   19.73 |          4 |    25.04 | False |
| pandas           | census                   |    35.8 |        19.4 |  0.5 |    0.33 |          3 |     4.09 | False |
| pandas           | coverage                 |     7.0 |        22.0 |  3.1 |    1.06 |          2 |     1.31 | False |
| pandas           | timing                   |   146.3 |       228.6 |  1.6 |    3.27 |         16 |     4.09 | False |
| pandas           | traced                   |   191.6 |      1151.9 |  6.0 |   14.03 |          6 |    19.82 | False |
| pandas           | tests-released           |   119.4 |       784.5 |  6.6 |   13.12 |          8 |    18.28 | False |
| pandas           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | tests-fix-unsafe         |   162.4 |       829.1 |  5.1 |   13.09 |          7 |    18.18 | False |
| pandas           | tests-infer-basedpyright |   123.1 |       763.1 |  6.2 |   12.99 |          8 |    17.64 | False |
| pandas           | tests-infer-ty           |   136.2 |       820.1 |  6.0 |   12.94 |          7 |    16.99 | False |
| pandas           | tests-infer-pyrefly      |   120.5 |       792.7 |  6.6 |   13.01 |          9 |    16.84 | False |
| pandas           | tests-infer-trace        |   127.8 |       700.9 |  5.5 |   10.61 |          8 |    13.63 | False |
| pandas           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | types-released           |    75.5 |       112.5 |  1.5 |    2.14 |          2 |     2.82 | False |
| pandas           | types-fix-certain        |    69.1 |       105.4 |  1.5 |    2.13 |          2 |     2.66 | False |
| pandas           | types-fix-likely         |    64.9 |        96.3 |  1.5 |    2.25 |          2 |      2.7 | False |
| pandas           | types-fix-unsafe         |    65.7 |       101.7 |  1.5 |    2.12 |          2 |     2.72 | False |
| pandas           | types-infer-basedpyright |    79.9 |        97.7 |  1.2 |     2.2 |          2 |     2.71 | False |
| pandas           | types-infer-ty           |    63.9 |        87.8 |  1.4 |    2.16 |          2 |      2.7 | False |
| pandas           | types-infer-pyrefly      |    77.5 |       101.7 |  1.3 |    2.03 |          2 |     2.94 | False |
| pandas           | types-infer-trace        |    82.9 |       104.0 |  1.3 |    2.05 |          2 |     2.74 | False |
| pandas           | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| twisted          | check                    |     7.0 |        14.8 |  2.1 |    0.83 |          3 |     1.02 | False |
| twisted          | fix-certain              |    14.0 |        36.5 |  2.6 |    0.94 |          4 |     1.17 | False |
| twisted          | fix-likely               |    19.0 |        49.0 |  2.6 |    1.41 |          3 |     1.76 | False |
| twisted          | fix-unsafe               |    16.4 |        38.5 |  2.3 |    0.96 |          3 |      1.2 | False |
| twisted          | infer-basedpyright       |    89.5 |       327.2 |  3.7 |    8.81 |          3 |    11.02 | False |
| twisted          | infer-ty                 |    24.0 |        82.2 |  3.4 |    3.58 |          3 |     4.02 | False |
| twisted          | infer-pyrefly            |    28.7 |        94.1 |  3.3 |    3.95 |          4 |     4.86 | False |
| twisted          | census                   |     7.0 |         5.5 |  0.8 |    0.11 |          3 |     1.02 | False |
| twisted          | coverage                 |     2.8 |         6.3 |  2.2 |    0.37 |          3 |     0.46 | False |
| twisted          | timing                   |    18.0 |        27.9 |  1.5 |    0.82 |         16 |     1.02 | False |
| pip              | check                    |     4.6 |         9.8 |  2.1 |    0.54 |          3 |     0.69 | False |
| pip              | fix-certain              |    13.2 |        29.3 |  2.2 |    0.72 |          3 |      0.9 | False |
| pip              | fix-likely               |    15.8 |        36.8 |  2.3 |    0.89 |          3 |     1.11 | False |
| pip              | fix-unsafe               |    10.6 |        27.0 |  2.5 |    0.71 |          3 |     0.89 | False |
| pip              | infer-basedpyright       |    43.7 |       196.0 |  4.5 |    5.24 |          5 |     6.71 | False |
| pip              | infer-ty                 |    20.2 |        59.8 |  3.0 |    2.84 |          3 |     3.31 | False |
| pip              | infer-pyrefly            |    21.6 |        68.3 |  3.2 |    3.23 |          4 |      3.2 | False |
| pip              | census                   |     3.6 |         3.3 |  0.9 |    0.09 |          3 |     0.69 | False |
| pip              | coverage                 |     2.0 |         4.1 |  2.0 |    0.33 |          3 |      0.4 | False |
| pip              | timing                   |    12.2 |        18.2 |  1.5 |    0.54 |         16 |     0.67 | False |

- django, 0.3.8-rc.1+dev, tests: the tests differ after fix-certain: 1 new
- standard library, 0.3.8-rc.1+dev, infer-basedpyright: held 12.53 GB beside other steps
- standard library, 0.3.8-rc.1+dev, infer-ty: held 15.27 GB beside other steps
- standard library, 0.3.8-rc.1+dev, infer-pyrefly: held 19.05 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-basedpyright: held 15.75 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-ty: held 13.79 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-pyrefly: held 19.73 GB beside other steps
- pandas, 0.3.8-rc.1+dev, traced: held 14.03 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-released: held 13.12 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-fix-unsafe: held 13.09 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-basedpyright: held 12.99 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-ty: held 12.94 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-pyrefly: held 13.01 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-trace: held 10.61 GB beside other steps
- twisted, 0.3.8-rc.1+dev, infer-basedpyright: held 8.81 GB beside other steps
