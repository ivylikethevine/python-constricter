# Super corpora

The run `super` (`python -m tests.corpus`) on super: constricter 0.4.4.dev5+g722e868f4.d20261026
(`b5f720c76df8`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 42 minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter | Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ------------------ | -------- | ----------- | ----: | --------------: | ------------: | -------: | -------------: | -----------: | ---------: | --------: | -------: | ------: |
| standard library   | 3.14.7   | super+dev   | 1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |         14 |         8 |        0 | 113,750 |
| django             | 5.2.18   | super+dev   |   883 |           9,926 |         2,166 |        0 |          5,084 |            0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy         | 2.1.4    | super+dev   |   258 |           8,825 |         1,636 |        0 |          2,501 |          572 |        128 |         2 |        1 |  13,665 |
| pydantic           | 2.14.0   | super+dev   |   105 |           2,072 |           440 |        0 |            605 |          184 |         15 |         0 |        0 |   3,316 |
| pandas             | 3.0.6    | super+dev   | 1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |          2 |         1 |        1 |  77,931 |
| twisted            | 12.3.0   | super+dev   |   819 |          13,310 |         1,349 |        0 |          3,215 |            0 |          0 |         0 |        0 |  17,874 |
| pip                | 20.3.4   | super+dev   |   366 |           5,902 |         1,150 |        0 |          1,872 |            0 |          0 |         0 |        0 |   8,924 |
| structlog          | 26.1.0   | super+dev   |    21 |             156 |            47 |        0 |            113 |           12 |          1 |         0 |        0 |     329 |
| attrs              | 26.1.0   | super+dev   |    13 |             285 |            50 |        0 |             58 |            2 |          0 |         1 |        0 |     396 |
| click              | 8.5.0    | super+dev   |    17 |             481 |            58 |        0 |             69 |           28 |          1 |         0 |        0 |     637 |
| hypercorn          | 0.18.0   | super+dev   |    39 |             220 |            67 |        0 |             68 |            8 |          0 |         0 |        0 |     363 |
| starlette          | 1.7.0    | super+dev   |    36 |             499 |            99 |        0 |            146 |           18 |          0 |         0 |        0 |     762 |
| werkzeug           | 3.1.9    | super+dev   |    52 |             835 |           235 |        0 |            223 |           15 |          1 |         0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | super+dev   |    61 |           1,674 |           198 |        0 |            460 |            8 |          0 |         0 |        0 |   2,340 |
| httpx              | 0.28.1   | super+dev   |    23 |             395 |           112 |        0 |             62 |            1 |          0 |         0 |        0 |     570 |
| black              | 26.10.0  | super+dev   |    25 |             996 |           232 |        0 |             45 |            5 |          4 |         0 |        0 |   1,282 |
| fastapi            | 0.142.2  | super+dev   |    52 |             586 |           105 |        0 |             51 |           98 |          5 |         0 |        0 |     845 |
| cattrs             | 26.2.1   | super+dev   |    36 |             420 |            70 |        0 |             30 |            9 |          1 |         0 |        0 |     530 |
| pytest             | 9.1.1    | super+dev   |    78 |           2,363 |           470 |        0 |            170 |           33 |          9 |         0 |        0 |   3,045 |
| botocore           | 1.43.108 | super+dev   |    76 |           2,825 |           367 |        0 |            594 |            2 |          0 |         0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | super+dev   |    45 |             363 |            71 |        0 |             55 |           11 |          4 |         0 |        0 |     504 |
| mcp                | 2.3.0    | super+dev   |   124 |           1,356 |           173 |        0 |            191 |          105 |          8 |         0 |        0 |   1,833 |
| textual            | 8.2.8    | super+dev   |   247 |           4,979 |           718 |        0 |            786 |           31 |         26 |         0 |        0 |   6,540 |
| pdm                | 2.29.2   | super+dev   |   128 |           2,114 |           417 |        0 |            187 |           37 |          2 |         0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | super+dev   |   244 |           1,436 |           243 |        0 |            127 |          137 |          2 |         0 |        0 |   1,945 |
| pygments           | 2.21.0   | super+dev   |   343 |           1,124 |           539 |        0 |          6,003 |            0 |          0 |         0 |        0 |   7,666 |
| streamlink         | 8.6.1    | super+dev   |   227 |           2,080 |           310 |        0 |            639 |           37 |         11 |         0 |        0 |   3,077 |
| sphinx             | 9.1.0    | super+dev   |   243 |           5,505 |         1,336 |        1 |          1,131 |           73 |         29 |         5 |        3 |   8,083 |
| tox                | 4.64.9   | super+dev   |   129 |           1,369 |           286 |        0 |            107 |           18 |          5 |         0 |        0 |   1,785 |
| **Total**          |          | super+dev   | 7,977 | 234,028 (77.2%) | 28,056 (9.3%) | 1 (0.0%) | 39,012 (12.9%) | 1,635 (0.5%) | 268 (0.1%) | 18 (0.0%) | 5 (0.0%) | 303,023 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | super+dev   | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,446 (32.9%) |   6,681 (5.9%) | 13,082 (11.5%) |      0 |    0 |            0 |
| django             | super+dev   |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,622 (15.3%) |     646 (3.8%) |  2,786 (16.2%) |      0 |    0 |            0 |
| sqlalchemy         | super+dev   |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |  1,938 (14.2%) |     350 (2.6%) |     847 (6.2%) |      0 |    0 |            0 |
| pydantic           | super+dev   |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,191 (35.9%) |     146 (4.4%) |    405 (12.2%) |      0 |    0 |            0 |
| pandas             | super+dev   |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,956 (21.8%) | 23,589 (30.3%) | 24,628 (31.6%) |      0 |    0 |            0 |
| twisted            | super+dev   |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,435 (13.6%) |  3,625 (20.3%) |  4,697 (26.3%) |      0 |    0 |            0 |
| pip                | super+dev   |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,270 (25.4%) |     468 (5.2%) |  1,304 (14.6%) |      0 |    0 |            0 |
| structlog          | super+dev   |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |     98 (29.8%) |      15 (4.6%) |      28 (8.5%) |      0 |    0 |            0 |
| attrs              | super+dev   |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |     93 (23.5%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | super+dev   |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |    302 (47.4%) |      27 (4.2%) |      63 (9.9%) |      0 |    0 |            0 |
| hypercorn          | super+dev   |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |    134 (36.9%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | super+dev   |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |    314 (41.2%) |      57 (7.5%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | super+dev   |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |    527 (40.3%) |      66 (5.0%) |     127 (9.7%) |      0 |    0 |            0 |
| mkdocs             | super+dev   |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |    810 (34.6%) |    377 (16.1%) |    482 (20.6%) |      0 |    0 |            0 |
| httpx              | super+dev   |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |    234 (41.1%) |     57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| black              | super+dev   |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |    707 (55.1%) |     127 (9.9%) |    163 (12.7%) |      0 |    0 |            0 |
| fastapi            | super+dev   |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |    257 (30.4%) |      40 (4.7%) |      65 (7.7%) |      0 |    0 |            0 |
| cattrs             | super+dev   |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |    105 (19.8%) |      34 (6.4%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | super+dev   |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |  1,358 (44.6%) |     156 (5.1%) |     285 (9.4%) |      0 |    0 |            0 |
| botocore           | super+dev   |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |    543 (14.3%) |     174 (4.6%) |    608 (16.1%) |      0 |    0 |            0 |
| uvicorn            | super+dev   |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |    231 (45.8%) |      32 (6.3%) |      47 (9.3%) |      0 |    0 |            0 |
| mcp                | super+dev   |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |    694 (37.9%) |     154 (8.4%) |    236 (12.9%) |      0 |    0 |            0 |
| textual            | super+dev   |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |  2,707 (41.4%) |     482 (7.4%) |    741 (11.3%) |      0 |    0 |            0 |
| pdm                | super+dev   |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |  1,147 (41.6%) |     201 (7.3%) |    323 (11.7%) |      0 |    0 |            0 |
| strawberry-graphql | super+dev   |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |    611 (31.4%) |     167 (8.6%) |    218 (11.2%) |      0 |    0 |            0 |
| pygments           | super+dev   |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |     735 (9.6%) |      79 (1.0%) |     228 (3.0%) |      0 |    0 |            0 |
| streamlink         | super+dev   |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |    682 (22.2%) |     111 (3.6%) |     250 (8.1%) |      0 |    0 |            0 |
| sphinx             | super+dev   |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |  3,231 (40.0%) |     521 (6.4%) |    900 (11.1%) |      0 |    0 |            0 |
| tox                | super+dev   |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |    943 (52.8%) |      82 (4.6%) |     138 (7.7%) |      0 |    0 |            0 |
| **Total**          | super+dev   | 0 / 301,115 | 273,040 / 29,983 | 301,114 / 1,909 | 303,023 / 0 | 81,321 (26.8%) | 38,493 (12.7%) | 52,936 (17.5%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | super+dev   |              1.2% |         33.7% |            39.5% |                  45.1% | +32.6 pts, 32.9% of untyped | +43.9 pts, 44.5% of untyped |
| django             | super+dev   |              0.0% |         15.3% |            19.1% |                  31.5% | +15.3 pts, 15.3% of untyped | +31.5 pts, 31.5% of untyped |
| sqlalchemy         | super+dev   |             15.3% |         27.9% |            30.2% |                  33.5% | +12.7 pts, 14.9% of untyped | +18.2 pts, 21.5% of untyped |
| pydantic           | super+dev   |             22.4% |         52.1% |            55.7% |                  62.2% | +29.6 pts, 38.2% of untyped | +39.7 pts, 51.2% of untyped |
| pandas             | super+dev   |              1.6% |         23.1% |            52.9% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.5% of untyped |
| twisted            | super+dev   |              0.0% |         13.6% |            33.9% |                  39.9% | +13.6 pts, 13.6% of untyped | +39.9 pts, 39.9% of untyped |
| pip                | super+dev   |              1.5% |         26.6% |            31.7% |                  40.9% | +25.0 pts, 25.4% of untyped | +39.4 pts, 40.0% of untyped |
| structlog          | super+dev   |             25.6% |         48.7% |            52.2% |                  55.3% | +23.1 pts, 31.0% of untyped | +29.6 pts, 39.9% of untyped |
| attrs              | super+dev   |              0.8% |         24.2% |            26.5% |                  27.0% | +23.5 pts, 23.7% of untyped | +26.3 pts, 26.5% of untyped |
| click              | super+dev   |             31.5% |         65.5% |            68.5% |                  72.6% | +34.0 pts, 49.7% of untyped | +41.1 pts, 60.0% of untyped |
| hypercorn          | super+dev   |             32.4% |         57.9% |            61.7% |                  69.0% | +25.5 pts, 37.7% of untyped | +36.6 pts, 54.1% of untyped |
| starlette          | super+dev   |             10.3% |         48.1% |            55.0% |                  59.8% | +37.9 pts, 42.2% of untyped | +49.6 pts, 55.2% of untyped |
| werkzeug           | super+dev   |             14.3% |         49.2% |            53.6% |                  57.7% | +34.9 pts, 40.8% of untyped | +43.3 pts, 50.6% of untyped |
| mkdocs             | super+dev   |              4.5% |         37.7% |            53.1% |                  57.4% | +33.2 pts, 34.7% of untyped | +52.9 pts, 55.4% of untyped |
| httpx              | super+dev   |              6.3% |         44.8% |            54.2% |                  56.8% | +38.6 pts, 41.1% of untyped | +50.6 pts, 54.0% of untyped |
| black              | super+dev   |             15.9% |         62.6% |            71.0% |                  73.4% | +46.7 pts, 55.5% of untyped | +57.5 pts, 68.3% of untyped |
| fastapi            | super+dev   |             42.0% |         62.1% |            65.2% |                  67.2% | +20.1 pts, 34.6% of untyped | +25.2 pts, 43.4% of untyped |
| cattrs             | super+dev   |              7.0% |         25.8% |            31.8% |                  34.0% | +18.8 pts, 20.2% of untyped | +27.0 pts, 29.0% of untyped |
| pytest             | super+dev   |             12.1% |         51.9% |            56.4% |                  60.2% | +39.7 pts, 45.2% of untyped | +48.1 pts, 54.7% of untyped |
| botocore           | super+dev   |              0.5% |         14.7% |            19.3% |                  30.7% | +14.3 pts, 14.3% of untyped | +30.2 pts, 30.4% of untyped |
| uvicorn            | super+dev   |             23.6% |         59.7% |            64.7% |                  67.0% | +36.1 pts, 47.2% of untyped | +43.4 pts, 56.9% of untyped |
| mcp                | super+dev   |             30.7% |         58.7% |            64.9% |                  68.2% | +28.0 pts, 40.3% of untyped | +37.5 pts, 54.1% of untyped |
| textual            | super+dev   |             15.6% |         50.8% |            57.1% |                  60.5% | +35.3 pts, 41.8% of untyped | +44.9 pts, 53.2% of untyped |
| pdm                | super+dev   |             11.7% |         49.0% |            55.5% |                  59.5% | +37.3 pts, 42.2% of untyped | +47.7 pts, 54.1% of untyped |
| strawberry-graphql | super+dev   |             30.1% |         53.7% |            60.2% |                  62.2% | +23.7 pts, 33.8% of untyped | +32.1 pts, 45.9% of untyped |
| pygments           | super+dev   |              0.0% |          9.6% |            10.6% |                  12.6% |   +9.6 pts, 9.6% of untyped | +12.6 pts, 12.6% of untyped |
| streamlink         | super+dev   |             42.8% |         55.6% |            57.7% |                  60.4% | +12.9 pts, 22.5% of untyped | +17.6 pts, 30.8% of untyped |
| sphinx             | super+dev   |             10.4% |         46.7% |            52.6% |                  56.8% | +36.3 pts, 40.5% of untyped | +46.4 pts, 51.8% of untyped |
| tox                | super+dev   |             16.0% |         61.0% |            64.9% |                  67.5% | +44.9 pts, 53.5% of untyped | +51.5 pts, 61.4% of untyped |
| **Total**          | super+dev   |              4.7% |         30.5% |            42.6% |                  47.2% | +25.7 pts, 27.0% of untyped | +42.5 pts, 44.6% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,446 |  37,446 |        |        |      0 |    0 | 38,775 |  115,001 |    59.3 |
| standard library   | likely             | 44,127 |  37,689 |  6,438 |        |      0 |    0 | 45,456 |  115,001 |    92.5 |
| standard library   | unsafe             | 50,528 |  37,453 |  6,426 |  6,649 |      0 |    0 | 51,857 |  115,001 |    81.9 |
| standard library   | infer-basedpyright | 58,562 |  37,458 |  6,912 | 14,192 |      0 |   10 | 59,891 |  115,001 |   805.6 |
| standard library   | infer-ty           | 56,302 |  37,458 |  6,863 | 11,981 |      0 |   11 | 57,631 |  115,001 |   117.2 |
| standard library   | infer-pyrefly      | 58,667 |  37,452 |  6,941 | 14,274 |      0 |   42 | 59,996 |  115,001 |   192.9 |
| django             | certain            |  2,622 |   2,622 |        |        |      0 |    0 |  2,627 |   17,181 |    11.5 |
| django             | likely             |  3,268 |   2,628 |    640 |        |      0 |    0 |  3,273 |   17,181 |    28.2 |
| django             | unsafe             |  5,408 |   2,622 |    639 |  2,147 |      0 |    0 |  5,413 |   17,181 |    13.8 |
| django             | infer-basedpyright |  5,808 |   2,616 |    652 |  2,540 |      0 |    0 |  5,813 |   17,181 |    87.5 |
| django             | infer-ty           |  5,618 |   2,623 |    648 |  2,347 |      0 |    0 |  5,623 |   17,181 |    32.2 |
| django             | infer-pyrefly      |  6,074 |   2,611 |    658 |  2,805 |      0 |    4 |  6,079 |   17,181 |    43.1 |
| django             | infer-trace        |  5,954 |   2,622 |    669 |  2,663 |      0 |    0 |  5,959 |   17,181 |    11.0 |
| sqlalchemy         | certain            |  1,938 |   1,938 |        |        |      0 |    0 |  4,273 |   15,304 |    11.9 |
| sqlalchemy         | likely             |  2,288 |   1,946 |    342 |        |      0 |    0 |  4,623 |   15,304 |    15.8 |
| sqlalchemy         | unsafe             |  2,785 |   1,938 |    342 |    505 |      0 |    0 |  5,120 |   15,304 |    14.1 |
| sqlalchemy         | infer-basedpyright |  3,547 |   1,930 |    384 |  1,233 |      0 |    0 |  5,882 |   15,304 |   107.2 |
| sqlalchemy         | infer-ty           |  3,501 |   1,930 |    370 |  1,201 |      0 |    0 |  5,836 |   15,304 |    34.2 |
| sqlalchemy         | infer-pyrefly      |  3,253 |   1,929 |    360 |    964 |      0 |    0 |  5,588 |   15,304 |    30.3 |
| sqlalchemy         | infer-trace        |  2,926 |   1,938 |    342 |    646 |      0 |    0 |  5,261 |   15,304 |    11.1 |
| pydantic           | certain            |  1,191 |   1,191 |        |        |      0 |    0 |  2,093 |    4,019 |     5.0 |
| pydantic           | likely             |  1,337 |   1,198 |    139 |        |      0 |    0 |  2,239 |    4,019 |     3.3 |
| pydantic           | unsafe             |  1,596 |   1,191 |    138 |    267 |      0 |    0 |  2,498 |    4,019 |     3.2 |
| pydantic           | infer-basedpyright |  1,819 |   1,192 |    141 |    486 |      0 |    0 |  2,721 |    4,019 |    53.2 |
| pydantic           | infer-ty           |  1,734 |   1,191 |    137 |    406 |      0 |    0 |  2,636 |    4,019 |    10.3 |
| pydantic           | infer-pyrefly      |  1,798 |   1,191 |    138 |    469 |      0 |    0 |  2,700 |    4,019 |    12.8 |
| pydantic           | infer-trace        |  1,597 |   1,191 |    138 |    268 |      0 |    0 |  2,499 |    4,019 |     5.5 |
| pandas             | certain            | 16,956 |  16,956 |        |        |      0 |    0 | 18,225 |   79,062 |    39.8 |
| pandas             | likely             | 40,545 |  17,146 | 23,399 |        |      0 |    0 | 41,814 |   79,062 |   112.4 |
| pandas             | unsafe             | 41,584 |  16,952 | 23,385 |  1,247 |      0 |    0 | 42,853 |   79,062 |   169.4 |
| pandas             | infer-basedpyright | 47,039 |  16,942 | 23,381 |  6,716 |      0 |    3 | 48,308 |   79,062 |   559.1 |
| pandas             | infer-ty           | 46,959 |  16,950 | 23,381 |  6,628 |      0 |    3 | 48,228 |   79,062 |   214.8 |
| pandas             | infer-pyrefly      | 48,159 |  16,950 | 23,387 |  7,822 |      0 |    9 | 49,428 |   79,062 |   150.8 |
| pandas             | infer-trace        | 42,868 |  16,952 | 23,249 |  2,667 |      0 |    0 | 44,137 |   79,062 |    96.1 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     6.0 |
| twisted            | likely             |  6,060 |   2,558 |  3,502 |        |      0 |    0 |  6,060 |   17,874 |     9.6 |
| twisted            | unsafe             |  7,132 |   2,434 |  3,502 |  1,196 |      0 |    0 |  7,132 |   17,874 |    11.8 |
| twisted            | infer-basedpyright |  8,548 |   2,435 |  3,532 |  2,581 |      0 |    0 |  8,548 |   17,874 |   179.9 |
| twisted            | infer-ty           |  7,538 |   2,434 |  3,526 |  1,578 |      0 |    0 |  7,538 |   17,874 |    29.9 |
| twisted            | infer-pyrefly      |  7,547 |   2,434 |  3,516 |  1,597 |      0 |    0 |  7,547 |   17,874 |    30.0 |
| pip                | certain            |  2,270 |   2,270 |        |        |      0 |    0 |  2,407 |    9,064 |     6.1 |
| pip                | likely             |  2,738 |   2,283 |    455 |        |      0 |    0 |  2,875 |    9,064 |     7.6 |
| pip                | unsafe             |  3,574 |   2,270 |    454 |    850 |      0 |    0 |  3,711 |    9,064 |    11.4 |
| pip                | infer-basedpyright |  4,293 |   2,271 |    498 |  1,524 |      0 |    3 |  4,430 |    9,064 |    72.5 |
| pip                | infer-ty           |  3,862 |   2,271 |    472 |  1,119 |      0 |    5 |  3,999 |    9,064 |    21.9 |
| pip                | infer-pyrefly      |  4,077 |   2,271 |    483 |  1,323 |      0 |    0 |  4,214 |    9,064 |    19.8 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.6 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.8 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     1.1 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     4.5 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     0.9 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     2.4 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     1.8 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.9 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     1.0 |
| attrs              | unsafe             |    104 |      93 |      8 |      3 |      0 |    0 |    107 |      396 |     1.1 |
| attrs              | infer-basedpyright |    130 |      93 |      8 |     29 |      0 |    0 |    133 |      396 |     7.8 |
| attrs              | infer-ty           |    115 |      93 |      8 |     14 |      0 |    0 |    118 |      396 |     2.6 |
| attrs              | infer-pyrefly      |    120 |      93 |      8 |     19 |      0 |    0 |    123 |      396 |     3.0 |
| attrs              | infer-trace        |    107 |      93 |      9 |      5 |      0 |    0 |    110 |      396 |     1.0 |
| click              | certain            |    302 |     302 |        |        |      0 |    0 |    581 |      887 |     0.6 |
| click              | likely             |    329 |     303 |     26 |        |      0 |    0 |    608 |      887 |     0.8 |
| click              | unsafe             |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     1.8 |
| click              | infer-basedpyright |    435 |     302 |     29 |    104 |      0 |    0 |    714 |      887 |    11.5 |
| click              | infer-ty           |    453 |     302 |     26 |    125 |      0 |    0 |    732 |      887 |     1.0 |
| click              | infer-pyrefly      |    442 |     302 |     31 |    109 |      0 |    0 |    721 |      887 |     1.5 |
| click              | infer-trace        |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     2.4 |
| hypercorn          | certain            |    134 |     134 |        |        |      0 |    0 |    304 |      525 |     0.8 |
| hypercorn          | likely             |    154 |     134 |     20 |        |      0 |    0 |    324 |      525 |     0.8 |
| hypercorn          | unsafe             |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     1.3 |
| hypercorn          | infer-basedpyright |    214 |     134 |     21 |     59 |      0 |    0 |    384 |      525 |     4.9 |
| hypercorn          | infer-ty           |    219 |     134 |     21 |     64 |      0 |    0 |    389 |      525 |     1.8 |
| hypercorn          | infer-pyrefly      |    201 |     134 |     20 |     47 |      0 |    0 |    371 |      525 |     1.7 |
| hypercorn          | infer-trace        |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     1.9 |
| starlette          | certain            |    314 |     314 |        |        |      0 |    0 |    399 |      829 |     0.5 |
| starlette          | likely             |    371 |     314 |     57 |        |      0 |    0 |    456 |      829 |     0.9 |
| starlette          | unsafe             |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     1.6 |
| starlette          | infer-basedpyright |    485 |     314 |     57 |    114 |      0 |    0 |    570 |      829 |     6.3 |
| starlette          | infer-ty           |    469 |     314 |     56 |     99 |      0 |    0 |    554 |      829 |     3.6 |
| starlette          | infer-pyrefly      |    447 |     314 |     56 |     77 |      0 |    0 |    532 |      829 |     2.8 |
| starlette          | infer-trace        |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     2.1 |
| werkzeug           | certain            |    527 |     527 |        |        |      0 |    0 |    743 |    1,509 |     0.8 |
| werkzeug           | likely             |    593 |     528 |     65 |        |      0 |    0 |    809 |    1,509 |     1.7 |
| werkzeug           | unsafe             |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     3.3 |
| werkzeug           | infer-basedpyright |    776 |     527 |     78 |    171 |      0 |    0 |    992 |    1,509 |     9.6 |
| werkzeug           | infer-ty           |    803 |     527 |     81 |    195 |      0 |    0 |  1,019 |    1,509 |     3.2 |
| werkzeug           | infer-pyrefly      |    806 |     528 |     70 |    208 |      0 |    0 |  1,022 |    1,509 |     3.3 |
| werkzeug           | infer-trace        |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     3.4 |
| mkdocs             | certain            |    810 |     810 |        |        |      0 |    0 |    921 |    2,443 |     0.8 |
| mkdocs             | likely             |  1,187 |     840 |    347 |        |      0 |    0 |  1,298 |    2,443 |     1.6 |
| mkdocs             | unsafe             |  1,292 |     810 |    347 |    135 |      0 |    0 |  1,403 |    2,443 |     3.1 |
| mkdocs             | infer-basedpyright |  1,385 |     810 |    354 |    221 |      0 |    0 |  1,496 |    2,443 |    15.7 |
| mkdocs             | infer-ty           |  1,418 |     810 |    359 |    249 |      0 |    0 |  1,529 |    2,443 |     3.3 |
| mkdocs             | infer-pyrefly      |  1,385 |     810 |    355 |    220 |      0 |    0 |  1,496 |    2,443 |     5.3 |
| mkdocs             | infer-trace        |  1,304 |     811 |    347 |    146 |      0 |    0 |  1,415 |    2,443 |     1.8 |
| httpx              | certain            |    234 |     234 |        |        |      0 |    0 |    272 |      607 |     0.7 |
| httpx              | likely             |    291 |     243 |     48 |        |      0 |    0 |    329 |      607 |     1.0 |
| httpx              | unsafe             |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     1.9 |
| httpx              | infer-basedpyright |    392 |     234 |     53 |    105 |      0 |    0 |    430 |      607 |    10.3 |
| httpx              | infer-ty           |    376 |     235 |     52 |     89 |      0 |    0 |    414 |      607 |     3.5 |
| httpx              | infer-pyrefly      |    353 |     234 |     51 |     68 |      0 |    0 |    391 |      607 |     3.0 |
| httpx              | infer-trace        |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     2.4 |
| black              | certain            |    707 |     707 |        |        |      0 |    0 |    947 |    1,513 |     1.0 |
| black              | likely             |    834 |     720 |    114 |        |      0 |    0 |  1,074 |    1,513 |     2.0 |
| black              | unsafe             |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     0.9 |
| black              | infer-basedpyright |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     9.3 |
| black              | infer-ty           |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     1.5 |
| black              | infer-pyrefly      |    914 |     707 |    112 |     95 |      0 |    0 |  1,154 |    1,513 |     1.3 |
| black              | infer-trace        |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     1.1 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     1.7 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |    11.5 |
| fastapi            | unsafe             |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     2.0 |
| fastapi            | infer-basedpyright |    348 |     257 |     33 |     58 |      0 |    0 |    885 |    1,279 |    13.1 |
| fastapi            | infer-ty           |    371 |     257 |     32 |     82 |      0 |    0 |    908 |    1,279 |     5.7 |
| fastapi            | infer-pyrefly      |    345 |     257 |     34 |     54 |      0 |    0 |    882 |    1,279 |     6.5 |
| fastapi            | infer-trace        |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     1.3 |
| cattrs             | certain            |    105 |     105 |        |        |      0 |    0 |    144 |      559 |     0.7 |
| cattrs             | likely             |    139 |     112 |     27 |        |      0 |    0 |    178 |      559 |     0.7 |
| cattrs             | unsafe             |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     1.5 |
| cattrs             | infer-basedpyright |    194 |     107 |     29 |     58 |      0 |    0 |    233 |      559 |    10.7 |
| cattrs             | infer-ty           |    195 |     105 |     27 |     63 |      0 |    0 |    234 |      559 |     3.5 |
| cattrs             | infer-pyrefly      |    182 |     105 |     28 |     49 |      0 |    0 |    221 |      559 |     3.3 |
| cattrs             | infer-trace        |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     1.2 |
| pytest             | certain            |  1,358 |   1,358 |        |        |      0 |    0 |  1,773 |    3,418 |     2.5 |
| pytest             | likely             |  1,514 |   1,362 |    152 |        |      0 |    0 |  1,929 |    3,418 |     3.6 |
| pytest             | unsafe             |  1,643 |   1,358 |    152 |    133 |      0 |    0 |  2,058 |    3,418 |     4.3 |
| pytest             | infer-basedpyright |  1,988 |   1,355 |    172 |    461 |      0 |    0 |  2,403 |    3,418 |    25.8 |
| pytest             | infer-ty           |  1,996 |   1,355 |    174 |    467 |      0 |    0 |  2,411 |    3,418 |     7.5 |
| pytest             | infer-pyrefly      |  2,059 |   1,355 |    174 |    530 |      0 |    0 |  2,474 |    3,418 |    12.6 |
| pytest             | infer-trace        |  1,660 |   1,358 |    152 |    150 |      0 |    0 |  2,075 |    3,418 |     2.3 |
| botocore           | certain            |    543 |     543 |        |        |      0 |    0 |    561 |    3,806 |     3.5 |
| botocore           | likely             |    717 |     549 |    168 |        |      0 |    0 |    735 |    3,806 |     3.8 |
| botocore           | unsafe             |  1,151 |     541 |    168 |    442 |      0 |    0 |  1,169 |    3,806 |     4.7 |
| botocore           | infer-basedpyright |  1,296 |     536 |    171 |    589 |      0 |    0 |  1,314 |    3,806 |    31.5 |
| botocore           | infer-ty           |  1,207 |     541 |    169 |    497 |      0 |    0 |  1,225 |    3,806 |    10.9 |
| botocore           | infer-pyrefly      |  1,282 |     537 |    171 |    574 |      0 |    0 |  1,300 |    3,806 |    10.3 |
| botocore           | infer-trace        |  1,496 |     541 |    193 |    762 |      0 |    0 |  1,514 |    3,806 |     4.0 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     0.5 |
| uvicorn            | likely             |    263 |     231 |     32 |        |      0 |    0 |    414 |      640 |     0.9 |
| uvicorn            | unsafe             |    278 |     231 |     32 |     15 |      0 |    0 |    429 |      640 |     1.2 |
| uvicorn            | infer-basedpyright |    346 |     231 |     35 |     80 |      0 |    0 |    497 |      640 |     9.5 |
| uvicorn            | infer-ty           |    325 |     231 |     32 |     62 |      0 |    0 |    476 |      640 |     4.0 |
| uvicorn            | infer-pyrefly      |    303 |     231 |     35 |     37 |      0 |    0 |    454 |      640 |     2.3 |
| uvicorn            | infer-trace        |    278 |     231 |     32 |     15 |      0 |    0 |    429 |      640 |     3.4 |
| mcp                | certain            |    694 |     694 |        |        |      0 |    0 |  1,457 |    2,483 |     1.4 |
| mcp                | likely             |    848 |     700 |    148 |        |      0 |    0 |  1,611 |    2,483 |     2.8 |
| mcp                | unsafe             |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     4.8 |
| mcp                | infer-basedpyright |  1,048 |     694 |    159 |    195 |      0 |    0 |  1,811 |    2,483 |    15.1 |
| mcp                | infer-ty           |  1,039 |     694 |    156 |    189 |      0 |    0 |  1,802 |    2,483 |     6.2 |
| mcp                | infer-pyrefly      |  1,016 |     694 |    152 |    170 |      0 |    0 |  1,779 |    2,483 |     8.1 |
| mcp                | infer-trace        |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     2.4 |
| textual            | certain            |  2,707 |   2,707 |        |        |      0 |    0 |  3,901 |    7,677 |     1.9 |
| textual            | likely             |  3,189 |   2,731 |    458 |        |      0 |    0 |  4,383 |    7,677 |     3.4 |
| textual            | unsafe             |  3,448 |   2,707 |    457 |    284 |      0 |    0 |  4,642 |    7,677 |     3.3 |
| textual            | infer-basedpyright |  4,634 |   2,707 |    525 |  1,402 |      0 |   14 |  5,828 |    7,677 |    25.8 |
| textual            | infer-ty           |  4,726 |   2,707 |    531 |  1,488 |      0 |    0 |  5,920 |    7,677 |     7.2 |
| textual            | infer-pyrefly      |  3,850 |   2,707 |    474 |    669 |      0 |    0 |  5,044 |    7,677 |     5.6 |
| pdm                | certain            |  1,147 |   1,147 |        |        |      0 |    0 |  1,508 |    3,079 |     1.7 |
| pdm                | likely             |  1,348 |   1,160 |    188 |        |      0 |    0 |  1,709 |    3,079 |     3.0 |
| pdm                | unsafe             |  1,470 |   1,147 |    187 |    136 |      0 |    0 |  1,831 |    3,079 |     5.8 |
| pdm                | infer-basedpyright |  1,853 |   1,150 |    216 |    487 |      0 |    0 |  2,214 |    3,079 |    21.5 |
| pdm                | infer-ty           |  1,845 |   1,150 |    216 |    479 |      0 |    0 |  2,206 |    3,079 |     7.8 |
| pdm                | infer-pyrefly      |  1,629 |   1,148 |    197 |    284 |      0 |    0 |  1,990 |    3,079 |    13.1 |
| pdm                | infer-trace        |  1,470 |   1,147 |    187 |    136 |      0 |    0 |  1,831 |    3,079 |     3.1 |
| strawberry-graphql | certain            |    611 |     611 |        |        |      0 |    0 |  1,387 |    2,582 |     2.2 |
| strawberry-graphql | likely             |    778 |     613 |    165 |        |      0 |    0 |  1,554 |    2,582 |     2.4 |
| strawberry-graphql | unsafe             |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     3.4 |
| strawberry-graphql | infer-basedpyright |    989 |     610 |    166 |    213 |      0 |    0 |  1,765 |    2,582 |    24.8 |
| strawberry-graphql | infer-ty           |    986 |     610 |    165 |    211 |      0 |    0 |  1,762 |    2,582 |    14.7 |
| strawberry-graphql | infer-pyrefly      |    885 |     610 |    166 |    109 |      0 |    0 |  1,661 |    2,582 |    10.8 |
| strawberry-graphql | infer-trace        |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     2.7 |
| pygments           | certain            |    735 |     735 |        |        |      0 |    0 |    735 |    7,666 |     3.8 |
| pygments           | likely             |    814 |     738 |     76 |        |      0 |    0 |    814 |    7,666 |     2.8 |
| pygments           | unsafe             |    963 |     735 |     76 |    152 |      0 |    0 |    963 |    7,666 |     3.4 |
| pygments           | infer-basedpyright |  1,076 |     735 |     83 |    258 |      0 |    0 |  1,076 |    7,666 |    37.7 |
| pygments           | infer-ty           |  1,077 |     735 |     84 |    258 |      0 |    0 |  1,077 |    7,666 |    11.0 |
| pygments           | infer-pyrefly      |  1,137 |     735 |     84 |    318 |      0 |    2 |  1,137 |    7,666 |    13.1 |
| pygments           | infer-trace        |  1,082 |     730 |    102 |    250 |      0 |    0 |  1,082 |    7,666 |     7.1 |
| streamlink         | certain            |    682 |     682 |        |        |      0 |    0 |  2,944 |    5,291 |     2.5 |
| streamlink         | likely             |    793 |     685 |    108 |        |      0 |    0 |  3,055 |    5,291 |     5.0 |
| streamlink         | unsafe             |    932 |     682 |    108 |    142 |      0 |    0 |  3,194 |    5,291 |     8.4 |
| streamlink         | infer-basedpyright |  1,318 |     683 |    125 |    510 |      0 |    0 |  3,580 |    5,291 |    16.5 |
| streamlink         | infer-ty           |  1,475 |     682 |    136 |    657 |      0 |    0 |  3,737 |    5,291 |    12.0 |
| streamlink         | infer-pyrefly      |  1,121 |     682 |    120 |    319 |      0 |    0 |  3,383 |    5,291 |     8.6 |
| streamlink         | infer-trace        |    940 |     682 |    108 |    150 |      0 |    0 |  3,202 |    5,291 |     6.2 |
| sphinx             | certain            |  3,231 |   3,231 |        |        |      0 |    0 |  4,159 |    8,901 |     3.9 |
| sphinx             | likely             |  3,752 |   3,246 |    506 |        |      0 |    0 |  4,680 |    8,901 |    11.1 |
| sphinx             | unsafe             |  4,131 |   3,231 |    505 |    395 |      0 |    0 |  5,059 |    8,901 |    10.0 |
| sphinx             | infer-basedpyright |  4,935 |   3,232 |    536 |  1,167 |      0 |    0 |  5,863 |    8,901 |    50.9 |
| sphinx             | infer-ty           |  4,992 |   3,231 |    530 |  1,231 |      0 |    0 |  5,920 |    8,901 |    17.1 |
| sphinx             | infer-pyrefly      |  5,204 |   3,232 |    540 |  1,432 |      0 |    0 |  6,132 |    8,901 |    14.8 |
| sphinx             | infer-trace        |  4,131 |   3,231 |    505 |    395 |      0 |    0 |  5,059 |    8,901 |     6.7 |
| tox                | certain            |    943 |     943 |        |        |      0 |    0 |  1,279 |    2,098 |     1.6 |
| tox                | likely             |  1,025 |     944 |     81 |        |      0 |    0 |  1,361 |    2,098 |     3.1 |
| tox                | unsafe             |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     1.4 |
| tox                | infer-basedpyright |  1,331 |     945 |     98 |    288 |      0 |    0 |  1,667 |    2,098 |    16.3 |
| tox                | infer-ty           |  1,368 |     945 |     97 |    326 |      0 |    0 |  1,704 |    2,098 |     4.5 |
| tox                | infer-pyrefly      |  1,413 |     945 |     97 |    371 |      0 |    0 |  1,749 |    2,098 |     9.6 |
| tox                | infer-trace        |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     1.6 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 19,330 |  19,330 |        |        |
| certain            | stdlib                 | 14,519 |  14,519 |        |        |
| certain            | call                   |  6,703 |   6,703 |        |        |
| certain            | container+literal      |  4,464 |   4,464 |        |        |
| certain            | builtin                |  3,061 |   3,061 |        |        |
| certain            | loop                   |  2,757 |   2,757 |        |        |
| certain            | method                 |  2,529 |   2,529 |        |        |
| certain            | copy+loop              |  2,385 |   2,385 |        |        |
| certain            | container+literal+loop |  1,675 |   1,675 |        |        |
| certain            | open                   |  1,274 |   1,274 |        |        |
| certain            | literal+method         |  1,254 |   1,254 |        |        |
| certain            | returned               |    996 |     996 |        |        |
| likely             | constructor            | 28,676 |     245 | 28,431 |        |
| likely             | literal                | 19,333 |  19,333 |        |        |
| likely             | stdlib                 | 14,597 |  14,597 |        |        |
| likely             | call                   |  7,173 |   6,716 |    457 |        |
| likely             | container+literal      |  4,464 |   4,464 |        |        |
| likely             | method                 |  3,653 |   2,552 |  1,101 |        |
| likely             | builtin                |  3,061 |   3,061 |        |        |
| likely             | copy+loop              |  2,766 |   2,399 |    367 |        |
| likely             | loop                   |  2,760 |   2,760 |        |        |
| likely             | container+literal+loop |  1,675 |   1,675 |        |        |
| likely             | open                   |  1,274 |   1,274 |        |        |
| likely             | literal+method         |  1,254 |   1,254 |        |        |
| unsafe             | constructor            | 28,675 |     245 | 28,430 |        |
| unsafe             | literal                | 19,332 |  19,328 |        |      4 |
| unsafe             | stdlib                 | 14,896 |  14,521 |        |    375 |
| unsafe             | call                   |  7,159 |   6,703 |    456 |        |
| unsafe             | container+literal      |  4,464 |   4,464 |        |        |
| unsafe             | literal+member         |  4,152 |         |        |  4,152 |
| unsafe             | returned               |  3,782 |     998 |        |  2,784 |
| unsafe             | method                 |  3,630 |   2,529 |  1,101 |        |
| unsafe             | builtin                |  3,061 |   3,061 |        |        |
| unsafe             | loop                   |  2,757 |   2,757 |        |        |
| unsafe             | copy+loop              |  2,751 |   2,385 |    366 |        |
| unsafe             | container+literal+loop |  1,675 |   1,675 |        |        |
| infer-basedpyright | constructor            | 28,623 |     244 | 28,379 |        |
| infer-basedpyright | literal                | 19,333 |  19,329 |        |      4 |
| infer-basedpyright | checker                | 18,349 |         |        | 18,349 |
| infer-basedpyright | stdlib                 | 15,012 |  14,463 |        |    549 |
| infer-basedpyright | call                   |  7,248 |   6,698 |    550 |        |
| infer-basedpyright | container+literal      |  4,467 |   4,467 |        |        |
| infer-basedpyright | literal+member         |  4,151 |         |        |  4,151 |
| infer-basedpyright | returned               |  4,038 |     977 |        |  3,061 |
| infer-basedpyright | method                 |  3,773 |   2,526 |  1,247 |        |
| infer-basedpyright | copy+loop              |  3,197 |   2,385 |    812 |        |
| infer-basedpyright | builtin                |  3,061 |   3,061 |        |        |
| infer-basedpyright | loop                   |  2,757 |   2,757 |        |        |
| infer-ty           | constructor            | 28,620 |     245 | 28,375 |        |
| infer-ty           | literal                | 19,332 |  19,328 |        |      4 |
| infer-ty           | stdlib                 | 15,022 |  14,479 |        |    543 |
| infer-ty           | checker                | 14,942 |         |        | 14,942 |
| infer-ty           | call                   |  7,208 |   6,698 |    510 |        |
| infer-ty           | container+literal      |  4,468 |   4,468 |        |        |
| infer-ty           | literal+member         |  4,152 |         |        |  4,152 |
| infer-ty           | returned               |  4,006 |     998 |        |  3,008 |
| infer-ty           | method                 |  3,743 |   2,526 |  1,217 |        |
| infer-ty           | copy+loop              |  3,102 |   2,385 |    717 |        |
| infer-ty           | builtin                |  3,061 |   3,061 |        |        |
| infer-ty           | loop                   |  2,757 |   2,757 |        |        |
| infer-pyrefly      | constructor            | 28,611 |     244 | 28,367 |        |
| infer-pyrefly      | literal                | 19,332 |  19,328 |        |      4 |
| infer-pyrefly      | checker                | 17,674 |         |        | 17,674 |
| infer-pyrefly      | stdlib                 | 15,039 |  14,483 |        |    556 |
| infer-pyrefly      | call                   |  7,205 |   6,698 |    507 |        |
| infer-pyrefly      | container+literal      |  4,466 |   4,466 |        |        |
| infer-pyrefly      | literal+member         |  4,151 |         |        |  4,151 |
| infer-pyrefly      | returned               |  3,992 |     993 |        |  2,999 |
| infer-pyrefly      | method                 |  3,743 |   2,526 |  1,217 |        |
| infer-pyrefly      | copy+loop              |  3,129 |   2,385 |    744 |        |
| infer-pyrefly      | builtin                |  3,061 |   3,061 |        |        |
| infer-pyrefly      | loop                   |  2,757 |   2,757 |        |        |
| infer-trace        | constructor            | 21,157 |      13 | 21,144 |        |
| infer-trace        | literal                |  9,243 |   9,242 |        |      1 |
| infer-trace        | call                   |  6,676 |   6,224 |    452 |        |
| infer-trace        | method                 |  2,992 |   1,965 |  1,027 |        |
| infer-trace        | stdlib                 |  2,438 |   2,345 |        |     93 |
| infer-trace        | literal+member         |  2,410 |         |        |  2,410 |
| infer-trace        | traced                 |  2,389 |         |        |  2,389 |
| infer-trace        | container+literal      |  2,076 |   2,076 |        |        |
| infer-trace        | builtin                |  1,275 |   1,275 |        |        |
| infer-trace        | copy+loop              |  1,260 |   1,073 |    187 |        |
| infer-trace        | returned               |    862 |     316 |        |    546 |
| infer-trace        | loop                   |    841 |     841 |        |        |
| infer-union        | constructor            | 21,093 |      13 | 21,080 |        |
| infer-union        | literal                |  9,243 |   9,242 |        |      1 |
| infer-union        | agreed+checker         |  8,591 |         |        |  8,591 |
| infer-union        | call                   |  6,710 |   6,219 |    491 |        |
| infer-union        | checker                |  5,312 |         |        |  5,312 |
| infer-union        | method                 |  3,103 |   1,962 |  1,141 |        |
| infer-union        | stdlib                 |  2,447 |   2,333 |        |    114 |
| infer-union        | literal+member         |  2,410 |         |        |  2,410 |
| infer-union        | traced                 |  2,370 |         |        |  2,370 |
| infer-union        | container+literal      |  2,079 |   2,079 |        |        |
| infer-union        | copy+loop              |  1,446 |   1,073 |    373 |        |
| infer-union        | builtin                |  1,275 |   1,275 |        |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  13,076 |  63,149 |        0 |
| django             |  17,176 |   2,786 |  11,768 |        0 |
| sqlalchemy         |  12,962 |     847 |  10,177 |        0 |
| pydantic           |   3,117 |     405 |   1,521 |        0 |
| pandas             |  77,793 |  24,356 |  36,481 |        0 |
| twisted            |  17,874 |   4,697 |  10,742 |        0 |
| pip                |   8,924 |   1,304 |   5,350 |        0 |
| structlog          |     316 |      28 |     190 |        0 |
| attrs              |     393 |      11 |     289 |        0 |
| click              |     608 |      63 |     243 |        0 |
| hypercorn          |     355 |      58 |     163 |        0 |
| starlette          |     744 |      97 |     333 |        0 |
| werkzeug           |   1,293 |     127 |     639 |        0 |
| mkdocs             |   2,332 |     482 |   1,040 |        0 |
| httpx              |     569 |      73 |     262 |        0 |
| black              |   1,273 |     163 |     403 |        0 |
| fastapi            |     742 |      65 |     420 |        0 |
| cattrs             |     520 |      37 |     380 |        0 |
| pytest             |   3,003 |     285 |   1,360 |        0 |
| botocore           |   3,786 |     608 |   2,635 |        0 |
| uvicorn            |     489 |      47 |     211 |        0 |
| mcp                |   1,720 |     236 |     790 |        0 |
| textual            |   6,483 |     741 |   3,035 |        0 |
| pdm                |   2,718 |     323 |   1,248 |        0 |
| strawberry-graphql |   1,806 |     218 |     977 |        0 |
| pygments           |   7,666 |     228 |   6,703 |        0 |
| streamlink         |   3,029 |     250 |   2,097 |        0 |
| sphinx             |   7,972 |     900 |   3,842 |        0 |
| tox                |   1,762 |     138 |     681 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |       42.13 |     17.45 |    1 |                       594.2 |     631.5 | hyperfine |
| django             |    4 |        8.44 |      3.45 |    1 |                       117.7 |     126.8 | hyperfine |
| sqlalchemy         |    4 |        6.95 |      3.63 |    1 |                       104.3 |     110.6 | hyperfine |
| pydantic           |    4 |        1.65 |      0.78 |    1 |                        23.4 |      25.7 | hyperfine |
| pandas             |    4 |       48.11 |     17.08 |    1 |                       735.1 |     760.8 | hyperfine |
| twisted            |    4 |        6.25 |      2.51 |    1 |                        88.8 |      96.8 | hyperfine |
| pip                |    4 |        4.13 |      1.69 |    1 |                        62.6 |      67.2 | hyperfine |
| structlog          |    4 |        0.25 |      0.24 |    1 |                         3.1 |       4.2 | hyperfine |
| attrs              |    4 |         0.2 |      0.27 |    1 |                         2.6 |       3.6 | hyperfine |
| click              |    4 |        0.39 |      0.32 |    1 |                         5.3 |       6.4 | hyperfine |
| hypercorn          |    4 |        0.33 |      0.26 |    1 |                         4.0 |       5.3 | hyperfine |
| starlette          |    4 |        0.42 |      0.32 |    1 |                         5.2 |       6.6 | hyperfine |
| werkzeug           |    4 |        0.72 |       0.4 |    1 |                         9.6 |      10.9 | hyperfine |
| mkdocs             |    4 |         0.8 |      0.52 |    1 |                        10.7 |      12.8 | hyperfine |
| httpx              |    4 |        0.35 |      0.27 |    1 |                         4.4 |       5.6 | hyperfine |
| black              |    4 |        0.51 |       0.3 |    1 |                         7.0 |       8.2 | hyperfine |
| fastapi            |    4 |         0.6 |      0.51 |    1 |                         8.6 |      10.1 | hyperfine |
| cattrs             |    4 |        0.34 |      0.32 |    1 |                         4.4 |       5.8 | hyperfine |
| pytest             |    4 |        1.38 |      0.82 |    1 |                        19.1 |      21.1 | hyperfine |
| botocore           |    4 |         1.7 |      0.78 |    1 |                        23.8 |      26.1 | hyperfine |
| uvicorn            |    4 |        0.41 |      0.29 |    1 |                         5.2 |       6.5 | hyperfine |
| mcp                |    4 |        1.07 |      0.58 |    1 |                        14.1 |      16.2 | hyperfine |
| textual            |    4 |        2.56 |      1.11 |    1 |                        35.3 |      38.8 | hyperfine |
| pdm                |    4 |        1.58 |       0.9 |    1 |                        21.0 |      24.0 | hyperfine |
| strawberry-graphql |    4 |        1.57 |       0.8 |    1 |                        21.1 |      24.4 | hyperfine |
| pygments           |    4 |        2.59 |      1.09 |    1 |                        45.6 |      48.9 | hyperfine |
| streamlink         |    4 |        2.03 |      0.89 |    1 |                        28.4 |      30.9 | hyperfine |
| sphinx             |    4 |        4.12 |      1.42 |    1 |                        60.5 |      63.0 | hyperfine |
| tox                |    4 |        1.02 |      0.48 |    1 |                        13.3 |      14.3 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                   tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | ----------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  482 | Ran 17585 tests: FAILED (failures=6, skipped=1149, expected failures=5) |    81.1 |     55.5 |
| django             | certain |    972 |    971 |        1 |                      |                                                                         |         |          |
| django             | likely  |    318 |    316 |        2 |                      |                                                                         |         |          |
| django             | guess   |    360 |    343 |       17 |                      |                                                                         |         |          |
| sqlalchemy         |         |        |        |          |                  139 |                                    29521 passed, 975 skipped, 1 warning |   142.8 |    126.9 |
| sqlalchemy         | certain |  1,068 |  1,050 |       18 |                      |                                                                         |         |          |
| sqlalchemy         | likely  |    157 |    154 |        3 |                      |                                                                         |         |          |
| sqlalchemy         | guess   |    117 |    115 |        2 |                      |                                                                         |         |          |
| pydantic           |         |        |        |          |                    1 |                         65 failed, 6900 passed, 350 skipped, 29 xfailed |    76.5 |     68.4 |
| pydantic           | certain |    522 |    517 |        5 |                      |                                                                         |         |          |
| pydantic           | likely  |     47 |     47 |        0 |                      |                                                                         |         |          |
| pydantic           | guess   |     31 |     31 |        0 |                      |                                                                         |         |          |
| pandas             |         |        |        |          |                1,417 |                   165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   159.9 |    110.6 |
| pandas             | certain | 12,885 | 12,807 |       78 |                      |                                                                         |         |          |
| pandas             | likely  | 20,038 | 19,972 |       66 |                      |                                                                         |         |          |
| pandas             | guess   |    821 |    775 |       46 |                      |                                                                         |         |          |
| structlog          |         |        |        |          |                    0 |                           24 failed, 860 passed, 37 skipped, 2 warnings |     5.2 |      2.7 |
| structlog          | certain |     62 |     62 |        0 |                      |                                                                         |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                         |         |          |
| structlog          | guess   |      6 |      6 |        0 |                      |                                                                         |         |          |
| attrs              |         |        |        |          |                    2 |                             1 failed, 1382 passed, 2 skipped, 2 xfailed |     5.0 |      2.5 |
| attrs              | certain |     72 |     72 |        0 |                      |                                                                         |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                         |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                         |         |          |
| click              |         |        |        |          |                    0 |                    1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     6.2 |      8.2 |
| click              | certain |    222 |    222 |        0 |                      |                                                                         |         |          |
| click              | likely  |     19 |     18 |        1 |                      |                                                                         |         |          |
| click              | guess   |     25 |     25 |        0 |                      |                                                                         |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                    2 failed, 194 passed |     8.9 |      8.7 |
| hypercorn          | certain |     63 |     63 |        0 |                      |                                                                         |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                         |         |          |
| hypercorn          | guess   |     10 |     10 |        0 |                      |                                                                         |         |          |
| starlette          |         |        |        |          |                    0 |                                       1271 passed, 2 skipped, 2 xfailed |    18.7 |     19.5 |
| starlette          | certain |    193 |    192 |        1 |                      |                                                                         |         |          |
| starlette          | likely  |     47 |     47 |        0 |                      |                                                                         |         |          |
| starlette          | guess   |     29 |     29 |        0 |                      |                                                                         |         |          |
| werkzeug           |         |        |        |          |                    0 |                              1 failed, 979 passed, 1 skipped, 1 warning |    13.3 |     10.6 |
| werkzeug           | certain |    354 |    350 |        4 |                      |                                                                         |         |          |
| werkzeug           | likely  |     44 |     44 |        0 |                      |                                                                         |         |          |
| werkzeug           | guess   |     33 |     33 |        0 |                      |                                                                         |         |          |
| mkdocs             |         |        |        |          |                   12 |                 Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    11.5 |     10.5 |
| mkdocs             | certain |    628 |    627 |        1 |                      |                                                                         |         |          |
| mkdocs             | likely  |    322 |    322 |        0 |                      |                                                                         |         |          |
| mkdocs             | guess   |    116 |    116 |        0 |                      |                                                                         |         |          |
| httpx              |         |        |        |          |                    0 |                                        1 failed, 1416 passed, 1 skipped |    11.7 |     10.2 |
| httpx              | certain |    181 |    181 |        0 |                      |                                                                         |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                         |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                         |         |          |
| black              |         |        |        |          |                    0 |                                519 passed, 1 skipped, 9 subtests passed |     7.1 |      5.8 |
| black              | certain |    606 |    606 |        0 |                      |                                                                         |         |          |
| black              | likely  |    101 |    101 |        0 |                      |                                                                         |         |          |
| black              | guess   |     39 |     39 |        0 |                      |                                                                         |         |          |
| fastapi            |         |        |        |          |                    0 |                                      3551 passed, 17 skipped, 4 xfailed |    15.2 |     14.5 |
| fastapi            | certain |    220 |    220 |        0 |                      |                                                                         |         |          |
| fastapi            | likely  |     28 |     28 |        0 |                      |                                                                         |         |          |
| fastapi            | guess   |     22 |     22 |        0 |                      |                                                                         |         |          |
| cattrs             |         |        |        |          |                    0 |                                                  994 passed, 15 xfailed |    22.3 |     20.6 |
| cattrs             | certain |     99 |     97 |        2 |                      |                                                                         |         |          |
| cattrs             | likely  |     23 |     23 |        0 |                      |                                                                         |         |          |
| cattrs             | guess   |     13 |     13 |        0 |                      |                                                                         |         |          |
| pytest             |         |        |        |          |                   14 |     46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    44.0 |     22.3 |
| pytest             | certain |  1,097 |  1,085 |       12 |                      |                                                                         |         |          |
| pytest             | likely  |    122 |    122 |        0 |                      |                                                                         |         |          |
| pytest             | guess   |    108 |    108 |        0 |                      |                                                                         |         |          |
| botocore           |         |        |        |          |                  299 |                                       7 failed, 4593 passed, 96 skipped |    30.5 |     29.1 |
| botocore           | certain |    327 |    326 |        1 |                      |                                                                         |         |          |
| botocore           | likely  |    138 |    138 |        0 |                      |                                                                         |         |          |
| botocore           | guess   |    102 |    101 |        1 |                      |                                                                         |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                 1350 passed, 12 skipped |    41.3 |     30.1 |
| uvicorn            | certain |    169 |    165 |        4 |                      |                                                                         |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                         |         |          |
| uvicorn            | guess   |      8 |      8 |        0 |                      |                                                                         |         |          |
| mcp                |         |        |        |          |                    0 |                             3 failed, 6092 passed, 8 skipped, 1 xfailed |    15.1 |     16.0 |
| mcp                | certain |    508 |    508 |        0 |                      |                                                                         |         |          |
| mcp                | likely  |    127 |    126 |        1 |                      |                                                                         |         |          |
| mcp                | guess   |     56 |     55 |        1 |                      |                                                                         |         |          |
| pdm                |         |        |        |          |                    0 |                                     1472 passed, 1 skipped, 60 warnings |    18.1 |     20.0 |
| pdm                | certain |    869 |    865 |        4 |                      |                                                                         |         |          |
| pdm                | likely  |    126 |    126 |        0 |                      |                                                                         |         |          |
| pdm                | guess   |     78 |     78 |        0 |                      |                                                                         |         |          |
| strawberry-graphql |         |        |        |          |                    0 | 51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    16.5 |     13.4 |
| strawberry-graphql | certain |    390 |    384 |        6 |                      |                                                                         |         |          |
| strawberry-graphql | likely  |     95 |     94 |        1 |                      |                                                                         |         |          |
| strawberry-graphql | guess   |     28 |     28 |        0 |                      |                                                                         |         |          |
| pygments           |         |        |        |          |                   87 |                                       1 failed, 5330 passed, 15 skipped |    31.7 |     23.3 |
| pygments           | certain |    289 |    289 |        0 |                      |                                                                         |         |          |
| pygments           | likely  |     58 |     58 |        0 |                      |                                                                         |         |          |
| pygments           | guess   |     62 |     62 |        0 |                      |                                                                         |         |          |
| streamlink         |         |        |        |          |                    8 |                            15 failed, 7233 passed, 36 skipped, 9 errors |    19.9 |     21.7 |
| streamlink         | certain |    274 |    273 |        1 |                      |                                                                         |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                         |         |          |
| streamlink         | guess   |     37 |     37 |        0 |                      |                                                                         |         |          |
| sphinx             |         |        |        |          |                    0 |                         10 failed, 2392 passed, 22 skipped, 35 warnings |    21.1 |     17.4 |
| sphinx             | certain |  2,056 |  2,027 |       29 |                      |                                                                         |         |          |
| sphinx             | likely  |    411 |    411 |        0 |                      |                                                                         |         |          |
| sphinx             | guess   |    196 |    193 |        3 |                      |                                                                         |         |          |
| tox                |         |        |        |          |                    0 |                            17 failed, 8525 passed, 31 skipped, 6 errors |    31.5 |     17.5 |
| tox                | certain |    703 |    700 |        3 |                      |                                                                         |         |          |
| tox                | likely  |     61 |     61 |        0 |                      |                                                                         |         |          |
| tox                | guess   |     30 |     29 |        1 |                      |                                                                         |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus             | shape                                        | no fix | traced | one type |
| ------------------ | -------------------------------------------- | -----: | -----: | -------: |
| django             | `call: chained .method()`                    |  1,355 |    958 |      609 |
| django             | `call: self.method()`                        |    987 |    662 |      421 |
| django             | `call: param.method()`                       |    657 |    477 |      377 |
| django             | `call: imported function`                    |    656 |    276 |      200 |
| django             | `call: local.method()`                       |    546 |    385 |      263 |
| django             | `empty list`                                 |    452 |      0 |        0 |
| django             | `copy: local`                                |    435 |    319 |      223 |
| django             | `attr: chained`                              |    406 |    280 |      183 |
| django             | `None literal`                               |    365 |    104 |      104 |
| django             | `copy: param (unannotated)`                  |    348 |    237 |      141 |
| django             | `attr: self.x`                               |    345 |    271 |      142 |
| django             | `call: imported.attr()`                      |    301 |    145 |       97 |
| django             | `other constant`                             |    296 |     22 |       22 |
| django             | `subscript: other`                           |    265 |    196 |      159 |
| django             | `dict (mixed/unknown elements)`              |    236 |    104 |       74 |
| django             | `empty dict`                                 |    201 |      0 |        0 |
| django             | `call: module function (unannotated)`        |    195 |    142 |      104 |
| django             | `tuple (mixed/unknown elements)`             |    193 |     92 |       70 |
| django             | `copy: imported`                             |    179 |      8 |        7 |
| django             | `call: builtin getattr()`                    |    174 |    154 |       73 |
| django             | `subscript: local[...]`                      |    173 |    108 |       90 |
| django             | `attr: local.x`                              |    170 |    130 |       94 |
| django             | `ListComp (unknown elements)`                |    165 |    118 |       81 |
| django             | `list (mixed/unknown elements)`              |    157 |     54 |       42 |
| django             | `conditional`                                |    157 |    127 |       65 |
| django             | `binop (unknown operands)`                   |    140 |     90 |       84 |
| django             | `subscript: param[...]`                      |    136 |    112 |       94 |
| django             | `attr: param.x`                              |    127 |    104 |       76 |
| django             | `boolop (or)`                                |    112 |     94 |       71 |
| django             | `call: builtin set()`                        |    109 |     16 |       12 |
| django             | `attr: imported.x`                           |    105 |     21 |       17 |
| django             | `call: imported class`                       |     96 |     14 |       14 |
| django             | `call: module.func()`                        |     96 |     70 |       61 |
| django             | `call: builtin enumerate()`                  |     85 |     67 |       37 |
| django             | `call: builtin sorted()`                     |     77 |     64 |       58 |
| django             | `call: builtin list()`                       |     62 |     47 |       34 |
| django             | `subscript: imported[...]`                   |     59 |     40 |       36 |
| django             | `call: builtin zip()`                        |     58 |     40 |       18 |
| django             | `DictComp (unknown elements)`                |     57 |     37 |       21 |
| django             | `call: other name`                           |     52 |     36 |       21 |
| django             | `call: local name`                           |     51 |     35 |       16 |
| django             | `call: builtin property()`                   |     49 |      0 |        0 |
| django             | `boolop (and)`                               |     42 |     29 |       22 |
| django             | `call: global.method()`                      |     42 |     29 |       19 |
| django             | `binop (one side literal)`                   |     42 |     16 |       16 |
| django             | `SetComp (unknown elements)`                 |     40 |     21 |       17 |
| django             | `copy: other`                                |     40 |      7 |        5 |
| django             | `empty tuple`                                |     39 |      0 |        0 |
| django             | `compare`                                    |     35 |     20 |       20 |
| django             | `call: builtin next()`                       |     32 |     31 |       27 |
| django             | `call: module class`                         |     31 |      7 |        7 |
| django             | `GeneratorExp (unknown elements)`            |     29 |     26 |       25 |
| django             | `copy: global`                               |     27 |      6 |        6 |
| django             | `copy: modclass`                             |     27 |      0 |        0 |
| django             | `copy: moddef`                               |     26 |      0 |        0 |
| django             | `call: other callee`                         |     24 |     17 |       12 |
| django             | `attr: module.x`                             |     21 |      5 |        4 |
| django             | `call: builtin iter()`                       |     21 |     17 |       16 |
| django             | `call: builtin reversed()`                   |     19 |     16 |        6 |
| django             | `await: call: self.method()`                 |     18 |     14 |        6 |
| django             | `call: builtin tuple()`                      |     18 |     13 |        7 |
| django             | `attr: modclass.x`                           |     17 |      1 |        1 |
| django             | `call: builtin type()`                       |     17 |     14 |       10 |
| django             | `await: call: chained .method()`             |     17 |     17 |        3 |
| django             | `call: other.method()`                       |     15 |     11 |        6 |
| django             | `call: builtin object()`                     |     14 |      2 |        2 |
| django             | `call: modclass.method()`                    |     14 |      5 |        5 |
| django             | `binop: literal % formatting`                |     13 |      7 |        7 |
| django             | `attr: cls.x`                                |     12 |     12 |       10 |
| django             | `copy: builtin`                              |     12 |      1 |        1 |
| django             | `call: builtin staticmethod()`               |     11 |      0 |        0 |
| django             | `call: builtin max()`                        |     11 |      7 |        7 |
| django             | `call: cls.method()`                         |     10 |      6 |        4 |
| django             | `copy: self`                                 |      9 |      7 |        4 |
| django             | `call: capitalised`                          |      9 |      6 |        3 |
| django             | `await: call: other name`                    |      9 |      9 |        8 |
| django             | `call: builtin dict()`                       |      8 |      7 |        3 |
| django             | `call: builtin.method()`                     |      8 |      6 |        5 |
| django             | `call: builtin map()`                        |      7 |      3 |        2 |
| django             | `call: builtin frozenset()`                  |      7 |      1 |        1 |
| django             | `set (mixed/unknown elements)`               |      6 |      4 |        4 |
| django             | `call: builtin min()`                        |      6 |      2 |        2 |
| django             | `attr: global.x`                             |      6 |      1 |        1 |
| django             | `await: call: module.func()`                 |      6 |      0 |        0 |
| django             | `call: param name`                           |      5 |      5 |        1 |
| django             | `await: call: param name`                    |      4 |      4 |        3 |
| django             | `call: builtin sum()`                        |      4 |      3 |        3 |
| django             | `call: builtin filter()`                     |      4 |      4 |        4 |
| django             | `call: builtin divmod()`                     |      4 |      4 |        4 |
| django             | `call: builtin str()`                        |      3 |      2 |        2 |
| django             | `call: builtin len()`                        |      3 |      2 |        2 |
| django             | `call: str-literal.method()`                 |      3 |      3 |        3 |
| django             | `attr: other.x`                              |      3 |      3 |        2 |
| django             | `await: call: param.method()`                |      2 |      2 |        0 |
| django             | `subscript: self[...]`                       |      2 |      1 |        1 |
| django             | `call: global name`                          |      2 |      0 |        0 |
| django             | `call: builtin slice()`                      |      2 |      1 |        1 |
| django             | `await: call: other callee`                  |      2 |      2 |        2 |
| django             | `JoinedStr`                                  |      2 |      1 |        1 |
| django             | `attr: builtin.x`                            |      2 |      1 |        1 |
| django             | `call: builtin int()`                        |      2 |      1 |        1 |
| django             | `call: bytes-literal.method()`               |      2 |      1 |        1 |
| django             | `subscript: global[...]`                     |      2 |      2 |        2 |
| django             | `await: call: local.method()`                |      1 |      1 |        0 |
| django             | `await: call: module function (unannotated)` |      1 |      1 |        1 |
| django             | `call: builtin abs()`                        |      1 |      1 |        1 |
| django             | `await: call: local name`                    |      1 |      1 |        0 |
| django             | `await: call: other.method()`                |      1 |      1 |        0 |
| django             | `call: builtin vars()`                       |      1 |      1 |        0 |
| django             | `unaryop USub`                               |      1 |      0 |        0 |
| django             | `call: builtin super()`                      |      1 |      1 |        1 |
| django             | `subscript: other[...]`                      |      1 |      1 |        0 |
| django             | `await: call: imported function`             |      1 |      1 |        0 |
| django             | `call: builtin __import__()`                 |      1 |      1 |        1 |
| django             | `call: builtin repr()`                       |      1 |      1 |        1 |
| django             | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| sqlalchemy         | `call: chained .method()`                    |    961 |    469 |      314 |
| sqlalchemy         | `other constant`                             |    773 |      8 |        8 |
| sqlalchemy         | `call: self.method()`                        |    644 |    347 |      204 |
| sqlalchemy         | `attr: chained`                              |    576 |    285 |      218 |
| sqlalchemy         | `call: local.method()`                       |    528 |    281 |      176 |
| sqlalchemy         | `call: param.method()`                       |    458 |    275 |      160 |
| sqlalchemy         | `attr: self.x`                               |    373 |    289 |      153 |
| sqlalchemy         | `copy: local`                                |    360 |    222 |      137 |
| sqlalchemy         | `subscript: other`                           |    357 |    211 |      133 |
| sqlalchemy         | `call: imported function`                    |    344 |    165 |       93 |
| sqlalchemy         | `attr: param.x`                              |    337 |    273 |      164 |
| sqlalchemy         | `call: imported.attr()`                      |    328 |    171 |      115 |
| sqlalchemy         | `attr: local.x`                              |    264 |    206 |      131 |
| sqlalchemy         | `tuple (mixed/unknown elements)`             |    206 |    137 |       91 |
| sqlalchemy         | `copy: param (unannotated)`                  |    183 |    134 |       89 |
| sqlalchemy         | `subscript: local[...]`                      |    180 |     98 |       58 |
| sqlalchemy         | `None literal`                               |    173 |     73 |       73 |
| sqlalchemy         | `ListComp (unknown elements)`                |    159 |    118 |       72 |
| sqlalchemy         | `copy: modclass`                             |    147 |      1 |        1 |
| sqlalchemy         | `attr: imported.x`                           |    145 |     17 |       17 |
| sqlalchemy         | `call: imported class`                       |    129 |     10 |       10 |
| sqlalchemy         | `call: builtin list()`                       |    120 |     76 |       44 |
| sqlalchemy         | `copy: imported`                             |    118 |      1 |        1 |
| sqlalchemy         | `empty list`                                 |    114 |      0 |        0 |
| sqlalchemy         | `copy: param (annotated)`                    |    110 |     91 |       55 |
| sqlalchemy         | `call: module.func()`                        |    108 |     49 |       41 |
| sqlalchemy         | `dict (mixed/unknown elements)`              |    103 |     16 |       14 |
| sqlalchemy         | `call: builtin getattr()`                    |    102 |     84 |       41 |
| sqlalchemy         | `binop (unknown operands)`                   |     90 |     48 |       37 |
| sqlalchemy         | `call: param name`                           |     90 |     36 |       13 |
| sqlalchemy         | `call: builtin set()`                        |     86 |     37 |       23 |
| sqlalchemy         | `empty dict`                                 |     82 |      0 |        0 |
| sqlalchemy         | `boolop (or)`                                |     76 |     62 |       49 |
| sqlalchemy         | `call: other name`                           |     76 |     57 |       32 |
| sqlalchemy         | `subscript: param[...]`                      |     76 |     60 |       36 |
| sqlalchemy         | `conditional`                                |     72 |     42 |       23 |
| sqlalchemy         | `call: local name`                           |     63 |     51 |       23 |
| sqlalchemy         | `copy: other`                                |     63 |     20 |       15 |
| sqlalchemy         | `list (mixed/unknown elements)`              |     62 |     18 |       10 |
| sqlalchemy         | `DictComp (unknown elements)`                |     61 |     35 |       15 |
| sqlalchemy         | `call: module function (unannotated)`        |     59 |     49 |       37 |
| sqlalchemy         | `call: builtin zip()`                        |     57 |     35 |       17 |
| sqlalchemy         | `copy: global`                               |     50 |      6 |        6 |
| sqlalchemy         | `call: builtin dict()`                       |     49 |     23 |       12 |
| sqlalchemy         | `call: builtin enumerate()`                  |     42 |     29 |        6 |
| sqlalchemy         | `call: builtin tuple()`                      |     38 |     15 |        5 |
| sqlalchemy         | `call: other.method()`                       |     36 |     21 |       11 |
| sqlalchemy         | `SetComp (unknown elements)`                 |     35 |     20 |       14 |
| sqlalchemy         | `call: module class`                         |     35 |     17 |       17 |
| sqlalchemy         | `call: cls.method()`                         |     34 |     28 |       19 |
| sqlalchemy         | `call: module function (annotated)`          |     32 |     29 |       15 |
| sqlalchemy         | `boolop (and)`                               |     26 |     26 |       22 |
| sqlalchemy         | `call: builtin.method()`                     |     24 |     22 |       10 |
| sqlalchemy         | `attr: modclass.x`                           |     21 |      0 |        0 |
| sqlalchemy         | `attr: cls.x`                                |     20 |     19 |        9 |
| sqlalchemy         | `empty tuple`                                |     16 |      0 |        0 |
| sqlalchemy         | `compare`                                    |     15 |      9 |        9 |
| sqlalchemy         | `call: builtin type()`                       |     15 |     10 |        3 |
| sqlalchemy         | `call: other callee`                         |     15 |     11 |        5 |
| sqlalchemy         | `await: call: imported function`             |     15 |     13 |        8 |
| sqlalchemy         | `GeneratorExp (unknown elements)`            |     14 |      7 |        7 |
| sqlalchemy         | `attr: global.x`                             |     14 |      0 |        0 |
| sqlalchemy         | `call: builtin sorted()`                     |     13 |      9 |        8 |
| sqlalchemy         | `call: global.method()`                      |     13 |     11 |       11 |
| sqlalchemy         | `copy: moddef`                               |     13 |      0 |        0 |
| sqlalchemy         | `subscript: global[...]`                     |     12 |     11 |        9 |
| sqlalchemy         | `call: global name`                          |     12 |     12 |        4 |
| sqlalchemy         | `attr: module.x`                             |     11 |      9 |        9 |
| sqlalchemy         | `copy: builtin`                              |     11 |      0 |        0 |
| sqlalchemy         | `attr: other.x`                              |     10 |      7 |        7 |
| sqlalchemy         | `call: builtin object()`                     |     10 |      6 |        6 |
| sqlalchemy         | `binop (one side literal)`                   |      9 |      6 |        6 |
| sqlalchemy         | `call: modclass.method()`                    |      8 |      8 |        5 |
| sqlalchemy         | `subscript: other[...]`                      |      8 |      8 |        4 |
| sqlalchemy         | `call: builtin reversed()`                   |      8 |      6 |        6 |
| sqlalchemy         | `copy: self`                                 |      7 |      6 |        5 |
| sqlalchemy         | `await: call: chained .method()`             |      6 |      1 |        1 |
| sqlalchemy         | `set (mixed/unknown elements)`               |      6 |      4 |        2 |
| sqlalchemy         | `call: builtin __import__()`                 |      5 |      2 |        2 |
| sqlalchemy         | `await: call: self.method()`                 |      4 |      4 |        4 |
| sqlalchemy         | `call: self name`                            |      4 |      4 |        2 |
| sqlalchemy         | `call: builtin frozenset()`                  |      4 |      0 |        0 |
| sqlalchemy         | `call: builtin int()`                        |      3 |      1 |        1 |
| sqlalchemy         | `call: builtin bool()`                       |      3 |      3 |        3 |
| sqlalchemy         | `subscript: imported[...]`                   |      3 |      2 |        1 |
| sqlalchemy         | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| sqlalchemy         | `await: call: local.method()`                |      2 |      0 |        0 |
| sqlalchemy         | `unaryop USub`                               |      2 |      1 |        1 |
| sqlalchemy         | `call: builtin next()`                       |      2 |      2 |        0 |
| sqlalchemy         | `call: builtin max()`                        |      2 |      2 |        2 |
| sqlalchemy         | `call: builtin globals()`                    |      2 |      1 |        1 |
| sqlalchemy         | `call: builtin eval()`                       |      2 |      2 |        0 |
| sqlalchemy         | `subscript: self[...]`                       |      2 |      2 |        0 |
| sqlalchemy         | `call: builtin vars()`                       |      2 |      2 |        2 |
| sqlalchemy         | `call: builtin sum()`                        |      2 |      0 |        0 |
| sqlalchemy         | `await: call: module function (unannotated)` |      2 |      2 |        2 |
| sqlalchemy         | `await: copy: param (annotated)`             |      1 |      0 |        0 |
| sqlalchemy         | `JoinedStr`                                  |      1 |      1 |        1 |
| sqlalchemy         | `call: builtin len()`                        |      1 |      1 |        1 |
| sqlalchemy         | `await: call: module.func()`                 |      1 |      0 |        0 |
| sqlalchemy         | `await: call: builtin anext()`               |      1 |      0 |        0 |
| sqlalchemy         | `call: builtin property()`                   |      1 |      0 |        0 |
| sqlalchemy         | `subscript: modclass[...]`                   |      1 |      0 |        0 |
| sqlalchemy         | `call: builtin str()`                        |      1 |      1 |        1 |
| sqlalchemy         | `binop: literal % formatting`                |      1 |      1 |        1 |
| sqlalchemy         | `call: capitalised`                          |      1 |      1 |        1 |
| sqlalchemy         | `call: builtin id()`                         |      1 |      1 |        1 |
| sqlalchemy         | `await: copy: local`                         |      1 |      1 |        0 |
| sqlalchemy         | `call: str-literal.method()`                 |      1 |      1 |        1 |
| pydantic           | `call: chained .method()`                    |    126 |     54 |       36 |
| pydantic           | `call: local.method()`                       |    114 |     58 |       30 |
| pydantic           | `call: imported function`                    |    112 |     60 |       41 |
| pydantic           | `call: param.method()`                       |    101 |     59 |       31 |
| pydantic           | `call: self.method()`                        |     56 |     32 |        9 |
| pydantic           | `call: builtin getattr()`                    |     53 |     29 |       17 |
| pydantic           | `call: module function (annotated)`          |     53 |     14 |        8 |
| pydantic           | `attr: param.x`                              |     49 |     25 |       12 |
| pydantic           | `conditional`                                |     37 |     18 |       10 |
| pydantic           | `copy: param (annotated)`                    |     36 |     20 |       12 |
| pydantic           | `copy: local`                                |     35 |     16 |       12 |
| pydantic           | `tuple (mixed/unknown elements)`             |     35 |      8 |        6 |
| pydantic           | `call: imported.attr()`                      |     33 |     28 |       10 |
| pydantic           | `attr: chained`                              |     33 |      5 |        4 |
| pydantic           | `subscript: other`                           |     32 |     11 |        3 |
| pydantic           | `boolop (or)`                                |     27 |     14 |        6 |
| pydantic           | `attr: local.x`                              |     26 |      9 |        6 |
| pydantic           | `subscript: param[...]`                      |     26 |     15 |       12 |
| pydantic           | `empty dict`                                 |     25 |      0 |        0 |
| pydantic           | `binop (unknown operands)`                   |     23 |      7 |        5 |
| pydantic           | `call: module class`                         |     23 |      2 |        2 |
| pydantic           | `dict (mixed/unknown elements)`              |     22 |     15 |       11 |
| pydantic           | `copy: imported`                             |     21 |      2 |        2 |
| pydantic           | `attr: cls.x`                                |     20 |      6 |        4 |
| pydantic           | `call: module.func()`                        |     20 |      9 |        6 |
| pydantic           | `subscript: imported[...]`                   |     20 |      1 |        0 |
| pydantic           | `other constant`                             |     20 |      1 |        1 |
| pydantic           | `None literal`                               |     19 |     10 |       10 |
| pydantic           | `ListComp (unknown elements)`                |     16 |      7 |        3 |
| pydantic           | `empty list`                                 |     16 |      0 |        0 |
| pydantic           | `DictComp (unknown elements)`                |     15 |      2 |        1 |
| pydantic           | `copy: builtin`                              |     14 |      0 |        0 |
| pydantic           | `attr: self.x`                               |     13 |      6 |        3 |
| pydantic           | `call: builtin zip()`                        |     13 |      2 |        2 |
| pydantic           | `subscript: local[...]`                      |     12 |      4 |        4 |
| pydantic           | `copy: global`                               |     12 |      5 |        3 |
| pydantic           | `call: builtin tuple()`                      |     12 |      5 |        4 |
| pydantic           | `call: builtin enumerate()`                  |     12 |      2 |        1 |
| pydantic           | `call: builtin dict()`                       |     12 |      1 |        0 |
| pydantic           | `call: param name`                           |     11 |     11 |        6 |
| pydantic           | `call: other name`                           |     10 |      5 |        3 |
| pydantic           | `call: builtin list()`                       |     10 |      7 |        6 |
| pydantic           | `set (mixed/unknown elements)`               |     10 |      0 |        0 |
| pydantic           | `call: builtin set()`                        |      8 |      1 |        1 |
| pydantic           | `GeneratorExp (unknown elements)`            |      8 |      2 |        2 |
| pydantic           | `call: builtin reversed()`                   |      7 |      6 |        2 |
| pydantic           | `call: global.method()`                      |      7 |      1 |        0 |
| pydantic           | `call: builtin object()`                     |      6 |      1 |        1 |
| pydantic           | `copy: other`                                |      6 |      5 |        5 |
| pydantic           | `attr: imported.x`                           |      6 |      2 |        2 |
| pydantic           | `call: cls.method()`                         |      6 |      2 |        1 |
| pydantic           | `call: local name`                           |      5 |      3 |        2 |
| pydantic           | `call: capitalised`                          |      5 |      2 |        2 |
| pydantic           | `list (mixed/unknown elements)`              |      5 |      3 |        2 |
| pydantic           | `attr: module.x`                             |      4 |      0 |        0 |
| pydantic           | `-`                                          |      4 |      0 |        0 |
| pydantic           | `call: builtin type()`                       |      4 |      3 |        0 |
| pydantic           | `call: other.method()`                       |      4 |      4 |        2 |
| pydantic           | `call: imported class`                       |      4 |      0 |        0 |
| pydantic           | `call: builtin next()`                       |      4 |      2 |        1 |
| pydantic           | `call: global name`                          |      4 |      4 |        4 |
| pydantic           | `SetComp (unknown elements)`                 |      3 |      2 |        0 |
| pydantic           | `compare`                                    |      3 |      0 |        0 |
| pydantic           | `attr: modclass.x`                           |      3 |      2 |        2 |
| pydantic           | `call: builtin.method()`                     |      3 |      3 |        2 |
| pydantic           | `NamedExpr`                                  |      2 |      0 |        0 |
| pydantic           | `call: builtin len()`                        |      2 |      2 |        2 |
| pydantic           | `attr: builtin.x`                            |      2 |      0 |        0 |
| pydantic           | `copy: cls`                                  |      2 |      2 |        1 |
| pydantic           | `subscript: builtin[...]`                    |      2 |      0 |        0 |
| pydantic           | `attr: other.x`                              |      2 |      0 |        0 |
| pydantic           | `subscript: global[...]`                     |      2 |      1 |        1 |
| pydantic           | `call: builtin max()`                        |      2 |      1 |        1 |
| pydantic           | `call: builtin min()`                        |      2 |      1 |        1 |
| pydantic           | `call: str-literal.method()`                 |      2 |      0 |        0 |
| pydantic           | `call: builtin globals()`                    |      1 |      1 |        1 |
| pydantic           | `copy: moddef`                               |      1 |      0 |        0 |
| pydantic           | `call: modclass.method()`                    |      1 |      1 |        1 |
| pydantic           | `binop (one side literal)`                   |      1 |      1 |        1 |
| pydantic           | `call: builtin iter()`                       |      1 |      0 |        0 |
| pydantic           | `call: builtin open()`                       |      1 |      0 |        0 |
| pydantic           | `copy: self`                                 |      1 |      0 |        0 |
| pandas             | `call: local.method()`                       |  6,252 |  5,162 |    4,816 |
| pandas             | `call: chained .method()`                    |  4,857 |  3,766 |    3,438 |
| pandas             | `call: module.func()`                        |  3,635 |  2,467 |    2,326 |
| pandas             | `copy: param (unannotated)`                  |  1,960 |  1,741 |      802 |
| pandas             | `call: imported function`                    |  1,614 |  1,186 |    1,025 |
| pandas             | `subscript: other`                           |  1,515 |  1,231 |    1,101 |
| pandas             | `call: param.method()`                       |  1,479 |  1,024 |      821 |
| pandas             | `binop (unknown operands)`                   |  1,123 |    965 |      818 |
| pandas             | `subscript: local[...]`                      |    948 |    753 |      704 |
| pandas             | `attr: chained`                              |    805 |    537 |      442 |
| pandas             | `list (mixed/unknown elements)`              |    798 |    548 |      410 |
| pandas             | `call: param name`                           |    769 |    726 |      269 |
| pandas             | `call: imported class`                       |    681 |    577 |      572 |
| pandas             | `call: self.method()`                        |    618 |    417 |      255 |
| pandas             | `call: imported.attr()`                      |    607 |    481 |      395 |
| pandas             | `call: other callee`                         |    503 |    418 |      339 |
| pandas             | `conditional`                                |    473 |    382 |      202 |
| pandas             | `attr: local.x`                              |    453 |    343 |      284 |
| pandas             | `copy: local`                                |    421 |    280 |      201 |
| pandas             | `subscript: param[...]`                      |    384 |    277 |      167 |
| pandas             | `ListComp (unknown elements)`                |    377 |    197 |      142 |
| pandas             | `tuple (mixed/unknown elements)`             |    371 |    224 |      177 |
| pandas             | `compare`                                    |    345 |    269 |      247 |
| pandas             | `dict (mixed/unknown elements)`              |    334 |    210 |      183 |
| pandas             | `attr: self.x`                               |    316 |    232 |      132 |
| pandas             | `call: builtin zip()`                        |    307 |    204 |      149 |
| pandas             | `call: builtin getattr()`                    |    307 |    222 |      151 |
| pandas             | `attr: param.x`                              |    300 |    200 |      111 |
| pandas             | `call: local name`                           |    296 |    255 |      148 |
| pandas             | `call: module function (unannotated)`        |    283 |    140 |       88 |
| pandas             | `binop (one side literal)`                   |    280 |    211 |      190 |
| pandas             | `empty list`                                 |    278 |      0 |        0 |
| pandas             | `call: builtin enumerate()`                  |    235 |    156 |      110 |
| pandas             | `other constant`                             |    176 |     48 |       48 |
| pandas             | `call: builtin list()`                       |    170 |    124 |       86 |
| pandas             | `None literal`                               |    157 |    112 |      112 |
| pandas             | `attr: module.x`                             |    121 |     84 |       82 |
| pandas             | `Lambda`                                     |    121 |     75 |       75 |
| pandas             | `call: global.method()`                      |    118 |      4 |        2 |
| pandas             | `call: other name`                           |    113 |     74 |       53 |
| pandas             | `call: module function (annotated)`          |    100 |     62 |       35 |
| pandas             | `attr: imported.x`                           |     94 |     23 |       23 |
| pandas             | `empty dict`                                 |     90 |      0 |        0 |
| pandas             | `copy: imported`                             |     89 |     50 |       50 |
| pandas             | `copy: other`                                |     78 |      7 |        4 |
| pandas             | `copy: param (annotated)`                    |     76 |     51 |       35 |
| pandas             | `GeneratorExp (unknown elements)`            |     70 |     60 |       60 |
| pandas             | `call: capitalised`                          |     60 |     59 |       58 |
| pandas             | `copy: builtin`                              |     59 |     42 |       42 |
| pandas             | `DictComp (unknown elements)`                |     58 |     43 |       33 |
| pandas             | `call: builtin set()`                        |     49 |     18 |       14 |
| pandas             | `call: other.method()`                       |     47 |     28 |       23 |
| pandas             | `unaryop Invert`                             |     40 |     28 |       26 |
| pandas             | `boolop (and)`                               |     37 |     22 |       20 |
| pandas             | `call: builtin next()`                       |     36 |     30 |       22 |
| pandas             | `call: builtin divmod()`                     |     35 |     24 |       24 |
| pandas             | `boolop (or)`                                |     34 |     22 |       22 |
| pandas             | `call: builtin dict()`                       |     31 |     11 |        6 |
| pandas             | `call: builtin sorted()`                     |     29 |     24 |       23 |
| pandas             | `call: builtin type()`                       |     27 |     24 |        6 |
| pandas             | `call: builtin tuple()`                      |     26 |     17 |        9 |
| pandas             | `call: builtin slice()`                      |     25 |     22 |       22 |
| pandas             | `call: cls name`                             |     22 |     15 |        1 |
| pandas             | `call: builtin max()`                        |     20 |     14 |       12 |
| pandas             | `call: builtin open()`                       |     20 |     13 |        6 |
| pandas             | `unaryop USub`                               |     19 |     14 |       14 |
| pandas             | `copy: self`                                 |     18 |     16 |       10 |
| pandas             | `subscript: self[...]`                       |     18 |     15 |       10 |
| pandas             | `subscript: imported[...]`                   |     17 |     13 |       11 |
| pandas             | `copy: moddef`                               |     17 |      0 |        0 |
| pandas             | `call: cls.method()`                         |     16 |     12 |        9 |
| pandas             | `attr: other.x`                              |     14 |      1 |        1 |
| pandas             | `SetComp (unknown elements)`                 |     14 |     10 |        5 |
| pandas             | `copy: global`                               |     13 |      7 |        6 |
| pandas             | `subscript: global[...]`                     |     13 |     11 |        4 |
| pandas             | `set (mixed/unknown elements)`               |     12 |      5 |        5 |
| pandas             | `call: builtin min()`                        |     12 |      7 |        6 |
| pandas             | `call: modclass.method()`                    |     11 |      8 |        8 |
| pandas             | `call: builtin len()`                        |     11 |      5 |        5 |
| pandas             | `call: builtin.method()`                     |     10 |      9 |        8 |
| pandas             | `copy: modclass`                             |     10 |      0 |        0 |
| pandas             | `JoinedStr`                                  |      8 |      4 |        4 |
| pandas             | `attr: cls.x`                                |      7 |      5 |        4 |
| pandas             | `call: builtin map()`                        |      7 |      7 |        7 |
| pandas             | `call: builtin abs()`                        |      7 |      6 |        6 |
| pandas             | `call: module class`                         |      7 |      3 |        2 |
| pandas             | `subscript: other[...]`                      |      6 |      3 |        3 |
| pandas             | `call: builtin frozenset()`                  |      6 |      2 |        2 |
| pandas             | `call: builtin iter()`                       |      6 |      4 |        4 |
| pandas             | `call: builtin property()`                   |      5 |      0 |        0 |
| pandas             | `call: builtin eval()`                       |      5 |      5 |        5 |
| pandas             | `call: builtin sum()`                        |      4 |      2 |        2 |
| pandas             | `call: builtin range()`                      |      4 |      2 |        2 |
| pandas             | `call: builtin pow()`                        |      4 |      4 |        4 |
| pandas             | `call: builtin all()`                        |      3 |      2 |        2 |
| pandas             | `call: global name`                          |      3 |      0 |        0 |
| pandas             | `call: builtin round()`                      |      3 |      1 |        1 |
| pandas             | `unaryop UAdd`                               |      3 |      3 |        3 |
| pandas             | `copy: cls`                                  |      2 |      0 |        0 |
| pandas             | `call: builtin object()`                     |      2 |      1 |        1 |
| pandas             | `call: str-literal.method()`                 |      2 |      1 |        1 |
| pandas             | `call: self name`                            |      1 |      1 |        1 |
| pandas             | `attr: modclass.x`                           |      1 |      1 |        1 |
| pandas             | `call: builtin ord()`                        |      1 |      0 |        0 |
| pandas             | `call: builtin isinstance()`                 |      1 |      1 |        1 |
| pandas             | `call: builtin float()`                      |      1 |      0 |        0 |
| pandas             | `call: builtin reversed()`                   |      1 |      0 |        0 |
| pandas             | `call: builtin bytes()`                      |      1 |      1 |        1 |
| pandas             | `attr: builtin.x`                            |      1 |      1 |        1 |
| pandas             | `empty tuple`                                |      1 |      0 |        0 |
| pandas             | `call: builtin repr()`                       |      1 |      1 |        1 |
| structlog          | `copy: other`                                |     47 |      2 |        2 |
| structlog          | `call: param.method()`                       |     27 |     23 |       11 |
| structlog          | `call: imported.attr()`                      |     16 |     15 |       13 |
| structlog          | `attr: chained`                              |     12 |      2 |        2 |
| structlog          | `call: chained .method()`                    |      8 |      6 |        5 |
| structlog          | `call: module function (annotated)`          |      7 |      2 |        1 |
| structlog          | `copy: param (annotated)`                    |      5 |      5 |        4 |
| structlog          | `call: imported function`                    |      5 |      1 |        1 |
| structlog          | `copy: local`                                |      5 |      5 |        5 |
| structlog          | `call: self.method()`                        |      4 |      4 |        1 |
| structlog          | `empty list`                                 |      4 |      0 |        0 |
| structlog          | `call: module.func()`                        |      4 |      3 |        2 |
| structlog          | `attr: self.x`                               |      3 |      3 |        1 |
| structlog          | `boolop (or)`                                |      3 |      3 |        2 |
| structlog          | `tuple (mixed/unknown elements)`             |      3 |      2 |        1 |
| structlog          | `subscript: imported[...]`                   |      3 |      3 |        3 |
| structlog          | `None literal`                               |      3 |      2 |        2 |
| structlog          | `DictComp (unknown elements)`                |      3 |      3 |        3 |
| structlog          | `call: builtin object()`                     |      3 |      0 |        0 |
| structlog          | `copy: global`                               |      3 |      0 |        0 |
| structlog          | `call: builtin getattr()`                    |      3 |      3 |        1 |
| structlog          | `await: call: chained .method()`             |      2 |      0 |        0 |
| structlog          | `dict (mixed/unknown elements)`              |      2 |      1 |        1 |
| structlog          | `empty dict`                                 |      2 |      0 |        0 |
| structlog          | `subscript: global[...]`                     |      2 |      2 |        2 |
| structlog          | `subscript: other`                           |      2 |      2 |        1 |
| structlog          | `copy: moddef`                               |      1 |      0 |        0 |
| structlog          | `call: local name`                           |      1 |      1 |        0 |
| structlog          | `conditional`                                |      1 |      1 |        0 |
| structlog          | `call: local.method()`                       |      1 |      1 |        1 |
| structlog          | `other constant`                             |      1 |      1 |        1 |
| structlog          | `call: builtin type()`                       |      1 |      1 |        1 |
| structlog          | `binop (unknown operands)`                   |      1 |      1 |        1 |
| structlog          | `attr: param.x`                              |      1 |      1 |        0 |
| structlog          | `subscript: local[...]`                      |      1 |      1 |        0 |
| attrs              | `call: imported function`                    |     35 |      6 |        3 |
| attrs              | `copy: param (unannotated)`                  |     18 |     17 |        6 |
| attrs              | `call: module function (annotated)`          |     18 |     15 |       10 |
| attrs              | `call: module function (unannotated)`        |     16 |     15 |        8 |
| attrs              | `call: local.method()`                       |     12 |      9 |        2 |
| attrs              | `empty list`                                 |     11 |      0 |        0 |
| attrs              | `empty dict`                                 |     11 |      0 |        0 |
| attrs              | `attr: self.x`                               |     11 |     11 |        7 |
| attrs              | `call: builtin getattr()`                    |     10 |      7 |        2 |
| attrs              | `call: module.func()`                        |      8 |      6 |        1 |
| attrs              | `copy: local`                                |      8 |      8 |        8 |
| attrs              | `conditional`                                |      8 |      5 |        5 |
| attrs              | `ListComp (unknown elements)`                |      8 |      5 |        3 |
| attrs              | `attr: local.x`                              |      8 |      7 |        5 |
| attrs              | `call: self.method()`                        |      6 |      6 |        0 |
| attrs              | `compare`                                    |      5 |      0 |        0 |
| attrs              | `call: param.method()`                       |      5 |      3 |        2 |
| attrs              | `tuple (mixed/unknown elements)`             |      5 |      4 |        4 |
| attrs              | `copy: imported`                             |      4 |      0 |        0 |
| attrs              | `dict (mixed/unknown elements)`              |      4 |      3 |        2 |
| attrs              | `call: builtin type()`                       |      4 |      3 |        0 |
| attrs              | `attr: modclass.x`                           |      4 |      3 |        3 |
| attrs              | `DictComp (unknown elements)`                |      4 |      0 |        0 |
| attrs              | `boolop (or)`                                |      4 |      3 |        3 |
| attrs              | `attr: param.x`                              |      3 |      3 |        1 |
| attrs              | `call: builtin set()`                        |      3 |      1 |        1 |
| attrs              | `attr: cls.x`                                |      3 |      3 |        2 |
| attrs              | `attr: chained`                              |      3 |      2 |        1 |
| attrs              | `call: chained .method()`                    |      3 |      3 |        0 |
| attrs              | `call: global.method()`                      |      3 |      2 |        2 |
| attrs              | `call: builtin zip()`                        |      3 |      1 |        0 |
| attrs              | `subscript: param[...]`                      |      3 |      3 |        2 |
| attrs              | `copy: moddef`                               |      3 |      1 |        1 |
| attrs              | `copy: other`                                |      3 |      3 |        1 |
| attrs              | `call: other name`                           |      2 |      1 |        1 |
| attrs              | `call: builtin list()`                       |      2 |      2 |        2 |
| attrs              | `call: builtin object()`                     |      2 |      0 |        0 |
| attrs              | `binop (unknown operands)`                   |      2 |      1 |        1 |
| attrs              | `call: other callee`                         |      2 |      2 |        0 |
| attrs              | `call: builtin tuple()`                      |      2 |      2 |        2 |
| attrs              | `subscript: other[...]`                      |      2 |      2 |        2 |
| attrs              | `boolop (and)`                               |      2 |      2 |        2 |
| attrs              | `call: module class`                         |      2 |      2 |        2 |
| attrs              | `subscript: imported[...]`                   |      1 |      0 |        0 |
| attrs              | `call: builtin frozenset()`                  |      1 |      0 |        0 |
| attrs              | `call: param name`                           |      1 |      0 |        0 |
| attrs              | `attr: builtin.x`                            |      1 |      0 |        0 |
| attrs              | `call: imported.attr()`                      |      1 |      0 |        0 |
| attrs              | `call: builtin compile()`                    |      1 |      1 |        1 |
| attrs              | `call: builtin reversed()`                   |      1 |      1 |        0 |
| attrs              | `subscript: other`                           |      1 |      0 |        0 |
| attrs              | `SetComp (unknown elements)`                 |      1 |      0 |        0 |
| attrs              | `call: builtin hash()`                       |      1 |      1 |        1 |
| attrs              | `copy: param (annotated)`                    |      1 |      1 |        1 |
| attrs              | `other constant`                             |      1 |      1 |        1 |
| attrs              | `binop (one side literal)`                   |      1 |      1 |        1 |
| attrs              | `call: builtin dict()`                       |      1 |      0 |        0 |
| click              | `call: chained .method()`                    |     29 |     23 |       16 |
| click              | `other constant`                             |     17 |      0 |        0 |
| click              | `call: imported function`                    |     16 |     12 |        8 |
| click              | `call: self.method()`                        |     16 |     14 |        4 |
| click              | `call: local.method()`                       |     12 |      9 |        7 |
| click              | `conditional`                                |     10 |      8 |        8 |
| click              | `call: builtin getattr()`                    |      9 |      5 |        3 |
| click              | `attr: self.x`                               |      9 |      6 |        4 |
| click              | `empty list`                                 |      9 |      0 |        0 |
| click              | `call: module.func()`                        |      9 |      4 |        4 |
| click              | `attr: imported.x`                           |      9 |      6 |        6 |
| click              | `None literal`                               |      9 |      7 |        7 |
| click              | `call: param.method()`                       |      7 |      5 |        4 |
| click              | `call: other name`                           |      6 |      4 |        4 |
| click              | `attr: global.x`                             |      5 |      0 |        0 |
| click              | `copy: param (annotated)`                    |      5 |      2 |        2 |
| click              | `call: module function (annotated)`          |      4 |      4 |        0 |
| click              | `copy: local`                                |      4 |      2 |        2 |
| click              | `call: imported class`                       |      4 |      2 |        2 |
| click              | `call: other callee`                         |      4 |      1 |        1 |
| click              | `call: capitalised`                          |      4 |      0 |        0 |
| click              | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| click              | `boolop (and)`                               |      4 |      4 |        4 |
| click              | `call: imported.attr()`                      |      3 |      2 |        1 |
| click              | `subscript: other`                           |      3 |      2 |        2 |
| click              | `attr: module.x`                             |      3 |      3 |        2 |
| click              | `boolop (or)`                                |      2 |      2 |        2 |
| click              | `binop (unknown operands)`                   |      2 |      1 |        1 |
| click              | `call: other.method()`                       |      2 |      2 |        1 |
| click              | `list (mixed/unknown elements)`              |      2 |      1 |        1 |
| click              | `call: global name`                          |      2 |      0 |        0 |
| click              | `copy: builtin`                              |      2 |      0 |        0 |
| click              | `copy: imported`                             |      1 |      1 |        1 |
| click              | `call: builtin dict()`                       |      1 |      1 |        1 |
| click              | `binop (one side literal)`                   |      1 |      0 |        0 |
| click              | `call: global.method()`                      |      1 |      0 |        0 |
| click              | `call: builtin.method()`                     |      1 |      1 |        1 |
| click              | `empty dict`                                 |      1 |      0 |        0 |
| click              | `attr: other.x`                              |      1 |      1 |        1 |
| click              | `DictComp (unknown elements)`                |      1 |      0 |        0 |
| click              | `JoinedStr`                                  |      1 |      0 |        0 |
| click              | `attr: param.x`                              |      1 |      1 |        0 |
| click              | `copy: other`                                |      1 |      0 |        0 |
| click              | `call: local name`                           |      1 |      1 |        0 |
| click              | `call: param name`                           |      1 |      1 |        0 |
| click              | `call: module class`                         |      1 |      1 |        1 |
| click              | `attr: chained`                              |      1 |      1 |        1 |
| click              | `ListComp (unknown elements)`                |      1 |      1 |        1 |
| click              | `subscript: param[...]`                      |      1 |      0 |        0 |
| hypercorn          | `call: chained .method()`                    |     24 |     15 |       12 |
| hypercorn          | `call: module.func()`                        |     13 |      8 |        8 |
| hypercorn          | `attr: param.x`                              |     13 |      8 |        8 |
| hypercorn          | `call: local.method()`                       |     12 |      2 |        1 |
| hypercorn          | `call: param.method()`                       |     11 |      2 |        1 |
| hypercorn          | `None literal`                               |     10 |      3 |        3 |
| hypercorn          | `binop (unknown operands)`                   |     10 |      2 |        2 |
| hypercorn          | `call: imported class`                       |      7 |      3 |        3 |
| hypercorn          | `subscript: param[...]`                      |      6 |      6 |        6 |
| hypercorn          | `call: other.method()`                       |      5 |      3 |        3 |
| hypercorn          | `await: call: chained .method()`             |      4 |      1 |        0 |
| hypercorn          | `binop (one side literal)`                   |      4 |      0 |        0 |
| hypercorn          | `call: imported function`                    |      4 |      0 |        0 |
| hypercorn          | `await: call: param name`                    |      3 |      3 |        2 |
| hypercorn          | `call: self.method()`                        |      3 |      1 |        1 |
| hypercorn          | `copy: local`                                |      3 |      2 |        2 |
| hypercorn          | `dict (mixed/unknown elements)`              |      2 |      1 |        1 |
| hypercorn          | `list (mixed/unknown elements)`              |      2 |      1 |        1 |
| hypercorn          | `copy: imported`                             |      2 |      0 |        0 |
| hypercorn          | `empty list`                                 |      2 |      0 |        0 |
| hypercorn          | `attr: chained`                              |      2 |      1 |        1 |
| hypercorn          | `call: other callee`                         |      2 |      2 |        2 |
| hypercorn          | `tuple (mixed/unknown elements)`             |      2 |      0 |        0 |
| hypercorn          | `call: builtin object()`                     |      1 |      0 |        0 |
| hypercorn          | `call: builtin bytearray()`                  |      1 |      1 |        1 |
| hypercorn          | `call: module function (annotated)`          |      1 |      1 |        1 |
| hypercorn          | `boolop (or)`                                |      1 |      1 |        1 |
| hypercorn          | `other constant`                             |      1 |      0 |        0 |
| hypercorn          | `await: call: local.method()`                |      1 |      0 |        0 |
| hypercorn          | `call: builtin property()`                   |      1 |      0 |        0 |
| hypercorn          | `attr: self.x`                               |      1 |      0 |        0 |
| hypercorn          | `subscript: local[...]`                      |      1 |      0 |        0 |
| hypercorn          | `DictComp (unknown elements)`                |      1 |      1 |        1 |
| hypercorn          | `call: builtin open()`                       |      1 |      0 |        0 |
| hypercorn          | `copy: modclass`                             |      1 |      0 |        0 |
| hypercorn          | `call: builtin next()`                       |      1 |      1 |        1 |
| hypercorn          | `call: builtin min()`                        |      1 |      1 |        1 |
| hypercorn          | `copy: other`                                |      1 |      0 |        0 |
| hypercorn          | `call: builtin eval()`                       |      1 |      0 |        0 |
| hypercorn          | `call: builtin getattr()`                    |      1 |      0 |        0 |
| starlette          | `call: param.method()`                       |     33 |     29 |       20 |
| starlette          | `call: local.method()`                       |     31 |     23 |       18 |
| starlette          | `call: chained .method()`                    |     26 |     24 |       18 |
| starlette          | `call: builtin reversed()`                   |     15 |      4 |        2 |
| starlette          | `call: imported class`                       |     15 |     15 |       14 |
| starlette          | `subscript: param[...]`                      |     14 |     14 |       13 |
| starlette          | `attr: self.x`                               |     11 |      8 |        4 |
| starlette          | `call: self.method()`                        |     11 |     10 |        8 |
| starlette          | `await: call: self.method()`                 |     10 |      9 |        2 |
| starlette          | `call: module.func()`                        |      9 |      9 |        7 |
| starlette          | `other constant`                             |      9 |      0 |        0 |
| starlette          | `call: imported function`                    |      9 |      9 |        7 |
| starlette          | `tuple (mixed/unknown elements)`             |      8 |      7 |        6 |
| starlette          | `call: other callee`                         |      8 |      8 |        8 |
| starlette          | `await: call: module.func()`                 |      7 |      7 |        6 |
| starlette          | `attr: chained`                              |      6 |      6 |        5 |
| starlette          | `conditional`                                |      6 |      6 |        3 |
| starlette          | `copy: param (annotated)`                    |      6 |      5 |        2 |
| starlette          | `copy: local`                                |      6 |      5 |        5 |
| starlette          | `dict (mixed/unknown elements)`              |      6 |      2 |        2 |
| starlette          | `None literal`                               |      5 |      4 |        4 |
| starlette          | `subscript: local[...]`                      |      5 |      5 |        4 |
| starlette          | `binop (unknown operands)`                   |      5 |      2 |        2 |
| starlette          | `ListComp (unknown elements)`                |      5 |      4 |        4 |
| starlette          | `call: builtin getattr()`                    |      5 |      5 |        3 |
| starlette          | `call: builtin dict()`                       |      5 |      2 |        2 |
| starlette          | `await: call: local.method()`                |      5 |      4 |        3 |
| starlette          | `call: module class`                         |      4 |      3 |        3 |
| starlette          | `attr: local.x`                              |      4 |      4 |        4 |
| starlette          | `boolop (or)`                                |      4 |      4 |        3 |
| starlette          | `await: call: other name`                    |      4 |      4 |        2 |
| starlette          | `call: builtin set()`                        |      4 |      3 |        3 |
| starlette          | `await: call: chained .method()`             |      3 |      3 |        2 |
| starlette          | `await: call: param name`                    |      3 |      3 |        1 |
| starlette          | `await: call: local name`                    |      2 |      2 |        2 |
| starlette          | `subscript: other`                           |      2 |      2 |        1 |
| starlette          | `binop (one side literal)`                   |      2 |      1 |        1 |
| starlette          | `attr: param.x`                              |      2 |      2 |        1 |
| starlette          | `boolop (and)`                               |      2 |      2 |        2 |
| starlette          | `subscript: imported[...]`                   |      2 |      1 |        0 |
| starlette          | `call: global.method()`                      |      1 |      1 |        1 |
| starlette          | `attr: imported.x`                           |      1 |      1 |        1 |
| starlette          | `copy: imported`                             |      1 |      0 |        0 |
| starlette          | `await: call: other.method()`                |      1 |      1 |        1 |
| starlette          | `copy: other`                                |      1 |      1 |        0 |
| starlette          | `await: call: imported function`             |      1 |      0 |        0 |
| starlette          | `set (mixed/unknown elements)`               |      1 |      1 |        1 |
| starlette          | `call: module function (annotated)`          |      1 |      1 |        1 |
| starlette          | `empty dict`                                 |      1 |      0 |        0 |
| starlette          | `call: builtin sorted()`                     |      1 |      1 |        1 |
| starlette          | `empty list`                                 |      1 |      0 |        0 |
| starlette          | `attr: module.x`                             |      1 |      0 |        0 |
| starlette          | `call: other.method()`                       |      1 |      1 |        1 |
| starlette          | `attr: other.x`                              |      1 |      1 |        1 |
| werkzeug           | `other constant`                             |     81 |      4 |        4 |
| werkzeug           | `call: chained .method()`                    |     64 |     43 |       29 |
| werkzeug           | `call: imported function`                    |     36 |     20 |       18 |
| werkzeug           | `call: local.method()`                       |     34 |     20 |       15 |
| werkzeug           | `call: param.method()`                       |     33 |     30 |       23 |
| werkzeug           | `copy: local`                                |     32 |     18 |       13 |
| werkzeug           | `call: module function (annotated)`          |     27 |     12 |        8 |
| werkzeug           | `attr: self.x`                               |     26 |     22 |       17 |
| werkzeug           | `empty list`                                 |     23 |      0 |        0 |
| werkzeug           | `call: self.method()`                        |     22 |     16 |       12 |
| werkzeug           | `call: other callee`                         |     20 |      0 |        0 |
| werkzeug           | `call: module.func()`                        |     17 |     10 |        8 |
| werkzeug           | `call: builtin getattr()`                    |     16 |     16 |        9 |
| werkzeug           | `copy: self`                                 |     13 |     11 |        6 |
| werkzeug           | `call: other name`                           |     11 |      9 |        8 |
| werkzeug           | `None literal`                               |     11 |     10 |       10 |
| werkzeug           | `call: builtin set()`                        |     10 |      0 |        0 |
| werkzeug           | `subscript: other`                           |     10 |      3 |        3 |
| werkzeug           | `copy: param (annotated)`                    |      9 |      4 |        2 |
| werkzeug           | `list (mixed/unknown elements)`              |      9 |      8 |        7 |
| werkzeug           | `call: local name`                           |      8 |      8 |        7 |
| werkzeug           | `call: builtin enumerate()`                  |      6 |      6 |        2 |
| werkzeug           | `tuple (mixed/unknown elements)`             |      6 |      4 |        1 |
| werkzeug           | `subscript: local[...]`                      |      5 |      5 |        4 |
| werkzeug           | `call: builtin next()`                       |      5 |      5 |        4 |
| werkzeug           | `attr: chained`                              |      5 |      2 |        2 |
| werkzeug           | `call: global.method()`                      |      5 |      5 |        3 |
| werkzeug           | `attr: local.x`                              |      5 |      3 |        3 |
| werkzeug           | `call: other.method()`                       |      5 |      5 |        5 |
| werkzeug           | `boolop (or)`                                |      5 |      2 |        2 |
| werkzeug           | `call: builtin iter()`                       |      4 |      4 |        4 |
| werkzeug           | `empty dict`                                 |      4 |      0 |        0 |
| werkzeug           | `call: imported class`                       |      4 |      1 |        1 |
| werkzeug           | `attr: module.x`                             |      4 |      1 |        1 |
| werkzeug           | `subscript: param[...]`                      |      4 |      3 |        3 |
| werkzeug           | `binop (unknown operands)`                   |      4 |      4 |        4 |
| werkzeug           | `ListComp (unknown elements)`                |      3 |      1 |        1 |
| werkzeug           | `call: builtin repr()`                       |      3 |      3 |        3 |
| werkzeug           | `call: imported.attr()`                      |      3 |      3 |        2 |
| werkzeug           | `copy: imported`                             |      3 |      0 |        0 |
| werkzeug           | `call: param name`                           |      3 |      2 |        1 |
| werkzeug           | `dict (mixed/unknown elements)`              |      3 |      3 |        3 |
| werkzeug           | `subscript: self[...]`                       |      2 |      2 |        0 |
| werkzeug           | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| werkzeug           | `call: builtin hash()`                       |      2 |      2 |        2 |
| werkzeug           | `attr: param.x`                              |      2 |      2 |        1 |
| werkzeug           | `call: builtin min()`                        |      2 |      1 |        1 |
| werkzeug           | `conditional`                                |      2 |      2 |        0 |
| werkzeug           | `call: builtin sorted()`                     |      2 |      0 |        0 |
| werkzeug           | `call: builtin zip()`                        |      2 |      0 |        0 |
| werkzeug           | `GeneratorExp (unknown elements)`            |      1 |      1 |        1 |
| werkzeug           | `call: module class`                         |      1 |      1 |        1 |
| werkzeug           | `call: builtin object()`                     |      1 |      0 |        0 |
| werkzeug           | `call: str-literal.method()`                 |      1 |      1 |        1 |
| werkzeug           | `compare`                                    |      1 |      1 |        1 |
| werkzeug           | `binop (one side literal)`                   |      1 |      1 |        1 |
| werkzeug           | `call: builtin max()`                        |      1 |      1 |        1 |
| werkzeug           | `attr: modclass.x`                           |      1 |      0 |        0 |
| werkzeug           | `subscript: builtin[...]`                    |      1 |      0 |        0 |
| werkzeug           | `copy: moddef`                               |      1 |      1 |        1 |
| werkzeug           | `attr: other.x`                              |      1 |      1 |        0 |
| werkzeug           | `call: builtin list()`                       |      1 |      1 |        1 |
| werkzeug           | `copy: other`                                |      1 |      1 |        1 |
| werkzeug           | `copy: builtin`                              |      1 |      0 |        0 |
| werkzeug           | `subscript: other[...]`                      |      1 |      0 |        0 |
| werkzeug           | `call: builtin compile()`                    |      1 |      1 |        1 |
| werkzeug           | `JoinedStr`                                  |      1 |      0 |        0 |
| werkzeug           | `call: builtin.method()`                     |      1 |      0 |        0 |
| werkzeug           | `copy: global`                               |      1 |      0 |        0 |
| werkzeug           | `call: capitalised`                          |      1 |      1 |        1 |
| werkzeug           | `call: builtin __import__()`                 |      1 |      1 |        1 |
| werkzeug           | `call: builtin property()`                   |      1 |      0 |        0 |
| mkdocs             | `call: imported.attr()`                      |    366 |     46 |       46 |
| mkdocs             | `call: self.method()`                        |    117 |    108 |      105 |
| mkdocs             | `call: local.method()`                       |     65 |     37 |       37 |
| mkdocs             | `dict (mixed/unknown elements)`              |     43 |     33 |       33 |
| mkdocs             | `call: imported function`                    |     42 |     26 |       25 |
| mkdocs             | `attr: param.x`                              |     37 |     32 |       31 |
| mkdocs             | `call: param.method()`                       |     32 |     24 |       21 |
| mkdocs             | `call: chained .method()`                    |     29 |     19 |       17 |
| mkdocs             | `tuple (mixed/unknown elements)`             |     29 |     29 |        9 |
| mkdocs             | `attr: chained`                              |     26 |     22 |       21 |
| mkdocs             | `copy: local`                                |     25 |     19 |       15 |
| mkdocs             | `call: module.func()`                        |     24 |     10 |        9 |
| mkdocs             | `call: module class`                         |     24 |     13 |       13 |
| mkdocs             | `call: other name`                           |     15 |      0 |        0 |
| mkdocs             | `call: other callee`                         |     15 |      0 |        0 |
| mkdocs             | `list (mixed/unknown elements)`              |     13 |     10 |        8 |
| mkdocs             | `call: imported class`                       |     12 |      9 |        9 |
| mkdocs             | `attr: self.x`                               |     12 |     12 |        7 |
| mkdocs             | `copy: param (unannotated)`                  |     10 |     10 |        7 |
| mkdocs             | `subscript: other`                           |      9 |      7 |        7 |
| mkdocs             | `call: module function (annotated)`          |      8 |      4 |        2 |
| mkdocs             | `attr: local.x`                              |      8 |      5 |        5 |
| mkdocs             | `subscript: param[...]`                      |      7 |      6 |        5 |
| mkdocs             | `copy: param (annotated)`                    |      6 |      5 |        3 |
| mkdocs             | `empty list`                                 |      6 |      0 |        0 |
| mkdocs             | `None literal`                               |      6 |      6 |        6 |
| mkdocs             | `conditional`                                |      4 |      4 |        4 |
| mkdocs             | `subscript: imported[...]`                   |      4 |      0 |        0 |
| mkdocs             | `call: builtin zip()`                        |      4 |      2 |        0 |
| mkdocs             | `call: other.method()`                       |      4 |      4 |        4 |
| mkdocs             | `call: module function (unannotated)`        |      3 |      1 |        0 |
| mkdocs             | `subscript: local[...]`                      |      3 |      1 |        1 |
| mkdocs             | `empty dict`                                 |      3 |      0 |        0 |
| mkdocs             | `other constant`                             |      3 |      0 |        0 |
| mkdocs             | `call: builtin reversed()`                   |      2 |      1 |        1 |
| mkdocs             | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| mkdocs             | `call: builtin open()`                       |      2 |      1 |        1 |
| mkdocs             | `call: capitalised`                          |      2 |      1 |        1 |
| mkdocs             | `call: builtin sorted()`                     |      1 |      0 |        0 |
| mkdocs             | `call: builtin dict()`                       |      1 |      1 |        1 |
| mkdocs             | `call: builtin set()`                        |      1 |      0 |        0 |
| mkdocs             | `JoinedStr`                                  |      1 |      0 |        0 |
| mkdocs             | `call: builtin tuple()`                      |      1 |      0 |        0 |
| mkdocs             | `copy: global`                               |      1 |      0 |        0 |
| mkdocs             | `call: builtin getattr()`                    |      1 |      1 |        1 |
| mkdocs             | `call: local name`                           |      1 |      0 |        0 |
| mkdocs             | `copy: self`                                 |      1 |      1 |        1 |
| mkdocs             | `boolop (or)`                                |      1 |      1 |        1 |
| mkdocs             | `ListComp (unknown elements)`                |      1 |      1 |        1 |
| mkdocs             | `copy: modclass`                             |      1 |      0 |        0 |
| mkdocs             | `call: builtin enumerate()`                  |      1 |      1 |        1 |
| mkdocs             | `call: builtin max()`                        |      1 |      1 |        1 |
| mkdocs             | `attr: builtin.x`                            |      1 |      0 |        0 |
| mkdocs             | `call: param name`                           |      1 |      0 |        0 |
| mkdocs             | `SetComp (unknown elements)`                 |      1 |      1 |        1 |
| mkdocs             | `binop (one side literal)`                   |      1 |      1 |        1 |
| httpx              | `attr: self.x`                               |     26 |     22 |       16 |
| httpx              | `call: param.method()`                       |     26 |     19 |       12 |
| httpx              | `call: local.method()`                       |     24 |     18 |       16 |
| httpx              | `call: chained .method()`                    |     24 |     22 |       18 |
| httpx              | `subscript: imported[...]`                   |     18 |      0 |        0 |
| httpx              | `subscript: other`                           |     17 |      2 |        2 |
| httpx              | `call: imported class`                       |     11 |      9 |        9 |
| httpx              | `call: self.method()`                        |     11 |      8 |        5 |
| httpx              | `boolop (or)`                                |     11 |      9 |        9 |
| httpx              | `ListComp (unknown elements)`                |      9 |      7 |        7 |
| httpx              | `attr: chained`                              |      8 |      6 |        6 |
| httpx              | `dict (mixed/unknown elements)`              |      8 |      7 |        7 |
| httpx              | `subscript: param[...]`                      |      8 |      4 |        4 |
| httpx              | `copy: local`                                |      7 |      2 |        2 |
| httpx              | `None literal`                               |      7 |      7 |        7 |
| httpx              | `conditional`                                |      5 |      5 |        3 |
| httpx              | `call: module class`                         |      5 |      5 |        5 |
| httpx              | `call: module.func()`                        |      4 |      2 |        2 |
| httpx              | `empty list`                                 |      4 |      0 |        0 |
| httpx              | `copy: param (annotated)`                    |      4 |      4 |        3 |
| httpx              | `Yield`                                      |      3 |      3 |        3 |
| httpx              | `tuple (mixed/unknown elements)`             |      3 |      3 |        3 |
| httpx              | `attr: param.x`                              |      3 |      2 |        2 |
| httpx              | `call: other name`                           |      2 |      2 |        2 |
| httpx              | `list (mixed/unknown elements)`              |      2 |      2 |        2 |
| httpx              | `await: call: chained .method()`             |      2 |      1 |        1 |
| httpx              | `call: builtin reversed()`                   |      2 |      1 |        1 |
| httpx              | `call: builtin locals()`                     |      1 |      0 |        0 |
| httpx              | `await: call: local.method()`                |      1 |      0 |        0 |
| httpx              | `call: builtin list()`                       |      1 |      1 |        1 |
| httpx              | `call: builtin dict()`                       |      1 |      1 |        1 |
| httpx              | `other constant`                             |      1 |      1 |        1 |
| httpx              | `call: builtin.method()`                     |      1 |      1 |        1 |
| httpx              | `copy: modclass`                             |      1 |      0 |        0 |
| httpx              | `await: call: other.method()`                |      1 |      0 |        0 |
| black              | `attr: param.x`                              |     59 |     57 |       31 |
| black              | `subscript: other`                           |     36 |     31 |       16 |
| black              | `attr: local.x`                              |     34 |     31 |       22 |
| black              | `call: local.method()`                       |     32 |     30 |       21 |
| black              | `call: chained .method()`                    |     21 |     15 |       13 |
| black              | `attr: chained`                              |     19 |     15 |       12 |
| black              | `copy: local`                                |     18 |     15 |       12 |
| black              | `copy: builtin`                              |     16 |      0 |        0 |
| black              | `call: imported function`                    |     13 |      5 |        4 |
| black              | `subscript: local[...]`                      |     12 |     11 |       11 |
| black              | `boolop (and)`                               |     11 |      8 |        6 |
| black              | `empty list`                                 |     11 |      0 |        0 |
| black              | `conditional`                                |     10 |     10 |        6 |
| black              | `call: builtin enumerate()`                  |      8 |      8 |        4 |
| black              | `call: module function (annotated)`          |      7 |      5 |        5 |
| black              | `call: module.func()`                        |      7 |      4 |        4 |
| black              | `binop (unknown operands)`                   |      7 |      7 |        7 |
| black              | `copy: param (annotated)`                    |      7 |      6 |        6 |
| black              | `call: param.method()`                       |      6 |      6 |        4 |
| black              | `binop (one side literal)`                   |      5 |      5 |        5 |
| black              | `attr: imported.x`                           |      4 |      4 |        4 |
| black              | `list (mixed/unknown elements)`              |      4 |      4 |        2 |
| black              | `tuple (mixed/unknown elements)`             |      4 |      3 |        1 |
| black              | `call: builtin next()`                       |      4 |      4 |        4 |
| black              | `attr: self.x`                               |      4 |      3 |        3 |
| black              | `call: builtin set()`                        |      3 |      1 |        1 |
| black              | `compare`                                    |      3 |      2 |        2 |
| black              | `call: builtin list()`                       |      3 |      3 |        3 |
| black              | `None literal`                               |      3 |      3 |        3 |
| black              | `copy: imported`                             |      2 |      1 |        1 |
| black              | `call: builtin getattr()`                    |      2 |      2 |        0 |
| black              | `SetComp (unknown elements)`                 |      2 |      2 |        2 |
| black              | `ListComp (unknown elements)`                |      2 |      1 |        1 |
| black              | `boolop (or)`                                |      2 |      2 |        2 |
| black              | `call: other name`                           |      2 |      2 |        2 |
| black              | `call: builtin min()`                        |      1 |      1 |        1 |
| black              | `call: imported class`                       |      1 |      1 |        1 |
| black              | `call: builtin.method()`                     |      1 |      1 |        1 |
| black              | `call: builtin max()`                        |      1 |      1 |        1 |
| black              | `DictComp (unknown elements)`                |      1 |      1 |        1 |
| black              | `dict (mixed/unknown elements)`              |      1 |      1 |        1 |
| black              | `call: builtin iter()`                       |      1 |      1 |        1 |
| black              | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| black              | `attr: module.x`                             |      1 |      1 |        1 |
| black              | `call: other.method()`                       |      1 |      1 |        1 |
| black              | `call: param name`                           |      1 |      1 |        1 |
| black              | `unaryop USub`                               |      1 |      1 |        1 |
| black              | `empty dict`                                 |      1 |      0 |        0 |
| black              | `call: builtin sorted()`                     |      1 |      1 |        1 |
| black              | `call: module class`                         |      1 |      1 |        1 |
| black              | `call: global.method()`                      |      1 |      1 |        1 |
| black              | `other constant`                             |      1 |      0 |        0 |
| black              | `subscript: imported[...]`                   |      1 |      0 |        0 |
| black              | `subscript: global[...]`                     |      1 |      0 |        0 |
| black              | `attr: other.x`                              |      1 |      1 |        1 |
| fastapi            | `call: chained .method()`                    |     42 |     40 |       19 |
| fastapi            | `call: module function (annotated)`          |     41 |     27 |       15 |
| fastapi            | `call: imported function`                    |     39 |     33 |       10 |
| fastapi            | `call: local.method()`                       |     28 |     20 |       16 |
| fastapi            | `call: param.method()`                       |     28 |     24 |       11 |
| fastapi            | `call: builtin getattr()`                    |     25 |     22 |       19 |
| fastapi            | `copy: local`                                |     18 |     18 |       12 |
| fastapi            | `attr: local.x`                              |     13 |     13 |        7 |
| fastapi            | `attr: self.x`                               |     12 |     11 |        6 |
| fastapi            | `dict (mixed/unknown elements)`              |     11 |      5 |        2 |
| fastapi            | `conditional`                                |     11 |     11 |        6 |
| fastapi            | `call: imported class`                       |     11 |     11 |       11 |
| fastapi            | `empty dict`                                 |      9 |      0 |        0 |
| fastapi            | `boolop (or)`                                |      9 |      7 |        4 |
| fastapi            | `DictComp (unknown elements)`                |      6 |      4 |        3 |
| fastapi            | `None literal`                               |      6 |      6 |        6 |
| fastapi            | `copy: param (annotated)`                    |      6 |      5 |        2 |
| fastapi            | `call: module.func()`                        |      6 |      6 |        5 |
| fastapi            | `call: self.method()`                        |      6 |      6 |        6 |
| fastapi            | `ListComp (unknown elements)`                |      5 |      4 |        1 |
| fastapi            | `attr: param.x`                              |      5 |      4 |        4 |
| fastapi            | `call: other callee`                         |      5 |      5 |        5 |
| fastapi            | `call: global.method()`                      |      5 |      3 |        2 |
| fastapi            | `call: builtin dict()`                       |      5 |      2 |        0 |
| fastapi            | `call: other.method()`                       |      4 |      3 |        2 |
| fastapi            | `await: call: module function (annotated)`   |      4 |      4 |        1 |
| fastapi            | `attr: modclass.x`                           |      4 |      0 |        0 |
| fastapi            | `tuple (mixed/unknown elements)`             |      3 |      3 |        0 |
| fastapi            | `attr: chained`                              |      3 |      3 |        1 |
| fastapi            | `call: builtin reversed()`                   |      3 |      2 |        0 |
| fastapi            | `binop (unknown operands)`                   |      3 |      3 |        2 |
| fastapi            | `list (mixed/unknown elements)`              |      3 |      3 |        2 |
| fastapi            | `await: call: other name`                    |      3 |      3 |        1 |
| fastapi            | `call: other name`                           |      3 |      3 |        2 |
| fastapi            | `copy: other`                                |      3 |      1 |        0 |
| fastapi            | `copy: imported`                             |      2 |      0 |        0 |
| fastapi            | `SetComp (unknown elements)`                 |      2 |      2 |        1 |
| fastapi            | `subscript: param[...]`                      |      2 |      1 |        0 |
| fastapi            | `call: builtin set()`                        |      2 |      2 |        2 |
| fastapi            | `empty list`                                 |      2 |      0 |        0 |
| fastapi            | `await: call: imported function`             |      2 |      2 |        1 |
| fastapi            | `call: local name`                           |      2 |      2 |        1 |
| fastapi            | `call: builtin tuple()`                      |      2 |      2 |        1 |
| fastapi            | `subscript: local[...]`                      |      2 |      2 |        2 |
| fastapi            | `copy: global`                               |      1 |      1 |        1 |
| fastapi            | `subscript: other`                           |      1 |      0 |        0 |
| fastapi            | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| fastapi            | `boolop (and)`                               |      1 |      1 |        0 |
| fastapi            | `await: call: param.method()`                |      1 |      1 |        1 |
| fastapi            | `await: call: other.method()`                |      1 |      1 |        1 |
| fastapi            | `await: call: local.method()`                |      1 |      0 |        0 |
| fastapi            | `call: builtin object()`                     |      1 |      0 |        0 |
| fastapi            | `other constant`                             |      1 |      0 |        0 |
| fastapi            | `call: imported.attr()`                      |      1 |      1 |        1 |
| fastapi            | `call: builtin type()`                       |      1 |      1 |        0 |
| fastapi            | `call: module class`                         |      1 |      0 |        0 |
| fastapi            | `compare`                                    |      1 |      1 |        1 |
| fastapi            | `attr: other.x`                              |      1 |      1 |        0 |
| cattrs             | `call: imported function`                    |     54 |     44 |       17 |
| cattrs             | `attr: local.x`                              |     20 |     19 |       12 |
| cattrs             | `empty dict`                                 |     20 |      0 |        0 |
| cattrs             | `copy: local`                                |     19 |     19 |       10 |
| cattrs             | `call: builtin getattr()`                    |     18 |     15 |        3 |
| cattrs             | `empty list`                                 |     18 |      0 |        0 |
| cattrs             | `call: chained .method()`                    |     15 |     13 |        8 |
| cattrs             | `attr: param.x`                              |     15 |     15 |        7 |
| cattrs             | `call: param.method()`                       |     12 |     10 |        9 |
| cattrs             | `copy: imported`                             |     11 |      3 |        3 |
| cattrs             | `conditional`                                |     10 |     10 |        5 |
| cattrs             | `attr: global.x`                             |      9 |      1 |        1 |
| cattrs             | `call: builtin set()`                        |      8 |      3 |        0 |
| cattrs             | `subscript: local[...]`                      |      8 |      6 |        5 |
| cattrs             | `call: local.method()`                       |      8 |      8 |        4 |
| cattrs             | `boolop (or)`                                |      7 |      6 |        2 |
| cattrs             | `SetComp (unknown elements)`                 |      7 |      7 |        3 |
| cattrs             | `copy: builtin`                              |      6 |      4 |        4 |
| cattrs             | `subscript: other`                           |      6 |      5 |        0 |
| cattrs             | `call: builtin zip()`                        |      6 |      6 |        3 |
| cattrs             | `subscript: param[...]`                      |      6 |      6 |        4 |
| cattrs             | `copy: param (annotated)`                    |      6 |      6 |        3 |
| cattrs             | `None literal`                               |      6 |      6 |        6 |
| cattrs             | `call: module function (annotated)`          |      6 |      6 |        2 |
| cattrs             | `attr: imported.x`                           |      5 |      4 |        0 |
| cattrs             | `attr: chained`                              |      5 |      5 |        5 |
| cattrs             | `DictComp (unknown elements)`                |      5 |      3 |        2 |
| cattrs             | `ListComp (unknown elements)`                |      5 |      4 |        3 |
| cattrs             | `call: other.method()`                       |      5 |      5 |        3 |
| cattrs             | `dict (mixed/unknown elements)`              |      5 |      5 |        0 |
| cattrs             | `call: builtin enumerate()`                  |      4 |      4 |        2 |
| cattrs             | `attr: self.x`                               |      4 |      4 |        1 |
| cattrs             | `binop (one side literal)`                   |      4 |      4 |        4 |
| cattrs             | `call: self.method()`                        |      3 |      2 |        1 |
| cattrs             | `call: local name`                           |      3 |      3 |        0 |
| cattrs             | `call: builtin tuple()`                      |      3 |      3 |        0 |
| cattrs             | `binop (unknown operands)`                   |      2 |      2 |        1 |
| cattrs             | `copy: param (unannotated)`                  |      2 |      2 |        0 |
| cattrs             | `call: builtin.method()`                     |      2 |      2 |        2 |
| cattrs             | `compare`                                    |      2 |      2 |        2 |
| cattrs             | `list (mixed/unknown elements)`              |      2 |      2 |        2 |
| cattrs             | `tuple (mixed/unknown elements)`             |      2 |      2 |        2 |
| cattrs             | `call: other name`                           |      2 |      2 |        2 |
| cattrs             | `subscript: imported[...]`                   |      2 |      2 |        2 |
| cattrs             | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| cattrs             | `call: builtin frozenset()`                  |      1 |      0 |        0 |
| cattrs             | `call: builtin type()`                       |      1 |      0 |        0 |
| cattrs             | `empty tuple`                                |      1 |      0 |        0 |
| cattrs             | `subscript: builtin[...]`                    |      1 |      1 |        1 |
| cattrs             | `boolop (and)`                               |      1 |      1 |        0 |
| cattrs             | `call: imported class`                       |      1 |      0 |        0 |
| cattrs             | `call: builtin sorted()`                     |      1 |      1 |        1 |
| cattrs             | `copy: moddef`                               |      1 |      0 |        0 |
| cattrs             | `call: builtin dict()`                       |      1 |      1 |        0 |
| cattrs             | `call: param name`                           |      1 |      1 |        0 |
| cattrs             | `call: other callee`                         |      1 |      1 |        0 |
| pytest             | `call: chained .method()`                    |    159 |    132 |      105 |
| pytest             | `call: self.method()`                        |     87 |     79 |       64 |
| pytest             | `attr: chained`                              |     68 |     56 |       50 |
| pytest             | `copy: local`                                |     62 |     48 |       39 |
| pytest             | `attr: param.x`                              |     61 |     55 |       42 |
| pytest             | `call: local.method()`                       |     57 |     46 |       40 |
| pytest             | `call: param.method()`                       |     53 |     46 |       41 |
| pytest             | `empty list`                                 |     52 |      0 |        0 |
| pytest             | `call: builtin getattr()`                    |     51 |     46 |       30 |
| pytest             | `call: module.func()`                        |     46 |     31 |       25 |
| pytest             | `attr: local.x`                              |     46 |     36 |       27 |
| pytest             | `subscript: other`                           |     44 |     31 |       20 |
| pytest             | `binop (unknown operands)`                   |     29 |     21 |       18 |
| pytest             | `attr: self.x`                               |     29 |     27 |       16 |
| pytest             | `None literal`                               |     27 |     21 |       21 |
| pytest             | `conditional`                                |     27 |     23 |       17 |
| pytest             | `tuple (mixed/unknown elements)`             |     25 |     23 |       19 |
| pytest             | `call: module function (annotated)`          |     24 |     23 |        9 |
| pytest             | `copy: param (annotated)`                    |     23 |     17 |       10 |
| pytest             | `other constant`                             |     22 |      5 |        5 |
| pytest             | `call: imported class`                       |     22 |      5 |        5 |
| pytest             | `boolop (or)`                                |     17 |     10 |        9 |
| pytest             | `call: other callee`                         |     17 |      4 |        4 |
| pytest             | `ListComp (unknown elements)`                |     16 |     12 |       10 |
| pytest             | `call: imported.attr()`                      |     15 |      9 |        8 |
| pytest             | `call: other name`                           |     14 |     12 |       10 |
| pytest             | `call: builtin list()`                       |     12 |     10 |        9 |
| pytest             | `call: module class`                         |     12 |     10 |       10 |
| pytest             | `call: builtin enumerate()`                  |     11 |      7 |        3 |
| pytest             | `call: imported function`                    |     11 |      9 |        7 |
| pytest             | `binop (one side literal)`                   |     10 |      7 |        7 |
| pytest             | `Yield`                                      |     10 |      7 |        7 |
| pytest             | `copy: other`                                |     10 |      1 |        1 |
| pytest             | `subscript: local[...]`                      |      9 |      7 |        5 |
| pytest             | `DictComp (unknown elements)`                |      9 |      6 |        3 |
| pytest             | `list (mixed/unknown elements)`              |      9 |      7 |        6 |
| pytest             | `call: builtin reversed()`                   |      9 |      7 |        5 |
| pytest             | `dict (mixed/unknown elements)`              |      8 |      4 |        4 |
| pytest             | `call: module function (unannotated)`        |      8 |      5 |        5 |
| pytest             | `call: builtin sorted()`                     |      8 |      7 |        7 |
| pytest             | `compare`                                    |      7 |      7 |        7 |
| pytest             | `unaryop USub`                               |      7 |      3 |        3 |
| pytest             | `attr: module.x`                             |      7 |      4 |        1 |
| pytest             | `subscript: global[...]`                     |      7 |      6 |        6 |
| pytest             | `subscript: param[...]`                      |      6 |      4 |        2 |
| pytest             | `-`                                          |      6 |      0 |        0 |
| pytest             | `copy: param (unannotated)`                  |      5 |      4 |        4 |
| pytest             | `empty dict`                                 |      5 |      0 |        0 |
| pytest             | `call: builtin dict()`                       |      4 |      3 |        3 |
| pytest             | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| pytest             | `call: builtin type()`                       |      4 |      2 |        0 |
| pytest             | `call: builtin zip()`                        |      4 |      4 |        3 |
| pytest             | `call: other.method()`                       |      4 |      4 |        3 |
| pytest             | `call: modclass.method()`                    |      4 |      4 |        4 |
| pytest             | `call: builtin.method()`                     |      4 |      2 |        1 |
| pytest             | `call: builtin max()`                        |      3 |      2 |        2 |
| pytest             | `copy: modclass`                             |      3 |      0 |        0 |
| pytest             | `call: builtin set()`                        |      3 |      2 |        0 |
| pytest             | `call: builtin compile()`                    |      3 |      3 |        3 |
| pytest             | `copy: self`                                 |      2 |      2 |        2 |
| pytest             | `call: builtin str()`                        |      2 |      2 |        2 |
| pytest             | `JoinedStr`                                  |      2 |      2 |        2 |
| pytest             | `boolop (and)`                               |      2 |      2 |        0 |
| pytest             | `call: cls.method()`                         |      2 |      2 |        2 |
| pytest             | `copy: imported`                             |      2 |      2 |        2 |
| pytest             | `call: global.method()`                      |      2 |      2 |        2 |
| pytest             | `call: builtin abs()`                        |      2 |      0 |        0 |
| pytest             | `call: builtin sum()`                        |      2 |      2 |        2 |
| pytest             | `call: builtin property()`                   |      1 |      0 |        0 |
| pytest             | `Lambda`                                     |      1 |      1 |        1 |
| pytest             | `call: builtin frozenset()`                  |      1 |      0 |        0 |
| pytest             | `call: builtin ascii()`                      |      1 |      0 |        0 |
| pytest             | `call: builtin repr()`                       |      1 |      1 |        1 |
| pytest             | `attr: global.x`                             |      1 |      0 |        0 |
| pytest             | `call: builtin open()`                       |      1 |      1 |        1 |
| pytest             | `call: global name`                          |      1 |      1 |        1 |
| pytest             | `SetComp (unknown elements)`                 |      1 |      1 |        0 |
| pytest             | `call: builtin object()`                     |      1 |      1 |        1 |
| pytest             | `copy: builtin`                              |      1 |      0 |        0 |
| pytest             | `call: builtin staticmethod()`               |      1 |      0 |        0 |
| pytest             | `call: param name`                           |      1 |      1 |        1 |
| pytest             | `subscript: other[...]`                      |      1 |      1 |        1 |
| pytest             | `call: builtin tuple()`                      |      1 |      0 |        0 |
| pytest             | `attr: modclass.x`                           |      1 |      0 |        0 |
| pytest             | `call: cls name`                             |      1 |      1 |        1 |
| pytest             | `call: local name`                           |      1 |      1 |        1 |
| pytest             | `call: builtin len()`                        |      1 |      1 |        1 |
| pytest             | `call: str-literal.method()`                 |      1 |      1 |        1 |
| pytest             | `call: builtin hasattr()`                    |      1 |      1 |        1 |
| pytest             | `call: builtin eval()`                       |      1 |      1 |        1 |
| pytest             | `call: builtin min()`                        |      1 |      0 |        0 |
| botocore           | `call: self.method()`                        |    373 |    329 |      214 |
| botocore           | `call: chained .method()`                    |    348 |    296 |      186 |
| botocore           | `call: param.method()`                       |    253 |    222 |      148 |
| botocore           | `call: local.method()`                       |    236 |    200 |      127 |
| botocore           | `copy: param (unannotated)`                  |    100 |     92 |       66 |
| botocore           | `subscript: other`                           |     97 |     78 |       63 |
| botocore           | `attr: param.x`                              |     86 |     81 |       42 |
| botocore           | `call: imported function`                    |     85 |     67 |       57 |
| botocore           | `subscript: local[...]`                      |     76 |     69 |       47 |
| botocore           | `empty dict`                                 |     76 |      0 |        0 |
| botocore           | `copy: local`                                |     71 |     66 |       50 |
| botocore           | `dict (mixed/unknown elements)`              |     70 |     36 |       27 |
| botocore           | `subscript: param[...]`                      |     65 |     53 |       32 |
| botocore           | `attr: self.x`                               |     60 |     57 |       31 |
| botocore           | `attr: chained`                              |     55 |     38 |       33 |
| botocore           | `empty list`                                 |     50 |      0 |        0 |
| botocore           | `call: module.func()`                        |     44 |     33 |       21 |
| botocore           | `call: module function (unannotated)`        |     33 |     26 |       19 |
| botocore           | `binop (unknown operands)`                   |     31 |     27 |       23 |
| botocore           | `None literal`                               |     29 |     20 |       20 |
| botocore           | `tuple (mixed/unknown elements)`             |     25 |     16 |       16 |
| botocore           | `attr: local.x`                              |     24 |     22 |       17 |
| botocore           | `list (mixed/unknown elements)`              |     23 |     16 |       14 |
| botocore           | `call: builtin getattr()`                    |     20 |     13 |        8 |
| botocore           | `ListComp (unknown elements)`                |     20 |     17 |       15 |
| botocore           | `boolop (or)`                                |     17 |     13 |        9 |
| botocore           | `call: global.method()`                      |     17 |     12 |       11 |
| botocore           | `call: local name`                           |     16 |     13 |        5 |
| botocore           | `call: imported.attr()`                      |     15 |     11 |       11 |
| botocore           | `other constant`                             |     14 |      4 |        4 |
| botocore           | `call: builtin enumerate()`                  |     13 |     11 |        6 |
| botocore           | `call: other.method()`                       |     13 |     11 |        9 |
| botocore           | `compare`                                    |     13 |      9 |        9 |
| botocore           | `boolop (and)`                               |     11 |      8 |        8 |
| botocore           | `call: builtin sorted()`                     |     10 |     10 |        9 |
| botocore           | `copy: modclass`                             |     10 |      0 |        0 |
| botocore           | `call: imported class`                       |     10 |      1 |        1 |
| botocore           | `copy: global`                               |      9 |      1 |        1 |
| botocore           | `call: modclass.method()`                    |      9 |      9 |        9 |
| botocore           | `copy: other`                                |      9 |      0 |        0 |
| botocore           | `binop (one side literal)`                   |      8 |      7 |        7 |
| botocore           | `call: builtin type()`                       |      8 |      7 |        2 |
| botocore           | `attr: module.x`                             |      8 |      1 |        1 |
| botocore           | `copy: imported`                             |      7 |      1 |        1 |
| botocore           | `conditional`                                |      6 |      4 |        2 |
| botocore           | `call: builtin iter()`                       |      6 |      5 |        5 |
| botocore           | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| botocore           | `call: builtin list()`                       |      5 |      3 |        3 |
| botocore           | `call: builtin zip()`                        |      5 |      5 |        2 |
| botocore           | `copy: builtin`                              |      5 |      0 |        0 |
| botocore           | `call: builtin next()`                       |      4 |      2 |        2 |
| botocore           | `call: module class`                         |      3 |      3 |        3 |
| botocore           | `call: param name`                           |      3 |      2 |        1 |
| botocore           | `call: builtin object()`                     |      3 |      0 |        0 |
| botocore           | `call: other name`                           |      3 |      1 |        0 |
| botocore           | `call: cls name`                             |      2 |      2 |        2 |
| botocore           | `call: other callee`                         |      2 |      2 |        0 |
| botocore           | `attr: imported.x`                           |      2 |      2 |        1 |
| botocore           | `JoinedStr`                                  |      2 |      1 |        1 |
| botocore           | `copy: self`                                 |      2 |      2 |        1 |
| botocore           | `call: builtin min()`                        |      2 |      2 |        1 |
| botocore           | `call: builtin dict()`                       |      1 |      1 |        0 |
| botocore           | `subscript: other[...]`                      |      1 |      1 |        1 |
| botocore           | `SetComp (unknown elements)`                 |      1 |      1 |        1 |
| botocore           | `attr: modclass.x`                           |      1 |      1 |        1 |
| botocore           | `subscript: global[...]`                     |      1 |      1 |        0 |
| botocore           | `call: builtin tuple()`                      |      1 |      0 |        0 |
| botocore           | `call: capitalised`                          |      1 |      1 |        1 |
| uvicorn            | `call: chained .method()`                    |     34 |     31 |       25 |
| uvicorn            | `call: param.method()`                       |     31 |     26 |       17 |
| uvicorn            | `binop (unknown operands)`                   |     24 |     17 |       14 |
| uvicorn            | `conditional`                                |      9 |      8 |        5 |
| uvicorn            | `subscript: param[...]`                      |      7 |      7 |        6 |
| uvicorn            | `copy: local`                                |      6 |      5 |        5 |
| uvicorn            | `dict (mixed/unknown elements)`              |      6 |      2 |        2 |
| uvicorn            | `call: self.method()`                        |      6 |      5 |        1 |
| uvicorn            | `call: local.method()`                       |      6 |      6 |        5 |
| uvicorn            | `attr: chained`                              |      6 |      6 |        6 |
| uvicorn            | `attr: local.x`                              |      6 |      6 |        6 |
| uvicorn            | `attr: self.x`                               |      6 |      5 |        4 |
| uvicorn            | `ListComp (unknown elements)`                |      6 |      3 |        3 |
| uvicorn            | `call: module.func()`                        |      5 |      0 |        0 |
| uvicorn            | `copy: imported`                             |      4 |      3 |        3 |
| uvicorn            | `await: call: param name`                    |      4 |      4 |        0 |
| uvicorn            | `boolop (or)`                                |      4 |      3 |        3 |
| uvicorn            | `await: call: self.method()`                 |      4 |      2 |        0 |
| uvicorn            | `call: imported function`                    |      3 |      3 |        3 |
| uvicorn            | `call: module function (annotated)`          |      3 |      3 |        1 |
| uvicorn            | `empty list`                                 |      3 |      0 |        0 |
| uvicorn            | `list (mixed/unknown elements)`              |      3 |      3 |        3 |
| uvicorn            | `attr: module.x`                             |      2 |      1 |        1 |
| uvicorn            | `subscript: global[...]`                     |      2 |      2 |        2 |
| uvicorn            | `call: builtin getattr()`                    |      2 |      2 |        2 |
| uvicorn            | `copy: param (annotated)`                    |      2 |      1 |        1 |
| uvicorn            | `call: builtin max()`                        |      2 |      2 |        2 |
| uvicorn            | `tuple (mixed/unknown elements)`             |      2 |      0 |        0 |
| uvicorn            | `DictComp (unknown elements)`                |      2 |      1 |        1 |
| uvicorn            | `copy: global`                               |      2 |      2 |        2 |
| uvicorn            | `subscript: builtin[...]`                    |      1 |      0 |        0 |
| uvicorn            | `call: builtin hasattr()`                    |      1 |      0 |        0 |
| uvicorn            | `await: call: other name`                    |      1 |      1 |        0 |
| uvicorn            | `other constant`                             |      1 |      1 |        1 |
| uvicorn            | `subscript: local[...]`                      |      1 |      1 |        1 |
| uvicorn            | `call: local name`                           |      1 |      1 |        0 |
| uvicorn            | `call: builtin bytearray()`                  |      1 |      1 |        1 |
| uvicorn            | `copy: self`                                 |      1 |      1 |        0 |
| uvicorn            | `call: builtin list()`                       |      1 |      1 |        1 |
| mcp                | `call: chained .method()`                    |     81 |     75 |       45 |
| mcp                | `call: other callee`                         |     50 |     44 |       44 |
| mcp                | `call: imported function`                    |     46 |     38 |       20 |
| mcp                | `call: param.method()`                       |     43 |     42 |       16 |
| mcp                | `call: module.func()`                        |     41 |     35 |       23 |
| mcp                | `conditional`                                |     41 |     39 |       18 |
| mcp                | `copy: local`                                |     37 |     31 |       22 |
| mcp                | `call: local.method()`                       |     36 |     31 |       11 |
| mcp                | `await: call: param.method()`                |     25 |     22 |       19 |
| mcp                | `call: imported class`                       |     23 |     11 |       11 |
| mcp                | `attr: param.x`                              |     20 |     20 |       10 |
| mcp                | `call: module function (annotated)`          |     20 |     19 |       10 |
| mcp                | `call: imported.attr()`                      |     17 |     17 |       14 |
| mcp                | `await: call: self.method()`                 |     16 |     16 |        7 |
| mcp                | `await: call: local.method()`                |     15 |     13 |       10 |
| mcp                | `attr: local.x`                              |     14 |     14 |        9 |
| mcp                | `boolop (or)`                                |     13 |     10 |        9 |
| mcp                | `attr: self.x`                               |     12 |     12 |        7 |
| mcp                | `attr: chained`                              |     12 |     12 |        6 |
| mcp                | `await: call: chained .method()`             |     12 |     12 |        5 |
| mcp                | `None literal`                               |     11 |      8 |        8 |
| mcp                | `call: self.method()`                        |     11 |      8 |        6 |
| mcp                | `tuple (mixed/unknown elements)`             |     11 |      8 |        6 |
| mcp                | `subscript: other`                           |     10 |      9 |        8 |
| mcp                | `call: builtin getattr()`                    |     10 |      7 |        3 |
| mcp                | `copy: param (annotated)`                    |     10 |      9 |        7 |
| mcp                | `ListComp (unknown elements)`                |     10 |      8 |        7 |
| mcp                | `Yield`                                      |     10 |      9 |        9 |
| mcp                | `dict (mixed/unknown elements)`              |     10 |      9 |        9 |
| mcp                | `copy: other`                                |      9 |      7 |        7 |
| mcp                | `call: global.method()`                      |      9 |      7 |        4 |
| mcp                | `call: module class`                         |      6 |      6 |        6 |
| mcp                | `await: call: param name`                    |      5 |      5 |        2 |
| mcp                | `call: other.method()`                       |      5 |      4 |        3 |
| mcp                | `binop (unknown operands)`                   |      5 |      2 |        1 |
| mcp                | `copy: imported`                             |      4 |      1 |        1 |
| mcp                | `boolop (and)`                               |      4 |      4 |        4 |
| mcp                | `subscript: local[...]`                      |      4 |      3 |        3 |
| mcp                | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| mcp                | `-`                                          |      4 |      0 |        0 |
| mcp                | `await: call: module function (annotated)`   |      4 |      4 |        1 |
| mcp                | `call: builtin next()`                       |      4 |      4 |        1 |
| mcp                | `call: builtin enumerate()`                  |      4 |      4 |        4 |
| mcp                | `list (mixed/unknown elements)`              |      3 |      3 |        3 |
| mcp                | `call: module function (unannotated)`        |      3 |      0 |        0 |
| mcp                | `await: call: other name`                    |      3 |      3 |        0 |
| mcp                | `call: modclass.method()`                    |      3 |      3 |        3 |
| mcp                | `await: call: local name`                    |      3 |      3 |        1 |
| mcp                | `copy: builtin`                              |      3 |      0 |        0 |
| mcp                | `binop (one side literal)`                   |      2 |      1 |        1 |
| mcp                | `other constant`                             |      2 |      0 |        0 |
| mcp                | `call: builtin tuple()`                      |      2 |      1 |        0 |
| mcp                | `subscript: imported[...]`                   |      2 |      2 |        2 |
| mcp                | `attr: other.x`                              |      2 |      2 |        1 |
| mcp                | `await: call: module.func()`                 |      2 |      0 |        0 |
| mcp                | `await: call: imported function`             |      2 |      2 |        1 |
| mcp                | `call: builtin dict()`                       |      2 |      1 |        1 |
| mcp                | `call: builtin reversed()`                   |      2 |      2 |        0 |
| mcp                | `DictComp (unknown elements)`                |      2 |      1 |        1 |
| mcp                | `call: builtin object()`                     |      2 |      1 |        1 |
| mcp                | `empty dict`                                 |      1 |      0 |        0 |
| mcp                | `set (mixed/unknown elements)`               |      1 |      1 |        1 |
| mcp                | `call: param name`                           |      1 |      1 |        1 |
| mcp                | `await: copy: param (annotated)`             |      1 |      1 |        1 |
| mcp                | `copy: global`                               |      1 |      0 |        0 |
| mcp                | `call: builtin set()`                        |      1 |      1 |        1 |
| mcp                | `call: other name`                           |      1 |      1 |        0 |
| mcp                | `call: builtin sorted()`                     |      1 |      0 |        0 |
| mcp                | `compare`                                    |      1 |      1 |        1 |
| mcp                | `await: call: other.method()`                |      1 |      1 |        0 |
| mcp                | `call: builtin frozenset()`                  |      1 |      1 |        1 |
| mcp                | `subscript: param[...]`                      |      1 |      0 |        0 |
| pdm                | `call: chained .method()`                    |    175 |    144 |      119 |
| pdm                | `call: local.method()`                       |    123 |     99 |       85 |
| pdm                | `attr: chained`                              |     72 |     59 |       45 |
| pdm                | `call: param.method()`                       |     69 |     59 |       44 |
| pdm                | `call: module.func()`                        |     60 |     40 |       37 |
| pdm                | `conditional`                                |     57 |     50 |       31 |
| pdm                | `call: imported function`                    |     56 |     50 |       48 |
| pdm                | `tuple (mixed/unknown elements)`             |     41 |     12 |        8 |
| pdm                | `copy: local`                                |     40 |     35 |       27 |
| pdm                | `attr: param.x`                              |     37 |     31 |       23 |
| pdm                | `call: imported.attr()`                      |     35 |     32 |       27 |
| pdm                | `attr: local.x`                              |     34 |     28 |       13 |
| pdm                | `boolop (or)`                                |     33 |     30 |       25 |
| pdm                | `subscript: other`                           |     30 |     24 |       22 |
| pdm                | `ListComp (unknown elements)`                |     20 |     14 |       12 |
| pdm                | `attr: self.x`                               |     20 |     17 |        7 |
| pdm                | `call: builtin list()`                       |     19 |     13 |       11 |
| pdm                | `call: builtin sorted()`                     |     19 |     14 |       13 |
| pdm                | `dict (mixed/unknown elements)`              |     19 |     11 |       10 |
| pdm                | `other constant`                             |     18 |      4 |        4 |
| pdm                | `binop (unknown operands)`                   |     17 |     10 |        9 |
| pdm                | `copy: param (annotated)`                    |     16 |     13 |        4 |
| pdm                | `list (mixed/unknown elements)`              |     15 |     12 |       12 |
| pdm                | `call: self.method()`                        |     15 |     14 |       11 |
| pdm                | `call: builtin next()`                       |     14 |     12 |        9 |
| pdm                | `call: module function (annotated)`          |     14 |     11 |        9 |
| pdm                | `empty dict`                                 |     13 |      0 |        0 |
| pdm                | `empty list`                                 |     13 |      0 |        0 |
| pdm                | `DictComp (unknown elements)`                |     13 |      9 |        8 |
| pdm                | `call: cls.method()`                         |     12 |     12 |        0 |
| pdm                | `call: imported class`                       |     10 |      5 |        5 |
| pdm                | `subscript: local[...]`                      |      9 |      7 |        7 |
| pdm                | `call: other name`                           |      9 |      6 |        5 |
| pdm                | `binop (one side literal)`                   |      8 |      8 |        8 |
| pdm                | `call: builtin getattr()`                    |      7 |      7 |        5 |
| pdm                | `call: builtin zip()`                        |      7 |      3 |        3 |
| pdm                | `call: builtin enumerate()`                  |      6 |      6 |        5 |
| pdm                | `call: module function (unannotated)`        |      5 |      2 |        2 |
| pdm                | `None literal`                               |      5 |      3 |        3 |
| pdm                | `call: builtin set()`                        |      4 |      2 |        1 |
| pdm                | `compare`                                    |      4 |      3 |        3 |
| pdm                | `subscript: param[...]`                      |      4 |      2 |        2 |
| pdm                | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| pdm                | `call: builtin frozenset()`                  |      4 |      2 |        2 |
| pdm                | `call: moddef.method()`                      |      4 |      0 |        0 |
| pdm                | `boolop (and)`                               |      3 |      3 |        1 |
| pdm                | `call: local name`                           |      3 |      3 |        1 |
| pdm                | `call: other.method()`                       |      3 |      2 |        2 |
| pdm                | `empty tuple`                                |      2 |      0 |        0 |
| pdm                | `copy: imported`                             |      2 |      1 |        1 |
| pdm                | `call: builtin iter()`                       |      2 |      2 |        2 |
| pdm                | `call: other callee`                         |      2 |      2 |        1 |
| pdm                | `call: builtin dict()`                       |      2 |      2 |        2 |
| pdm                | `call: builtin min()`                        |      2 |      2 |        2 |
| pdm                | `call: builtin object()`                     |      2 |      1 |        1 |
| pdm                | `call: global.method()`                      |      2 |      2 |        2 |
| pdm                | `call: str-literal.method()`                 |      2 |      2 |        2 |
| pdm                | `call: module class`                         |      2 |      2 |        2 |
| pdm                | `JoinedStr`                                  |      1 |      1 |        1 |
| pdm                | `call: builtin max()`                        |      1 |      1 |        1 |
| pdm                | `copy: global`                               |      1 |      1 |        1 |
| pdm                | `call: builtin filter()`                     |      1 |      1 |        1 |
| pdm                | `subscript: imported[...]`                   |      1 |      0 |        0 |
| pdm                | `attr: other.x`                              |      1 |      0 |        0 |
| pdm                | `call: builtin open()`                       |      1 |      0 |        0 |
| pdm                | `set (mixed/unknown elements)`               |      1 |      1 |        1 |
| pdm                | `call: builtin reversed()`                   |      1 |      1 |        1 |
| pdm                | `attr: imported.x`                           |      1 |      0 |        0 |
| strawberry-graphql | `call: chained .method()`                    |     89 |     64 |       41 |
| strawberry-graphql | `call: imported function`                    |     64 |     48 |       13 |
| strawberry-graphql | `attr: chained`                              |     58 |     45 |       33 |
| strawberry-graphql | `call: self.method()`                        |     53 |     20 |       15 |
| strawberry-graphql | `attr: param.x`                              |     51 |     43 |       29 |
| strawberry-graphql | `call: builtin getattr()`                    |     43 |     31 |       14 |
| strawberry-graphql | `attr: local.x`                              |     42 |     35 |       21 |
| strawberry-graphql | `conditional`                                |     41 |     33 |       10 |
| strawberry-graphql | `call: local.method()`                       |     40 |     24 |       11 |
| strawberry-graphql | `subscript: other`                           |     36 |     23 |       19 |
| strawberry-graphql | `copy: local`                                |     29 |     20 |       14 |
| strawberry-graphql | `call: module function (annotated)`          |     24 |     17 |        2 |
| strawberry-graphql | `call: module.func()`                        |     23 |     17 |       11 |
| strawberry-graphql | `ListComp (unknown elements)`                |     22 |     12 |        7 |
| strawberry-graphql | `call: param.method()`                       |     21 |     11 |        4 |
| strawberry-graphql | `empty list`                                 |     19 |      0 |        0 |
| strawberry-graphql | `copy: imported`                             |     16 |      1 |        1 |
| strawberry-graphql | `attr: self.x`                               |     14 |     12 |        4 |
| strawberry-graphql | `tuple (mixed/unknown elements)`             |     14 |      5 |        3 |
| strawberry-graphql | `boolop (or)`                                |     14 |     12 |        9 |
| strawberry-graphql | `copy: param (annotated)`                    |     14 |      8 |        4 |
| strawberry-graphql | `empty dict`                                 |     13 |      0 |        0 |
| strawberry-graphql | `await: call: self.method()`                 |     12 |      0 |        0 |
| strawberry-graphql | `call: param name`                           |     12 |      9 |        6 |
| strawberry-graphql | `None literal`                               |     12 |     12 |       12 |
| strawberry-graphql | `subscript: local[...]`                      |     11 |      4 |        3 |
| strawberry-graphql | `DictComp (unknown elements)`                |     11 |      8 |        5 |
| strawberry-graphql | `GeneratorExp (unknown elements)`            |     10 |     10 |       10 |
| strawberry-graphql | `binop (unknown operands)`                   |      9 |      4 |        3 |
| strawberry-graphql | `dict (mixed/unknown elements)`              |      9 |      2 |        2 |
| strawberry-graphql | `call: builtin list()`                       |      9 |      5 |        3 |
| strawberry-graphql | `other constant`                             |      8 |      1 |        1 |
| strawberry-graphql | `copy: modclass`                             |      8 |      0 |        0 |
| strawberry-graphql | `await: call: chained .method()`             |      8 |      0 |        0 |
| strawberry-graphql | `call: imported class`                       |      8 |      5 |        5 |
| strawberry-graphql | `call: builtin sorted()`                     |      8 |      3 |        1 |
| strawberry-graphql | `call: builtin enumerate()`                  |      8 |      8 |        6 |
| strawberry-graphql | `call: other name`                           |      8 |      6 |        3 |
| strawberry-graphql | `subscript: param[...]`                      |      6 |      2 |        1 |
| strawberry-graphql | `attr: module.x`                             |      6 |      0 |        0 |
| strawberry-graphql | `SetComp (unknown elements)`                 |      6 |      5 |        5 |
| strawberry-graphql | `call: builtin tuple()`                      |      5 |      5 |        1 |
| strawberry-graphql | `await: call: imported function`             |      5 |      5 |        2 |
| strawberry-graphql | `boolop (and)`                               |      4 |      4 |        4 |
| strawberry-graphql | `call: local name`                           |      3 |      2 |        1 |
| strawberry-graphql | `call: other callee`                         |      3 |      2 |        2 |
| strawberry-graphql | `call: builtin type()`                       |      3 |      3 |        1 |
| strawberry-graphql | `call: builtin zip()`                        |      3 |      3 |        1 |
| strawberry-graphql | `copy: other`                                |      3 |      2 |        0 |
| strawberry-graphql | `call: builtin next()`                       |      3 |      1 |        0 |
| strawberry-graphql | `await: call: local.method()`                |      2 |      1 |        1 |
| strawberry-graphql | `call: builtin object()`                     |      2 |      0 |        0 |
| strawberry-graphql | `subscript: imported[...]`                   |      2 |      1 |        0 |
| strawberry-graphql | `binop (one side literal)`                   |      2 |      2 |        2 |
| strawberry-graphql | `await: call: other.method()`                |      2 |      0 |        0 |
| strawberry-graphql | `copy: moddef`                               |      2 |      0 |        0 |
| strawberry-graphql | `call: global.method()`                      |      2 |      2 |        2 |
| strawberry-graphql | `attr: cls.x`                                |      2 |      2 |        0 |
| strawberry-graphql | `compare`                                    |      2 |      1 |        1 |
| strawberry-graphql | `call: builtin eval()`                       |      2 |      1 |        1 |
| strawberry-graphql | `await: copy: local`                         |      1 |      0 |        0 |
| strawberry-graphql | `list (mixed/unknown elements)`              |      1 |      0 |        0 |
| strawberry-graphql | `call: builtin min()`                        |      1 |      0 |        0 |
| strawberry-graphql | `JoinedStr`                                  |      1 |      1 |        1 |
| strawberry-graphql | `call: str-literal.method()`                 |      1 |      1 |        1 |
| strawberry-graphql | `await: call: param.method()`                |      1 |      1 |        0 |
| strawberry-graphql | `call: builtin frozenset()`                  |      1 |      0 |        0 |
| strawberry-graphql | `call: builtin set()`                        |      1 |      0 |        0 |
| strawberry-graphql | `attr: other.x`                              |      1 |      0 |        0 |
| strawberry-graphql | `call: cls.method()`                         |      1 |      1 |        0 |
| strawberry-graphql | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| strawberry-graphql | `call: module class`                         |      1 |      0 |        0 |
| strawberry-graphql | `call: builtin dict()`                       |      1 |      1 |        0 |
| strawberry-graphql | `copy: cls`                                  |      1 |      1 |        0 |
| strawberry-graphql | `copy: self`                                 |      1 |      1 |        1 |
| strawberry-graphql | `attr: imported.x`                           |      1 |      0 |        0 |
| pygments           | `other constant`                             |  2,314 |      0 |        0 |
| pygments           | `list (mixed/unknown elements)`              |  1,586 |      6 |        6 |
| pygments           | `dict (mixed/unknown elements)`              |    563 |      2 |        2 |
| pygments           | `tuple (mixed/unknown elements)`             |    352 |     11 |       10 |
| pygments           | `empty list`                                 |    161 |      0 |        0 |
| pygments           | `binop (unknown operands)`                   |    128 |      9 |        9 |
| pygments           | `binop (one side literal)`                   |    114 |     25 |       25 |
| pygments           | `call: imported.attr()`                      |    109 |    100 |       98 |
| pygments           | `copy: param (unannotated)`                  |     97 |     88 |       88 |
| pygments           | `call: local.method()`                       |     94 |     72 |       67 |
| pygments           | `call: imported function`                    |     91 |     24 |       19 |
| pygments           | `call: param.method()`                       |     82 |     79 |       75 |
| pygments           | `JoinedStr`                                  |     78 |      0 |        0 |
| pygments           | `call: chained .method()`                    |     72 |     58 |       42 |
| pygments           | `set (mixed/unknown elements)`               |     65 |      0 |        0 |
| pygments           | `attr: module.x`                             |     64 |      0 |        0 |
| pygments           | `copy: local`                                |     61 |     46 |       42 |
| pygments           | `call: module.func()`                        |     54 |      8 |        8 |
| pygments           | `call: self.method()`                        |     52 |     42 |       37 |
| pygments           | `attr: self.x`                               |     42 |     35 |       24 |
| pygments           | `call: builtin set()`                        |     39 |      0 |        0 |
| pygments           | `empty dict`                                 |     38 |      0 |        0 |
| pygments           | `None literal`                               |     31 |     17 |       17 |
| pygments           | `subscript: local[...]`                      |     29 |     23 |       23 |
| pygments           | `copy: global`                               |     27 |      1 |        1 |
| pygments           | `call: module function (unannotated)`        |     23 |     15 |       10 |
| pygments           | `call: other name`                           |     23 |      3 |        1 |
| pygments           | `subscript: other`                           |     19 |     13 |       13 |
| pygments           | `call: str-literal.method()`                 |     19 |      0 |        0 |
| pygments           | `subscript: global[...]`                     |     17 |      5 |        3 |
| pygments           | `copy: modclass`                             |     17 |      2 |        2 |
| pygments           | `attr: imported.x`                           |     16 |      3 |        3 |
| pygments           | `call: modclass.method()`                    |     16 |     16 |       16 |
| pygments           | `attr: chained`                              |     15 |      8 |        8 |
| pygments           | `attr: param.x`                              |     14 |     14 |       11 |
| pygments           | `attr: global.x`                             |     14 |      0 |        0 |
| pygments           | `call: builtin sorted()`                     |     13 |      3 |        3 |
| pygments           | `call: builtin enumerate()`                  |     13 |      9 |        9 |
| pygments           | `empty tuple`                                |     13 |      0 |        0 |
| pygments           | `boolop (or)`                                |     11 |      8 |        8 |
| pygments           | `call: other.method()`                       |     10 |      5 |        5 |
| pygments           | `attr: local.x`                              |      9 |      4 |        4 |
| pygments           | `call: global.method()`                      |      9 |      3 |        1 |
| pygments           | `subscript: param[...]`                      |      8 |      7 |        6 |
| pygments           | `copy: other`                                |      8 |      2 |        2 |
| pygments           | `copy: imported`                             |      8 |      2 |        2 |
| pygments           | `conditional`                                |      7 |      6 |        6 |
| pygments           | `call: builtin getattr()`                    |      6 |      3 |        1 |
| pygments           | `ListComp (unknown elements)`                |      5 |      3 |        3 |
| pygments           | `DictComp (unknown elements)`                |      5 |      0 |        0 |
| pygments           | `call: builtin __import__()`                 |      4 |      2 |        2 |
| pygments           | `call: builtin list()`                       |      4 |      3 |        3 |
| pygments           | `call: local name`                           |      4 |      3 |        2 |
| pygments           | `attr: modclass.x`                           |      4 |      0 |        0 |
| pygments           | `attr: cls.x`                                |      3 |      3 |        2 |
| pygments           | `call: cls.method()`                         |      3 |      2 |        1 |
| pygments           | `boolop (and)`                               |      2 |      2 |        2 |
| pygments           | `call: builtin dict()`                       |      2 |      0 |        0 |
| pygments           | `call: builtin next()`                       |      2 |      2 |        2 |
| pygments           | `call: builtin max()`                        |      2 |      1 |        1 |
| pygments           | `call: builtin zip()`                        |      2 |      0 |        0 |
| pygments           | `call: builtin open()`                       |      1 |      1 |        1 |
| pygments           | `call: imported class`                       |      1 |      0 |        0 |
| pygments           | `subscript: imported[...]`                   |      1 |      1 |        1 |
| pygments           | `call: builtin staticmethod()`               |      1 |      0 |        0 |
| pygments           | `call: module class`                         |      1 |      1 |        1 |
| pygments           | `call: builtin sum()`                        |      1 |      0 |        0 |
| pygments           | `SetComp (unknown elements)`                 |      1 |      0 |        0 |
| pygments           | `call: builtin tuple()`                      |      1 |      0 |        0 |
| pygments           | `call: builtin min()`                        |      1 |      1 |        1 |
| pygments           | `call: builtin.method()`                     |      1 |      1 |        0 |
| streamlink         | `call: chained .method()`                    |    482 |     67 |       56 |
| streamlink         | `other constant`                             |    211 |      6 |        6 |
| streamlink         | `copy: local`                                |    198 |     27 |       23 |
| streamlink         | `call: self.method()`                        |    191 |     41 |       37 |
| streamlink         | `call: local.method()`                       |    118 |     31 |       27 |
| streamlink         | `Yield`                                      |    118 |      6 |        5 |
| streamlink         | `call: imported function`                    |     74 |     41 |       38 |
| streamlink         | `call: imported.attr()`                      |     74 |      8 |        8 |
| streamlink         | `call: module.func()`                        |     66 |     14 |       13 |
| streamlink         | `dict (mixed/unknown elements)`              |     51 |      2 |        2 |
| streamlink         | `call: param.method()`                       |     38 |     23 |        7 |
| streamlink         | `boolop (or)`                                |     37 |     19 |       17 |
| streamlink         | `subscript: other`                           |     36 |      6 |        3 |
| streamlink         | `subscript: local[...]`                      |     32 |      6 |        5 |
| streamlink         | `attr: chained`                              |     29 |     17 |       16 |
| streamlink         | `tuple (mixed/unknown elements)`             |     24 |     18 |       16 |
| streamlink         | `copy: param (unannotated)`                  |     20 |      6 |        5 |
| streamlink         | `attr: self.x`                               |     19 |     11 |       10 |
| streamlink         | `empty dict`                                 |     17 |      0 |        0 |
| streamlink         | `attr: param.x`                              |     17 |     14 |        7 |
| streamlink         | `binop (unknown operands)`                   |     15 |     15 |       12 |
| streamlink         | `conditional`                                |     15 |     11 |        5 |
| streamlink         | `None literal`                               |     13 |      3 |        3 |
| streamlink         | `call: builtin next()`                       |     13 |      1 |        0 |
| streamlink         | `binop (one side literal)`                   |     12 |      2 |        2 |
| streamlink         | `list (mixed/unknown elements)`              |     11 |      3 |        3 |
| streamlink         | `empty list`                                 |     11 |      0 |        0 |
| streamlink         | `await: call: chained .method()`             |     10 |     10 |        8 |
| streamlink         | `boolop (and)`                               |      9 |      0 |        0 |
| streamlink         | `attr: local.x`                              |      8 |      7 |        7 |
| streamlink         | `call: builtin sorted()`                     |      8 |      2 |        1 |
| streamlink         | `call: builtin getattr()`                    |      8 |      8 |        5 |
| streamlink         | `call: other callee`                         |      7 |      2 |        1 |
| streamlink         | `ListComp (unknown elements)`                |      6 |      3 |        1 |
| streamlink         | `call: builtin dict()`                       |      6 |      2 |        2 |
| streamlink         | `DictComp (unknown elements)`                |      5 |      0 |        0 |
| streamlink         | `call: imported class`                       |      5 |      3 |        3 |
| streamlink         | `call: other.method()`                       |      5 |      5 |        3 |
| streamlink         | `call: cls.method()`                         |      5 |      5 |        4 |
| streamlink         | `call: modclass.method()`                    |      4 |      1 |        1 |
| streamlink         | `call: builtin list()`                       |      4 |      3 |        3 |
| streamlink         | `call: builtin enumerate()`                  |      4 |      2 |        1 |
| streamlink         | `call: module function (unannotated)`        |      4 |      2 |        0 |
| streamlink         | `call: builtin type()`                       |      4 |      4 |        1 |
| streamlink         | `subscript: other[...]`                      |      3 |      3 |        0 |
| streamlink         | `set (mixed/unknown elements)`               |      3 |      2 |        2 |
| streamlink         | `call: local name`                           |      3 |      2 |        1 |
| streamlink         | `call: builtin set()`                        |      3 |      0 |        0 |
| streamlink         | `attr: module.x`                             |      2 |      0 |        0 |
| streamlink         | `attr: global.x`                             |      2 |      0 |        0 |
| streamlink         | `call: global.method()`                      |      2 |      0 |        0 |
| streamlink         | `attr: cls.x`                                |      2 |      2 |        2 |
| streamlink         | `call: builtin max()`                        |      2 |      2 |        2 |
| streamlink         | `attr: other.x`                              |      2 |      1 |        0 |
| streamlink         | `JoinedStr`                                  |      2 |      0 |        0 |
| streamlink         | `call: module class`                         |      2 |      1 |        1 |
| streamlink         | `call: param name`                           |      2 |      2 |        1 |
| streamlink         | `call: builtin reversed()`                   |      2 |      2 |        2 |
| streamlink         | `call: builtin divmod()`                     |      2 |      2 |        0 |
| streamlink         | `await: call: self.method()`                 |      2 |      2 |        2 |
| streamlink         | `call: builtin len()`                        |      1 |      1 |        1 |
| streamlink         | `call: builtin min()`                        |      1 |      1 |        1 |
| streamlink         | `copy: param (annotated)`                    |      1 |      1 |        1 |
| streamlink         | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| streamlink         | `-`                                          |      1 |      0 |        0 |
| streamlink         | `unaryop USub`                               |      1 |      0 |        0 |
| streamlink         | `call: str-literal.method()`                 |      1 |      0 |        0 |
| streamlink         | `call: other name`                           |      1 |      0 |        0 |
| streamlink         | `compare`                                    |      1 |      1 |        1 |
| streamlink         | `call: builtin super()`                      |      1 |      1 |        1 |
| streamlink         | `attr: modclass.x`                           |      1 |      1 |        1 |
| streamlink         | `call: builtin filter()`                     |      1 |      1 |        1 |
| streamlink         | `copy: other`                                |      1 |      1 |        1 |
| streamlink         | `await: call: param.method()`                |      1 |      1 |        1 |
| streamlink         | `await: call: module.func()`                 |      1 |      0 |        0 |
| streamlink         | `attr: imported.x`                           |      1 |      0 |        0 |
| streamlink         | `call: cls name`                             |      1 |      1 |        1 |
| sphinx             | `call: chained .method()`                    |    452 |    341 |      269 |
| sphinx             | `other constant`                             |    357 |      5 |        5 |
| sphinx             | `call: imported function`                    |    242 |    112 |       92 |
| sphinx             | `call: local.method()`                       |    233 |    163 |      135 |
| sphinx             | `call: imported.attr()`                      |    193 |     77 |       66 |
| sphinx             | `attr: chained`                              |    182 |    140 |      126 |
| sphinx             | `copy: local`                                |    177 |    141 |      122 |
| sphinx             | `call: param.method()`                       |    123 |    103 |       69 |
| sphinx             | `subscript: other`                           |    110 |     85 |       73 |
| sphinx             | `empty list`                                 |    105 |      0 |        0 |
| sphinx             | `binop (unknown operands)`                   |    104 |     68 |       67 |
| sphinx             | `list (mixed/unknown elements)`              |     90 |     51 |       51 |
| sphinx             | `attr: self.x`                               |     83 |     65 |       63 |
| sphinx             | `subscript: local[...]`                      |     76 |     61 |       58 |
| sphinx             | `attr: local.x`                              |     73 |     63 |       48 |
| sphinx             | `attr: param.x`                              |     71 |     51 |       38 |
| sphinx             | `call: self.method()`                        |     70 |     45 |       34 |
| sphinx             | `copy: other`                                |     69 |      2 |        2 |
| sphinx             | `tuple (mixed/unknown elements)`             |     69 |     28 |       23 |
| sphinx             | `subscript: param[...]`                      |     66 |     59 |       55 |
| sphinx             | `dict (mixed/unknown elements)`              |     64 |     19 |       17 |
| sphinx             | `call: module.func()`                        |     61 |     50 |       47 |
| sphinx             | `call: builtin list()`                       |     55 |     37 |       35 |
| sphinx             | `binop (one side literal)`                   |     42 |     30 |       30 |
| sphinx             | `call: builtin getattr()`                    |     42 |     30 |       13 |
| sphinx             | `None literal`                               |     42 |     32 |       32 |
| sphinx             | `call: module function (annotated)`          |     42 |     36 |       14 |
| sphinx             | `boolop (or)`                                |     37 |     28 |       25 |
| sphinx             | `copy: imported`                             |     34 |      9 |        8 |
| sphinx             | `ListComp (unknown elements)`                |     32 |     24 |       22 |
| sphinx             | `copy: param (annotated)`                    |     29 |     21 |       11 |
| sphinx             | `conditional`                                |     29 |     25 |       20 |
| sphinx             | `call: other name`                           |     24 |     17 |        9 |
| sphinx             | `call: param name`                           |     24 |     20 |       18 |
| sphinx             | `empty dict`                                 |     21 |      0 |        0 |
| sphinx             | `call: imported class`                       |     19 |     17 |       17 |
| sphinx             | `attr: imported.x`                           |     18 |      5 |        5 |
| sphinx             | `call: builtin sorted()`                     |     17 |     16 |       14 |
| sphinx             | `call: local name`                           |     17 |      9 |        9 |
| sphinx             | `call: global.method()`                      |     15 |     13 |       10 |
| sphinx             | `call: builtin enumerate()`                  |     13 |     10 |        7 |
| sphinx             | `copy: global`                               |     13 |      3 |        3 |
| sphinx             | `call: builtin object()`                     |     13 |      5 |        5 |
| sphinx             | `call: builtin set()`                        |     12 |      4 |        4 |
| sphinx             | `compare`                                    |     12 |     10 |       10 |
| sphinx             | `DictComp (unknown elements)`                |     12 |      8 |        8 |
| sphinx             | `call: builtin zip()`                        |     12 |      7 |        7 |
| sphinx             | `call: builtin frozenset()`                  |     12 |      6 |        6 |
| sphinx             | `boolop (and)`                               |     11 |     10 |       10 |
| sphinx             | `GeneratorExp (unknown elements)`            |      9 |      8 |        8 |
| sphinx             | `subscript: imported[...]`                   |      9 |      6 |        6 |
| sphinx             | `call: module class`                         |      8 |      6 |        6 |
| sphinx             | `subscript: global[...]`                     |      7 |      4 |        4 |
| sphinx             | `call: builtin reversed()`                   |      6 |      1 |        0 |
| sphinx             | `JoinedStr`                                  |      6 |      3 |        3 |
| sphinx             | `subscript: self[...]`                       |      5 |      5 |        4 |
| sphinx             | `copy: modclass`                             |      5 |      0 |        0 |
| sphinx             | `attr: cls.x`                                |      5 |      3 |        1 |
| sphinx             | `call: builtin next()`                       |      5 |      3 |        1 |
| sphinx             | `call: builtin type()`                       |      5 |      4 |        2 |
| sphinx             | `call: builtin dict()`                       |      5 |      3 |        2 |
| sphinx             | `call: other.method()`                       |      5 |      5 |        3 |
| sphinx             | `call: builtin tuple()`                      |      5 |      3 |        3 |
| sphinx             | `SetComp (unknown elements)`                 |      4 |      3 |        3 |
| sphinx             | `attr: module.x`                             |      4 |      2 |        2 |
| sphinx             | `attr: modclass.x`                           |      4 |      4 |        2 |
| sphinx             | `set (mixed/unknown elements)`               |      3 |      2 |        2 |
| sphinx             | `call: str-literal.method()`                 |      3 |      2 |        2 |
| sphinx             | `call: builtin max()`                        |      2 |      2 |        2 |
| sphinx             | `call: builtin divmod()`                     |      2 |      2 |        2 |
| sphinx             | `unaryop USub`                               |      2 |      0 |        0 |
| sphinx             | `call: builtin eval()`                       |      2 |      1 |        1 |
| sphinx             | `copy: builtin`                              |      2 |      0 |        0 |
| sphinx             | `call: builtin round()`                      |      1 |      0 |        0 |
| sphinx             | `call: builtin vars()`                       |      1 |      1 |        1 |
| sphinx             | `call: builtin compile()`                    |      1 |      1 |        1 |
| sphinx             | `call: builtin filter()`                     |      1 |      1 |        1 |
| sphinx             | `call: builtin dir()`                        |      1 |      1 |        1 |
| sphinx             | `copy: moddef`                               |      1 |      1 |        1 |
| sphinx             | `call: cls.method()`                         |      1 |      0 |        0 |
| sphinx             | `call: other callee`                         |      1 |      1 |        0 |
| sphinx             | `call: builtin map()`                        |      1 |      1 |        1 |
| sphinx             | `call: builtin bool()`                       |      1 |      1 |        1 |
| tox                | `call: chained .method()`                    |    135 |    117 |       94 |
| tox                | `call: param.method()`                       |     45 |     41 |       27 |
| tox                | `call: local.method()`                       |     45 |     37 |       29 |
| tox                | `tuple (mixed/unknown elements)`             |     31 |     22 |       17 |
| tox                | `conditional`                                |     30 |     27 |       22 |
| tox                | `subscript: other`                           |     27 |     22 |       21 |
| tox                | `attr: chained`                              |     27 |     23 |       22 |
| tox                | `call: imported function`                    |     25 |     20 |       17 |
| tox                | `copy: local`                                |     25 |     21 |       19 |
| tox                | `call: builtin getattr()`                    |     22 |     17 |       13 |
| tox                | `call: self.method()`                        |     20 |     19 |       13 |
| tox                | `call: module.func()`                        |     17 |     12 |        6 |
| tox                | `attr: self.x`                               |     16 |     15 |        6 |
| tox                | `copy: param (annotated)`                    |     16 |     14 |        8 |
| tox                | `boolop (or)`                                |     14 |     13 |        9 |
| tox                | `call: builtin set()`                        |     13 |     10 |       10 |
| tox                | `attr: local.x`                              |     13 |     12 |       11 |
| tox                | `ListComp (unknown elements)`                |     11 |      8 |        8 |
| tox                | `call: imported class`                       |     10 |      7 |        7 |
| tox                | `subscript: local[...]`                      |     10 |      9 |        4 |
| tox                | `dict (mixed/unknown elements)`              |      8 |      5 |        5 |
| tox                | `empty list`                                 |      6 |      0 |        0 |
| tox                | `call: builtin list()`                       |      6 |      5 |        5 |
| tox                | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| tox                | `attr: imported.x`                           |      6 |      4 |        4 |
| tox                | `binop (unknown operands)`                   |      6 |      6 |        6 |
| tox                | `call: builtin sorted()`                     |      5 |      4 |        4 |
| tox                | `attr: param.x`                              |      5 |      5 |        5 |
| tox                | `binop (one side literal)`                   |      5 |      5 |        5 |
| tox                | `attr: module.x`                             |      5 |      1 |        1 |
| tox                | `call: global.method()`                      |      4 |      2 |        1 |
| tox                | `call: builtin enumerate()`                  |      4 |      3 |        1 |
| tox                | `None literal`                               |      4 |      2 |        2 |
| tox                | `call: other name`                           |      4 |      2 |        1 |
| tox                | `call: builtin.method()`                     |      4 |      3 |        2 |
| tox                | `other constant`                             |      4 |      0 |        0 |
| tox                | `call: builtin next()`                       |      3 |      1 |        1 |
| tox                | `GeneratorExp (unknown elements)`            |      3 |      3 |        3 |
| tox                | `subscript: param[...]`                      |      3 |      3 |        1 |
| tox                | `Yield`                                      |      3 |      3 |        3 |
| tox                | `compare`                                    |      3 |      3 |        3 |
| tox                | `call: module function (annotated)`          |      3 |      3 |        2 |
| tox                | `call: imported.attr()`                      |      3 |      3 |        2 |
| tox                | `call: builtin object()`                     |      2 |      0 |        0 |
| tox                | `call: str-literal.method()`                 |      2 |      1 |        1 |
| tox                | `empty dict`                                 |      2 |      0 |        0 |
| tox                | `call: builtin reversed()`                   |      2 |      0 |        0 |
| tox                | `call: module class`                         |      2 |      0 |        0 |
| tox                | `SetComp (unknown elements)`                 |      1 |      1 |        1 |
| tox                | `call: builtin type()`                       |      1 |      0 |        0 |
| tox                | `copy: self`                                 |      1 |      1 |        1 |
| tox                | `copy: imported`                             |      1 |      0 |        0 |
| tox                | `empty tuple`                                |      1 |      0 |        0 |
| tox                | `copy: modclass`                             |      1 |      0 |        0 |
| tox                | `call: builtin max()`                        |      1 |      0 |        0 |
| tox                | `subscript: other[...]`                      |      1 |      1 |        1 |
| tox                | `boolop (and)`                               |      1 |      1 |        1 |
| tox                | `call: local name`                           |      1 |      1 |        1 |
| tox                | `call: builtin id()`                         |      1 |      1 |        1 |
| tox                | `list (mixed/unknown elements)`              |      1 |      1 |        1 |
| tox                | `JoinedStr`                                  |      1 |      0 |        0 |
| tox                | `call: builtin vars()`                       |      1 |      1 |        0 |
| tox                | `call: cls.method()`                         |      1 |      1 |        1 |
| tox                | `call: other.method()`                       |      1 |      1 |        1 |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                              | new failures | gone | named | skipped anew | skipped no more |
| ------------------ | ------------------ | ---------------- | -------------------------------------------------------------------- | -----------: | ---: | ----: | -----------: | --------------: |
| django             | released           |                  | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped           |              |      |       |              |                 |
| django             | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| django             | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | released           |                  | 29,521 passed, 975 skipped                                           |              |      |       |              |                 |
| sqlalchemy         | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sqlalchemy         | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | released           |                  | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     |              |      |       |              |                 |
| pydantic           | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pydantic           | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |              |      |       |              |                 |
| pandas             | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pandas             | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | released           |                  | 24 failed, 860 passed, 37 skipped                                    |              |      |       |              |                 |
| structlog          | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| structlog          | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | released           |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |              |      |       |              |                 |
| attrs              | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| attrs              | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | released           |                  | 1,991 passed, 24 skipped, 1 xfailed                                  |              |      |       |              |                 |
| click              | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| click              | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | released           |                  | 2 failed, 194 passed                                                 |              |      |       |              |                 |
| hypercorn          | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| hypercorn          | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | released           |                  | 1,271 passed, 2 skipped, 2 xfailed                                   |              |      |       |              |                 |
| starlette          | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| starlette          | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | released           |                  | 1 failed, 979 passed, 1 skipped                                      |              |      |       |              |                 |
| werkzeug           | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| werkzeug           | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | released           |                  | 2 errors, 2 failures, 724 ran, 4 skipped                             |              |      |       |              |                 |
| mkdocs             | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | released           |                  | 1 failed, 1,416 passed, 1 skipped                                    |              |      |       |              |                 |
| httpx              | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| httpx              | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| black              | released           |                  | 519 passed, 1 skipped                                                |              |      |       |              |                 |
| black              | fix-certain        | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| black              | fix-likely         | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| black              | fix-unsafe         | True             | as infer-trace's (implied)                                           |            0 |    0 |     1 |              |                 |
| black              | infer-basedpyright | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| black              | infer-pyrefly      | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| black              | infer-trace        | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| black              | infer-ty           | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |            0 |               0 |
| fastapi            | released           |                  | 3,551 passed, 17 skipped, 4 xfailed                                  |              |      |       |              |                 |
| fastapi            | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| fastapi            | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | released           |                  | 994 passed, 15 xfailed                                               |              |      |       |              |                 |
| cattrs             | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| cattrs             | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | released           |                  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed |              |      |       |              |                 |
| pytest             | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pytest             | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | released           |                  | 7 failed, 4,593 passed, 96 skipped                                   |              |      |       |              |                 |
| botocore           | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| botocore           | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | released           |                  | 1,350 passed, 12 skipped                                             |              |      |       |              |                 |
| uvicorn            | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| uvicorn            | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | released           |                  | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         |              |      |       |              |                 |
| mcp                | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| mcp                | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | released           |                  | 1,472 passed, 1 skipped                                              |              |      |       |              |                 |
| pdm                | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pdm                | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | released           |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |              |      |       |              |                 |
| strawberry-graphql | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| strawberry-graphql | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | released           |                  | 1 failed, 5,330 passed, 15 skipped                                   |              |      |       |              |                 |
| pygments           | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| pygments           | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | released           |                  | 9 error, 15 failed, 7,233 passed, 36 skipped                         |              |      |       |              |                 |
| streamlink         | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| streamlink         | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| sphinx             | released           |                  | 9 failed, 2,393 passed, 22 skipped                                   |              |      |       |              |                 |
| sphinx             | fix-certain        | True             | as infer-trace's (implied)                                           |            0 |    0 |     0 |              |                 |
| sphinx             | fix-likely         | True             | as infer-trace's (implied)                                           |            0 |    0 |     0 |              |                 |
| sphinx             | fix-unsafe         | True             | as infer-trace's (implied)                                           |            0 |    0 |     0 |              |                 |
| sphinx             | infer-basedpyright | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-pyrefly      | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-trace        | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-ty           | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |            0 |               0 |
| tox                | released           |                  | 6 error, 17 failed, 8,525 passed, 31 skipped                         |              |      |       |              |                 |
| tox                | fix-certain        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | fix-likely         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | fix-unsafe         | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | infer-basedpyright | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | infer-pyrefly      | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | infer-trace        | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |
| tox                | infer-ty           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |              |                 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      0 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      0 |   0 |    0 |    198 files changed, 2873 insertions(+), 2385 deletions(-) |
| sqlalchemy         | fix-likely         |      0 |   0 |    0 |    187 files changed, 2368 insertions(+), 1920 deletions(-) |
| sqlalchemy         | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2873 insertions(+), 2385 deletions(-) |
| sqlalchemy         | infer-basedpyright |      3 |   3 |    0 |    204 files changed, 3657 insertions(+), 3120 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      1 |   1 |    0 |    203 files changed, 3359 insertions(+), 2704 deletions(-) |
| sqlalchemy         | infer-trace        |      6 |   6 |    0 |    200 files changed, 3049 insertions(+), 2513 deletions(-) |
| sqlalchemy         | infer-ty           |      2 |   2 |    0 |    205 files changed, 3620 insertions(+), 2971 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1908 insertions(+), 1493 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1940 insertions(+), 1409 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1814 insertions(+), 1402 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   1 |    1 | 1069 files changed, 18266 insertions(+), 15203 deletions(-) |
| pandas             | fix-likely         |    259 |   1 |    1 | 1201 files changed, 42130 insertions(+), 38449 deletions(-) |
| pandas             | fix-unsafe         |    261 |   3 |    1 | 1204 files changed, 43226 insertions(+), 39378 deletions(-) |
| pandas             | infer-basedpyright |    300 |  42 |    1 | 1213 files changed, 49141 insertions(+), 44753 deletions(-) |
| pandas             | infer-pyrefly      |    314 |  56 |    1 | 1210 files changed, 50225 insertions(+), 45505 deletions(-) |
| pandas             | infer-trace        |    262 |   4 |    1 | 1207 files changed, 44552 insertions(+), 40626 deletions(-) |
| pandas             | infer-ty           |    266 |   8 |    1 | 1215 files changed, 48895 insertions(+), 44480 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 443 insertions(+), 349 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 449 insertions(+), 350 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 461 insertions(+), 361 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 219 insertions(+), 150 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 164 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 523 insertions(+), 403 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 802 insertions(+), 568 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 832 insertions(+), 561 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 828 insertions(+), 575 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 399 insertions(+), 330 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 356 insertions(+), 284 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 383 insertions(+), 306 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | infer-basedpyright |      4 |   4 |    0 |       29 files changed, 370 insertions(+), 282 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 351 insertions(+), 266 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 938 insertions(+), 666 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 938 insertions(+), 666 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1152 insertions(+), 851 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1117 insertions(+), 805 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1157 insertions(+), 825 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-basedpyright |     13 |   3 |    0 |     155 files changed, 1101 insertions(+), 840 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     11 |   1 |    0 |      153 files changed, 979 insertions(+), 733 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-ty           |     11 |   1 |    0 |     155 files changed, 1098 insertions(+), 833 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    186 files changed, 1753 insertions(+), 1133 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |     173 files changed, 1494 insertions(+), 902 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-ty           |     24 |  24 |    0 |    186 files changed, 2008 insertions(+), 1133 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    194 files changed, 3306 insertions(+), 2230 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    197 files changed, 3831 insertions(+), 2653 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    213 files changed, 4225 insertions(+), 2981 deletions(-) |
| sphinx             | infer-basedpyright |      8 |   5 |    0 |    216 files changed, 5067 insertions(+), 3739 deletions(-) |
| sphinx             | infer-pyrefly      |     13 |  10 |    0 |    217 files changed, 5339 insertions(+), 3789 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    213 files changed, 4225 insertions(+), 2981 deletions(-) |
| sphinx             | infer-ty           |      6 |   3 |    0 |    215 files changed, 5115 insertions(+), 3708 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    39.3 |        89.4 |  2.3 |    3.49 |          3 |     4.31 | False |
| standard library   | fix-certain              |   120.2 |       267.3 |  2.2 |    4.66 |          3 |     5.85 | False |
| standard library   | fix-likely               |   143.2 |       334.3 |  2.3 |    6.86 |          3 |     8.55 | False |
| standard library   | fix-unsafe               |   133.0 |       318.9 |  2.4 |    6.31 |          3 |      7.9 | False |
| standard library   | infer-basedpyright       |   915.8 |      1381.0 |  1.5 |   11.83 |          2 |      6.2 | False |
| standard library   | infer-ty                 |   162.5 |       476.5 |  2.9 |   12.47 |          1 |     3.22 | False |
| standard library   | infer-pyrefly            |   227.9 |       508.0 |  2.2 |   14.87 |          2 |     6.97 | False |
| standard library   | census                   |    27.1 |        26.2 |  1.0 |    0.54 |          3 |     4.31 | False |
| standard library   | coverage                 |     8.0 |        26.6 |  3.3 |    0.74 |          4 |     0.94 | False |
| standard library   | timing                   |    59.8 |        91.0 |  1.5 |    3.44 |         16 |      4.3 | False |
| django             | check                    |     0.6 |         0.4 |  0.7 |    0.06 |          2 |     1.09 | False |
| django             | fix-certain              |    24.3 |        47.5 |  2.0 |    1.12 |          3 |      1.4 | False |
| django             | fix-likely               |    51.3 |        66.3 |  1.3 |    1.47 |          2 |     1.84 | False |
| django             | fix-unsafe               |    23.1 |        55.2 |  2.4 |    1.42 |          3 |     1.74 | False |
| django             | infer-basedpyright       |   104.2 |       251.2 |  2.4 |    4.22 |          1 |     0.63 | False |
| django             | infer-ty                 |    47.7 |        95.0 |  2.0 |    3.46 |          1 |     1.02 | False |
| django             | infer-pyrefly            |    67.5 |       104.4 |  1.5 |    3.88 |          1 |      1.1 | False |
| django             | census                   |    10.4 |        20.8 |  2.0 |    0.87 |          2 |     1.09 | False |
| django             | coverage                 |     1.6 |         4.0 |  2.5 |    0.33 |          2 |      0.4 | False |
| django             | timing                   |    12.2 |        18.3 |  1.5 |    0.87 |         16 |     1.09 | False |
| django             | traced                   |    98.7 |       585.4 |  5.9 |    7.11 |          7 |     8.56 | False |
| django             | tests-released           |    55.9 |       387.9 |  6.9 |    4.34 |          8 |     5.02 | False |
| django             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.68 | False |
| django             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.05 | False |
| django             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |         13 |     6.81 | False |
| django             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.44 | False |
| django             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     4.18 | False |
| django             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |         13 |     6.88 | False |
| django             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     8.38 | False |
| django             | infer-union              |   128.8 |       378.6 |  2.9 |    5.31 |          2 |     2.57 | False |
| django             | tests-infer-union        |    53.1 |       428.6 |  8.1 |    5.27 |          9 |     6.72 | False |
| django             | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          2 |     0.15 | False |
| sqlalchemy         | check                    |     0.6 |         0.3 |  0.5 |    0.06 |          2 |     1.01 | False |
| sqlalchemy         | fix-certain              |    22.5 |        40.2 |  1.8 |    0.94 |          2 |     1.14 | False |
| sqlalchemy         | fix-likely               |    24.3 |        52.8 |  2.2 |    1.23 |          2 |     1.54 | False |
| sqlalchemy         | fix-unsafe               |    26.6 |        49.9 |  1.9 |    1.14 |          2 |     1.41 | False |
| sqlalchemy         | infer-basedpyright       |   124.3 |       224.1 |  1.8 |    4.39 |          1 |     0.81 | False |
| sqlalchemy         | infer-ty                 |    46.3 |        89.4 |  1.9 |    2.97 |          1 |     0.79 | False |
| sqlalchemy         | infer-pyrefly            |    47.5 |        83.0 |  1.7 |    3.34 |          1 |     0.81 | False |
| sqlalchemy         | census                   |    10.2 |        17.6 |  1.7 |    0.81 |          2 |     1.01 | False |
| sqlalchemy         | coverage                 |     4.0 |         7.0 |  1.8 |    0.35 |          3 |     0.44 | False |
| sqlalchemy         | timing                   |    10.8 |        15.1 |  1.4 |    0.81 |         16 |     1.01 | False |
| sqlalchemy         | traced                   |   159.6 |      1109.0 |  6.9 |    5.64 |          8 |     7.39 | False |
| sqlalchemy         | tests-released           |   127.2 |       879.8 |  6.9 |    4.61 |          9 |      5.5 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         13 |     7.19 | False |
| sqlalchemy         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.91 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |         14 |     7.26 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          9 |     5.47 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.89 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.85 | False |
| sqlalchemy         | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |         15 |      7.3 | False |
| sqlalchemy         | infer-union              |    90.9 |       288.1 |  3.2 |    5.74 |          3 |     6.15 | False |
| sqlalchemy         | tests-infer-union        |   119.7 |      1025.8 |  8.6 |    5.76 |         11 |     7.27 | False |
| sqlalchemy         | tests                    |     0.8 |         0.5 |  0.6 |    0.12 |          1 |     0.15 | False |
| sqlalchemy         | types-released           |     9.2 |         6.6 |  0.7 |    0.33 |          1 |      0.4 | False |
| sqlalchemy         | types-fix-certain        |     0.4 |         0.3 |  0.7 |    0.04 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-likely         |     5.0 |         4.9 |  1.0 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-unsafe         |     6.2 |         6.1 |  1.0 |     0.3 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |    12.2 |         8.1 |  0.7 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |    12.0 |         7.2 |  0.6 |    0.31 |          1 |     0.42 | False |
| sqlalchemy         | types-infer-pyrefly      |    10.0 |         6.8 |  0.7 |    0.35 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-trace        |     5.2 |         5.0 |  1.0 |    0.33 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.36 | False |
| pydantic           | fix-certain              |     9.0 |        12.0 |  1.3 |    0.47 |          2 |     0.49 | False |
| pydantic           | fix-likely               |     6.2 |        13.0 |  2.1 |    0.47 |          2 |     0.57 | False |
| pydantic           | fix-unsafe               |     6.0 |        12.3 |  2.1 |    0.42 |          3 |     0.51 | False |
| pydantic           | infer-basedpyright       |    58.9 |        75.9 |  1.3 |     2.5 |          1 |     0.29 | False |
| pydantic           | infer-ty                 |    15.8 |        21.4 |  1.4 |    1.18 |          1 |     0.29 | False |
| pydantic           | infer-pyrefly            |    17.2 |        32.0 |  1.9 |    1.88 |          1 |     0.29 | False |
| pydantic           | census                   |     2.4 |         3.8 |  1.6 |     0.3 |          2 |     0.36 | False |
| pydantic           | coverage                 |     2.5 |         2.0 |  0.8 |    0.21 |          2 |     0.26 | False |
| pydantic           | timing                   |     2.6 |         3.7 |  1.4 |     0.3 |         16 |     0.36 | False |
| pydantic           | traced                   |    86.0 |        63.0 |  0.7 |    0.44 |          1 |     0.56 | False |
| pydantic           | tests-released           |    69.1 |        44.1 |  0.6 |    0.29 |          1 |      0.4 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.4 | False |
| pydantic           | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.37 | False |
| pydantic           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.4 | False |
| pydantic           | infer-union              |    78.5 |       193.2 |  2.5 |    2.41 |          2 |      0.6 | False |
| pydantic           | tests-infer-union        |    76.0 |        46.2 |  0.6 |    0.35 |          1 |     0.39 | False |
| pydantic           | tests                    |     1.2 |         0.8 |  0.7 |    0.16 |          1 |     0.15 | False |
| pydantic           | types-released           |    18.8 |        19.3 |  1.0 |    0.53 |          2 |     0.67 | False |
| pydantic           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.66 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-infer-basedpyright |    16.1 |        20.1 |  1.2 |    0.55 |          2 |     0.67 | False |
| pydantic           | types-infer-ty           |    12.0 |        16.6 |  1.4 |    0.53 |          2 |      0.7 | False |
| pydantic           | types-infer-pyrefly      |    12.6 |        17.6 |  1.4 |    0.53 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |    20.8 |        19.6 |  0.9 |    0.53 |          1 |     0.66 | False |
| pydantic           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |     1.8 |         1.3 |  0.7 |    0.23 |          2 |     4.07 | False |
| pandas             | fix-certain              |    80.4 |       243.6 |  3.0 |    3.85 |          4 |     4.81 | False |
| pandas             | fix-likely               |   174.3 |       431.8 |  2.5 |    6.56 |          3 |      8.2 | False |
| pandas             | fix-unsafe               |   223.6 |       466.2 |  2.1 |    6.44 |          4 |     8.04 | False |
| pandas             | infer-basedpyright       |   629.1 |      1252.4 |  2.0 |   13.61 |          2 |     6.66 | False |
| pandas             | infer-ty                 |   260.2 |       757.4 |  2.9 |   11.15 |          1 |     3.32 | False |
| pandas             | infer-pyrefly            |   223.5 |       639.8 |  2.9 |   15.38 |          2 |     6.62 | False |
| pandas             | census                   |    60.7 |       129.1 |  2.1 |    3.26 |          2 |     4.07 | False |
| pandas             | coverage                 |     8.2 |        23.4 |  2.9 |    0.78 |          4 |     0.97 | False |
| pandas             | timing                   |    65.4 |       104.7 |  1.6 |    3.26 |         16 |     4.05 | False |
| pandas             | traced                   |   292.2 |      1272.0 |  4.4 |   12.52 |          6 |    15.64 | False |
| pandas             | tests-released           |   111.0 |       673.0 |  6.1 |   11.49 |          9 |    14.08 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    14.35 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    14.32 | False |
| pandas             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    14.39 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    13.73 | False |
| pandas             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    12.18 | False |
| pandas             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |    12.24 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    15.06 | False |
| pandas             | infer-union              |   520.8 |      1675.8 |  3.2 |   14.56 |          4 |    17.72 | False |
| pandas             | tests-infer-union        |   123.4 |       725.8 |  5.9 |    11.5 |          8 |    14.35 | False |
| pandas             | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          1 |     0.15 | False |
| pandas             | types-released           |    86.9 |       105.6 |  1.2 |    2.15 |          2 |     2.59 | False |
| pandas             | types-fix-certain        |    72.8 |        89.6 |  1.2 |    2.42 |          2 |     2.92 | False |
| pandas             | types-fix-likely         |    59.1 |        86.5 |  1.5 |    2.28 |          2 |     2.77 | False |
| pandas             | types-fix-unsafe         |    65.2 |        98.4 |  1.5 |    2.27 |          2 |     2.82 | False |
| pandas             | types-infer-basedpyright |    61.1 |        88.0 |  1.4 |    2.28 |          2 |     2.72 | False |
| pandas             | types-infer-ty           |    94.4 |       110.4 |  1.2 |    2.26 |          2 |     2.67 | False |
| pandas             | types-infer-pyrefly      |    65.5 |        96.9 |  1.5 |    2.28 |          2 |     2.81 | False |
| pandas             | types-infer-trace        |    67.6 |       100.7 |  1.5 |     2.3 |          2 |     2.85 | False |
| pandas             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     4.6 |        12.5 |  2.7 |    0.78 |          3 |     0.97 | False |
| twisted            | fix-certain              |    13.6 |        37.3 |  2.7 |     0.9 |          3 |     1.12 | False |
| twisted            | fix-likely               |    16.4 |        45.4 |  2.8 |    1.27 |          3 |     1.59 | False |
| twisted            | fix-unsafe               |    19.5 |        43.1 |  2.2 |    1.17 |          3 |     1.47 | False |
| twisted            | infer-basedpyright       |   197.6 |       243.0 |  1.2 |     4.0 |          1 |     0.64 | False |
| twisted            | infer-ty                 |    49.1 |        90.1 |  1.8 |    2.87 |          1 |     0.57 | False |
| twisted            | infer-pyrefly            |    43.5 |        86.1 |  2.0 |    3.39 |          1 |     0.58 | False |
| twisted            | census                   |     6.2 |         5.0 |  0.8 |    0.12 |          3 |     0.97 | False |
| twisted            | coverage                 |     4.2 |         6.6 |  1.6 |    0.36 |          3 |     0.45 | False |
| twisted            | timing                   |     9.0 |        13.8 |  1.5 |    0.78 |         16 |     0.96 | False |
| pip                | check                    |     4.2 |         9.3 |  2.2 |    0.54 |          3 |     0.67 | False |
| pip                | fix-certain              |    13.7 |        25.8 |  1.9 |    0.71 |          2 |     0.86 | False |
| pip                | fix-likely               |    12.0 |        30.6 |  2.6 |     0.9 |          3 |     1.12 | False |
| pip                | fix-unsafe               |    21.5 |        32.3 |  1.5 |    0.84 |          3 |     1.05 | False |
| pip                | infer-basedpyright       |    88.9 |       194.3 |  2.2 |    3.83 |          1 |     0.59 | False |
| pip                | infer-ty                 |    33.5 |        62.5 |  1.9 |    2.62 |          1 |     0.58 | False |
| pip                | infer-pyrefly            |    29.7 |        62.5 |  2.1 |    3.06 |          1 |     0.57 | False |
| pip                | census                   |     5.8 |         3.6 |  0.6 |     0.1 |          3 |     0.67 | False |
| pip                | coverage                 |     1.2 |         2.8 |  2.3 |     0.3 |          2 |     0.37 | False |
| pip                | timing                   |     6.0 |         9.0 |  1.5 |    0.55 |         16 |     0.67 | False |
| structlog          | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.2 | False |
| structlog          | fix-certain              |     1.8 |         2.5 |  1.4 |    0.25 |          2 |     0.31 | False |
| structlog          | fix-likely               |     2.0 |         2.8 |  1.4 |    0.25 |          2 |     0.29 | False |
| structlog          | fix-unsafe               |     2.2 |         2.9 |  1.3 |    0.25 |          2 |      0.3 | False |
| structlog          | infer-basedpyright       |    10.0 |        11.3 |  1.1 |    0.59 |          1 |     0.12 | False |
| structlog          | infer-ty                 |     2.0 |         3.2 |  1.6 |     0.4 |          1 |     0.16 | False |
| structlog          | infer-pyrefly            |     4.2 |         4.0 |  1.0 |    0.43 |          1 |     0.12 | False |
| structlog          | census                   |     1.4 |         1.1 |  0.8 |    0.16 |          1 |      0.2 | False |
| structlog          | coverage                 |     0.6 |         0.5 |  0.8 |    0.15 |          2 |     0.17 | False |
| structlog          | timing                   |     0.8 |         0.8 |  1.0 |    0.16 |         16 |      0.2 | False |
| structlog          | traced                   |     9.6 |         6.0 |  0.6 |    0.28 |          1 |     0.35 | False |
| structlog          | tests-released           |     3.6 |         2.0 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | infer-union              |    23.3 |        18.3 |  0.8 |    0.52 |          1 |     0.31 | False |
| structlog          | tests-infer-union        |     3.0 |         2.1 |  0.7 |    0.08 |          1 |     0.09 | False |
| structlog          | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| structlog          | types-released           |     1.2 |         0.5 |  0.4 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-basedpyright |     0.6 |         0.4 |  0.7 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-pyrefly      |     1.2 |         0.5 |  0.4 |    0.08 |          1 |     0.09 | False |
| structlog          | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| attrs              | fix-certain              |     2.4 |         2.4 |  1.0 |    0.26 |          1 |     0.31 | False |
| attrs              | fix-likely               |     2.2 |         2.5 |  1.1 |    0.26 |          2 |     0.32 | False |
| attrs              | fix-unsafe               |     2.4 |         2.5 |  1.0 |    0.25 |          1 |     0.32 | False |
| attrs              | infer-basedpyright       |    13.4 |        13.8 |  1.0 |    0.57 |          1 |     0.31 | False |
| attrs              | infer-ty                 |     4.8 |         4.1 |  0.9 |    0.27 |          1 |     0.34 | False |
| attrs              | infer-pyrefly            |     5.2 |         7.6 |  1.5 |    0.44 |          1 |     0.31 | False |
| attrs              | census                   |     2.0 |         1.0 |  0.5 |    0.15 |          1 |     0.19 | False |
| attrs              | coverage                 |     1.0 |         0.7 |  0.7 |    0.14 |          1 |     0.17 | False |
| attrs              | timing                   |     0.8 |         0.6 |  0.7 |    0.15 |         16 |     0.19 | False |
| attrs              | traced                   |     7.0 |        26.1 |  3.7 |    0.75 |          6 |     0.92 | False |
| attrs              | tests-released           |     2.8 |        13.6 |  4.9 |     0.6 |          6 |     0.77 | False |
| attrs              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     0.75 | False |
| attrs              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.74 | False |
| attrs              | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     0.75 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.72 | False |
| attrs              | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     0.74 | False |
| attrs              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.72 | False |
| attrs              | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     0.75 | False |
| attrs              | infer-union              |    15.4 |        25.6 |  1.7 |    0.54 |          1 |      0.3 | False |
| attrs              | tests-infer-union        |     3.2 |        15.7 |  4.9 |    0.59 |          7 |     0.75 | False |
| attrs              | tests                    |     0.6 |         0.5 |  0.8 |    0.12 |          1 |     0.15 | False |
| click              | check                    |     1.2 |         1.2 |  1.0 |    0.18 |          1 |     0.21 | False |
| click              | fix-certain              |     1.6 |         2.9 |  1.8 |     0.3 |          2 |     0.37 | False |
| click              | fix-likely               |     1.8 |         3.3 |  1.8 |     0.3 |          2 |     0.36 | False |
| click              | fix-unsafe               |     4.4 |         4.2 |  1.0 |    0.31 |          2 |     0.37 | False |
| click              | infer-basedpyright       |    14.2 |        14.8 |  1.0 |    0.68 |          1 |     0.27 | False |
| click              | infer-ty                 |     2.4 |         4.2 |  1.8 |    0.43 |          1 |     0.16 | False |
| click              | infer-pyrefly            |     3.0 |         7.9 |  2.6 |     0.6 |          1 |     0.19 | False |
| click              | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.21 | False |
| click              | coverage                 |     1.2 |         1.0 |  0.8 |    0.16 |          1 |      0.2 | False |
| click              | timing                   |     1.0 |         1.0 |  1.0 |    0.18 |         16 |     0.22 | False |
| click              | traced                   |    10.8 |        10.2 |  0.9 |    0.29 |          1 |     0.37 | False |
| click              | tests-released           |     8.6 |         6.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | infer-union              |    22.3 |        24.9 |  1.1 |    0.59 |          1 |     0.31 | False |
| click              | tests-infer-union        |     7.8 |         5.8 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| click              | types-released           |     1.2 |         0.7 |  0.6 |    0.11 |          1 |     0.12 | False |
| click              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| click              | types-infer-basedpyright |     1.4 |         0.7 |  0.5 |    0.12 |          1 |     0.12 | False |
| click              | types-infer-ty           |     0.6 |         0.4 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-trace        |     1.0 |         0.6 |  0.6 |    0.13 |          1 |     0.12 | False |
| click              | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| hypercorn          | fix-certain              |     2.0 |         2.9 |  1.4 |    0.25 |          2 |     0.31 | False |
| hypercorn          | fix-likely               |     2.2 |         3.2 |  1.5 |    0.25 |          2 |     0.31 | False |
| hypercorn          | fix-unsafe               |     2.8 |         3.6 |  1.3 |    0.26 |          2 |     0.31 | False |
| hypercorn          | infer-basedpyright       |    11.0 |        19.1 |  1.7 |    0.88 |          1 |     0.14 | False |
| hypercorn          | infer-ty                 |     4.4 |         5.0 |  1.1 |    0.61 |          1 |     0.16 | False |
| hypercorn          | infer-pyrefly            |     4.0 |        10.0 |  2.5 |    0.91 |          1 |     0.18 | False |
| hypercorn          | census                   |     3.0 |         1.7 |  0.6 |    0.19 |          1 |     0.21 | False |
| hypercorn          | coverage                 |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.17 | False |
| hypercorn          | timing                   |     0.8 |         0.9 |  1.1 |    0.18 |         16 |     0.21 | False |
| hypercorn          | traced                   |    12.4 |         5.9 |  0.5 |    0.27 |          1 |     0.31 | False |
| hypercorn          | tests-released           |     9.2 |         1.6 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-infer-trace        |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | infer-union              |    24.3 |        28.3 |  1.2 |    0.78 |          1 |     0.16 | False |
| hypercorn          | tests-infer-union        |     9.6 |         1.7 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types-released           |     2.2 |         1.1 |  0.5 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| hypercorn          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-infer-basedpyright |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.12 | False |
| hypercorn          | types-infer-ty           |     0.6 |         0.4 |  0.7 |     0.1 |          1 |     0.12 | False |
| hypercorn          | types-infer-pyrefly      |     0.6 |         0.4 |  0.7 |     0.1 |          1 |     0.15 | False |
| hypercorn          | types-infer-trace        |     2.6 |         1.2 |  0.5 |    0.12 |          1 |     0.14 | False |
| hypercorn          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| starlette          | fix-certain              |     1.4 |         2.7 |  1.9 |    0.26 |          2 |     0.32 | False |
| starlette          | fix-likely               |     2.0 |         3.6 |  1.8 |    0.29 |          2 |     0.36 | False |
| starlette          | fix-unsafe               |     3.2 |         4.2 |  1.3 |     0.3 |          2 |     0.34 | False |
| starlette          | infer-basedpyright       |     8.4 |        12.8 |  1.5 |    0.89 |          1 |     0.14 | False |
| starlette          | infer-ty                 |     5.8 |         6.9 |  1.2 |    0.39 |          1 |     0.37 | False |
| starlette          | infer-pyrefly            |     5.2 |        13.1 |  2.5 |    0.93 |          1 |     0.18 | False |
| starlette          | census                   |     1.6 |         1.6 |  1.0 |    0.18 |          1 |     0.22 | False |
| starlette          | coverage                 |     0.6 |         0.7 |  1.2 |    0.15 |          2 |     0.19 | False |
| starlette          | timing                   |     1.0 |         1.1 |  1.1 |    0.19 |         16 |     0.22 | False |
| starlette          | traced                   |    23.3 |        14.0 |  0.6 |    0.28 |          1 |     0.34 | False |
| starlette          | tests-released           |    19.9 |         7.6 |  0.4 |    0.22 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.26 | False |
| starlette          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.26 | False |
| starlette          | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.26 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.29 | False |
| starlette          | infer-union              |    26.1 |        40.9 |  1.6 |     0.8 |          1 |     0.32 | False |
| starlette          | tests-infer-union        |    20.5 |         8.0 |  0.4 |    0.23 |          1 |     0.29 | False |
| starlette          | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| starlette          | types-released           |     3.2 |         1.8 |  0.6 |    0.14 |          1 |     0.17 | False |
| starlette          | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| starlette          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.16 | False |
| starlette          | types-infer-basedpyright |     0.8 |         0.5 |  0.6 |    0.12 |          1 |     0.16 | False |
| starlette          | types-infer-ty           |     2.6 |         1.7 |  0.7 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-pyrefly      |     1.4 |         1.1 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.17 | False |
| starlette          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.25 | False |
| werkzeug           | fix-certain              |     2.0 |         4.8 |  2.4 |    0.33 |          2 |     0.42 | False |
| werkzeug           | fix-likely               |     3.2 |         6.3 |  2.0 |    0.33 |          2 |     0.41 | False |
| werkzeug           | fix-unsafe               |     7.0 |         7.4 |  1.1 |    0.35 |          2 |     0.41 | False |
| werkzeug           | infer-basedpyright       |    19.6 |        32.0 |  1.6 |    1.18 |          1 |     0.19 | False |
| werkzeug           | infer-ty                 |     6.2 |        10.7 |  1.7 |    0.73 |          1 |      0.2 | False |
| werkzeug           | infer-pyrefly            |     5.6 |        12.3 |  2.2 |     1.1 |          1 |     0.21 | False |
| werkzeug           | census                   |     3.2 |         2.8 |  0.9 |    0.21 |          2 |     0.25 | False |
| werkzeug           | coverage                 |     1.8 |         1.3 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | timing                   |     1.4 |         1.7 |  1.2 |     0.2 |         16 |     0.25 | False |
| werkzeug           | traced                   |    18.6 |        15.1 |  0.8 |    0.31 |          1 |      0.4 | False |
| werkzeug           | tests-released           |    11.0 |         7.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | infer-union              |    31.1 |        56.4 |  1.8 |    1.11 |          1 |     0.16 | False |
| werkzeug           | tests-infer-union        |    10.4 |         7.1 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests                    |     1.2 |         0.9 |  0.8 |    0.12 |          1 |     0.15 | False |
| werkzeug           | types-released           |     2.0 |         1.1 |  0.6 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-infer-basedpyright |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.12 | False |
| werkzeug           | types-infer-ty           |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-pyrefly      |     1.6 |         1.1 |  0.7 |    0.11 |          1 |     0.12 | False |
| werkzeug           | types-infer-trace        |     1.8 |         1.1 |  0.6 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     0.8 |         0.2 |  0.2 |    0.04 |          1 |     0.31 | False |
| mkdocs             | fix-certain              |     2.4 |         5.0 |  2.1 |    0.36 |          2 |     0.45 | False |
| mkdocs             | fix-likely               |     3.2 |         6.4 |  2.0 |    0.37 |          2 |     0.42 | False |
| mkdocs             | fix-unsafe               |     6.4 |         8.2 |  1.3 |    0.38 |          2 |     0.45 | False |
| mkdocs             | infer-basedpyright       |    27.7 |        44.7 |  1.6 |    1.38 |          1 |     0.19 | False |
| mkdocs             | infer-ty                 |     6.0 |        11.4 |  1.9 |    0.86 |          1 |      0.2 | False |
| mkdocs             | infer-pyrefly            |     9.4 |        18.8 |  2.0 |    0.97 |          1 |     0.22 | False |
| mkdocs             | census                   |     2.8 |         3.3 |  1.2 |    0.29 |          1 |     0.31 | False |
| mkdocs             | coverage                 |     1.2 |         1.3 |  1.1 |    0.18 |          2 |     0.22 | False |
| mkdocs             | timing                   |     1.6 |         2.0 |  1.2 |    0.25 |         16 |     0.31 | False |
| mkdocs             | traced                   |    15.6 |        10.3 |  0.7 |    0.37 |          1 |     0.44 | False |
| mkdocs             | tests-released           |    11.2 |         2.7 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    15.4 |        44.5 |  2.9 |    1.18 |          2 |     0.41 | False |
| mkdocs             | tests-infer-union        |    11.6 |         2.8 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     1.0 |         0.8 |  0.8 |    0.12 |          1 |     0.15 | False |
| httpx              | check                    |     1.6 |         1.2 |  0.7 |    0.18 |          1 |     0.22 | False |
| httpx              | fix-certain              |     2.0 |         3.1 |  1.6 |    0.26 |          2 |     0.36 | False |
| httpx              | fix-likely               |     2.2 |         3.6 |  1.6 |    0.26 |          2 |     0.32 | False |
| httpx              | fix-unsafe               |     4.0 |         3.9 |  1.0 |    0.29 |          2 |     0.32 | False |
| httpx              | infer-basedpyright       |    16.8 |        17.6 |  1.0 |    0.73 |          1 |     0.31 | False |
| httpx              | infer-ty                 |     5.8 |         5.2 |  0.9 |    0.37 |          1 |     0.16 | False |
| httpx              | infer-pyrefly            |     6.0 |         8.8 |  1.5 |    0.62 |          1 |     0.18 | False |
| httpx              | census                   |     0.8 |         0.3 |  0.4 |    0.04 |          1 |     0.22 | False |
| httpx              | coverage                 |     1.4 |         1.0 |  0.7 |    0.15 |          1 |     0.19 | False |
| httpx              | timing                   |     0.8 |         0.9 |  1.1 |    0.18 |         16 |     0.22 | False |
| httpx              | traced                   |    15.9 |        10.8 |  0.7 |    0.31 |          1 |     0.35 | False |
| httpx              | tests-released           |    11.0 |         6.4 |  0.6 |    0.23 |          1 |     0.27 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| httpx              | tests-infer-trace        |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     0.27 | False |
| httpx              | infer-union              |    24.2 |        24.1 |  1.0 |    0.63 |          1 |     0.16 | False |
| httpx              | tests-infer-union        |    12.6 |         6.4 |  0.5 |    0.22 |          1 |     0.27 | False |
| httpx              | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| httpx              | types-released           |     8.6 |         6.4 |  0.7 |    0.24 |          1 |      0.3 | False |
| httpx              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.24 | False |
| httpx              | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| httpx              | types-infer-basedpyright |    12.0 |         6.9 |  0.6 |    0.24 |          1 |     0.29 | False |
| httpx              | types-infer-ty           |     8.0 |         6.1 |  0.8 |    0.23 |          1 |     0.24 | False |
| httpx              | types-infer-pyrefly      |     4.8 |         4.5 |  0.9 |     0.2 |          1 |     0.29 | False |
| httpx              | types-infer-trace        |    10.4 |         6.5 |  0.6 |     0.2 |          1 |     0.25 | False |
| httpx              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| black              | fix-certain              |     2.4 |         4.4 |  1.8 |     0.3 |          2 |     0.37 | False |
| black              | fix-likely               |     4.6 |         5.2 |  1.1 |    0.32 |          3 |     0.39 | False |
| black              | fix-unsafe               |     2.2 |         4.5 |  2.0 |     0.3 |          2 |     0.36 | False |
| black              | infer-basedpyright       |    14.2 |        20.9 |  1.5 |    0.76 |          1 |     0.14 | False |
| black              | infer-ty                 |     2.4 |         5.5 |  2.3 |    0.51 |          1 |      0.2 | False |
| black              | infer-pyrefly            |     2.8 |         8.8 |  3.1 |    0.69 |          1 |     0.21 | False |
| black              | census                   |     3.0 |         2.3 |  0.8 |    0.21 |          1 |     0.24 | False |
| black              | coverage                 |     1.0 |         1.1 |  1.1 |    0.17 |          1 |     0.21 | False |
| black              | timing                   |     1.0 |         1.3 |  1.3 |    0.19 |         16 |     0.24 | False |
| black              | traced                   |     9.0 |        50.9 |  5.7 |     0.9 |          8 |     1.11 | False |
| black              | tests-released           |     6.2 |        37.8 |  6.1 |     0.8 |          8 |     0.94 | False |
| black              | tests-fix-certain        |     7.0 |        45.7 |  6.5 |    0.76 |          8 |     0.97 | False |
| black              | tests-fix-likely         |     7.8 |        47.4 |  6.1 |    0.75 |          8 |     0.95 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.94 | False |
| black              | tests-infer-basedpyright |     7.6 |        47.5 |  6.2 |    0.79 |          8 |     0.94 | False |
| black              | tests-infer-ty           |     7.6 |        47.8 |  6.3 |    0.78 |          8 |     0.92 | False |
| black              | tests-infer-pyrefly      |     7.2 |        46.8 |  6.5 |    0.76 |          8 |     0.95 | False |
| black              | tests-infer-trace        |     7.2 |        46.2 |  6.4 |    0.76 |          8 |     0.94 | False |
| black              | infer-union              |     9.6 |        20.8 |  2.2 |    0.67 |          2 |     0.37 | False |
| black              | tests-infer-union        |     6.6 |        41.8 |  6.3 |    0.74 |          8 |     0.92 | False |
| black              | tests                    |     0.6 |         0.5 |  0.8 |    0.12 |          1 |     0.15 | False |
| fastapi            | check                    |     2.6 |         2.1 |  0.8 |    0.22 |          1 |     0.26 | False |
| fastapi            | fix-certain              |     3.4 |         4.6 |  1.4 |    0.35 |          2 |     0.37 | False |
| fastapi            | fix-likely               |    16.3 |         9.6 |  0.6 |    0.45 |          1 |     0.46 | False |
| fastapi            | fix-unsafe               |     3.6 |         4.9 |  1.4 |    0.31 |          2 |     0.39 | False |
| fastapi            | infer-basedpyright       |    25.7 |        36.2 |  1.4 |    1.21 |          1 |     0.19 | False |
| fastapi            | infer-ty                 |    10.6 |        11.5 |  1.1 |    0.56 |          1 |     0.19 | False |
| fastapi            | infer-pyrefly            |    11.2 |        17.5 |  1.6 |    1.13 |          1 |     0.19 | False |
| fastapi            | census                   |     0.8 |         0.5 |  0.6 |    0.05 |          1 |     0.26 | False |
| fastapi            | coverage                 |     1.8 |         1.3 |  0.7 |    0.17 |          1 |     0.21 | False |
| fastapi            | timing                   |     1.4 |         1.5 |  1.1 |    0.22 |         16 |     0.26 | False |
| fastapi            | traced                   |    17.4 |       111.4 |  6.4 |    2.35 |          7 |      2.9 | False |
| fastapi            | tests-released           |    14.8 |        92.6 |  6.3 |    2.11 |          8 |     2.62 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.56 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      2.6 | False |
| fastapi            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.52 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.62 | False |
| fastapi            | infer-union              |    14.8 |        32.6 |  2.2 |    0.91 |          2 |     0.39 | False |
| fastapi            | tests-infer-union        |    14.8 |        97.8 |  6.6 |    2.03 |          8 |      2.6 | False |
| fastapi            | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          2 |     0.15 | False |
| cattrs             | check                    |     1.4 |         1.2 |  0.9 |    0.18 |          1 |     0.22 | False |
| cattrs             | fix-certain              |     2.2 |         3.0 |  1.4 |    0.25 |          2 |     0.31 | False |
| cattrs             | fix-likely               |     1.6 |         2.7 |  1.7 |    0.27 |          2 |     0.34 | False |
| cattrs             | fix-unsafe               |     2.8 |         3.7 |  1.3 |    0.28 |          2 |     0.34 | False |
| cattrs             | infer-basedpyright       |    15.9 |        20.7 |  1.3 |    0.96 |          1 |     0.14 | False |
| cattrs             | infer-ty                 |     6.2 |         6.1 |  1.0 |    0.62 |          1 |     0.17 | False |
| cattrs             | infer-pyrefly            |     5.0 |         8.7 |  1.7 |    0.69 |          1 |     0.34 | False |
| cattrs             | census                   |     1.0 |         0.4 |  0.4 |    0.04 |          1 |     0.22 | False |
| cattrs             | coverage                 |     1.4 |         0.8 |  0.6 |    0.15 |          1 |     0.17 | False |
| cattrs             | timing                   |     1.0 |         1.0 |  1.0 |    0.18 |         16 |     0.22 | False |
| cattrs             | traced                   |    24.6 |       139.4 |  5.7 |    1.31 |          8 |     1.65 | False |
| cattrs             | tests-released           |    20.8 |       126.5 |  6.1 |    1.01 |          8 |     1.26 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.27 | False |
| cattrs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.27 | False |
| cattrs             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.25 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.21 | False |
| cattrs             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.27 | False |
| cattrs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.21 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.22 | False |
| cattrs             | infer-union              |     8.0 |        22.2 |  2.8 |    0.78 |          2 |     0.31 | False |
| cattrs             | tests-infer-union        |    20.0 |       120.4 |  6.0 |     1.0 |          8 |     1.26 | False |
| cattrs             | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          2 |     0.15 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.34 | False |
| pytest             | fix-certain              |     6.2 |         9.5 |  1.5 |    0.36 |          2 |     0.46 | False |
| pytest             | fix-likely               |     6.8 |        12.1 |  1.8 |    0.41 |          2 |     0.51 | False |
| pytest             | fix-unsafe               |     8.2 |        11.8 |  1.4 |    0.38 |          2 |     0.49 | False |
| pytest             | infer-basedpyright       |    41.9 |        68.5 |  1.6 |    1.98 |          1 |     0.24 | False |
| pytest             | infer-ty                 |    14.4 |        19.4 |  1.3 |    1.06 |          1 |     0.24 | False |
| pytest             | infer-pyrefly            |    19.1 |        23.4 |  1.2 |    1.76 |          1 |     0.27 | False |
| pytest             | census                   |     2.2 |         3.5 |  1.6 |    0.28 |          2 |     0.34 | False |
| pytest             | coverage                 |     1.0 |         1.8 |  1.8 |     0.2 |          2 |     0.25 | False |
| pytest             | timing                   |     2.4 |         3.2 |  1.3 |    0.27 |         16 |     0.34 | False |
| pytest             | traced                   |    47.9 |       323.9 |  6.8 |    1.74 |          8 |     2.15 | False |
| pytest             | tests-released           |    22.6 |       160.2 |  7.1 |    1.41 |          8 |     1.71 | False |
| pytest             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.67 | False |
| pytest             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.69 | False |
| pytest             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |      1.7 | False |
| pytest             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          7 |      1.7 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      1.7 | False |
| pytest             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      1.7 | False |
| pytest             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.71 | False |
| pytest             | infer-union              |    25.5 |        76.3 |  3.0 |    1.79 |          3 |     2.19 | False |
| pytest             | tests-infer-union        |    21.4 |       141.2 |  6.6 |    1.35 |          8 |     1.72 | False |
| pytest             | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          2 |     0.15 | False |
| botocore           | check                    |     1.6 |         3.4 |  2.1 |     0.3 |          2 |     0.37 | False |
| botocore           | fix-certain              |     6.6 |        10.7 |  1.6 |    0.38 |          2 |     0.47 | False |
| botocore           | fix-likely               |     7.0 |        13.4 |  1.9 |    0.47 |          2 |     0.59 | False |
| botocore           | fix-unsafe               |     8.4 |        13.5 |  1.6 |    0.46 |          2 |     0.56 | False |
| botocore           | infer-basedpyright       |    47.3 |        63.7 |  1.3 |    2.17 |          1 |     0.33 | False |
| botocore           | infer-ty                 |    18.8 |        21.5 |  1.1 |    1.24 |          1 |     0.29 | False |
| botocore           | infer-pyrefly            |    18.0 |        21.2 |  1.2 |     1.3 |          1 |     0.29 | False |
| botocore           | census                   |     1.0 |         0.9 |  0.9 |    0.05 |          2 |     0.37 | False |
| botocore           | coverage                 |     1.0 |         1.5 |  1.5 |     0.2 |          2 |     0.25 | False |
| botocore           | timing                   |     2.8 |         3.8 |  1.4 |     0.3 |         16 |     0.37 | False |
| botocore           | traced                   |    36.7 |       122.5 |  3.3 |    5.11 |          5 |     6.39 | False |
| botocore           | tests-released           |    29.7 |        93.5 |  3.1 |    4.92 |          4 |     6.15 | False |
| botocore           | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          4 |     6.05 | False |
| botocore           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     6.05 | False |
| botocore           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     5.97 | False |
| botocore           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     6.06 | False |
| botocore           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.11 | False |
| botocore           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          5 |      6.0 | False |
| botocore           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.12 | False |
| botocore           | infer-union              |    32.5 |        78.6 |  2.4 |    1.87 |          2 |     1.55 | False |
| botocore           | tests-infer-union        |    25.8 |        86.5 |  3.4 |     4.8 |          4 |     6.17 | False |
| botocore           | tests                    |     1.2 |         0.8 |  0.7 |    0.12 |          1 |     0.15 | False |
| uvicorn            | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| uvicorn            | fix-certain              |     1.4 |         2.8 |  2.0 |    0.26 |          2 |     0.32 | False |
| uvicorn            | fix-likely               |     2.4 |         3.8 |  1.6 |     0.3 |          2 |     0.34 | False |
| uvicorn            | fix-unsafe               |     3.4 |         3.9 |  1.1 |     0.3 |          2 |     0.37 | False |
| uvicorn            | infer-basedpyright       |    16.9 |        23.6 |  1.4 |    0.99 |          1 |     0.29 | False |
| uvicorn            | infer-ty                 |     6.0 |         5.7 |  1.0 |    0.37 |          1 |     0.16 | False |
| uvicorn            | infer-pyrefly            |     3.8 |         8.8 |  2.3 |    0.76 |          1 |     0.32 | False |
| uvicorn            | census                   |     1.2 |         1.5 |  1.2 |    0.18 |          1 |     0.22 | False |
| uvicorn            | coverage                 |     1.6 |         1.0 |  0.6 |    0.15 |          1 |     0.19 | False |
| uvicorn            | timing                   |     1.0 |         1.1 |  1.1 |    0.18 |         16 |     0.22 | False |
| uvicorn            | traced                   |    47.4 |        30.0 |  0.6 |    0.96 |          1 |     1.19 | False |
| uvicorn            | tests-released           |    30.9 |        21.3 |  0.7 |    0.83 |          1 |     1.05 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.02 | False |
| uvicorn            | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.97 | False |
| uvicorn            | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.99 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.02 | False |
| uvicorn            | infer-union              |    18.0 |        27.5 |  1.5 |    0.95 |          1 |     0.16 | False |
| uvicorn            | tests-infer-union        |    29.1 |        20.8 |  0.7 |    0.85 |          1 |     1.01 | False |
| uvicorn            | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-released           |     2.8 |         1.6 |  0.6 |    0.13 |          1 |     0.16 | False |
| uvicorn            | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-infer-basedpyright |     2.4 |         1.6 |  0.7 |    0.12 |          1 |     0.16 | False |
| uvicorn            | types-infer-ty           |     2.8 |         1.6 |  0.6 |    0.13 |          1 |     0.15 | False |
| uvicorn            | types-infer-pyrefly      |     1.6 |         1.0 |  0.6 |    0.13 |          1 |     0.14 | False |
| uvicorn            | types-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.16 | False |
| uvicorn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     1.6 |         2.6 |  1.6 |    0.25 |          2 |     0.31 | False |
| mcp                | fix-certain              |     3.0 |         6.8 |  2.3 |    0.33 |          2 |      0.4 | False |
| mcp                | fix-likely               |     4.8 |         9.6 |  2.0 |     0.4 |          3 |     0.49 | False |
| mcp                | fix-unsafe               |     7.9 |        10.5 |  1.3 |    0.43 |          2 |     0.42 | False |
| mcp                | infer-basedpyright       |    17.6 |        47.5 |  2.7 |    2.34 |          1 |     0.24 | False |
| mcp                | infer-ty                 |     9.8 |        13.7 |  1.4 |    0.81 |          1 |     0.24 | False |
| mcp                | infer-pyrefly            |    12.0 |        21.6 |  1.8 |    1.67 |          1 |     0.25 | False |
| mcp                | census                   |     0.8 |         0.7 |  0.9 |    0.04 |          2 |     0.31 | False |
| mcp                | coverage                 |     1.2 |         1.5 |  1.2 |    0.18 |          2 |     0.21 | False |
| mcp                | timing                   |     2.0 |         2.5 |  1.2 |    0.25 |         16 |     0.31 | False |
| mcp                | traced                   |    19.0 |        86.4 |  4.5 |    2.06 |          6 |     2.51 | False |
| mcp                | tests-released           |    16.4 |        73.0 |  4.5 |    1.83 |          6 |     2.29 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     2.24 | False |
| mcp                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.52 | False |
| mcp                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     2.24 | False |
| mcp                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.29 | False |
| mcp                | infer-union              |    19.8 |        76.4 |  3.9 |    2.01 |          1 |     0.25 | False |
| mcp                | tests-infer-union        |    25.5 |        81.0 |  3.2 |     1.8 |          6 |     2.24 | False |
| mcp                | tests                    |     0.8 |         0.5 |  0.6 |    0.15 |          2 |     0.15 | False |
| mcp                | types-released           |    26.7 |        27.7 |  1.0 |    1.21 |          1 |      1.5 | False |
| mcp                | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      1.6 | False |
| mcp                | types-fix-likely         |    17.8 |        25.4 |  1.4 |    1.26 |          2 |     1.57 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.57 | False |
| mcp                | types-infer-basedpyright |    18.2 |        26.1 |  1.4 |    1.28 |          2 |      1.6 | False |
| mcp                | types-infer-ty           |    16.4 |        24.2 |  1.5 |    1.28 |          2 |     1.56 | False |
| mcp                | types-infer-pyrefly      |    19.2 |        26.1 |  1.4 |    1.26 |          2 |     1.54 | False |
| mcp                | types-infer-trace        |    22.1 |        26.8 |  1.2 |    1.23 |          2 |     1.57 | False |
| mcp                | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     2.0 |         4.7 |  2.4 |     0.4 |          2 |      0.5 | False |
| textual            | fix-certain              |     4.6 |        12.5 |  2.7 |    0.54 |          3 |     0.67 | False |
| textual            | fix-likely               |     6.2 |        17.7 |  2.9 |    0.54 |          3 |     0.66 | False |
| textual            | fix-unsafe               |     6.8 |        17.9 |  2.6 |    0.53 |          2 |     0.67 | False |
| textual            | infer-basedpyright       |    29.0 |        95.2 |  3.3 |    3.22 |          1 |     0.33 | False |
| textual            | infer-ty                 |    10.4 |        29.6 |  2.8 |    1.88 |          1 |     0.23 | False |
| textual            | infer-pyrefly            |     8.8 |        31.2 |  3.5 |     2.0 |          1 |     0.22 | False |
| textual            | census                   |     2.0 |         1.7 |  0.8 |    0.06 |          2 |      0.5 | False |
| textual            | coverage                 |     1.2 |         2.8 |  2.3 |    0.24 |          2 |      0.3 | False |
| textual            | timing                   |     4.0 |         5.6 |  1.4 |     0.4 |         16 |      0.5 | False |
| pdm                | check                    |     1.2 |         0.2 |  0.2 |    0.04 |          2 |     0.52 | False |
| pdm                | fix-certain              |     3.6 |         8.4 |  2.3 |    0.46 |          2 |     0.56 | False |
| pdm                | fix-likely               |     5.2 |        11.4 |  2.2 |    0.51 |          3 |     0.64 | False |
| pdm                | fix-unsafe               |     9.8 |        13.5 |  1.4 |     0.5 |          2 |     0.62 | False |
| pdm                | infer-basedpyright       |    25.4 |        60.4 |  2.4 |    2.48 |          1 |     0.32 | False |
| pdm                | infer-ty                 |    12.2 |        19.2 |  1.6 |    1.53 |          1 |     0.32 | False |
| pdm                | infer-pyrefly            |    18.9 |        28.5 |  1.5 |    1.89 |          1 |     0.32 | False |
| pdm                | census                   |     1.8 |         3.1 |  1.7 |    0.42 |          2 |     0.52 | False |
| pdm                | coverage                 |     1.0 |         1.7 |  1.7 |    0.19 |          2 |     0.22 | False |
| pdm                | timing                   |     2.8 |         3.6 |  1.3 |    0.42 |         16 |     0.52 | False |
| pdm                | traced                   |    23.4 |       113.6 |  4.9 |    1.53 |          7 |     1.82 | False |
| pdm                | tests-released           |    20.4 |       101.5 |  5.0 |    1.22 |          8 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.61 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      1.5 | False |
| pdm                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.47 | False |
| pdm                | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.61 | False |
| pdm                | infer-union              |    23.8 |        89.4 |  3.8 |    2.32 |          2 |     0.65 | False |
| pdm                | tests-infer-union        |    14.2 |        79.0 |  5.6 |    1.21 |          7 |     1.51 | False |
| pdm                | tests                    |     0.8 |         0.6 |  0.7 |    0.12 |          2 |     0.15 | False |
| strawberry-graphql | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.41 | False |
| strawberry-graphql | fix-certain              |     5.2 |        10.3 |  2.0 |    0.42 |          2 |     0.52 | False |
| strawberry-graphql | fix-likely               |     4.8 |        11.1 |  2.3 |    0.53 |          2 |     0.66 | False |
| strawberry-graphql | fix-unsafe               |     6.4 |        11.9 |  1.9 |    0.46 |          2 |     0.56 | False |
| strawberry-graphql | infer-basedpyright       |    46.1 |       107.3 |  2.3 |     2.9 |          1 |     0.29 | False |
| strawberry-graphql | infer-ty                 |    21.2 |        24.9 |  1.2 |     1.6 |          1 |     0.29 | False |
| strawberry-graphql | infer-pyrefly            |    19.9 |        39.4 |  2.0 |    2.01 |          1 |     0.29 | False |
| strawberry-graphql | census                   |     2.4 |         4.3 |  1.8 |    0.33 |          2 |     0.41 | False |
| strawberry-graphql | coverage                 |     0.8 |         1.5 |  1.9 |    0.18 |          2 |     0.22 | False |
| strawberry-graphql | timing                   |     2.6 |         3.6 |  1.4 |    0.33 |         16 |     0.41 | False |
| strawberry-graphql | traced                   |    21.4 |       110.7 |  5.2 |     1.5 |          8 |     1.86 | False |
| strawberry-graphql | tests-released           |    13.6 |        77.3 |  5.7 |    1.27 |          7 |     1.57 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.56 | False |
| strawberry-graphql | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     1.54 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.52 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.55 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.59 | False |
| strawberry-graphql | infer-union              |    31.9 |       108.2 |  3.4 |    2.22 |          1 |     0.29 | False |
| strawberry-graphql | tests-infer-union        |    20.4 |        86.8 |  4.3 |    1.27 |          7 |     1.59 | False |
| strawberry-graphql | tests                    |     0.8 |         0.7 |  0.9 |    0.12 |          2 |     0.15 | False |
| strawberry-graphql | types-released           |     4.0 |         2.1 |  0.5 |    0.22 |          1 |     0.27 | False |
| strawberry-graphql | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-basedpyright |     3.6 |         2.0 |  0.6 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-ty           |     3.6 |         2.2 |  0.6 |    0.24 |          1 |     0.29 | False |
| strawberry-graphql | types-infer-pyrefly      |     3.2 |         1.9 |  0.6 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-trace        |     3.2 |         1.9 |  0.6 |    0.24 |          1 |     0.27 | False |
| strawberry-graphql | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     1.8 |         0.3 |  0.2 |    0.04 |          2 |     0.47 | False |
| pygments           | fix-certain              |     8.8 |        17.3 |  2.0 |     0.5 |          3 |     0.64 | False |
| pygments           | fix-likely               |     7.2 |        18.4 |  2.6 |    0.55 |          3 |     0.67 | False |
| pygments           | fix-unsafe               |     7.4 |        17.5 |  2.4 |    0.54 |          3 |     0.66 | False |
| pygments           | infer-basedpyright       |    69.1 |       108.2 |  1.6 |    2.23 |          1 |     0.33 | False |
| pygments           | infer-ty                 |    18.0 |        28.6 |  1.6 |    1.42 |          1 |     0.34 | False |
| pygments           | infer-pyrefly            |    20.6 |        33.4 |  1.6 |    1.64 |          1 |     0.34 | False |
| pygments           | census                   |     7.4 |         8.9 |  1.2 |    0.38 |          2 |     0.47 | False |
| pygments           | coverage                 |     3.0 |         3.7 |  1.2 |     0.2 |          3 |     0.25 | False |
| pygments           | timing                   |     4.0 |         5.8 |  1.4 |    0.38 |         16 |     0.47 | False |
| pygments           | traced                   |    44.9 |        40.8 |  0.9 |    0.63 |          1 |     0.79 | False |
| pygments           | tests-released           |    23.8 |        15.7 |  0.7 |    0.28 |          1 |     0.36 | False |
| pygments           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.35 | False |
| pygments           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | infer-union              |   143.5 |       239.3 |  1.7 |    2.55 |          2 |     2.85 | False |
| pygments           | tests-infer-union        |    23.3 |        16.2 |  0.7 |    0.29 |          1 |     0.36 | False |
| pygments           | tests                    |     1.0 |         0.8 |  0.8 |    0.12 |          1 |     0.15 | False |
| streamlink         | check                    |     0.4 |         0.1 |  0.2 |    0.04 |          2 |     0.39 | False |
| streamlink         | fix-certain              |     6.0 |        12.6 |  2.1 |    0.41 |          3 |     0.52 | False |
| streamlink         | fix-likely               |     9.2 |        15.8 |  1.7 |    0.49 |          2 |     0.57 | False |
| streamlink         | fix-unsafe               |    13.2 |        17.0 |  1.3 |    0.45 |          2 |     0.56 | False |
| streamlink         | infer-basedpyright       |    21.6 |        50.9 |  2.4 |    2.04 |          1 |      0.2 | False |
| streamlink         | infer-ty                 |    19.4 |        25.7 |  1.3 |    0.93 |          1 |     0.29 | False |
| streamlink         | infer-pyrefly            |    15.5 |        29.0 |  1.9 |    1.61 |          1 |     0.29 | False |
| streamlink         | census                   |     3.6 |         5.6 |  1.6 |    0.31 |          2 |     0.39 | False |
| streamlink         | coverage                 |     1.6 |         2.1 |  1.3 |    0.21 |          2 |     0.26 | False |
| streamlink         | timing                   |     3.2 |         4.5 |  1.4 |    0.32 |         16 |     0.39 | False |
| streamlink         | traced                   |    32.7 |        31.3 |  1.0 |    0.46 |          1 |     0.56 | False |
| streamlink         | tests-released           |    22.3 |        14.0 |  0.6 |    0.18 |          1 |     0.25 | False |
| streamlink         | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| streamlink         | infer-union              |    54.5 |       190.6 |  3.5 |    2.34 |          1 |     0.33 | False |
| streamlink         | tests-infer-union        |    24.4 |        14.5 |  0.6 |     0.2 |          1 |     0.25 | False |
| streamlink         | tests                    |     1.2 |         0.8 |  0.7 |    0.15 |          1 |     0.15 | False |
| streamlink         | types-released           |     7.8 |         6.0 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.04 |          1 |     0.44 | False |
| streamlink         | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.44 | False |
| streamlink         | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.45 | False |
| streamlink         | types-infer-basedpyright |    13.3 |         7.6 |  0.6 |    0.38 |          1 |     0.46 | False |
| streamlink         | types-infer-ty           |    10.2 |         7.3 |  0.7 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |    11.5 |         7.6 |  0.7 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |    14.8 |         7.9 |  0.5 |     0.4 |          1 |     0.46 | False |
| streamlink         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     2.4 |         6.5 |  2.7 |    0.43 |          2 |     0.54 | False |
| sphinx             | fix-certain              |     8.2 |        22.7 |  2.8 |    0.63 |          3 |     0.77 | False |
| sphinx             | fix-likely               |    18.8 |        32.8 |  1.7 |    0.76 |          4 |     0.94 | False |
| sphinx             | fix-unsafe               |    16.2 |        33.6 |  2.1 |    0.73 |          3 |     0.82 | False |
| sphinx             | infer-basedpyright       |    55.9 |       102.8 |  1.8 |    2.63 |          1 |     0.32 | False |
| sphinx             | infer-ty                 |    26.5 |        48.1 |  1.8 |    1.56 |          1 |     0.32 | False |
| sphinx             | infer-pyrefly            |    23.5 |        44.0 |  1.9 |    2.31 |          1 |     0.32 | False |
| sphinx             | census                   |     1.8 |         1.6 |  0.9 |    0.07 |          2 |     0.54 | False |
| sphinx             | coverage                 |     1.8 |         3.5 |  1.9 |    0.26 |          2 |     0.32 | False |
| sphinx             | timing                   |     5.8 |         8.8 |  1.5 |    0.43 |         16 |     0.54 | False |
| sphinx             | traced                   |    31.7 |       176.2 |  5.6 |    1.68 |          8 |     2.05 | False |
| sphinx             | tests-released           |    17.6 |       116.1 |  6.6 |    1.37 |          8 |     1.69 | False |
| sphinx             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.04 |          8 |     1.65 | False |
| sphinx             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.04 |          8 |     1.65 | False |
| sphinx             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.04 |          8 |     1.65 | False |
| sphinx             | tests-infer-basedpyright |    15.6 |       107.1 |  6.9 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-infer-ty           |    15.6 |       105.7 |  6.8 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-infer-pyrefly      |    15.6 |       106.8 |  6.8 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-infer-trace        |    13.6 |        97.3 |  7.2 |    1.33 |          8 |     1.65 | False |
| sphinx             | infer-union              |    52.5 |       116.2 |  2.2 |    2.32 |          1 |     0.32 | False |
| sphinx             | tests-infer-union        |    16.6 |       113.7 |  6.8 |    1.32 |          8 |     1.65 | False |
| sphinx             | tests                    |     0.6 |         0.4 |  0.7 |    0.12 |          1 |     0.15 | False |
| sphinx             | types-released           |    13.4 |         7.5 |  0.6 |    0.32 |          1 |     0.37 | False |
| sphinx             | types-fix-certain        |    10.2 |         6.8 |  0.7 |    0.27 |          1 |     0.32 | False |
| sphinx             | types-fix-likely         |    12.2 |         7.1 |  0.6 |    0.26 |          1 |     0.32 | False |
| sphinx             | types-fix-unsafe         |     1.0 |         0.3 |  0.3 |    0.04 |          1 |     0.34 | False |
| sphinx             | types-infer-basedpyright |     8.4 |         6.3 |  0.8 |    0.27 |          1 |     0.31 | False |
| sphinx             | types-infer-ty           |     9.6 |         6.6 |  0.7 |    0.29 |          1 |      0.4 | False |
| sphinx             | types-infer-pyrefly      |     8.8 |         6.2 |  0.7 |    0.26 |          1 |     0.31 | False |
| sphinx             | types-infer-trace        |     5.2 |         4.9 |  0.9 |    0.32 |          1 |     0.35 | False |
| sphinx             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     1.8 |         2.4 |  1.3 |    0.23 |          2 |     0.29 | False |
| tox                | fix-certain              |     3.4 |         6.4 |  1.9 |    0.34 |          2 |     0.37 | False |
| tox                | fix-likely               |     5.2 |         8.7 |  1.7 |    0.37 |          2 |     0.46 | False |
| tox                | fix-unsafe               |     3.4 |         7.4 |  2.2 |    0.32 |          2 |     0.39 | False |
| tox                | infer-basedpyright       |    19.7 |        44.4 |  2.3 |    2.19 |          1 |     0.23 | False |
| tox                | infer-ty                 |     8.8 |        16.5 |  1.9 |    1.16 |          1 |     0.22 | False |
| tox                | infer-pyrefly            |    14.5 |        13.8 |  1.0 |     1.0 |          1 |     0.23 | False |
| tox                | census                   |     1.2 |         0.7 |  0.6 |    0.04 |          2 |     0.29 | False |
| tox                | coverage                 |     1.0 |         1.4 |  1.4 |    0.17 |          2 |     0.21 | False |
| tox                | timing                   |     1.8 |         2.4 |  1.3 |    0.23 |         16 |     0.29 | False |
| tox                | traced                   |    34.3 |       151.2 |  4.4 |    1.57 |          7 |     1.85 | False |
| tox                | tests-released           |    17.8 |       104.5 |  5.9 |    1.36 |          8 |     1.67 | False |
| tox                | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.64 | False |
| tox                | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.66 | False |
| tox                | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.64 | False |
| tox                | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.65 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.65 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.62 | False |
| tox                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.71 | False |
| tox                | infer-union              |    25.1 |        57.7 |  2.3 |    1.94 |          3 |     0.46 | False |
| tox                | tests-infer-union        |    22.8 |       115.0 |  5.0 |    1.37 |          7 |      1.7 | False |
| tox                | tests                    |     1.2 |         0.7 |  0.6 |    0.12 |          1 |     0.15 | False |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,231 |       4,159 |     1 |
| sphinx | likely             |          929 | 3,752 |       4,680 |     1 |
| sphinx | unsafe             |          929 | 4,131 |       5,059 |     1 |
| sphinx | infer-basedpyright |          929 | 4,935 |       5,863 |     1 |
| sphinx | infer-ty           |          929 | 4,992 |       5,920 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,204 |       6,132 |     1 |
| sphinx | infer-trace        |          929 | 4,131 |       5,059 |     1 |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus             | released                                                             | traced                                                               | same failures |
| ------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------- |
| django             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped           | 5 expected failures, 6 failures, 17,585 ran, 1,149 skipped           | False         |
| sqlalchemy         | 29,521 passed, 975 skipped                                           | 29,521 passed, 975 skipped                                           | True          |
| pydantic           | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     | True          |
| pandas             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              | True          |
| structlog          | 24 failed, 860 passed, 37 skipped                                    | 24 failed, 860 passed, 37 skipped                                    | True          |
| attrs              | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         | True          |
| click              | 1,991 passed, 24 skipped, 1 xfailed                                  | 1,991 passed, 24 skipped, 1 xfailed                                  | True          |
| hypercorn          | 2 failed, 194 passed                                                 | 2 failed, 194 passed                                                 | True          |
| starlette          | 1,271 passed, 2 skipped, 2 xfailed                                   | 1,271 passed, 2 skipped, 2 xfailed                                   | True          |
| werkzeug           | 1 failed, 979 passed, 1 skipped                                      | 1 failed, 979 passed, 1 skipped                                      | True          |
| mkdocs             | 2 errors, 2 failures, 724 ran, 4 skipped                             | 2 errors, 2 failures, 724 ran, 4 skipped                             | True          |
| httpx              | 1 failed, 1,416 passed, 1 skipped                                    | 1 failed, 1,416 passed, 1 skipped                                    | True          |
| black              | 519 passed, 1 skipped                                                | 519 passed, 1 skipped                                                | True          |
| fastapi            | 3,551 passed, 17 skipped, 4 xfailed                                  | 3,551 passed, 17 skipped, 4 xfailed                                  | True          |
| cattrs             | 994 passed, 15 xfailed                                               | 994 passed, 15 xfailed                                               | True          |
| pytest             | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed | True          |
| botocore           | 7 failed, 4,593 passed, 96 skipped                                   | 7 failed, 4,593 passed, 96 skipped                                   | True          |
| uvicorn            | 1,350 passed, 12 skipped                                             | 1,350 passed, 12 skipped                                             | True          |
| mcp                | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         | False         |
| pdm                | 1,472 passed, 1 skipped                                              | 1,472 passed, 1 skipped                                              | True          |
| strawberry-graphql | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          | False         |
| pygments           | 1 failed, 5,330 passed, 15 skipped                                   | 1 failed, 5,330 passed, 15 skipped                                   | True          |
| streamlink         | 9 error, 15 failed, 7,233 passed, 36 skipped                         | 9 error, 15 failed, 7,233 passed, 36 skipped                         | True          |
| sphinx             | 9 failed, 2,393 passed, 22 skipped                                   | 10 failed, 2,392 passed, 22 skipped                                  | False         |
| tox                | 6 error, 17 failed, 8,525 passed, 31 skipped                         | 6 error, 17 failed, 8,525 passed, 31 skipped                         | True          |

- standard library, super+dev, infer-basedpyright: held 11.83 GB beside other steps
- standard library, super+dev, infer-ty: held 12.47 GB beside other steps
- standard library, super+dev, infer-pyrefly: held 14.87 GB beside other steps
- django, super+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, super+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, super+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, super+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, super+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, super+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, super+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- pydantic, super+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pydantic, super+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pandas, super+dev, infer-basedpyright: held 13.61 GB beside other steps
- pandas, super+dev, infer-ty: held 11.15 GB beside other steps
- pandas, super+dev, infer-pyrefly: held 15.38 GB beside other steps
- pandas, super+dev, traced: held 12.52 GB beside other steps
- pandas, super+dev, tests-released: held 11.49 GB beside other steps
- pandas, super+dev, infer-union: held 14.56 GB beside other steps
- pandas, super+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, super+dev, infer-union: pyrefly's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, super+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, super+dev, tests-infer-union: held 11.5 GB beside other steps
- structlog, super+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- structlog, super+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- structlog, super+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- attrs, super+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, super+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, super+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- click, super+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- click, super+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, super+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, super+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- hypercorn, super+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, super+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- starlette, super+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- starlette, super+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, super+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, super+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- werkzeug, super+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, super+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- mkdocs, super+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, super+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, super+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- httpx, super+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- httpx, super+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- httpx, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, super+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, super+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- fastapi, super+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- fastapi, super+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, super+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- cattrs, super+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, super+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, super+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pytest, super+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, super+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, super+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its seconds
  measure less of the checker
- botocore, super+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- botocore, super+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- botocore, super+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- uvicorn, super+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- uvicorn, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- uvicorn, super+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, super+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mcp, super+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- textual, super+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the
  store, so its seconds measure less of the checker
- textual, super+dev, infer-ty: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- textual, super+dev, infer-pyrefly: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, super+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, super+dev, infer-union: pyrefly's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pdm, super+dev, infer-union: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- strawberry-graphql, super+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, super+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- strawberry-graphql, super+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- pygments, super+dev, infer-basedpyright: basedpyright's hints for 1 of 4 rounds came from the
  store, so its seconds measure less of the checker
- pygments, super+dev, infer-ty: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pygments, super+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, super+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- streamlink, super+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- streamlink, super+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, super+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, super+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, super+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, super+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, super+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
