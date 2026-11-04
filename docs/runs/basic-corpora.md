# Basic corpora

The run `basic` (`python -m tests.corpus`) on original: constricter 0.4.5.dev1+gd61ea5d39.d20261029
(`8c3a75653b6c`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 35 minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14.7  | basic+dev   | 1,867 |          88,565 |        12,334 |         12,772 |         57 |         14 |         8 |        0 | 113,750 |
| django           | 5.2.18  | basic+dev   |   883 |           9,926 |         2,166 |          5,084 |          0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy       | 2.1.4   | basic+dev   |   258 |           8,825 |         1,636 |          2,471 |        572 |        128 |         2 |        1 |  13,635 |
| pydantic         | 2.14.0  | basic+dev   |   105 |           2,072 |           440 |            605 |        184 |         15 |         0 |        0 |   3,316 |
| pandas           | 3.0.6   | basic+dev   | 1,420 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | basic+dev   |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | basic+dev   |   366 |           5,902 |         1,150 |          1,871 |          0 |          0 |         0 |        0 |   8,923 |
| **Total**        |         | basic+dev   | 5,718 | 201,967 (80.0%) | 21,853 (8.7%) | 27,666 (11.0%) | 947 (0.4%) | 159 (0.1%) | 12 (0.0%) | 2 (0.0%) | 252,606 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | basic+dev   | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,330 (32.8%) |   6,946 (6.1%) | 14,213 (12.5%) |      0 |    0 |            0 |
| django           | basic+dev   |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,622 (15.3%) |     726 (4.2%) |  2,945 (17.1%) |      0 |    0 |            0 |
| sqlalchemy       | basic+dev   |  0 / 12,934 |   11,296 / 2,339 |    12,934 / 701 |  13,635 / 0 |  2,144 (15.7%) |     445 (3.3%) |   1,164 (8.5%) |      0 |    0 |            0 |
| pydantic         | basic+dev   |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,196 (36.1%) |     150 (4.5%) |    413 (12.5%) |      0 |    0 |            0 |
| pandas           | basic+dev   |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 17,130 (22.0%) | 24,477 (31.4%) | 25,752 (33.0%) |      0 |    0 |            0 |
| twisted          | basic+dev   |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,435 (13.6%) |  3,741 (20.9%) |  4,829 (27.0%) |      0 |    0 |            0 |
| pip              | basic+dev   |   0 / 8,923 |    7,773 / 1,150 |       8,923 / 0 |   8,923 / 0 |  2,271 (25.5%) |     490 (5.5%) |  1,349 (15.1%) |      0 |    0 |            0 |
| **Total**        | basic+dev   | 0 / 251,498 | 229,633 / 22,973 | 251,498 / 1,108 | 252,606 / 0 | 65,128 (25.8%) | 36,975 (14.6%) | 50,665 (20.1%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | basic+dev   |              1.2% |         33.6% |            39.7% |                  46.0% | +32.5 pts, 32.8% of untyped | +44.8 pts, 45.3% of untyped |
| django           | basic+dev   |              0.0% |         15.3% |            19.5% |                  32.4% | +15.3 pts, 15.3% of untyped | +32.4 pts, 32.4% of untyped |
| sqlalchemy       | basic+dev   |             15.3% |         29.3% |            32.2% |                  36.9% | +14.0 pts, 16.5% of untyped | +21.6 pts, 25.5% of untyped |
| pydantic         | basic+dev   |             22.4% |         52.2% |            55.9% |                  62.5% | +29.8 pts, 38.4% of untyped | +40.0 pts, 51.6% of untyped |
| pandas           | basic+dev   |              1.6% |         23.3% |            54.2% |                  55.8% | +21.7 pts, 22.0% of untyped | +54.2 pts, 55.1% of untyped |
| twisted          | basic+dev   |              0.0% |         13.6% |            34.6% |                  40.6% | +13.6 pts, 13.6% of untyped | +40.6 pts, 40.6% of untyped |
| pip              | basic+dev   |              1.5% |         26.6% |            32.0% |                  41.4% | +25.1 pts, 25.4% of untyped | +39.9 pts, 40.6% of untyped |
| **Total**        | basic+dev   |              2.3% |         27.6% |            42.0% |                  47.3% | +25.3 pts, 25.9% of untyped | +45.0 pts, 46.0% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus           | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ---------------- | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library | certain            | 37,330 |  37,330 |        |        |      0 |    0 | 38,659 |  115,001 |    74.7 |
| standard library | likely             | 44,276 |  37,606 |  6,670 |        |      0 |    0 | 45,605 |  115,001 |   114.5 |
| standard library | unsafe             | 51,543 |  37,337 |  6,650 |  7,556 |      0 |    0 | 52,872 |  115,001 |   108.1 |
| standard library | infer-basedpyright | 59,268 |  37,340 |  7,060 | 14,868 |      0 |    7 | 60,597 |  115,001 |   248.7 |
| standard library | infer-ty           | 57,032 |  37,373 |  7,044 | 12,615 |      0 |    5 | 58,361 |  115,001 |   143.1 |
| standard library | infer-pyrefly      | 59,391 |  37,329 |  7,097 | 14,965 |      0 |   39 | 60,720 |  115,001 |   146.6 |
| django           | certain            |  2,622 |   2,622 |        |        |      0 |    0 |  2,627 |   17,181 |    13.4 |
| django           | likely             |  3,348 |   2,627 |    721 |        |      0 |    0 |  3,353 |   17,181 |    18.7 |
| django           | unsafe             |  5,567 |   2,622 |    719 |  2,226 |      0 |    0 |  5,572 |   17,181 |    24.0 |
| django           | infer-basedpyright |  5,958 |   2,616 |    732 |  2,610 |      0 |    0 |  5,963 |   17,181 |    21.4 |
| django           | infer-ty           |  5,770 |   2,623 |    727 |  2,420 |      0 |    0 |  5,775 |   17,181 |    28.0 |
| django           | infer-pyrefly      |  6,242 |   2,611 |    740 |  2,891 |      0 |    0 |  6,247 |   17,181 |    30.1 |
| django           | infer-trace        |  6,110 |   2,622 |    749 |  2,739 |      0 |    0 |  6,115 |   17,181 |    17.7 |
| sqlalchemy       | certain            |  2,144 |   2,144 |        |        |      0 |    0 |  4,479 |   15,304 |    11.8 |
| sqlalchemy       | likely             |  2,589 |   2,152 |    437 |        |      0 |    0 |  4,924 |   15,304 |    32.4 |
| sqlalchemy       | unsafe             |  3,308 |   2,144 |    437 |    727 |      0 |    0 |  5,643 |   15,304 |    21.7 |
| sqlalchemy       | infer-basedpyright |  4,031 |   2,146 |    474 |  1,411 |      0 |    0 |  6,366 |   15,304 |    60.2 |
| sqlalchemy       | infer-ty           |  3,969 |   2,146 |    463 |  1,360 |      0 |    0 |  6,304 |   15,304 |    27.3 |
| sqlalchemy       | infer-pyrefly      |  3,771 |   2,145 |    456 |  1,170 |      0 |    0 |  6,106 |   15,304 |    31.8 |
| sqlalchemy       | infer-trace        |  3,459 |   2,144 |    437 |    878 |      0 |    0 |  5,794 |   15,304 |    14.4 |
| pydantic         | certain            |  1,196 |   1,196 |        |        |      0 |    0 |  2,098 |    4,019 |     2.3 |
| pydantic         | likely             |  1,346 |   1,203 |    143 |        |      0 |    0 |  2,248 |    4,019 |     2.9 |
| pydantic         | unsafe             |  1,609 |   1,196 |    142 |    271 |      0 |    0 |  2,511 |    4,019 |     4.1 |
| pydantic         | infer-basedpyright |  1,828 |   1,197 |    144 |    487 |      0 |    0 |  2,730 |    4,019 |     6.4 |
| pydantic         | infer-ty           |  1,743 |   1,196 |    140 |    407 |      0 |    0 |  2,645 |    4,019 |     5.1 |
| pydantic         | infer-pyrefly      |  1,807 |   1,196 |    141 |    470 |      0 |    0 |  2,709 |    4,019 |     8.5 |
| pydantic         | infer-trace        |  1,610 |   1,196 |    142 |    272 |      0 |    0 |  2,512 |    4,019 |     7.4 |
| pandas           | certain            | 17,130 |  17,130 |        |        |      0 |    0 | 18,399 |   79,062 |    69.3 |
| pandas           | likely             | 41,607 |  17,342 | 24,265 |        |      0 |    0 | 42,876 |   79,062 |   122.0 |
| pandas           | unsafe             | 42,882 |  17,126 | 24,245 |  1,511 |      0 |    0 | 44,151 |   79,062 |   168.6 |
| pandas           | infer-basedpyright | 48,471 |  17,117 | 24,231 |  7,123 |      0 |   24 | 49,740 |   79,062 |   215.5 |
| pandas           | infer-ty           | 48,405 |  17,126 | 24,241 |  7,038 |      0 |   21 | 49,674 |   79,062 |   158.7 |
| pandas           | infer-pyrefly      | 50,900 |  17,125 | 24,182 |  9,593 |      0 |   25 | 52,169 |   79,062 |   116.2 |
| pandas           | infer-trace        | 44,318 |  17,130 | 24,114 |  3,074 |      0 |    0 | 45,587 |   79,062 |    89.3 |
| twisted          | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     6.9 |
| twisted          | likely             |  6,176 |   2,453 |  3,723 |        |      0 |    0 |  6,176 |   17,874 |    16.5 |
| twisted          | unsafe             |  7,264 |   2,434 |  3,723 |  1,107 |      0 |    0 |  7,264 |   17,874 |    10.0 |
| twisted          | infer-basedpyright |  8,627 |   2,435 |  3,739 |  2,453 |      0 |    0 |  8,627 |   17,874 |    18.6 |
| twisted          | infer-ty           |  7,630 |   2,434 |  3,734 |  1,462 |      0 |    0 |  7,630 |   17,874 |    15.9 |
| twisted          | infer-pyrefly      |  7,665 |   2,434 |  3,733 |  1,498 |      0 |    0 |  7,665 |   17,874 |    18.1 |
| pip              | certain            |  2,271 |   2,271 |        |        |      0 |    0 |  2,408 |    9,064 |     5.6 |
| pip              | likely             |  2,761 |   2,278 |    483 |        |      0 |    0 |  2,898 |    9,064 |     7.7 |
| pip              | unsafe             |  3,620 |   2,271 |    481 |    868 |      0 |    0 |  3,757 |    9,064 |     9.8 |
| pip              | infer-basedpyright |  4,329 |   2,272 |    527 |  1,530 |      0 |    0 |  4,466 |    9,064 |    17.6 |
| pip              | infer-ty           |  3,911 |   2,272 |    500 |  1,139 |      0 |    0 |  4,048 |    9,064 |    12.1 |
| pip              | infer-pyrefly      |  4,116 |   2,270 |    511 |  1,335 |      0 |    0 |  4,253 |    9,064 |    11.3 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 16,729 |  16,729 |        |        |
| certain            | stdlib                 | 13,156 |  13,156 |        |        |
| certain            | call                   |  5,218 |   5,218 |        |        |
| certain            | container+literal      |  3,917 |   3,917 |        |        |
| certain            | builtin                |  2,516 |   2,516 |        |        |
| certain            | loop                   |  2,442 |   2,442 |        |        |
| certain            | container+literal+loop |  1,581 |   1,581 |        |        |
| certain            | copy+loop              |  1,563 |   1,563 |        |        |
| certain            | method                 |  1,366 |   1,366 |        |        |
| certain            | open                   |  1,101 |   1,101 |        |        |
| certain            | literal+method         |    943 |     943 |        |        |
| certain            | returned               |    873 |     873 |        |        |
| likely             | constructor            | 27,268 |     235 | 27,033 |        |
| likely             | literal                | 16,730 |  16,730 |        |        |
| likely             | stdlib                 | 13,245 |  13,245 |        |        |
| likely             | call                   |  5,744 |   5,230 |    514 |        |
| likely             | container+literal      |  3,917 |   3,917 |        |        |
| likely             | builtin                |  2,516 |   2,516 |        |        |
| likely             | method                 |  2,463 |   1,387 |  1,076 |        |
| likely             | loop                   |  2,445 |   2,445 |        |        |
| likely             | copy+loop              |  1,880 |   1,573 |    307 |        |
| likely             | container+literal+loop |  1,581 |   1,581 |        |        |
| likely             | open                   |  1,101 |   1,101 |        |        |
| likely             | copy+stdlib            |  1,041 |     758 |    283 |        |
| unsafe             | constructor            | 27,267 |     235 | 27,032 |        |
| unsafe             | literal                | 16,732 |  16,729 |        |      3 |
| unsafe             | stdlib                 | 13,548 |  13,158 |        |    390 |
| unsafe             | call                   |  5,731 |   5,218 |    513 |        |
| unsafe             | literal+member         |  3,952 |         |        |  3,952 |
| unsafe             | container+literal      |  3,917 |   3,917 |        |        |
| unsafe             | returned               |  3,026 |     875 |        |  2,151 |
| unsafe             | builtin                |  2,516 |   2,516 |        |        |
| unsafe             | loop                   |  2,442 |   2,442 |        |        |
| unsafe             | method                 |  2,442 |   1,366 |  1,076 |        |
| unsafe             | copy+loop              |  1,868 |   1,563 |    305 |        |
| unsafe             | container+literal+loop |  1,581 |   1,581 |        |        |
| infer-basedpyright | constructor            | 27,222 |     234 | 26,988 |        |
| infer-basedpyright | literal                | 16,733 |  16,730 |        |      3 |
| infer-basedpyright | checker                | 14,264 |         |        | 14,264 |
| infer-basedpyright | stdlib                 | 13,658 |  13,106 |        |    552 |
| infer-basedpyright | call                   |  5,804 |   5,216 |    588 |        |
| infer-basedpyright | literal+member         |  3,951 |         |        |  3,951 |
| infer-basedpyright | container+literal      |  3,918 |   3,918 |        |        |
| infer-basedpyright | returned               |  3,232 |     860 |        |  2,372 |
| infer-basedpyright | method                 |  2,535 |   1,366 |  1,169 |        |
| infer-basedpyright | builtin                |  2,516 |   2,516 |        |        |
| infer-basedpyright | loop                   |  2,442 |   2,442 |        |        |
| infer-basedpyright | copy+loop              |  2,179 |   1,564 |    615 |        |
| infer-ty           | constructor            | 27,222 |     235 | 26,987 |        |
| infer-ty           | literal                | 16,732 |  16,729 |        |      3 |
| infer-ty           | stdlib                 | 13,667 |  13,128 |        |    539 |
| infer-ty           | checker                | 10,750 |         |        | 10,750 |
| infer-ty           | call                   |  5,782 |   5,216 |    566 |        |
| infer-ty           | literal+member         |  3,952 |         |        |  3,952 |
| infer-ty           | container+literal      |  3,918 |   3,918 |        |        |
| infer-ty           | returned               |  3,160 |     875 |        |  2,285 |
| infer-ty           | builtin                |  2,516 |   2,516 |        |        |
| infer-ty           | method                 |  2,509 |   1,366 |  1,143 |        |
| infer-ty           | loop                   |  2,442 |   2,442 |        |        |
| infer-ty           | copy+loop              |  2,087 |   1,564 |    523 |        |
| infer-pyrefly      | constructor            | 27,173 |     234 | 26,939 |        |
| infer-pyrefly      | literal                | 16,732 |  16,729 |        |      3 |
| infer-pyrefly      | checker                | 15,717 |         |        | 15,717 |
| infer-pyrefly      | stdlib                 | 13,680 |  13,119 |        |    561 |
| infer-pyrefly      | call                   |  5,779 |   5,216 |    563 |        |
| infer-pyrefly      | literal+member         |  3,951 |         |        |  3,951 |
| infer-pyrefly      | container+literal      |  3,918 |   3,918 |        |        |
| infer-pyrefly      | returned               |  3,180 |     876 |        |  2,304 |
| infer-pyrefly      | method                 |  2,526 |   1,366 |  1,160 |        |
| infer-pyrefly      | builtin                |  2,516 |   2,516 |        |        |
| infer-pyrefly      | loop                   |  2,442 |   2,442 |        |        |
| infer-pyrefly      | copy+loop              |  2,148 |   1,563 |    585 |        |
| infer-trace        | constructor            | 19,934 |       3 | 19,931 |        |
| infer-trace        | literal                |  6,887 |   6,887 |        |        |
| infer-trace        | call                   |  5,367 |   4,854 |    513 |        |
| infer-trace        | literal+member         |  2,165 |         |        |  2,165 |
| infer-trace        | traced                 |  2,126 |         |        |  2,126 |
| infer-trace        | method                 |  1,973 |     983 |    990 |        |
| infer-trace        | container+literal      |  1,561 |   1,561 |        |        |
| infer-trace        | stdlib                 |  1,182 |   1,135 |        |     47 |
| infer-trace        | builtin                |    835 |     835 |        |        |
| infer-trace        | returned               |    598 |     234 |        |    364 |
| infer-trace        | loop                   |    587 |     587 |        |        |
| infer-trace        | copy+loop              |    499 |     390 |    109 |        |
| infer-union        | constructor            | 19,838 |       3 | 19,835 |        |
| infer-union        | literal                |  6,887 |   6,887 |        |        |
| infer-union        | agreed+checker         |  5,804 |         |        |  5,804 |
| infer-union        | call                   |  5,402 |   4,852 |    550 |        |
| infer-union        | checker                |  5,070 |         |        |  5,070 |
| infer-union        | literal+member         |  2,165 |         |        |  2,165 |
| infer-union        | traced                 |  2,075 |         |        |  2,075 |
| infer-union        | method                 |  2,041 |     980 |  1,061 |        |
| infer-union        | container+literal      |  1,561 |   1,561 |        |        |
| infer-union        | stdlib                 |  1,177 |   1,127 |        |     50 |
| infer-union        | builtin                |    835 |     835 |        |        |
| infer-union        | returned               |    606 |     218 |        |    388 |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus           | untyped | guessed | unfixed | unparsed |
| ---------------- | ------: | ------: | ------: | -------: |
| standard library | 113,671 |  14,204 |  62,138 |        0 |
| django           |  17,176 |   2,945 |  11,609 |        0 |
| sqlalchemy       |  12,932 |   1,164 |   9,624 |        0 |
| pydantic         |   3,117 |     413 |   1,508 |        0 |
| pandas           |  77,793 |  25,499 |  35,164 |        0 |
| twisted          |  17,874 |   4,826 |  10,613 |        0 |
| pip              |   8,923 |   1,349 |   5,303 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus           | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by | beside other steps |
| ---------------- | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: | -----------------: |
| standard library |    4 |       53.54 |     22.36 |    1 |                       824.2 |     867.4 | hyperfine |                 no |
| django           |    4 |        11.3 |      4.75 |    1 |                       170.7 |     181.8 | hyperfine |                 no |
| sqlalchemy       |    4 |        9.44 |      5.09 |    1 |                       152.2 |     160.1 | hyperfine |                 no |
| pydantic         |    4 |        1.86 |      0.91 |    1 |                        28.3 |      30.6 | hyperfine |                 no |
| pandas           |    4 |       67.15 |     24.41 |    1 |                      1034.8 |    1067.7 | hyperfine |                 no |
| twisted          |    4 |        7.63 |      3.09 |    1 |                       117.8 |     126.9 | hyperfine |                 no |
| pip              |    4 |         5.0 |      2.12 |    1 |                        81.6 |      86.7 | hyperfine |                 no |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus     | tier    |   told |   held | differed | resting on the trace |                                                                   tests | seconds | untraced |
| ---------- | ------- | -----: | -----: | -------: | -------------------: | ----------------------------------------------------------------------: | ------: | -------: |
| django     |         |        |        |          |                  484 | Ran 17585 tests: FAILED (failures=6, skipped=1149, expected failures=5) |    62.9 |     55.8 |
| django     | certain |    974 |    973 |        1 |                      |                                                                         |         |          |
| django     | likely  |    333 |    332 |        1 |                      |                                                                         |         |          |
| django     | guess   |    399 |    382 |       17 |                      |                                                                         |         |          |
| sqlalchemy |         |        |        |          |                  149 |                          4 failed, 29517 passed, 975 skipped, 1 warning |   132.9 |     96.1 |
| sqlalchemy | certain |  1,184 |  1,164 |       20 |                      |                                                                         |         |          |
| sqlalchemy | likely  |    188 |    184 |        4 |                      |                                                                         |         |          |
| sqlalchemy | guess   |    137 |    134 |        3 |                      |                                                                         |         |          |
| pydantic   |         |        |        |          |                    1 |                         65 failed, 6900 passed, 350 skipped, 29 xfailed |    78.0 |     68.4 |
| pydantic   | certain |    531 |    526 |        5 |                      |                                                                         |         |          |
| pydantic   | likely  |     49 |     49 |        0 |                      |                                                                         |         |          |
| pydantic   | guess   |     31 |     31 |        0 |                      |                                                                         |         |          |
| pandas     |         |        |        |          |                1,560 |                   165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   136.6 |    110.6 |
| pandas     | certain | 13,044 | 12,939 |      105 |                      |                                                                         |         |          |
| pandas     | likely  | 20,767 | 20,689 |       78 |                      |                                                                         |         |          |
| pandas     | guess   |  1,032 |    988 |       44 |                      |                                                                         |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus     | shape                                        | no fix | traced | one type |
| ---------- | -------------------------------------------- | -----: | -----: | -------: |
| django     | `call: chained .method()`                    |  1,353 |    955 |      605 |
| django     | `call: self.method()`                        |    978 |    657 |      420 |
| django     | `call: param.method()`                       |    654 |    474 |      373 |
| django     | `call: imported function`                    |    654 |    273 |      200 |
| django     | `call: local.method()`                       |    545 |    383 |      265 |
| django     | `empty list`                                 |    450 |      0 |        0 |
| django     | `copy: local`                                |    434 |    322 |      226 |
| django     | `attr: chained`                              |    406 |    279 |      182 |
| django     | `copy: param (unannotated)`                  |    348 |    237 |      141 |
| django     | `attr: self.x`                               |    342 |    264 |      135 |
| django     | `None literal`                               |    319 |    104 |      104 |
| django     | `call: imported.attr()`                      |    301 |    145 |       96 |
| django     | `other constant`                             |    270 |     22 |       22 |
| django     | `subscript: other`                           |    265 |    194 |      157 |
| django     | `dict (mixed/unknown elements)`              |    236 |    103 |       72 |
| django     | `empty dict`                                 |    201 |      0 |        0 |
| django     | `call: module function (unannotated)`        |    185 |    133 |       95 |
| django     | `tuple (mixed/unknown elements)`             |    176 |     95 |       72 |
| django     | `copy: imported`                             |    175 |      8 |        7 |
| django     | `call: builtin getattr()`                    |    174 |    154 |       74 |
| django     | `subscript: local[...]`                      |    173 |    108 |       89 |
| django     | `attr: local.x`                              |    170 |    130 |       94 |
| django     | `ListComp (unknown elements)`                |    165 |    119 |       81 |
| django     | `list (mixed/unknown elements)`              |    159 |     56 |       44 |
| django     | `conditional`                                |    157 |    128 |       65 |
| django     | `subscript: param[...]`                      |    136 |    111 |       93 |
| django     | `binop (unknown operands)`                   |    130 |     84 |       77 |
| django     | `attr: param.x`                              |    124 |    102 |       74 |
| django     | `boolop (or)`                                |    112 |     95 |       72 |
| django     | `call: builtin set()`                        |    109 |     16 |       12 |
| django     | `attr: imported.x`                           |    105 |     21 |       17 |
| django     | `call: imported class`                       |     95 |     14 |       14 |
| django     | `call: module.func()`                        |     94 |     68 |       58 |
| django     | `call: builtin enumerate()`                  |     85 |     67 |       38 |
| django     | `call: builtin sorted()`                     |     77 |     57 |       51 |
| django     | `call: builtin list()`                       |     62 |     48 |       36 |
| django     | `subscript: imported[...]`                   |     59 |     40 |       36 |
| django     | `DictComp (unknown elements)`                |     57 |     36 |       19 |
| django     | `call: builtin zip()`                        |     56 |     36 |       14 |
| django     | `call: other name`                           |     52 |     36 |       21 |
| django     | `call: local name`                           |     51 |     35 |       15 |
| django     | `call: builtin property()`                   |     49 |      0 |        0 |
| django     | `boolop (and)`                               |     42 |     29 |       22 |
| django     | `call: global.method()`                      |     42 |     29 |       17 |
| django     | `SetComp (unknown elements)`                 |     40 |     21 |       17 |
| django     | `copy: other`                                |     40 |      8 |        6 |
| django     | `empty tuple`                                |     39 |      0 |        0 |
| django     | `compare`                                    |     35 |     20 |       20 |
| django     | `call: builtin next()`                       |     32 |     31 |       27 |
| django     | `call: module class`                         |     31 |      7 |        7 |
| django     | `GeneratorExp (unknown elements)`            |     29 |     27 |       26 |
| django     | `binop (one side literal)`                   |     29 |      5 |        5 |
| django     | `copy: modclass`                             |     27 |      0 |        0 |
| django     | `copy: moddef`                               |     26 |      0 |        0 |
| django     | `copy: global`                               |     25 |      4 |        4 |
| django     | `call: other callee`                         |     24 |     17 |       12 |
| django     | `attr: module.x`                             |     21 |      5 |        4 |
| django     | `call: builtin iter()`                       |     21 |     17 |       16 |
| django     | `call: builtin reversed()`                   |     19 |     16 |        6 |
| django     | `await: call: self.method()`                 |     18 |     14 |        6 |
| django     | `call: builtin tuple()`                      |     18 |     14 |        8 |
| django     | `attr: modclass.x`                           |     17 |      1 |        1 |
| django     | `call: builtin type()`                       |     17 |     14 |       10 |
| django     | `await: call: chained .method()`             |     17 |     17 |        3 |
| django     | `call: other.method()`                       |     15 |     11 |        6 |
| django     | `call: builtin object()`                     |     14 |      2 |        2 |
| django     | `call: modclass.method()`                    |     14 |      5 |        5 |
| django     | `binop: literal % formatting`                |     13 |      8 |        8 |
| django     | `attr: cls.x`                                |     12 |     12 |       10 |
| django     | `copy: builtin`                              |     12 |      1 |        1 |
| django     | `call: builtin staticmethod()`               |     11 |      0 |        0 |
| django     | `call: builtin max()`                        |     11 |      7 |        7 |
| django     | `call: cls.method()`                         |     10 |      6 |        4 |
| django     | `copy: self`                                 |      9 |      7 |        4 |
| django     | `call: capitalised`                          |      9 |      6 |        3 |
| django     | `await: call: other name`                    |      9 |      9 |        8 |
| django     | `call: builtin dict()`                       |      8 |      7 |        3 |
| django     | `call: builtin.method()`                     |      8 |      6 |        5 |
| django     | `call: builtin map()`                        |      7 |      3 |        2 |
| django     | `set (mixed/unknown elements)`               |      6 |      4 |        4 |
| django     | `call: builtin min()`                        |      6 |      2 |        2 |
| django     | `call: builtin frozenset()`                  |      6 |      1 |        1 |
| django     | `attr: global.x`                             |      6 |      1 |        1 |
| django     | `await: call: module.func()`                 |      6 |      0 |        0 |
| django     | `call: param name`                           |      5 |      5 |        1 |
| django     | `await: call: param name`                    |      4 |      4 |        3 |
| django     | `call: builtin sum()`                        |      4 |      3 |        3 |
| django     | `call: builtin filter()`                     |      4 |      4 |        4 |
| django     | `call: builtin divmod()`                     |      4 |      4 |        4 |
| django     | `call: builtin str()`                        |      3 |      2 |        2 |
| django     | `call: builtin len()`                        |      3 |      2 |        2 |
| django     | `call: str-literal.method()`                 |      3 |      3 |        3 |
| django     | `attr: other.x`                              |      3 |      3 |        2 |
| django     | `await: call: param.method()`                |      2 |      2 |        0 |
| django     | `subscript: self[...]`                       |      2 |      1 |        1 |
| django     | `call: global name`                          |      2 |      0 |        0 |
| django     | `call: builtin slice()`                      |      2 |      1 |        1 |
| django     | `await: call: other callee`                  |      2 |      2 |        2 |
| django     | `JoinedStr`                                  |      2 |      1 |        1 |
| django     | `attr: builtin.x`                            |      2 |      1 |        1 |
| django     | `call: builtin int()`                        |      2 |      1 |        1 |
| django     | `call: bytes-literal.method()`               |      2 |      1 |        1 |
| django     | `subscript: global[...]`                     |      2 |      2 |        2 |
| django     | `await: call: local.method()`                |      1 |      1 |        0 |
| django     | `await: call: module function (unannotated)` |      1 |      1 |        1 |
| django     | `call: builtin abs()`                        |      1 |      1 |        1 |
| django     | `await: call: local name`                    |      1 |      1 |        0 |
| django     | `await: call: other.method()`                |      1 |      1 |        0 |
| django     | `call: builtin vars()`                       |      1 |      1 |        0 |
| django     | `call: builtin super()`                      |      1 |      1 |        1 |
| django     | `subscript: other[...]`                      |      1 |      1 |        0 |
| django     | `await: call: imported function`             |      1 |      1 |        0 |
| django     | `call: builtin __import__()`                 |      1 |      1 |        1 |
| django     | `call: builtin repr()`                       |      1 |      1 |        1 |
| django     | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| sqlalchemy | `call: chained .method()`                    |    943 |    453 |      305 |
| sqlalchemy | `other constant`                             |    590 |      8 |        8 |
| sqlalchemy | `attr: chained`                              |    571 |    284 |      215 |
| sqlalchemy | `call: self.method()`                        |    567 |    297 |      164 |
| sqlalchemy | `call: local.method()`                       |    521 |    283 |      177 |
| sqlalchemy | `call: param.method()`                       |    446 |    273 |      161 |
| sqlalchemy | `attr: self.x`                               |    358 |    278 |      158 |
| sqlalchemy | `subscript: other`                           |    354 |    215 |      136 |
| sqlalchemy | `copy: local`                                |    351 |    220 |      135 |
| sqlalchemy | `call: imported function`                    |    334 |    158 |       90 |
| sqlalchemy | `call: imported.attr()`                      |    317 |    167 |      110 |
| sqlalchemy | `attr: param.x`                              |    312 |    248 |      149 |
| sqlalchemy | `attr: local.x`                              |    253 |    203 |      127 |
| sqlalchemy | `tuple (mixed/unknown elements)`             |    202 |    135 |       92 |
| sqlalchemy | `copy: param (unannotated)`                  |    183 |    136 |       92 |
| sqlalchemy | `subscript: local[...]`                      |    173 |     92 |       52 |
| sqlalchemy | `None literal`                               |    172 |     73 |       73 |
| sqlalchemy | `ListComp (unknown elements)`                |    158 |    120 |       71 |
| sqlalchemy | `copy: modclass`                             |    147 |      1 |        1 |
| sqlalchemy | `attr: imported.x`                           |    145 |     17 |       17 |
| sqlalchemy | `copy: imported`                             |    118 |      1 |        1 |
| sqlalchemy | `call: builtin list()`                       |    117 |     75 |       45 |
| sqlalchemy | `empty list`                                 |    114 |      0 |        0 |
| sqlalchemy | `call: module.func()`                        |    107 |     52 |       43 |
| sqlalchemy | `copy: param (annotated)`                    |    106 |     87 |       52 |
| sqlalchemy | `dict (mixed/unknown elements)`              |    103 |     16 |       14 |
| sqlalchemy | `call: builtin getattr()`                    |    100 |     82 |       37 |
| sqlalchemy | `call: param name`                           |     90 |     36 |       14 |
| sqlalchemy | `empty dict`                                 |     82 |      0 |        0 |
| sqlalchemy | `call: builtin set()`                        |     82 |     34 |       23 |
| sqlalchemy | `binop (unknown operands)`                   |     81 |     42 |       31 |
| sqlalchemy | `call: other name`                           |     76 |     58 |       33 |
| sqlalchemy | `subscript: param[...]`                      |     74 |     60 |       36 |
| sqlalchemy | `boolop (or)`                                |     73 |     59 |       47 |
| sqlalchemy | `conditional`                                |     71 |     40 |       21 |
| sqlalchemy | `call: local name`                           |     63 |     51 |       24 |
| sqlalchemy | `copy: other`                                |     63 |     20 |       15 |
| sqlalchemy | `list (mixed/unknown elements)`              |     62 |     18 |       10 |
| sqlalchemy | `DictComp (unknown elements)`                |     61 |     35 |       17 |
| sqlalchemy | `call: module function (unannotated)`        |     59 |     49 |       37 |
| sqlalchemy | `call: builtin zip()`                        |     57 |     37 |       20 |
| sqlalchemy | `copy: global`                               |     50 |      6 |        6 |
| sqlalchemy | `call: builtin dict()`                       |     49 |     24 |       13 |
| sqlalchemy | `call: builtin enumerate()`                  |     39 |     29 |        6 |
| sqlalchemy | `call: builtin tuple()`                      |     38 |     15 |        5 |
| sqlalchemy | `call: other.method()`                       |     36 |     20 |       10 |
| sqlalchemy | `SetComp (unknown elements)`                 |     35 |     21 |       15 |
| sqlalchemy | `call: imported class`                       |     33 |      7 |        7 |
| sqlalchemy | `call: module function (annotated)`          |     32 |     29 |       14 |
| sqlalchemy | `call: cls.method()`                         |     30 |     24 |       15 |
| sqlalchemy | `boolop (and)`                               |     25 |     25 |       21 |
| sqlalchemy | `call: builtin.method()`                     |     24 |     21 |       10 |
| sqlalchemy | `call: module class`                         |     23 |     15 |       15 |
| sqlalchemy | `attr: modclass.x`                           |     21 |      0 |        0 |
| sqlalchemy | `attr: cls.x`                                |     20 |     20 |       10 |
| sqlalchemy | `empty tuple`                                |     16 |      0 |        0 |
| sqlalchemy | `compare`                                    |     15 |      9 |        9 |
| sqlalchemy | `call: builtin type()`                       |     15 |     10 |        3 |
| sqlalchemy | `call: other callee`                         |     15 |     11 |        5 |
| sqlalchemy | `await: call: imported function`             |     15 |     13 |        8 |
| sqlalchemy | `attr: global.x`                             |     14 |      0 |        0 |
| sqlalchemy | `GeneratorExp (unknown elements)`            |     13 |      6 |        6 |
| sqlalchemy | `call: global.method()`                      |     13 |     11 |       10 |
| sqlalchemy | `copy: moddef`                               |     13 |      0 |        0 |
| sqlalchemy | `call: builtin sorted()`                     |     12 |      8 |        7 |
| sqlalchemy | `subscript: global[...]`                     |     12 |     11 |        9 |
| sqlalchemy | `call: global name`                          |     12 |     12 |        4 |
| sqlalchemy | `attr: module.x`                             |     11 |      9 |        9 |
| sqlalchemy | `copy: builtin`                              |     11 |      0 |        0 |
| sqlalchemy | `attr: other.x`                              |     10 |      7 |        7 |
| sqlalchemy | `call: builtin object()`                     |     10 |      6 |        6 |
| sqlalchemy | `call: modclass.method()`                    |      8 |      8 |        5 |
| sqlalchemy | `subscript: other[...]`                      |      8 |      8 |        4 |
| sqlalchemy | `call: builtin reversed()`                   |      8 |      6 |        6 |
| sqlalchemy | `copy: self`                                 |      7 |      6 |        5 |
| sqlalchemy | `await: call: chained .method()`             |      6 |      1 |        1 |
| sqlalchemy | `call: builtin __import__()`                 |      5 |      2 |        2 |
| sqlalchemy | `set (mixed/unknown elements)`               |      5 |      3 |        2 |
| sqlalchemy | `await: call: self.method()`                 |      4 |      4 |        4 |
| sqlalchemy | `call: self name`                            |      4 |      4 |        2 |
| sqlalchemy | `call: builtin frozenset()`                  |      4 |      0 |        0 |
| sqlalchemy | `call: builtin int()`                        |      3 |      1 |        1 |
| sqlalchemy | `binop (one side literal)`                   |      3 |      3 |        3 |
| sqlalchemy | `call: builtin bool()`                       |      3 |      3 |        3 |
| sqlalchemy | `subscript: imported[...]`                   |      3 |      2 |        1 |
| sqlalchemy | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| sqlalchemy | `await: call: local.method()`                |      2 |      0 |        0 |
| sqlalchemy | `unaryop USub`                               |      2 |      1 |        1 |
| sqlalchemy | `call: builtin next()`                       |      2 |      2 |        0 |
| sqlalchemy | `call: builtin max()`                        |      2 |      2 |        2 |
| sqlalchemy | `call: builtin globals()`                    |      2 |      1 |        1 |
| sqlalchemy | `call: builtin eval()`                       |      2 |      2 |        0 |
| sqlalchemy | `subscript: self[...]`                       |      2 |      2 |        0 |
| sqlalchemy | `call: builtin vars()`                       |      2 |      2 |        2 |
| sqlalchemy | `call: builtin sum()`                        |      2 |      2 |        2 |
| sqlalchemy | `await: call: module function (unannotated)` |      2 |      2 |        2 |
| sqlalchemy | `await: copy: param (annotated)`             |      1 |      0 |        0 |
| sqlalchemy | `JoinedStr`                                  |      1 |      1 |        1 |
| sqlalchemy | `call: builtin len()`                        |      1 |      1 |        1 |
| sqlalchemy | `await: call: module.func()`                 |      1 |      0 |        0 |
| sqlalchemy | `await: call: builtin anext()`               |      1 |      0 |        0 |
| sqlalchemy | `call: builtin property()`                   |      1 |      0 |        0 |
| sqlalchemy | `subscript: modclass[...]`                   |      1 |      0 |        0 |
| sqlalchemy | `call: builtin str()`                        |      1 |      1 |        1 |
| sqlalchemy | `binop: literal % formatting`                |      1 |      1 |        1 |
| sqlalchemy | `call: capitalised`                          |      1 |      1 |        1 |
| sqlalchemy | `call: builtin id()`                         |      1 |      1 |        1 |
| sqlalchemy | `await: copy: local`                         |      1 |      1 |        0 |
| sqlalchemy | `call: str-literal.method()`                 |      1 |      1 |        1 |
| pydantic   | `call: chained .method()`                    |    125 |     53 |       35 |
| pydantic   | `call: imported function`                    |    112 |     61 |       42 |
| pydantic   | `call: local.method()`                       |    111 |     55 |       30 |
| pydantic   | `call: param.method()`                       |    101 |     59 |       31 |
| pydantic   | `call: self.method()`                        |     56 |     32 |        9 |
| pydantic   | `call: builtin getattr()`                    |     53 |     29 |       17 |
| pydantic   | `call: module function (annotated)`          |     53 |     14 |        8 |
| pydantic   | `attr: param.x`                              |     46 |     25 |       12 |
| pydantic   | `conditional`                                |     37 |     18 |       10 |
| pydantic   | `copy: param (annotated)`                    |     36 |     20 |       12 |
| pydantic   | `copy: local`                                |     35 |     16 |       12 |
| pydantic   | `tuple (mixed/unknown elements)`             |     35 |      8 |        6 |
| pydantic   | `call: imported.attr()`                      |     33 |     28 |       10 |
| pydantic   | `attr: chained`                              |     33 |      5 |        4 |
| pydantic   | `subscript: other`                           |     32 |     11 |        3 |
| pydantic   | `boolop (or)`                                |     27 |     14 |        6 |
| pydantic   | `subscript: param[...]`                      |     26 |     15 |       12 |
| pydantic   | `empty dict`                                 |     25 |      0 |        0 |
| pydantic   | `attr: local.x`                              |     25 |      8 |        5 |
| pydantic   | `call: module class`                         |     23 |      2 |        2 |
| pydantic   | `dict (mixed/unknown elements)`              |     22 |     15 |       11 |
| pydantic   | `binop (unknown operands)`                   |     21 |      8 |        6 |
| pydantic   | `copy: imported`                             |     21 |      2 |        2 |
| pydantic   | `attr: cls.x`                                |     20 |      6 |        4 |
| pydantic   | `call: module.func()`                        |     20 |      9 |        6 |
| pydantic   | `subscript: imported[...]`                   |     20 |      1 |        0 |
| pydantic   | `None literal`                               |     19 |     10 |       10 |
| pydantic   | `other constant`                             |     18 |      1 |        1 |
| pydantic   | `ListComp (unknown elements)`                |     16 |      7 |        3 |
| pydantic   | `empty list`                                 |     16 |      0 |        0 |
| pydantic   | `DictComp (unknown elements)`                |     15 |      2 |        1 |
| pydantic   | `copy: builtin`                              |     14 |      0 |        0 |
| pydantic   | `call: builtin zip()`                        |     13 |      2 |        2 |
| pydantic   | `subscript: local[...]`                      |     12 |      4 |        4 |
| pydantic   | `copy: global`                               |     12 |      5 |        3 |
| pydantic   | `attr: self.x`                               |     12 |      5 |        2 |
| pydantic   | `call: builtin tuple()`                      |     12 |      5 |        4 |
| pydantic   | `call: builtin enumerate()`                  |     12 |      2 |        1 |
| pydantic   | `call: builtin dict()`                       |     12 |      1 |        0 |
| pydantic   | `call: param name`                           |     11 |     11 |        6 |
| pydantic   | `call: other name`                           |     10 |      5 |        3 |
| pydantic   | `call: builtin list()`                       |     10 |      7 |        6 |
| pydantic   | `set (mixed/unknown elements)`               |     10 |      0 |        0 |
| pydantic   | `call: builtin set()`                        |      8 |      1 |        1 |
| pydantic   | `GeneratorExp (unknown elements)`            |      8 |      2 |        2 |
| pydantic   | `call: builtin reversed()`                   |      7 |      6 |        2 |
| pydantic   | `call: global.method()`                      |      7 |      1 |        0 |
| pydantic   | `call: builtin object()`                     |      6 |      1 |        1 |
| pydantic   | `copy: other`                                |      6 |      5 |        5 |
| pydantic   | `attr: imported.x`                           |      6 |      2 |        2 |
| pydantic   | `call: cls.method()`                         |      6 |      2 |        1 |
| pydantic   | `call: local name`                           |      5 |      3 |        2 |
| pydantic   | `call: capitalised`                          |      5 |      2 |        2 |
| pydantic   | `list (mixed/unknown elements)`              |      5 |      3 |        2 |
| pydantic   | `attr: module.x`                             |      4 |      0 |        0 |
| pydantic   | `-`                                          |      4 |      0 |        0 |
| pydantic   | `call: builtin type()`                       |      4 |      3 |        0 |
| pydantic   | `call: other.method()`                       |      4 |      4 |        2 |
| pydantic   | `call: imported class`                       |      4 |      0 |        0 |
| pydantic   | `call: builtin next()`                       |      4 |      2 |        1 |
| pydantic   | `call: global name`                          |      4 |      4 |        4 |
| pydantic   | `SetComp (unknown elements)`                 |      3 |      2 |        0 |
| pydantic   | `compare`                                    |      3 |      0 |        0 |
| pydantic   | `attr: modclass.x`                           |      3 |      2 |        2 |
| pydantic   | `call: builtin.method()`                     |      3 |      3 |        2 |
| pydantic   | `NamedExpr`                                  |      2 |      0 |        0 |
| pydantic   | `call: builtin len()`                        |      2 |      2 |        2 |
| pydantic   | `attr: builtin.x`                            |      2 |      0 |        0 |
| pydantic   | `copy: cls`                                  |      2 |      2 |        1 |
| pydantic   | `subscript: builtin[...]`                    |      2 |      0 |        0 |
| pydantic   | `attr: other.x`                              |      2 |      0 |        0 |
| pydantic   | `subscript: global[...]`                     |      2 |      1 |        1 |
| pydantic   | `call: builtin max()`                        |      2 |      2 |        2 |
| pydantic   | `call: builtin min()`                        |      2 |      2 |        2 |
| pydantic   | `call: str-literal.method()`                 |      2 |      0 |        0 |
| pydantic   | `call: builtin globals()`                    |      1 |      1 |        1 |
| pydantic   | `copy: moddef`                               |      1 |      0 |        0 |
| pydantic   | `call: modclass.method()`                    |      1 |      1 |        1 |
| pydantic   | `binop (one side literal)`                   |      1 |      1 |        1 |
| pydantic   | `call: builtin iter()`                       |      1 |      0 |        0 |
| pydantic   | `call: builtin open()`                       |      1 |      0 |        0 |
| pydantic   | `copy: self`                                 |      1 |      0 |        0 |
| pandas     | `call: local.method()`                       |  5,964 |  4,931 |    4,585 |
| pandas     | `call: chained .method()`                    |  4,671 |  3,605 |    3,281 |
| pandas     | `call: module.func()`                        |  3,385 |  2,238 |    2,130 |
| pandas     | `copy: param (unannotated)`                  |  1,960 |  1,740 |      799 |
| pandas     | `subscript: other`                           |  1,510 |  1,226 |    1,093 |
| pandas     | `call: imported function`                    |  1,505 |  1,069 |      914 |
| pandas     | `call: param.method()`                       |  1,413 |    984 |      774 |
| pandas     | `binop (unknown operands)`                   |  1,112 |    955 |      806 |
| pandas     | `subscript: local[...]`                      |    948 |    755 |      706 |
| pandas     | `attr: chained`                              |    792 |    530 |      434 |
| pandas     | `list (mixed/unknown elements)`              |    780 |    534 |      401 |
| pandas     | `call: param name`                           |    769 |    726 |      269 |
| pandas     | `call: imported class`                       |    756 |    651 |      646 |
| pandas     | `call: self.method()`                        |    593 |    402 |      242 |
| pandas     | `call: other callee`                         |    503 |    418 |      340 |
| pandas     | `conditional`                                |    470 |    379 |      202 |
| pandas     | `attr: local.x`                              |    439 |    332 |      271 |
| pandas     | `copy: local`                                |    412 |    272 |      194 |
| pandas     | `subscript: param[...]`                      |    384 |    276 |      167 |
| pandas     | `tuple (mixed/unknown elements)`             |    372 |    225 |      174 |
| pandas     | `call: imported.attr()`                      |    368 |    266 |      196 |
| pandas     | `ListComp (unknown elements)`                |    360 |    186 |      132 |
| pandas     | `compare`                                    |    347 |    271 |      250 |
| pandas     | `dict (mixed/unknown elements)`              |    332 |    209 |      182 |
| pandas     | `call: builtin getattr()`                    |    307 |    224 |      153 |
| pandas     | `call: builtin zip()`                        |    306 |    209 |      151 |
| pandas     | `call: local name`                           |    296 |    255 |      149 |
| pandas     | `attr: param.x`                              |    281 |    188 |      101 |
| pandas     | `call: module function (unannotated)`        |    278 |    135 |       84 |
| pandas     | `empty list`                                 |    276 |      0 |        0 |
| pandas     | `attr: self.x`                               |    274 |    192 |      105 |
| pandas     | `binop (one side literal)`                   |    254 |    200 |      179 |
| pandas     | `call: builtin enumerate()`                  |    233 |    156 |      108 |
| pandas     | `other constant`                             |    172 |     48 |       48 |
| pandas     | `call: builtin list()`                       |    170 |    126 |       86 |
| pandas     | `None literal`                               |    157 |    113 |      113 |
| pandas     | `attr: module.x`                             |    121 |     84 |       82 |
| pandas     | `Lambda`                                     |    120 |     75 |       75 |
| pandas     | `call: global.method()`                      |    118 |      4 |        2 |
| pandas     | `call: other name`                           |    113 |     75 |       52 |
| pandas     | `attr: imported.x`                           |     94 |     23 |       23 |
| pandas     | `empty dict`                                 |     90 |      0 |        0 |
| pandas     | `copy: imported`                             |     89 |     50 |       50 |
| pandas     | `call: module function (annotated)`          |     86 |     48 |       26 |
| pandas     | `copy: other`                                |     78 |      7 |        4 |
| pandas     | `copy: param (annotated)`                    |     70 |     46 |       32 |
| pandas     | `GeneratorExp (unknown elements)`            |     70 |     60 |       60 |
| pandas     | `call: capitalised`                          |     60 |     59 |       58 |
| pandas     | `copy: builtin`                              |     59 |     42 |       42 |
| pandas     | `DictComp (unknown elements)`                |     58 |     43 |       33 |
| pandas     | `call: builtin set()`                        |     49 |     18 |       13 |
| pandas     | `unaryop Invert`                             |     40 |     28 |       26 |
| pandas     | `call: other.method()`                       |     39 |     20 |       15 |
| pandas     | `boolop (and)`                               |     37 |     22 |       21 |
| pandas     | `call: builtin next()`                       |     35 |     29 |       21 |
| pandas     | `call: builtin divmod()`                     |     35 |     24 |       24 |
| pandas     | `boolop (or)`                                |     32 |     20 |       20 |
| pandas     | `call: builtin dict()`                       |     31 |     11 |        6 |
| pandas     | `call: builtin sorted()`                     |     29 |     23 |       22 |
| pandas     | `call: builtin tuple()`                      |     26 |     17 |        9 |
| pandas     | `call: builtin type()`                       |     26 |     25 |        6 |
| pandas     | `call: builtin slice()`                      |     25 |     22 |       22 |
| pandas     | `call: cls name`                             |     22 |     15 |        1 |
| pandas     | `call: builtin open()`                       |     20 |     13 |        6 |
| pandas     | `unaryop USub`                               |     19 |     14 |       14 |
| pandas     | `call: builtin max()`                        |     19 |     15 |       13 |
| pandas     | `copy: self`                                 |     18 |     16 |       10 |
| pandas     | `subscript: self[...]`                       |     18 |     16 |       11 |
| pandas     | `subscript: imported[...]`                   |     17 |     13 |       11 |
| pandas     | `copy: moddef`                               |     17 |      0 |        0 |
| pandas     | `attr: other.x`                              |     14 |      1 |        1 |
| pandas     | `SetComp (unknown elements)`                 |     14 |     10 |        5 |
| pandas     | `copy: global`                               |     13 |      7 |        6 |
| pandas     | `subscript: global[...]`                     |     13 |     11 |        4 |
| pandas     | `call: cls.method()`                         |     12 |     11 |        8 |
| pandas     | `set (mixed/unknown elements)`               |     12 |      5 |        5 |
| pandas     | `call: builtin min()`                        |     12 |      7 |        6 |
| pandas     | `call: modclass.method()`                    |     11 |      8 |        8 |
| pandas     | `call: builtin len()`                        |     11 |      4 |        4 |
| pandas     | `call: builtin.method()`                     |     10 |      9 |        8 |
| pandas     | `copy: modclass`                             |     10 |      0 |        0 |
| pandas     | `JoinedStr`                                  |      8 |      4 |        4 |
| pandas     | `attr: cls.x`                                |      7 |      5 |        4 |
| pandas     | `call: builtin map()`                        |      7 |      7 |        7 |
| pandas     | `call: builtin abs()`                        |      7 |      6 |        6 |
| pandas     | `call: module class`                         |      7 |      3 |        2 |
| pandas     | `subscript: other[...]`                      |      6 |      3 |        3 |
| pandas     | `call: builtin iter()`                       |      6 |      4 |        3 |
| pandas     | `call: builtin property()`                   |      5 |      0 |        0 |
| pandas     | `call: builtin frozenset()`                  |      5 |      1 |        1 |
| pandas     | `call: builtin eval()`                       |      5 |      5 |        5 |
| pandas     | `call: builtin sum()`                        |      4 |      2 |        2 |
| pandas     | `call: builtin range()`                      |      4 |      2 |        2 |
| pandas     | `call: builtin pow()`                        |      4 |      4 |        4 |
| pandas     | `call: builtin all()`                        |      3 |      2 |        2 |
| pandas     | `call: global name`                          |      3 |      0 |        0 |
| pandas     | `call: builtin round()`                      |      3 |      1 |        1 |
| pandas     | `unaryop UAdd`                               |      3 |      3 |        3 |
| pandas     | `copy: cls`                                  |      2 |      0 |        0 |
| pandas     | `call: builtin object()`                     |      2 |      1 |        1 |
| pandas     | `call: str-literal.method()`                 |      2 |      1 |        1 |
| pandas     | `call: self name`                            |      1 |      1 |        1 |
| pandas     | `attr: modclass.x`                           |      1 |      1 |        1 |
| pandas     | `call: builtin ord()`                        |      1 |      0 |        0 |
| pandas     | `call: builtin isinstance()`                 |      1 |      1 |        1 |
| pandas     | `call: builtin float()`                      |      1 |      0 |        0 |
| pandas     | `call: builtin reversed()`                   |      1 |      0 |        0 |
| pandas     | `call: builtin bytes()`                      |      1 |      1 |        1 |
| pandas     | `attr: builtin.x`                            |      1 |      1 |        1 |
| pandas     | `empty tuple`                                |      1 |      0 |        0 |
| pandas     | `call: builtin repr()`                       |      1 |      1 |        1 |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus     | run                                   | same as released | summary                                                    | new failures | gone | named | skipped anew | skipped no more |
| ---------- | ------------------------------------- | ---------------- | ---------------------------------------------------------- | -----------: | ---: | ----: | -----------: | --------------: |
| django     | released                              |                  | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped |              |      |       |              |                 |
| django     | fix-certain                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | fix-likely                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | fix-unsafe                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | infer-basedpyright                    | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | infer-pyrefly                         | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | infer-trace                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | infer-ty                              | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |              |                 |
| django     | infer-union                           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped |            0 |    0 |     0 |              |                 |
| sqlalchemy | released                              |                  | 29,521 passed, 975 skipped                                 |              |      |       |              |                 |
| sqlalchemy | fix-certain                           | True             | as infer-pyrefly's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | fix-likely                            | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | fix-unsafe                            | True             | as infer-pyrefly's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | infer-basedpyright                    | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | infer-pyrefly                         | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | infer-trace                           | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | infer-ty                              | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy | infer-union                           | True             | 4 failed, 29,517 passed, 975 skipped                       |            0 |    0 |     0 |            0 |               0 |
| pydantic   | released (from super-10-26-2026-0545) |                  | 65 failed, 6,900 passed, 350 skipped, 29 xfailed           |              |      |       |              |                 |
| pydantic   | fix-certain                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | fix-likely                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | fix-unsafe                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | infer-basedpyright                    | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | infer-pyrefly                         | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | infer-trace                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | infer-ty                              | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pydantic   | infer-union                           | True             | 65 failed, 6,900 passed, 350 skipped, 29 xfailed           |            0 |    0 |     0 |            0 |               0 |
| pandas     | released (from super-10-26-2026-0545) |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |              |      |       |              |                 |
| pandas     | fix-certain                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | fix-likely                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | fix-unsafe                            | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | infer-basedpyright                    | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | infer-pyrefly                         | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | infer-trace                           | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | infer-ty                              | True             | as infer-union's (implied)                                 |            0 |    0 |     0 |            0 |               0 |
| pandas     | infer-union                           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |            0 |               0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus     | run                | errors | new | gone |                                                      change |
| ---------- | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy | released           |      0 |     |      |                                                             |
| sqlalchemy | fix-certain        |      1 |   1 |    0 |    183 files changed, 2263 insertions(+), 1721 deletions(-) |
| sqlalchemy | fix-likely         |      1 |   1 |    0 |    193 files changed, 2727 insertions(+), 2140 deletions(-) |
| sqlalchemy | fix-unsafe         |      1 |   1 |    0 |    206 files changed, 3453 insertions(+), 2828 deletions(-) |
| sqlalchemy | infer-basedpyright |      9 |   9 |    0 |    210 files changed, 4201 insertions(+), 3530 deletions(-) |
| sqlalchemy | infer-pyrefly      |      7 |   7 |    0 |    209 files changed, 3935 insertions(+), 3152 deletions(-) |
| sqlalchemy | infer-trace        |      7 |   7 |    0 |    208 files changed, 3651 insertions(+), 2965 deletions(-) |
| sqlalchemy | infer-ty           |      5 |   5 |    0 |    208 files changed, 4143 insertions(+), 3373 deletions(-) |
| pydantic   | released           |      0 |     |      |                                                             |
| pydantic   | fix-certain        |      0 |   0 |    0 |     79 files changed, 1953 insertions(+), 1413 deletions(-) |
| pydantic   | fix-likely         |      0 |   0 |    0 |     79 files changed, 1953 insertions(+), 1413 deletions(-) |
| pydantic   | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1953 insertions(+), 1413 deletions(-) |
| pydantic   | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1921 insertions(+), 1497 deletions(-) |
| pydantic   | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1953 insertions(+), 1413 deletions(-) |
| pydantic   | infer-trace        |      0 |   0 |    0 |     79 files changed, 1691 insertions(+), 1280 deletions(-) |
| pydantic   | infer-ty           |      3 |   3 |    0 |     79 files changed, 1827 insertions(+), 1406 deletions(-) |
| pandas     | released           |    259 |     |      |                                                             |
| pandas     | fix-certain        |    261 |   3 |    1 | 1072 files changed, 18457 insertions(+), 15369 deletions(-) |
| pandas     | fix-likely         |    262 |   4 |    1 | 1204 files changed, 43270 insertions(+), 39355 deletions(-) |
| pandas     | fix-unsafe         |    267 |   9 |    1 | 1208 files changed, 44610 insertions(+), 40496 deletions(-) |
| pandas     | infer-basedpyright |    301 |  43 |    1 | 1216 files changed, 50745 insertions(+), 46001 deletions(-) |
| pandas     | infer-pyrefly      |    319 |  61 |    1 | 1217 files changed, 53133 insertions(+), 48067 deletions(-) |
| pandas     | infer-trace        |    267 |   9 |    1 | 1212 files changed, 46133 insertions(+), 41895 deletions(-) |
| pandas     | infer-ty           |    274 |  16 |    1 | 1218 files changed, 50507 insertions(+), 45774 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus           | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ---------------- | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library | check                    |    56.9 |       121.0 |  2.1 |    3.67 |          3 |     4.56 | False |
| standard library | fix-certain              |   155.6 |       338.8 |  2.2 |    4.96 |          3 |     6.07 | False |
| standard library | fix-likely               |   196.5 |       426.1 |  2.2 |    6.84 |          3 |     8.57 | False |
| standard library | fix-unsafe               |   183.9 |       404.0 |  2.2 |    6.78 |          3 |     8.51 | False |
| standard library | infer-basedpyright       |   292.2 |       554.0 |  1.9 |   11.46 |          2 |     5.67 | False |
| standard library | infer-ty                 |   209.2 |       486.6 |  2.3 |    9.37 |          1 |     3.43 | False |
| standard library | infer-pyrefly            |   188.7 |       499.4 |  2.6 |   11.88 |          2 |     7.82 | False |
| standard library | census                   |    37.7 |        33.3 |  0.9 |    0.53 |          3 |     4.56 | False |
| standard library | coverage                 |    12.4 |        42.8 |  3.5 |    0.75 |          4 |     0.94 | False |
| standard library | timing                   |    76.2 |       116.0 |  1.5 |    3.61 |         16 |     4.51 | False |
| django           | check                    |     0.4 |         0.3 |  0.7 |    0.06 |          3 |     1.19 | False |
| django           | fix-certain              |    27.6 |        60.5 |  2.2 |    1.27 |          2 |     1.54 | False |
| django           | fix-likely               |    30.2 |        73.6 |  2.4 |    1.61 |          2 |     2.04 | False |
| django           | fix-unsafe               |    40.2 |        73.5 |  1.8 |    1.53 |          2 |     1.91 | False |
| django           | infer-basedpyright       |    37.0 |        81.9 |  2.2 |    1.76 |          1 |      1.1 | False |
| django           | infer-ty                 |    46.4 |        81.4 |  1.8 |    1.69 |          1 |     1.06 | False |
| django           | infer-pyrefly            |    50.9 |        91.4 |  1.8 |    1.77 |          1 |     1.11 | False |
| django           | census                   |    13.8 |        28.0 |  2.0 |    0.95 |          3 |     1.19 | False |
| django           | coverage                 |     2.0 |         5.4 |  2.7 |    0.33 |          3 |     0.41 | False |
| django           | timing                   |    16.2 |        24.3 |  1.5 |    0.95 |         16 |     1.19 | False |
| django           | traced                   |    87.9 |       568.0 |  6.5 |     7.4 |          8 |     9.19 | False |
| django           | tests-released           |    56.2 |       465.5 |  8.3 |    5.51 |          8 |      6.8 | False |
| django           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     8.56 | False |
| django           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     4.15 | False |
| django           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |         12 |     6.72 | False |
| django           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.04 |         10 |     8.08 | False |
| django           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.04 |          9 |     5.56 | False |
| django           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     7.11 | False |
| django           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.04 |          9 |     8.23 | False |
| django           | infer-union              |    88.7 |       315.9 |  3.6 |    4.15 |          3 |     3.79 | False |
| django           | tests-infer-union        |    49.8 |       446.6 |  9.0 |     5.7 |          9 |     7.83 | False |
| django           | tests                    |     1.6 |         1.3 |  0.8 |    0.15 |          1 |     0.35 | False |
| sqlalchemy       | check                    |     9.4 |        19.1 |  2.0 |    0.87 |          2 |     1.07 | False |
| sqlalchemy       | fix-certain              |    22.4 |        50.4 |  2.2 |    0.99 |          2 |     1.24 | False |
| sqlalchemy       | fix-likely               |    50.2 |        75.6 |  1.5 |    1.31 |          2 |     1.64 | False |
| sqlalchemy       | fix-unsafe               |    41.2 |        68.4 |  1.7 |    1.21 |          2 |     1.56 | False |
| sqlalchemy       | infer-basedpyright       |   102.5 |       269.7 |  2.6 |    5.55 |          2 |     1.61 | False |
| sqlalchemy       | infer-ty                 |    46.0 |        95.9 |  2.1 |     3.2 |          1 |     0.81 | False |
| sqlalchemy       | infer-pyrefly            |    53.6 |       101.6 |  1.9 |    3.53 |          1 |     0.82 | False |
| sqlalchemy       | census                   |     3.8 |         3.5 |  0.9 |    0.09 |          2 |     1.07 | False |
| sqlalchemy       | coverage                 |     2.4 |         7.0 |  2.9 |    0.37 |          3 |     0.45 | False |
| sqlalchemy       | timing                   |    14.8 |        20.2 |  1.4 |    0.87 |         16 |     1.09 | False |
| sqlalchemy       | traced                   |   155.1 |      1231.8 |  7.9 |    6.42 |          9 |     8.42 | False |
| sqlalchemy       | tests-released           |    96.5 |       628.6 |  6.5 |    3.97 |          8 |     4.88 | False |
| sqlalchemy       | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          7 |     8.11 | False |
| sqlalchemy       | tests-fix-likely         |    92.7 |       963.8 | 10.4 |    5.84 |         12 |     7.24 | False |
| sqlalchemy       | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.27 | False |
| sqlalchemy       | tests-infer-basedpyright |    93.7 |       962.9 | 10.3 |    5.78 |         10 |     7.22 | False |
| sqlalchemy       | tests-infer-ty           |   118.3 |      1055.6 |  8.9 |    5.77 |         10 |     7.27 | False |
| sqlalchemy       | tests-infer-pyrefly      |   117.3 |       965.6 |  8.2 |    5.17 |         11 |     6.63 | False |
| sqlalchemy       | tests-infer-trace        |    92.7 |       962.8 | 10.4 |    5.81 |         11 |     7.24 | False |
| sqlalchemy       | infer-union              |   119.1 |       319.7 |  2.7 |    4.71 |          3 |     4.77 | False |
| sqlalchemy       | tests-infer-union        |   112.9 |       767.1 |  6.8 |    4.21 |          8 |     5.24 | False |
| sqlalchemy       | tests                    |     0.8 |         0.7 |  0.9 |    0.15 |          2 |     0.35 | False |
| sqlalchemy       | types-released           |     7.4 |         5.9 |  0.8 |    0.36 |          1 |      0.4 | False |
| sqlalchemy       | types-fix-certain        |    10.4 |         6.7 |  0.6 |    0.33 |          1 |      0.4 | False |
| sqlalchemy       | types-fix-likely         |     3.8 |         3.7 |  1.0 |    0.31 |          1 |      0.4 | False |
| sqlalchemy       | types-fix-unsafe         |     8.2 |         6.9 |  0.8 |    0.31 |          1 |     0.37 | False |
| sqlalchemy       | types-infer-basedpyright |     9.6 |         7.6 |  0.8 |    0.32 |          1 |     0.41 | False |
| sqlalchemy       | types-infer-ty           |    10.8 |         7.2 |  0.7 |    0.35 |          1 |      0.4 | False |
| sqlalchemy       | types-infer-pyrefly      |     9.6 |         7.6 |  0.8 |    0.31 |          1 |      0.4 | False |
| sqlalchemy       | types-infer-trace        |     9.6 |         7.3 |  0.8 |    0.34 |          1 |      0.4 | False |
| sqlalchemy       | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | check                    |     0.6 |         0.2 |  0.3 |    0.04 |          2 |     0.37 | False |
| pydantic         | fix-certain              |     4.8 |        11.6 |  2.4 |     0.4 |          3 |      0.5 | False |
| pydantic         | fix-likely               |     5.0 |        12.7 |  2.5 |    0.49 |          3 |     0.61 | False |
| pydantic         | fix-unsafe               |     7.8 |        14.5 |  1.9 |    0.43 |          2 |      0.7 | False |
| pydantic         | infer-basedpyright       |    10.0 |        16.7 |  1.7 |    0.49 |          1 |     0.31 | False |
| pydantic         | infer-ty                 |     9.4 |        16.1 |  1.7 |    0.49 |          1 |     0.31 | False |
| pydantic         | infer-pyrefly            |    12.8 |        19.1 |  1.5 |     0.6 |          1 |     0.31 | False |
| pydantic         | census                   |     3.8 |         5.4 |  1.4 |    0.31 |          2 |     0.37 | False |
| pydantic         | coverage                 |     1.4 |         2.1 |  1.5 |    0.21 |          2 |     0.26 | False |
| pydantic         | timing                   |     3.0 |         4.1 |  1.4 |    0.31 |         16 |     0.37 | False |
| pydantic         | traced                   |    90.5 |        66.6 |  0.7 |    0.57 |          1 |     0.61 | False |
| pydantic         | tests-released           |    69.1 |        44.1 |  0.6 |    0.29 |          1 |      0.4 | False |
| pydantic         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic         | infer-union              |    15.6 |        21.0 |  1.3 |     0.5 |          1 |     0.31 | False |
| pydantic         | tests-infer-union        |    58.4 |        41.6 |  0.7 |    0.32 |          1 |      0.4 | False |
| pydantic         | tests                    |     1.8 |         1.5 |  0.8 |    0.16 |          1 |     0.35 | False |
| pydantic         | types-released           |    20.8 |        18.8 |  0.9 |    0.59 |          2 |     0.66 | False |
| pydantic         | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          1 |     0.67 | False |
| pydantic         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.67 | False |
| pydantic         | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.67 | False |
| pydantic         | types-infer-basedpyright |    19.2 |        21.2 |  1.1 |    0.54 |          2 |     0.66 | False |
| pydantic         | types-infer-ty           |    12.2 |        17.3 |  1.4 |    0.54 |          2 |     0.66 | False |
| pydantic         | types-infer-pyrefly      |    23.3 |        20.6 |  0.9 |    0.53 |          2 |     0.67 | False |
| pydantic         | types-infer-trace        |    21.2 |        19.8 |  0.9 |    0.54 |          1 |     0.67 | False |
| pydantic         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | check                    |     1.6 |         1.3 |  0.8 |    0.23 |          3 |      4.4 | False |
| pandas           | fix-certain              |   141.3 |       350.2 |  2.5 |    4.25 |          3 |     5.24 | False |
| pandas           | fix-likely               |   165.9 |       482.5 |  2.9 |    6.78 |          3 |     8.36 | False |
| pandas           | fix-unsafe               |   228.0 |       580.6 |  2.5 |    6.75 |          3 |     8.32 | False |
| pandas           | infer-basedpyright       |   416.1 |       927.8 |  2.2 |   11.47 |          2 |     4.97 | False |
| pandas           | infer-ty                 |   232.2 |       674.3 |  2.9 |    9.17 |          1 |     2.58 | False |
| pandas           | infer-pyrefly            |   169.1 |       601.0 |  3.6 |   14.26 |          2 |     5.22 | False |
| pandas           | census                   |    75.5 |       167.8 |  2.2 |    3.58 |          3 |      4.4 | False |
| pandas           | coverage                 |     8.8 |        23.9 |  2.7 |    0.79 |          3 |     0.99 | False |
| pandas           | timing                   |    91.8 |       145.7 |  1.6 |     3.6 |         16 |     4.42 | False |
| pandas           | traced                   |   276.4 |      1394.3 |  5.0 |   15.12 |          7 |    19.16 | False |
| pandas           | tests-released           |   111.0 |       673.0 |  6.1 |   11.49 |          9 |    14.08 | False |
| pandas           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.47 | False |
| pandas           | infer-union              |   423.1 |      1293.7 |  3.1 |   11.57 |          3 |     8.19 | False |
| pandas           | tests-infer-union        |    91.1 |       687.8 |  7.5 |   14.29 |          8 |    17.47 | False |
| pandas           | tests                    |     0.8 |         0.7 |  0.9 |    0.15 |          2 |     0.38 | False |
| pandas           | types-released           |    75.6 |       100.6 |  1.3 |    2.22 |          2 |     2.64 | False |
| pandas           | types-fix-certain        |    63.6 |        95.4 |  1.5 |     2.2 |          2 |     2.92 | False |
| pandas           | types-fix-likely         |    56.8 |        88.7 |  1.6 |    2.31 |          2 |     2.87 | False |
| pandas           | types-fix-unsafe         |    67.2 |        96.2 |  1.4 |    2.25 |          2 |      2.8 | False |
| pandas           | types-infer-basedpyright |    46.0 |        71.5 |  1.6 |    2.27 |          2 |     2.64 | False |
| pandas           | types-infer-ty           |    57.4 |        90.2 |  1.6 |    2.22 |          2 |     2.84 | False |
| pandas           | types-infer-pyrefly      |    82.8 |        98.1 |  1.2 |    2.16 |          2 |     2.76 | False |
| pandas           | types-infer-trace        |    57.7 |        95.0 |  1.6 |    2.21 |          2 |     2.84 | False |
| pandas           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted          | check                    |     6.6 |        16.5 |  2.5 |    0.82 |          3 |     1.01 | False |
| twisted          | fix-certain              |    18.2 |        44.2 |  2.4 |    0.95 |          3 |     1.17 | False |
| twisted          | fix-likely               |    26.4 |        58.1 |  2.2 |    1.27 |          3 |     1.59 | False |
| twisted          | fix-unsafe               |    19.0 |        54.2 |  2.9 |    1.21 |          3 |     1.51 | False |
| twisted          | infer-basedpyright       |    29.8 |        63.7 |  2.1 |    1.34 |          1 |     0.84 | False |
| twisted          | infer-ty                 |    27.5 |        58.9 |  2.1 |     1.3 |          2 |     1.62 | False |
| twisted          | infer-pyrefly            |    32.8 |        62.4 |  1.9 |     1.3 |          1 |     0.81 | False |
| twisted          | census                   |     4.4 |         4.3 |  1.0 |    0.12 |          3 |     1.01 | False |
| twisted          | coverage                 |     2.4 |         6.8 |  2.8 |    0.36 |          3 |     0.45 | False |
| twisted          | timing                   |    11.0 |        16.7 |  1.5 |    0.81 |         16 |     1.01 | False |
| pip              | check                    |     5.0 |        11.3 |  2.3 |    0.57 |          3 |      0.7 | False |
| pip              | fix-certain              |    11.6 |        30.1 |  2.6 |    0.71 |          3 |      0.9 | False |
| pip              | fix-likely               |    14.4 |        36.3 |  2.5 |    0.91 |          3 |     1.14 | False |
| pip              | fix-unsafe               |    16.4 |        36.0 |  2.2 |    0.86 |          3 |     1.07 | False |
| pip              | infer-basedpyright       |    30.8 |        56.6 |  1.8 |    0.98 |          1 |     0.58 | False |
| pip              | infer-ty                 |    21.4 |        45.6 |  2.1 |     0.9 |          1 |     0.56 | False |
| pip              | infer-pyrefly            |    19.0 |        41.2 |  2.2 |    0.92 |          1 |     0.39 | False |
| pip              | census                   |     2.4 |         2.3 |  1.0 |     0.1 |          3 |      0.7 | False |
| pip              | coverage                 |     4.0 |         5.1 |  1.3 |     0.3 |          3 |     0.37 | False |
| pip              | timing                   |     7.4 |        10.9 |  1.5 |    0.56 |         16 |      0.7 | False |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus     | released                                                   | traced                                                     | same failures |
| ---------- | ---------------------------------------------------------- | ---------------------------------------------------------- | ------------- |
| django     | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped | 5 expected failures, 6 failures, 17,585 ran, 1,149 skipped | False         |
| sqlalchemy | 29,521 passed, 975 skipped                                 | 4 failed, 29,517 passed, 975 skipped                       | False         |
| pydantic   | 65 failed, 6,900 passed, 350 skipped, 29 xfailed           | 65 failed, 6,900 passed, 350 skipped, 29 xfailed           | True          |
| pandas     | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    | True          |

- standard library, basic+dev, infer-basedpyright: held 11.46 GB beside other steps
- standard library, basic+dev, infer-basedpyright: basedpyright's hints for 4 of 5 rounds came from
  the store, so its seconds measure less of the checker
- standard library, basic+dev, infer-ty: held 9.37 GB beside other steps
- standard library, basic+dev, infer-ty: ty's hints for 4 of 5 rounds came from the store, so its
  seconds measure less of the checker
- standard library, basic+dev, infer-pyrefly: held 11.88 GB beside other steps
- standard library, basic+dev, infer-pyrefly: pyrefly's hints for 5 of 6 rounds came from the store,
  so its seconds measure less of the checker
- django, basic+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- django, basic+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- django, basic+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, basic+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, basic+dev, infer-union: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, basic+dev, infer-union: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, basic+dev, infer-basedpyright: basedpyright's hints for 3 of 5 rounds came from the
  store, so its seconds measure less of the checker
- sqlalchemy, basic+dev, infer-ty: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, basic+dev, infer-pyrefly: pyrefly's hints for 4 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, basic+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, basic+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, basic+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, basic+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- pydantic, basic+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pydantic, basic+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, basic+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, basic+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, basic+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pandas, basic+dev, infer-basedpyright: held 11.47 GB beside other steps
- pandas, basic+dev, infer-basedpyright: basedpyright's hints for 2 of 5 rounds came from the store,
  so its seconds measure less of the checker
- pandas, basic+dev, infer-ty: held 9.17 GB beside other steps
- pandas, basic+dev, infer-ty: ty's hints for 3 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, basic+dev, infer-pyrefly: held 14.26 GB beside other steps
- pandas, basic+dev, infer-pyrefly: pyrefly's hints for 3 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, basic+dev, traced: held 15.12 GB beside other steps
- pandas, basic+dev, tests-released: held 11.49 GB beside other steps
- pandas, basic+dev, infer-union: held 11.57 GB beside other steps
- pandas, basic+dev, infer-union: basedpyright's hints for 3 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, basic+dev, infer-union: pyrefly's hints for 3 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, basic+dev, infer-union: ty's hints for 3 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, basic+dev, tests-infer-union: held 14.29 GB beside other steps
- twisted, basic+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the
  store, so its seconds measure less of the checker
- twisted, basic+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- twisted, basic+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pip, basic+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store, so
  its seconds measure less of the checker
- pip, basic+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds measure
  less of the checker
- pip, basic+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
