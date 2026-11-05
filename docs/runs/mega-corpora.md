# Mega corpora

The run `mega` (`python -m tests.corpus`) on mega: constricter 0.4.5.dev1+gd61ea5d39.d20261029
(`866d2e2fa488`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 83 minutes. Timings don't compare across machines, nor their seconds across runs, taken
beside the other steps: their instructions do.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter |  Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |     `LVA006` |  `LVA009` | `LVA010` | `LVA011` |   Total |
| ------------------ | -------- | ----------- | -----: | --------------: | ------------: | -------: | -------------: | -----------: | -----------: | --------: | -------: | -------: | ------: |
| standard library   | 3.14.7   | mega+dev    |  1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |           14 |         8 |        0 |        0 | 113,750 |
| django             | 5.2.18   | mega+dev    |    883 |           9,926 |         2,166 |        0 |          5,084 |            0 |            0 |         1 |        0 |        0 |  17,177 |
| sqlalchemy         | 2.1.4    | mega+dev    |    258 |           8,825 |         1,636 |        0 |          2,471 |          572 |          128 |         2 |        0 |        1 |  13,635 |
| pydantic           | 2.14.0   | mega+dev    |    105 |           2,072 |           440 |        0 |            605 |          184 |           15 |         0 |        0 |        0 |   3,316 |
| pandas             | 3.0.6    | mega+dev    |  1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |            2 |         1 |        0 |        1 |  77,931 |
| twisted            | 12.3.0   | mega+dev    |    819 |          13,310 |         1,349 |        0 |          3,215 |            0 |            0 |         0 |        0 |        0 |  17,874 |
| pip                | 20.3.4   | mega+dev    |    366 |           5,902 |         1,150 |        0 |          1,871 |            0 |            0 |         0 |        0 |        0 |   8,923 |
| structlog          | 26.1.0   | mega+dev    |     21 |             156 |            47 |        0 |            113 |           12 |            1 |         0 |        0 |        0 |     329 |
| attrs              | 26.1.0   | mega+dev    |     13 |             285 |            50 |        0 |             58 |            2 |            0 |         1 |        0 |        0 |     396 |
| click              | 8.5.0    | mega+dev    |     17 |             481 |            58 |        0 |             68 |           28 |            1 |         0 |        0 |        0 |     636 |
| hypercorn          | 0.18.0   | mega+dev    |     39 |             220 |            67 |        0 |             68 |            8 |            0 |         0 |        0 |        0 |     363 |
| starlette          | 1.7.0    | mega+dev    |     36 |             499 |            99 |        0 |            146 |           18 |            0 |         0 |        0 |        0 |     762 |
| werkzeug           | 3.1.9    | mega+dev    |     52 |             835 |           235 |        0 |            223 |           15 |            1 |         0 |        0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | mega+dev    |     61 |           1,674 |           198 |        0 |            459 |            8 |            0 |         0 |        0 |        0 |   2,339 |
| httpx              | 0.28.1   | mega+dev    |     23 |             395 |           112 |        0 |             62 |            1 |            0 |         0 |        0 |        0 |     570 |
| black              | 26.10.0  | mega+dev    |     25 |             996 |           232 |        0 |             45 |            5 |            4 |         0 |        0 |        0 |   1,282 |
| fastapi            | 0.142.2  | mega+dev    |     52 |             586 |           105 |        0 |             51 |           98 |            5 |         0 |        0 |        0 |     845 |
| cattrs             | 26.2.1   | mega+dev    |     36 |             420 |            70 |        0 |             30 |            9 |            1 |         0 |        0 |        0 |     530 |
| pytest             | 9.1.1    | mega+dev    |     78 |           2,363 |           470 |        0 |            167 |           33 |            9 |         0 |        0 |        0 |   3,042 |
| botocore           | 1.43.108 | mega+dev    |     76 |           2,825 |           367 |        0 |            594 |            2 |            0 |         0 |        0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | mega+dev    |     45 |             363 |            71 |        0 |             55 |           11 |            4 |         0 |        0 |        0 |     504 |
| mcp                | 2.3.0    | mega+dev    |    124 |           1,356 |           173 |        0 |            191 |          105 |            8 |         0 |        0 |        0 |   1,833 |
| textual            | 8.2.8    | mega+dev    |    247 |           4,979 |           718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| pdm                | 2.29.2   | mega+dev    |    128 |           2,114 |           417 |        0 |            182 |           37 |            2 |         0 |        0 |        0 |   2,752 |
| strawberry-graphql | 0.332.0  | mega+dev    |    244 |           1,436 |           243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| pygments           | 2.21.0   | mega+dev    |    343 |           1,124 |           539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| streamlink         | 8.6.1    | mega+dev    |    227 |           2,080 |           310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| sphinx             | 9.1.0    | mega+dev    |    243 |           5,505 |         1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| tox                | 4.64.9   | mega+dev    |    129 |           1,369 |           286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| pint               | 0.26.1   | mega+dev    |    109 |           2,591 |           297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| altair             | 6.3.0    | mega+dev    |     55 |             814 |           130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| seaborn            | 0.13.2   | mega+dev    |     54 |           2,361 |           370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| aiohttp            | 3.14.4   | mega+dev    |     54 |           1,307 |           195 |        0 |            355 |           13 |            5 |         2 |        0 |        0 |   1,877 |
| websockets         | 17.2     | mega+dev    |     52 |             605 |            85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| anyio              | 4.15.1   | mega+dev    |     46 |             615 |            77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| zarr               | 3.4.0    | mega+dev    |     98 |           1,874 |           370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| joblib             | 1.6.0    | mega+dev    |     73 |           1,842 |           158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| networkx           | 3.7      | mega+dev    |    583 |          18,854 |         3,221 |        0 |            381 |            8 |            0 |         0 |        0 |        0 |  22,464 |
| nibabel            | 5.4.2    | mega+dev    |    229 |           6,504 |         1,032 |        0 |            930 |            5 |            1 |         0 |        0 |        0 |   8,472 |
| narwhals           | 2.26.0   | mega+dev    |    162 |           2,775 |           106 |        0 |            231 |           62 |            5 |         0 |        0 |        0 |   3,179 |
| xarray             | 2026.9.0 | mega+dev    |    199 |          18,968 |         1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| litestar           | 2.24.0   | mega+dev    |    374 |           1,474 |           306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| stripe             | 16.0.0   | mega+dev    |  1,460 |           1,772 |            49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| celery             | 5.6.3    | mega+dev    |    161 |           2,202 |           331 |        0 |          1,214 |            0 |            0 |         2 |        0 |        0 |   3,749 |
| optuna             | 5.0.0    | mega+dev    |    220 |           2,740 |           446 |        0 |            409 |           28 |            4 |         0 |        0 |        0 |   3,627 |
| dask               | 2026.8.0 | mega+dev    |    361 |          20,748 |         1,691 |        0 |          1,732 |           76 |            5 |         2 |        0 |        1 |  24,255 |
| mypy               | 2.4.0    | mega+dev    |    195 |           9,008 |         2,197 |        0 |            196 |          340 |           45 |         0 |        1 |        1 |  11,788 |
| **Total**          |          | mega+dev    | 12,462 | 331,082 (78.0%) | 40,716 (9.6%) | 1 (0.0%) | 48,497 (11.4%) | 2,754 (0.6%) | 1,273 (0.3%) | 28 (0.0%) | 1 (0.0%) | 7 (0.0%) | 424,359 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |           Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | ----------- | ----------: | ---------------: | --------------: | ----------: | --------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | mega+dev    | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,325 (32.8%) |   6,945 (6.1%) | 14,198 (12.5%) |      0 |    0 |            0 |
| django             | mega+dev    |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |   2,622 (15.3%) |     726 (4.2%) |  2,883 (16.8%) |      0 |    0 |            0 |
| sqlalchemy         | mega+dev    |  0 / 12,934 |   11,296 / 2,339 |    12,934 / 701 |  13,635 / 0 |   2,144 (15.7%) |     445 (3.3%) |   1,152 (8.4%) |      0 |    0 |            0 |
| pydantic           | mega+dev    |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |   1,196 (36.1%) |     150 (4.5%) |    413 (12.5%) |      0 |    0 |            0 |
| pandas             | mega+dev    |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  17,186 (22.1%) | 24,507 (31.4%) | 25,784 (33.1%) |      0 |    0 |            0 |
| twisted            | mega+dev    |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,435 (13.6%) |  3,741 (20.9%) |  4,829 (27.0%) |      0 |    0 |            0 |
| pip                | mega+dev    |   0 / 8,923 |    7,773 / 1,150 |       8,923 / 0 |   8,923 / 0 |   2,242 (25.1%) |     490 (5.5%) |  1,342 (15.0%) |      0 |    0 |            0 |
| structlog          | mega+dev    |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |      98 (29.8%) |      15 (4.6%) |      28 (8.5%) |      0 |    0 |            0 |
| attrs              | mega+dev    |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |      93 (23.5%) |       9 (2.3%) |      14 (3.5%) |      0 |    0 |            0 |
| click              | mega+dev    |     0 / 607 |         549 / 87 |        607 / 29 |     636 / 0 |     311 (48.9%) |      27 (4.2%) |     64 (10.1%) |      0 |    0 |            0 |
| hypercorn          | mega+dev    |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |     137 (37.7%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | mega+dev    |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |     321 (42.1%) |      75 (9.8%) |    116 (15.2%) |      0 |    0 |            0 |
| werkzeug           | mega+dev    |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |     545 (41.6%) |      72 (5.5%) |    138 (10.5%) |      0 |    0 |            0 |
| mkdocs             | mega+dev    |   0 / 2,331 |      2,133 / 206 |       2,331 / 8 |   2,339 / 0 |     826 (35.3%) |    430 (18.4%) |    552 (23.6%) |      0 |    0 |            0 |
| httpx              | mega+dev    |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |     240 (42.1%) |     69 (12.1%) |     84 (14.7%) |      0 |    0 |            0 |
| black              | mega+dev    |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |     714 (55.7%) |    128 (10.0%) |    169 (13.2%) |      0 |    0 |            0 |
| fastapi            | mega+dev    |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |     258 (30.5%) |      45 (5.3%) |      71 (8.4%) |      0 |    0 |            0 |
| cattrs             | mega+dev    |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     112 (21.1%) |      34 (6.4%) |      52 (9.8%) |      0 |    0 |            0 |
| pytest             | mega+dev    |   0 / 3,000 |      2,530 / 512 |      3,000 / 42 |   3,042 / 0 |   1,375 (45.2%) |     160 (5.3%) |    313 (10.3%) |      0 |    0 |            0 |
| botocore           | mega+dev    |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     548 (14.5%) |     182 (4.8%) |    656 (17.3%) |      0 |    0 |            0 |
| uvicorn            | mega+dev    |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     236 (46.8%) |      32 (6.3%) |     57 (11.3%) |      0 |    0 |            0 |
| mcp                | mega+dev    |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     718 (39.2%) |     162 (8.8%) |    248 (13.5%) |      0 |    0 |            0 |
| textual            | mega+dev    |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,795 (42.7%) |     508 (7.8%) |    774 (11.8%) |      0 |    0 |            0 |
| pdm                | mega+dev    |   0 / 2,713 |      2,296 / 456 |      2,713 / 39 |   2,752 / 0 |   1,246 (45.3%) |     218 (7.9%) |    364 (13.2%) |      0 |    0 |            0 |
| strawberry-graphql | mega+dev    |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     656 (33.7%) |     174 (8.9%) |    241 (12.4%) |      0 |    0 |            0 |
| pygments           | mega+dev    |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      735 (9.6%) |      81 (1.1%) |  4,617 (60.2%) |      0 |    0 |            0 |
| streamlink         | mega+dev    |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     701 (22.8%) |     136 (4.4%) |    578 (18.8%) |      0 |    0 |            0 |
| sphinx             | mega+dev    |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,392 (42.0%) |     538 (6.7%) |    942 (11.7%) |      0 |    0 |            0 |
| tox                | mega+dev    |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     985 (55.2%) |     103 (5.8%) |     158 (8.9%) |      0 |    0 |            0 |
| pint               | mega+dev    |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     649 (21.0%) |     275 (8.9%) |    327 (10.6%) |      0 |    0 |            0 |
| altair             | mega+dev    |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     389 (22.0%) |      52 (2.9%) |      65 (3.7%) |      0 |    0 |            0 |
| seaborn            | mega+dev    |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     657 (22.5%) |     164 (5.6%) |     242 (8.3%) |      0 |    0 |            0 |
| aiohttp            | mega+dev    |   0 / 1,859 |      1,662 / 215 |      1,859 / 18 |   1,877 / 0 |     722 (38.5%) |     152 (8.1%) |    274 (14.6%) |      0 |    0 |            0 |
| websockets         | mega+dev    |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     362 (45.8%) |      77 (9.7%) |    130 (16.4%) |      0 |    0 |            0 |
| anyio              | mega+dev    |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     230 (30.8%) |      36 (4.8%) |      69 (9.2%) |      0 |    0 |            0 |
| zarr               | mega+dev    |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,169 (47.3%) |      79 (3.2%) |     118 (4.8%) |      0 |    0 |            0 |
| joblib             | mega+dev    |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     179 (8.0%) |    301 (13.4%) |      0 |    0 |            0 |
| networkx           | mega+dev    |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |   3,971 (17.7%) |   2,206 (9.8%) |  2,522 (11.2%) |      0 |    0 |            0 |
| nibabel            | mega+dev    |   0 / 8,466 |    7,434 / 1,038 |       8,466 / 6 |   8,472 / 0 |   1,870 (22.1%) |     841 (9.9%) |  1,172 (13.8%) |      0 |    0 |            0 |
| narwhals           | mega+dev    |   0 / 3,112 |      3,006 / 173 |      3,112 / 67 |   3,179 / 0 |   1,082 (34.0%) |      76 (2.4%) |     131 (4.1%) |      0 |    0 |            0 |
| xarray             | mega+dev    |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   4,622 (21.4%) |  5,151 (23.8%) |  5,499 (25.4%) |      0 |    0 |            0 |
| litestar           | mega+dev    |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     648 (31.0%) |     124 (5.9%) |     198 (9.5%) |      0 |    0 |            0 |
| stripe             | mega+dev    |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     781 (18.5%) |     166 (3.9%) |    671 (15.9%) |      0 |    0 |            0 |
| celery             | mega+dev    |   0 / 3,749 |      3,416 / 333 |       3,749 / 0 |   3,749 / 0 |     508 (13.6%) |     130 (3.5%) |     371 (9.9%) |      0 |    0 |            0 |
| optuna             | mega+dev    |   0 / 3,595 |      3,149 / 478 |      3,595 / 32 |   3,627 / 0 |   1,583 (43.6%) |     219 (6.0%) |     327 (9.0%) |      0 |    0 |            0 |
| dask               | mega+dev    |  0 / 24,173 |   22,480 / 1,775 |     24,173 / 82 |  24,255 / 0 |   3,158 (13.0%) |   1,980 (8.2%) |  2,898 (11.9%) |      0 |    0 |            0 |
| mypy               | mega+dev    |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |   5,142 (43.6%) |  1,209 (10.3%) |  1,616 (13.7%) |      0 |    0 |            0 |
| **Total**          | mega+dev    | 0 / 420,324 | 379,579 / 44,779 | 420,323 / 4,036 | 424,359 / 0 | 110,260 (26.0%) | 53,338 (12.6%) | 77,826 (18.3%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | mega+dev    |              1.2% |         33.6% |            39.7% |                  46.0% | +32.5 pts, 32.8% of untyped | +44.8 pts, 45.3% of untyped |
| django             | mega+dev    |              0.0% |         15.3% |            19.5% |                  32.1% | +15.3 pts, 15.3% of untyped | +32.0 pts, 32.1% of untyped |
| sqlalchemy         | mega+dev    |             15.3% |         29.3% |            32.2% |                  36.8% | +14.0 pts, 16.5% of untyped | +21.5 pts, 25.4% of untyped |
| pydantic           | mega+dev    |             22.4% |         52.2% |            55.9% |                  62.5% | +29.8 pts, 38.4% of untyped | +40.0 pts, 51.6% of untyped |
| pandas             | mega+dev    |              1.6% |         23.3% |            54.3% |                  56.0% | +21.7 pts, 22.1% of untyped | +54.3 pts, 55.2% of untyped |
| twisted            | mega+dev    |              0.0% |         13.6% |            34.6% |                  40.6% | +13.6 pts, 13.6% of untyped | +40.6 pts, 40.6% of untyped |
| pip                | mega+dev    |              1.5% |         26.2% |            31.7% |                  41.1% | +24.7 pts, 25.1% of untyped | +39.5 pts, 40.1% of untyped |
| structlog          | mega+dev    |             25.6% |         48.7% |            52.2% |                  55.3% | +23.1 pts, 31.0% of untyped | +29.6 pts, 39.9% of untyped |
| attrs              | mega+dev    |              0.8% |         24.2% |            26.5% |                  27.8% | +23.5 pts, 23.7% of untyped | +27.0 pts, 27.2% of untyped |
| click              | mega+dev    |             31.5% |         66.5% |            69.6% |                  73.7% | +35.1 pts, 51.2% of untyped | +42.3 pts, 61.7% of untyped |
| hypercorn          | mega+dev    |             32.4% |         58.5% |            62.3% |                  69.5% | +26.1 pts, 38.6% of untyped | +37.1 pts, 54.9% of untyped |
| starlette          | mega+dev    |             10.3% |         49.0% |            58.0% |                  63.0% | +38.7 pts, 43.1% of untyped | +52.7 pts, 58.7% of untyped |
| werkzeug           | mega+dev    |             14.3% |         50.4% |            55.2% |                  59.6% | +36.1 pts, 42.2% of untyped | +45.3 pts, 52.8% of untyped |
| mkdocs             | mega+dev    |              4.5% |         38.4% |            56.0% |                  60.9% | +33.8 pts, 35.4% of untyped | +56.4 pts, 59.1% of untyped |
| httpx              | mega+dev    |              6.3% |         45.8% |            57.2% |                  59.6% | +39.5 pts, 42.2% of untyped | +53.4 pts, 56.9% of untyped |
| black              | mega+dev    |             15.9% |         63.1% |            71.5% |                  74.2% | +47.2 pts, 56.1% of untyped | +58.4 pts, 69.4% of untyped |
| fastapi            | mega+dev    |             42.0% |         62.2% |            65.7% |                  67.7% | +20.2 pts, 34.8% of untyped | +25.7 pts, 44.3% of untyped |
| cattrs             | mega+dev    |              7.0% |         27.0% |            33.1% |                  36.3% | +20.0 pts, 21.5% of untyped | +29.3 pts, 31.5% of untyped |
| pytest             | mega+dev    |             12.1% |         52.4% |            57.1% |                  61.5% | +40.2 pts, 45.8% of untyped | +49.4 pts, 56.2% of untyped |
| botocore           | mega+dev    |              0.5% |         14.9% |            19.7% |                  32.1% | +14.4 pts, 14.5% of untyped | +31.6 pts, 31.8% of untyped |
| uvicorn            | mega+dev    |             23.6% |         60.5% |            65.5% |                  69.4% | +36.9 pts, 48.3% of untyped | +45.8 pts, 59.9% of untyped |
| mcp                | mega+dev    |             30.7% |         59.6% |            66.2% |                  69.6% | +28.9 pts, 41.7% of untyped | +38.9 pts, 56.2% of untyped |
| textual            | mega+dev    |             15.6% |         52.0% |            58.6% |                  62.0% | +36.4 pts, 43.1% of untyped | +46.5 pts, 55.1% of untyped |
| pdm                | mega+dev    |             11.7% |         52.2% |            59.3% |                  64.0% | +40.5 pts, 45.8% of untyped | +52.3 pts, 59.2% of untyped |
| strawberry-graphql | mega+dev    |             30.1% |         55.5% |            62.2% |                  64.8% | +25.4 pts, 36.3% of untyped | +34.7 pts, 49.7% of untyped |
| pygments           | mega+dev    |              0.0% |          9.6% |            10.6% |                  69.8% |   +9.6 pts, 9.6% of untyped | +69.8 pts, 69.8% of untyped |
| streamlink         | mega+dev    |             42.8% |         56.0% |            58.6% |                  66.9% | +13.2 pts, 23.1% of untyped | +24.2 pts, 42.2% of untyped |
| sphinx             | mega+dev    |             10.4% |         48.5% |            54.6% |                  59.1% | +38.1 pts, 42.5% of untyped | +48.7 pts, 54.4% of untyped |
| tox                | mega+dev    |             16.0% |         63.0% |            67.9% |                  70.5% | +46.9 pts, 55.9% of untyped | +54.5 pts, 64.9% of untyped |
| pint               | mega+dev    |              5.1% |         25.1% |            33.6% |                  35.2% | +20.0 pts, 21.1% of untyped | +30.1 pts, 31.7% of untyped |
| altair             | mega+dev    |             49.7% |         61.2% |            62.8% |                  63.1% | +11.5 pts, 22.9% of untyped | +13.4 pts, 26.7% of untyped |
| seaborn            | mega+dev    |              6.9% |         28.0% |            33.3% |                  35.8% | +21.1 pts, 22.7% of untyped | +28.9 pts, 31.1% of untyped |
| aiohttp            | mega+dev    |             23.7% |         53.3% |            59.6% |                  64.6% | +29.7 pts, 38.9% of untyped | +40.9 pts, 53.6% of untyped |
| websockets         | mega+dev    |             13.8% |         53.3% |            61.7% |                  67.4% | +39.4 pts, 45.8% of untyped | +53.6 pts, 62.2% of untyped |
| anyio              | mega+dev    |             27.8% |         51.0% |            54.6% |                  58.0% | +23.2 pts, 32.2% of untyped | +30.2 pts, 41.8% of untyped |
| zarr               | mega+dev    |             21.7% |         59.7% |            62.2% |                  63.5% | +38.0 pts, 48.5% of untyped | +41.8 pts, 53.4% of untyped |
| joblib             | mega+dev    |              0.0% |         23.5% |            31.5% |                  36.9% | +23.4 pts, 23.4% of untyped | +36.9 pts, 36.9% of untyped |
| networkx           | mega+dev    |              0.3% |         17.9% |            27.7% |                  29.1% | +17.6 pts, 17.7% of untyped | +28.8 pts, 28.9% of untyped |
| nibabel            | mega+dev    |              1.0% |         22.8% |            32.7% |                  36.5% | +21.9 pts, 22.1% of untyped | +35.6 pts, 35.9% of untyped |
| narwhals           | mega+dev    |             21.7% |         48.9% |            50.8% |                  52.1% | +27.2 pts, 34.7% of untyped | +30.4 pts, 38.9% of untyped |
| xarray             | mega+dev    |              4.6% |         25.3% |            48.3% |                  49.8% | +20.7 pts, 21.7% of untyped | +45.2 pts, 47.4% of untyped |
| litestar           | mega+dev    |             44.9% |         63.7% |            67.2% |                  69.4% | +18.7 pts, 34.0% of untyped | +24.5 pts, 44.4% of untyped |
| stripe             | mega+dev    |             89.5% |         92.0% |            92.5% |                  94.1% |  +2.4 pts, 23.3% of untyped |  +4.5 pts, 43.3% of untyped |
| celery             | mega+dev    |              0.4% |         13.9% |            17.4% |                  23.8% | +13.5 pts, 13.6% of untyped | +23.4 pts, 23.5% of untyped |
| optuna             | mega+dev    |              7.5% |         48.2% |            53.8% |                  56.6% | +40.7 pts, 44.0% of untyped | +49.1 pts, 53.1% of untyped |
| dask               | mega+dev    |              1.1% |         14.0% |            22.1% |                  25.8% | +12.9 pts, 13.1% of untyped | +24.8 pts, 25.1% of untyped |
| mypy               | mega+dev    |             16.8% |         54.3% |            63.1% |                  66.1% | +37.5 pts, 45.1% of untyped | +49.3 pts, 59.3% of untyped |
| **Total**          | mega+dev    |             11.4% |         34.6% |            45.9% |                  51.0% | +23.2 pts, 26.2% of untyped | +39.7 pts, 44.7% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,325 |  37,325 |        |        |      0 |    0 | 38,654 |  115,001 |    91.7 |
| standard library   | likely             | 44,270 |  37,601 |  6,669 |        |      0 |    0 | 45,599 |  115,001 |   125.3 |
| standard library   | unsafe             | 51,523 |  37,333 |  6,649 |  7,541 |      0 |    0 | 52,852 |  115,001 |   119.5 |
| standard library   | infer-basedpyright | 59,239 |  37,335 |  7,061 | 14,843 |      0 |    7 | 60,568 |  115,001 |   196.0 |
| standard library   | infer-ty           | 57,011 |  37,369 |  7,043 | 12,599 |      0 |    4 | 58,340 |  115,001 |   149.8 |
| standard library   | infer-pyrefly      | 59,371 |  37,324 |  7,098 | 14,949 |      0 |   39 | 60,700 |  115,001 |   152.8 |
| django             | certain            |  2,622 |   2,622 |        |        |      0 |    0 |  2,627 |   17,181 |    22.8 |
| django             | likely             |  3,348 |   2,627 |    721 |        |      0 |    0 |  3,353 |   17,181 |    24.8 |
| django             | unsafe             |  5,505 |   2,622 |    719 |  2,164 |      0 |    0 |  5,510 |   17,181 |    18.9 |
| django             | infer-basedpyright |  5,889 |   2,616 |    732 |  2,541 |      0 |    0 |  5,894 |   17,181 |    25.0 |
| django             | infer-ty           |  5,707 |   2,623 |    727 |  2,357 |      0 |    0 |  5,712 |   17,181 |    37.5 |
| django             | infer-pyrefly      |  6,186 |   2,611 |    740 |  2,835 |      0 |    0 |  6,191 |   17,181 |    38.0 |
| django             | infer-trace        |  6,049 |   2,622 |    749 |  2,678 |      0 |    0 |  6,054 |   17,181 |    12.7 |
| sqlalchemy         | certain            |  2,144 |   2,144 |        |        |      0 |    0 |  4,479 |   15,304 |    26.1 |
| sqlalchemy         | likely             |  2,589 |   2,152 |    437 |        |      0 |    0 |  4,924 |   15,304 |    51.3 |
| sqlalchemy         | unsafe             |  3,296 |   2,144 |    437 |    715 |      0 |    0 |  5,631 |   15,304 |    20.7 |
| sqlalchemy         | infer-basedpyright |  4,015 |   2,146 |    474 |  1,395 |      0 |    0 |  6,350 |   15,304 |    51.2 |
| sqlalchemy         | infer-ty           |  3,955 |   2,146 |    463 |  1,346 |      0 |    0 |  6,290 |   15,304 |    27.5 |
| sqlalchemy         | infer-pyrefly      |  3,757 |   2,145 |    456 |  1,156 |      0 |    0 |  6,092 |   15,304 |    32.2 |
| sqlalchemy         | infer-trace        |  3,448 |   2,144 |    437 |    867 |      0 |    0 |  5,783 |   15,304 |    14.4 |
| pydantic           | certain            |  1,196 |   1,196 |        |        |      0 |    0 |  2,098 |    4,019 |     3.1 |
| pydantic           | likely             |  1,346 |   1,203 |    143 |        |      0 |    0 |  2,248 |    4,019 |     3.0 |
| pydantic           | unsafe             |  1,609 |   1,196 |    142 |    271 |      0 |    0 |  2,511 |    4,019 |     2.8 |
| pydantic           | infer-basedpyright |  1,824 |   1,197 |    144 |    483 |      0 |    0 |  2,726 |    4,019 |     8.2 |
| pydantic           | infer-ty           |  1,742 |   1,196 |    140 |    406 |      0 |    0 |  2,644 |    4,019 |     5.4 |
| pydantic           | infer-pyrefly      |  1,806 |   1,196 |    141 |    469 |      0 |    0 |  2,708 |    4,019 |     5.5 |
| pydantic           | infer-trace        |  1,610 |   1,196 |    142 |    272 |      0 |    0 |  2,512 |    4,019 |     5.4 |
| pandas             | certain            | 17,186 |  17,186 |        |        |      0 |    0 | 18,455 |   79,062 |    65.4 |
| pandas             | likely             | 41,693 |  17,398 | 24,295 |        |      0 |    0 | 42,962 |   79,062 |   183.7 |
| pandas             | unsafe             | 42,970 |  17,182 | 24,275 |  1,513 |      0 |    0 | 44,239 |   79,062 |   183.9 |
| pandas             | infer-basedpyright | 48,470 |  17,173 | 24,258 |  7,039 |      0 |   23 | 49,739 |   79,062 |   195.8 |
| pandas             | infer-ty           | 48,430 |  17,182 | 24,266 |  6,982 |      0 |   21 | 49,699 |   79,062 |   174.3 |
| pandas             | infer-pyrefly      | 50,919 |  17,181 | 24,207 |  9,531 |      0 |   25 | 52,188 |   79,062 |   136.0 |
| pandas             | infer-trace        | 44,400 |  17,185 | 24,144 |  3,071 |      0 |    0 | 45,669 |   79,062 |   104.6 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     5.5 |
| twisted            | likely             |  6,176 |   2,453 |  3,723 |        |      0 |    0 |  6,176 |   17,874 |    11.5 |
| twisted            | unsafe             |  7,264 |   2,434 |  3,723 |  1,107 |      0 |    0 |  7,264 |   17,874 |     9.9 |
| twisted            | infer-basedpyright |  8,627 |   2,435 |  3,739 |  2,453 |      0 |    0 |  8,627 |   17,874 |    19.5 |
| twisted            | infer-ty           |  7,630 |   2,434 |  3,734 |  1,462 |      0 |    0 |  7,630 |   17,874 |    19.1 |
| twisted            | infer-pyrefly      |  7,665 |   2,434 |  3,733 |  1,498 |      0 |    0 |  7,665 |   17,874 |    18.4 |
| pip                | certain            |  2,242 |   2,242 |        |        |      0 |    0 |  2,379 |    9,064 |     5.6 |
| pip                | likely             |  2,732 |   2,249 |    483 |        |      0 |    0 |  2,869 |    9,064 |     8.8 |
| pip                | unsafe             |  3,584 |   2,242 |    481 |    861 |      0 |    0 |  3,721 |    9,064 |     7.3 |
| pip                | infer-basedpyright |  4,314 |   2,243 |    526 |  1,545 |      0 |    0 |  4,451 |    9,064 |    22.3 |
| pip                | infer-ty           |  3,887 |   2,243 |    500 |  1,144 |      0 |    0 |  4,024 |    9,064 |    19.7 |
| pip                | infer-pyrefly      |  4,098 |   2,241 |    510 |  1,347 |      0 |    0 |  4,235 |    9,064 |    15.3 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.7 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.8 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.7 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     1.6 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     2.0 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     1.9 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     1.7 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.8 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     0.8 |
| attrs              | unsafe             |    107 |      93 |      8 |      6 |      0 |    0 |    110 |      396 |     0.9 |
| attrs              | infer-basedpyright |    126 |      93 |      8 |     25 |      0 |    0 |    129 |      396 |     1.3 |
| attrs              | infer-ty           |    118 |      93 |      8 |     17 |      0 |    0 |    121 |      396 |     1.7 |
| attrs              | infer-pyrefly      |    122 |      93 |      8 |     21 |      0 |    0 |    125 |      396 |     2.3 |
| attrs              | infer-trace        |    110 |      93 |      9 |      8 |      0 |    0 |    113 |      396 |     1.0 |
| click              | certain            |    311 |     311 |        |        |      0 |    0 |    590 |      887 |     0.8 |
| click              | likely             |    338 |     312 |     26 |        |      0 |    0 |    617 |      887 |     1.0 |
| click              | unsafe             |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     1.2 |
| click              | infer-basedpyright |    437 |     311 |     30 |     96 |      0 |    0 |    716 |      887 |     2.8 |
| click              | infer-ty           |    455 |     311 |     28 |    116 |      0 |    0 |    734 |      887 |     2.3 |
| click              | infer-pyrefly      |    449 |     311 |     31 |    107 |      0 |    0 |    728 |      887 |     1.7 |
| click              | infer-trace        |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     1.5 |
| hypercorn          | certain            |    137 |     137 |        |        |      0 |    0 |    307 |      525 |     0.8 |
| hypercorn          | likely             |    157 |     137 |     20 |        |      0 |    0 |    327 |      525 |     1.3 |
| hypercorn          | unsafe             |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     1.7 |
| hypercorn          | infer-basedpyright |    216 |     137 |     21 |     58 |      0 |    0 |    386 |      525 |     1.8 |
| hypercorn          | infer-ty           |    219 |     137 |     21 |     61 |      0 |    0 |    389 |      525 |     1.0 |
| hypercorn          | infer-pyrefly      |    204 |     137 |     20 |     47 |      0 |    0 |    374 |      525 |     1.9 |
| hypercorn          | infer-trace        |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     2.1 |
| starlette          | certain            |    321 |     321 |        |        |      0 |    0 |    406 |      829 |     0.7 |
| starlette          | likely             |    396 |     322 |     74 |        |      0 |    0 |    481 |      829 |     0.9 |
| starlette          | unsafe             |    437 |     321 |     74 |     42 |      0 |    0 |    522 |      829 |     1.7 |
| starlette          | infer-basedpyright |    497 |     321 |     73 |    103 |      0 |    0 |    582 |      829 |     3.2 |
| starlette          | infer-ty           |    483 |     321 |     73 |     89 |      0 |    0 |    568 |      829 |     2.2 |
| starlette          | infer-pyrefly      |    465 |     321 |     73 |     71 |      0 |    0 |    550 |      829 |     1.9 |
| starlette          | infer-trace        |    437 |     321 |     74 |     42 |      0 |    0 |    522 |      829 |     1.9 |
| werkzeug           | certain            |    545 |     545 |        |        |      0 |    0 |    761 |    1,509 |     1.5 |
| werkzeug           | likely             |    617 |     546 |     71 |        |      0 |    0 |    833 |    1,509 |     1.5 |
| werkzeug           | unsafe             |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     2.2 |
| werkzeug           | infer-basedpyright |    798 |     545 |     82 |    171 |      0 |    0 |  1,014 |    1,509 |     3.1 |
| werkzeug           | infer-ty           |    823 |     545 |     84 |    194 |      0 |    0 |  1,039 |    1,509 |     1.7 |
| werkzeug           | infer-pyrefly      |    817 |     546 |     72 |    199 |      0 |    0 |  1,033 |    1,509 |     2.6 |
| werkzeug           | infer-trace        |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     2.0 |
| mkdocs             | certain            |    826 |     826 |        |        |      0 |    0 |    937 |    2,443 |     1.4 |
| mkdocs             | likely             |  1,256 |     858 |    398 |        |      0 |    0 |  1,367 |    2,443 |     1.9 |
| mkdocs             | unsafe             |  1,378 |     826 |    398 |    154 |      0 |    0 |  1,489 |    2,443 |     3.4 |
| mkdocs             | infer-basedpyright |  1,463 |     826 |    405 |    232 |      0 |    0 |  1,574 |    2,443 |     5.3 |
| mkdocs             | infer-ty           |  1,492 |     826 |    410 |    256 |      0 |    0 |  1,603 |    2,443 |     4.2 |
| mkdocs             | infer-pyrefly      |  1,470 |     826 |    406 |    238 |      0 |    0 |  1,581 |    2,443 |     3.8 |
| mkdocs             | infer-trace        |  1,390 |     827 |    398 |    165 |      0 |    0 |  1,501 |    2,443 |     3.7 |
| httpx              | certain            |    240 |     240 |        |        |      0 |    0 |    278 |      607 |     0.6 |
| httpx              | likely             |    309 |     250 |     59 |        |      0 |    0 |    347 |      607 |     0.9 |
| httpx              | unsafe             |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     1.0 |
| httpx              | infer-basedpyright |    408 |     240 |     64 |    104 |      0 |    0 |    446 |      607 |     1.9 |
| httpx              | infer-ty           |    392 |     241 |     63 |     88 |      0 |    0 |    430 |      607 |     2.3 |
| httpx              | infer-pyrefly      |    367 |     240 |     62 |     65 |      0 |    0 |    405 |      607 |     1.0 |
| httpx              | infer-trace        |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     2.8 |
| black              | certain            |    714 |     714 |        |        |      0 |    0 |    954 |    1,513 |     0.8 |
| black              | likely             |    842 |     727 |    115 |        |      0 |    0 |  1,082 |    1,513 |     0.8 |
| black              | unsafe             |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     1.3 |
| black              | infer-basedpyright |    938 |     714 |    116 |    108 |      0 |    0 |  1,178 |    1,513 |     2.1 |
| black              | infer-ty           |    938 |     714 |    116 |    108 |      0 |    0 |  1,178 |    1,513 |     2.3 |
| black              | infer-pyrefly      |    924 |     714 |    115 |     95 |      0 |    0 |  1,164 |    1,513 |     2.3 |
| black              | infer-trace        |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     1.2 |
| fastapi            | certain            |    258 |     258 |        |        |      0 |    0 |    795 |    1,279 |     1.5 |
| fastapi            | likely             |    303 |     264 |     39 |        |      0 |    0 |    840 |    1,279 |     3.6 |
| fastapi            | unsafe             |    329 |     258 |     39 |     32 |      0 |    0 |    866 |    1,279 |     3.0 |
| fastapi            | infer-basedpyright |    355 |     258 |     38 |     59 |      0 |    0 |    892 |    1,279 |     3.1 |
| fastapi            | infer-ty           |    372 |     258 |     37 |     77 |      0 |    0 |    909 |    1,279 |     4.7 |
| fastapi            | infer-pyrefly      |    352 |     258 |     39 |     55 |      0 |    0 |    889 |    1,279 |     3.2 |
| fastapi            | infer-trace        |    329 |     258 |     39 |     32 |      0 |    0 |    866 |    1,279 |     1.7 |
| cattrs             | certain            |    112 |     112 |        |        |      0 |    0 |    151 |      559 |     1.0 |
| cattrs             | likely             |    146 |     119 |     27 |        |      0 |    0 |    185 |      559 |     1.2 |
| cattrs             | unsafe             |    164 |     115 |     26 |     23 |      0 |    0 |    203 |      559 |     1.1 |
| cattrs             | infer-basedpyright |    197 |     114 |     29 |     54 |      0 |    0 |    236 |      559 |     3.1 |
| cattrs             | infer-ty           |    205 |     112 |     27 |     66 |      0 |    0 |    244 |      559 |     1.8 |
| cattrs             | infer-pyrefly      |    191 |     112 |     28 |     51 |      0 |    0 |    230 |      559 |     2.4 |
| cattrs             | infer-trace        |    164 |     115 |     26 |     23 |      0 |    0 |    203 |      559 |     0.8 |
| pytest             | certain            |  1,375 |   1,375 |        |        |      0 |    0 |  1,790 |    3,418 |     2.4 |
| pytest             | likely             |  1,535 |   1,380 |    155 |        |      0 |    0 |  1,950 |    3,418 |     3.4 |
| pytest             | unsafe             |  1,688 |   1,375 |    155 |    158 |      0 |    0 |  2,103 |    3,418 |     5.4 |
| pytest             | infer-basedpyright |  2,019 |   1,375 |    173 |    471 |      0 |    0 |  2,434 |    3,418 |    14.5 |
| pytest             | infer-ty           |  2,028 |   1,375 |    175 |    478 |      0 |    0 |  2,443 |    3,418 |     9.0 |
| pytest             | infer-pyrefly      |  2,086 |   1,375 |    175 |    536 |      0 |    0 |  2,501 |    3,418 |     8.8 |
| pytest             | infer-trace        |  1,705 |   1,375 |    155 |    175 |      0 |    0 |  2,120 |    3,418 |     2.5 |
| botocore           | certain            |    548 |     548 |        |        |      0 |    0 |    566 |    3,806 |     2.5 |
| botocore           | likely             |    730 |     550 |    180 |        |      0 |    0 |    748 |    3,806 |     4.3 |
| botocore           | unsafe             |  1,204 |     546 |    178 |    480 |      0 |    0 |  1,222 |    3,806 |     7.4 |
| botocore           | infer-basedpyright |  1,339 |     541 |    177 |    621 |      0 |    0 |  1,357 |    3,806 |     8.9 |
| botocore           | infer-ty           |  1,261 |     546 |    179 |    536 |      0 |    0 |  1,279 |    3,806 |     9.7 |
| botocore           | infer-pyrefly      |  1,322 |     541 |    175 |    606 |      0 |    0 |  1,340 |    3,806 |     6.9 |
| botocore           | infer-trace        |  1,536 |     546 |    199 |    791 |      0 |    0 |  1,554 |    3,806 |     3.7 |
| uvicorn            | certain            |    236 |     236 |        |        |      0 |    0 |    387 |      640 |     0.8 |
| uvicorn            | likely             |    268 |     236 |     32 |        |      0 |    0 |    419 |      640 |     1.0 |
| uvicorn            | unsafe             |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     2.6 |
| uvicorn            | infer-basedpyright |    354 |     236 |     35 |     83 |      0 |    0 |    505 |      640 |     1.5 |
| uvicorn            | infer-ty           |    334 |     236 |     32 |     66 |      0 |    0 |    485 |      640 |     2.4 |
| uvicorn            | infer-pyrefly      |    316 |     236 |     35 |     45 |      0 |    0 |    467 |      640 |     2.4 |
| uvicorn            | infer-trace        |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     1.6 |
| mcp                | certain            |    718 |     718 |        |        |      0 |    0 |  1,481 |    2,483 |     2.5 |
| mcp                | likely             |    880 |     724 |    156 |        |      0 |    0 |  1,643 |    2,483 |     2.7 |
| mcp                | unsafe             |    966 |     718 |    156 |     92 |      0 |    0 |  1,729 |    2,483 |     3.5 |
| mcp                | infer-basedpyright |  1,079 |     718 |    167 |    194 |      0 |    0 |  1,842 |    2,483 |     4.1 |
| mcp                | infer-ty           |  1,069 |     718 |    164 |    187 |      0 |    0 |  1,832 |    2,483 |     4.6 |
| mcp                | infer-pyrefly      |  1,048 |     718 |    161 |    169 |      0 |    0 |  1,811 |    2,483 |     4.7 |
| mcp                | infer-trace        |    966 |     718 |    156 |     92 |      0 |    0 |  1,729 |    2,483 |     3.1 |
| textual            | certain            |  2,795 |   2,795 |        |        |      0 |    0 |  3,989 |    7,677 |     2.6 |
| textual            | likely             |  3,303 |   2,819 |    484 |        |      0 |    0 |  4,497 |    7,677 |     3.5 |
| textual            | unsafe             |  3,569 |   2,795 |    483 |    291 |      0 |    0 |  4,763 |    7,677 |     3.9 |
| textual            | infer-basedpyright |  4,684 |   2,795 |    557 |  1,332 |      0 |    0 |  5,878 |    7,677 |    25.7 |
| textual            | infer-ty           |  4,756 |   2,795 |    555 |  1,406 |      0 |    0 |  5,950 |    7,677 |    13.2 |
| textual            | infer-pyrefly      |  3,922 |   2,795 |    500 |    627 |      0 |    0 |  5,116 |    7,677 |     8.2 |
| pdm                | certain            |  1,246 |   1,246 |        |        |      0 |    0 |  1,607 |    3,079 |     3.3 |
| pdm                | likely             |  1,464 |   1,262 |    202 |        |      0 |    0 |  1,825 |    3,079 |     4.4 |
| pdm                | unsafe             |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |     6.3 |
| pdm                | infer-basedpyright |  1,895 |   1,248 |    220 |    427 |      0 |    2 |  2,256 |    3,079 |     6.1 |
| pdm                | infer-ty           |  1,902 |   1,248 |    221 |    433 |      0 |    0 |  2,263 |    3,079 |     7.7 |
| pdm                | infer-pyrefly      |  1,760 |   1,248 |    211 |    301 |      0 |    0 |  2,121 |    3,079 |     6.1 |
| pdm                | infer-trace        |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |     5.5 |
| strawberry-graphql | certain            |    656 |     656 |        |        |      0 |    0 |  1,432 |    2,582 |     3.0 |
| strawberry-graphql | likely             |    830 |     658 |    172 |        |      0 |    0 |  1,606 |    2,582 |     4.5 |
| strawberry-graphql | unsafe             |    897 |     656 |    172 |     69 |      0 |    0 |  1,673 |    2,582 |     5.1 |
| strawberry-graphql | infer-basedpyright |  1,014 |     656 |    172 |    186 |      0 |    2 |  1,790 |    2,582 |     5.9 |
| strawberry-graphql | infer-ty           |  1,011 |     656 |    171 |    184 |      0 |    2 |  1,787 |    2,582 |     6.2 |
| strawberry-graphql | infer-pyrefly      |    948 |     656 |    172 |    120 |      0 |    0 |  1,724 |    2,582 |     5.2 |
| strawberry-graphql | infer-trace        |    897 |     656 |    172 |     69 |      0 |    0 |  1,673 |    2,582 |     4.8 |
| pygments           | certain            |    735 |     735 |        |        |      0 |    0 |    735 |    7,666 |     3.1 |
| pygments           | likely             |    816 |     738 |     78 |        |      0 |    0 |    816 |    7,666 |     5.3 |
| pygments           | unsafe             |  5,352 |     735 |     78 |  4,539 |      0 |    0 |  5,352 |    7,666 |     6.1 |
| pygments           | infer-basedpyright |  5,445 |     735 |     85 |  4,625 |      0 |    0 |  5,445 |    7,666 |     6.9 |
| pygments           | infer-ty           |  5,449 |     735 |     85 |  4,629 |      0 |    0 |  5,449 |    7,666 |     9.4 |
| pygments           | infer-pyrefly      |  5,517 |     735 |     85 |  4,697 |      0 |    0 |  5,517 |    7,666 |    10.3 |
| pygments           | infer-trace        |  5,462 |     730 |    103 |  4,629 |      0 |    0 |  5,462 |    7,666 |     9.7 |
| streamlink         | certain            |    701 |     701 |        |        |      0 |    0 |  2,963 |    5,291 |     2.6 |
| streamlink         | likely             |    837 |     704 |    133 |        |      0 |    0 |  3,099 |    5,291 |     6.9 |
| streamlink         | unsafe             |  1,279 |     701 |    133 |    445 |      0 |    0 |  3,541 |    5,291 |     3.7 |
| streamlink         | infer-basedpyright |  1,608 |     703 |    154 |    751 |      0 |    1 |  3,870 |    5,291 |     5.3 |
| streamlink         | infer-ty           |  1,775 |     702 |    166 |    907 |      0 |    2 |  4,037 |    5,291 |     7.2 |
| streamlink         | infer-pyrefly      |  1,423 |     702 |    145 |    576 |      0 |    0 |  3,685 |    5,291 |     6.5 |
| streamlink         | infer-trace        |  1,287 |     701 |    133 |    453 |      0 |    0 |  3,549 |    5,291 |     7.6 |
| sphinx             | certain            |  3,392 |   3,392 |        |        |      0 |    0 |  4,320 |    8,901 |     4.3 |
| sphinx             | likely             |  3,930 |   3,407 |    523 |        |      0 |    0 |  4,858 |    8,901 |     7.7 |
| sphinx             | unsafe             |  4,334 |   3,392 |    522 |    420 |      0 |    0 |  5,262 |    8,901 |     7.8 |
| sphinx             | infer-basedpyright |  5,089 |   3,393 |    550 |  1,146 |      0 |    0 |  6,017 |    8,901 |    23.9 |
| sphinx             | infer-ty           |  5,142 |   3,392 |    544 |  1,206 |      0 |    0 |  6,070 |    8,901 |    11.0 |
| sphinx             | infer-pyrefly      |  5,326 |   3,393 |    553 |  1,380 |      0 |    0 |  6,254 |    8,901 |    12.6 |
| sphinx             | infer-trace        |  4,334 |   3,392 |    522 |    420 |      0 |    0 |  5,262 |    8,901 |     9.2 |
| tox                | certain            |    985 |     985 |        |        |      0 |    0 |  1,321 |    2,098 |     2.0 |
| tox                | likely             |  1,088 |     986 |    102 |        |      0 |    0 |  1,424 |    2,098 |     3.1 |
| tox                | unsafe             |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     2.6 |
| tox                | infer-basedpyright |  1,361 |     987 |    118 |    256 |      0 |    0 |  1,697 |    2,098 |     4.0 |
| tox                | infer-ty           |  1,392 |     987 |    117 |    288 |      0 |    0 |  1,728 |    2,098 |     1.8 |
| tox                | infer-pyrefly      |  1,433 |     987 |    117 |    329 |      0 |    0 |  1,769 |    2,098 |     4.6 |
| tox                | infer-trace        |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     2.6 |
| pint               | certain            |    649 |     649 |        |        |      0 |    0 |    814 |    3,243 |     3.6 |
| pint               | likely             |    924 |     650 |    274 |        |      0 |    0 |  1,089 |    3,243 |     6.7 |
| pint               | unsafe             |    976 |     649 |    274 |     53 |      0 |    0 |  1,141 |    3,243 |     5.1 |
| pint               | infer-basedpyright |  1,204 |     650 |    282 |    272 |      0 |   15 |  1,369 |    3,243 |     8.6 |
| pint               | infer-ty           |  1,115 |     650 |    277 |    188 |      0 |   19 |  1,280 |    3,243 |     8.0 |
| pint               | infer-pyrefly      |  1,040 |     650 |    274 |    116 |      0 |    0 |  1,205 |    3,243 |     6.1 |
| pint               | infer-trace        |    983 |     649 |    274 |     60 |      0 |    0 |  1,148 |    3,243 |     9.6 |
| altair             | certain            |    389 |     389 |        |        |      0 |    0 |  2,071 |    3,383 |    16.0 |
| altair             | likely             |    441 |     389 |     52 |        |      0 |    0 |  2,123 |    3,383 |    14.2 |
| altair             | unsafe             |    454 |     389 |     52 |     13 |      0 |    0 |  2,136 |    3,383 |    22.2 |
| altair             | infer-basedpyright |    523 |     389 |     55 |     79 |      0 |    0 |  2,205 |    3,383 |    16.7 |
| altair             | infer-ty           |    517 |     389 |     53 |     75 |      0 |    0 |  2,199 |    3,383 |    15.9 |
| altair             | infer-pyrefly      |    515 |     389 |     53 |     73 |      0 |    0 |  2,197 |    3,383 |    18.1 |
| altair             | infer-trace        |    461 |     389 |     53 |     19 |      0 |    0 |  2,143 |    3,383 |     7.4 |
| seaborn            | certain            |    657 |     657 |        |        |      0 |    0 |    872 |    3,110 |     6.5 |
| seaborn            | likely             |    821 |     664 |    157 |        |      0 |    0 |  1,036 |    3,110 |    14.3 |
| seaborn            | unsafe             |    899 |     657 |    156 |     86 |      0 |    0 |  1,114 |    3,110 |    13.4 |
| seaborn            | infer-basedpyright |  1,009 |     657 |    159 |    193 |      0 |    0 |  1,224 |    3,110 |    14.5 |
| seaborn            | infer-ty           |    983 |     656 |    158 |    169 |      0 |    0 |  1,198 |    3,110 |    12.0 |
| seaborn            | infer-pyrefly      |  1,092 |     657 |    149 |    286 |      0 |    0 |  1,307 |    3,110 |    32.5 |
| seaborn            | infer-trace        |    951 |     661 |    158 |    132 |      0 |    0 |  1,166 |    3,110 |     6.6 |
| aiohttp            | certain            |    722 |     722 |        |        |      0 |    0 |  1,298 |    2,433 |     1.9 |
| aiohttp            | likely             |    874 |     729 |    145 |        |      0 |    0 |  1,450 |    2,433 |     6.3 |
| aiohttp            | unsafe             |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     2.6 |
| aiohttp            | infer-basedpyright |  1,179 |     724 |    152 |    303 |      0 |    0 |  1,755 |    2,433 |    14.3 |
| aiohttp            | infer-ty           |  1,199 |     724 |    152 |    323 |      0 |    0 |  1,775 |    2,433 |     6.3 |
| aiohttp            | infer-pyrefly      |  1,300 |     724 |    157 |    419 |      0 |    0 |  1,876 |    2,433 |     4.2 |
| aiohttp            | infer-trace        |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     3.6 |
| websockets         | certain            |    362 |     362 |        |        |      0 |    0 |    489 |      918 |     0.8 |
| websockets         | likely             |    439 |     363 |     76 |        |      0 |    0 |    566 |      918 |     1.7 |
| websockets         | unsafe             |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     3.2 |
| websockets         | infer-basedpyright |    597 |     364 |     74 |    159 |      0 |    0 |    724 |      918 |     3.4 |
| websockets         | infer-ty           |    606 |     364 |     76 |    166 |      0 |    0 |    733 |      918 |     2.0 |
| websockets         | infer-pyrefly      |    605 |     364 |     76 |    165 |      0 |    0 |    732 |      918 |     3.1 |
| websockets         | infer-trace        |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     2.3 |
| anyio              | certain            |    230 |     230 |        |        |      0 |    0 |    505 |      990 |     2.5 |
| anyio              | likely             |    266 |     230 |     36 |        |      0 |    0 |    541 |      990 |     3.5 |
| anyio              | unsafe             |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     4.8 |
| anyio              | infer-basedpyright |    382 |     230 |     42 |    110 |      0 |    0 |    657 |      990 |     3.1 |
| anyio              | infer-ty           |    397 |     230 |     44 |    123 |      0 |    0 |    672 |      990 |     4.8 |
| anyio              | infer-pyrefly      |    387 |     230 |     42 |    115 |      0 |    0 |    662 |      990 |     2.2 |
| anyio              | infer-trace        |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     5.0 |
| zarr               | certain            |  1,169 |   1,169 |        |        |      0 |    0 |  1,837 |    3,079 |     5.2 |
| zarr               | likely             |  1,248 |   1,170 |     78 |        |      0 |    0 |  1,916 |    3,079 |     5.1 |
| zarr               | unsafe             |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     7.0 |
| zarr               | infer-basedpyright |  1,667 |   1,169 |     99 |    399 |      0 |    0 |  2,335 |    3,079 |    15.7 |
| zarr               | infer-ty           |  1,635 |   1,169 |     98 |    368 |      0 |    0 |  2,303 |    3,079 |     5.6 |
| zarr               | infer-pyrefly      |  1,477 |   1,169 |     86 |    222 |      0 |    0 |  2,145 |    3,079 |     9.1 |
| zarr               | infer-trace        |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     4.1 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     3.2 |
| joblib             | likely             |    704 |     526 |    178 |        |      0 |    0 |    705 |    2,241 |     3.1 |
| joblib             | unsafe             |    826 |     524 |    176 |    126 |      0 |    0 |    827 |    2,241 |     4.0 |
| joblib             | infer-basedpyright |    942 |     524 |    179 |    239 |      0 |    0 |    943 |    2,241 |     8.7 |
| joblib             | infer-ty           |    890 |     524 |    177 |    189 |      0 |    0 |    891 |    2,241 |     4.3 |
| joblib             | infer-pyrefly      |    938 |     522 |    179 |    237 |      0 |    0 |    939 |    2,241 |     5.3 |
| joblib             | infer-trace        |    838 |     524 |    178 |    136 |      0 |    0 |    839 |    2,241 |     3.4 |
| networkx           | certain            |  3,971 |   3,971 |        |        |      0 |    0 |  4,033 |   22,518 |    24.7 |
| networkx           | likely             |  6,177 |   3,985 |  2,192 |        |      0 |    0 |  6,239 |   22,518 |    33.7 |
| networkx           | unsafe             |  6,493 |   3,976 |  2,189 |    328 |      0 |    0 |  6,555 |   22,518 |    46.0 |
| networkx           | infer-basedpyright |  7,501 |   3,976 |  2,243 |  1,282 |      0 |    0 |  7,563 |   22,518 |    34.6 |
| networkx           | infer-ty           |  6,939 |   3,976 |  2,203 |    760 |      0 |    0 |  7,001 |   22,518 |    31.2 |
| networkx           | infer-pyrefly      |  7,052 |   3,978 |  2,211 |    863 |      0 |    1 |  7,114 |   22,518 |    34.1 |
| networkx           | infer-trace        |  6,910 |   3,976 |  2,216 |    718 |      0 |    0 |  6,972 |   22,518 |    16.8 |
| nibabel            | certain            |  1,870 |   1,870 |        |        |      0 |    0 |  1,952 |    8,550 |     9.9 |
| nibabel            | likely             |  2,711 |   1,887 |    824 |        |      0 |    0 |  2,793 |    8,550 |    19.1 |
| nibabel            | unsafe             |  3,042 |   1,870 |    820 |    352 |      0 |    0 |  3,124 |    8,550 |    13.5 |
| nibabel            | infer-basedpyright |  3,597 |   1,870 |    855 |    872 |      0 |    3 |  3,679 |    8,550 |    17.6 |
| nibabel            | infer-ty           |  3,587 |   1,870 |    875 |    842 |      0 |    3 |  3,669 |    8,550 |    13.5 |
| nibabel            | infer-pyrefly      |  3,623 |   1,868 |    835 |    920 |      0 |    0 |  3,705 |    8,550 |     9.2 |
| nibabel            | infer-trace        |  3,120 |   1,871 |    826 |    423 |      0 |    0 |  3,202 |    8,550 |    11.9 |
| narwhals           | certain            |  1,082 |   1,082 |        |        |      0 |    0 |  1,947 |    3,985 |     9.3 |
| narwhals           | likely             |  1,158 |   1,083 |     75 |        |      0 |    0 |  2,023 |    3,985 |    16.2 |
| narwhals           | unsafe             |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |    11.3 |
| narwhals           | infer-basedpyright |  1,519 |   1,082 |     87 |    350 |      0 |    2 |  2,384 |    3,985 |    12.9 |
| narwhals           | infer-ty           |  1,492 |   1,082 |     97 |    313 |      0 |    1 |  2,357 |    3,985 |    14.9 |
| narwhals           | infer-pyrefly      |  1,721 |   1,082 |     92 |    547 |      0 |    2 |  2,586 |    3,985 |    16.4 |
| narwhals           | infer-trace        |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |     7.8 |
| xarray             | certain            |  4,622 |   4,622 |        |        |      0 |    0 |  5,651 |   22,373 |    36.5 |
| xarray             | likely             |  9,773 |   4,678 |  5,095 |        |      0 |    0 | 10,802 |   22,373 |    50.1 |
| xarray             | unsafe             | 10,121 |   4,622 |  5,088 |    411 |      0 |    0 | 11,150 |   22,373 |    58.5 |
| xarray             | infer-basedpyright | 12,638 |   4,622 |  5,142 |  2,874 |      0 |    0 | 13,667 |   22,373 |   156.1 |
| xarray             | infer-ty           | 12,669 |   4,622 |  5,133 |  2,914 |      0 |    0 | 13,698 |   22,373 |    57.4 |
| xarray             | infer-pyrefly      | 10,808 |   4,623 |  5,073 |  1,112 |      0 |    0 | 11,837 |   22,373 |    51.6 |
| xarray             | infer-trace        | 10,140 |   4,622 |  5,087 |    431 |      0 |    0 | 11,169 |   22,373 |    31.0 |
| litestar           | certain            |    648 |     648 |        |        |      0 |    0 |  2,202 |    3,459 |     5.2 |
| litestar           | likely             |    772 |     650 |    122 |        |      0 |    0 |  2,326 |    3,459 |     8.3 |
| litestar           | unsafe             |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     7.6 |
| litestar           | infer-basedpyright |  1,038 |     648 |    130 |    260 |      0 |    1 |  2,592 |    3,459 |     7.6 |
| litestar           | infer-ty           |  1,050 |     648 |    133 |    269 |      0 |    0 |  2,604 |    3,459 |     9.5 |
| litestar           | infer-pyrefly      |    930 |     648 |    126 |    156 |      0 |    0 |  2,484 |    3,459 |     6.6 |
| litestar           | infer-trace        |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     3.8 |
| stripe             | certain            |    781 |     781 |        |        |      0 |    0 | 29,531 |   32,107 |     7.5 |
| stripe             | likely             |    947 |     781 |    166 |        |      0 |    0 | 29,697 |   32,107 |     8.5 |
| stripe             | unsafe             |  1,452 |     781 |    166 |    505 |      0 |    0 | 30,202 |   32,107 |    10.2 |
| stripe             | infer-basedpyright |  2,158 |     781 |    161 |  1,216 |      0 |    0 | 30,908 |   32,107 |   235.6 |
| stripe             | infer-ty           |  1,499 |     781 |    161 |    557 |      0 |    0 | 30,249 |   32,107 |    15.4 |
| stripe             | infer-pyrefly      |  1,488 |     781 |    164 |    543 |      0 |    0 | 30,238 |   32,107 |    24.8 |
| celery             | certain            |    508 |     508 |        |        |      0 |    0 |    524 |    3,764 |     9.8 |
| celery             | likely             |    638 |     510 |    128 |        |      0 |    0 |    654 |    3,764 |    17.1 |
| celery             | unsafe             |    879 |     508 |    128 |    243 |      0 |    0 |    895 |    3,764 |    15.8 |
| celery             | infer-basedpyright |  1,045 |     508 |    137 |    400 |      0 |    0 |  1,061 |    3,764 |    17.5 |
| celery             | infer-ty           |    949 |     508 |    129 |    312 |      0 |    0 |    965 |    3,764 |    12.9 |
| celery             | infer-pyrefly      |    987 |     508 |    129 |    350 |      0 |    0 |  1,003 |    3,764 |    15.7 |
| celery             | infer-trace        |    945 |     508 |    127 |    310 |      0 |    0 |    961 |    3,764 |    13.6 |
| optuna             | certain            |  1,583 |   1,583 |        |        |      0 |    0 |  1,874 |    3,889 |     8.5 |
| optuna             | likely             |  1,802 |   1,591 |    211 |        |      0 |    0 |  2,093 |    3,889 |    21.2 |
| optuna             | unsafe             |  1,910 |   1,583 |    211 |    116 |      0 |    0 |  2,201 |    3,889 |    11.1 |
| optuna             | infer-basedpyright |  2,196 |   1,583 |    222 |    391 |      0 |   11 |  2,487 |    3,889 |    18.5 |
| optuna             | infer-ty           |  2,233 |   1,583 |    240 |    410 |      0 |    6 |  2,524 |    3,889 |    17.3 |
| optuna             | infer-pyrefly      |  2,194 |   1,583 |    227 |    384 |      0 |    6 |  2,485 |    3,889 |    17.1 |
| optuna             | infer-trace        |  1,910 |   1,583 |    211 |    116 |      0 |    0 |  2,201 |    3,889 |     6.7 |
| dask               | certain            |  3,158 |   3,158 |        |        |      0 |    0 |  3,416 |   24,430 |    35.9 |
| dask               | likely             |  5,138 |   3,201 |  1,937 |        |      0 |    0 |  5,396 |   24,430 |    50.3 |
| dask               | unsafe             |  6,056 |   3,166 |  1,934 |    956 |      0 |    0 |  6,314 |   24,430 |    42.0 |
| dask               | infer-basedpyright |  6,816 |   3,166 |  1,953 |  1,697 |      0 |    0 |  7,074 |   24,430 |   159.2 |
| dask               | infer-ty           |  6,530 |   3,166 |  1,926 |  1,438 |      0 |    0 |  6,788 |   24,430 |    55.4 |
| dask               | infer-pyrefly      |  6,990 |   3,170 |  1,944 |  1,876 |      0 |    2 |  7,248 |   24,430 |    73.0 |
| dask               | infer-trace        |  6,218 |   3,163 |  1,937 |  1,118 |      0 |    0 |  6,476 |   24,430 |    31.2 |
| mypy               | certain            |  5,142 |   5,142 |        |        |      0 |    0 |  7,442 |   13,701 |     7.6 |
| mypy               | likely             |  6,351 |   5,172 |  1,179 |        |      0 |    0 |  8,651 |   13,701 |    14.8 |
| mypy               | unsafe             |  6,758 |   5,142 |  1,177 |    439 |      0 |    0 |  9,057 |   13,701 |    11.1 |
| mypy               | infer-basedpyright |  8,392 |   5,143 |  1,291 |  1,958 |      0 |    4 | 10,690 |   13,701 |    26.4 |
| mypy               | infer-ty           |  8,696 |   5,142 |  1,293 |  2,261 |      0 |    3 | 10,994 |   13,701 |    15.1 |
| mypy               | infer-pyrefly      |  8,915 |   5,139 |  1,299 |  2,477 |      0 |    4 | 11,213 |   13,701 |    13.4 |
| mypy               | infer-trace        |  6,758 |   5,142 |  1,177 |    439 |      0 |    0 |  9,057 |   13,701 |    12.4 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms               |  fixed | certain | likely |  guess |
| ------------------ | ------------------------ | -----: | ------: | -----: | -----: |
| certain            | literal                  | 23,998 |  23,998 |        |        |
| certain            | stdlib                   | 16,072 |  16,072 |        |        |
| certain            | call                     | 10,796 |  10,796 |        |        |
| certain            | container+literal        |  6,846 |   6,846 |        |        |
| certain            | builtin                  |  4,402 |   4,402 |        |        |
| certain            | method                   |  4,357 |   4,357 |        |        |
| certain            | loop                     |  3,942 |   3,942 |        |        |
| certain            | copy+loop                |  3,690 |   3,690 |        |        |
| certain            | container+literal+loop   |  2,079 |   2,079 |        |        |
| certain            | literal+method           |  1,616 |   1,616 |        |        |
| certain            | call+unpack              |  1,601 |   1,601 |        |        |
| certain            | open                     |  1,493 |   1,493 |        |        |
| likely             | constructor              | 38,146 |     257 | 37,889 |        |
| likely             | literal                  | 24,006 |  24,006 |        |        |
| likely             | stdlib                   | 16,172 |  16,172 |        |        |
| likely             | call                     | 11,383 |  10,809 |    574 |        |
| likely             | container+literal        |  6,846 |   6,846 |        |        |
| likely             | method                   |  6,192 |   4,394 |  1,798 |        |
| likely             | builtin                  |  4,403 |   4,403 |        |        |
| likely             | copy+loop                |  4,282 |   3,717 |    565 |        |
| likely             | loop                     |  3,946 |   3,946 |        |        |
| likely             | container+literal+loop   |  2,079 |   2,079 |        |        |
| likely             | literal+method           |  1,616 |   1,616 |        |        |
| likely             | call+unpack              |  1,601 |   1,601 |        |        |
| unsafe             | constructor              | 38,139 |     257 | 37,882 |        |
| unsafe             | literal                  | 24,001 |  23,996 |        |      5 |
| unsafe             | stdlib                   | 16,631 |  16,074 |        |    557 |
| unsafe             | call                     | 11,369 |  10,796 |    573 |        |
| unsafe             | literal+member           |  7,834 |         |        |  7,834 |
| unsafe             | container+literal        |  6,846 |   6,846 |        |        |
| unsafe             | method                   |  6,156 |   4,358 |  1,798 |        |
| unsafe             | builtin                  |  4,404 |   4,402 |        |      2 |
| unsafe             | copy+loop                |  4,252 |   3,690 |    562 |        |
| unsafe             | loop                     |  3,942 |   3,942 |        |        |
| unsafe             | returned                 |  3,859 |   1,190 |        |  2,669 |
| unsafe             | container+literal+member |  3,044 |         |        |  3,044 |
| infer-basedpyright | constructor              | 38,072 |     256 | 37,816 |        |
| infer-basedpyright | checker                  | 25,865 |         |        | 25,865 |
| infer-basedpyright | literal                  | 24,003 |  23,998 |        |      5 |
| infer-basedpyright | stdlib                   | 16,744 |  16,016 |        |    728 |
| infer-basedpyright | call                     | 11,493 |  10,793 |    700 |        |
| infer-basedpyright | literal+member           |  7,833 |         |        |  7,833 |
| infer-basedpyright | container+literal        |  6,848 |   6,848 |        |        |
| infer-basedpyright | method                   |  6,404 |   4,357 |  2,047 |        |
| infer-basedpyright | copy+loop                |  4,825 |   3,691 |  1,134 |        |
| infer-basedpyright | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-basedpyright | returned                 |  4,059 |   1,169 |        |  2,890 |
| infer-basedpyright | loop                     |  3,942 |   3,942 |        |        |
| infer-ty           | constructor              | 38,071 |     257 | 37,814 |        |
| infer-ty           | literal                  | 24,002 |  23,997 |        |      5 |
| infer-ty           | checker                  | 21,209 |         |        | 21,209 |
| infer-ty           | stdlib                   | 16,743 |  16,037 |        |    706 |
| infer-ty           | call                     | 11,444 |  10,794 |    650 |        |
| infer-ty           | literal+member           |  7,834 |         |        |  7,834 |
| infer-ty           | container+literal        |  6,847 |   6,847 |        |        |
| infer-ty           | method                   |  6,364 |   4,357 |  2,007 |        |
| infer-ty           | copy+loop                |  4,738 |   3,691 |  1,047 |        |
| infer-ty           | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-ty           | returned                 |  4,008 |   1,190 |        |  2,818 |
| infer-ty           | loop                     |  3,942 |   3,942 |        |        |
| infer-pyrefly      | constructor              | 38,011 |     256 | 37,755 |        |
| infer-pyrefly      | checker                  | 24,560 |         |        | 24,560 |
| infer-pyrefly      | literal                  | 24,002 |  23,997 |        |      5 |
| infer-pyrefly      | stdlib                   | 16,764 |  16,028 |        |    736 |
| infer-pyrefly      | call                     | 11,421 |  10,794 |    627 |        |
| infer-pyrefly      | literal+member           |  7,833 |         |        |  7,833 |
| infer-pyrefly      | container+literal        |  6,853 |   6,853 |        |        |
| infer-pyrefly      | method                   |  6,309 |   4,357 |  1,952 |        |
| infer-pyrefly      | copy+loop                |  4,751 |   3,690 |  1,061 |        |
| infer-pyrefly      | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-pyrefly      | returned                 |  4,028 |   1,187 |        |  2,841 |
| infer-pyrefly      | loop                     |  3,942 |   3,942 |        |        |
| infer-trace        | constructor              | 30,603 |      25 | 30,578 |        |
| infer-trace        | literal                  | 13,903 |  13,901 |        |      2 |
| infer-trace        | call                     | 10,659 |  10,092 |    567 |        |
| infer-trace        | literal+member           |  5,572 |         |        |  5,572 |
| infer-trace        | method                   |  5,475 |   3,764 |  1,711 |        |
| infer-trace        | container+literal        |  4,351 |   4,351 |        |        |
| infer-trace        | stdlib                   |  4,114 |   3,898 |        |    216 |
| infer-trace        | traced                   |  3,199 |         |        |  3,199 |
| infer-trace        | copy+loop                |  2,736 |   2,373 |    363 |        |
| infer-trace        | container+literal+member |  2,643 |         |        |  2,643 |
| infer-trace        | builtin                  |  2,617 |   2,615 |        |      2 |
| infer-trace        | loop                     |  2,024 |   2,024 |        |        |
| infer-union        | constructor              | 30,462 |      25 | 30,437 |        |
| infer-union        | agreed+checker           | 14,481 |         |        | 14,481 |
| infer-union        | literal                  | 13,904 |  13,902 |        |      2 |
| infer-union        | checker                  | 11,618 |         |        | 11,618 |
| infer-union        | call                     | 10,744 |  10,089 |    655 |        |
| infer-union        | method                   |  5,707 |   3,758 |  1,949 |        |
| infer-union        | literal+member           |  5,572 |         |        |  5,572 |
| infer-union        | container+literal        |  4,358 |   4,358 |        |        |
| infer-union        | stdlib                   |  4,105 |   3,881 |        |    224 |
| infer-union        | traced                   |  3,144 |         |        |  3,144 |
| infer-union        | copy+loop                |  3,136 |   2,373 |    763 |        |
| infer-union        | container+literal+member |  2,643 |         |        |  2,643 |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  14,189 |  62,158 |        0 |
| django             |  17,176 |   2,883 |  11,671 |        0 |
| sqlalchemy         |  12,932 |   1,152 |   9,636 |        0 |
| pydantic           |   3,117 |     413 |   1,508 |        0 |
| pandas             |  77,793 |  25,526 |  35,081 |        0 |
| twisted            |  17,874 |   4,826 |  10,613 |        0 |
| pip                |   8,923 |   1,342 |   5,339 |        0 |
| structlog          |     316 |      28 |     190 |        0 |
| attrs              |     393 |      14 |     286 |        0 |
| click              |     607 |      64 |     232 |        0 |
| hypercorn          |     355 |      58 |     160 |        0 |
| starlette          |     744 |     116 |     307 |        0 |
| werkzeug           |   1,293 |     138 |     610 |        0 |
| mkdocs             |   2,331 |     552 |     953 |        0 |
| httpx              |     569 |      84 |     245 |        0 |
| black              |   1,273 |     169 |     390 |        0 |
| fastapi            |     742 |      71 |     413 |        0 |
| cattrs             |     520 |      43 |     367 |        0 |
| pytest             |   3,000 |     313 |   1,312 |        0 |
| botocore           |   3,786 |     656 |   2,582 |        0 |
| uvicorn            |     489 |      57 |     196 |        0 |
| mcp                |   1,720 |     248 |     754 |        0 |
| textual            |   6,483 |     774 |   2,914 |        0 |
| pdm                |   2,713 |     364 |   1,103 |        0 |
| strawberry-graphql |   1,806 |     241 |     909 |        0 |
| pygments           |   7,666 |   4,617 |   2,314 |        0 |
| streamlink         |   3,029 |     578 |   1,750 |        0 |
| sphinx             |   7,972 |     942 |   3,639 |        0 |
| tox                |   1,762 |     158 |     619 |        0 |
| pint               |   3,078 |     322 |   2,107 |        0 |
| altair             |   1,700 |      65 |   1,246 |        0 |
| seaborn            |   2,895 |     242 |   1,996 |        0 |
| aiohttp            |   1,857 |     274 |     861 |        0 |
| websockets         |     791 |     130 |     299 |        0 |
| anyio              |     715 |      69 |     416 |        0 |
| zarr               |   2,411 |     118 |   1,124 |        0 |
| joblib             |   2,239 |     301 |   1,413 |        0 |
| networkx           |  22,456 |   2,463 |  16,022 |        0 |
| nibabel            |   8,466 |   1,172 |   5,424 |        0 |
| narwhals           |   3,112 |     130 |   1,900 |        0 |
| xarray             |  21,344 |   5,497 |  11,225 |        0 |
| litestar           |   1,905 |     198 |   1,059 |        0 |
| stripe             |   3,357 |     671 |   1,905 |        0 |
| celery             |   3,747 |     371 |   2,868 |        0 |
| optuna             |   3,595 |     327 |   1,685 |        0 |
| dask               |  24,171 |   2,763 |  18,250 |        0 |
| mypy               |  11,401 |   1,615 |   4,645 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by | beside other steps |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: | -----------------: |
| standard library   |    4 |      147.93 |     56.24 |    1 |                       872.1 |     915.4 | hyperfine |                yes |
| django             |    4 |       19.74 |      9.31 |    1 |                       184.0 |     196.3 | hyperfine |                yes |
| sqlalchemy         |    4 |        21.2 |      9.49 |    1 |                       160.9 |     168.9 | hyperfine |                yes |
| pydantic           |    4 |        3.18 |      1.73 |    1 |                        30.0 |      32.5 | hyperfine |                yes |
| pandas             |    4 |      195.89 |     62.19 |    1 |                      1076.1 |    1106.9 | hyperfine |                yes |
| twisted            |    4 |        15.7 |      9.73 |    1 |                       125.6 |     134.6 | hyperfine |                yes |
| pip                |    4 |       10.05 |      4.71 |    1 |                        88.6 |      94.4 | hyperfine |                yes |
| structlog          |    4 |        0.84 |      0.83 |    1 |                         4.5 |       5.6 | hyperfine |                yes |
| attrs              |    4 |         0.6 |      0.73 |    1 |                         3.6 |       4.6 | hyperfine |                yes |
| click              |    4 |        1.15 |      0.92 |    1 |                         7.0 |       8.1 | hyperfine |                yes |
| hypercorn          |    4 |        1.01 |      0.91 |    1 |                         5.4 |       6.7 | hyperfine |                yes |
| starlette          |    4 |        0.76 |      0.54 |    1 |                         7.0 |       8.4 | hyperfine |                yes |
| werkzeug           |    4 |        1.35 |      0.73 |    1 |                        13.4 |      14.7 | hyperfine |                yes |
| mkdocs             |    4 |        3.04 |      2.35 |    1 |                        15.9 |      18.3 | hyperfine |                yes |
| httpx              |    4 |        1.21 |      1.22 |    1 |                         6.7 |       7.9 | hyperfine |                yes |
| black              |    4 |        1.23 |      0.69 |    1 |                         9.8 |      11.1 | hyperfine |                yes |
| fastapi            |    4 |        1.18 |      0.87 |    1 |                        12.3 |      14.1 | hyperfine |                yes |
| cattrs             |    4 |        0.95 |      1.14 |    1 |                         6.7 |       8.2 | hyperfine |                yes |
| pytest             |    4 |        3.24 |      1.87 |    1 |                        25.8 |      28.0 | hyperfine |                yes |
| botocore           |    4 |        3.45 |      1.61 |    1 |                        35.1 |      37.8 | hyperfine |                yes |
| uvicorn            |    4 |        0.78 |      0.71 |    1 |                         7.7 |       9.0 | hyperfine |                yes |
| mcp                |    4 |        1.93 |      0.96 |    1 |                        20.1 |      22.5 | hyperfine |                yes |
| textual            |    4 |        6.35 |      2.03 |    1 |                        46.5 |      50.5 | hyperfine |                yes |
| pdm                |    4 |        3.07 |      3.32 |    1 |                        33.1 |      36.6 | hyperfine |                yes |
| strawberry-graphql |    4 |        2.95 |      2.26 |    1 |                        31.2 |      35.3 | hyperfine |                yes |
| pygments           |    4 |        6.09 |      2.14 |    1 |                        64.3 |      68.3 | hyperfine |                yes |
| streamlink         |    4 |        3.84 |      1.87 |    1 |                        38.3 |      41.1 | hyperfine |                yes |
| sphinx             |    4 |        7.77 |      3.81 |    1 |                        78.7 |      81.3 | hyperfine |                yes |
| tox                |    4 |        2.31 |      1.79 |    1 |                        18.4 |      19.4 | hyperfine |                yes |
| pint               |    4 |        2.77 |      2.25 |    1 |                        34.5 |      39.4 | hyperfine |                yes |
| altair             |    4 |         5.8 |      6.39 |    1 |                        68.8 |      77.9 | hyperfine |                yes |
| seaborn            |    4 |        5.47 |      4.57 |    1 |                        59.1 |      71.6 | hyperfine |                yes |
| aiohttp            |    4 |         6.3 |      3.61 |    1 |                        22.0 |      23.6 | hyperfine |                yes |
| websockets         |    4 |         1.0 |      0.97 |    1 |                        10.2 |      11.8 | hyperfine |                yes |
| anyio              |    4 |        1.61 |      0.98 |    1 |                        11.7 |      13.0 | hyperfine |                yes |
| zarr               |    4 |        3.01 |      1.46 |    1 |                        28.3 |      31.3 | hyperfine |                yes |
| joblib             |    4 |         2.3 |      2.29 |    1 |                        25.7 |      29.4 | hyperfine |                yes |
| networkx           |    4 |       60.82 |     20.63 |    1 |                       254.2 |     253.7 | hyperfine |                yes |
| nibabel            |    4 |        8.31 |      4.76 |    1 |                        76.0 |      87.4 | hyperfine |                yes |
| narwhals           |    4 |        5.88 |      4.48 |    1 |                        62.2 |      71.8 | hyperfine |                yes |
| xarray             |    4 |       32.31 |     17.76 |    1 |                       288.8 |     307.5 | hyperfine |                yes |
| litestar           |    4 |        3.45 |      2.17 |    1 |                        39.2 |      43.4 | hyperfine |                yes |
| stripe             |    4 |       17.09 |      6.12 |    1 |                       152.0 |     159.0 | hyperfine |                yes |
| celery             |    4 |        8.11 |      7.45 |    1 |                        77.7 |      87.4 | hyperfine |                yes |
| optuna             |    4 |        8.37 |      4.75 |    1 |                        71.2 |      76.9 | hyperfine |                yes |
| dask               |    4 |       52.43 |      28.1 |    1 |                       414.3 |     433.7 | hyperfine |                yes |
| mypy               |    4 |       16.64 |      5.88 |    1 |                        98.2 |     100.7 | hyperfine |                yes |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  485 |          Ran 17585 tests: FAILED (failures=5, skipped=1149, expected failures=5) |    68.2 |     88.4 |
| django             | certain |    979 |    978 |        1 |                      |                                                                                  |         |          |
| django             | likely  |    333 |    332 |        1 |                      |                                                                                  |         |          |
| django             | guess   |    400 |    383 |       17 |                      |                                                                                  |         |          |
| sqlalchemy         |         |        |        |          |                  150 |                                             29521 passed, 975 skipped, 1 warning |   126.6 |     96.1 |
| sqlalchemy         | certain |  1,185 |  1,165 |       20 |                      |                                                                                  |         |          |
| sqlalchemy         | likely  |    183 |    179 |        4 |                      |                                                                                  |         |          |
| sqlalchemy         | guess   |    137 |    134 |        3 |                      |                                                                                  |         |          |
| pydantic           |         |        |        |          |                    1 |                                  65 failed, 6900 passed, 350 skipped, 29 xfailed |    87.8 |     68.4 |
| pydantic           | certain |    531 |    526 |        5 |                      |                                                                                  |         |          |
| pydantic           | likely  |     49 |     49 |        0 |                      |                                                                                  |         |          |
| pydantic           | guess   |     31 |     31 |        0 |                      |                                                                                  |         |          |
| pandas             |         |        |        |          |                1,557 |                            165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   133.2 |    110.6 |
| pandas             | certain | 13,085 | 12,981 |      104 |                      |                                                                                  |         |          |
| pandas             | likely  | 20,789 | 20,711 |       78 |                      |                                                                                  |         |          |
| pandas             | guess   |  1,040 |    996 |       44 |                      |                                                                                  |         |          |
| structlog          |         |        |        |          |                    0 |                                    24 failed, 860 passed, 37 skipped, 2 warnings |     3.5 |      2.7 |
| structlog          | certain |     63 |     63 |        0 |                      |                                                                                  |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess   |      6 |      6 |        0 |                      |                                                                                  |         |          |
| attrs              |         |        |        |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.6 |      2.5 |
| attrs              | certain |     71 |     71 |        0 |                      |                                                                                  |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess   |      4 |      4 |        0 |                      |                                                                                  |         |          |
| click              |         |        |        |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     6.0 |      8.2 |
| click              | certain |    229 |    229 |        0 |                      |                                                                                  |         |          |
| click              | likely  |     18 |     17 |        1 |                      |                                                                                  |         |          |
| click              | guess   |     26 |     26 |        0 |                      |                                                                                  |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                             2 failed, 194 passed |     8.2 |      8.7 |
| hypercorn          | certain |     63 |     63 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess   |     11 |     11 |        0 |                      |                                                                                  |         |          |
| starlette          |         |        |        |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |    17.2 |     19.5 |
| starlette          | certain |    200 |    199 |        1 |                      |                                                                                  |         |          |
| starlette          | likely  |     63 |     63 |        0 |                      |                                                                                  |         |          |
| starlette          | guess   |     31 |     31 |        0 |                      |                                                                                  |         |          |
| werkzeug           |         |        |        |          |                    0 |                                       1 failed, 979 passed, 1 skipped, 1 warning |     8.6 |     10.6 |
| werkzeug           | certain |    366 |    362 |        4 |                      |                                                                                  |         |          |
| werkzeug           | likely  |     49 |     49 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess   |     34 |     34 |        0 |                      |                                                                                  |         |          |
| mkdocs             |         |        |        |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    12.4 |     10.5 |
| mkdocs             | certain |    643 |    642 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely  |    378 |    378 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess   |    129 |    129 |        0 |                      |                                                                                  |         |          |
| httpx              |         |        |        |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |    11.4 |     10.2 |
| httpx              | certain |    187 |    187 |        0 |                      |                                                                                  |         |          |
| httpx              | likely  |     50 |     50 |        0 |                      |                                                                                  |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| black              |         |        |        |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |     8.5 |      5.8 |
| black              | certain |    611 |    611 |        0 |                      |                                                                                  |         |          |
| black              | likely  |    103 |    103 |        0 |                      |                                                                                  |         |          |
| black              | guess   |     42 |     42 |        0 |                      |                                                                                  |         |          |
| fastapi            |         |        |        |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    18.6 |     14.5 |
| fastapi            | certain |    216 |    216 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely  |     32 |     32 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess   |     23 |     23 |        0 |                      |                                                                                  |         |          |
| cattrs             |         |        |        |          |                    0 |                                                           994 passed, 15 xfailed |    20.3 |     20.6 |
| cattrs             | certain |    104 |    102 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely  |     24 |     24 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess   |     19 |     19 |        0 |                      |                                                                                  |         |          |
| pytest             |         |        |        |          |                   14 |              46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    49.3 |     22.3 |
| pytest             | certain |  1,117 |  1,106 |       11 |                      |                                                                                  |         |          |
| pytest             | likely  |    126 |    126 |        0 |                      |                                                                                  |         |          |
| pytest             | guess   |    120 |    120 |        0 |                      |                                                                                  |         |          |
| botocore           |         |        |        |          |                  289 |                                                7 failed, 4593 passed, 96 skipped |    32.6 |     29.1 |
| botocore           | certain |    330 |    329 |        1 |                      |                                                                                  |         |          |
| botocore           | likely  |    146 |    146 |        0 |                      |                                                                                  |         |          |
| botocore           | guess   |    136 |    128 |        8 |                      |                                                                                  |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                          1350 passed, 12 skipped |    29.7 |     30.1 |
| uvicorn            | certain |    170 |    166 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| mcp                |         |        |        |          |                    0 |                                      3 failed, 6092 passed, 8 skipped, 1 xfailed |    22.0 |     22.0 |
| mcp                | certain |    528 |    528 |        0 |                      |                                                                                  |         |          |
| mcp                | likely  |    136 |    135 |        1 |                      |                                                                                  |         |          |
| mcp                | guess   |     59 |     59 |        0 |                      |                                                                                  |         |          |
| pdm                |         |        |        |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    18.5 |     20.0 |
| pdm                | certain |    939 |    936 |        3 |                      |                                                                                  |         |          |
| pdm                | likely  |    136 |    136 |        0 |                      |                                                                                  |         |          |
| pdm                | guess   |    102 |    101 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql |         |        |        |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    24.4 |     17.7 |
| strawberry-graphql | certain |    416 |    409 |        7 |                      |                                                                                  |         |          |
| strawberry-graphql | likely  |     99 |     98 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql | guess   |     42 |     42 |        0 |                      |                                                                                  |         |          |
| pygments           |         |        |        |          |                   89 |                                                          5330 passed, 16 skipped |    20.9 |     21.3 |
| pygments           | certain |    289 |    289 |        0 |                      |                                                                                  |         |          |
| pygments           | likely  |     61 |     61 |        0 |                      |                                                                                  |         |          |
| pygments           | guess   |     87 |     87 |        0 |                      |                                                                                  |         |          |
| streamlink         |         |        |        |          |                    8 |                                     15 failed, 7233 passed, 36 skipped, 9 errors |    21.3 |     21.7 |
| streamlink         | certain |    287 |    286 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely  |     46 |     46 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess   |     46 |     46 |        0 |                      |                                                                                  |         |          |
| sphinx             |         |        |        |          |                    0 |                                   7 failed, 2394 passed, 23 skipped, 35 warnings |    17.9 |     16.1 |
| sphinx             | certain |  2,144 |  2,112 |       32 |                      |                                                                                  |         |          |
| sphinx             | likely  |    428 |    427 |        1 |                      |                                                                                  |         |          |
| sphinx             | guess   |    220 |    216 |        4 |                      |                                                                                  |         |          |
| tox                |         |        |        |          |                    0 |                                     17 failed, 8525 passed, 31 skipped, 6 errors |    22.7 |     17.5 |
| tox                | certain |    751 |    747 |        4 |                      |                                                                                  |         |          |
| tox                | likely  |     76 |     76 |        0 |                      |                                                                                  |         |          |
| tox                | guess   |     29 |     29 |        0 |                      |                                                                                  |         |          |
| pint               |         |        |        |          |                    5 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    38.5 |     63.7 |
| pint               | certain |    216 |    213 |        3 |                      |                                                                                  |         |          |
| pint               | likely  |     12 |     12 |        0 |                      |                                                                                  |         |          |
| pint               | guess   |     24 |     22 |        2 |                      |                                                                                  |         |          |
| altair             |         |        |        |          |                    6 |            28 failed, 1866 passed, 12 skipped, 6 xfailed, 4 xpassed, 92 warnings |    19.9 |     22.2 |
| altair             | certain |    202 |    201 |        1 |                      |                                                                                  |         |          |
| altair             | likely  |     35 |     35 |        0 |                      |                                                                                  |         |          |
| altair             | guess   |      6 |      5 |        1 |                      |                                                                                  |         |          |
| seaborn            |         |        |        |          |                   44 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 959 warnings, 8 errors |    42.1 |     38.7 |
| seaborn            | certain |    502 |    500 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely  |    133 |    131 |        2 |                      |                                                                                  |         |          |
| seaborn            | guess   |     46 |     44 |        2 |                      |                                                                                  |         |          |
| aiohttp            |         |        |        |          |                    0 |                 3 failed, 4840 passed, 535 skipped, 2 xfailed, 4 subtests passed |    95.7 |     98.0 |
| aiohttp            | certain |    537 |    519 |       18 |                      |                                                                                  |         |          |
| aiohttp            | likely  |    114 |    113 |        1 |                      |                                                                                  |         |          |
| aiohttp            | guess   |     84 |     78 |        6 |                      |                                                                                  |         |          |
| websockets         |         |        |        |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    28.5 |     32.2 |
| websockets         | certain |    259 |    258 |        1 |                      |                                                                                  |         |          |
| websockets         | likely  |     68 |     68 |        0 |                      |                                                                                  |         |          |
| websockets         | guess   |     36 |     36 |        0 |                      |                                                                                  |         |          |
| anyio              |         |        |        |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   104.5 |    118.5 |
| anyio              | certain |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | likely  |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | guess   |      0 |      0 |        0 |                      |                                                                                  |         |          |
| zarr               |         |        |        |          |                    0 |                                             8422 passed, 1205 skipped, 4 xfailed |   131.8 |    114.5 |
| zarr               | certain |    781 |    768 |       13 |                      |                                                                                  |         |          |
| zarr               | likely  |     52 |     52 |        0 |                      |                                                                                  |         |          |
| zarr               | guess   |     24 |     22 |        2 |                      |                                                                                  |         |          |
| joblib             |         |        |        |          |                   10 |                       10 failed, 1482 passed, 45 skipped, 4 xpassed, 82 warnings |   181.8 |    156.7 |
| joblib             | certain |    127 |    127 |        0 |                      |                                                                                  |         |          |
| joblib             | likely  |     16 |     16 |        0 |                      |                                                                                  |         |          |
| joblib             | guess   |     29 |     29 |        0 |                      |                                                                                  |         |          |
| networkx           |         |        |        |          |                  356 |                                            10083 passed, 62 skipped, 741 xfailed |    18.3 |     29.0 |
| networkx           | certain |    932 |    931 |        1 |                      |                                                                                  |         |          |
| networkx           | likely  |    188 |    187 |        1 |                      |                                                                                  |         |          |
| networkx           | guess   |    156 |    153 |        3 |                      |                                                                                  |         |          |
| nibabel            |         |        |        |          |                   76 |                      111 failed, 5166 passed, 303 skipped, 40 xfailed, 20 errors |    19.2 |     11.2 |
| nibabel            | certain |    415 |    412 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely  |    177 |    177 |        0 |                      |                                                                                  |         |          |
| nibabel            | guess   |    100 |     99 |        1 |                      |                                                                                  |         |          |
| narwhals           |         |        |        |          |                    0 |                               972 failed, 11116 passed, 235 skipped, 699 xfailed |    24.1 |     41.9 |
| narwhals           | certain |    553 |    550 |        3 |                      |                                                                                  |         |          |
| narwhals           | likely  |     41 |     41 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess   |     24 |     24 |        0 |                      |                                                                                  |         |          |
| xarray             |         |        |        |          |                   20 |  3 failed, 6333 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    17.4 |     28.0 |
| xarray             | certain |    970 |    960 |       10 |                      |                                                                                  |         |          |
| xarray             | likely  |    143 |    142 |        1 |                      |                                                                                  |         |          |
| xarray             | guess   |     87 |     86 |        1 |                      |                                                                                  |         |          |
| litestar           |         |        |        |          |                    0 |           7 failed, 5644 passed, 256 skipped, 13 xfailed, 30 xpassed, 3 warnings |    23.4 |     36.8 |
| litestar           | certain |    497 |    496 |        1 |                      |                                                                                  |         |          |
| litestar           | likely  |     94 |     94 |        0 |                      |                                                                                  |         |          |
| litestar           | guess   |     52 |     51 |        1 |                      |                                                                                  |         |          |
| celery             |         |        |        |          |                   66 |                                     4 failed, 3520 passed, 36 skipped, 3 xfailed |    49.7 |     49.9 |
| celery             | certain |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | likely  |     45 |     44 |        1 |                      |                                                                                  |         |          |
| celery             | guess   |     29 |     25 |        4 |                      |                                                                                  |         |          |
| optuna             |         |        |        |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 318 warnings, 16 errors |   156.8 |    133.3 |
| optuna             | certain |    695 |    695 |        0 |                      |                                                                                  |         |          |
| optuna             | likely  |    122 |    122 |        0 |                      |                                                                                  |         |          |
| optuna             | guess   |     56 |     56 |        0 |                      |                                                                                  |         |          |
| dask               |         |        |        |          |                  155 |         5 failed, 16196 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   154.1 |    133.8 |
| dask               | certain |  1,073 |  1,066 |        7 |                      |                                                                                  |         |          |
| dask               | likely  |    180 |    179 |        1 |                      |                                                                                  |         |          |
| dask               | guess   |    117 |    114 |        3 |                      |                                                                                  |         |          |
| mypy               |         |        |        |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   339.6 |    303.3 |
| mypy               | certain |  3,344 |  3,344 |        0 |                      |                                                                                  |         |          |
| mypy               | likely  |    713 |    713 |        0 |                      |                                                                                  |         |          |
| mypy               | guess   |    267 |    267 |        0 |                      |                                                                                  |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus             | shape                                        | no fix | traced | one type |
| ------------------ | -------------------------------------------- | -----: | -----: | -------: |
| django             | `call: chained .method()`                    |  1,353 |    955 |      602 |
| django             | `call: self.method()`                        |    978 |    656 |      423 |
| django             | `call: param.method()`                       |    654 |    477 |      376 |
| django             | `call: imported function`                    |    654 |    273 |      199 |
| django             | `call: local.method()`                       |    545 |    385 |      264 |
| django             | `empty list`                                 |    450 |      0 |        0 |
| django             | `copy: local`                                |    434 |    318 |      224 |
| django             | `attr: chained`                              |    406 |    279 |      183 |
| django             | `copy: param (unannotated)`                  |    348 |    238 |      142 |
| django             | `attr: self.x`                               |    342 |    270 |      140 |
| django             | `other constant`                             |    330 |     22 |       22 |
| django             | `None literal`                               |    319 |    103 |      103 |
| django             | `call: imported.attr()`                      |    301 |    145 |       98 |
| django             | `subscript: other`                           |    265 |    196 |      160 |
| django             | `dict (mixed/unknown elements)`              |    237 |    104 |       73 |
| django             | `empty dict`                                 |    201 |      0 |        0 |
| django             | `call: module function (unannotated)`        |    185 |    129 |       92 |
| django             | `tuple (mixed/unknown elements)`             |    176 |     95 |       72 |
| django             | `copy: imported`                             |    175 |      8 |        7 |
| django             | `call: builtin getattr()`                    |    174 |    154 |       72 |
| django             | `subscript: local[...]`                      |    173 |    108 |       89 |
| django             | `attr: local.x`                              |    170 |    129 |       92 |
| django             | `ListComp (unknown elements)`                |    165 |    119 |       82 |
| django             | `list (mixed/unknown elements)`              |    159 |     56 |       44 |
| django             | `conditional`                                |    157 |    127 |       65 |
| django             | `subscript: param[...]`                      |    136 |    111 |       93 |
| django             | `binop (unknown operands)`                   |    130 |     83 |       76 |
| django             | `attr: param.x`                              |    124 |    102 |       75 |
| django             | `boolop (or)`                                |    112 |     96 |       73 |
| django             | `call: builtin set()`                        |    109 |     16 |       12 |
| django             | `attr: imported.x`                           |    105 |     21 |       17 |
| django             | `call: imported class`                       |     95 |     14 |       14 |
| django             | `call: module.func()`                        |     94 |     69 |       59 |
| django             | `call: builtin enumerate()`                  |     85 |     66 |       37 |
| django             | `call: builtin sorted()`                     |     77 |     64 |       58 |
| django             | `call: builtin list()`                       |     62 |     48 |       35 |
| django             | `subscript: imported[...]`                   |     59 |     40 |       36 |
| django             | `DictComp (unknown elements)`                |     57 |     36 |       20 |
| django             | `call: builtin zip()`                        |     56 |     36 |       14 |
| django             | `call: other name`                           |     52 |     36 |       21 |
| django             | `call: local name`                           |     51 |     36 |       17 |
| django             | `call: builtin property()`                   |     49 |      0 |        0 |
| django             | `boolop (and)`                               |     42 |     29 |       22 |
| django             | `call: global.method()`                      |     42 |     29 |       18 |
| django             | `SetComp (unknown elements)`                 |     40 |     21 |       17 |
| django             | `copy: other`                                |     40 |      8 |        6 |
| django             | `empty tuple`                                |     39 |      0 |        0 |
| django             | `compare`                                    |     35 |     20 |       20 |
| django             | `call: builtin next()`                       |     32 |     31 |       27 |
| django             | `call: module class`                         |     31 |      7 |        7 |
| django             | `GeneratorExp (unknown elements)`            |     29 |     26 |       25 |
| django             | `binop (one side literal)`                   |     29 |      5 |        5 |
| django             | `copy: modclass`                             |     27 |      0 |        0 |
| django             | `copy: moddef`                               |     26 |      0 |        0 |
| django             | `copy: global`                               |     25 |      4 |        4 |
| django             | `call: other callee`                         |     24 |     17 |       13 |
| django             | `attr: module.x`                             |     21 |      5 |        4 |
| django             | `call: builtin iter()`                       |     21 |     17 |       16 |
| django             | `call: builtin reversed()`                   |     19 |     16 |        7 |
| django             | `await: call: self.method()`                 |     18 |     14 |        6 |
| django             | `call: builtin tuple()`                      |     18 |     14 |        8 |
| django             | `attr: modclass.x`                           |     17 |      1 |        1 |
| django             | `call: builtin type()`                       |     17 |     14 |       10 |
| django             | `await: call: chained .method()`             |     17 |     17 |        3 |
| django             | `call: other.method()`                       |     15 |     11 |        6 |
| django             | `call: builtin object()`                     |     14 |      2 |        2 |
| django             | `call: modclass.method()`                    |     14 |      5 |        5 |
| django             | `binop: literal % formatting`                |     13 |      8 |        8 |
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
| django             | `set (mixed/unknown elements)`               |      7 |      4 |        4 |
| django             | `call: builtin map()`                        |      7 |      3 |        2 |
| django             | `call: builtin min()`                        |      6 |      2 |        2 |
| django             | `call: builtin frozenset()`                  |      6 |      1 |        1 |
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
| django             | `call: builtin super()`                      |      1 |      1 |        1 |
| django             | `subscript: other[...]`                      |      1 |      1 |        0 |
| django             | `await: call: imported function`             |      1 |      1 |        0 |
| django             | `call: builtin __import__()`                 |      1 |      1 |        1 |
| django             | `call: builtin repr()`                       |      1 |      1 |        1 |
| django             | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| sqlalchemy         | `call: chained .method()`                    |    943 |    453 |      308 |
| sqlalchemy         | `other constant`                             |    602 |      8 |        8 |
| sqlalchemy         | `attr: chained`                              |    571 |    283 |      213 |
| sqlalchemy         | `call: self.method()`                        |    567 |    297 |      161 |
| sqlalchemy         | `call: local.method()`                       |    521 |    277 |      172 |
| sqlalchemy         | `call: param.method()`                       |    446 |    271 |      162 |
| sqlalchemy         | `attr: self.x`                               |    358 |    277 |      154 |
| sqlalchemy         | `subscript: other`                           |    354 |    214 |      139 |
| sqlalchemy         | `copy: local`                                |    351 |    216 |      134 |
| sqlalchemy         | `call: imported function`                    |    334 |    161 |       91 |
| sqlalchemy         | `call: imported.attr()`                      |    317 |    165 |      108 |
| sqlalchemy         | `attr: param.x`                              |    312 |    249 |      153 |
| sqlalchemy         | `attr: local.x`                              |    253 |    201 |      126 |
| sqlalchemy         | `tuple (mixed/unknown elements)`             |    202 |    135 |       91 |
| sqlalchemy         | `copy: param (unannotated)`                  |    183 |    134 |       93 |
| sqlalchemy         | `subscript: local[...]`                      |    173 |     93 |       55 |
| sqlalchemy         | `None literal`                               |    172 |     73 |       73 |
| sqlalchemy         | `ListComp (unknown elements)`                |    158 |    118 |       69 |
| sqlalchemy         | `copy: modclass`                             |    147 |      1 |        1 |
| sqlalchemy         | `attr: imported.x`                           |    145 |     17 |       17 |
| sqlalchemy         | `copy: imported`                             |    118 |      1 |        1 |
| sqlalchemy         | `call: builtin list()`                       |    117 |     75 |       45 |
| sqlalchemy         | `empty list`                                 |    114 |      0 |        0 |
| sqlalchemy         | `call: module.func()`                        |    107 |     51 |       43 |
| sqlalchemy         | `copy: param (annotated)`                    |    106 |     87 |       51 |
| sqlalchemy         | `dict (mixed/unknown elements)`              |    103 |     16 |       14 |
| sqlalchemy         | `call: builtin getattr()`                    |    100 |     82 |       38 |
| sqlalchemy         | `call: param name`                           |     90 |     36 |       14 |
| sqlalchemy         | `empty dict`                                 |     82 |      0 |        0 |
| sqlalchemy         | `call: builtin set()`                        |     82 |     33 |       22 |
| sqlalchemy         | `binop (unknown operands)`                   |     81 |     43 |       32 |
| sqlalchemy         | `call: other name`                           |     76 |     58 |       34 |
| sqlalchemy         | `subscript: param[...]`                      |     74 |     59 |       36 |
| sqlalchemy         | `boolop (or)`                                |     73 |     59 |       47 |
| sqlalchemy         | `conditional`                                |     71 |     41 |       22 |
| sqlalchemy         | `call: local name`                           |     63 |     51 |       23 |
| sqlalchemy         | `copy: other`                                |     63 |     19 |       14 |
| sqlalchemy         | `list (mixed/unknown elements)`              |     62 |     18 |       10 |
| sqlalchemy         | `DictComp (unknown elements)`                |     61 |     35 |       15 |
| sqlalchemy         | `call: module function (unannotated)`        |     59 |     49 |       38 |
| sqlalchemy         | `call: builtin zip()`                        |     57 |     39 |       19 |
| sqlalchemy         | `copy: global`                               |     50 |      6 |        6 |
| sqlalchemy         | `call: builtin dict()`                       |     49 |     24 |       13 |
| sqlalchemy         | `call: builtin enumerate()`                  |     39 |     29 |        6 |
| sqlalchemy         | `call: builtin tuple()`                      |     38 |     15 |        5 |
| sqlalchemy         | `call: other.method()`                       |     36 |     20 |       10 |
| sqlalchemy         | `SetComp (unknown elements)`                 |     35 |     21 |       15 |
| sqlalchemy         | `call: imported class`                       |     33 |      7 |        7 |
| sqlalchemy         | `call: module function (annotated)`          |     32 |     29 |       14 |
| sqlalchemy         | `call: cls.method()`                         |     30 |     24 |       16 |
| sqlalchemy         | `boolop (and)`                               |     25 |     25 |       21 |
| sqlalchemy         | `call: builtin.method()`                     |     24 |     23 |       10 |
| sqlalchemy         | `call: module class`                         |     23 |     15 |       15 |
| sqlalchemy         | `attr: modclass.x`                           |     21 |      0 |        0 |
| sqlalchemy         | `attr: cls.x`                                |     20 |     20 |       10 |
| sqlalchemy         | `empty tuple`                                |     16 |      0 |        0 |
| sqlalchemy         | `compare`                                    |     15 |      9 |        9 |
| sqlalchemy         | `call: builtin type()`                       |     15 |     10 |        3 |
| sqlalchemy         | `call: other callee`                         |     15 |     11 |        5 |
| sqlalchemy         | `await: call: imported function`             |     15 |     13 |        9 |
| sqlalchemy         | `attr: global.x`                             |     14 |      0 |        0 |
| sqlalchemy         | `GeneratorExp (unknown elements)`            |     13 |      6 |        6 |
| sqlalchemy         | `call: global.method()`                      |     13 |     11 |       11 |
| sqlalchemy         | `copy: moddef`                               |     13 |      0 |        0 |
| sqlalchemy         | `call: builtin sorted()`                     |     12 |      8 |        7 |
| sqlalchemy         | `subscript: global[...]`                     |     12 |     11 |        9 |
| sqlalchemy         | `call: global name`                          |     12 |     12 |        3 |
| sqlalchemy         | `attr: module.x`                             |     11 |      9 |        9 |
| sqlalchemy         | `copy: builtin`                              |     11 |      0 |        0 |
| sqlalchemy         | `attr: other.x`                              |     10 |      7 |        7 |
| sqlalchemy         | `call: builtin object()`                     |     10 |      6 |        6 |
| sqlalchemy         | `call: modclass.method()`                    |      8 |      8 |        5 |
| sqlalchemy         | `subscript: other[...]`                      |      8 |      8 |        4 |
| sqlalchemy         | `call: builtin reversed()`                   |      8 |      6 |        5 |
| sqlalchemy         | `copy: self`                                 |      7 |      6 |        5 |
| sqlalchemy         | `await: call: chained .method()`             |      6 |      1 |        1 |
| sqlalchemy         | `call: builtin __import__()`                 |      5 |      2 |        2 |
| sqlalchemy         | `set (mixed/unknown elements)`               |      5 |      3 |        2 |
| sqlalchemy         | `await: call: self.method()`                 |      4 |      4 |        4 |
| sqlalchemy         | `call: self name`                            |      4 |      4 |        2 |
| sqlalchemy         | `call: builtin frozenset()`                  |      4 |      0 |        0 |
| sqlalchemy         | `call: builtin int()`                        |      3 |      1 |        1 |
| sqlalchemy         | `binop (one side literal)`                   |      3 |      3 |        3 |
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
| pydantic           | `call: chained .method()`                    |    125 |     53 |       35 |
| pydantic           | `call: imported function`                    |    112 |     61 |       42 |
| pydantic           | `call: local.method()`                       |    111 |     55 |       30 |
| pydantic           | `call: param.method()`                       |    101 |     59 |       31 |
| pydantic           | `call: self.method()`                        |     56 |     32 |        9 |
| pydantic           | `call: builtin getattr()`                    |     53 |     29 |       17 |
| pydantic           | `call: module function (annotated)`          |     53 |     14 |        8 |
| pydantic           | `attr: param.x`                              |     46 |     25 |       12 |
| pydantic           | `conditional`                                |     37 |     18 |       10 |
| pydantic           | `copy: param (annotated)`                    |     36 |     20 |       12 |
| pydantic           | `copy: local`                                |     35 |     16 |       12 |
| pydantic           | `tuple (mixed/unknown elements)`             |     35 |      8 |        6 |
| pydantic           | `call: imported.attr()`                      |     33 |     28 |       10 |
| pydantic           | `attr: chained`                              |     33 |      5 |        4 |
| pydantic           | `subscript: other`                           |     32 |     11 |        3 |
| pydantic           | `boolop (or)`                                |     27 |     14 |        6 |
| pydantic           | `subscript: param[...]`                      |     26 |     15 |       12 |
| pydantic           | `empty dict`                                 |     25 |      0 |        0 |
| pydantic           | `attr: local.x`                              |     25 |      8 |        5 |
| pydantic           | `call: module class`                         |     23 |      2 |        2 |
| pydantic           | `dict (mixed/unknown elements)`              |     22 |     15 |       11 |
| pydantic           | `binop (unknown operands)`                   |     21 |      8 |        6 |
| pydantic           | `copy: imported`                             |     21 |      2 |        2 |
| pydantic           | `attr: cls.x`                                |     20 |      6 |        4 |
| pydantic           | `call: module.func()`                        |     20 |      9 |        6 |
| pydantic           | `subscript: imported[...]`                   |     20 |      1 |        0 |
| pydantic           | `None literal`                               |     19 |     10 |       10 |
| pydantic           | `other constant`                             |     18 |      1 |        1 |
| pydantic           | `ListComp (unknown elements)`                |     16 |      7 |        3 |
| pydantic           | `empty list`                                 |     16 |      0 |        0 |
| pydantic           | `DictComp (unknown elements)`                |     15 |      2 |        1 |
| pydantic           | `copy: builtin`                              |     14 |      0 |        0 |
| pydantic           | `call: builtin zip()`                        |     13 |      2 |        2 |
| pydantic           | `subscript: local[...]`                      |     12 |      4 |        4 |
| pydantic           | `copy: global`                               |     12 |      5 |        3 |
| pydantic           | `attr: self.x`                               |     12 |      5 |        2 |
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
| pydantic           | `call: builtin max()`                        |      2 |      2 |        2 |
| pydantic           | `call: builtin min()`                        |      2 |      2 |        2 |
| pydantic           | `call: str-literal.method()`                 |      2 |      0 |        0 |
| pydantic           | `call: builtin globals()`                    |      1 |      1 |        1 |
| pydantic           | `copy: moddef`                               |      1 |      0 |        0 |
| pydantic           | `call: modclass.method()`                    |      1 |      1 |        1 |
| pydantic           | `binop (one side literal)`                   |      1 |      1 |        1 |
| pydantic           | `call: builtin iter()`                       |      1 |      0 |        0 |
| pydantic           | `call: builtin open()`                       |      1 |      0 |        0 |
| pydantic           | `copy: self`                                 |      1 |      0 |        0 |
| pandas             | `call: local.method()`                       |  5,961 |  4,933 |    4,583 |
| pandas             | `call: chained .method()`                    |  4,671 |  3,604 |    3,280 |
| pandas             | `call: module.func()`                        |  3,372 |  2,230 |    2,121 |
| pandas             | `copy: param (unannotated)`                  |  1,960 |  1,740 |      794 |
| pandas             | `subscript: other`                           |  1,510 |  1,221 |    1,091 |
| pandas             | `call: imported function`                    |  1,456 |  1,038 |      883 |
| pandas             | `call: param.method()`                       |  1,413 |    987 |      779 |
| pandas             | `binop (unknown operands)`                   |  1,112 |    955 |      807 |
| pandas             | `subscript: local[...]`                      |    948 |    755 |      706 |
| pandas             | `attr: chained`                              |    792 |    529 |      433 |
| pandas             | `list (mixed/unknown elements)`              |    780 |    534 |      401 |
| pandas             | `call: param name`                           |    769 |    726 |      269 |
| pandas             | `call: imported class`                       |    737 |    632 |      627 |
| pandas             | `call: self.method()`                        |    588 |    398 |      240 |
| pandas             | `call: other callee`                         |    503 |    418 |      340 |
| pandas             | `conditional`                                |    470 |    377 |      200 |
| pandas             | `attr: local.x`                              |    439 |    333 |      271 |
| pandas             | `copy: local`                                |    412 |    274 |      194 |
| pandas             | `subscript: param[...]`                      |    384 |    276 |      163 |
| pandas             | `tuple (mixed/unknown elements)`             |    372 |    225 |      177 |
| pandas             | `call: imported.attr()`                      |    368 |    267 |      196 |
| pandas             | `ListComp (unknown elements)`                |    360 |    187 |      136 |
| pandas             | `compare`                                    |    347 |    271 |      250 |
| pandas             | `dict (mixed/unknown elements)`              |    332 |    208 |      182 |
| pandas             | `call: builtin getattr()`                    |    307 |    224 |      154 |
| pandas             | `call: builtin zip()`                        |    306 |    209 |      152 |
| pandas             | `call: local name`                           |    296 |    255 |      149 |
| pandas             | `attr: param.x`                              |    281 |    190 |      103 |
| pandas             | `call: module function (unannotated)`        |    278 |    135 |       84 |
| pandas             | `empty list`                                 |    276 |      0 |        0 |
| pandas             | `attr: self.x`                               |    274 |    193 |      107 |
| pandas             | `binop (one side literal)`                   |    254 |    201 |      180 |
| pandas             | `call: builtin enumerate()`                  |    233 |    156 |      107 |
| pandas             | `other constant`                             |    178 |     48 |       48 |
| pandas             | `call: builtin list()`                       |    170 |    124 |       84 |
| pandas             | `None literal`                               |    157 |    112 |      112 |
| pandas             | `attr: module.x`                             |    121 |     84 |       82 |
| pandas             | `Lambda`                                     |    120 |     77 |       77 |
| pandas             | `call: global.method()`                      |    118 |      4 |        2 |
| pandas             | `call: other name`                           |    113 |     75 |       52 |
| pandas             | `attr: imported.x`                           |     94 |     23 |       23 |
| pandas             | `empty dict`                                 |     90 |      0 |        0 |
| pandas             | `copy: imported`                             |     89 |     50 |       50 |
| pandas             | `call: module function (annotated)`          |     86 |     48 |       24 |
| pandas             | `copy: other`                                |     78 |      7 |        4 |
| pandas             | `copy: param (annotated)`                    |     70 |     47 |       33 |
| pandas             | `GeneratorExp (unknown elements)`            |     70 |     60 |       60 |
| pandas             | `call: capitalised`                          |     60 |     59 |       58 |
| pandas             | `copy: builtin`                              |     59 |     42 |       42 |
| pandas             | `DictComp (unknown elements)`                |     58 |     43 |       33 |
| pandas             | `call: builtin set()`                        |     49 |     18 |       13 |
| pandas             | `unaryop Invert`                             |     40 |     30 |       28 |
| pandas             | `call: other.method()`                       |     39 |     20 |       15 |
| pandas             | `boolop (and)`                               |     37 |     23 |       21 |
| pandas             | `call: builtin next()`                       |     35 |     29 |       21 |
| pandas             | `call: builtin divmod()`                     |     35 |     24 |       24 |
| pandas             | `boolop (or)`                                |     32 |     20 |       20 |
| pandas             | `call: builtin dict()`                       |     31 |     11 |        6 |
| pandas             | `call: builtin sorted()`                     |     29 |     23 |       22 |
| pandas             | `call: builtin tuple()`                      |     26 |     17 |        9 |
| pandas             | `call: builtin type()`                       |     26 |     25 |        6 |
| pandas             | `call: builtin slice()`                      |     25 |     23 |       23 |
| pandas             | `call: cls name`                             |     22 |     15 |        1 |
| pandas             | `call: builtin open()`                       |     20 |     13 |        6 |
| pandas             | `unaryop USub`                               |     19 |     14 |       14 |
| pandas             | `call: builtin max()`                        |     19 |     15 |       13 |
| pandas             | `copy: self`                                 |     18 |     15 |        9 |
| pandas             | `subscript: self[...]`                       |     18 |     16 |       10 |
| pandas             | `subscript: imported[...]`                   |     17 |     13 |       11 |
| pandas             | `copy: moddef`                               |     17 |      0 |        0 |
| pandas             | `attr: other.x`                              |     14 |      1 |        1 |
| pandas             | `SetComp (unknown elements)`                 |     14 |     10 |        5 |
| pandas             | `copy: global`                               |     13 |      7 |        6 |
| pandas             | `subscript: global[...]`                     |     13 |     11 |        4 |
| pandas             | `call: cls.method()`                         |     12 |     11 |        8 |
| pandas             | `set (mixed/unknown elements)`               |     12 |      5 |        5 |
| pandas             | `call: builtin min()`                        |     12 |      7 |        6 |
| pandas             | `call: modclass.method()`                    |     11 |      8 |        8 |
| pandas             | `call: builtin len()`                        |     11 |      4 |        4 |
| pandas             | `call: builtin.method()`                     |     10 |      9 |        8 |
| pandas             | `copy: modclass`                             |     10 |      0 |        0 |
| pandas             | `JoinedStr`                                  |      8 |      4 |        4 |
| pandas             | `attr: cls.x`                                |      7 |      5 |        4 |
| pandas             | `call: builtin map()`                        |      7 |      7 |        7 |
| pandas             | `call: builtin abs()`                        |      7 |      6 |        6 |
| pandas             | `call: module class`                         |      7 |      3 |        2 |
| pandas             | `subscript: other[...]`                      |      6 |      3 |        3 |
| pandas             | `call: builtin iter()`                       |      6 |      4 |        4 |
| pandas             | `call: builtin property()`                   |      5 |      0 |        0 |
| pandas             | `call: builtin frozenset()`                  |      5 |      1 |        1 |
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
| structlog          | `copy: local`                                |      5 |      4 |        4 |
| structlog          | `call: self.method()`                        |      4 |      4 |        0 |
| structlog          | `empty list`                                 |      4 |      0 |        0 |
| structlog          | `call: module.func()`                        |      4 |      3 |        3 |
| structlog          | `attr: self.x`                               |      3 |      3 |        1 |
| structlog          | `boolop (or)`                                |      3 |      3 |        1 |
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
| attrs              | `ListComp (unknown elements)`                |      8 |      5 |        4 |
| attrs              | `attr: local.x`                              |      8 |      7 |        5 |
| attrs              | `conditional`                                |      7 |      4 |        4 |
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
| attrs              | `call: builtin zip()`                        |      3 |      3 |        2 |
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
| attrs              | `call: builtin dict()`                       |      1 |      0 |        0 |
| click              | `call: chained .method()`                    |     26 |     21 |       15 |
| click              | `other constant`                             |     17 |      0 |        0 |
| click              | `call: imported function`                    |     16 |     12 |        8 |
| click              | `call: self.method()`                        |     12 |     11 |        3 |
| click              | `call: local.method()`                       |     12 |      9 |        7 |
| click              | `call: builtin getattr()`                    |      9 |      5 |        3 |
| click              | `empty list`                                 |      9 |      0 |        0 |
| click              | `call: module.func()`                        |      9 |      4 |        4 |
| click              | `attr: imported.x`                           |      9 |      6 |        6 |
| click              | `None literal`                               |      9 |      7 |        7 |
| click              | `conditional`                                |      9 |      7 |        7 |
| click              | `attr: self.x`                               |      7 |      5 |        3 |
| click              | `call: param.method()`                       |      7 |      5 |        4 |
| click              | `call: other name`                           |      6 |      4 |        4 |
| click              | `attr: global.x`                             |      5 |      0 |        0 |
| click              | `copy: param (annotated)`                    |      5 |      2 |        2 |
| click              | `call: module function (annotated)`          |      4 |      4 |        0 |
| click              | `copy: local`                                |      4 |      2 |        2 |
| click              | `call: other callee`                         |      4 |      1 |        1 |
| click              | `call: capitalised`                          |      4 |      0 |        0 |
| click              | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| click              | `boolop (and)`                               |      4 |      4 |        4 |
| click              | `call: imported.attr()`                      |      3 |      2 |        1 |
| click              | `call: imported class`                       |      3 |      2 |        2 |
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
| hypercorn          | `call: local.method()`                       |     12 |      2 |        1 |
| hypercorn          | `call: param.method()`                       |     11 |      2 |        1 |
| hypercorn          | `attr: param.x`                              |     11 |      8 |        8 |
| hypercorn          | `None literal`                               |     10 |      3 |        3 |
| hypercorn          | `binop (unknown operands)`                   |      9 |      1 |        1 |
| hypercorn          | `call: imported class`                       |      7 |      3 |        3 |
| hypercorn          | `subscript: param[...]`                      |      6 |      6 |        6 |
| hypercorn          | `call: other.method()`                       |      5 |      3 |        3 |
| hypercorn          | `await: call: chained .method()`             |      4 |      1 |        1 |
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
| starlette          | `call: chained .method()`                    |     22 |     20 |       14 |
| starlette          | `call: builtin reversed()`                   |     15 |      4 |        2 |
| starlette          | `subscript: param[...]`                      |     14 |     14 |       13 |
| starlette          | `attr: self.x`                               |     11 |      8 |        4 |
| starlette          | `await: call: self.method()`                 |     10 |      9 |        2 |
| starlette          | `call: module.func()`                        |      9 |      9 |        7 |
| starlette          | `other constant`                             |      9 |      0 |        0 |
| starlette          | `call: imported function`                    |      9 |      9 |        7 |
| starlette          | `call: self.method()`                        |      9 |      8 |        7 |
| starlette          | `tuple (mixed/unknown elements)`             |      8 |      7 |        6 |
| starlette          | `call: other callee`                         |      8 |      8 |        8 |
| starlette          | `await: call: module.func()`                 |      7 |      7 |        6 |
| starlette          | `attr: chained`                              |      6 |      6 |        5 |
| starlette          | `copy: param (annotated)`                    |      6 |      5 |        2 |
| starlette          | `dict (mixed/unknown elements)`              |      6 |      2 |        2 |
| starlette          | `None literal`                               |      5 |      4 |        4 |
| starlette          | `conditional`                                |      5 |      5 |        2 |
| starlette          | `subscript: local[...]`                      |      5 |      5 |        4 |
| starlette          | `copy: local`                                |      5 |      4 |        4 |
| starlette          | `ListComp (unknown elements)`                |      5 |      4 |        4 |
| starlette          | `call: builtin getattr()`                    |      5 |      5 |        3 |
| starlette          | `call: builtin dict()`                       |      5 |      2 |        2 |
| starlette          | `await: call: local.method()`                |      5 |      4 |        3 |
| starlette          | `attr: local.x`                              |      4 |      4 |        4 |
| starlette          | `boolop (or)`                                |      4 |      4 |        3 |
| starlette          | `binop (unknown operands)`                   |      4 |      1 |        1 |
| starlette          | `await: call: other name`                    |      4 |      4 |        2 |
| starlette          | `call: builtin set()`                        |      4 |      3 |        3 |
| starlette          | `call: imported class`                       |      3 |      3 |        2 |
| starlette          | `await: call: chained .method()`             |      3 |      3 |        2 |
| starlette          | `await: call: param name`                    |      3 |      3 |        1 |
| starlette          | `await: call: local name`                    |      2 |      2 |        2 |
| starlette          | `subscript: other`                           |      2 |      2 |        1 |
| starlette          | `attr: param.x`                              |      2 |      2 |        1 |
| starlette          | `boolop (and)`                               |      2 |      2 |        2 |
| starlette          | `subscript: imported[...]`                   |      2 |      1 |        0 |
| starlette          | `call: global.method()`                      |      1 |      1 |        1 |
| starlette          | `attr: imported.x`                           |      1 |      1 |        1 |
| starlette          | `binop (one side literal)`                   |      1 |      0 |        0 |
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
| werkzeug           | `call: chained .method()`                    |     63 |     43 |       29 |
| werkzeug           | `call: param.method()`                       |     32 |     29 |       22 |
| werkzeug           | `call: imported function`                    |     32 |     17 |       15 |
| werkzeug           | `copy: local`                                |     31 |     18 |       13 |
| werkzeug           | `call: local.method()`                       |     30 |     16 |       12 |
| werkzeug           | `call: module function (annotated)`          |     27 |     12 |        8 |
| werkzeug           | `empty list`                                 |     23 |      0 |        0 |
| werkzeug           | `call: other callee`                         |     20 |      0 |        0 |
| werkzeug           | `attr: self.x`                               |     19 |     15 |       13 |
| werkzeug           | `call: module.func()`                        |     17 |     10 |        8 |
| werkzeug           | `call: builtin getattr()`                    |     16 |     16 |        9 |
| werkzeug           | `call: self.method()`                        |     15 |     11 |        8 |
| werkzeug           | `copy: self`                                 |     13 |     11 |        6 |
| werkzeug           | `call: other name`                           |     11 |      9 |        8 |
| werkzeug           | `None literal`                               |     11 |     10 |       10 |
| werkzeug           | `subscript: other`                           |     10 |      3 |        3 |
| werkzeug           | `copy: param (annotated)`                    |      9 |      4 |        2 |
| werkzeug           | `list (mixed/unknown elements)`              |      9 |      8 |        7 |
| werkzeug           | `call: local name`                           |      8 |      8 |        7 |
| werkzeug           | `call: builtin set()`                        |      7 |      0 |        0 |
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
| mkdocs             | `call: imported.attr()`                      |    327 |      7 |        7 |
| mkdocs             | `call: self.method()`                        |    114 |    106 |      103 |
| mkdocs             | `call: local.method()`                       |     56 |     31 |       31 |
| mkdocs             | `dict (mixed/unknown elements)`              |     43 |     33 |       33 |
| mkdocs             | `attr: param.x`                              |     36 |     31 |       30 |
| mkdocs             | `call: param.method()`                       |     31 |     23 |       20 |
| mkdocs             | `call: imported function`                    |     30 |     14 |       13 |
| mkdocs             | `call: chained .method()`                    |     29 |     19 |       17 |
| mkdocs             | `tuple (mixed/unknown elements)`             |     29 |     29 |        9 |
| mkdocs             | `copy: local`                                |     25 |     19 |       15 |
| mkdocs             | `attr: chained`                              |     25 |     21 |       21 |
| mkdocs             | `call: module.func()`                        |     24 |     10 |        9 |
| mkdocs             | `call: other name`                           |     15 |      0 |        0 |
| mkdocs             | `call: other callee`                         |     15 |      0 |        0 |
| mkdocs             | `list (mixed/unknown elements)`              |     13 |     10 |        8 |
| mkdocs             | `attr: self.x`                               |     12 |     12 |        7 |
| mkdocs             | `call: module class`                         |     12 |      1 |        1 |
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
| mkdocs             | `call: imported class`                       |      3 |      2 |        2 |
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
| httpx              | `call: param.method()`                       |     26 |     19 |       12 |
| httpx              | `call: local.method()`                       |     24 |     18 |       16 |
| httpx              | `attr: self.x`                               |     24 |     20 |       14 |
| httpx              | `call: chained .method()`                    |     23 |     21 |       17 |
| httpx              | `subscript: imported[...]`                   |     18 |      0 |        0 |
| httpx              | `subscript: other`                           |     17 |      2 |        2 |
| httpx              | `boolop (or)`                                |     11 |      9 |        9 |
| httpx              | `call: self.method()`                        |      9 |      6 |        4 |
| httpx              | `attr: chained`                              |      8 |      6 |        6 |
| httpx              | `dict (mixed/unknown elements)`              |      8 |      7 |        7 |
| httpx              | `subscript: param[...]`                      |      8 |      4 |        4 |
| httpx              | `ListComp (unknown elements)`                |      8 |      6 |        6 |
| httpx              | `copy: local`                                |      7 |      2 |        2 |
| httpx              | `None literal`                               |      7 |      7 |        7 |
| httpx              | `call: imported class`                       |      5 |      5 |        5 |
| httpx              | `conditional`                                |      5 |      5 |        3 |
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
| black              | `attr: param.x`                              |     59 |     57 |       30 |
| black              | `subscript: other`                           |     36 |     31 |       16 |
| black              | `attr: local.x`                              |     34 |     30 |       21 |
| black              | `call: local.method()`                       |     32 |     30 |       21 |
| black              | `attr: chained`                              |     19 |     15 |       12 |
| black              | `copy: local`                                |     18 |     15 |       12 |
| black              | `call: chained .method()`                    |     17 |     14 |       12 |
| black              | `copy: builtin`                              |     16 |      0 |        0 |
| black              | `call: imported function`                    |     13 |      5 |        4 |
| black              | `subscript: local[...]`                      |     12 |     11 |       11 |
| black              | `boolop (and)`                               |     11 |      9 |        7 |
| black              | `conditional`                                |     10 |     10 |        6 |
| black              | `empty list`                                 |     10 |      0 |        0 |
| black              | `call: builtin enumerate()`                  |      8 |      8 |        4 |
| black              | `call: module function (annotated)`          |      7 |      5 |        5 |
| black              | `call: module.func()`                        |      7 |      4 |        4 |
| black              | `copy: param (annotated)`                    |      7 |      6 |        6 |
| black              | `call: param.method()`                       |      6 |      6 |        4 |
| black              | `binop (one side literal)`                   |      5 |      5 |        5 |
| black              | `attr: imported.x`                           |      4 |      4 |        4 |
| black              | `binop (unknown operands)`                   |      4 |      4 |        4 |
| black              | `list (mixed/unknown elements)`              |      4 |      4 |        2 |
| black              | `tuple (mixed/unknown elements)`             |      4 |      3 |        1 |
| black              | `call: builtin next()`                       |      4 |      4 |        4 |
| black              | `call: builtin set()`                        |      3 |      1 |        1 |
| black              | `compare`                                    |      3 |      2 |        2 |
| black              | `call: builtin list()`                       |      3 |      3 |        3 |
| black              | `None literal`                               |      3 |      3 |        3 |
| black              | `attr: self.x`                               |      3 |      2 |        2 |
| black              | `copy: imported`                             |      2 |      1 |        1 |
| black              | `call: builtin getattr()`                    |      2 |      2 |        0 |
| black              | `SetComp (unknown elements)`                 |      2 |      2 |        2 |
| black              | `ListComp (unknown elements)`                |      2 |      1 |        1 |
| black              | `boolop (or)`                                |      2 |      2 |        2 |
| black              | `call: other name`                           |      2 |      2 |        2 |
| black              | `call: builtin min()`                        |      1 |      1 |        1 |
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
| black              | `call: global.method()`                      |      1 |      1 |        1 |
| black              | `other constant`                             |      1 |      0 |        0 |
| black              | `subscript: global[...]`                     |      1 |      0 |        0 |
| black              | `attr: other.x`                              |      1 |      1 |        1 |
| fastapi            | `call: chained .method()`                    |     42 |     40 |       20 |
| fastapi            | `call: module function (annotated)`          |     41 |     26 |       13 |
| fastapi            | `call: imported function`                    |     38 |     30 |        7 |
| fastapi            | `call: local.method()`                       |     28 |     20 |       16 |
| fastapi            | `call: param.method()`                       |     27 |     24 |       11 |
| fastapi            | `call: builtin getattr()`                    |     25 |     22 |       19 |
| fastapi            | `copy: local`                                |     18 |     17 |       11 |
| fastapi            | `attr: local.x`                              |     13 |     13 |        7 |
| fastapi            | `attr: self.x`                               |     12 |     11 |        6 |
| fastapi            | `dict (mixed/unknown elements)`              |     11 |      5 |        2 |
| fastapi            | `conditional`                                |     11 |     11 |        6 |
| fastapi            | `empty dict`                                 |      9 |      0 |        0 |
| fastapi            | `boolop (or)`                                |      9 |      7 |        4 |
| fastapi            | `call: imported class`                       |      7 |      7 |        7 |
| fastapi            | `DictComp (unknown elements)`                |      6 |      4 |        3 |
| fastapi            | `None literal`                               |      6 |      6 |        6 |
| fastapi            | `copy: param (annotated)`                    |      6 |      5 |        2 |
| fastapi            | `call: module.func()`                        |      6 |      6 |        5 |
| fastapi            | `call: self.method()`                        |      6 |      6 |        6 |
| fastapi            | `ListComp (unknown elements)`                |      5 |      4 |        2 |
| fastapi            | `attr: param.x`                              |      5 |      4 |        4 |
| fastapi            | `call: other callee`                         |      5 |      5 |        5 |
| fastapi            | `call: global.method()`                      |      5 |      3 |        2 |
| fastapi            | `call: builtin dict()`                       |      5 |      2 |        0 |
| fastapi            | `call: other.method()`                       |      4 |      4 |        3 |
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
| fastapi            | `await: call: local.method()`                |      1 |      1 |        1 |
| fastapi            | `call: builtin object()`                     |      1 |      0 |        0 |
| fastapi            | `other constant`                             |      1 |      0 |        0 |
| fastapi            | `call: imported.attr()`                      |      1 |      1 |        1 |
| fastapi            | `call: builtin type()`                       |      1 |      1 |        0 |
| fastapi            | `compare`                                    |      1 |      1 |        1 |
| fastapi            | `attr: other.x`                              |      1 |      1 |        0 |
| cattrs             | `call: imported function`                    |     54 |     43 |       16 |
| cattrs             | `attr: local.x`                              |     20 |     18 |       12 |
| cattrs             | `empty dict`                                 |     20 |      0 |        0 |
| cattrs             | `copy: local`                                |     19 |     19 |        9 |
| cattrs             | `call: builtin getattr()`                    |     18 |     15 |        3 |
| cattrs             | `empty list`                                 |     18 |      0 |        0 |
| cattrs             | `attr: param.x`                              |     15 |     15 |        7 |
| cattrs             | `call: chained .method()`                    |     14 |     12 |        7 |
| cattrs             | `copy: imported`                             |     11 |      3 |        3 |
| cattrs             | `conditional`                                |     10 |     10 |        5 |
| cattrs             | `attr: global.x`                             |      9 |      1 |        1 |
| cattrs             | `call: builtin set()`                        |      8 |      3 |        0 |
| cattrs             | `subscript: local[...]`                      |      8 |      6 |        5 |
| cattrs             | `call: local.method()`                       |      8 |      8 |        4 |
| cattrs             | `boolop (or)`                                |      7 |      6 |        2 |
| cattrs             | `SetComp (unknown elements)`                 |      7 |      7 |        3 |
| cattrs             | `copy: builtin`                              |      6 |      4 |        4 |
| cattrs             | `call: param.method()`                       |      6 |      5 |        4 |
| cattrs             | `subscript: other`                           |      6 |      5 |        0 |
| cattrs             | `call: builtin zip()`                        |      6 |      6 |        2 |
| cattrs             | `subscript: param[...]`                      |      6 |      6 |        4 |
| cattrs             | `copy: param (annotated)`                    |      6 |      6 |        3 |
| cattrs             | `None literal`                               |      6 |      5 |        5 |
| cattrs             | `call: module function (annotated)`          |      6 |      6 |        2 |
| cattrs             | `attr: imported.x`                           |      5 |      4 |        0 |
| cattrs             | `attr: chained`                              |      5 |      5 |        5 |
| cattrs             | `call: other.method()`                       |      5 |      5 |        3 |
| cattrs             | `dict (mixed/unknown elements)`              |      5 |      5 |        0 |
| cattrs             | `DictComp (unknown elements)`                |      4 |      2 |        1 |
| cattrs             | `call: builtin enumerate()`                  |      4 |      4 |        2 |
| cattrs             | `attr: self.x`                               |      4 |      4 |        1 |
| cattrs             | `ListComp (unknown elements)`                |      4 |      4 |        3 |
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
| pytest             | `call: chained .method()`                    |    157 |    130 |      103 |
| pytest             | `call: self.method()`                        |     88 |     75 |       62 |
| pytest             | `attr: chained`                              |     68 |     55 |       49 |
| pytest             | `copy: local`                                |     61 |     46 |       37 |
| pytest             | `call: local.method()`                       |     55 |     42 |       36 |
| pytest             | `attr: param.x`                              |     55 |     47 |       38 |
| pytest             | `call: builtin getattr()`                    |     51 |     46 |       29 |
| pytest             | `call: param.method()`                       |     51 |     45 |       40 |
| pytest             | `empty list`                                 |     49 |      0 |        0 |
| pytest             | `call: module.func()`                        |     46 |     30 |       25 |
| pytest             | `attr: local.x`                              |     45 |     35 |       24 |
| pytest             | `subscript: other`                           |     42 |     28 |       18 |
| pytest             | `attr: self.x`                               |     28 |     26 |       17 |
| pytest             | `None literal`                               |     27 |     22 |       22 |
| pytest             | `conditional`                                |     27 |     23 |       17 |
| pytest             | `tuple (mixed/unknown elements)`             |     23 |     19 |       17 |
| pytest             | `copy: param (annotated)`                    |     23 |     17 |       10 |
| pytest             | `call: module function (annotated)`          |     22 |     21 |        8 |
| pytest             | `binop (unknown operands)`                   |     20 |     17 |       14 |
| pytest             | `call: imported class`                       |     19 |      5 |        5 |
| pytest             | `other constant`                             |     17 |      4 |        4 |
| pytest             | `boolop (or)`                                |     17 |     11 |       10 |
| pytest             | `call: other callee`                         |     17 |      4 |        4 |
| pytest             | `ListComp (unknown elements)`                |     15 |     11 |        9 |
| pytest             | `call: imported.attr()`                      |     15 |      9 |        8 |
| pytest             | `call: other name`                           |     14 |     12 |        9 |
| pytest             | `call: builtin list()`                       |     12 |      9 |        8 |
| pytest             | `call: module class`                         |     12 |     10 |       10 |
| pytest             | `call: imported function`                    |     11 |      9 |        7 |
| pytest             | `call: builtin enumerate()`                  |     10 |      6 |        2 |
| pytest             | `Yield`                                      |     10 |      7 |        7 |
| pytest             | `copy: other`                                |     10 |      1 |        1 |
| pytest             | `subscript: local[...]`                      |      9 |      5 |        4 |
| pytest             | `DictComp (unknown elements)`                |      9 |      6 |        3 |
| pytest             | `list (mixed/unknown elements)`              |      9 |      7 |        6 |
| pytest             | `call: builtin reversed()`                   |      9 |      8 |        5 |
| pytest             | `dict (mixed/unknown elements)`              |      8 |      4 |        4 |
| pytest             | `call: module function (unannotated)`        |      8 |      3 |        3 |
| pytest             | `call: builtin sorted()`                     |      8 |      6 |        6 |
| pytest             | `compare`                                    |      7 |      7 |        7 |
| pytest             | `unaryop USub`                               |      7 |      3 |        3 |
| pytest             | `attr: module.x`                             |      7 |      5 |        2 |
| pytest             | `subscript: global[...]`                     |      7 |      6 |        6 |
| pytest             | `subscript: param[...]`                      |      6 |      4 |        2 |
| pytest             | `binop (one side literal)`                   |      6 |      6 |        6 |
| pytest             | `-`                                          |      6 |      0 |        0 |
| pytest             | `copy: param (unannotated)`                  |      5 |      5 |        4 |
| pytest             | `empty dict`                                 |      5 |      0 |        0 |
| pytest             | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| pytest             | `call: builtin type()`                       |      4 |      3 |        0 |
| pytest             | `call: builtin zip()`                        |      4 |      4 |        3 |
| pytest             | `call: other.method()`                       |      4 |      4 |        3 |
| pytest             | `call: modclass.method()`                    |      4 |      4 |        4 |
| pytest             | `call: builtin.method()`                     |      4 |      2 |        1 |
| pytest             | `call: builtin dict()`                       |      3 |      2 |        2 |
| pytest             | `call: builtin max()`                        |      3 |      3 |        3 |
| pytest             | `copy: modclass`                             |      3 |      0 |        0 |
| pytest             | `call: builtin set()`                        |      3 |      2 |        0 |
| pytest             | `call: builtin compile()`                    |      3 |      3 |        3 |
| pytest             | `copy: self`                                 |      2 |      2 |        2 |
| pytest             | `call: builtin str()`                        |      2 |      2 |        2 |
| pytest             | `boolop (and)`                               |      2 |      2 |        0 |
| pytest             | `call: cls.method()`                         |      2 |      2 |        2 |
| pytest             | `copy: imported`                             |      2 |      2 |        2 |
| pytest             | `call: global.method()`                      |      2 |      2 |        2 |
| pytest             | `call: builtin abs()`                        |      2 |      0 |        0 |
| pytest             | `call: builtin sum()`                        |      2 |      2 |        2 |
| pytest             | `call: builtin property()`                   |      1 |      0 |        0 |
| pytest             | `Lambda`                                     |      1 |      1 |        1 |
| pytest             | `JoinedStr`                                  |      1 |      1 |        1 |
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
| pytest             | `call: builtin eval()`                       |      1 |      1 |        0 |
| pytest             | `call: builtin min()`                        |      1 |      0 |        0 |
| botocore           | `call: self.method()`                        |    362 |    318 |      203 |
| botocore           | `call: chained .method()`                    |    345 |    297 |      188 |
| botocore           | `call: param.method()`                       |    245 |    215 |      141 |
| botocore           | `call: local.method()`                       |    233 |    197 |      122 |
| botocore           | `copy: param (unannotated)`                  |    100 |     92 |       67 |
| botocore           | `subscript: other`                           |     97 |     77 |       62 |
| botocore           | `call: imported function`                    |     84 |     66 |       55 |
| botocore           | `attr: param.x`                              |     79 |     74 |       36 |
| botocore           | `empty dict`                                 |     76 |      0 |        0 |
| botocore           | `subscript: local[...]`                      |     75 |     69 |       47 |
| botocore           | `copy: local`                                |     71 |     66 |       51 |
| botocore           | `dict (mixed/unknown elements)`              |     70 |     36 |       27 |
| botocore           | `subscript: param[...]`                      |     65 |     53 |       32 |
| botocore           | `attr: self.x`                               |     60 |     57 |       31 |
| botocore           | `attr: chained`                              |     55 |     38 |       32 |
| botocore           | `empty list`                                 |     48 |      0 |        0 |
| botocore           | `call: module.func()`                        |     37 |     26 |       14 |
| botocore           | `call: module function (unannotated)`        |     33 |     26 |       19 |
| botocore           | `binop (unknown operands)`                   |     30 |     26 |       22 |
| botocore           | `tuple (mixed/unknown elements)`             |     25 |     16 |       16 |
| botocore           | `None literal`                               |     25 |     20 |       20 |
| botocore           | `attr: local.x`                              |     24 |     22 |       16 |
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
| botocore           | `compare`                                    |     12 |      8 |        8 |
| botocore           | `boolop (and)`                               |     11 |      8 |        8 |
| botocore           | `call: builtin sorted()`                     |     10 |     10 |        9 |
| botocore           | `copy: modclass`                             |     10 |      0 |        0 |
| botocore           | `call: imported class`                       |     10 |      1 |        1 |
| botocore           | `copy: global`                               |      9 |      1 |        1 |
| botocore           | `call: modclass.method()`                    |      9 |      9 |        9 |
| botocore           | `copy: other`                                |      9 |      0 |        0 |
| botocore           | `call: builtin type()`                       |      8 |      8 |        3 |
| botocore           | `attr: module.x`                             |      8 |      1 |        1 |
| botocore           | `copy: imported`                             |      7 |      1 |        1 |
| botocore           | `conditional`                                |      6 |      4 |        2 |
| botocore           | `call: builtin iter()`                       |      6 |      5 |        5 |
| botocore           | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| botocore           | `call: builtin list()`                       |      5 |      3 |        3 |
| botocore           | `call: builtin zip()`                        |      5 |      5 |        2 |
| botocore           | `copy: builtin`                              |      5 |      0 |        0 |
| botocore           | `binop (one side literal)`                   |      4 |      3 |        3 |
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
| uvicorn            | `call: chained .method()`                    |     32 |     29 |       24 |
| uvicorn            | `call: param.method()`                       |     30 |     26 |       17 |
| uvicorn            | `binop (unknown operands)`                   |     14 |      9 |        6 |
| uvicorn            | `conditional`                                |      9 |      8 |        5 |
| uvicorn            | `subscript: param[...]`                      |      7 |      7 |        6 |
| uvicorn            | `copy: local`                                |      6 |      5 |        5 |
| uvicorn            | `dict (mixed/unknown elements)`              |      6 |      2 |        2 |
| uvicorn            | `call: self.method()`                        |      6 |      5 |        1 |
| uvicorn            | `call: local.method()`                       |      6 |      6 |        5 |
| uvicorn            | `attr: chained`                              |      6 |      6 |        6 |
| uvicorn            | `attr: local.x`                              |      6 |      6 |        6 |
| uvicorn            | `attr: self.x`                               |      6 |      5 |        4 |
| uvicorn            | `call: module.func()`                        |      5 |      0 |        0 |
| uvicorn            | `copy: imported`                             |      4 |      3 |        3 |
| uvicorn            | `await: call: param name`                    |      4 |      4 |        0 |
| uvicorn            | `ListComp (unknown elements)`                |      4 |      3 |        3 |
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
| mcp                | `call: chained .method()`                    |     73 |     67 |       41 |
| mcp                | `call: other callee`                         |     50 |     44 |       44 |
| mcp                | `call: imported function`                    |     46 |     38 |       20 |
| mcp                | `call: param.method()`                       |     42 |     41 |       13 |
| mcp                | `call: module.func()`                        |     41 |     35 |       19 |
| mcp                | `conditional`                                |     41 |     39 |       17 |
| mcp                | `copy: local`                                |     36 |     30 |       21 |
| mcp                | `call: local.method()`                       |     35 |     30 |        9 |
| mcp                | `call: module function (annotated)`          |     20 |     19 |       10 |
| mcp                | `attr: param.x`                              |     19 |     19 |        9 |
| mcp                | `call: imported class`                       |     18 |      6 |        6 |
| mcp                | `call: imported.attr()`                      |     17 |     17 |       14 |
| mcp                | `await: call: param.method()`                |     16 |     13 |       10 |
| mcp                | `await: call: self.method()`                 |     16 |     16 |        7 |
| mcp                | `await: call: local.method()`                |     15 |     13 |       10 |
| mcp                | `attr: local.x`                              |     14 |     14 |        9 |
| mcp                | `boolop (or)`                                |     13 |     10 |        9 |
| mcp                | `attr: self.x`                               |     12 |     12 |        7 |
| mcp                | `attr: chained`                              |     12 |     12 |        6 |
| mcp                | `await: call: chained .method()`             |     12 |     12 |        5 |
| mcp                | `None literal`                               |     11 |      8 |        8 |
| mcp                | `tuple (mixed/unknown elements)`             |     11 |      8 |        6 |
| mcp                | `subscript: other`                           |     10 |      9 |        8 |
| mcp                | `call: builtin getattr()`                    |     10 |      7 |        3 |
| mcp                | `copy: param (annotated)`                    |     10 |      9 |        7 |
| mcp                | `ListComp (unknown elements)`                |     10 |      8 |        7 |
| mcp                | `Yield`                                      |     10 |      9 |        9 |
| mcp                | `dict (mixed/unknown elements)`              |     10 |      9 |        9 |
| mcp                | `call: self.method()`                        |      9 |      8 |        6 |
| mcp                | `copy: other`                                |      9 |      7 |        7 |
| mcp                | `call: global.method()`                      |      9 |      7 |        4 |
| mcp                | `await: call: param name`                    |      5 |      5 |        2 |
| mcp                | `call: other.method()`                       |      5 |      4 |        3 |
| mcp                | `call: module class`                         |      5 |      5 |        5 |
| mcp                | `copy: imported`                             |      4 |      1 |        1 |
| mcp                | `boolop (and)`                               |      4 |      4 |        3 |
| mcp                | `subscript: local[...]`                      |      4 |      3 |        3 |
| mcp                | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| mcp                | `-`                                          |      4 |      0 |        0 |
| mcp                | `await: call: module function (annotated)`   |      4 |      4 |        1 |
| mcp                | `call: builtin next()`                       |      4 |      4 |        1 |
| mcp                | `binop (unknown operands)`                   |      4 |      1 |        0 |
| mcp                | `call: builtin enumerate()`                  |      4 |      4 |        4 |
| mcp                | `list (mixed/unknown elements)`              |      3 |      3 |        3 |
| mcp                | `await: call: other name`                    |      3 |      3 |        0 |
| mcp                | `await: call: local name`                    |      3 |      3 |        1 |
| mcp                | `copy: builtin`                              |      3 |      0 |        0 |
| mcp                | `call: module function (unannotated)`        |      2 |      0 |        0 |
| mcp                | `other constant`                             |      2 |      0 |        0 |
| mcp                | `call: builtin tuple()`                      |      2 |      1 |        0 |
| mcp                | `subscript: imported[...]`                   |      2 |      2 |        2 |
| mcp                | `attr: other.x`                              |      2 |      2 |        1 |
| mcp                | `await: call: module.func()`                 |      2 |      0 |        0 |
| mcp                | `await: call: imported function`             |      2 |      2 |        0 |
| mcp                | `call: builtin dict()`                       |      2 |      1 |        1 |
| mcp                | `DictComp (unknown elements)`                |      2 |      1 |        1 |
| mcp                | `call: builtin object()`                     |      2 |      1 |        1 |
| mcp                | `binop (one side literal)`                   |      1 |      1 |        1 |
| mcp                | `empty dict`                                 |      1 |      0 |        0 |
| mcp                | `set (mixed/unknown elements)`               |      1 |      1 |        1 |
| mcp                | `call: param name`                           |      1 |      1 |        1 |
| mcp                | `await: copy: param (annotated)`             |      1 |      1 |        1 |
| mcp                | `copy: global`                               |      1 |      0 |        0 |
| mcp                | `call: builtin set()`                        |      1 |      1 |        1 |
| mcp                | `call: builtin reversed()`                   |      1 |      1 |        0 |
| mcp                | `call: other name`                           |      1 |      1 |        0 |
| mcp                | `call: builtin sorted()`                     |      1 |      0 |        0 |
| mcp                | `compare`                                    |      1 |      1 |        1 |
| mcp                | `await: call: other.method()`                |      1 |      1 |        0 |
| mcp                | `call: builtin frozenset()`                  |      1 |      1 |        1 |
| mcp                | `subscript: param[...]`                      |      1 |      0 |        0 |
| pdm                | `call: chained .method()`                    |    144 |    120 |       97 |
| pdm                | `call: local.method()`                       |    107 |     86 |       76 |
| pdm                | `attr: chained`                              |     66 |     53 |       38 |
| pdm                | `call: module.func()`                        |     60 |     40 |       37 |
| pdm                | `call: imported function`                    |     56 |     50 |       48 |
| pdm                | `call: param.method()`                       |     54 |     48 |       37 |
| pdm                | `conditional`                                |     50 |     44 |       26 |
| pdm                | `tuple (mixed/unknown elements)`             |     40 |     12 |        8 |
| pdm                | `call: imported.attr()`                      |     35 |     32 |       27 |
| pdm                | `copy: local`                                |     33 |     28 |       23 |
| pdm                | `attr: local.x`                              |     30 |     25 |       11 |
| pdm                | `boolop (or)`                                |     30 |     27 |       22 |
| pdm                | `subscript: other`                           |     28 |     22 |       20 |
| pdm                | `attr: param.x`                              |     26 |     20 |       15 |
| pdm                | `dict (mixed/unknown elements)`              |     19 |     11 |       10 |
| pdm                | `attr: self.x`                               |     19 |     16 |        8 |
| pdm                | `ListComp (unknown elements)`                |     18 |     11 |       10 |
| pdm                | `other constant`                             |     17 |      3 |        3 |
| pdm                | `binop (unknown operands)`                   |     16 |      9 |        8 |
| pdm                | `copy: param (annotated)`                    |     16 |     13 |        4 |
| pdm                | `call: builtin list()`                       |     16 |     10 |        8 |
| pdm                | `call: builtin sorted()`                     |     15 |     10 |        9 |
| pdm                | `list (mixed/unknown elements)`              |     14 |     11 |       11 |
| pdm                | `call: module function (annotated)`          |     14 |     11 |        9 |
| pdm                | `call: builtin next()`                       |     13 |      9 |        7 |
| pdm                | `empty dict`                                 |     13 |      0 |        0 |
| pdm                | `empty list`                                 |     13 |      0 |        0 |
| pdm                | `call: cls.method()`                         |     12 |     12 |        0 |
| pdm                | `call: self.method()`                        |     11 |     11 |        9 |
| pdm                | `call: other name`                           |      9 |      7 |        6 |
| pdm                | `DictComp (unknown elements)`                |      8 |      4 |        4 |
| pdm                | `call: builtin getattr()`                    |      7 |      7 |        5 |
| pdm                | `call: builtin zip()`                        |      7 |      3 |        3 |
| pdm                | `call: builtin enumerate()`                  |      6 |      6 |        5 |
| pdm                | `subscript: local[...]`                      |      6 |      4 |        4 |
| pdm                | `binop (one side literal)`                   |      5 |      5 |        5 |
| pdm                | `None literal`                               |      5 |      3 |        3 |
| pdm                | `compare`                                    |      4 |      3 |        3 |
| pdm                | `call: imported class`                       |      4 |      4 |        4 |
| pdm                | `subscript: param[...]`                      |      4 |      2 |        2 |
| pdm                | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| pdm                | `call: moddef.method()`                      |      4 |      0 |        0 |
| pdm                | `call: builtin set()`                        |      3 |      1 |        0 |
| pdm                | `boolop (and)`                               |      3 |      3 |        1 |
| pdm                | `call: module function (unannotated)`        |      3 |      0 |        0 |
| pdm                | `call: local name`                           |      3 |      3 |        1 |
| pdm                | `call: other.method()`                       |      3 |      2 |        2 |
| pdm                | `empty tuple`                                |      2 |      0 |        0 |
| pdm                | `copy: imported`                             |      2 |      1 |        1 |
| pdm                | `call: builtin iter()`                       |      2 |      2 |        2 |
| pdm                | `call: other callee`                         |      2 |      2 |        1 |
| pdm                | `call: builtin dict()`                       |      2 |      2 |        2 |
| pdm                | `call: builtin object()`                     |      2 |      1 |        1 |
| pdm                | `call: global.method()`                      |      2 |      2 |        2 |
| pdm                | `call: str-literal.method()`                 |      2 |      2 |        2 |
| pdm                | `call: builtin frozenset()`                  |      2 |      0 |        0 |
| pdm                | `call: module class`                         |      2 |      2 |        2 |
| pdm                | `JoinedStr`                                  |      1 |      1 |        1 |
| pdm                | `copy: global`                               |      1 |      1 |        1 |
| pdm                | `call: builtin filter()`                     |      1 |      1 |        1 |
| pdm                | `subscript: imported[...]`                   |      1 |      0 |        0 |
| pdm                | `attr: other.x`                              |      1 |      0 |        0 |
| pdm                | `call: builtin open()`                       |      1 |      0 |        0 |
| pdm                | `set (mixed/unknown elements)`               |      1 |      1 |        1 |
| pdm                | `call: builtin reversed()`                   |      1 |      1 |        1 |
| pdm                | `attr: imported.x`                           |      1 |      0 |        0 |
| pdm                | `call: builtin min()`                        |      1 |      1 |        1 |
| strawberry-graphql | `call: chained .method()`                    |     67 |     44 |       23 |
| strawberry-graphql | `call: imported function`                    |     64 |     48 |       13 |
| strawberry-graphql | `attr: chained`                              |     56 |     43 |       31 |
| strawberry-graphql | `call: builtin getattr()`                    |     43 |     32 |       15 |
| strawberry-graphql | `attr: param.x`                              |     42 |     34 |       21 |
| strawberry-graphql | `conditional`                                |     41 |     32 |        9 |
| strawberry-graphql | `call: self.method()`                        |     39 |     20 |       15 |
| strawberry-graphql | `call: local.method()`                       |     39 |     23 |       11 |
| strawberry-graphql | `attr: local.x`                              |     39 |     32 |       18 |
| strawberry-graphql | `subscript: other`                           |     35 |     22 |       18 |
| strawberry-graphql | `copy: local`                                |     28 |     17 |       12 |
| strawberry-graphql | `call: module function (annotated)`          |     24 |     19 |        3 |
| strawberry-graphql | `call: module.func()`                        |     23 |     18 |       12 |
| strawberry-graphql | `call: param.method()`                       |     21 |     11 |        4 |
| strawberry-graphql | `ListComp (unknown elements)`                |     17 |      9 |        5 |
| strawberry-graphql | `empty list`                                 |     17 |      0 |        0 |
| strawberry-graphql | `copy: imported`                             |     16 |      1 |        1 |
| strawberry-graphql | `attr: self.x`                               |     15 |     13 |        5 |
| strawberry-graphql | `tuple (mixed/unknown elements)`             |     14 |      4 |        2 |
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
| strawberry-graphql | `other constant`                             |      8 |      1 |        1 |
| strawberry-graphql | `copy: modclass`                             |      8 |      0 |        0 |
| strawberry-graphql | `call: imported class`                       |      8 |      5 |        5 |
| strawberry-graphql | `dict (mixed/unknown elements)`              |      8 |      1 |        1 |
| strawberry-graphql | `call: builtin enumerate()`                  |      8 |      8 |        6 |
| strawberry-graphql | `call: other name`                           |      8 |      6 |        3 |
| strawberry-graphql | `call: builtin sorted()`                     |      7 |      1 |        0 |
| strawberry-graphql | `await: call: chained .method()`             |      6 |      0 |        0 |
| strawberry-graphql | `subscript: param[...]`                      |      6 |      2 |        1 |
| strawberry-graphql | `call: builtin list()`                       |      6 |      3 |        1 |
| strawberry-graphql | `attr: module.x`                             |      6 |      0 |        0 |
| strawberry-graphql | `SetComp (unknown elements)`                 |      6 |      5 |        5 |
| strawberry-graphql | `call: builtin tuple()`                      |      5 |      5 |        1 |
| strawberry-graphql | `await: call: imported function`             |      5 |      5 |        3 |
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
| pygments           | `dict (mixed/unknown elements)`              |    560 |      2 |        2 |
| pygments           | `empty list`                                 |    159 |      0 |        0 |
| pygments           | `binop (unknown operands)`                   |    124 |      6 |        6 |
| pygments           | `call: imported.attr()`                      |    108 |    100 |       98 |
| pygments           | `binop (one side literal)`                   |    102 |     20 |       20 |
| pygments           | `copy: param (unannotated)`                  |     97 |     88 |       88 |
| pygments           | `call: imported function`                    |     91 |     24 |       19 |
| pygments           | `call: local.method()`                       |     90 |     66 |       63 |
| pygments           | `call: param.method()`                       |     78 |     74 |       70 |
| pygments           | `attr: module.x`                             |     64 |      0 |        0 |
| pygments           | `call: chained .method()`                    |     63 |     48 |       39 |
| pygments           | `copy: local`                                |     60 |     46 |       42 |
| pygments           | `call: self.method()`                        |     52 |     41 |       36 |
| pygments           | `tuple (mixed/unknown elements)`             |     51 |     11 |       11 |
| pygments           | `attr: self.x`                               |     42 |     35 |       25 |
| pygments           | `empty dict`                                 |     38 |      0 |        0 |
| pygments           | `call: module.func()`                        |     35 |      8 |        8 |
| pygments           | `subscript: local[...]`                      |     29 |     23 |       23 |
| pygments           | `copy: global`                               |     27 |      1 |        1 |
| pygments           | `call: builtin set()`                        |     26 |      0 |        0 |
| pygments           | `None literal`                               |     26 |     17 |       17 |
| pygments           | `other constant`                             |     26 |      0 |        0 |
| pygments           | `list (mixed/unknown elements)`              |     24 |      6 |        6 |
| pygments           | `call: other name`                           |     23 |      3 |        1 |
| pygments           | `call: module function (unannotated)`        |     22 |     13 |        8 |
| pygments           | `subscript: other`                           |     19 |     13 |       13 |
| pygments           | `subscript: global[...]`                     |     17 |      5 |        3 |
| pygments           | `attr: imported.x`                           |     16 |      4 |        4 |
| pygments           | `call: modclass.method()`                    |     16 |     16 |       16 |
| pygments           | `attr: chained`                              |     15 |      8 |        8 |
| pygments           | `attr: param.x`                              |     14 |     14 |        9 |
| pygments           | `attr: global.x`                             |     14 |      0 |        0 |
| pygments           | `call: builtin enumerate()`                  |     13 |      9 |        9 |
| pygments           | `copy: modclass`                             |     13 |      2 |        2 |
| pygments           | `empty tuple`                                |     13 |      0 |        0 |
| pygments           | `call: builtin sorted()`                     |     12 |      2 |        2 |
| pygments           | `boolop (or)`                                |     11 |      9 |        8 |
| pygments           | `call: other.method()`                       |     10 |      5 |        5 |
| pygments           | `attr: local.x`                              |      9 |      4 |        4 |
| pygments           | `call: global.method()`                      |      9 |      3 |        1 |
| pygments           | `subscript: param[...]`                      |      8 |      7 |        6 |
| pygments           | `copy: other`                                |      8 |      2 |        2 |
| pygments           | `copy: imported`                             |      8 |      2 |        2 |
| pygments           | `conditional`                                |      7 |      6 |        6 |
| pygments           | `call: builtin getattr()`                    |      6 |      3 |        1 |
| pygments           | `JoinedStr`                                  |      5 |      0 |        0 |
| pygments           | `DictComp (unknown elements)`                |      5 |      0 |        0 |
| pygments           | `ListComp (unknown elements)`                |      4 |      3 |        3 |
| pygments           | `call: builtin __import__()`                 |      4 |      2 |        2 |
| pygments           | `call: builtin list()`                       |      4 |      3 |        3 |
| pygments           | `call: local name`                           |      4 |      3 |        1 |
| pygments           | `attr: modclass.x`                           |      4 |      0 |        0 |
| pygments           | `set (mixed/unknown elements)`               |      4 |      0 |        0 |
| pygments           | `attr: cls.x`                                |      3 |      3 |        2 |
| pygments           | `call: cls.method()`                         |      3 |      2 |        1 |
| pygments           | `boolop (and)`                               |      2 |      2 |        1 |
| pygments           | `call: imported class`                       |      2 |      0 |        0 |
| pygments           | `call: builtin dict()`                       |      2 |      1 |        1 |
| pygments           | `call: builtin next()`                       |      2 |      2 |        2 |
| pygments           | `call: builtin max()`                        |      2 |      1 |        1 |
| pygments           | `call: builtin zip()`                        |      2 |      0 |        0 |
| pygments           | `call: builtin open()`                       |      1 |      1 |        1 |
| pygments           | `subscript: imported[...]`                   |      1 |      1 |        1 |
| pygments           | `call: builtin staticmethod()`               |      1 |      0 |        0 |
| pygments           | `call: module class`                         |      1 |      1 |        1 |
| pygments           | `call: builtin sum()`                        |      1 |      0 |        0 |
| pygments           | `call: builtin min()`                        |      1 |      1 |        1 |
| pygments           | `call: builtin.method()`                     |      1 |      1 |        0 |
| streamlink         | `call: chained .method()`                    |    441 |     59 |       49 |
| streamlink         | `copy: local`                                |    198 |     27 |       23 |
| streamlink         | `call: self.method()`                        |    182 |     34 |       30 |
| streamlink         | `Yield`                                      |    118 |      6 |        5 |
| streamlink         | `call: local.method()`                       |    117 |     31 |       27 |
| streamlink         | `call: imported function`                    |     73 |     40 |       37 |
| streamlink         | `call: imported.attr()`                      |     62 |      7 |        7 |
| streamlink         | `call: param.method()`                       |     38 |     23 |        7 |
| streamlink         | `boolop (or)`                                |     37 |     19 |       17 |
| streamlink         | `subscript: other`                           |     35 |      6 |        3 |
| streamlink         | `subscript: local[...]`                      |     31 |      5 |        4 |
| streamlink         | `call: module.func()`                        |     29 |     14 |       13 |
| streamlink         | `other constant`                             |     29 |      6 |        6 |
| streamlink         | `attr: chained`                              |     28 |     17 |       16 |
| streamlink         | `dict (mixed/unknown elements)`              |     26 |      2 |        2 |
| streamlink         | `copy: param (unannotated)`                  |     20 |      6 |        5 |
| streamlink         | `tuple (mixed/unknown elements)`             |     19 |     16 |       14 |
| streamlink         | `attr: param.x`                              |     16 |     13 |        6 |
| streamlink         | `conditional`                                |     15 |     11 |        5 |
| streamlink         | `attr: self.x`                               |     15 |      9 |        8 |
| streamlink         | `empty dict`                                 |     14 |      0 |        0 |
| streamlink         | `binop (unknown operands)`                   |     14 |     14 |       11 |
| streamlink         | `None literal`                               |     13 |      3 |        3 |
| streamlink         | `call: builtin next()`                       |     13 |      1 |        0 |
| streamlink         | `empty list`                                 |     11 |      0 |        0 |
| streamlink         | `boolop (and)`                               |      9 |      0 |        0 |
| streamlink         | `await: call: chained .method()`             |      9 |      9 |        7 |
| streamlink         | `attr: local.x`                              |      8 |      7 |        7 |
| streamlink         | `list (mixed/unknown elements)`              |      8 |      3 |        3 |
| streamlink         | `call: builtin sorted()`                     |      8 |      2 |        1 |
| streamlink         | `call: builtin getattr()`                    |      8 |      8 |        5 |
| streamlink         | `call: other callee`                         |      7 |      2 |        1 |
| streamlink         | `ListComp (unknown elements)`                |      6 |      3 |        1 |
| streamlink         | `call: builtin dict()`                       |      6 |      2 |        2 |
| streamlink         | `binop (one side literal)`                   |      5 |      1 |        1 |
| streamlink         | `DictComp (unknown elements)`                |      5 |      0 |        0 |
| streamlink         | `call: other.method()`                       |      5 |      5 |        3 |
| streamlink         | `call: builtin list()`                       |      4 |      3 |        3 |
| streamlink         | `call: builtin enumerate()`                  |      4 |      2 |        1 |
| streamlink         | `call: module function (unannotated)`        |      4 |      2 |        0 |
| streamlink         | `call: builtin type()`                       |      4 |      4 |        1 |
| streamlink         | `call: modclass.method()`                    |      3 |      1 |        1 |
| streamlink         | `subscript: other[...]`                      |      3 |      3 |        0 |
| streamlink         | `set (mixed/unknown elements)`               |      3 |      2 |        2 |
| streamlink         | `call: imported class`                       |      3 |      1 |        1 |
| streamlink         | `call: local name`                           |      3 |      2 |        1 |
| streamlink         | `call: cls.method()`                         |      3 |      3 |        2 |
| streamlink         | `call: builtin set()`                        |      3 |      0 |        0 |
| streamlink         | `attr: module.x`                             |      2 |      0 |        0 |
| streamlink         | `attr: global.x`                             |      2 |      0 |        0 |
| streamlink         | `call: global.method()`                      |      2 |      0 |        0 |
| streamlink         | `call: builtin max()`                        |      2 |      2 |        2 |
| streamlink         | `attr: other.x`                              |      2 |      1 |        0 |
| streamlink         | `call: param name`                           |      2 |      2 |        1 |
| streamlink         | `call: builtin reversed()`                   |      2 |      2 |        2 |
| streamlink         | `call: builtin divmod()`                     |      2 |      2 |        0 |
| streamlink         | `await: call: self.method()`                 |      2 |      2 |        2 |
| streamlink         | `call: builtin len()`                        |      1 |      1 |        1 |
| streamlink         | `call: builtin min()`                        |      1 |      1 |        1 |
| streamlink         | `copy: param (annotated)`                    |      1 |      1 |        1 |
| streamlink         | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| streamlink         | `-`                                          |      1 |      0 |        0 |
| streamlink         | `call: other name`                           |      1 |      0 |        0 |
| streamlink         | `compare`                                    |      1 |      1 |        1 |
| streamlink         | `call: builtin super()`                      |      1 |      1 |        1 |
| streamlink         | `attr: modclass.x`                           |      1 |      1 |        1 |
| streamlink         | `attr: cls.x`                                |      1 |      1 |        1 |
| streamlink         | `call: builtin filter()`                     |      1 |      1 |        1 |
| streamlink         | `copy: other`                                |      1 |      1 |        1 |
| streamlink         | `await: call: param.method()`                |      1 |      1 |        1 |
| streamlink         | `await: call: module.func()`                 |      1 |      0 |        0 |
| streamlink         | `attr: imported.x`                           |      1 |      0 |        0 |
| streamlink         | `call: module class`                         |      1 |      1 |        1 |
| streamlink         | `call: cls name`                             |      1 |      1 |        1 |
| sphinx             | `call: chained .method()`                    |    429 |    324 |      254 |
| sphinx             | `other constant`                             |    356 |      4 |        4 |
| sphinx             | `call: imported function`                    |    242 |    112 |       92 |
| sphinx             | `call: local.method()`                       |    228 |    162 |      134 |
| sphinx             | `attr: chained`                              |    178 |    136 |      121 |
| sphinx             | `copy: local`                                |    160 |    124 |      107 |
| sphinx             | `call: imported.attr()`                      |    113 |     77 |       66 |
| sphinx             | `call: param.method()`                       |    112 |     93 |       59 |
| sphinx             | `subscript: other`                           |    109 |     87 |       75 |
| sphinx             | `empty list`                                 |    104 |      0 |        0 |
| sphinx             | `binop (unknown operands)`                   |     98 |     64 |       63 |
| sphinx             | `list (mixed/unknown elements)`              |     89 |     50 |       50 |
| sphinx             | `attr: self.x`                               |     83 |     69 |       67 |
| sphinx             | `subscript: local[...]`                      |     76 |     61 |       58 |
| sphinx             | `attr: local.x`                              |     73 |     63 |       48 |
| sphinx             | `copy: other`                                |     69 |      2 |        2 |
| sphinx             | `subscript: param[...]`                      |     66 |     59 |       55 |
| sphinx             | `tuple (mixed/unknown elements)`             |     66 |     25 |       20 |
| sphinx             | `dict (mixed/unknown elements)`              |     64 |     19 |       17 |
| sphinx             | `attr: param.x`                              |     62 |     45 |       32 |
| sphinx             | `call: self.method()`                        |     60 |     37 |       27 |
| sphinx             | `call: module.func()`                        |     59 |     49 |       46 |
| sphinx             | `call: builtin list()`                       |     53 |     35 |       33 |
| sphinx             | `call: builtin getattr()`                    |     42 |     30 |       13 |
| sphinx             | `None literal`                               |     42 |     33 |       33 |
| sphinx             | `call: module function (annotated)`          |     41 |     36 |       14 |
| sphinx             | `boolop (or)`                                |     34 |     25 |       22 |
| sphinx             | `copy: imported`                             |     34 |      9 |        8 |
| sphinx             | `ListComp (unknown elements)`                |     32 |     24 |       22 |
| sphinx             | `binop (one side literal)`                   |     32 |     21 |       21 |
| sphinx             | `copy: param (annotated)`                    |     29 |     22 |       12 |
| sphinx             | `conditional`                                |     28 |     24 |       20 |
| sphinx             | `call: other name`                           |     24 |     17 |        9 |
| sphinx             | `call: param name`                           |     24 |     20 |       18 |
| sphinx             | `empty dict`                                 |     21 |      0 |        0 |
| sphinx             | `call: imported class`                       |     19 |     17 |       17 |
| sphinx             | `attr: imported.x`                           |     18 |      5 |        5 |
| sphinx             | `call: local name`                           |     17 |      9 |        9 |
| sphinx             | `call: global.method()`                      |     15 |     13 |       10 |
| sphinx             | `call: builtin sorted()`                     |     14 |     13 |       11 |
| sphinx             | `call: builtin enumerate()`                  |     13 |     10 |        7 |
| sphinx             | `copy: global`                               |     13 |      3 |        3 |
| sphinx             | `call: builtin object()`                     |     13 |      5 |        5 |
| sphinx             | `compare`                                    |     12 |     10 |       10 |
| sphinx             | `DictComp (unknown elements)`                |     12 |      8 |        8 |
| sphinx             | `call: builtin zip()`                        |     12 |      7 |        7 |
| sphinx             | `call: builtin frozenset()`                  |     12 |      6 |        6 |
| sphinx             | `call: builtin set()`                        |     10 |      4 |        4 |
| sphinx             | `boolop (and)`                               |     10 |      9 |        9 |
| sphinx             | `GeneratorExp (unknown elements)`            |      9 |      8 |        8 |
| sphinx             | `subscript: imported[...]`                   |      9 |      6 |        6 |
| sphinx             | `subscript: global[...]`                     |      7 |      4 |        4 |
| sphinx             | `call: builtin reversed()`                   |      6 |      1 |        0 |
| sphinx             | `subscript: self[...]`                       |      5 |      5 |        4 |
| sphinx             | `copy: modclass`                             |      5 |      0 |        0 |
| sphinx             | `attr: cls.x`                                |      5 |      3 |        1 |
| sphinx             | `call: builtin next()`                       |      5 |      3 |        1 |
| sphinx             | `call: builtin type()`                       |      5 |      4 |        2 |
| sphinx             | `call: builtin dict()`                       |      5 |      3 |        2 |
| sphinx             | `call: other.method()`                       |      5 |      5 |        3 |
| sphinx             | `call: module class`                         |      5 |      3 |        3 |
| sphinx             | `call: builtin tuple()`                      |      5 |      3 |        3 |
| sphinx             | `SetComp (unknown elements)`                 |      4 |      3 |        3 |
| sphinx             | `attr: module.x`                             |      4 |      2 |        2 |
| sphinx             | `JoinedStr`                                  |      4 |      2 |        2 |
| sphinx             | `attr: modclass.x`                           |      4 |      4 |        2 |
| sphinx             | `call: str-literal.method()`                 |      3 |      2 |        2 |
| sphinx             | `call: builtin max()`                        |      2 |      2 |        2 |
| sphinx             | `call: builtin divmod()`                     |      2 |      2 |        2 |
| sphinx             | `set (mixed/unknown elements)`               |      2 |      1 |        1 |
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
| tox                | `call: chained .method()`                    |    117 |    102 |       87 |
| tox                | `call: local.method()`                       |     40 |     32 |       24 |
| tox                | `call: param.method()`                       |     30 |     28 |       16 |
| tox                | `conditional`                                |     30 |     27 |       22 |
| tox                | `tuple (mixed/unknown elements)`             |     29 |     21 |       17 |
| tox                | `subscript: other`                           |     27 |     22 |       21 |
| tox                | `attr: chained`                              |     27 |     23 |       22 |
| tox                | `call: imported function`                    |     24 |     19 |       16 |
| tox                | `copy: local`                                |     24 |     20 |       18 |
| tox                | `call: builtin getattr()`                    |     22 |     17 |       13 |
| tox                | `call: self.method()`                        |     18 |     17 |       12 |
| tox                | `call: module.func()`                        |     17 |     12 |        6 |
| tox                | `attr: self.x`                               |     16 |     15 |        6 |
| tox                | `copy: param (annotated)`                    |     16 |     14 |        8 |
| tox                | `boolop (or)`                                |     13 |     12 |        8 |
| tox                | `call: builtin set()`                        |     13 |     10 |       10 |
| tox                | `ListComp (unknown elements)`                |     10 |      8 |        8 |
| tox                | `subscript: local[...]`                      |     10 |      8 |        3 |
| tox                | `attr: local.x`                              |     10 |     10 |        9 |
| tox                | `dict (mixed/unknown elements)`              |      7 |      4 |        4 |
| tox                | `empty list`                                 |      6 |      0 |        0 |
| tox                | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| tox                | `attr: imported.x`                           |      6 |      4 |        4 |
| tox                | `binop (unknown operands)`                   |      6 |      5 |        5 |
| tox                | `call: builtin sorted()`                     |      5 |      4 |        4 |
| tox                | `call: imported class`                       |      5 |      4 |        4 |
| tox                | `binop (one side literal)`                   |      5 |      5 |        5 |
| tox                | `attr: module.x`                             |      5 |      1 |        1 |
| tox                | `call: global.method()`                      |      4 |      2 |        1 |
| tox                | `call: builtin enumerate()`                  |      4 |      4 |        2 |
| tox                | `None literal`                               |      4 |      2 |        2 |
| tox                | `call: other name`                           |      4 |      2 |        1 |
| tox                | `call: builtin.method()`                     |      4 |      3 |        2 |
| tox                | `attr: param.x`                              |      4 |      3 |        3 |
| tox                | `other constant`                             |      4 |      0 |        0 |
| tox                | `call: builtin list()`                       |      3 |      2 |        2 |
| tox                | `GeneratorExp (unknown elements)`            |      3 |      3 |        3 |
| tox                | `subscript: param[...]`                      |      3 |      3 |        1 |
| tox                | `Yield`                                      |      3 |      3 |        3 |
| tox                | `compare`                                    |      3 |      3 |        3 |
| tox                | `call: module function (annotated)`          |      3 |      3 |        2 |
| tox                | `call: imported.attr()`                      |      3 |      3 |        2 |
| tox                | `call: builtin object()`                     |      2 |      0 |        0 |
| tox                | `call: builtin next()`                       |      2 |      0 |        0 |
| tox                | `call: str-literal.method()`                 |      2 |      1 |        1 |
| tox                | `empty dict`                                 |      2 |      0 |        0 |
| tox                | `call: builtin reversed()`                   |      2 |      0 |        0 |
| tox                | `call: module class`                         |      2 |      0 |        0 |
| tox                | `SetComp (unknown elements)`                 |      1 |      1 |        1 |
| tox                | `call: builtin type()`                       |      1 |      0 |        0 |
| tox                | `copy: imported`                             |      1 |      0 |        0 |
| tox                | `empty tuple`                                |      1 |      0 |        0 |
| tox                | `copy: modclass`                             |      1 |      0 |        0 |
| tox                | `call: builtin max()`                        |      1 |      0 |        0 |
| tox                | `subscript: other[...]`                      |      1 |      1 |        1 |
| tox                | `boolop (and)`                               |      1 |      1 |        1 |
| tox                | `call: local name`                           |      1 |      1 |        1 |
| tox                | `call: builtin id()`                         |      1 |      1 |        1 |
| tox                | `JoinedStr`                                  |      1 |      1 |        1 |
| tox                | `call: builtin vars()`                       |      1 |      0 |        0 |
| tox                | `call: cls.method()`                         |      1 |      1 |        1 |
| tox                | `call: other.method()`                       |      1 |      1 |        1 |
| pint               | `call: self.method()`                        |    274 |     40 |       34 |
| pint               | `call: local.method()`                       |    164 |     26 |       22 |
| pint               | `call: chained .method()`                    |    151 |     48 |       39 |
| pint               | `binop (unknown operands)`                   |    134 |     13 |        8 |
| pint               | `tuple (mixed/unknown elements)`             |    128 |      2 |        1 |
| pint               | `call: param.method()`                       |    104 |     27 |       25 |
| pint               | `copy: param (unannotated)`                  |     99 |      5 |        3 |
| pint               | `call: module.func()`                        |     96 |      4 |        3 |
| pint               | `call: imported function`                    |     88 |     40 |       28 |
| pint               | `binop (one side literal)`                   |     79 |      2 |        2 |
| pint               | `call: imported.attr()`                      |     65 |     13 |       11 |
| pint               | `attr: chained`                              |     64 |     22 |       20 |
| pint               | `call: module function (unannotated)`        |     37 |     28 |       23 |
| pint               | `call: other callee`                         |     34 |      0 |        0 |
| pint               | `call: imported class`                       |     33 |      3 |        3 |
| pint               | `attr: self.x`                               |     29 |     12 |       12 |
| pint               | `call: builtin zip()`                        |     27 |      6 |        3 |
| pint               | `attr: param.x`                              |     26 |      6 |        6 |
| pint               | `call: other name`                           |     26 |     11 |        3 |
| pint               | `call: param name`                           |     22 |      5 |        3 |
| pint               | `copy: local`                                |     21 |     11 |       10 |
| pint               | `subscript: local[...]`                      |     21 |     17 |       15 |
| pint               | `attr: local.x`                              |     20 |      4 |        3 |
| pint               | `list (mixed/unknown elements)`              |     19 |      1 |        1 |
| pint               | `call: capitalised`                          |     19 |      0 |        0 |
| pint               | `call: builtin tuple()`                      |     17 |      7 |        7 |
| pint               | `call: module function (annotated)`          |     16 |     13 |       11 |
| pint               | `call: builtin dict()`                       |     16 |      3 |        2 |
| pint               | `call: local name`                           |     16 |      1 |        1 |
| pint               | `subscript: other`                           |     15 |      4 |        2 |
| pint               | `call: builtin getattr()`                    |     14 |     10 |        7 |
| pint               | `attr: imported.x`                           |     14 |      1 |        1 |
| pint               | `empty list`                                 |     13 |      0 |        0 |
| pint               | `call: builtin enumerate()`                  |     12 |      8 |        7 |
| pint               | `ListComp (unknown elements)`                |     12 |      9 |        6 |
| pint               | `copy: param (annotated)`                    |     11 |      6 |        5 |
| pint               | `None literal`                               |     10 |      3 |        3 |
| pint               | `call: builtin set()`                        |     10 |      0 |        0 |
| pint               | `GeneratorExp (unknown elements)`            |      9 |      7 |        7 |
| pint               | `Lambda`                                     |      9 |      1 |        1 |
| pint               | `subscript: param[...]`                      |      9 |      5 |        4 |
| pint               | `empty dict`                                 |      8 |      0 |        0 |
| pint               | `call: builtin divmod()`                     |      8 |      2 |        0 |
| pint               | `call: builtin next()`                       |      7 |      2 |        2 |
| pint               | `call: global.method()`                      |      7 |      1 |        1 |
| pint               | `copy: other`                                |      6 |      4 |        2 |
| pint               | `conditional`                                |      6 |      6 |        3 |
| pint               | `copy: moddef`                               |      6 |      1 |        1 |
| pint               | `DictComp (unknown elements)`                |      6 |      3 |        1 |
| pint               | `call: builtin list()`                       |      6 |      3 |        2 |
| pint               | `attr: module.x`                             |      5 |      0 |        0 |
| pint               | `copy: imported`                             |      4 |      2 |        2 |
| pint               | `dict (mixed/unknown elements)`              |      4 |      1 |        1 |
| pint               | `boolop (or)`                                |      4 |      1 |        1 |
| pint               | `other constant`                             |      4 |      3 |        3 |
| pint               | `copy: self`                                 |      4 |      4 |        4 |
| pint               | `call: module class`                         |      4 |      4 |        4 |
| pint               | `call: builtin.method()`                     |      4 |      2 |        1 |
| pint               | `compare`                                    |      3 |      1 |        0 |
| pint               | `attr: builtin.x`                            |      3 |      0 |        0 |
| pint               | `empty tuple`                                |      3 |      0 |        0 |
| pint               | `call: builtin frozenset()`                  |      2 |      2 |        2 |
| pint               | `subscript: imported[...]`                   |      2 |      0 |        0 |
| pint               | `call: other.method()`                       |      2 |      2 |        2 |
| pint               | `SetComp (unknown elements)`                 |      2 |      2 |        1 |
| pint               | `call: builtin sorted()`                     |      2 |      2 |        2 |
| pint               | `call: builtin iter()`                       |      1 |      1 |        1 |
| pint               | `copy: modclass`                             |      1 |      0 |        0 |
| pint               | `call: builtin any()`                        |      1 |      1 |        1 |
| pint               | `subscript: builtin[...]`                    |      1 |      0 |        0 |
| pint               | `call: builtin object()`                     |      1 |      0 |        0 |
| pint               | `copy: global`                               |      1 |      1 |        1 |
| pint               | `call: str-literal.method()`                 |      1 |      1 |        1 |
| pint               | `call: builtin sum()`                        |      1 |      1 |        1 |
| pint               | `await: copy: local`                         |      1 |      0 |        0 |
| pint               | `call: builtin type()`                       |      1 |      0 |        0 |
| pint               | `copy: builtin`                              |      1 |      1 |        1 |
| pint               | `call: builtin max()`                        |      1 |      1 |        1 |
| altair             | `dict (mixed/unknown elements)`              |    472 |      6 |        2 |
| altair             | `other constant`                             |    203 |      0 |        0 |
| altair             | `call: self.method()`                        |    100 |     51 |       42 |
| altair             | `call: chained .method()`                    |     57 |     27 |       16 |
| altair             | `call: param.method()`                       |     46 |     42 |       32 |
| altair             | `call: local.method()`                       |     46 |     38 |       17 |
| altair             | `call: module function (annotated)`          |     23 |     18 |       12 |
| altair             | `call: module.func()`                        |     22 |     13 |       11 |
| altair             | `copy: param (annotated)`                    |     21 |     15 |        9 |
| altair             | `call: imported function`                    |     20 |     14 |       14 |
| altair             | `conditional`                                |     17 |     12 |       10 |
| altair             | `call: builtin getattr()`                    |     15 |     13 |        5 |
| altair             | `call: imported.attr()`                      |     12 |      8 |        7 |
| altair             | `attr: param.x`                              |     12 |     11 |        8 |
| altair             | `copy: local`                                |     11 |      9 |        4 |
| altair             | `attr: local.x`                              |     10 |      6 |        5 |
| altair             | `empty list`                                 |     10 |      0 |        0 |
| altair             | `subscript: other`                           |      9 |      7 |        6 |
| altair             | `GeneratorExp (unknown elements)`            |      9 |      8 |        8 |
| altair             | `subscript: local[...]`                      |      9 |      5 |        2 |
| altair             | `tuple (mixed/unknown elements)`             |      8 |      7 |        5 |
| altair             | `attr: chained`                              |      7 |      5 |        4 |
| altair             | `empty dict`                                 |      7 |      0 |        0 |
| altair             | `attr: imported.x`                           |      7 |      0 |        0 |
| altair             | `call: module function (unannotated)`        |      7 |      7 |        4 |
| altair             | `binop (unknown operands)`                   |      6 |      4 |        3 |
| altair             | `ListComp (unknown elements)`                |      6 |      4 |        3 |
| altair             | `attr: self.x`                               |      5 |      4 |        2 |
| altair             | `call: builtin set()`                        |      4 |      1 |        1 |
| altair             | `boolop (or)`                                |      4 |      4 |        2 |
| altair             | `subscript: param[...]`                      |      4 |      4 |        4 |
| altair             | `DictComp (unknown elements)`                |      4 |      4 |        1 |
| altair             | `binop (one side literal)`                   |      3 |      0 |        0 |
| altair             | `subscript: imported[...]`                   |      3 |      2 |        2 |
| altair             | `None literal`                               |      3 |      2 |        2 |
| altair             | `call: local name`                           |      3 |      2 |        1 |
| altair             | `call: builtin tuple()`                      |      2 |      1 |        1 |
| altair             | `subscript: self[...]`                       |      2 |      2 |        2 |
| altair             | `copy: self`                                 |      2 |      1 |        0 |
| altair             | `call: builtin dict()`                       |      2 |      0 |        0 |
| altair             | `call: builtin list()`                       |      2 |      0 |        0 |
| altair             | `call: imported class`                       |      2 |      0 |        0 |
| altair             | `call: builtin next()`                       |      2 |      2 |        0 |
| altair             | `call: other.method()`                       |      2 |      2 |        2 |
| altair             | `set (mixed/unknown elements)`               |      2 |      2 |        2 |
| altair             | `call: other name`                           |      2 |      1 |        1 |
| altair             | `subscript: other[...]`                      |      2 |      0 |        0 |
| altair             | `list (mixed/unknown elements)`              |      2 |      2 |        0 |
| altair             | `compare`                                    |      2 |      2 |        2 |
| altair             | `call: other callee`                         |      1 |      0 |        0 |
| altair             | `copy: modclass`                             |      1 |      0 |        0 |
| altair             | `call: builtin enumerate()`                  |      1 |      1 |        1 |
| altair             | `copy: imported`                             |      1 |      0 |        0 |
| altair             | `call: builtin compile()`                    |      1 |      1 |        1 |
| altair             | `call: global.method()`                      |      1 |      1 |        1 |
| altair             | `call: builtin zip()`                        |      1 |      1 |        1 |
| altair             | `call: builtin min()`                        |      1 |      1 |        1 |
| altair             | `call: builtin sorted()`                     |      1 |      1 |        1 |
| altair             | `call: cls.method()`                         |      1 |      1 |        1 |
| altair             | `call: modclass.method()`                    |      1 |      1 |        0 |
| altair             | `SetComp (unknown elements)`                 |      1 |      0 |        0 |
| altair             | `copy: global`                               |      1 |      0 |        0 |
| altair             | `call: builtin iter()`                       |      1 |      1 |        1 |
| altair             | `attr: modclass.x`                           |      1 |      0 |        0 |
| seaborn            | `call: self.method()`                        |    149 |    135 |      100 |
| seaborn            | `call: module.func()`                        |    140 |    120 |      115 |
| seaborn            | `call: local.method()`                       |    125 |    108 |       89 |
| seaborn            | `call: chained .method()`                    |    124 |    111 |       93 |
| seaborn            | `call: param.method()`                       |    124 |    117 |       66 |
| seaborn            | `call: imported function`                    |     89 |     73 |       58 |
| seaborn            | `tuple (mixed/unknown elements)`             |     81 |     57 |       47 |
| seaborn            | `binop (unknown operands)`                   |     79 |     70 |       57 |
| seaborn            | `subscript: other`                           |     70 |     60 |       52 |
| seaborn            | `copy: param (unannotated)`                  |     68 |     46 |       34 |
| seaborn            | `copy: local`                                |     59 |     49 |       37 |
| seaborn            | `empty list`                                 |     55 |      0 |        0 |
| seaborn            | `attr: self.x`                               |     49 |     47 |       23 |
| seaborn            | `conditional`                                |     48 |     42 |       23 |
| seaborn            | `ListComp (unknown elements)`                |     45 |     44 |       40 |
| seaborn            | `subscript: local[...]`                      |     42 |     39 |       28 |
| seaborn            | `attr: chained`                              |     41 |     33 |       30 |
| seaborn            | `call: local name`                           |     39 |     35 |       31 |
| seaborn            | `subscript: imported[...]`                   |     33 |      1 |        0 |
| seaborn            | `dict (mixed/unknown elements)`              |     32 |     30 |       12 |
| seaborn            | `empty dict`                                 |     30 |      0 |        0 |
| seaborn            | `binop (one side literal)`                   |     30 |     23 |       21 |
| seaborn            | `call: builtin getattr()`                    |     29 |     23 |        9 |
| seaborn            | `call: builtin enumerate()`                  |     29 |     25 |       21 |
| seaborn            | `call: builtin zip()`                        |     29 |     28 |       23 |
| seaborn            | `subscript: param[...]`                      |     26 |     25 |       22 |
| seaborn            | `None literal`                               |     25 |     12 |       12 |
| seaborn            | `call: param name`                           |     25 |     25 |       20 |
| seaborn            | `list (mixed/unknown elements)`              |     25 |     21 |       19 |
| seaborn            | `DictComp (unknown elements)`                |     25 |     22 |       18 |
| seaborn            | `call: builtin dict()`                       |     24 |     22 |       10 |
| seaborn            | `other constant`                             |     20 |      9 |        9 |
| seaborn            | `call: imported.attr()`                      |     19 |     14 |       13 |
| seaborn            | `call: module function (unannotated)`        |     16 |     15 |        5 |
| seaborn            | `compare`                                    |     14 |     12 |       12 |
| seaborn            | `attr: local.x`                              |     13 |     13 |       13 |
| seaborn            | `call: other name`                           |     12 |      7 |        6 |
| seaborn            | `attr: param.x`                              |     10 |      8 |        7 |
| seaborn            | `boolop (or)`                                |      9 |      9 |        7 |
| seaborn            | `call: builtin min()`                        |      8 |      8 |        4 |
| seaborn            | `boolop (and)`                               |      7 |      6 |        5 |
| seaborn            | `call: builtin tuple()`                      |      7 |      7 |        3 |
| seaborn            | `subscript: self[...]`                       |      7 |      3 |        3 |
| seaborn            | `call: builtin list()`                       |      6 |      6 |        5 |
| seaborn            | `attr: module.x`                             |      6 |      4 |        4 |
| seaborn            | `copy: param (annotated)`                    |      5 |      5 |        3 |
| seaborn            | `call: builtin max()`                        |      5 |      5 |        3 |
| seaborn            | `call: other.method()`                       |      4 |      3 |        2 |
| seaborn            | `SetComp (unknown elements)`                 |      3 |      3 |        3 |
| seaborn            | `call: other callee`                         |      3 |      2 |        1 |
| seaborn            | `call: imported class`                       |      3 |      2 |        2 |
| seaborn            | `copy: imported`                             |      3 |      3 |        3 |
| seaborn            | `call: builtin sorted()`                     |      3 |      2 |        1 |
| seaborn            | `copy: other`                                |      2 |      1 |        1 |
| seaborn            | `unaryop Invert`                             |      2 |      1 |        0 |
| seaborn            | `copy: modclass`                             |      2 |      2 |        2 |
| seaborn            | `call: capitalised`                          |      2 |      2 |        0 |
| seaborn            | `copy: moddef`                               |      2 |      1 |        1 |
| seaborn            | `copy: global`                               |      2 |      0 |        0 |
| seaborn            | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| seaborn            | `call: module class`                         |      1 |      0 |        0 |
| seaborn            | `call: builtin sum()`                        |      1 |      1 |        0 |
| seaborn            | `GeneratorExp (unknown elements)`            |      1 |      1 |        1 |
| seaborn            | `call: builtin set()`                        |      1 |      1 |        1 |
| seaborn            | `call: builtin reversed()`                   |      1 |      1 |        1 |
| seaborn            | `call: builtin slice()`                      |      1 |      1 |        1 |
| seaborn            | `copy: builtin`                              |      1 |      0 |        0 |
| seaborn            | `call: builtin str()`                        |      1 |      0 |        0 |
| seaborn            | `call: builtin map()`                        |      1 |      1 |        1 |
| seaborn            | `call: self name`                            |      1 |      1 |        1 |
| aiohttp            | `call: chained .method()`                    |    106 |     99 |       68 |
| aiohttp            | `attr: self.x`                               |     80 |     76 |       37 |
| aiohttp            | `other constant`                             |     74 |      2 |        2 |
| aiohttp            | `call: local.method()`                       |     66 |     59 |       43 |
| aiohttp            | `call: module.func()`                        |     43 |     29 |       29 |
| aiohttp            | `attr: local.x`                              |     34 |     32 |       20 |
| aiohttp            | `copy: local`                                |     27 |     26 |       21 |
| aiohttp            | `attr: chained`                              |     25 |     14 |       13 |
| aiohttp            | `conditional`                                |     25 |     23 |       13 |
| aiohttp            | `attr: param.x`                              |     25 |     23 |       11 |
| aiohttp            | `tuple (mixed/unknown elements)`             |     19 |     12 |       10 |
| aiohttp            | `subscript: other`                           |     18 |     17 |       17 |
| aiohttp            | `call: self.method()`                        |     16 |     14 |       11 |
| aiohttp            | `call: param.method()`                       |     16 |     16 |       10 |
| aiohttp            | `copy: param (annotated)`                    |     15 |     13 |        8 |
| aiohttp            | `binop (unknown operands)`                   |     15 |      9 |        7 |
| aiohttp            | `await: call: chained .method()`             |     15 |     10 |        8 |
| aiohttp            | `None literal`                               |     14 |      8 |        8 |
| aiohttp            | `await: call: local.method()`                |     14 |      6 |        3 |
| aiohttp            | `subscript: imported[...]`                   |     13 |      0 |        0 |
| aiohttp            | `empty list`                                 |     12 |      0 |        0 |
| aiohttp            | `call: imported class`                       |     12 |      8 |        7 |
| aiohttp            | `copy: imported`                             |     11 |      0 |        0 |
| aiohttp            | `await: call: self.method()`                 |     11 |     11 |        6 |
| aiohttp            | `boolop (or)`                                |     10 |      6 |        5 |
| aiohttp            | `call: global.method()`                      |      9 |      7 |        7 |
| aiohttp            | `dict (mixed/unknown elements)`              |      8 |      5 |        5 |
| aiohttp            | `attr: module.x`                             |      8 |      1 |        1 |
| aiohttp            | `call: builtin getattr()`                    |      8 |      8 |        6 |
| aiohttp            | `call: imported function`                    |      7 |      6 |        5 |
| aiohttp            | `subscript: local[...]`                      |      7 |      7 |        6 |
| aiohttp            | `boolop (and)`                               |      6 |      5 |        2 |
| aiohttp            | `attr: imported.x`                           |      4 |      0 |        0 |
| aiohttp            | `call: capitalised`                          |      4 |      4 |        4 |
| aiohttp            | `call: builtin frozenset()`                  |      4 |      0 |        0 |
| aiohttp            | `DictComp (unknown elements)`                |      4 |      0 |        0 |
| aiohttp            | `ListComp (unknown elements)`                |      3 |      3 |        3 |
| aiohttp            | `set (mixed/unknown elements)`               |      3 |      0 |        0 |
| aiohttp            | `copy: global`                               |      3 |      0 |        0 |
| aiohttp            | `call: imported.attr()`                      |      3 |      2 |        1 |
| aiohttp            | `binop (one side literal)`                   |      3 |      1 |        1 |
| aiohttp            | `empty dict`                                 |      3 |      0 |        0 |
| aiohttp            | `compare`                                    |      3 |      0 |        0 |
| aiohttp            | `call: local name`                           |      3 |      3 |        1 |
| aiohttp            | `call: other name`                           |      3 |      1 |        0 |
| aiohttp            | `subscript: builtin[...]`                    |      3 |      0 |        0 |
| aiohttp            | `copy: moddef`                               |      2 |      0 |        0 |
| aiohttp            | `copy: modclass`                             |      2 |      1 |        1 |
| aiohttp            | `call: builtin list()`                       |      2 |      2 |        0 |
| aiohttp            | `attr: global.x`                             |      2 |      1 |        1 |
| aiohttp            | `call: builtin reversed()`                   |      2 |      2 |        2 |
| aiohttp            | `SetComp (unknown elements)`                 |      2 |      2 |        2 |
| aiohttp            | `GeneratorExp (unknown elements)`            |      2 |      2 |        2 |
| aiohttp            | `subscript: param[...]`                      |      2 |      1 |        1 |
| aiohttp            | `call: builtin sorted()`                     |      2 |      2 |        2 |
| aiohttp            | `attr: builtin.x`                            |      1 |      0 |        0 |
| aiohttp            | `copy: builtin`                              |      1 |      0 |        0 |
| aiohttp            | `call: builtin bytearray()`                  |      1 |      1 |        1 |
| aiohttp            | `call: builtin.method()`                     |      1 |      0 |        0 |
| aiohttp            | `await: call: param.method()`                |      1 |      1 |        1 |
| aiohttp            | `copy: other`                                |      1 |      1 |        0 |
| aiohttp            | `JoinedStr`                                  |      1 |      1 |        1 |
| aiohttp            | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| aiohttp            | `list (mixed/unknown elements)`              |      1 |      1 |        1 |
| aiohttp            | `await: call: module.func()`                 |      1 |      0 |        0 |
| aiohttp            | `call: module function (annotated)`          |      1 |      1 |        1 |
| aiohttp            | `call: builtin open()`                       |      1 |      1 |        1 |
| aiohttp            | `call: builtin int()`                        |      1 |      1 |        1 |
| aiohttp            | `call: builtin dict()`                       |      1 |      1 |        1 |
| aiohttp            | `call: builtin set()`                        |      1 |      1 |        1 |
| aiohttp            | `unaryop Not`                                |      1 |      0 |        0 |
| aiohttp            | `call: global name`                          |      1 |      1 |        1 |
| aiohttp            | `call: builtin min()`                        |      1 |      1 |        1 |
| aiohttp            | `call: module class`                         |      1 |      1 |        1 |
| aiohttp            | `call: module function (unannotated)`        |      1 |      0 |        0 |
| aiohttp            | `call: param name`                           |      1 |      0 |        0 |
| aiohttp            | `call: builtin tuple()`                      |      1 |      0 |        0 |
| aiohttp            | `call: other callee`                         |      1 |      0 |        0 |
| aiohttp            | `copy: self`                                 |      1 |      1 |        1 |
| aiohttp            | `unaryop USub`                               |      1 |      0 |        0 |
| aiohttp            | `await: call: param name`                    |      1 |      1 |        0 |
| aiohttp            | `await: copy: local`                         |      1 |      1 |        1 |
| aiohttp            | `await: call: local name`                    |      1 |      1 |        1 |
| websockets         | `call: local.method()`                       |     31 |     24 |       24 |
| websockets         | `call: module.func()`                        |     31 |     22 |       22 |
| websockets         | `call: chained .method()`                    |     23 |     15 |       10 |
| websockets         | `tuple (mixed/unknown elements)`             |     13 |      7 |        7 |
| websockets         | `YieldFrom`                                  |     12 |     11 |       11 |
| websockets         | `attr: modclass.x`                           |     12 |      0 |        0 |
| websockets         | `attr: self.x`                               |     10 |      7 |        6 |
| websockets         | `call: self.method()`                        |      9 |      8 |        5 |
| websockets         | `copy: param (annotated)`                    |      9 |      8 |        2 |
| websockets         | `attr: local.x`                              |      9 |      9 |        7 |
| websockets         | `call: other name`                           |      8 |      8 |        4 |
| websockets         | `subscript: other`                           |      8 |      6 |        6 |
| websockets         | `copy: local`                                |      8 |      6 |        6 |
| websockets         | `await: call: chained .method()`             |      7 |      6 |        5 |
| websockets         | `attr: chained`                              |      6 |      2 |        2 |
| websockets         | `binop (unknown operands)`                   |      6 |      3 |        2 |
| websockets         | `call: param.method()`                       |      6 |      6 |        2 |
| websockets         | `copy: moddef`                               |      5 |      0 |        0 |
| websockets         | `subscript: param[...]`                      |      5 |      5 |        5 |
| websockets         | `dict (mixed/unknown elements)`              |      4 |      0 |        0 |
| websockets         | `call: builtin iter()`                       |      4 |      3 |        3 |
| websockets         | `call: builtin next()`                       |      4 |      3 |        0 |
| websockets         | `None literal`                               |      4 |      4 |        4 |
| websockets         | `subscript: other[...]`                      |      4 |      4 |        4 |
| websockets         | `other constant`                             |      4 |      0 |        0 |
| websockets         | `copy: self`                                 |      3 |      3 |        3 |
| websockets         | `attr: other.x`                              |      3 |      3 |        3 |
| websockets         | `call: capitalised`                          |      3 |      3 |        3 |
| websockets         | `call: param name`                           |      3 |      3 |        0 |
| websockets         | `subscript: local[...]`                      |      3 |      3 |        3 |
| websockets         | `call: imported class`                       |      3 |      0 |        0 |
| websockets         | `binop (one side literal)`                   |      3 |      3 |        3 |
| websockets         | `await: call: self.method()`                 |      3 |      3 |        3 |
| websockets         | `await: call: local.method()`                |      2 |      0 |        0 |
| websockets         | `call: builtin aiter()`                      |      2 |      2 |        2 |
| websockets         | `list (mixed/unknown elements)`              |      2 |      2 |        2 |
| websockets         | `ListComp (unknown elements)`                |      2 |      1 |        1 |
| websockets         | `set (mixed/unknown elements)`               |      2 |      0 |        0 |
| websockets         | `call: builtin reversed()`                   |      2 |      1 |        1 |
| websockets         | `empty list`                                 |      2 |      0 |        0 |
| websockets         | `copy: modclass`                             |      2 |      0 |        0 |
| websockets         | `await: call: param name`                    |      2 |      2 |        2 |
| websockets         | `await: call: other name`                    |      1 |      0 |        0 |
| websockets         | `call: builtin.method()`                     |      1 |      0 |        0 |
| websockets         | `await: call: imported function`             |      1 |      0 |        0 |
| websockets         | `empty dict`                                 |      1 |      0 |        0 |
| websockets         | `conditional`                                |      1 |      0 |        0 |
| websockets         | `call: builtin int()`                        |      1 |      0 |        0 |
| websockets         | `call: builtin __import__()`                 |      1 |      1 |        1 |
| websockets         | `call: builtin dict()`                       |      1 |      1 |        1 |
| websockets         | `call: local name`                           |      1 |      0 |        0 |
| websockets         | `await: call: imported.attr()`               |      1 |      1 |        1 |
| websockets         | `await: copy: local`                         |      1 |      1 |        0 |
| websockets         | `binop: literal % formatting`                |      1 |      1 |        1 |
| websockets         | `call: builtin memoryview()`                 |      1 |      1 |        1 |
| websockets         | `await: call: param.method()`                |      1 |      1 |        1 |
| websockets         | `compare`                                    |      1 |      1 |        1 |
| zarr               | `call: imported function`                    |     92 |     80 |       49 |
| zarr               | `call: chained .method()`                    |     90 |     71 |       57 |
| zarr               | `call: param.method()`                       |     64 |     39 |       27 |
| zarr               | `call: module.func()`                        |     58 |     44 |       44 |
| zarr               | `binop (unknown operands)`                   |     57 |     33 |       28 |
| zarr               | `call: param name`                           |     53 |     52 |       38 |
| zarr               | `call: local.method()`                       |     52 |     46 |       28 |
| zarr               | `copy: local`                                |     50 |     36 |       26 |
| zarr               | `call: self.method()`                        |     42 |     28 |       14 |
| zarr               | `attr: chained`                              |     41 |     18 |       17 |
| zarr               | `subscript: param[...]`                      |     31 |     30 |       27 |
| zarr               | `call: builtin tuple()`                      |     31 |     25 |       23 |
| zarr               | `subscript: other`                           |     29 |     23 |       22 |
| zarr               | `subscript: local[...]`                      |     25 |     20 |       11 |
| zarr               | `call: module function (annotated)`          |     23 |     18 |        6 |
| zarr               | `other constant`                             |     22 |      8 |        8 |
| zarr               | `await: call: chained .method()`             |     22 |     14 |        2 |
| zarr               | `ListComp (unknown elements)`                |     20 |      8 |        7 |
| zarr               | `copy: param (annotated)`                    |     20 |     14 |        9 |
| zarr               | `conditional`                                |     17 |      9 |        7 |
| zarr               | `attr: param.x`                              |     14 |     11 |        7 |
| zarr               | `await: call: module.func()`                 |     14 |      0 |        0 |
| zarr               | `call: builtin sorted()`                     |     13 |     10 |       10 |
| zarr               | `empty list`                                 |     12 |      0 |        0 |
| zarr               | `await: call: param.method()`                |     12 |     12 |       11 |
| zarr               | `call: imported.attr()`                      |     11 |     10 |        9 |
| zarr               | `await: call: imported function`             |     11 |      9 |        8 |
| zarr               | `dict (mixed/unknown elements)`              |     11 |      6 |        4 |
| zarr               | `call: builtin list()`                       |     10 |      7 |        7 |
| zarr               | `call: builtin zip()`                        |     10 |      9 |        5 |
| zarr               | `None literal`                               |      9 |      8 |        8 |
| zarr               | `tuple (mixed/unknown elements)`             |      9 |      9 |        7 |
| zarr               | `attr: self.x`                               |      8 |      8 |        2 |
| zarr               | `binop (one side literal)`                   |      8 |      4 |        4 |
| zarr               | `empty dict`                                 |      6 |      0 |        0 |
| zarr               | `boolop (or)`                                |      6 |      5 |        3 |
| zarr               | `call: builtin enumerate()`                  |      6 |      5 |        4 |
| zarr               | `compare`                                    |      6 |      6 |        6 |
| zarr               | `list (mixed/unknown elements)`              |      6 |      3 |        3 |
| zarr               | `JoinedStr`                                  |      6 |      2 |        2 |
| zarr               | `attr: local.x`                              |      5 |      4 |        4 |
| zarr               | `call: global.method()`                      |      5 |      5 |        5 |
| zarr               | `await: copy: local`                         |      5 |      5 |        2 |
| zarr               | `await: call: local.method()`                |      5 |      2 |        1 |
| zarr               | `SetComp (unknown elements)`                 |      4 |      4 |        2 |
| zarr               | `call: other.method()`                       |      4 |      2 |        0 |
| zarr               | `call: builtin dict()`                       |      4 |      4 |        2 |
| zarr               | `call: builtin slice()`                      |      4 |      4 |        4 |
| zarr               | `call: builtin getattr()`                    |      3 |      3 |        1 |
| zarr               | `call: builtin max()`                        |      3 |      3 |        3 |
| zarr               | `await: call: imported.attr()`               |      3 |      2 |        2 |
| zarr               | `DictComp (unknown elements)`                |      3 |      1 |        1 |
| zarr               | `call: cls name`                             |      3 |      3 |        3 |
| zarr               | `subscript: self[...]`                       |      3 |      3 |        2 |
| zarr               | `call: builtin sum()`                        |      3 |      2 |        2 |
| zarr               | `copy: self`                                 |      3 |      2 |        0 |
| zarr               | `GeneratorExp (unknown elements)`            |      3 |      1 |        1 |
| zarr               | `await: call: self.method()`                 |      3 |      3 |        3 |
| zarr               | `call: other name`                           |      2 |      1 |        1 |
| zarr               | `boolop (and)`                               |      2 |      2 |        2 |
| zarr               | `call: builtin set()`                        |      2 |      2 |        2 |
| zarr               | `call: builtin.method()`                     |      2 |      2 |        2 |
| zarr               | `call: builtin next()`                       |      2 |      0 |        0 |
| zarr               | `call: imported class`                       |      2 |      0 |        0 |
| zarr               | `call: cls.method()`                         |      2 |      2 |        2 |
| zarr               | `copy: global`                               |      2 |      0 |        0 |
| zarr               | `subscript: imported[...]`                   |      2 |      0 |        0 |
| zarr               | `copy: builtin`                              |      1 |      0 |        0 |
| zarr               | `call: builtin object()`                     |      1 |      1 |        1 |
| zarr               | `await: call: modclass.method()`             |      1 |      1 |        1 |
| zarr               | `call: modclass.method()`                    |      1 |      1 |        1 |
| zarr               | `call: module class`                         |      1 |      1 |        1 |
| zarr               | `copy: imported`                             |      1 |      1 |        1 |
| zarr               | `attr: modclass.x`                           |      1 |      1 |        1 |
| zarr               | `attr: cls.x`                                |      1 |      1 |        1 |
| zarr               | `await: call: cls.method()`                  |      1 |      0 |        0 |
| zarr               | `await: call: module function (annotated)`   |      1 |      1 |        1 |
| zarr               | `attr: module.x`                             |      1 |      0 |        0 |
| zarr               | `await: copy: param (annotated)`             |      1 |      0 |        0 |
| zarr               | `call: builtin min()`                        |      1 |      1 |        1 |
| joblib             | `call: imported function`                    |    121 |     19 |       16 |
| joblib             | `call: local.method()`                       |    110 |      8 |        6 |
| joblib             | `call: imported.attr()`                      |    109 |      7 |        4 |
| joblib             | `call: chained .method()`                    |     93 |     38 |       33 |
| joblib             | `attr: chained`                              |     79 |      4 |        3 |
| joblib             | `call: module.func()`                        |     77 |     16 |       16 |
| joblib             | `call: module function (unannotated)`        |     56 |     23 |       13 |
| joblib             | `call: other callee`                         |     41 |      0 |        0 |
| joblib             | `call: param.method()`                       |     39 |     14 |       10 |
| joblib             | `call: self.method()`                        |     33 |     27 |       24 |
| joblib             | `copy: param (unannotated)`                  |     32 |      9 |        7 |
| joblib             | `copy: local`                                |     32 |      8 |        5 |
| joblib             | `None literal`                               |     31 |     11 |       11 |
| joblib             | `binop (unknown operands)`                   |     30 |     13 |       13 |
| joblib             | `call: other name`                           |     26 |      1 |        0 |
| joblib             | `call: local name`                           |     25 |      2 |        0 |
| joblib             | `attr: self.x`                               |     24 |     17 |       13 |
| joblib             | `tuple (mixed/unknown elements)`             |     24 |      8 |        8 |
| joblib             | `list (mixed/unknown elements)`              |     24 |      4 |        4 |
| joblib             | `empty list`                                 |     22 |      0 |        0 |
| joblib             | `ListComp (unknown elements)`                |     19 |      3 |        3 |
| joblib             | `attr: param.x`                              |     18 |      9 |        8 |
| joblib             | `other constant`                             |     18 |      2 |        2 |
| joblib             | `call: builtin list()`                       |     18 |      3 |        3 |
| joblib             | `subscript: other`                           |     17 |      7 |        6 |
| joblib             | `attr: local.x`                              |     17 |      3 |        3 |
| joblib             | `call: builtin getattr()`                    |     16 |      9 |        5 |
| joblib             | `dict (mixed/unknown elements)`              |     16 |      3 |        2 |
| joblib             | `call: param name`                           |     16 |      0 |        0 |
| joblib             | `call: builtin zip()`                        |     15 |      1 |        1 |
| joblib             | `call: imported class`                       |     15 |      1 |        1 |
| joblib             | `call: builtin dict()`                       |     14 |      7 |        6 |
| joblib             | `empty dict`                                 |     13 |      0 |        0 |
| joblib             | `attr: module.x`                             |     13 |      0 |        0 |
| joblib             | `subscript: local[...]`                      |     13 |      2 |        2 |
| joblib             | `call: builtin set()`                        |      7 |      0 |        0 |
| joblib             | `binop (one side literal)`                   |      7 |      2 |        2 |
| joblib             | `compare`                                    |      7 |      1 |        1 |
| joblib             | `boolop (or)`                                |      6 |      4 |        4 |
| joblib             | `call: builtin max()`                        |      6 |      4 |        4 |
| joblib             | `conditional`                                |      6 |      4 |        3 |
| joblib             | `copy: global`                               |      6 |      0 |        0 |
| joblib             | `call: global.method()`                      |      6 |      2 |        2 |
| joblib             | `call: builtin open()`                       |      6 |      0 |        0 |
| joblib             | `call: other.method()`                       |      5 |      3 |        3 |
| joblib             | `copy: imported`                             |      5 |      1 |        1 |
| joblib             | `attr: global.x`                             |      5 |      0 |        0 |
| joblib             | `call: builtin staticmethod()`               |      4 |      0 |        0 |
| joblib             | `call: builtin enumerate()`                  |      4 |      2 |        2 |
| joblib             | `DictComp (unknown elements)`                |      4 |      1 |        1 |
| joblib             | `subscript: param[...]`                      |      4 |      2 |        0 |
| joblib             | `call: builtin iter()`                       |      4 |      1 |        1 |
| joblib             | `await: call: local.method()`                |      4 |      0 |        0 |
| joblib             | `call: builtin sum()`                        |      3 |      2 |        2 |
| joblib             | `call: builtin min()`                        |      3 |      3 |        3 |
| joblib             | `copy: builtin`                              |      3 |      0 |        0 |
| joblib             | `boolop (and)`                               |      3 |      2 |        2 |
| joblib             | `subscript: global[...]`                     |      3 |      2 |        1 |
| joblib             | `copy: other`                                |      3 |      0 |        0 |
| joblib             | `call: builtin eval()`                       |      3 |      0 |        0 |
| joblib             | `await: call: other name`                    |      3 |      0 |        0 |
| joblib             | `await: call: other.method()`                |      2 |      0 |        0 |
| joblib             | `call: builtin type()`                       |      2 |      0 |        0 |
| joblib             | `call: str-literal.method()`                 |      2 |      1 |        1 |
| joblib             | `call: builtin vars()`                       |      2 |      0 |        0 |
| joblib             | `SetComp (unknown elements)`                 |      1 |      0 |        0 |
| joblib             | `call: builtin abs()`                        |      1 |      1 |        0 |
| joblib             | `call: builtin RuntimeError()`               |      1 |      0 |        0 |
| joblib             | `call: builtin tuple()`                      |      1 |      1 |        1 |
| joblib             | `copy: modclass`                             |      1 |      0 |        0 |
| joblib             | `call: modclass.method()`                    |      1 |      1 |        1 |
| joblib             | `call: module class`                         |      1 |      1 |        1 |
| joblib             | `await: call: self.method()`                 |      1 |      0 |        0 |
| joblib             | `call: builtin.method()`                     |      1 |      1 |        1 |
| joblib             | `subscript: imported[...]`                   |      1 |      1 |        1 |
| joblib             | `call: builtin next()`                       |      1 |      1 |        1 |
| joblib             | `Lambda`                                     |      1 |      0 |        0 |
| joblib             | `call: moddef.method()`                      |      1 |      0 |        0 |
| joblib             | `await: call: param name`                    |      1 |      0 |        0 |
| joblib             | `await: call: local name`                    |      1 |      0 |        0 |
| joblib             | `empty tuple`                                |      1 |      0 |        0 |
| joblib             | `attr: imported.x`                           |      1 |      0 |        0 |
| joblib             | `call: builtin sorted()`                     |      1 |      0 |        0 |
| joblib             | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| networkx           | `call: module.func()`                        |  4,476 |    581 |      501 |
| networkx           | `call: local.method()`                       |    810 |    402 |      305 |
| networkx           | `call: imported function`                    |    725 |    200 |      141 |
| networkx           | `copy: local`                                |    667 |    468 |      334 |
| networkx           | `call: param.method()`                       |    609 |    484 |      370 |
| networkx           | `copy: param (unannotated)`                  |    503 |    371 |      206 |
| networkx           | `call: module function (unannotated)`        |    474 |    346 |      257 |
| networkx           | `call: chained .method()`                    |    468 |    217 |      159 |
| networkx           | `binop (unknown operands)`                   |    383 |    317 |      277 |
| networkx           | `call: builtin list()`                       |    373 |    150 |      103 |
| networkx           | `call: self.method()`                        |    334 |    113 |       58 |
| networkx           | `subscript: other`                           |    326 |    213 |      146 |
| networkx           | `subscript: local[...]`                      |    307 |    263 |      192 |
| networkx           | `attr: self.x`                               |    296 |     75 |       32 |
| networkx           | `list (mixed/unknown elements)`              |    276 |     97 |       59 |
| networkx           | `call: builtin set()`                        |    274 |    121 |       82 |
| networkx           | `ListComp (unknown elements)`                |    267 |    159 |      111 |
| networkx           | `call: builtin sorted()`                     |    256 |     42 |       36 |
| networkx           | `DictComp (unknown elements)`                |    219 |    118 |       55 |
| networkx           | `empty dict`                                 |    219 |      0 |        0 |
| networkx           | `tuple (mixed/unknown elements)`             |    218 |    126 |       84 |
| networkx           | `empty list`                                 |    198 |      0 |        0 |
| networkx           | `call: global.method()`                      |    170 |      0 |        0 |
| networkx           | `dict (mixed/unknown elements)`              |    169 |     74 |       46 |
| networkx           | `call: local name`                           |    168 |     73 |       63 |
| networkx           | `call: imported.attr()`                      |    157 |      4 |        4 |
| networkx           | `call: param name`                           |    157 |     21 |       15 |
| networkx           | `call: builtin zip()`                        |    144 |     72 |       51 |
| networkx           | `subscript: param[...]`                      |    142 |    113 |       83 |
| networkx           | `attr: local.x`                              |    139 |     56 |       51 |
| networkx           | `call: builtin dict()`                       |    137 |     71 |       38 |
| networkx           | `call: builtin sum()`                        |    126 |     80 |       72 |
| networkx           | `conditional`                                |    126 |     85 |       48 |
| networkx           | `call: other name`                           |    123 |     93 |       55 |
| networkx           | `GeneratorExp (unknown elements)`            |    106 |     74 |       73 |
| networkx           | `attr: param.x`                              |    105 |     91 |       70 |
| networkx           | `binop (one side literal)`                   |    102 |     79 |       78 |
| networkx           | `SetComp (unknown elements)`                 |     95 |     51 |       33 |
| networkx           | `attr: module.x`                             |     91 |     30 |       30 |
| networkx           | `call: builtin enumerate()`                  |     87 |     71 |       47 |
| networkx           | `call: builtin next()`                       |     79 |     67 |       45 |
| networkx           | `attr: chained`                              |     79 |     30 |       26 |
| networkx           | `other constant`                             |     69 |     53 |       53 |
| networkx           | `call: builtin.method()`                     |     62 |     41 |       28 |
| networkx           | `call: builtin min()`                        |     60 |     56 |       43 |
| networkx           | `None literal`                               |     60 |     50 |       50 |
| networkx           | `copy: global`                               |     58 |      0 |        0 |
| networkx           | `call: capitalised`                          |     53 |      6 |        5 |
| networkx           | `call: builtin max()`                        |     47 |     43 |       38 |
| networkx           | `set (mixed/unknown elements)`               |     45 |     29 |       12 |
| networkx           | `copy: other`                                |     32 |     19 |        9 |
| networkx           | `call: other.method()`                       |     32 |     25 |       18 |
| networkx           | `subscript: other[...]`                      |     28 |     28 |        7 |
| networkx           | `call: other callee`                         |     28 |     13 |       10 |
| networkx           | `call: builtin iter()`                       |     27 |     17 |       17 |
| networkx           | `copy: moddef`                               |     25 |     14 |       14 |
| networkx           | `compare`                                    |     22 |     11 |       11 |
| networkx           | `copy: modclass`                             |     21 |      0 |        0 |
| networkx           | `call: imported class`                       |     17 |     12 |       11 |
| networkx           | `call: builtin staticmethod()`               |     16 |      0 |        0 |
| networkx           | `boolop (or)`                                |     14 |     10 |        8 |
| networkx           | `call: builtin object()`                     |     13 |      1 |        1 |
| networkx           | `subscript: global[...]`                     |     11 |      6 |        6 |
| networkx           | `copy: imported`                             |     11 |      2 |        2 |
| networkx           | `call: global name`                          |     10 |      3 |        3 |
| networkx           | `call: builtin tuple()`                      |      9 |      8 |        7 |
| networkx           | `copy: builtin`                              |      9 |      0 |        0 |
| networkx           | `call: builtin frozenset()`                  |      8 |      5 |        3 |
| networkx           | `attr: imported.x`                           |      6 |      0 |        0 |
| networkx           | `boolop (and)`                               |      6 |      1 |        1 |
| networkx           | `call: module class`                         |      6 |      1 |        1 |
| networkx           | `call: modclass.method()`                    |      5 |      3 |        3 |
| networkx           | `call: builtin round()`                      |      4 |      3 |        3 |
| networkx           | `call: builtin map()`                        |      4 |      4 |        2 |
| networkx           | `call: builtin reversed()`                   |      3 |      3 |        3 |
| networkx           | `copy: self`                                 |      3 |      3 |        3 |
| networkx           | `call: builtin len()`                        |      2 |      1 |        1 |
| networkx           | `unaryop USub`                               |      2 |      2 |        2 |
| networkx           | `call: cls.method()`                         |      2 |      2 |        2 |
| networkx           | `call: builtin float()`                      |      1 |      1 |        1 |
| networkx           | `attr: global.x`                             |      1 |      0 |        0 |
| networkx           | `call: builtin range()`                      |      1 |      1 |        1 |
| networkx           | `subscript: self[...]`                       |      1 |      1 |        1 |
| networkx           | `call: builtin abs()`                        |      1 |      0 |        0 |
| networkx           | `empty tuple`                                |      1 |      0 |        0 |
| networkx           | `attr: cls.x`                                |      1 |      0 |        0 |
| networkx           | `call: builtin type()`                       |      1 |      1 |        0 |
| networkx           | `copy: cls`                                  |      1 |      1 |        0 |
| networkx           | `call: builtin compile()`                    |      1 |      1 |        1 |
| networkx           | `call: builtin getattr()`                    |      1 |      0 |        0 |
| networkx           | `call: cls name`                             |      1 |      0 |        0 |
| nibabel            | `call: module.func()`                        |    551 |    130 |      119 |
| nibabel            | `call: chained .method()`                    |    411 |    125 |      114 |
| nibabel            | `call: imported function`                    |    366 |     48 |       36 |
| nibabel            | `tuple (mixed/unknown elements)`             |    337 |     67 |       33 |
| nibabel            | `call: local.method()`                       |    323 |     65 |       60 |
| nibabel            | `call: self.method()`                        |    257 |     81 |       54 |
| nibabel            | `subscript: other`                           |    217 |    113 |      105 |
| nibabel            | `call: imported.attr()`                      |    216 |      7 |        6 |
| nibabel            | `binop (unknown operands)`                   |    208 |     88 |       69 |
| nibabel            | `attr: self.x`                               |    177 |     72 |       60 |
| nibabel            | `call: module function (unannotated)`        |    165 |     70 |       46 |
| nibabel            | `copy: local`                                |    123 |     36 |       24 |
| nibabel            | `attr: local.x`                              |    114 |     23 |       18 |
| nibabel            | `call: local name`                           |    105 |      4 |        2 |
| nibabel            | `copy: imported`                             |    105 |      3 |        1 |
| nibabel            | `call: param.method()`                       |    103 |     74 |       62 |
| nibabel            | `subscript: local[...]`                      |     95 |     52 |       45 |
| nibabel            | `list (mixed/unknown elements)`              |     84 |      4 |        4 |
| nibabel            | `attr: chained`                              |     83 |     15 |       10 |
| nibabel            | `attr: param.x`                              |     76 |     47 |       39 |
| nibabel            | `copy: global`                               |     76 |      2 |        2 |
| nibabel            | `call: builtin zip()`                        |     67 |     19 |       19 |
| nibabel            | `ListComp (unknown elements)`                |     62 |     18 |       15 |
| nibabel            | `copy: param (unannotated)`                  |     58 |     47 |       28 |
| nibabel            | `subscript: param[...]`                      |     57 |     42 |       30 |
| nibabel            | `binop (one side literal)`                   |     56 |     27 |       24 |
| nibabel            | `other constant`                             |     56 |      9 |        9 |
| nibabel            | `call: param name`                           |     55 |      4 |        0 |
| nibabel            | `empty list`                                 |     53 |      0 |        0 |
| nibabel            | `empty dict`                                 |     52 |      0 |        0 |
| nibabel            | `call: builtin enumerate()`                  |     46 |     30 |       20 |
| nibabel            | `conditional`                                |     44 |     25 |       18 |
| nibabel            | `call: global name`                          |     38 |      0 |        0 |
| nibabel            | `dict (mixed/unknown elements)`              |     36 |      3 |        2 |
| nibabel            | `call: capitalised`                          |     32 |      0 |        0 |
| nibabel            | `None literal`                               |     31 |     12 |       12 |
| nibabel            | `compare`                                    |     30 |     14 |       14 |
| nibabel            | `call: imported class`                       |     30 |      5 |        5 |
| nibabel            | `call: builtin dict()`                       |     27 |      5 |        4 |
| nibabel            | `attr: module.x`                             |     26 |      3 |        3 |
| nibabel            | `call: global.method()`                      |     25 |      3 |        1 |
| nibabel            | `copy: modclass`                             |     24 |      0 |        0 |
| nibabel            | `call: builtin list()`                       |     22 |      3 |        3 |
| nibabel            | `attr: imported.x`                           |     20 |      0 |        0 |
| nibabel            | `call: builtin getattr()`                    |     18 |      8 |        4 |
| nibabel            | `attr: modclass.x`                           |     17 |      0 |        0 |
| nibabel            | `call: other.method()`                       |     16 |      5 |        5 |
| nibabel            | `call: builtin tuple()`                      |     16 |     10 |       10 |
| nibabel            | `subscript: imported[...]`                   |     16 |      1 |        0 |
| nibabel            | `subscript: global[...]`                     |     14 |      3 |        2 |
| nibabel            | `copy: other`                                |     12 |      2 |        1 |
| nibabel            | `copy: self`                                 |     11 |     11 |        5 |
| nibabel            | `copy: param (annotated)`                    |     11 |     10 |        7 |
| nibabel            | `call: builtin next()`                       |     10 |      8 |        8 |
| nibabel            | `call: other name`                           |      8 |      0 |        0 |
| nibabel            | `call: builtin sorted()`                     |      8 |      4 |        4 |
| nibabel            | `call: other callee`                         |      8 |      3 |        2 |
| nibabel            | `GeneratorExp (unknown elements)`            |      8 |      5 |        5 |
| nibabel            | `attr: other.x`                              |      6 |      2 |        1 |
| nibabel            | `boolop (and)`                               |      6 |      3 |        2 |
| nibabel            | `boolop (or)`                                |      6 |      3 |        2 |
| nibabel            | `call: cls.method()`                         |      6 |      6 |        4 |
| nibabel            | `call: builtin __import__()`                 |      6 |      3 |        3 |
| nibabel            | `call: builtin set()`                        |      6 |      1 |        1 |
| nibabel            | `call: builtin open()`                       |      6 |      0 |        0 |
| nibabel            | `call: builtin.method()`                     |      5 |      1 |        1 |
| nibabel            | `DictComp (unknown elements)`                |      5 |      3 |        3 |
| nibabel            | `SetComp (unknown elements)`                 |      4 |      1 |        1 |
| nibabel            | `call: builtin min()`                        |      4 |      1 |        1 |
| nibabel            | `call: modclass.method()`                    |      4 |      4 |        4 |
| nibabel            | `empty tuple`                                |      4 |      0 |        0 |
| nibabel            | `call: builtin max()`                        |      3 |      1 |        1 |
| nibabel            | `call: builtin sum()`                        |      3 |      2 |        2 |
| nibabel            | `call: str-literal.method()`                 |      3 |      3 |        3 |
| nibabel            | `call: builtin type()`                       |      3 |      0 |        0 |
| nibabel            | `call: builtin slice()`                      |      3 |      1 |        1 |
| nibabel            | `call: builtin staticmethod()`               |      3 |      0 |        0 |
| nibabel            | `call: module function (annotated)`          |      3 |      3 |        2 |
| nibabel            | `call: module class`                         |      2 |      1 |        1 |
| nibabel            | `call: builtin property()`                   |      2 |      0 |        0 |
| nibabel            | `copy: builtin`                              |      2 |      0 |        0 |
| nibabel            | `unaryop Invert`                             |      2 |      1 |        1 |
| nibabel            | `call: builtin iter()`                       |      2 |      1 |        1 |
| nibabel            | `copy: moddef`                               |      2 |      2 |        2 |
| nibabel            | `subscript: other[...]`                      |      2 |      2 |        2 |
| nibabel            | `attr: global.x`                             |      2 |      0 |        0 |
| nibabel            | `call: builtin abs()`                        |      1 |      1 |        0 |
| nibabel            | `call: builtin range()`                      |      1 |      1 |        1 |
| nibabel            | `call: builtin len()`                        |      1 |      0 |        0 |
| nibabel            | `unaryop USub`                               |      1 |      0 |        0 |
| nibabel            | `set (mixed/unknown elements)`               |      1 |      0 |        0 |
| nibabel            | `Lambda`                                     |      1 |      0 |        0 |
| nibabel            | `call: builtin bytearray()`                  |      1 |      1 |        1 |
| narwhals           | `call: chained .method()`                    |    214 |    170 |      149 |
| narwhals           | `call: imported function`                    |    204 |    128 |       90 |
| narwhals           | `attr: chained`                              |    135 |    113 |       90 |
| narwhals           | `conditional`                                |    133 |    117 |       73 |
| narwhals           | `call: module.func()`                        |    129 |    113 |      108 |
| narwhals           | `call: local.method()`                       |     98 |     87 |       69 |
| narwhals           | `attr: self.x`                               |     93 |     85 |       77 |
| narwhals           | `call: self.method()`                        |     84 |     71 |       62 |
| narwhals           | `call: param.method()`                       |     80 |     52 |       31 |
| narwhals           | `ListComp (unknown elements)`                |     65 |     49 |       37 |
| narwhals           | `tuple (mixed/unknown elements)`             |     59 |     50 |       32 |
| narwhals           | `call: module function (annotated)`          |     55 |     34 |       32 |
| narwhals           | `attr: param.x`                              |     45 |     40 |       30 |
| narwhals           | `binop (unknown operands)`                   |     38 |     31 |       31 |
| narwhals           | `call: imported class`                       |     38 |      7 |        7 |
| narwhals           | `GeneratorExp (unknown elements)`            |     28 |     22 |       22 |
| narwhals           | `attr: local.x`                              |     27 |     23 |       22 |
| narwhals           | `attr: imported.x`                           |     24 |      1 |        1 |
| narwhals           | `call: builtin list()`                       |     19 |     15 |       15 |
| narwhals           | `call: other.method()`                       |     19 |     17 |       10 |
| narwhals           | `copy: param (annotated)`                    |     18 |     18 |       10 |
| narwhals           | `copy: local`                                |     18 |     16 |       13 |
| narwhals           | `subscript: other`                           |     17 |     15 |       13 |
| narwhals           | `call: builtin tuple()`                      |     16 |     16 |       12 |
| narwhals           | `DictComp (unknown elements)`                |     15 |     13 |        4 |
| narwhals           | `subscript: local[...]`                      |     12 |     12 |        9 |
| narwhals           | `dict (mixed/unknown elements)`              |     12 |      6 |        6 |
| narwhals           | `binop (one side literal)`                   |     12 |     11 |       11 |
| narwhals           | `attr: other.x`                              |     12 |     12 |       12 |
| narwhals           | `call: builtin zip()`                        |     11 |     10 |        7 |
| narwhals           | `call: local name`                           |     11 |     11 |       10 |
| narwhals           | `call: other name`                           |     10 |     10 |        5 |
| narwhals           | `call: builtin len()`                        |     10 |      9 |        9 |
| narwhals           | `boolop (or)`                                |      9 |      5 |        4 |
| narwhals           | `empty list`                                 |      9 |      0 |        0 |
| narwhals           | `call: builtin getattr()`                    |      9 |      5 |        4 |
| narwhals           | `call: imported.attr()`                      |      8 |      4 |        4 |
| narwhals           | `compare`                                    |      7 |      6 |        5 |
| narwhals           | `call: builtin next()`                       |      6 |      5 |        3 |
| narwhals           | `attr: module.x`                             |      6 |      1 |        1 |
| narwhals           | `other constant`                             |      6 |      4 |        4 |
| narwhals           | `call: global.method()`                      |      6 |      6 |        3 |
| narwhals           | `unaryop Invert`                             |      5 |      4 |        4 |
| narwhals           | `subscript: param[...]`                      |      5 |      4 |        3 |
| narwhals           | `call: other callee`                         |      5 |      4 |        3 |
| narwhals           | `call: builtin enumerate()`                  |      4 |      4 |        3 |
| narwhals           | `boolop (and)`                               |      4 |      4 |        4 |
| narwhals           | `list (mixed/unknown elements)`              |      4 |      3 |        2 |
| narwhals           | `call: param name`                           |      4 |      4 |        2 |
| narwhals           | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| narwhals           | `call: builtin dict()`                       |      3 |      1 |        0 |
| narwhals           | `call: capitalised`                          |      3 |      3 |        2 |
| narwhals           | `copy: other`                                |      2 |      0 |        0 |
| narwhals           | `empty tuple`                                |      2 |      0 |        0 |
| narwhals           | `call: builtin max()`                        |      2 |      2 |        2 |
| narwhals           | `call: builtin type()`                       |      2 |      1 |        1 |
| narwhals           | `call: builtin iter()`                       |      2 |      1 |        1 |
| narwhals           | `subscript: other[...]`                      |      2 |      1 |        1 |
| narwhals           | `attr: modclass.x`                           |      2 |      1 |        1 |
| narwhals           | `set (mixed/unknown elements)`               |      2 |      0 |        0 |
| narwhals           | `copy: imported`                             |      2 |      0 |        0 |
| narwhals           | `call: builtin sorted()`                     |      2 |      2 |        2 |
| narwhals           | `call: builtin all()`                        |      1 |      1 |        1 |
| narwhals           | `call: global name`                          |      1 |      1 |        0 |
| narwhals           | `copy: self`                                 |      1 |      1 |        0 |
| narwhals           | `call: builtin sum()`                        |      1 |      1 |        1 |
| narwhals           | `attr: cls.x`                                |      1 |      1 |        1 |
| narwhals           | `call: builtin slice()`                      |      1 |      1 |        1 |
| narwhals           | `call: modclass.method()`                    |      1 |      1 |        1 |
| narwhals           | `call: builtin str()`                        |      1 |      1 |        1 |
| narwhals           | `call: builtin object()`                     |      1 |      1 |        1 |
| narwhals           | `subscript: imported[...]`                   |      1 |      1 |        1 |
| narwhals           | `copy: global`                               |      1 |      0 |        0 |
| narwhals           | `call: builtin.method()`                     |      1 |      1 |        1 |
| xarray             | `call: module.func()`                        |  1,405 |    106 |      102 |
| xarray             | `call: chained .method()`                    |  1,404 |    172 |      112 |
| xarray             | `call: imported function`                    |    939 |    175 |      121 |
| xarray             | `call: local.method()`                       |    923 |    104 |       73 |
| xarray             | `binop (unknown operands)`                   |    737 |     95 |       79 |
| xarray             | `call: self.method()`                        |    449 |    105 |       93 |
| xarray             | `call: module function (unannotated)`        |    393 |     65 |       44 |
| xarray             | `call: param.method()`                       |    333 |    153 |      107 |
| xarray             | `subscript: local[...]`                      |    298 |     30 |       23 |
| xarray             | `subscript: other`                           |    250 |     41 |       34 |
| xarray             | `attr: chained`                              |    236 |     44 |       34 |
| xarray             | `dict (mixed/unknown elements)`              |    204 |     10 |        8 |
| xarray             | `ListComp (unknown elements)`                |    203 |     73 |       59 |
| xarray             | `call: imported.attr()`                      |    179 |     51 |       32 |
| xarray             | `call: param name`                           |    170 |      6 |        4 |
| xarray             | `list (mixed/unknown elements)`              |    162 |     20 |       18 |
| xarray             | `conditional`                                |    149 |     56 |       38 |
| xarray             | `DictComp (unknown elements)`                |    148 |     56 |       41 |
| xarray             | `copy: local`                                |    148 |     55 |       42 |
| xarray             | `call: builtin zip()`                        |    144 |     47 |       34 |
| xarray             | `attr: local.x`                              |    131 |     43 |       33 |
| xarray             | `empty dict`                                 |    120 |      0 |        0 |
| xarray             | `copy: param (unannotated)`                  |    116 |     40 |       28 |
| xarray             | `call: local name`                           |    116 |      6 |        3 |
| xarray             | `binop (one side literal)`                   |    108 |      9 |        9 |
| xarray             | `call: imported class`                       |    101 |      5 |        4 |
| xarray             | `attr: self.x`                               |     86 |     40 |       32 |
| xarray             | `call: module function (annotated)`          |     84 |     27 |       18 |
| xarray             | `call: builtin tuple()`                      |     83 |     43 |       36 |
| xarray             | `attr: param.x`                              |     82 |     32 |       24 |
| xarray             | `call: builtin getattr()`                    |     80 |     29 |       16 |
| xarray             | `empty list`                                 |     80 |      0 |        0 |
| xarray             | `call: other name`                           |     80 |     10 |       10 |
| xarray             | `subscript: param[...]`                      |     76 |     28 |       12 |
| xarray             | `call: builtin dict()`                       |     73 |     13 |        5 |
| xarray             | `call: other callee`                         |     65 |      9 |        3 |
| xarray             | `tuple (mixed/unknown elements)`             |     62 |      9 |        7 |
| xarray             | `call: builtin set()`                        |     55 |     20 |       15 |
| xarray             | `compare`                                    |     53 |     19 |       17 |
| xarray             | `other constant`                             |     52 |      1 |        1 |
| xarray             | `copy: param (annotated)`                    |     44 |     26 |       18 |
| xarray             | `call: global.method()`                      |     41 |      1 |        1 |
| xarray             | `call: builtin list()`                       |     40 |     18 |       15 |
| xarray             | `call: builtin enumerate()`                  |     40 |     17 |        9 |
| xarray             | `copy: imported`                             |     39 |      0 |        0 |
| xarray             | `attr: global.x`                             |     36 |      0 |        0 |
| xarray             | `Lambda`                                     |     34 |     21 |       21 |
| xarray             | `None literal`                               |     30 |     16 |       16 |
| xarray             | `attr: module.x`                             |     26 |      0 |        0 |
| xarray             | `SetComp (unknown elements)`                 |     25 |     16 |       13 |
| xarray             | `subscript: imported[...]`                   |     21 |     13 |       13 |
| xarray             | `boolop (or)`                                |     18 |      8 |        7 |
| xarray             | `call: other.method()`                       |     18 |      3 |        3 |
| xarray             | `call: builtin.method()`                     |     16 |      8 |        7 |
| xarray             | `call: builtin next()`                       |     16 |     11 |        6 |
| xarray             | `boolop (and)`                               |     12 |      4 |        3 |
| xarray             | `call: builtin sorted()`                     |     11 |      5 |        3 |
| xarray             | `call: modclass.method()`                    |     10 |      0 |        0 |
| xarray             | `copy: other`                                |     10 |      2 |        2 |
| xarray             | `copy: self`                                 |     10 |      7 |        6 |
| xarray             | `GeneratorExp (unknown elements)`            |      9 |      5 |        5 |
| xarray             | `copy: global`                               |      9 |      0 |        0 |
| xarray             | `subscript: global[...]`                     |      8 |      4 |        1 |
| xarray             | `subscript: other[...]`                      |      8 |      3 |        3 |
| xarray             | `copy: modclass`                             |      7 |      0 |        0 |
| xarray             | `call: builtin open()`                       |      7 |      0 |        0 |
| xarray             | `call: builtin type()`                       |      6 |      2 |        2 |
| xarray             | `await: call: chained .method()`             |      6 |      1 |        1 |
| xarray             | `call: capitalised`                          |      6 |      0 |        0 |
| xarray             | `call: builtin staticmethod()`               |      6 |      0 |        0 |
| xarray             | `call: builtin max()`                        |      5 |      4 |        3 |
| xarray             | `call: global name`                          |      5 |      3 |        3 |
| xarray             | `call: builtin slice()`                      |      5 |      2 |        2 |
| xarray             | `attr: imported.x`                           |      5 |      3 |        3 |
| xarray             | `call: builtin abs()`                        |      4 |      0 |        0 |
| xarray             | `unaryop Invert`                             |      4 |      2 |        2 |
| xarray             | `call: builtin iter()`                       |      4 |      3 |        3 |
| xarray             | `call: builtin min()`                        |      4 |      4 |        4 |
| xarray             | `copy: builtin`                              |      3 |      0 |        0 |
| xarray             | `copy: moddef`                               |      3 |      2 |        2 |
| xarray             | `attr: modclass.x`                           |      3 |      0 |        0 |
| xarray             | `subscript: self[...]`                       |      3 |      3 |        3 |
| xarray             | `call: builtin object()`                     |      3 |      0 |        0 |
| xarray             | `call: cls name`                             |      3 |      2 |        2 |
| xarray             | `call: builtin reversed()`                   |      3 |      1 |        0 |
| xarray             | `call: module class`                         |      3 |      2 |        2 |
| xarray             | `set (mixed/unknown elements)`               |      2 |      2 |        2 |
| xarray             | `call: builtin locals()`                     |      2 |      0 |        0 |
| xarray             | `await: call: local.method()`                |      2 |      0 |        0 |
| xarray             | `unaryop USub`                               |      2 |      0 |        0 |
| xarray             | `empty tuple`                                |      1 |      0 |        0 |
| xarray             | `await: call: imported.attr()`               |      1 |      0 |        0 |
| xarray             | `JoinedStr`                                  |      1 |      1 |        1 |
| xarray             | `call: builtin property()`                   |      1 |      0 |        0 |
| xarray             | `call: cls.method()`                         |      1 |      1 |        1 |
| xarray             | `call: builtin compile()`                    |      1 |      1 |        1 |
| xarray             | `call: builtin any()`                        |      1 |      1 |        1 |
| xarray             | `await: call: param name`                    |      1 |      0 |        0 |
| xarray             | `await: call: module.func()`                 |      1 |      0 |        0 |
| xarray             | `await: copy: local`                         |      1 |      0 |        0 |
| xarray             | `attr: other.x`                              |      1 |      1 |        1 |
| litestar           | `call: imported function`                    |     84 |     64 |       45 |
| litestar           | `call: chained .method()`                    |     79 |     64 |       43 |
| litestar           | `conditional`                                |     63 |     59 |       36 |
| litestar           | `call: local.method()`                       |     57 |     43 |       28 |
| litestar           | `subscript: other`                           |     56 |     50 |       33 |
| litestar           | `call: param.method()`                       |     54 |     36 |       21 |
| litestar           | `call: builtin getattr()`                    |     47 |     43 |       15 |
| litestar           | `attr: chained`                              |     36 |     34 |       22 |
| litestar           | `attr: self.x`                               |     34 |     32 |       12 |
| litestar           | `await: call: self.method()`                 |     33 |     31 |       25 |
| litestar           | `call: self.method()`                        |     33 |     29 |       19 |
| litestar           | `attr: param.x`                              |     28 |     19 |        6 |
| litestar           | `attr: local.x`                              |     28 |     20 |       12 |
| litestar           | `copy: local`                                |     25 |     19 |       15 |
| litestar           | `boolop (or)`                                |     24 |     21 |       16 |
| litestar           | `call: module function (annotated)`          |     23 |     20 |        4 |
| litestar           | `copy: param (annotated)`                    |     21 |     17 |       11 |
| litestar           | `ListComp (unknown elements)`                |     21 |     17 |       13 |
| litestar           | `subscript: imported[...]`                   |     19 |      0 |        0 |
| litestar           | `dict (mixed/unknown elements)`              |     18 |     10 |        8 |
| litestar           | `DictComp (unknown elements)`                |     16 |     13 |       12 |
| litestar           | `empty list`                                 |     14 |      0 |        0 |
| litestar           | `GeneratorExp (unknown elements)`            |     13 |     13 |       12 |
| litestar           | `copy: imported`                             |     13 |      6 |        6 |
| litestar           | `await: call: chained .method()`             |     13 |     13 |       12 |
| litestar           | `empty dict`                                 |     12 |      0 |        0 |
| litestar           | `subscript: local[...]`                      |     12 |     11 |        8 |
| litestar           | `call: module.func()`                        |     12 |      9 |        8 |
| litestar           | `subscript: param[...]`                      |     11 |     10 |        5 |
| litestar           | `call: builtin list()`                       |     11 |     11 |        6 |
| litestar           | `attr: imported.x`                           |     10 |      4 |        4 |
| litestar           | `call: cls.method()`                         |     10 |      9 |        5 |
| litestar           | `await: call: param.method()`                |      9 |      9 |        3 |
| litestar           | `call: builtin set()`                        |      9 |      4 |        4 |
| litestar           | `call: imported class`                       |      9 |      8 |        8 |
| litestar           | `copy: modclass`                             |      7 |      0 |        0 |
| litestar           | `SetComp (unknown elements)`                 |      6 |      2 |        2 |
| litestar           | `binop (unknown operands)`                   |      6 |      5 |        5 |
| litestar           | `call: other callee`                         |      6 |      6 |        6 |
| litestar           | `list (mixed/unknown elements)`              |      6 |      4 |        4 |
| litestar           | `call: builtin tuple()`                      |      6 |      6 |        1 |
| litestar           | `set (mixed/unknown elements)`               |      5 |      2 |        2 |
| litestar           | `other constant`                             |      5 |      2 |        2 |
| litestar           | `call: imported.attr()`                      |      4 |      3 |        3 |
| litestar           | `call: builtin dict()`                       |      4 |      4 |        3 |
| litestar           | `tuple (mixed/unknown elements)`             |      4 |      0 |        0 |
| litestar           | `None literal`                               |      3 |      1 |        1 |
| litestar           | `call: modclass.method()`                    |      3 |      2 |        1 |
| litestar           | `call: global.method()`                      |      3 |      3 |        2 |
| litestar           | `call: other name`                           |      3 |      2 |        2 |
| litestar           | `await: call: local.method()`                |      3 |      3 |        2 |
| litestar           | `call: builtin next()`                       |      2 |      2 |        2 |
| litestar           | `await: call: imported function`             |      2 |      1 |        0 |
| litestar           | `attr: other.x`                              |      2 |      1 |        0 |
| litestar           | `await: call: local name`                    |      2 |      2 |        1 |
| litestar           | `call: local name`                           |      2 |      2 |        1 |
| litestar           | `subscript: global[...]`                     |      2 |      2 |        1 |
| litestar           | `subscript: other[...]`                      |      1 |      1 |        1 |
| litestar           | `JoinedStr`                                  |      1 |      0 |        0 |
| litestar           | `call: module class`                         |      1 |      1 |        1 |
| litestar           | `call: builtin enumerate()`                  |      1 |      1 |        0 |
| litestar           | `call: str-literal.method()`                 |      1 |      1 |        1 |
| litestar           | `call: builtin sorted()`                     |      1 |      1 |        1 |
| litestar           | `await: call: other name`                    |      1 |      1 |        0 |
| litestar           | `call: builtin compile()`                    |      1 |      1 |        1 |
| litestar           | `call: param name`                           |      1 |      1 |        1 |
| litestar           | `call: builtin reversed()`                   |      1 |      1 |        0 |
| litestar           | `binop (one side literal)`                   |      1 |      1 |        1 |
| litestar           | `attr: cls.x`                                |      1 |      1 |        1 |
| litestar           | `boolop (and)`                               |      1 |      1 |        1 |
| litestar           | `await: call: param name`                    |      1 |      1 |        0 |
| litestar           | `copy: other`                                |      1 |      1 |        0 |
| litestar           | `copy: builtin`                              |      1 |      0 |        0 |
| celery             | `None literal`                               |    294 |     39 |       39 |
| celery             | `call: chained .method()`                    |    209 |    142 |      106 |
| celery             | `call: self.method()`                        |    186 |    139 |      102 |
| celery             | `call: imported function`                    |    185 |     74 |       50 |
| celery             | `attr: self.x`                               |    166 |    141 |      110 |
| celery             | `tuple (mixed/unknown elements)`             |    155 |     76 |       61 |
| celery             | `call: local.method()`                       |    104 |     68 |       45 |
| celery             | `attr: chained`                              |     97 |     71 |       60 |
| celery             | `call: param.method()`                       |     93 |     81 |       60 |
| celery             | `other constant`                             |     93 |      4 |        4 |
| celery             | `copy: local`                                |     62 |     44 |       33 |
| celery             | `conditional`                                |     62 |     48 |       33 |
| celery             | `attr: param.x`                              |     61 |     58 |       43 |
| celery             | `boolop (or)`                                |     60 |     45 |       34 |
| celery             | `copy: other`                                |     57 |      1 |        0 |
| celery             | `call: module.func()`                        |     56 |     23 |       15 |
| celery             | `call: module function (unannotated)`        |     54 |     36 |       22 |
| celery             | `subscript: other`                           |     51 |     34 |       27 |
| celery             | `copy: param (unannotated)`                  |     49 |     41 |       26 |
| celery             | `attr: local.x`                              |     44 |     39 |       32 |
| celery             | `dict (mixed/unknown elements)`              |     43 |     21 |       13 |
| celery             | `attr: imported.x`                           |     33 |     10 |       10 |
| celery             | `call: builtin getattr()`                    |     30 |     22 |       10 |
| celery             | `call: param name`                           |     29 |     21 |       18 |
| celery             | `binop (unknown operands)`                   |     29 |     19 |       16 |
| celery             | `call: builtin set()`                        |     27 |      5 |        5 |
| celery             | `copy: imported`                             |     27 |      1 |        1 |
| celery             | `empty dict`                                 |     24 |      0 |        0 |
| celery             | `call: imported.attr()`                      |     23 |     18 |       13 |
| celery             | `call: local name`                           |     23 |     19 |        9 |
| celery             | `empty list`                                 |     22 |      0 |        0 |
| celery             | `copy: modclass`                             |     21 |      0 |        0 |
| celery             | `call: global name`                          |     20 |      0 |        0 |
| celery             | `call: other name`                           |     20 |     10 |        7 |
| celery             | `call: builtin next()`                       |     19 |      9 |        5 |
| celery             | `subscript: local[...]`                      |     19 |     14 |       10 |
| celery             | `call: imported class`                       |     16 |      6 |        5 |
| celery             | `call: builtin list()`                       |     16 |     11 |       10 |
| celery             | `subscript: param[...]`                      |     15 |     10 |       10 |
| celery             | `call: builtin dict()`                       |     15 |      9 |        5 |
| celery             | `call: capitalised`                          |     14 |      8 |        6 |
| celery             | `boolop (and)`                               |     13 |     10 |        5 |
| celery             | `call: builtin enumerate()`                  |     12 |     10 |        5 |
| celery             | `DictComp (unknown elements)`                |     12 |      5 |        3 |
| celery             | `attr: global.x`                             |     11 |      0 |        0 |
| celery             | `ListComp (unknown elements)`                |     11 |      7 |        5 |
| celery             | `call: builtin tuple()`                      |     10 |      8 |        7 |
| celery             | `call: other.method()`                       |      9 |      5 |        1 |
| celery             | `copy: global`                               |      9 |      3 |        3 |
| celery             | `call: other callee`                         |      9 |      6 |        2 |
| celery             | `attr: module.x`                             |      9 |      0 |        0 |
| celery             | `set (mixed/unknown elements)`               |      9 |      2 |        2 |
| celery             | `call: module function (annotated)`          |      8 |      8 |        5 |
| celery             | `subscript: other[...]`                      |      7 |      6 |        3 |
| celery             | `call: global.method()`                      |      7 |      6 |        2 |
| celery             | `binop (one side literal)`                   |      7 |      6 |        6 |
| celery             | `empty tuple`                                |      6 |      0 |        0 |
| celery             | `compare`                                    |      6 |      4 |        4 |
| celery             | `call: builtin min()`                        |      6 |      6 |        6 |
| celery             | `subscript: self[...]`                       |      6 |      5 |        1 |
| celery             | `call: builtin reversed()`                   |      5 |      2 |        2 |
| celery             | `copy: self`                                 |      5 |      4 |        1 |
| celery             | `list (mixed/unknown elements)`              |      5 |      3 |        3 |
| celery             | `copy: moddef`                               |      5 |      1 |        1 |
| celery             | `copy: builtin`                              |      4 |      0 |        0 |
| celery             | `call: builtin type()`                       |      3 |      3 |        1 |
| celery             | `GeneratorExp (unknown elements)`            |      3 |      3 |        3 |
| celery             | `call: builtin property()`                   |      3 |      0 |        0 |
| celery             | `SetComp (unknown elements)`                 |      3 |      1 |        1 |
| celery             | `call: cls.method()`                         |      3 |      2 |        0 |
| celery             | `call: builtin max()`                        |      3 |      2 |        2 |
| celery             | `call: builtin.method()`                     |      3 |      3 |        3 |
| celery             | `attr: cls.x`                                |      2 |      2 |        2 |
| celery             | `call: builtin frozenset()`                  |      2 |      0 |        0 |
| celery             | `call: builtin iter()`                       |      2 |      1 |        0 |
| celery             | `call: builtin sum()`                        |      2 |      0 |        0 |
| celery             | `call: builtin len()`                        |      2 |      2 |        2 |
| celery             | `call: modclass.method()`                    |      2 |      2 |        0 |
| celery             | `attr: other.x`                              |      2 |      2 |        1 |
| celery             | `subscript: global[...]`                     |      2 |      2 |        0 |
| celery             | `attr: builtin.x`                            |      2 |      2 |        2 |
| celery             | `call: builtin object()`                     |      2 |      0 |        0 |
| celery             | `call: builtin open()`                       |      2 |      2 |        2 |
| celery             | `call: builtin sorted()`                     |      2 |      2 |        2 |
| celery             | `JoinedStr`                                  |      1 |      1 |        1 |
| celery             | `call: builtin map()`                        |      1 |      1 |        1 |
| celery             | `call: builtin bytearray()`                  |      1 |      0 |        0 |
| celery             | `call: builtin memoryview()`                 |      1 |      0 |        0 |
| celery             | `call: str-literal.method()`                 |      1 |      1 |        1 |
| celery             | `call: builtin __import__()`                 |      1 |      1 |        1 |
| celery             | `subscript: imported[...]`                   |      1 |      1 |        1 |
| celery             | `attr: modclass.x`                           |      1 |      0 |        0 |
| celery             | `call: cls name`                             |      1 |      1 |        1 |
| optuna             | `call: module.func()`                        |    278 |    230 |      220 |
| optuna             | `call: chained .method()`                    |    209 |    156 |      119 |
| optuna             | `call: imported.attr()`                      |    108 |     41 |       41 |
| optuna             | `binop (unknown operands)`                   |     87 |     76 |       74 |
| optuna             | `call: imported function`                    |     79 |      5 |        3 |
| optuna             | `empty list`                                 |     71 |      0 |        0 |
| optuna             | `attr: param.x`                              |     65 |     59 |       51 |
| optuna             | `call: local.method()`                       |     62 |     35 |       30 |
| optuna             | `subscript: other`                           |     54 |     43 |       37 |
| optuna             | `call: module function (annotated)`          |     39 |     34 |       33 |
| optuna             | `subscript: param[...]`                      |     35 |     35 |       33 |
| optuna             | `call: builtin zip()`                        |     35 |     24 |       18 |
| optuna             | `call: imported class`                       |     35 |      0 |        0 |
| optuna             | `call: param.method()`                       |     33 |     16 |       13 |
| optuna             | `subscript: local[...]`                      |     32 |     28 |       24 |
| optuna             | `ListComp (unknown elements)`                |     32 |     23 |       21 |
| optuna             | `attr: chained`                              |     31 |     19 |       14 |
| optuna             | `binop (one side literal)`                   |     28 |     26 |       26 |
| optuna             | `conditional`                                |     28 |     21 |       14 |
| optuna             | `None literal`                               |     28 |      5 |        5 |
| optuna             | `attr: local.x`                              |     28 |     16 |       13 |
| optuna             | `tuple (mixed/unknown elements)`             |     24 |     15 |       12 |
| optuna             | `compare`                                    |     23 |     22 |       22 |
| optuna             | `empty dict`                                 |     20 |      0 |        0 |
| optuna             | `call: global.method()`                      |     20 |      0 |        0 |
| optuna             | `copy: local`                                |     19 |      5 |        5 |
| optuna             | `call: builtin enumerate()`                  |     15 |      8 |        7 |
| optuna             | `call: other name`                           |     13 |      6 |        6 |
| optuna             | `other constant`                             |     12 |      4 |        4 |
| optuna             | `DictComp (unknown elements)`                |     11 |      7 |        0 |
| optuna             | `copy: param (annotated)`                    |     11 |      6 |        4 |
| optuna             | `list (mixed/unknown elements)`              |     10 |      5 |        5 |
| optuna             | `unaryop USub`                               |      9 |      9 |        8 |
| optuna             | `call: self.method()`                        |      9 |      6 |        4 |
| optuna             | `call: builtin max()`                        |      9 |      6 |        3 |
| optuna             | `attr: self.x`                               |      8 |      8 |        5 |
| optuna             | `dict (mixed/unknown elements)`              |      7 |      2 |        2 |
| optuna             | `call: builtin getattr()`                    |      6 |      4 |        4 |
| optuna             | `call: builtin set()`                        |      6 |      5 |        5 |
| optuna             | `unaryop Invert`                             |      5 |      4 |        4 |
| optuna             | `subscript: imported[...]`                   |      5 |      0 |        0 |
| optuna             | `call: builtin list()`                       |      4 |      0 |        0 |
| optuna             | `copy: other`                                |      4 |      3 |        2 |
| optuna             | `call: builtin tuple()`                      |      4 |      0 |        0 |
| optuna             | `boolop (or)`                                |      3 |      1 |        1 |
| optuna             | `copy: global`                               |      2 |      1 |        0 |
| optuna             | `subscript: other[...]`                      |      2 |      2 |        2 |
| optuna             | `boolop (and)`                               |      2 |      2 |        0 |
| optuna             | `copy: imported`                             |      2 |      1 |        1 |
| optuna             | `call: builtin next()`                       |      2 |      2 |        0 |
| optuna             | `attr: imported.x`                           |      2 |      1 |        1 |
| optuna             | `call: param name`                           |      2 |      2 |        2 |
| optuna             | `call: builtin sorted()`                     |      2 |      2 |        2 |
| optuna             | `call: builtin min()`                        |      2 |      0 |        0 |
| optuna             | `GeneratorExp (unknown elements)`            |      1 |      1 |        1 |
| optuna             | `call: other.method()`                       |      1 |      1 |        0 |
| optuna             | `attr: modclass.x`                           |      1 |      0 |        0 |
| optuna             | `call: builtin len()`                        |      1 |      0 |        0 |
| optuna             | `call: local name`                           |      1 |      0 |        0 |
| optuna             | `call: other callee`                         |      1 |      1 |        1 |
| optuna             | `subscript: builtin[...]`                    |      1 |      0 |        0 |
| optuna             | `call: builtin sum()`                        |      1 |      1 |        1 |
| optuna             | `call: builtin globals()`                    |      1 |      0 |        0 |
| optuna             | `attr: module.x`                             |      1 |      0 |        0 |
| optuna             | `call: moddef.method()`                      |      1 |      0 |        0 |
| optuna             | `call: builtin property()`                   |      1 |      0 |        0 |
| optuna             | `call: builtin object()`                     |      1 |      0 |        0 |
| dask               | `call: module.func()`                        |  3,995 |    196 |      183 |
| dask               | `call: imported function`                    |  1,744 |    334 |      246 |
| dask               | `call: chained .method()`                    |  1,448 |    182 |      149 |
| dask               | `call: local.method()`                       |  1,411 |    164 |      104 |
| dask               | `call: global.method()`                      |    908 |     11 |        9 |
| dask               | `call: module function (unannotated)`        |    492 |    217 |      153 |
| dask               | `call: param.method()`                       |    470 |    212 |      144 |
| dask               | `dict (mixed/unknown elements)`              |    446 |     56 |       45 |
| dask               | `binop (unknown operands)`                   |    406 |    215 |      170 |
| dask               | `copy: param (unannotated)`                  |    390 |    159 |      106 |
| dask               | `list (mixed/unknown elements)`              |    366 |     59 |       33 |
| dask               | `ListComp (unknown elements)`                |    350 |    194 |      141 |
| dask               | `subscript: other`                           |    334 |     90 |       68 |
| dask               | `empty list`                                 |    296 |      0 |        0 |
| dask               | `tuple (mixed/unknown elements)`             |    269 |     83 |       73 |
| dask               | `subscript: local[...]`                      |    247 |     99 |       71 |
| dask               | `call: builtin zip()`                        |    235 |    119 |       92 |
| dask               | `copy: local`                                |    232 |    111 |       81 |
| dask               | `call: builtin list()`                       |    211 |    109 |       83 |
| dask               | `binop (one side literal)`                   |    195 |     27 |       27 |
| dask               | `empty dict`                                 |    193 |      0 |        0 |
| dask               | `subscript: param[...]`                      |    180 |    113 |       86 |
| dask               | `attr: chained`                              |    178 |     75 |       55 |
| dask               | `call: module class`                         |    173 |      6 |        5 |
| dask               | `DictComp (unknown elements)`                |    168 |     88 |       66 |
| dask               | `attr: self.x`                               |    166 |    130 |       62 |
| dask               | `call: other callee`                         |    152 |     22 |       14 |
| dask               | `conditional`                                |    149 |     81 |       45 |
| dask               | `call: builtin getattr()`                    |    146 |     33 |       19 |
| dask               | `attr: local.x`                              |    144 |     70 |       54 |
| dask               | `call: local name`                           |    143 |     33 |       19 |
| dask               | `call: builtin enumerate()`                  |    135 |     92 |       67 |
| dask               | `call: param name`                           |    131 |     25 |       10 |
| dask               | `call: self.method()`                        |    129 |    112 |       62 |
| dask               | `attr: imported.x`                           |    112 |      1 |        1 |
| dask               | `other constant`                             |    100 |     25 |       25 |
| dask               | `attr: param.x`                              |     98 |     64 |       46 |
| dask               | `call: builtin tuple()`                      |     96 |     58 |       44 |
| dask               | `call: builtin set()`                        |     83 |     21 |       15 |
| dask               | `call: builtin staticmethod()`               |     79 |      0 |        0 |
| dask               | `call: builtin dict()`                       |     72 |     19 |        9 |
| dask               | `call: imported.attr()`                      |     70 |     36 |       25 |
| dask               | `None literal`                               |     67 |     36 |       36 |
| dask               | `call: imported class`                       |     64 |     10 |       10 |
| dask               | `attr: module.x`                             |     59 |      1 |        1 |
| dask               | `boolop (or)`                                |     56 |     46 |       38 |
| dask               | `Lambda`                                     |     53 |      3 |        3 |
| dask               | `call: other name`                           |     51 |     20 |       14 |
| dask               | `compare`                                    |     48 |     18 |       17 |
| dask               | `call: module function (annotated)`          |     36 |     28 |       10 |
| dask               | `call: builtin sorted()`                     |     31 |     18 |        9 |
| dask               | `GeneratorExp (unknown elements)`            |     31 |     14 |       14 |
| dask               | `call: builtin max()`                        |     30 |     23 |       17 |
| dask               | `SetComp (unknown elements)`                 |     28 |     21 |       16 |
| dask               | `copy: other`                                |     19 |      6 |        5 |
| dask               | `call: builtin type()`                       |     19 |     13 |        2 |
| dask               | `call: builtin divmod()`                     |     18 |     14 |       14 |
| dask               | `await: call: param.method()`                |     17 |      0 |        0 |
| dask               | `call: builtin sum()`                        |     16 |      5 |        5 |
| dask               | `copy: builtin`                              |     15 |      1 |        0 |
| dask               | `copy: param (annotated)`                    |     14 |     13 |        6 |
| dask               | `copy: imported`                             |     14 |      5 |        5 |
| dask               | `call: builtin next()`                       |     14 |     12 |        5 |
| dask               | `call: global name`                          |     13 |      4 |        3 |
| dask               | `copy: modclass`                             |     13 |      0 |        0 |
| dask               | `call: builtin min()`                        |     12 |      8 |        7 |
| dask               | `call: builtin slice()`                      |     11 |      5 |        5 |
| dask               | `copy: global`                               |     11 |      0 |        0 |
| dask               | `call: cls.method()`                         |     10 |      9 |        7 |
| dask               | `call: other.method()`                       |     10 |      6 |        4 |
| dask               | `copy: self`                                 |     10 |      8 |        5 |
| dask               | `subscript: global[...]`                     |      9 |      4 |        4 |
| dask               | `set (mixed/unknown elements)`               |      8 |      4 |        3 |
| dask               | `copy: moddef`                               |      8 |      3 |        3 |
| dask               | `subscript: other[...]`                      |      8 |      5 |        4 |
| dask               | `attr: global.x`                             |      8 |      0 |        0 |
| dask               | `call: builtin iter()`                       |      7 |      5 |        4 |
| dask               | `call: capitalised`                          |      7 |      1 |        1 |
| dask               | `JoinedStr`                                  |      7 |      7 |        7 |
| dask               | `attr: modclass.x`                           |      6 |      0 |        0 |
| dask               | `call: builtin.method()`                     |      5 |      3 |        2 |
| dask               | `empty tuple`                                |      5 |      0 |        0 |
| dask               | `call: builtin range()`                      |      5 |      4 |        4 |
| dask               | `call: builtin open()`                       |      5 |      0 |        0 |
| dask               | `call: builtin object()`                     |      4 |      0 |        0 |
| dask               | `call: builtin int()`                        |      3 |      2 |        2 |
| dask               | `subscript: self[...]`                       |      3 |      3 |        3 |
| dask               | `boolop (and)`                               |      3 |      2 |        2 |
| dask               | `call: builtin abs()`                        |      2 |      2 |        2 |
| dask               | `call: builtin vars()`                       |      2 |      0 |        0 |
| dask               | `attr: cls.x`                                |      2 |      2 |        1 |
| dask               | `unaryop USub`                               |      2 |      1 |        1 |
| dask               | `call: cls name`                             |      1 |      0 |        0 |
| dask               | `call: builtin property()`                   |      1 |      0 |        0 |
| dask               | `attr: builtin.x`                            |      1 |      1 |        1 |
| dask               | `call: builtin any()`                        |      1 |      1 |        1 |
| dask               | `await: call: chained .method()`             |      1 |      0 |        0 |
| dask               | `call: builtin reversed()`                   |      1 |      1 |        1 |
| dask               | `call: builtin len()`                        |      1 |      1 |        1 |
| dask               | `call: builtin frozenset()`                  |      1 |      1 |        0 |
| dask               | `await: call: local.method()`                |      1 |      0 |        0 |
| mypy               | `call: imported function`                    |    515 |    335 |      119 |
| mypy               | `call: chained .method()`                    |    370 |    258 |      149 |
| mypy               | `call: self.method()`                        |    339 |    263 |       90 |
| mypy               | `copy: local`                                |    256 |    169 |      102 |
| mypy               | `attr: chained`                              |    253 |    173 |      136 |
| mypy               | `attr: param.x`                              |    236 |    199 |      102 |
| mypy               | `empty list`                                 |    229 |      0 |        0 |
| mypy               | `subscript: other`                           |    224 |    143 |       81 |
| mypy               | `attr: local.x`                              |    224 |    132 |       94 |
| mypy               | `call: local.method()`                       |    193 |    130 |       82 |
| mypy               | `call: module function (annotated)`          |    124 |     89 |       31 |
| mypy               | `call: param.method()`                       |    106 |     87 |       46 |
| mypy               | `ListComp (unknown elements)`                |    102 |     62 |       40 |
| mypy               | `copy: param (annotated)`                    |    101 |     87 |       42 |
| mypy               | `call: builtin zip()`                        |     99 |     73 |       29 |
| mypy               | `conditional`                                |     99 |     66 |       37 |
| mypy               | `None literal`                               |     92 |     67 |       67 |
| mypy               | `call: module.func()`                        |     86 |     36 |       20 |
| mypy               | `binop (unknown operands)`                   |     75 |     34 |       27 |
| mypy               | `attr: self.x`                               |     71 |     60 |       39 |
| mypy               | `subscript: local[...]`                      |     67 |     47 |       30 |
| mypy               | `subscript: param[...]`                      |     66 |     42 |       28 |
| mypy               | `call: builtin enumerate()`                  |     64 |     58 |       26 |
| mypy               | `boolop (or)`                                |     51 |     34 |       28 |
| mypy               | `tuple (mixed/unknown elements)`             |     48 |     31 |       24 |
| mypy               | `other constant`                             |     42 |     11 |       11 |
| mypy               | `call: builtin set()`                        |     40 |      8 |        7 |
| mypy               | `boolop (and)`                               |     33 |     28 |       26 |
| mypy               | `call: builtin sorted()`                     |     33 |     12 |       11 |
| mypy               | `list (mixed/unknown elements)`              |     33 |     13 |        8 |
| mypy               | `call: imported.attr()`                      |     29 |     21 |       14 |
| mypy               | `empty dict`                                 |     28 |      0 |        0 |
| mypy               | `SetComp (unknown elements)`                 |     27 |     15 |       14 |
| mypy               | `call: builtin list()`                       |     24 |     13 |        9 |
| mypy               | `DictComp (unknown elements)`                |     22 |     13 |        9 |
| mypy               | `call: builtin getattr()`                    |     21 |     15 |        8 |
| mypy               | `call: global.method()`                      |     17 |      1 |        1 |
| mypy               | `binop (one side literal)`                   |     16 |      4 |        4 |
| mypy               | `attr: imported.x`                           |     15 |      7 |        7 |
| mypy               | `copy: imported`                             |     15 |      5 |        5 |
| mypy               | `call: other name`                           |     13 |      9 |        8 |
| mypy               | `dict (mixed/unknown elements)`              |     12 |      7 |        4 |
| mypy               | `attr: module.x`                             |     11 |      0 |        0 |
| mypy               | `call: builtin reversed()`                   |     11 |      3 |        0 |
| mypy               | `compare`                                    |      8 |      7 |        7 |
| mypy               | `copy: global`                               |      8 |      2 |        2 |
| mypy               | `call: imported class`                       |      8 |      7 |        7 |
| mypy               | `subscript: imported[...]`                   |      7 |      6 |        5 |
| mypy               | `call: local name`                           |      7 |      2 |        0 |
| mypy               | `call: builtin next()`                       |      6 |      4 |        3 |
| mypy               | `call: builtin dict()`                       |      6 |      2 |        2 |
| mypy               | `call: other.method()`                       |      6 |      6 |        4 |
| mypy               | `call: builtin open()`                       |      4 |      1 |        1 |
| mypy               | `call: builtin tuple()`                      |      4 |      2 |        1 |
| mypy               | `subscript: global[...]`                     |      4 |      4 |        3 |
| mypy               | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| mypy               | `call: modclass.method()`                    |      4 |      4 |        4 |
| mypy               | `copy: other`                                |      3 |      3 |        3 |
| mypy               | `call: builtin any()`                        |      3 |      3 |        3 |
| mypy               | `JoinedStr`                                  |      3 |      0 |        0 |
| mypy               | `subscript: other[...]`                      |      3 |      3 |        2 |
| mypy               | `attr: modclass.x`                           |      2 |      1 |        1 |
| mypy               | `call: param name`                           |      2 |      1 |        0 |
| mypy               | `call: builtin type()`                       |      2 |      2 |        1 |
| mypy               | `call: builtin.method()`                     |      2 |      1 |        0 |
| mypy               | `call: builtin format()`                     |      2 |      1 |        1 |
| mypy               | `set (mixed/unknown elements)`               |      2 |      2 |        2 |
| mypy               | `call: builtin min()`                        |      2 |      2 |        2 |
| mypy               | `call: other callee`                         |      1 |      1 |        0 |
| mypy               | `call: builtin object()`                     |      1 |      0 |        0 |
| mypy               | `attr: other.x`                              |      1 |      1 |        1 |
| mypy               | `copy: builtin`                              |      1 |      0 |        0 |
| mypy               | `call: global name`                          |      1 |      0 |        0 |
| mypy               | `call: module class`                         |      1 |      1 |        1 |
| mypy               | `call: builtin str()`                        |      1 |      1 |        1 |
| mypy               | `call: builtin max()`                        |      1 |      0 |        0 |
| mypy               | `call: builtin iter()`                       |      1 |      0 |        0 |
| mypy               | `call: builtin property()`                   |      1 |      0 |        0 |
| mypy               | `copy: modclass`                             |      1 |      0 |        0 |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                                   | same as released | summary                                                               | new failures | gone | named | skipped anew | skipped no more |
| ------------------ | ------------------------------------- | ---------------- | --------------------------------------------------------------------- | -----------: | ---: | ----: | -----------: | --------------: |
| django             | released                              |                  | 1 errors, 5 expected failures, 2 failures, 17,585 ran, 1,149 skipped  |              |      |       |              |                 |
| django             | fix-certain                           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | fix-likely                            | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | fix-unsafe                            | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | infer-basedpyright                    | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | infer-pyrefly                         | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | infer-trace                           | True             | 5 expected failures, 3 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | infer-ty                              | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| django             | infer-union                           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| sqlalchemy         | released (from basic-11-03-2026-2103) |                  | 29,521 passed, 975 skipped                                            |              |      |       |              |                 |
| sqlalchemy         | fix-certain                           | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | fix-likely                            | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-basedpyright                    | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-pyrefly                         | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-trace                           | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-ty                              | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-union                           | False            | 4 failed, 29,517 passed, 975 skipped                                  |            4 |    0 |     0 |            0 |               0 |
| pydantic           | released (from super-10-26-2026-0545) |                  | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      |              |      |       |              |                 |
| pydantic           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pydantic           | infer-union                           | True             | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |            0 |               0 |
| pandas             | released (from super-10-26-2026-0545) |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |              |      |       |              |                 |
| pandas             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pandas             | infer-union                           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |            0 |               0 |
| structlog          | released (from super-10-26-2026-0545) |                  | 24 failed, 860 passed, 37 skipped                                     |              |      |       |              |                 |
| structlog          | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| structlog          | infer-union                           | True             | 24 failed, 860 passed, 37 skipped                                     |            0 |    0 |     0 |            0 |               0 |
| attrs              | released (from super-10-26-2026-0545) |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |              |      |       |              |                 |
| attrs              | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| attrs              | infer-union                           | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |            0 |               0 |
| click              | released (from super-10-26-2026-0545) |                  | 1,991 passed, 24 skipped, 1 xfailed                                   |              |      |       |              |                 |
| click              | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| click              | infer-union                           | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | released (from super-10-26-2026-0545) |                  | 2 failed, 194 passed                                                  |              |      |       |              |                 |
| hypercorn          | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| hypercorn          | infer-union                           | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |            0 |               0 |
| starlette          | released (from super-10-26-2026-0545) |                  | 1,271 passed, 2 skipped, 2 xfailed                                    |              |      |       |              |                 |
| starlette          | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| starlette          | infer-union                           | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | released (from super-10-26-2026-0545) |                  | 1 failed, 979 passed, 1 skipped                                       |              |      |       |              |                 |
| werkzeug           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| werkzeug           | infer-union                           | True             | 1 failed, 979 passed, 1 skipped                                       |            0 |    0 |     0 |            0 |               0 |
| mkdocs             | released (from super-10-26-2026-0545) |                  | 2 errors, 2 failures, 724 ran, 4 skipped                              |              |      |       |              |                 |
| mkdocs             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| mkdocs             | infer-union                           | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |              |                 |
| httpx              | released (from super-10-26-2026-0545) |                  | 1 failed, 1,416 passed, 1 skipped                                     |              |      |       |              |                 |
| httpx              | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| httpx              | infer-union                           | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |            0 |               0 |
| black              | released (from super-10-26-2026-0545) |                  | 519 passed, 1 skipped                                                 |              |      |       |              |                 |
| black              | fix-certain                           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | fix-likely                            | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     1 |            0 |               0 |
| black              | infer-basedpyright                    | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | infer-pyrefly                         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | infer-trace                           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | infer-ty                              | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| black              | infer-union                           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |            0 |               0 |
| fastapi            | released (from super-10-26-2026-0545) |                  | 3,551 passed, 17 skipped, 4 xfailed                                   |              |      |       |              |                 |
| fastapi            | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| fastapi            | infer-union                           | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |            0 |               0 |
| cattrs             | released (from super-10-26-2026-0545) |                  | 994 passed, 15 xfailed                                                |              |      |       |              |                 |
| cattrs             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| cattrs             | infer-union                           | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |            0 |               0 |
| pytest             | released (from super-10-26-2026-0545) |                  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  |              |      |       |              |                 |
| pytest             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pytest             | infer-union                           | True             | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  |            0 |    0 |     0 |            0 |               0 |
| botocore           | released (from super-10-26-2026-0545) |                  | 7 failed, 4,593 passed, 96 skipped                                    |              |      |       |              |                 |
| botocore           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| botocore           | infer-union                           | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | released (from super-10-26-2026-0545) |                  | 1,350 passed, 12 skipped                                              |              |      |       |              |                 |
| uvicorn            | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| uvicorn            | infer-union                           | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |            0 |               0 |
| mcp                | released                              |                  | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          |              |      |       |              |                 |
| mcp                | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mcp                | infer-union                           | True             | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          |            0 |    0 |     0 |            0 |               0 |
| pdm                | released (from super-10-26-2026-0545) |                  | 1,472 passed, 1 skipped                                               |              |      |       |              |                 |
| pdm                | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pdm                | infer-union                           | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | released                              |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |              |      |       |              |                 |
| strawberry-graphql | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| strawberry-graphql | infer-union                           | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |            0 |               0 |
| pygments           | released (from mega-11-04-2026-1810)  |                  | 5,330 passed, 16 skipped                                              |              |      |       |              |                 |
| pygments           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pygments           | infer-union                           | True             | 5,330 passed, 16 skipped                                              |            0 |    0 |     0 |            0 |               0 |
| streamlink         | released (from super-10-26-2026-0545) |                  | 9 error, 15 failed, 7,233 passed, 36 skipped                          |              |      |       |              |                 |
| streamlink         | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| streamlink         | infer-union                           | True             | 9 error, 15 failed, 7,233 passed, 36 skipped                          |            0 |    0 |     0 |            0 |               0 |
| sphinx             | released (from mega-11-04-2026-1810)  |                  | 7 failed, 2,394 passed, 23 skipped                                    |              |      |       |              |                 |
| sphinx             | fix-certain                           | True             | as infer-pyrefly's (implied)                                          |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-likely                            | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     1 |            0 |               0 |
| sphinx             | infer-basedpyright                    | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-pyrefly                         | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-trace                           | True             | 8 failed, 2,393 passed, 23 skipped                                    |            0 |    0 |     1 |            0 |               0 |
| sphinx             | infer-ty                              | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-union                           | True             | 8 failed, 2,393 passed, 23 skipped                                    |            0 |    0 |     1 |            0 |               0 |
| tox                | released (from super-10-26-2026-0545) |                  | 6 error, 17 failed, 8,525 passed, 31 skipped                          |              |      |       |              |                 |
| tox                | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| tox                | infer-union                           | True             | 6 error, 17 failed, 8,525 passed, 31 skipped                          |            0 |    0 |     0 |            0 |               0 |
| pint               | released (from mega-10-26-2026-2120)  |                  | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |              |      |       |              |                 |
| pint               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-union                           | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |            0 |               0 |
| altair             | released (from mega-11-04-2026-1810)  |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |              |                 |
| altair             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-union                           | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |            0 |               0 |
| seaborn            | released                              |                  | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |              |      |       |              |                 |
| seaborn            | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| seaborn            | infer-union                           | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | released (from mega-10-26-2026-2120)  |                  | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        |              |      |       |              |                 |
| aiohttp            | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| aiohttp            | infer-union                           | True             | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        |            0 |    0 |     0 |            0 |               0 |
| websockets         | released (from mega-10-30-2026-0857)  |                  | 2,589 ran, 8 skipped                                                  |              |      |       |              |                 |
| websockets         | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| websockets         | infer-union                           | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |              |                 |
| anyio              | released (from mega-10-30-2026-0857)  |                  | 3,824 passed, 19 skipped, 5 xfailed                                   |              |      |       |              |                 |
| anyio              | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| anyio              | infer-union                           | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |            0 |               0 |
| zarr               | released (from mega-10-28-2026-0057)  |                  | 8,422 passed, 1,205 skipped, 4 xfailed                                |              |      |       |              |                 |
| zarr               | fix-certain                           | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | fix-likely                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-basedpyright                    | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-pyrefly                         | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-trace                           | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-ty                              | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-union                           | True             | 1 failed, 8,421 passed, 1,205 skipped, 4 xfailed                      |            0 |    0 |     0 |            0 |               0 |
| joblib             | released                              |                  | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |              |      |       |              |                 |
| joblib             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| joblib             | infer-union                           | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |            0 |               0 |
| networkx           | released (from mega-10-26-2026-2120)  |                  | 10,083 passed, 62 skipped, 741 xfailed                                |              |      |       |              |                 |
| networkx           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| networkx           | infer-union                           | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |            0 |               0 |
| nibabel            | released                              |                  | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |              |      |       |              |                 |
| nibabel            | fix-certain                           | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | fix-likely                            | True             | 20 error, 107 failed, 5,170 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | fix-unsafe                            | True             | 20 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | infer-basedpyright                    | True             | 19 error, 109 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-pyrefly                         | True             | 20 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | infer-trace                           | True             | 21 error, 107 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-ty                              | True             | 21 error, 110 failed, 5,165 passed, 304 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-union                           | False            | 19 error, 109 failed, 5,167 passed, 304 skipped, 40 xfailed           |            2 |    0 |     0 |            0 |               0 |
| narwhals           | released (from mega-10-26-2026-2120)  |                  | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |              |      |       |              |                 |
| narwhals           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| narwhals           | infer-union                           | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |            0 |               0 |
| xarray             | released                              |                  | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |              |      |       |              |                 |
| xarray             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| xarray             | infer-union                           | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |            0 |               0 |
| litestar           | released                              |                  | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |              |      |       |              |                 |
| litestar           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| litestar           | infer-union                           | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |            0 |               0 |
| celery             | released                              |                  | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |              |      |       |              |                 |
| celery             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| celery             | infer-union                           | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |            0 |               0 |
| optuna             | released                              |                  | 16 error, 263 failed, 4,203 passed, 43 skipped                        |              |      |       |              |                 |
| optuna             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| optuna             | infer-union                           | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |            0 |               0 |
| dask               | released                              |                  | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |              |      |       |              |                 |
| dask               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| dask               | infer-union                           | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |            0 |               0 |
| mypy               | released (from mega-10-26-2026-2120)  |                  | 14,464 passed, 366 skipped, 12 xfailed                                |              |      |       |              |                 |
| mypy               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| mypy               | infer-union                           | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |            0 |               0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      0 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      1 |   1 |    0 |    183 files changed, 2263 insertions(+), 1721 deletions(-) |
| sqlalchemy         | fix-likely         |      1 |   1 |    0 |    193 files changed, 2727 insertions(+), 2140 deletions(-) |
| sqlalchemy         | fix-unsafe         |      1 |   1 |    0 |    206 files changed, 3441 insertions(+), 2816 deletions(-) |
| sqlalchemy         | infer-basedpyright |      4 |   4 |    0 |    210 files changed, 4184 insertions(+), 3514 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      2 |   2 |    0 |    209 files changed, 3920 insertions(+), 3138 deletions(-) |
| sqlalchemy         | infer-trace        |      7 |   7 |    0 |    208 files changed, 3638 insertions(+), 2954 deletions(-) |
| sqlalchemy         | infer-ty           |      3 |   3 |    0 |    208 files changed, 4129 insertions(+), 3359 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1691 insertions(+), 1280 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1691 insertions(+), 1280 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1691 insertions(+), 1280 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1917 insertions(+), 1493 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1952 insertions(+), 1412 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1691 insertions(+), 1280 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1826 insertions(+), 1405 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    261 |   3 |    1 | 1072 files changed, 18520 insertions(+), 15423 deletions(-) |
| pandas             | fix-likely         |    262 |   4 |    1 | 1204 files changed, 43362 insertions(+), 39439 deletions(-) |
| pandas             | fix-unsafe         |    267 |   9 |    1 | 1208 files changed, 44707 insertions(+), 40582 deletions(-) |
| pandas             | infer-basedpyright |    299 |  41 |    1 | 1216 files changed, 50750 insertions(+), 45998 deletions(-) |
| pandas             | infer-pyrefly      |    319 |  61 |    1 | 1217 files changed, 53158 insertions(+), 48084 deletions(-) |
| pandas             | infer-trace        |    267 |   9 |    1 | 1212 files changed, 46224 insertions(+), 41975 deletions(-) |
| pandas             | infer-ty           |    274 |  16 |    1 | 1218 files changed, 50542 insertions(+), 45797 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 380 insertions(+), 294 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 380 insertions(+), 294 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 380 insertions(+), 294 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 456 insertions(+), 356 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 380 insertions(+), 294 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 463 insertions(+), 362 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 212 insertions(+), 146 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 212 insertions(+), 146 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 212 insertions(+), 146 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 222 insertions(+), 151 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 212 insertions(+), 146 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 162 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 458 insertions(+), 356 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 458 insertions(+), 356 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 458 insertions(+), 356 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 489 insertions(+), 377 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 458 insertions(+), 356 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 509 insertions(+), 398 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 701 insertions(+), 477 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 701 insertions(+), 477 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 701 insertions(+), 477 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 843 insertions(+), 566 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 701 insertions(+), 477 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 848 insertions(+), 581 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 415 insertions(+), 344 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 370 insertions(+), 298 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 399 insertions(+), 320 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | infer-basedpyright |      4 |   4 |    0 |       29 files changed, 378 insertions(+), 288 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 339 insertions(+), 246 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 360 insertions(+), 273 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 806 insertions(+), 540 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 972 insertions(+), 693 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1069 insertions(+), 768 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1185 insertions(+), 877 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1151 insertions(+), 832 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1069 insertions(+), 768 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1188 insertions(+), 850 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-basedpyright |     12 |   2 |    0 |     156 files changed, 1135 insertions(+), 857 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-ty           |     10 |   0 |    0 |     156 files changed, 1133 insertions(+), 850 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |    176 files changed, 1668 insertions(+), 1102 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |    176 files changed, 1668 insertions(+), 1102 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |    176 files changed, 1668 insertions(+), 1102 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    189 files changed, 2038 insertions(+), 1412 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |    177 files changed, 1803 insertions(+), 1197 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |    176 files changed, 1668 insertions(+), 1102 deletions(-) |
| streamlink         | infer-ty           |     24 |  24 |    0 |    186 files changed, 2303 insertions(+), 1418 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    196 files changed, 3475 insertions(+), 2361 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    198 files changed, 4017 insertions(+), 2791 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    213 files changed, 4439 insertions(+), 3142 deletions(-) |
| sphinx             | infer-basedpyright |      6 |   3 |    0 |    216 files changed, 5227 insertions(+), 3850 deletions(-) |
| sphinx             | infer-pyrefly      |     11 |   8 |    0 |    217 files changed, 5468 insertions(+), 3903 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    213 files changed, 4439 insertions(+), 3142 deletions(-) |
| sphinx             | infer-ty           |      4 |   1 |    0 |    215 files changed, 5272 insertions(+), 3823 deletions(-) |
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |      78 files changed, 1023 insertions(+), 757 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |      78 files changed, 1023 insertions(+), 757 deletions(-) |
| pint               | fix-unsafe         |    659 |   0 |    0 |      78 files changed, 1023 insertions(+), 757 deletions(-) |
| pint               | infer-basedpyright |    660 |   1 |    0 |      81 files changed, 1302 insertions(+), 965 deletions(-) |
| pint               | infer-pyrefly      |    664 |   5 |    0 |      79 files changed, 1093 insertions(+), 801 deletions(-) |
| pint               | infer-trace        |    662 |   3 |    0 |      78 files changed, 1036 insertions(+), 762 deletions(-) |
| pint               | infer-ty           |    660 |   2 |    1 |      79 files changed, 1183 insertions(+), 880 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |       40 files changed, 565 insertions(+), 446 deletions(-) |
| altair             | infer-pyrefly      |      4 |   3 |    0 |       40 files changed, 547 insertions(+), 426 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 489 insertions(+), 388 deletions(-) |
| altair             | infer-ty           |      4 |   3 |    0 |       40 files changed, 561 insertions(+), 440 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |      46 files changed, 1071 insertions(+), 832 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |       46 files changed, 865 insertions(+), 653 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |      46 files changed, 1071 insertions(+), 832 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      46 files changed, 1071 insertions(+), 832 deletions(-) |
| seaborn            | infer-pyrefly      |     39 |   0 |    0 |      47 files changed, 1158 insertions(+), 880 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |      47 files changed, 1014 insertions(+), 767 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |      46 files changed, 1035 insertions(+), 804 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 378 insertions(+), 250 deletions(-) |
| websockets         | fix-likely         |      1 |   1 |    0 |       39 files changed, 467 insertions(+), 323 deletions(-) |
| websockets         | fix-unsafe         |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 631 insertions(+), 459 deletions(-) |
| websockets         | infer-pyrefly      |      4 |   4 |    0 |       40 files changed, 642 insertions(+), 462 deletions(-) |
| websockets         | infer-trace        |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-ty           |      4 |   4 |    0 |       40 files changed, 643 insertions(+), 459 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    475 files changed, 7085 insertions(+), 5866 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    475 files changed, 7085 insertions(+), 5866 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    475 files changed, 7085 insertions(+), 5866 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    475 files changed, 7890 insertions(+), 6554 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    472 files changed, 7201 insertions(+), 5994 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    475 files changed, 7085 insertions(+), 5866 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    465 files changed, 7104 insertions(+), 5978 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    182 files changed, 2078 insertions(+), 1389 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    193 files changed, 2934 insertions(+), 2149 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    198 files changed, 3297 insertions(+), 2453 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    203 files changed, 3958 insertions(+), 2992 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    203 files changed, 3901 insertions(+), 2880 deletions(-) |
| nibabel            | infer-trace        |     14 |   2 |    0 |    198 files changed, 3395 insertions(+), 2519 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    200 files changed, 3918 insertions(+), 2948 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     20 |   1 |    0 |     100 files changed, 1132 insertions(+), 929 deletions(-) |
| narwhals           | fix-likely         |     20 |   1 |    0 |    100 files changed, 1212 insertions(+), 1001 deletions(-) |
| narwhals           | fix-unsafe         |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-basedpyright |     31 |  12 |    0 |    101 files changed, 1647 insertions(+), 1340 deletions(-) |
| narwhals           | infer-pyrefly      |     34 |  15 |    0 |    102 files changed, 1865 insertions(+), 1489 deletions(-) |
| narwhals           | infer-trace        |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-ty           |     34 |  15 |    0 |    102 files changed, 1572 insertions(+), 1284 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-basedpyright |     88 |   2 |    0 |     177 files changed, 1122 insertions(+), 810 deletions(-) |
| litestar           | infer-pyrefly      |     87 |   1 |    0 |      175 files changed, 986 insertions(+), 689 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-ty           |     91 |   5 |    0 |     179 files changed, 1127 insertions(+), 807 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    141 files changed, 1691 insertions(+), 1165 deletions(-) |
| optuna             | fix-likely         |     53 |   1 |    0 |    144 files changed, 1914 insertions(+), 1354 deletions(-) |
| optuna             | fix-unsafe         |     54 |   2 |    0 |    144 files changed, 2042 insertions(+), 1449 deletions(-) |
| optuna             | infer-basedpyright |     54 |   2 |    0 |    164 files changed, 2383 insertions(+), 1726 deletions(-) |
| optuna             | infer-pyrefly      |     56 |   4 |    0 |    147 files changed, 2337 insertions(+), 1689 deletions(-) |
| optuna             | infer-trace        |     54 |   2 |    0 |    144 files changed, 2042 insertions(+), 1449 deletions(-) |
| optuna             | infer-ty           |     57 |   5 |    0 |    162 files changed, 2394 insertions(+), 1726 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    160 files changed, 5400 insertions(+), 3339 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    166 files changed, 6639 insertions(+), 4417 deletions(-) |
| mypy               | fix-unsafe         |     14 |  14 |    0 |    167 files changed, 7057 insertions(+), 4768 deletions(-) |
| mypy               | infer-basedpyright |     20 |  20 |    0 |    170 files changed, 8789 insertions(+), 6312 deletions(-) |
| mypy               | infer-pyrefly      |     20 |  20 |    0 |    170 files changed, 9329 insertions(+), 6467 deletions(-) |
| mypy               | infer-trace        |     14 |  14 |    0 |    167 files changed, 7057 insertions(+), 4768 deletions(-) |
| mypy               | infer-ty           |     26 |  26 |    0 |    170 files changed, 9096 insertions(+), 6485 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    58.8 |       126.1 |  2.1 |    3.62 |          3 |     4.52 | False |
| standard library   | fix-certain              |   166.6 |       355.7 |  2.1 |    4.92 |          3 |      6.2 | False |
| standard library   | fix-likely               |   188.9 |       438.6 |  2.3 |    6.88 |          3 |      8.6 | False |
| standard library   | fix-unsafe               |   182.7 |       424.0 |  2.3 |    6.83 |          2 |     8.54 | False |
| standard library   | infer-basedpyright       |   459.9 |      1068.9 |  2.3 |   14.35 |          2 |    17.79 | False |
| standard library   | infer-ty                 |   279.3 |       583.1 |  2.1 |   10.26 |          1 |     4.15 | False |
| standard library   | infer-pyrefly            |   277.3 |       652.7 |  2.4 |   12.69 |          2 |    10.46 | False |
| standard library   | census                   |    25.8 |        25.5 |  1.0 |    0.48 |          3 |     4.52 | False |
| standard library   | coverage                 |    10.8 |        39.1 |  3.6 |    0.76 |          4 |     0.95 | False |
| standard library   | timing                   |   204.9 |       248.2 |  1.2 |    3.62 |          2 |     4.52 | False |
| django             | check                    |    11.2 |        27.0 |  2.4 |    1.06 |          2 |     1.32 | False |
| django             | fix-certain              |    42.8 |        68.4 |  1.6 |    1.38 |          2 |     1.72 | False |
| django             | fix-likely               |    38.6 |        79.7 |  2.1 |    1.77 |          2 |     2.21 | False |
| django             | fix-unsafe               |    35.2 |        80.2 |  2.3 |    1.67 |          2 |     2.09 | False |
| django             | infer-basedpyright       |    41.4 |        93.3 |  2.3 |    1.92 |          1 |     1.97 | False |
| django             | infer-ty                 |    62.5 |       108.8 |  1.7 |    3.36 |          1 |     2.09 | False |
| django             | infer-pyrefly            |    63.4 |       117.2 |  1.8 |    3.75 |          1 |     1.55 | False |
| django             | census                   |     3.6 |         3.3 |  0.9 |     0.1 |          2 |     1.32 | False |
| django             | coverage                 |     1.6 |         4.2 |  2.6 |    0.33 |          3 |     0.41 | False |
| django             | timing                   |    29.4 |        41.8 |  1.4 |    1.06 |          2 |     1.32 | False |
| django             | traced                   |    88.6 |       579.0 |  6.5 |    7.26 |          8 |     9.14 | False |
| django             | tests-released           |    88.8 |       398.4 |  4.5 |    4.86 |          8 |      6.1 | False |
| django             | tests-fix-certain        |    60.4 |       446.9 |  7.4 |    5.44 |          8 |     8.56 | False |
| django             | tests-fix-likely         |    40.4 |       409.0 | 10.1 |    5.47 |         13 |     6.82 | False |
| django             | tests-fix-unsafe         |    40.8 |       408.4 | 10.0 |    5.36 |          9 |     8.14 | False |
| django             | tests-infer-basedpyright |    52.8 |       382.5 |  7.2 |     4.7 |          8 |     5.76 | False |
| django             | tests-infer-ty           |    40.6 |       407.9 | 10.0 |    5.41 |         13 |     6.81 | False |
| django             | tests-infer-pyrefly      |    62.8 |       435.3 |  6.9 |    4.37 |          8 |     5.16 | False |
| django             | tests-infer-trace        |    69.4 |       436.8 |  6.3 |    5.35 |          8 |     6.53 | False |
| django             | infer-union              |   170.9 |       308.9 |  1.8 |    2.94 |          1 |     1.59 | False |
| django             | tests-infer-union        |    63.7 |       464.8 |  7.3 |    4.71 |          8 |     6.06 | False |
| django             | tests                    |    42.2 |       420.5 | 10.0 |    5.88 |          2 |      0.2 | False |
| sqlalchemy         | check                    |     0.4 |         0.3 |  0.7 |    0.06 |          2 |      1.1 | False |
| sqlalchemy         | fix-certain              |    58.8 |        61.1 |  1.0 |     1.0 |          2 |     1.25 | False |
| sqlalchemy         | fix-likely               |    74.3 |        81.6 |  1.1 |    1.31 |          2 |     1.65 | False |
| sqlalchemy         | fix-unsafe               |    34.4 |        68.1 |  2.0 |    1.22 |          3 |     1.52 | False |
| sqlalchemy         | infer-basedpyright       |    86.9 |        83.2 |  1.0 |    1.32 |          1 |     1.77 | False |
| sqlalchemy         | infer-ty                 |    43.0 |        76.2 |  1.8 |    1.31 |          1 |     1.97 | False |
| sqlalchemy         | infer-pyrefly            |    51.5 |        79.1 |  1.5 |    1.32 |          1 |     1.51 | False |
| sqlalchemy         | census                   |    13.8 |        23.9 |  1.7 |    0.87 |          2 |      1.1 | False |
| sqlalchemy         | coverage                 |     2.2 |         6.7 |  3.0 |    0.37 |          3 |     0.46 | False |
| sqlalchemy         | timing                   |    31.0 |        39.9 |  1.3 |    0.87 |          2 |     1.09 | False |
| sqlalchemy         | traced                   |   149.5 |      1135.7 |  7.6 |    5.76 |          9 |     7.19 | False |
| sqlalchemy         | tests-released           |    96.5 |       628.6 |  6.5 |    3.97 |          8 |     4.88 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          7 |     8.11 | False |
| sqlalchemy         | tests-fix-likely         |   123.3 |       734.3 |  6.0 |    3.93 |          8 |     4.82 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.27 | False |
| sqlalchemy         | tests-infer-basedpyright |    90.3 |       959.0 | 10.6 |    5.77 |         10 |     7.22 | False |
| sqlalchemy         | tests-infer-ty           |    87.1 |       952.7 | 10.9 |    5.82 |         10 |     7.27 | False |
| sqlalchemy         | tests-infer-pyrefly      |   104.9 |       719.5 |  6.9 |    3.91 |          8 |     4.82 | False |
| sqlalchemy         | tests-infer-trace        |   105.1 |       838.3 |  8.0 |    4.93 |          9 |     5.92 | False |
| sqlalchemy         | infer-union              |   109.4 |       345.9 |  3.2 |    5.54 |          3 |     4.47 | False |
| sqlalchemy         | tests-infer-union        |   127.2 |       845.9 |  6.7 |    4.28 |          8 |     5.46 | False |
| sqlalchemy         | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          1 |     0.19 | False |
| sqlalchemy         | types-released           |     5.2 |         4.7 |  0.9 |    0.31 |          1 |      0.4 | False |
| sqlalchemy         | types-fix-certain        |     9.2 |         6.9 |  0.8 |    0.33 |          1 |     0.41 | False |
| sqlalchemy         | types-fix-likely         |     8.6 |         7.2 |  0.8 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-unsafe         |     8.4 |         7.2 |  0.9 |    0.31 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |    11.8 |         8.3 |  0.7 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |    15.4 |         7.2 |  0.5 |    0.33 |          1 |     0.41 | False |
| sqlalchemy         | types-infer-pyrefly      |     8.6 |         7.0 |  0.8 |    0.32 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-trace        |     7.8 |         7.0 |  0.9 |    0.32 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     1.8 |         3.7 |  2.1 |    0.31 |          2 |     0.39 | False |
| pydantic           | fix-certain              |     6.5 |        13.5 |  2.1 |    0.41 |          2 |     0.52 | False |
| pydantic           | fix-likely               |     5.4 |        13.6 |  2.5 |    0.49 |          3 |     0.61 | False |
| pydantic           | fix-unsafe               |     5.4 |        14.2 |  2.6 |    0.44 |          2 |     0.55 | False |
| pydantic           | infer-basedpyright       |    13.6 |        18.6 |  1.4 |    0.49 |          1 |     1.44 | False |
| pydantic           | infer-ty                 |     8.8 |        16.4 |  1.9 |     0.5 |          1 |     0.87 | False |
| pydantic           | infer-pyrefly            |     9.2 |        17.7 |  1.9 |    0.49 |          1 |     0.91 | False |
| pydantic           | census                   |     1.4 |         1.1 |  0.8 |    0.05 |          2 |     0.39 | False |
| pydantic           | coverage                 |     1.2 |         2.2 |  1.8 |    0.22 |          2 |     0.27 | False |
| pydantic           | timing                   |     5.2 |         7.5 |  1.4 |    0.31 |          2 |     0.39 | False |
| pydantic           | traced                   |    95.7 |        69.6 |  0.7 |    0.55 |          1 |     0.67 | False |
| pydantic           | tests-released           |    69.1 |        44.1 |  0.6 |    0.29 |          1 |      0.4 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.37 | False |
| pydantic           | infer-union              |    11.2 |        20.4 |  1.8 |     0.5 |          1 |     0.82 | False |
| pydantic           | tests-infer-union        |    99.1 |        48.8 |  0.5 |    0.33 |          1 |     0.41 | False |
| pydantic           | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          1 |     0.19 | False |
| pydantic           | types-released           |    25.2 |        20.9 |  0.8 |    0.54 |          1 |     0.69 | False |
| pydantic           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.69 | False |
| pydantic           | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.69 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pydantic           | types-infer-basedpyright |    15.6 |        20.2 |  1.3 |    0.56 |          2 |      0.7 | False |
| pydantic           | types-infer-ty           |    20.8 |        19.7 |  0.9 |    0.52 |          1 |     0.69 | False |
| pydantic           | types-infer-pyrefly      |    11.2 |        16.1 |  1.4 |    0.54 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |    13.1 |        16.6 |  1.3 |    0.58 |          1 |     0.66 | False |
| pydantic           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |     1.2 |         1.1 |  0.9 |    0.21 |          3 |     4.52 | False |
| pandas             | fix-certain              |   125.9 |       340.2 |  2.7 |    4.24 |          3 |     5.32 | False |
| pandas             | fix-likely               |   260.2 |       623.5 |  2.4 |     6.8 |          3 |      8.5 | False |
| pandas             | fix-unsafe               |   255.8 |       594.8 |  2.3 |     6.7 |          3 |     8.37 | False |
| pandas             | infer-basedpyright       |   327.1 |       934.4 |  2.9 |   11.87 |          3 |    15.05 | False |
| pandas             | infer-ty                 |   268.6 |       714.6 |  2.7 |    9.41 |          3 |    11.76 | False |
| pandas             | infer-pyrefly            |   223.0 |       661.5 |  3.0 |    14.1 |          2 |    11.58 | False |
| pandas             | census                   |    62.6 |       141.8 |  2.3 |    3.62 |          3 |     4.52 | False |
| pandas             | coverage                 |     6.0 |        19.9 |  3.3 |    0.79 |          4 |     0.99 | False |
| pandas             | timing                   |   258.5 |       313.5 |  1.2 |    3.62 |          2 |     4.52 | False |
| pandas             | traced                   |   293.7 |      1439.4 |  4.9 |   14.13 |          7 |     17.8 | False |
| pandas             | tests-released           |   111.0 |       673.0 |  6.1 |   11.49 |          9 |    14.08 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    12.93 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    13.33 | False |
| pandas             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |    13.26 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    16.27 | False |
| pandas             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |    16.27 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    16.27 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    14.47 | False |
| pandas             | infer-union              |   426.4 |      1418.4 |  3.3 |   11.46 |          3 |    14.41 | False |
| pandas             | tests-infer-union        |   117.0 |       765.3 |  6.5 |    13.0 |          8 |    16.27 | False |
| pandas             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |     0.19 | False |
| pandas             | types-released           |    88.1 |       104.7 |  1.2 |    2.12 |          1 |     2.45 | False |
| pandas             | types-fix-certain        |    46.6 |        72.8 |  1.6 |    2.25 |          2 |     2.84 | False |
| pandas             | types-fix-likely         |    78.0 |       107.3 |  1.4 |    2.21 |          2 |     2.72 | False |
| pandas             | types-fix-unsafe         |    59.4 |        93.4 |  1.6 |    2.23 |          2 |     2.79 | False |
| pandas             | types-infer-basedpyright |    57.4 |        90.9 |  1.6 |     2.3 |          2 |      2.7 | False |
| pandas             | types-infer-ty           |    55.8 |        89.8 |  1.6 |    2.32 |          2 |     2.87 | False |
| pandas             | types-infer-pyrefly      |   104.9 |       116.3 |  1.1 |    2.23 |          2 |      2.8 | False |
| pandas             | types-infer-trace        |    65.7 |        85.5 |  1.3 |    2.27 |          2 |     2.76 | False |
| pandas             | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     7.0 |        17.2 |  2.5 |    0.81 |          3 |     1.01 | False |
| twisted            | fix-certain              |    12.8 |        37.5 |  2.9 |    0.95 |          3 |     1.19 | False |
| twisted            | fix-likely               |    19.6 |        57.0 |  2.9 |    1.28 |          3 |      1.6 | False |
| twisted            | fix-unsafe               |    18.2 |        53.9 |  3.0 |    1.22 |          3 |     1.52 | False |
| twisted            | infer-basedpyright       |    37.0 |        70.7 |  1.9 |    1.35 |          1 |     0.84 | False |
| twisted            | infer-ty                 |    36.6 |        67.3 |  1.8 |    1.31 |          1 |     0.82 | False |
| twisted            | infer-pyrefly            |    32.8 |        63.6 |  1.9 |     1.3 |          1 |     0.54 | False |
| twisted            | census                   |     3.8 |         3.6 |  0.9 |    0.11 |          3 |     1.01 | False |
| twisted            | coverage                 |     2.2 |         6.0 |  2.7 |    0.37 |          3 |     0.46 | False |
| twisted            | timing                   |    26.0 |        32.9 |  1.3 |    0.82 |          2 |     1.01 | False |
| pip                | check                    |     3.2 |         0.3 |  0.1 |    0.05 |          3 |     0.77 | False |
| pip                | fix-certain              |    10.8 |        29.4 |  2.7 |    0.77 |          3 |     0.96 | False |
| pip                | fix-likely               |    14.4 |        37.9 |  2.6 |    0.99 |          3 |     1.24 | False |
| pip                | fix-unsafe               |    12.4 |        34.4 |  2.8 |    0.92 |          3 |     1.16 | False |
| pip                | infer-basedpyright       |    39.7 |        64.4 |  1.6 |     1.0 |          1 |      1.4 | False |
| pip                | infer-ty                 |    31.2 |        49.7 |  1.6 |    0.97 |          1 |     0.79 | False |
| pip                | infer-pyrefly            |    26.8 |        46.7 |  1.7 |    0.99 |          1 |     1.28 | False |
| pip                | census                   |     5.4 |        10.6 |  2.0 |    0.62 |          3 |     0.77 | False |
| pip                | coverage                 |     1.6 |         4.2 |  2.6 |    0.31 |          3 |     0.39 | False |
| pip                | timing                   |    15.0 |        21.8 |  1.5 |    0.62 |          2 |     0.77 | False |
| structlog          | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| structlog          | fix-certain              |     1.8 |         2.8 |  1.6 |    0.26 |          2 |     0.32 | False |
| structlog          | fix-likely               |     1.8 |         3.0 |  1.7 |    0.26 |          2 |     0.32 | False |
| structlog          | fix-unsafe               |     1.8 |         3.0 |  1.7 |    0.26 |          1 |     0.34 | False |
| structlog          | infer-basedpyright       |     3.2 |         3.7 |  1.2 |    0.23 |          1 |     0.32 | False |
| structlog          | infer-ty                 |     3.4 |         3.5 |  1.0 |    0.26 |          1 |     0.16 | False |
| structlog          | infer-pyrefly            |     4.2 |         3.7 |  0.9 |    0.26 |          1 |     0.15 | False |
| structlog          | census                   |     1.2 |         1.2 |  1.0 |    0.17 |          1 |     0.21 | False |
| structlog          | coverage                 |     1.0 |         0.8 |  0.8 |    0.15 |          1 |     0.19 | False |
| structlog          | timing                   |     2.2 |         1.8 |  0.8 |    0.17 |          1 |     0.21 | False |
| structlog          | traced                   |     7.4 |         6.2 |  0.8 |    0.26 |          1 |     0.32 | False |
| structlog          | tests-released           |     3.6 |         2.0 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| structlog          | infer-union              |     5.8 |         4.9 |  0.8 |    0.26 |          1 |     0.31 | False |
| structlog          | tests-infer-union        |     3.2 |         2.2 |  0.7 |    0.08 |          1 |      0.1 | False |
| structlog          | tests                    |     2.0 |         1.7 |  0.8 |    0.16 |          1 |     0.19 | False |
| structlog          | types-released           |     0.8 |         0.5 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-infer-basedpyright |     0.8 |         0.5 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| structlog          | types-infer-pyrefly      |     0.8 |         0.4 |  0.5 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-trace        |     0.8 |         0.5 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| attrs              | fix-certain              |     1.8 |         2.6 |  1.4 |    0.28 |          2 |     0.32 | False |
| attrs              | fix-likely               |     1.6 |         2.2 |  1.4 |    0.28 |          2 |     0.32 | False |
| attrs              | fix-unsafe               |     2.0 |         2.6 |  1.3 |    0.28 |          1 |     0.35 | False |
| attrs              | infer-basedpyright       |     2.4 |         3.1 |  1.3 |    0.22 |          1 |     0.64 | False |
| attrs              | infer-ty                 |     3.0 |         3.1 |  1.0 |    0.27 |          1 |     0.17 | False |
| attrs              | infer-pyrefly            |     4.8 |         3.5 |  0.7 |    0.29 |          1 |     0.35 | False |
| attrs              | census                   |     1.2 |         1.1 |  0.9 |    0.16 |          1 |      0.2 | False |
| attrs              | coverage                 |     0.8 |         0.7 |  0.9 |    0.15 |          1 |     0.19 | False |
| attrs              | timing                   |     1.8 |         1.5 |  0.8 |    0.16 |          1 |      0.2 | False |
| attrs              | traced                   |     6.4 |        24.0 |  3.8 |    0.76 |          5 |     0.94 | False |
| attrs              | tests-released           |     2.8 |        13.6 |  4.9 |     0.6 |          6 |     0.77 | False |
| attrs              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.74 | False |
| attrs              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     0.75 | False |
| attrs              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | infer-union              |     2.8 |         3.7 |  1.3 |    0.26 |          2 |      0.7 | False |
| attrs              | tests-infer-union        |     4.4 |        17.7 |  4.0 |    0.61 |          5 |     0.75 | False |
| attrs              | tests                    |     1.9 |         1.4 |  0.7 |    0.16 |          2 |     0.19 | False |
| click              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| click              | fix-certain              |     2.4 |         3.9 |  1.6 |    0.31 |          2 |     0.39 | False |
| click              | fix-likely               |     2.0 |         4.0 |  2.0 |    0.31 |          2 |     0.39 | False |
| click              | fix-unsafe               |     2.7 |         4.3 |  1.6 |    0.31 |          2 |     0.39 | False |
| click              | infer-basedpyright       |     5.4 |         5.6 |  1.0 |     0.3 |          1 |     0.37 | False |
| click              | infer-ty                 |     5.2 |         5.0 |  1.0 |    0.32 |          1 |     0.27 | False |
| click              | infer-pyrefly            |     3.4 |         4.6 |  1.4 |    0.31 |          1 |     0.25 | False |
| click              | census                   |     2.2 |         1.8 |  0.8 |    0.18 |          1 |     0.22 | False |
| click              | coverage                 |     0.8 |         1.0 |  1.2 |    0.17 |          2 |     0.21 | False |
| click              | timing                   |     2.6 |         2.4 |  0.9 |    0.18 |          1 |     0.22 | False |
| click              | traced                   |     8.7 |        10.6 |  1.2 |     0.3 |          1 |     0.39 | False |
| click              | tests-released           |     8.6 |         6.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | infer-union              |     7.2 |         6.6 |  0.9 |    0.27 |          1 |     0.37 | False |
| click              | tests-infer-union        |    10.0 |         6.8 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     1.8 |         1.7 |  0.9 |    0.16 |          1 |     0.19 | False |
| click              | types-released           |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| click              | types-infer-basedpyright |     1.6 |         0.7 |  0.4 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-ty           |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-pyrefly      |     1.2 |         0.6 |  0.5 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-trace        |     1.0 |         0.6 |  0.6 |     0.1 |          1 |     0.12 | False |
| click              | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.22 | False |
| hypercorn          | fix-certain              |     1.8 |         3.3 |  1.8 |    0.26 |          2 |     0.32 | False |
| hypercorn          | fix-likely               |     2.6 |         3.9 |  1.5 |    0.26 |          2 |     0.32 | False |
| hypercorn          | fix-unsafe               |     3.4 |         4.0 |  1.2 |    0.27 |          1 |     0.32 | False |
| hypercorn          | infer-basedpyright       |     3.8 |         4.4 |  1.2 |    0.23 |          1 |     0.14 | False |
| hypercorn          | infer-ty                 |     2.2 |         3.7 |  1.7 |    0.27 |          1 |     0.32 | False |
| hypercorn          | infer-pyrefly            |     3.6 |         4.0 |  1.1 |    0.26 |          1 |     0.16 | False |
| hypercorn          | census                   |     1.4 |         1.4 |  1.0 |    0.18 |          2 |     0.22 | False |
| hypercorn          | coverage                 |     0.8 |         0.8 |  1.0 |    0.15 |          1 |     0.19 | False |
| hypercorn          | timing                   |     2.4 |         2.1 |  0.9 |    0.18 |          1 |     0.22 | False |
| hypercorn          | traced                   |    12.8 |         6.3 |  0.5 |    0.27 |          1 |     0.34 | False |
| hypercorn          | tests-released           |     9.2 |         1.6 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | infer-union              |     6.2 |         5.5 |  0.9 |    0.25 |          1 |     0.16 | False |
| hypercorn          | tests-infer-union        |     9.2 |         1.8 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests                    |     1.8 |         1.7 |  0.9 |    0.16 |          1 |     0.19 | False |
| hypercorn          | types-released           |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| hypercorn          | types-infer-basedpyright |     1.6 |         1.0 |  0.6 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-ty           |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.14 | False |
| hypercorn          | types-infer-pyrefly      |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.12 | False |
| hypercorn          | types-infer-trace        |     0.8 |         0.7 |  0.9 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     1.2 |         1.6 |  1.3 |    0.19 |          2 |     0.24 | False |
| starlette          | fix-certain              |     2.0 |         3.8 |  1.9 |    0.27 |          2 |     0.34 | False |
| starlette          | fix-likely               |     2.0 |         4.1 |  2.0 |    0.27 |          2 |     0.34 | False |
| starlette          | fix-unsafe               |     3.4 |         4.4 |  1.3 |    0.27 |          2 |     0.34 | False |
| starlette          | infer-basedpyright       |     5.4 |         5.6 |  1.0 |    0.26 |          1 |     0.15 | False |
| starlette          | infer-ty                 |     4.6 |         5.2 |  1.1 |    0.27 |          1 |     0.19 | False |
| starlette          | infer-pyrefly            |     4.8 |         5.0 |  1.0 |    0.31 |          1 |      0.4 | False |
| starlette          | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          2 |     0.24 | False |
| starlette          | coverage                 |     1.0 |         1.0 |  1.0 |    0.16 |          1 |      0.2 | False |
| starlette          | timing                   |     1.6 |         2.0 |  1.2 |    0.19 |          2 |     0.24 | False |
| starlette          | traced                   |    20.6 |        14.5 |  0.7 |    0.29 |          1 |     0.36 | False |
| starlette          | tests-released           |    19.9 |         7.6 |  0.4 |    0.22 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | infer-union              |     5.0 |         5.9 |  1.2 |    0.26 |          1 |     0.57 | False |
| starlette          | tests-infer-union        |    11.8 |         6.5 |  0.6 |    0.23 |          1 |     0.29 | False |
| starlette          | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          1 |     0.19 | False |
| starlette          | types-released           |     1.6 |         1.3 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| starlette          | types-infer-basedpyright |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.14 | False |
| starlette          | types-infer-ty           |     1.8 |         1.4 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-pyrefly      |     1.2 |         0.7 |  0.6 |    0.11 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     1.2 |         1.0 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.4 |         2.3 |  1.6 |    0.21 |          2 |     0.26 | False |
| werkzeug           | fix-certain              |     3.2 |         6.2 |  1.9 |    0.31 |          3 |     0.39 | False |
| werkzeug           | fix-likely               |     3.2 |         7.1 |  2.2 |    0.31 |          3 |     0.39 | False |
| werkzeug           | fix-unsafe               |     4.6 |         7.3 |  1.6 |    0.31 |          2 |     0.39 | False |
| werkzeug           | infer-basedpyright       |     6.2 |         8.5 |  1.4 |    0.27 |          1 |     0.72 | False |
| werkzeug           | infer-ty                 |     4.6 |         7.7 |  1.7 |    0.32 |          1 |     0.46 | False |
| werkzeug           | infer-pyrefly            |     5.8 |         8.1 |  1.4 |    0.31 |          1 |     0.66 | False |
| werkzeug           | census                   |     0.8 |         0.6 |  0.7 |    0.04 |          2 |     0.26 | False |
| werkzeug           | coverage                 |     1.0 |         1.3 |  1.3 |    0.18 |          2 |     0.22 | False |
| werkzeug           | timing                   |     2.4 |         3.0 |  1.2 |    0.21 |          2 |     0.26 | False |
| werkzeug           | traced                   |    12.1 |        14.8 |  1.2 |    0.34 |          1 |     0.41 | False |
| werkzeug           | tests-released           |    11.0 |         7.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| werkzeug           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| werkzeug           | infer-union              |     7.2 |         9.7 |  1.3 |    0.32 |          1 |     0.45 | False |
| werkzeug           | tests-infer-union        |    11.2 |         7.2 |  0.6 |    0.17 |          1 |     0.22 | False |
| werkzeug           | tests                    |     1.8 |         1.5 |  0.8 |    0.16 |          1 |     0.19 | False |
| werkzeug           | types-released           |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-infer-basedpyright |     1.8 |         1.1 |  0.6 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-ty           |     1.8 |         1.0 |  0.6 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-pyrefly      |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-trace        |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.12 | False |
| werkzeug           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     1.8 |         2.8 |  1.6 |    0.28 |          2 |     0.35 | False |
| mkdocs             | fix-certain              |     3.6 |         7.3 |  2.0 |    0.34 |          2 |     0.42 | False |
| mkdocs             | fix-likely               |     4.0 |         8.4 |  2.1 |    0.35 |          3 |     0.44 | False |
| mkdocs             | fix-unsafe               |     6.6 |         9.5 |  1.4 |    0.35 |          2 |     0.44 | False |
| mkdocs             | infer-basedpyright       |     9.2 |        10.8 |  1.2 |    0.33 |          1 |     0.76 | False |
| mkdocs             | infer-ty                 |     7.8 |         9.8 |  1.3 |    0.35 |          1 |     0.42 | False |
| mkdocs             | infer-pyrefly            |     8.2 |         9.7 |  1.2 |    0.35 |          1 |     0.47 | False |
| mkdocs             | census                   |     0.8 |         0.6 |  0.7 |    0.05 |          2 |     0.35 | False |
| mkdocs             | coverage                 |     1.0 |         1.5 |  1.5 |    0.19 |          2 |     0.24 | False |
| mkdocs             | timing                   |     6.0 |         5.1 |  0.8 |    0.28 |          1 |     0.35 | False |
| mkdocs             | traced                   |    19.0 |        14.3 |  0.8 |    0.38 |          1 |     0.45 | False |
| mkdocs             | tests-released           |    11.2 |         2.7 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    10.2 |        11.7 |  1.1 |    0.34 |          1 |     0.72 | False |
| mkdocs             | tests-infer-union        |    11.6 |         2.6 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     1.4 |         1.3 |  0.9 |    0.16 |          1 |     0.19 | False |
| httpx              | check                    |     1.4 |         1.4 |  1.0 |    0.19 |          1 |     0.24 | False |
| httpx              | fix-certain              |     1.6 |         3.0 |  1.9 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-likely               |     2.0 |         3.9 |  1.9 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-unsafe               |     2.3 |         3.8 |  1.7 |    0.27 |          2 |     0.34 | False |
| httpx              | infer-basedpyright       |     4.2 |         4.9 |  1.2 |    0.24 |          1 |     0.15 | False |
| httpx              | infer-ty                 |     4.6 |         4.7 |  1.0 |    0.27 |          1 |     0.17 | False |
| httpx              | infer-pyrefly            |     2.8 |         4.2 |  1.5 |    0.27 |          1 |     0.17 | False |
| httpx              | census                   |     0.8 |         0.4 |  0.5 |    0.04 |          1 |     0.24 | False |
| httpx              | coverage                 |     1.0 |         0.9 |  0.9 |    0.15 |          1 |     0.19 | False |
| httpx              | timing                   |     2.8 |         2.4 |  0.9 |    0.19 |          1 |     0.24 | False |
| httpx              | traced                   |    17.0 |        10.8 |  0.6 |    0.29 |          1 |     0.36 | False |
| httpx              | tests-released           |    11.0 |         6.4 |  0.6 |    0.23 |          1 |     0.27 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | infer-union              |     7.4 |         6.2 |  0.8 |    0.26 |          1 |     0.16 | False |
| httpx              | tests-infer-union        |    11.8 |         5.7 |  0.5 |    0.22 |          1 |     0.27 | False |
| httpx              | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |     0.19 | False |
| httpx              | types-released           |     8.0 |         6.4 |  0.8 |     0.2 |          1 |     0.27 | False |
| httpx              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| httpx              | types-infer-basedpyright |     8.6 |         6.2 |  0.7 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-ty           |     9.4 |         6.5 |  0.7 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-pyrefly      |     7.6 |         6.2 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-trace        |     8.7 |         6.4 |  0.7 |     0.2 |          1 |     0.25 | False |
| httpx              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     1.2 |         1.8 |  1.5 |     0.2 |          2 |     0.25 | False |
| black              | fix-certain              |     2.0 |         4.4 |  2.2 |    0.31 |          3 |     0.39 | False |
| black              | fix-likely               |     1.8 |         4.4 |  2.4 |    0.31 |          3 |     0.37 | False |
| black              | fix-unsafe               |     2.6 |         5.3 |  2.0 |    0.31 |          2 |     0.39 | False |
| black              | infer-basedpyright       |     4.4 |         6.3 |  1.4 |    0.27 |          1 |     0.41 | False |
| black              | infer-ty                 |     4.6 |         6.1 |  1.3 |    0.31 |          1 |     0.29 | False |
| black              | infer-pyrefly            |     4.8 |         5.9 |  1.2 |    0.31 |          1 |     0.41 | False |
| black              | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.25 | False |
| black              | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| black              | timing                   |     2.2 |         2.8 |  1.3 |     0.2 |          2 |     0.25 | False |
| black              | traced                   |    10.6 |        63.6 |  6.0 |    0.91 |          5 |     1.14 | False |
| black              | tests-released           |     6.2 |        37.8 |  6.1 |     0.8 |          8 |     0.94 | False |
| black              | tests-fix-certain        |     4.6 |        31.7 |  6.9 |    0.73 |          8 |     0.95 | False |
| black              | tests-fix-likely         |     6.6 |        39.8 |  6.0 |    0.75 |          8 |     0.95 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.95 | False |
| black              | tests-infer-basedpyright |     5.0 |        33.2 |  6.6 |    0.74 |          8 |     0.94 | False |
| black              | tests-infer-ty           |     5.2 |        34.6 |  6.7 |    0.77 |          8 |     0.92 | False |
| black              | tests-infer-pyrefly      |     8.4 |        46.3 |  5.5 |    0.76 |          8 |     0.95 | False |
| black              | tests-infer-trace        |     7.6 |        41.7 |  5.5 |    0.77 |          8 |     0.92 | False |
| black              | infer-union              |     4.2 |         7.0 |  1.7 |    0.26 |          1 |     0.27 | False |
| black              | tests-infer-union        |     6.6 |        43.7 |  6.6 |    0.76 |          8 |     0.96 | False |
| black              | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |     0.19 | False |
| fastapi            | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      0.3 | False |
| fastapi            | fix-certain              |     3.6 |         5.5 |  1.5 |    0.32 |          2 |      0.4 | False |
| fastapi            | fix-likely               |     5.6 |         7.7 |  1.4 |    0.43 |          2 |     0.54 | False |
| fastapi            | fix-unsafe               |     6.4 |         7.4 |  1.2 |    0.34 |          2 |     0.44 | False |
| fastapi            | infer-basedpyright       |     5.4 |         7.3 |  1.4 |    0.35 |          1 |     0.44 | False |
| fastapi            | infer-ty                 |     8.0 |         7.7 |  1.0 |    0.35 |          1 |     0.22 | False |
| fastapi            | infer-pyrefly            |     6.6 |         7.2 |  1.1 |    0.35 |          1 |     0.22 | False |
| fastapi            | census                   |     2.0 |         2.3 |  1.1 |    0.24 |          2 |      0.3 | False |
| fastapi            | coverage                 |     0.8 |         1.1 |  1.4 |    0.18 |          2 |     0.22 | False |
| fastapi            | timing                   |     2.4 |         2.6 |  1.1 |    0.24 |          2 |      0.3 | False |
| fastapi            | traced                   |    22.1 |       123.7 |  5.6 |    2.37 |          7 |     3.02 | False |
| fastapi            | tests-released           |    14.8 |        92.6 |  6.3 |    2.11 |          8 |     2.62 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| fastapi            | infer-union              |     5.6 |         7.9 |  1.4 |    0.36 |          2 |     0.44 | False |
| fastapi            | tests-infer-union        |    14.0 |        96.4 |  6.9 |    2.09 |          8 |     2.65 | False |
| fastapi            | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |     0.19 | False |
| cattrs             | check                    |     2.2 |         1.7 |  0.8 |     0.2 |          1 |     0.25 | False |
| cattrs             | fix-certain              |     2.2 |         3.4 |  1.5 |    0.26 |          2 |     0.32 | False |
| cattrs             | fix-likely               |     2.6 |         3.9 |  1.5 |    0.26 |          2 |     0.32 | False |
| cattrs             | fix-unsafe               |     2.6 |         3.9 |  1.5 |    0.26 |          2 |     0.32 | False |
| cattrs             | infer-basedpyright       |     5.4 |         5.2 |  1.0 |    0.23 |          1 |     0.16 | False |
| cattrs             | infer-ty                 |     3.6 |         4.6 |  1.3 |    0.26 |          1 |     0.32 | False |
| cattrs             | infer-pyrefly            |     4.6 |         4.7 |  1.0 |    0.29 |          1 |     0.17 | False |
| cattrs             | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.25 | False |
| cattrs             | coverage                 |     1.0 |         0.9 |  0.9 |    0.15 |          1 |     0.19 | False |
| cattrs             | timing                   |     2.6 |         2.3 |  0.9 |     0.2 |          1 |     0.25 | False |
| cattrs             | traced                   |    21.8 |       148.5 |  6.8 |    1.33 |          8 |     1.71 | False |
| cattrs             | tests-released           |    20.8 |       126.5 |  6.1 |    1.01 |          8 |     1.26 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | infer-union              |     3.8 |         5.3 |  1.4 |    0.24 |          1 |     0.29 | False |
| cattrs             | tests-infer-union        |    16.8 |       102.9 |  6.1 |    1.01 |          8 |     1.26 | False |
| cattrs             | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          1 |     0.19 | False |
| pytest             | check                    |     0.6 |         0.2 |  0.3 |    0.04 |          2 |     0.37 | False |
| pytest             | fix-certain              |     5.4 |        10.8 |  2.0 |     0.4 |          3 |      0.5 | False |
| pytest             | fix-likely               |     5.6 |        12.7 |  2.3 |    0.45 |          3 |     0.56 | False |
| pytest             | fix-unsafe               |    10.0 |        14.6 |  1.5 |     0.4 |          2 |      0.5 | False |
| pytest             | infer-basedpyright       |    30.4 |        58.5 |  1.9 |    1.81 |          1 |     0.77 | False |
| pytest             | infer-ty                 |    14.6 |        19.5 |  1.3 |    0.76 |          1 |     0.75 | False |
| pytest             | infer-pyrefly            |    16.2 |        30.9 |  1.9 |    1.27 |          1 |     0.69 | False |
| pytest             | census                   |     3.2 |         4.7 |  1.5 |     0.3 |          2 |     0.37 | False |
| pytest             | coverage                 |     1.0 |         2.0 |  2.0 |    0.22 |          2 |     0.27 | False |
| pytest             | timing                   |     5.4 |         7.0 |  1.3 |     0.3 |          2 |     0.37 | False |
| pytest             | traced                   |    53.8 |       323.1 |  6.0 |     1.8 |          8 |     2.24 | False |
| pytest             | tests-released           |    22.6 |       160.2 |  7.1 |    1.41 |          8 |     1.71 | False |
| pytest             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.76 | False |
| pytest             | infer-union              |    21.8 |        62.6 |  2.9 |    1.62 |          1 |     0.58 | False |
| pytest             | tests-infer-union        |    20.4 |       143.7 |  7.0 |    1.35 |          8 |     1.75 | False |
| pytest             | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |     0.19 | False |
| botocore           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.41 | False |
| botocore           | fix-certain              |     5.2 |        12.0 |  2.3 |    0.42 |          3 |     0.52 | False |
| botocore           | fix-likely               |     7.0 |        16.2 |  2.3 |    0.52 |          3 |     0.65 | False |
| botocore           | fix-unsafe               |    12.9 |        17.7 |  1.4 |    0.49 |          2 |     0.62 | False |
| botocore           | infer-basedpyright       |    14.6 |        20.6 |  1.4 |    0.54 |          1 |     0.82 | False |
| botocore           | infer-ty                 |    14.8 |        19.1 |  1.3 |    0.52 |          1 |     0.79 | False |
| botocore           | infer-pyrefly            |    12.2 |        19.1 |  1.6 |    0.52 |          1 |      0.8 | False |
| botocore           | census                   |     3.2 |         5.4 |  1.7 |    0.33 |          2 |     0.41 | False |
| botocore           | coverage                 |     1.2 |         1.8 |  1.5 |    0.21 |          2 |     0.26 | False |
| botocore           | timing                   |     5.4 |         7.7 |  1.4 |    0.33 |          2 |     0.41 | False |
| botocore           | traced                   |    38.6 |       118.6 |  3.1 |    5.19 |          5 |     6.42 | False |
| botocore           | tests-released           |    29.7 |        93.5 |  3.1 |    4.92 |          4 |     6.15 | False |
| botocore           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | infer-union              |    34.5 |        85.3 |  2.5 |    1.83 |          2 |     1.48 | False |
| botocore           | tests-infer-union        |    29.8 |        90.3 |  3.0 |    4.94 |          4 |     6.17 | False |
| botocore           | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          2 |     0.19 | False |
| uvicorn            | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.24 | False |
| uvicorn            | fix-certain              |     2.2 |         4.0 |  1.8 |    0.31 |          2 |     0.34 | False |
| uvicorn            | fix-likely               |     2.2 |         4.3 |  2.0 |    0.27 |          2 |     0.34 | False |
| uvicorn            | fix-unsafe               |     6.0 |         5.0 |  0.8 |    0.27 |          2 |     0.34 | False |
| uvicorn            | infer-basedpyright       |     3.6 |         5.3 |  1.5 |    0.23 |          1 |     0.29 | False |
| uvicorn            | infer-ty                 |     4.2 |         5.2 |  1.2 |    0.28 |          1 |     0.17 | False |
| uvicorn            | infer-pyrefly            |     5.0 |         5.4 |  1.1 |    0.27 |          1 |     0.17 | False |
| uvicorn            | census                   |     1.2 |         1.6 |  1.3 |    0.19 |          2 |     0.24 | False |
| uvicorn            | coverage                 |     1.0 |         0.9 |  0.9 |    0.16 |          1 |      0.2 | False |
| uvicorn            | timing                   |     1.8 |         2.2 |  1.2 |    0.19 |          2 |     0.24 | False |
| uvicorn            | traced                   |    32.8 |        28.8 |  0.9 |    0.95 |          1 |     1.19 | False |
| uvicorn            | tests-released           |    30.9 |        21.3 |  0.7 |    0.83 |          1 |     1.05 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | infer-union              |     4.4 |         6.0 |  1.4 |    0.25 |          1 |     0.16 | False |
| uvicorn            | tests-infer-union        |    40.8 |        22.5 |  0.6 |    0.79 |          1 |     1.01 | False |
| uvicorn            | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |     0.19 | False |
| uvicorn            | types-released           |     2.0 |         1.5 |  0.8 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| uvicorn            | types-infer-basedpyright |     2.8 |         1.6 |  0.6 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-ty           |     1.8 |         1.4 |  0.8 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-pyrefly      |     2.0 |         1.5 |  0.8 |    0.12 |          1 |     0.14 | False |
| uvicorn            | types-infer-trace        |     1.6 |         1.3 |  0.8 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.34 | False |
| mcp                | fix-certain              |     5.0 |         9.1 |  1.8 |    0.34 |          3 |     0.42 | False |
| mcp                | fix-likely               |     4.8 |        11.0 |  2.3 |    0.43 |          2 |     0.54 | False |
| mcp                | fix-unsafe               |     6.8 |        11.3 |  1.7 |    0.38 |          2 |     0.47 | False |
| mcp                | infer-basedpyright       |     7.6 |        12.1 |  1.6 |    0.43 |          1 |      0.8 | False |
| mcp                | infer-ty                 |     8.2 |        12.2 |  1.5 |    0.43 |          1 |     0.74 | False |
| mcp                | infer-pyrefly            |     8.6 |        12.1 |  1.4 |    0.43 |          1 |     0.79 | False |
| mcp                | census                   |     2.2 |         3.6 |  1.6 |    0.27 |          2 |     0.34 | False |
| mcp                | coverage                 |     1.2 |         1.6 |  1.3 |    0.19 |          2 |     0.24 | False |
| mcp                | timing                   |     3.2 |         4.1 |  1.3 |    0.27 |          2 |     0.34 | False |
| mcp                | traced                   |    27.5 |       104.5 |  3.8 |    2.07 |          4 |     2.59 | False |
| mcp                | tests-released           |    22.4 |        80.9 |  3.6 |    1.84 |          6 |     2.29 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | infer-union              |     8.6 |        14.4 |  1.7 |    0.44 |          1 |     0.43 | False |
| mcp                | tests-infer-union        |    14.8 |        68.8 |  4.6 |    1.79 |          5 |     2.24 | False |
| mcp                | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          1 |     0.19 | False |
| mcp                | types-released           |    40.4 |        31.4 |  0.8 |     1.2 |          2 |     1.57 | False |
| mcp                | types-fix-certain        |    19.2 |        27.3 |  1.4 |    1.28 |          2 |     1.54 | False |
| mcp                | types-fix-likely         |    16.4 |        24.8 |  1.5 |    1.26 |          2 |     1.57 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      1.6 | False |
| mcp                | types-infer-basedpyright |    18.0 |        26.0 |  1.4 |    1.26 |          2 |     1.62 | False |
| mcp                | types-infer-ty           |    16.0 |        24.6 |  1.5 |    1.25 |          2 |     1.59 | False |
| mcp                | types-infer-pyrefly      |    17.8 |        27.0 |  1.5 |    1.28 |          2 |     1.59 | False |
| mcp                | types-infer-trace        |    21.4 |        27.9 |  1.3 |    1.21 |          2 |     1.42 | False |
| mcp                | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     3.2 |         7.0 |  2.2 |    0.42 |          3 |     0.52 | False |
| textual            | fix-certain              |     5.8 |        15.6 |  2.7 |    0.54 |          3 |     0.62 | False |
| textual            | fix-likely               |     6.6 |        20.1 |  3.0 |    0.56 |          3 |      0.7 | False |
| textual            | fix-unsafe               |     7.0 |        20.3 |  2.9 |    0.54 |          3 |     0.67 | False |
| textual            | infer-basedpyright       |    45.1 |        89.7 |  2.0 |    1.85 |          1 |     1.15 | False |
| textual            | infer-ty                 |    21.4 |        38.2 |  1.8 |    1.21 |          1 |     1.11 | False |
| textual            | infer-pyrefly            |    14.0 |        25.7 |  1.8 |    0.56 |          1 |     0.94 | False |
| textual            | census                   |     1.4 |         1.2 |  0.9 |    0.07 |          3 |     0.52 | False |
| textual            | coverage                 |     1.2 |         2.9 |  2.4 |    0.25 |          3 |     0.31 | False |
| textual            | timing                   |     8.8 |        12.1 |  1.4 |    0.42 |          2 |     0.52 | False |
| pdm                | check                    |     2.4 |         4.1 |  1.7 |    0.47 |          2 |     0.59 | False |
| pdm                | fix-certain              |     7.0 |        13.4 |  1.9 |    0.51 |          2 |     0.64 | False |
| pdm                | fix-likely               |     8.2 |        16.6 |  2.0 |    0.57 |          2 |     0.71 | False |
| pdm                | fix-unsafe               |    11.8 |        17.2 |  1.5 |    0.55 |          2 |     0.69 | False |
| pdm                | infer-basedpyright       |    11.8 |        17.1 |  1.4 |    0.51 |          1 |     0.97 | False |
| pdm                | infer-ty                 |    15.8 |        18.9 |  1.2 |    0.56 |          1 |     0.96 | False |
| pdm                | infer-pyrefly            |    11.2 |        17.3 |  1.5 |    0.56 |          1 |     1.34 | False |
| pdm                | census                   |     0.6 |         0.5 |  0.8 |    0.05 |          2 |     0.59 | False |
| pdm                | coverage                 |     1.0 |         1.8 |  1.8 |    0.19 |          2 |     0.25 | False |
| pdm                | timing                   |     6.8 |         8.3 |  1.2 |    0.47 |          2 |     0.59 | False |
| pdm                | traced                   |    29.2 |       118.2 |  4.0 |    1.53 |          7 |     2.01 | False |
| pdm                | tests-released           |    20.4 |       101.5 |  5.0 |    1.22 |          8 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          7 |     1.52 | False |
| pdm                | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     1.52 | False |
| pdm                | infer-union              |    15.3 |        15.8 |  1.0 |    0.52 |          3 |     2.82 | False |
| pdm                | tests-infer-union        |    15.0 |        87.4 |  5.8 |    1.21 |          8 |     1.52 | False |
| pdm                | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          1 |     0.19 | False |
| strawberry-graphql | check                    |     2.6 |         4.5 |  1.7 |    0.38 |          2 |     0.47 | False |
| strawberry-graphql | fix-certain              |     5.8 |        12.3 |  2.1 |     0.5 |          3 |     0.62 | False |
| strawberry-graphql | fix-likely               |     7.4 |        16.3 |  2.2 |    0.64 |          3 |      0.8 | False |
| strawberry-graphql | fix-unsafe               |     9.2 |        15.9 |  1.7 |    0.54 |          2 |     0.67 | False |
| strawberry-graphql | infer-basedpyright       |    11.4 |        17.4 |  1.5 |    0.53 |          1 |     1.03 | False |
| strawberry-graphql | infer-ty                 |    11.2 |        16.7 |  1.5 |    0.53 |          1 |     0.96 | False |
| strawberry-graphql | infer-pyrefly            |     9.4 |        16.5 |  1.8 |    0.53 |          1 |     0.95 | False |
| strawberry-graphql | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.47 | False |
| strawberry-graphql | coverage                 |     1.0 |         1.8 |  1.8 |    0.19 |          2 |     0.24 | False |
| strawberry-graphql | timing                   |     5.6 |         7.8 |  1.4 |    0.38 |          2 |     0.47 | False |
| strawberry-graphql | traced                   |    32.6 |       104.6 |  3.2 |    1.51 |          6 |     1.86 | False |
| strawberry-graphql | tests-released           |    18.0 |        87.2 |  4.8 |     1.3 |          7 |     1.61 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | infer-union              |     8.2 |        14.5 |  1.8 |    0.54 |          2 |     1.43 | False |
| strawberry-graphql | tests-infer-union        |    17.2 |        90.3 |  5.2 |    1.25 |          7 |     1.55 | False |
| strawberry-graphql | tests                    |     1.0 |         0.8 |  0.8 |    0.16 |          1 |     0.19 | False |
| strawberry-graphql | types-released           |     2.0 |         1.6 |  0.8 |     0.2 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.32 | False |
| strawberry-graphql | types-infer-basedpyright |     3.8 |         2.1 |  0.6 |     0.2 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-ty           |     3.6 |         1.8 |  0.5 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-pyrefly      |     2.0 |         1.6 |  0.8 |    0.19 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| strawberry-graphql | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          3 |     0.52 | False |
| pygments           | fix-certain              |     7.4 |        20.5 |  2.8 |    0.54 |          3 |     0.62 | False |
| pygments           | fix-likely               |     9.2 |        25.6 |  2.8 |    0.63 |          3 |     0.79 | False |
| pygments           | fix-unsafe               |    12.0 |        26.7 |  2.2 |    0.62 |          3 |     0.77 | False |
| pygments           | infer-basedpyright       |    12.6 |        32.5 |  2.6 |    0.61 |          1 |     1.11 | False |
| pygments           | infer-ty                 |    19.6 |        31.5 |  1.6 |    0.63 |          1 |     0.99 | False |
| pygments           | infer-pyrefly            |    18.0 |        31.5 |  1.8 |    0.64 |          1 |     1.11 | False |
| pygments           | census                   |     5.6 |         9.8 |  1.8 |    0.42 |          3 |     0.52 | False |
| pygments           | coverage                 |     1.4 |         3.3 |  2.4 |    0.21 |          3 |     0.26 | False |
| pygments           | timing                   |     8.6 |        12.0 |  1.4 |    0.42 |          2 |     0.52 | False |
| pygments           | traced                   |    36.6 |        47.4 |  1.3 |    0.71 |          1 |     0.89 | False |
| pygments           | tests-released           |    21.8 |        15.8 |  0.7 |     0.3 |          1 |     0.35 | False |
| pygments           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| pygments           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.05 | False |
| pygments           | infer-union              |    22.0 |        41.2 |  1.9 |    0.72 |          1 |     0.99 | False |
| pygments           | tests-infer-union        |    16.0 |        13.9 |  0.9 |     0.3 |          1 |     0.31 | False |
| pygments           | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          1 |     0.19 | False |
| streamlink         | check                    |     2.4 |         5.8 |  2.4 |    0.34 |          3 |     0.42 | False |
| streamlink         | fix-certain              |     6.0 |        14.5 |  2.4 |    0.43 |          3 |     0.54 | False |
| streamlink         | fix-likely               |    11.2 |        19.1 |  1.7 |     0.5 |          3 |     0.62 | False |
| streamlink         | fix-unsafe               |     7.0 |        17.0 |  2.4 |    0.45 |          3 |     0.56 | False |
| streamlink         | infer-basedpyright       |     9.6 |        19.6 |  2.0 |    0.53 |          1 |     0.95 | False |
| streamlink         | infer-ty                 |    12.8 |        20.5 |  1.6 |     0.5 |          1 |     0.92 | False |
| streamlink         | infer-pyrefly            |    11.4 |        19.1 |  1.7 |     0.5 |          1 |     1.26 | False |
| streamlink         | census                   |     1.0 |         0.8 |  0.8 |    0.06 |          3 |     0.42 | False |
| streamlink         | coverage                 |     1.2 |         2.3 |  1.9 |    0.23 |          2 |     0.29 | False |
| streamlink         | timing                   |     6.0 |         9.1 |  1.5 |    0.34 |          2 |     0.42 | False |
| streamlink         | traced                   |    32.9 |        35.1 |  1.1 |    0.54 |          1 |     0.69 | False |
| streamlink         | tests-released           |    22.3 |        14.0 |  0.6 |    0.18 |          1 |     0.25 | False |
| streamlink         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | infer-union              |    13.4 |        23.8 |  1.8 |    0.57 |          1 |     0.89 | False |
| streamlink         | tests-infer-union        |    16.6 |        12.8 |  0.8 |     0.2 |          1 |     0.25 | False |
| streamlink         | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          1 |     0.19 | False |
| streamlink         | types-released           |    11.0 |         7.6 |  0.7 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          1 |     0.49 | False |
| streamlink         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.47 | False |
| streamlink         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.45 | False |
| streamlink         | types-infer-basedpyright |     5.8 |         5.3 |  0.9 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-ty           |     8.8 |         7.1 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |     7.6 |         6.4 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |     4.8 |         4.6 |  1.0 |    0.36 |          1 |     0.45 | False |
| streamlink         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     2.6 |         7.5 |  2.9 |    0.45 |          3 |     0.56 | False |
| sphinx             | fix-certain              |     9.0 |        28.0 |  3.1 |    0.64 |          3 |     0.74 | False |
| sphinx             | fix-likely               |    13.8 |        40.0 |  2.9 |     0.8 |          3 |     1.01 | False |
| sphinx             | fix-unsafe               |    13.9 |        36.8 |  2.6 |    0.71 |          3 |     0.89 | False |
| sphinx             | infer-basedpyright       |    39.7 |       102.9 |  2.6 |    2.31 |          1 |     1.28 | False |
| sphinx             | infer-ty                 |    20.2 |        50.6 |  2.5 |     2.0 |          1 |     1.26 | False |
| sphinx             | infer-pyrefly            |    21.8 |        49.6 |  2.3 |    2.38 |          1 |     1.49 | False |
| sphinx             | census                   |     2.2 |         2.0 |  0.9 |    0.07 |          3 |     0.56 | False |
| sphinx             | coverage                 |     1.4 |         3.4 |  2.4 |    0.27 |          3 |     0.34 | False |
| sphinx             | timing                   |    12.0 |        18.3 |  1.5 |    0.45 |          2 |     0.57 | False |
| sphinx             | traced                   |    33.5 |       159.9 |  4.8 |    1.67 |          7 |     2.09 | False |
| sphinx             | tests-released           |    16.4 |       115.4 |  7.0 |    1.35 |          8 |     1.69 | False |
| sphinx             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          8 |     1.66 | False |
| sphinx             | tests-fix-likely         |    18.0 |       110.6 |  6.1 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     1.69 | False |
| sphinx             | tests-infer-basedpyright |    16.6 |       110.8 |  6.7 |    1.32 |          8 |     1.66 | False |
| sphinx             | tests-infer-ty           |    16.6 |       115.6 |  7.0 |    1.33 |          8 |     1.67 | False |
| sphinx             | tests-infer-pyrefly      |    16.0 |       103.1 |  6.4 |    1.32 |          8 |     1.66 | False |
| sphinx             | tests-infer-trace        |    12.6 |        90.6 |  7.2 |    1.33 |          8 |     1.66 | False |
| sphinx             | infer-union              |    41.8 |       101.3 |  2.4 |    2.07 |          1 |     0.94 | False |
| sphinx             | tests-infer-union        |    14.6 |        96.6 |  6.6 |    1.35 |          8 |     1.66 | False |
| sphinx             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |     0.19 | False |
| sphinx             | types-released           |     4.6 |         4.2 |  0.9 |    0.26 |          1 |     0.34 | False |
| sphinx             | types-fix-certain        |     6.8 |         5.3 |  0.8 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-likely         |     6.4 |         5.1 |  0.8 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.42 | False |
| sphinx             | types-infer-basedpyright |     8.6 |         6.7 |  0.8 |    0.27 |          1 |     0.32 | False |
| sphinx             | types-infer-ty           |     8.2 |         6.4 |  0.8 |    0.26 |          1 |     0.32 | False |
| sphinx             | types-infer-pyrefly      |     7.4 |         5.7 |  0.8 |    0.26 |          1 |     0.36 | False |
| sphinx             | types-infer-trace        |     5.2 |         4.5 |  0.9 |    0.27 |          1 |     0.34 | False |
| sphinx             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     1.4 |         0.2 |  0.1 |    0.04 |          2 |     0.31 | False |
| tox                | fix-certain              |     3.8 |         8.0 |  2.1 |    0.33 |          3 |     0.41 | False |
| tox                | fix-likely               |     5.0 |        10.4 |  2.1 |    0.39 |          3 |     0.49 | False |
| tox                | fix-unsafe               |     4.6 |         9.9 |  2.2 |    0.35 |          2 |     0.44 | False |
| tox                | infer-basedpyright       |     7.6 |        11.3 |  1.5 |     0.4 |          1 |     0.84 | False |
| tox                | infer-ty                 |     3.6 |         8.9 |  2.5 |    0.35 |          1 |     0.22 | False |
| tox                | infer-pyrefly            |     8.2 |        10.9 |  1.3 |     0.4 |          1 |     0.25 | False |
| tox                | census                   |     2.2 |         3.4 |  1.5 |    0.25 |          2 |     0.31 | False |
| tox                | coverage                 |     1.0 |         1.4 |  1.4 |    0.18 |          2 |     0.22 | False |
| tox                | timing                   |     4.6 |         5.1 |  1.1 |    0.25 |          1 |     0.31 | False |
| tox                | traced                   |    27.0 |       143.9 |  5.3 |     1.6 |          5 |     1.89 | False |
| tox                | tests-released           |    17.8 |       104.5 |  5.9 |    1.36 |          8 |     1.67 | False |
| tox                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | tests-fix-unsafe         |     0.5 |         0.2 |  0.4 |    0.03 |          6 |     1.72 | False |
| tox                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.72 | False |
| tox                | infer-union              |     6.2 |        12.1 |  2.0 |     0.4 |          3 |      0.5 | False |
| tox                | tests-infer-union        |    28.4 |       122.9 |  4.3 |    1.35 |          6 |     1.72 | False |
| tox                | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          2 |     0.19 | False |
| pint               | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.51 | False |
| pint               | fix-certain              |     8.5 |        14.3 |  1.7 |    0.46 |          2 |     0.57 | False |
| pint               | fix-likely               |    10.4 |        18.7 |  1.8 |    0.52 |          2 |     0.65 | False |
| pint               | fix-unsafe               |     9.0 |        17.7 |  2.0 |    0.52 |          2 |     0.65 | False |
| pint               | infer-basedpyright       |    15.2 |        19.6 |  1.3 |    0.53 |          1 |     1.52 | False |
| pint               | infer-ty                 |    14.5 |        18.6 |  1.3 |    0.52 |          1 |     1.27 | False |
| pint               | infer-pyrefly            |    11.0 |        17.3 |  1.6 |    0.52 |          1 |     0.82 | False |
| pint               | census                   |     4.0 |         6.1 |  1.5 |    0.41 |          2 |     0.51 | False |
| pint               | coverage                 |     1.0 |         1.9 |  1.9 |    0.22 |          2 |     0.27 | False |
| pint               | timing                   |     5.4 |         7.4 |  1.4 |    0.41 |          2 |     0.51 | False |
| pint               | traced                   |    55.1 |        51.8 |  0.9 |    0.54 |          1 |     0.67 | False |
| pint               | tests-released           |    64.4 |        32.8 |  0.5 |    0.15 |          1 |     0.19 | False |
| pint               | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | infer-union              |    14.2 |        21.8 |  1.5 |    0.53 |          1 |     1.31 | False |
| pint               | tests-infer-union        |    41.6 |        31.6 |  0.8 |    0.15 |          1 |     0.19 | False |
| pint               | tests                    |     1.8 |         1.5 |  0.8 |    0.16 |          1 |     0.19 | False |
| pint               | types-released           |    15.2 |        12.7 |  0.8 |    0.52 |          1 |     0.66 | False |
| pint               | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-unsafe         |     7.8 |        10.9 |  1.4 |    0.54 |          2 |     0.69 | False |
| pint               | types-infer-basedpyright |     6.4 |         9.9 |  1.5 |    0.56 |          2 |     0.66 | False |
| pint               | types-infer-ty           |     4.8 |         8.7 |  1.8 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-pyrefly      |     7.4 |        10.6 |  1.4 |    0.54 |          2 |     0.69 | False |
| pint               | types-infer-trace        |     7.2 |        10.9 |  1.5 |    0.54 |          2 |     0.69 | False |
| pint               | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.02 | False |
| altair             | fix-certain              |    26.6 |        26.3 |  1.0 |    0.93 |          1 |     1.16 | False |
| altair             | fix-likely               |    21.8 |        27.0 |  1.2 |    1.03 |          2 |     1.29 | False |
| altair             | fix-unsafe               |    37.8 |        27.5 |  0.7 |    1.02 |          1 |     1.29 | False |
| altair             | infer-basedpyright       |    27.8 |        29.8 |  1.1 |    0.98 |          1 |     1.45 | False |
| altair             | infer-ty                 |    30.8 |        29.9 |  1.0 |    0.94 |          1 |     2.04 | False |
| altair             | infer-pyrefly            |    30.6 |        31.8 |  1.0 |    1.04 |          1 |     1.12 | False |
| altair             | census                   |     8.0 |         9.9 |  1.2 |    0.82 |          2 |     1.02 | False |
| altair             | coverage                 |     1.0 |         2.0 |  2.0 |    0.28 |          3 |     0.35 | False |
| altair             | timing                   |    12.6 |        14.4 |  1.1 |    0.82 |          2 |     1.02 | False |
| altair             | traced                   |    32.2 |       169.3 |  5.3 |     5.4 |          6 |     6.67 | False |
| altair             | tests-released           |    22.4 |       134.0 |  6.0 |    4.98 |          8 |     5.87 | False |
| altair             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     5.71 | False |
| altair             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.56 | False |
| altair             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.89 | False |
| altair             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     6.04 | False |
| altair             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.85 | False |
| altair             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.84 | False |
| altair             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.95 | False |
| altair             | infer-union              |    42.9 |        29.1 |  0.7 |     1.1 |          1 |     0.94 | False |
| altair             | tests-infer-union        |    24.2 |       134.9 |  5.6 |    4.57 |          8 |      6.0 | False |
| altair             | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          2 |     0.19 | False |
| altair             | types-released           |     7.6 |         6.1 |  0.8 |    0.38 |          1 |     0.47 | False |
| altair             | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.47 | False |
| altair             | types-fix-likely         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.49 | False |
| altair             | types-fix-unsafe         |     6.6 |         3.8 |  0.6 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-basedpyright |     7.4 |         6.3 |  0.9 |    0.39 |          1 |     0.47 | False |
| altair             | types-infer-ty           |     7.4 |         6.0 |  0.8 |    0.38 |          1 |      0.5 | False |
| altair             | types-infer-pyrefly      |     8.0 |         6.0 |  0.8 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-trace        |     9.4 |         4.8 |  0.5 |    0.38 |          1 |     0.49 | False |
| altair             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| seaborn            | check                    |     5.0 |         8.0 |  1.6 |    0.75 |          2 |     0.94 | False |
| seaborn            | fix-certain              |    15.1 |        21.0 |  1.4 |    0.91 |          2 |     1.14 | False |
| seaborn            | fix-likely               |    22.2 |        31.7 |  1.4 |    1.01 |          2 |     1.26 | False |
| seaborn            | fix-unsafe               |    22.6 |        28.4 |  1.3 |    0.94 |          2 |     1.19 | False |
| seaborn            | infer-basedpyright       |    22.6 |        31.0 |  1.4 |     1.0 |          1 |     1.25 | False |
| seaborn            | infer-ty                 |    20.6 |        29.0 |  1.4 |    0.91 |          1 |     0.99 | False |
| seaborn            | infer-pyrefly            |    43.8 |        40.8 |  0.9 |    1.95 |          1 |     1.22 | False |
| seaborn            | census                   |     4.0 |         0.6 |  0.1 |    0.05 |          2 |     0.94 | False |
| seaborn            | coverage                 |     1.0 |         1.6 |  1.6 |     0.2 |          2 |     0.25 | False |
| seaborn            | timing                   |    10.4 |        12.9 |  1.2 |    0.75 |          2 |     0.94 | False |
| seaborn            | traced                   |    53.2 |       429.9 |  8.1 |    3.67 |          8 |     4.64 | False |
| seaborn            | tests-released           |    39.1 |       382.4 |  9.8 |    3.48 |          8 |     4.39 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-fix-unsafe         |     0.6 |         0.4 |  0.7 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| seaborn            | infer-union              |    77.0 |       127.7 |  1.7 |    2.47 |          1 |     1.47 | False |
| seaborn            | tests-infer-union        |    48.2 |       395.4 |  8.2 |     3.4 |          8 |     4.16 | False |
| seaborn            | tests                    |     1.0 |         0.9 |  0.9 |    0.16 |          2 |     0.19 | False |
| seaborn            | types-released           |     1.6 |         1.2 |  0.7 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| seaborn            | types-fix-likely         |     1.6 |         1.1 |  0.7 |    0.16 |          1 |      0.2 | False |
| seaborn            | types-fix-unsafe         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.21 | False |
| seaborn            | types-infer-basedpyright |     1.6 |         1.1 |  0.7 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-ty           |     1.6 |         1.2 |  0.7 |    0.16 |          1 |     0.19 | False |
| seaborn            | types-infer-pyrefly      |     2.2 |         1.2 |  0.5 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-trace        |     1.3 |         1.1 |  0.8 |    0.16 |          1 |      0.2 | False |
| seaborn            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.31 | False |
| aiohttp            | fix-certain              |     4.4 |         9.0 |  2.0 |    0.35 |          2 |     0.44 | False |
| aiohttp            | fix-likely               |     9.4 |        13.3 |  1.4 |    0.43 |          3 |     0.54 | False |
| aiohttp            | fix-unsafe               |     5.4 |        11.4 |  2.1 |    0.36 |          2 |     0.45 | False |
| aiohttp            | infer-basedpyright       |    29.4 |        49.5 |  1.7 |    1.36 |          1 |      0.9 | False |
| aiohttp            | infer-ty                 |    10.6 |        17.1 |  1.6 |    0.71 |          1 |     0.61 | False |
| aiohttp            | infer-pyrefly            |     7.6 |        15.5 |  2.0 |    0.97 |          1 |     0.61 | False |
| aiohttp            | census                   |     2.6 |         3.9 |  1.5 |    0.25 |          2 |     0.31 | False |
| aiohttp            | coverage                 |     1.0 |         1.7 |  1.7 |    0.19 |          2 |     0.25 | False |
| aiohttp            | timing                   |    10.8 |         6.7 |  0.6 |    0.25 |          2 |     0.31 | False |
| aiohttp            | traced                   |   101.5 |       726.4 |  7.2 |    2.99 |          1 |     3.71 | False |
| aiohttp            | tests-released           |    98.4 |       643.0 |  6.5 |    2.58 |          1 |     3.24 | False |
| aiohttp            | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.26 | False |
| aiohttp            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.26 | False |
| aiohttp            | infer-union              |    35.7 |        59.9 |  1.7 |    1.16 |          1 |      0.5 | False |
| aiohttp            | tests-infer-union        |    95.7 |       627.0 |  6.6 |    2.59 |          1 |     3.26 | False |
| aiohttp            | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |     0.19 | False |
| websockets         | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.26 | False |
| websockets         | fix-certain              |     2.2 |         4.8 |  2.2 |     0.3 |          2 |     0.41 | False |
| websockets         | fix-likely               |     3.0 |         6.1 |  2.0 |     0.3 |          2 |     0.37 | False |
| websockets         | fix-unsafe               |     6.8 |         6.5 |  1.0 |     0.3 |          2 |     0.36 | False |
| websockets         | infer-basedpyright       |     6.2 |         8.0 |  1.3 |    0.29 |          1 |     0.36 | False |
| websockets         | infer-ty                 |     4.2 |         6.6 |  1.6 |     0.3 |          1 |     0.18 | False |
| websockets         | infer-pyrefly            |     5.4 |         7.0 |  1.3 |    0.35 |          1 |     0.19 | False |
| websockets         | census                   |     1.6 |         2.2 |  1.4 |    0.21 |          2 |     0.26 | False |
| websockets         | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| websockets         | timing                   |     2.2 |         2.9 |  1.3 |    0.21 |          2 |     0.26 | False |
| websockets         | traced                   |    32.4 |        13.3 |  0.4 |    0.33 |          1 |     0.42 | False |
| websockets         | tests-released           |    32.6 |         5.6 |  0.2 |    0.14 |          1 |     0.17 | False |
| websockets         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| websockets         | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | infer-union              |     5.0 |         8.0 |  1.6 |    0.28 |          1 |     0.17 | False |
| websockets         | tests-infer-union        |    29.7 |         5.6 |  0.2 |    0.15 |          1 |     0.19 | False |
| websockets         | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          1 |     0.19 | False |
| websockets         | types-released           |     1.4 |         0.8 |  0.6 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-certain        |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-likely         |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| websockets         | types-infer-basedpyright |     1.4 |         0.9 |  0.6 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-ty           |     0.8 |         0.7 |  0.9 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-trace        |     1.2 |         0.8 |  0.7 |    0.11 |          1 |     0.14 | False |
| websockets         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.26 | False |
| anyio              | fix-certain              |     4.4 |         6.1 |  1.4 |    0.29 |          2 |     0.37 | False |
| anyio              | fix-likely               |     7.0 |         7.8 |  1.1 |     0.3 |          1 |     0.37 | False |
| anyio              | fix-unsafe               |     8.8 |         7.4 |  0.8 |     0.3 |          2 |     0.37 | False |
| anyio              | infer-basedpyright       |     6.2 |         7.6 |  1.2 |     0.3 |          1 |     0.62 | False |
| anyio              | infer-ty                 |     8.8 |         8.6 |  1.0 |    0.34 |          1 |     0.42 | False |
| anyio              | infer-pyrefly            |     4.3 |         7.0 |  1.6 |     0.3 |          1 |     0.61 | False |
| anyio              | census                   |     1.8 |         2.4 |  1.3 |    0.21 |          2 |     0.26 | False |
| anyio              | coverage                 |     1.0 |         1.1 |  1.1 |    0.17 |          1 |     0.21 | False |
| anyio              | timing                   |     2.8 |         3.2 |  1.1 |    0.21 |          2 |     0.26 | False |
| anyio              | traced                   |   113.4 |        57.1 |  0.5 |    0.41 |          1 |     0.44 | False |
| anyio              | tests-released           |   119.3 |        48.2 |  0.4 |    0.26 |          1 |     0.34 | False |
| anyio              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.34 | False |
| anyio              | infer-union              |     8.2 |         9.2 |  1.1 |    0.34 |          1 |     1.05 | False |
| anyio              | tests-infer-union        |    96.0 |        45.1 |  0.5 |    0.27 |          1 |     0.34 | False |
| anyio              | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          1 |     0.19 | False |
| zarr               | check                    |     2.0 |         0.1 |  0.1 |    0.04 |          2 |      0.4 | False |
| zarr               | fix-certain              |    11.8 |        12.8 |  1.1 |     0.4 |          2 |      0.5 | False |
| zarr               | fix-likely               |     8.8 |        16.6 |  1.9 |    0.54 |          2 |     0.69 | False |
| zarr               | fix-unsafe               |    13.2 |        15.8 |  1.2 |    0.45 |          2 |     0.56 | False |
| zarr               | infer-basedpyright       |    27.8 |        79.4 |  2.9 |    2.04 |          1 |     0.91 | False |
| zarr               | infer-ty                 |    10.4 |        22.8 |  2.2 |    1.38 |          1 |     0.57 | False |
| zarr               | infer-pyrefly            |    17.4 |        35.1 |  2.0 |    1.96 |          1 |     0.82 | False |
| zarr               | census                   |     2.8 |         4.6 |  1.6 |    0.32 |          2 |      0.4 | False |
| zarr               | coverage                 |     1.2 |         1.8 |  1.5 |     0.2 |          2 |     0.25 | False |
| zarr               | timing                   |     4.8 |         6.7 |  1.4 |    0.32 |          2 |      0.4 | False |
| zarr               | traced                   |   138.4 |       267.7 |  1.9 |    2.56 |          2 |     3.34 | False |
| zarr               | tests-released           |   115.0 |       212.3 |  1.8 |    2.41 |          3 |      3.0 | False |
| zarr               | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     3.01 | False |
| zarr               | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.04 |          4 |     3.04 | False |
| zarr               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      2.9 | False |
| zarr               | tests-infer-basedpyright |    90.5 |       209.5 |  2.3 |    2.34 |          3 |     3.07 | False |
| zarr               | tests-infer-ty           |    99.5 |       223.0 |  2.2 |    2.39 |          3 |     2.91 | False |
| zarr               | tests-infer-pyrefly      |   122.7 |       226.7 |  1.8 |    2.38 |          2 |      2.9 | False |
| zarr               | tests-infer-trace        |   129.5 |       226.6 |  1.7 |    2.42 |          3 |     2.89 | False |
| zarr               | infer-union              |    41.1 |        93.6 |  2.3 |    1.63 |          1 |     0.62 | False |
| zarr               | tests-infer-union        |   134.2 |       239.7 |  1.8 |    2.33 |          2 |     2.99 | False |
| zarr               | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |     0.19 | False |
| joblib             | check                    |     0.2 |         0.2 |  1.0 |    0.04 |          2 |     0.45 | False |
| joblib             | fix-certain              |     5.8 |         9.9 |  1.7 |    0.42 |          2 |     0.52 | False |
| joblib             | fix-likely               |     6.0 |        11.2 |  1.9 |    0.45 |          2 |     0.56 | False |
| joblib             | fix-unsafe               |     8.6 |        12.1 |  1.4 |    0.45 |          2 |     0.57 | False |
| joblib             | infer-basedpyright       |    16.8 |        14.4 |  0.9 |    0.45 |          1 |     2.25 | False |
| joblib             | infer-ty                 |     7.4 |        12.2 |  1.6 |    0.45 |          1 |     0.28 | False |
| joblib             | infer-pyrefly            |    10.2 |        13.3 |  1.3 |    0.45 |          1 |     0.56 | False |
| joblib             | census                   |     2.4 |         3.7 |  1.5 |    0.36 |          2 |     0.45 | False |
| joblib             | coverage                 |     1.0 |         1.4 |  1.4 |    0.19 |          2 |     0.25 | False |
| joblib             | timing                   |     4.8 |         6.2 |  1.3 |    0.36 |          2 |     0.45 | False |
| joblib             | traced                   |   188.3 |       496.8 |  2.6 |    1.12 |          1 |      1.4 | False |
| joblib             | tests-released           |   157.3 |       487.9 |  3.1 |    1.08 |          1 |     1.36 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-unsafe         |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.32 | False |
| joblib             | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-infer-pyrefly      |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.34 | False |
| joblib             | infer-union              |     8.8 |        14.0 |  1.6 |    0.49 |          1 |     1.02 | False |
| joblib             | tests-infer-union        |   168.8 |       492.6 |  2.9 |     1.1 |          1 |     1.34 | False |
| joblib             | tests                    |     1.7 |         1.6 |  0.9 |    0.16 |          1 |     0.19 | False |
| networkx           | check                    |     0.6 |         0.4 |  0.7 |    0.07 |          2 |     1.67 | False |
| networkx           | fix-certain              |    45.6 |        76.9 |  1.7 |     1.6 |          2 |      2.0 | False |
| networkx           | fix-likely               |    51.9 |       113.8 |  2.2 |    2.14 |          2 |     2.66 | False |
| networkx           | fix-unsafe               |    71.3 |       119.3 |  1.7 |    2.13 |          2 |     2.66 | False |
| networkx           | infer-basedpyright       |    54.5 |       110.9 |  2.0 |    2.08 |          1 |     2.83 | False |
| networkx           | infer-ty                 |    47.8 |       102.6 |  2.1 |    2.06 |          1 |     1.29 | False |
| networkx           | infer-pyrefly            |    63.1 |       109.5 |  1.7 |    2.06 |          1 |     2.67 | False |
| networkx           | census                   |    16.5 |        31.9 |  1.9 |    1.34 |          2 |     1.67 | False |
| networkx           | coverage                 |     2.2 |         5.7 |  2.6 |     0.4 |          3 |      0.5 | False |
| networkx           | timing                   |    82.3 |        70.5 |  0.9 |    1.34 |          2 |     1.67 | False |
| networkx           | traced                   |    44.8 |       256.7 |  5.7 |    2.59 |          7 |     3.27 | False |
| networkx           | tests-released           |    29.5 |       236.9 |  8.0 |    2.39 |          8 |     2.94 | False |
| networkx           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      3.0 | False |
| networkx           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.02 | False |
| networkx           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.99 | False |
| networkx           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | infer-union              |   178.3 |       311.5 |  1.7 |    3.75 |          1 |     1.21 | False |
| networkx           | tests-infer-union        |    27.2 |       232.1 |  8.5 |    2.37 |          8 |     2.96 | False |
| networkx           | tests                    |     1.0 |         0.9 |  0.9 |    0.16 |          1 |     0.19 | False |
| networkx           | types-released           |     3.5 |         3.0 |  0.9 |     0.3 |          1 |     0.39 | False |
| networkx           | types-fix-certain        |     0.6 |         0.3 |  0.5 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-likely         |     0.8 |         0.4 |  0.5 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-unsafe         |     0.8 |         0.4 |  0.5 |    0.05 |          1 |      0.4 | False |
| networkx           | types-infer-basedpyright |     5.8 |         3.8 |  0.7 |    0.33 |          1 |     0.41 | False |
| networkx           | types-infer-ty           |     3.8 |         3.2 |  0.8 |    0.29 |          1 |     0.36 | False |
| networkx           | types-infer-pyrefly      |     3.8 |         3.4 |  0.9 |    0.31 |          1 |     0.39 | False |
| networkx           | types-infer-trace        |     3.8 |         2.8 |  0.7 |    0.29 |          1 |     0.36 | False |
| networkx           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| nibabel            | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          3 |     0.77 | False |
| nibabel            | fix-certain              |    20.6 |        28.9 |  1.4 |    0.73 |          2 |     0.91 | False |
| nibabel            | fix-likely               |    30.6 |        40.5 |  1.3 |    0.96 |          2 |      1.2 | False |
| nibabel            | fix-unsafe               |    23.5 |        36.4 |  1.5 |    0.87 |          2 |     1.09 | False |
| nibabel            | infer-basedpyright       |    29.6 |        43.8 |  1.5 |    0.98 |          1 |     1.55 | False |
| nibabel            | infer-ty                 |    21.4 |        40.1 |  1.9 |    0.96 |          1 |      0.6 | False |
| nibabel            | infer-pyrefly            |    16.8 |        38.1 |  2.3 |    0.98 |          1 |     0.61 | False |
| nibabel            | census                   |     9.8 |        13.6 |  1.4 |    0.62 |          3 |     0.77 | False |
| nibabel            | coverage                 |     1.6 |         3.0 |  1.9 |    0.25 |          2 |     0.31 | False |
| nibabel            | timing                   |    13.4 |        19.5 |  1.5 |    0.62 |          2 |     0.77 | False |
| nibabel            | traced                   |    37.8 |       127.1 |  3.4 |    1.17 |          6 |     1.45 | False |
| nibabel            | tests-released           |    11.4 |        85.2 |  7.5 |    1.04 |          5 |      1.3 | False |
| nibabel            | tests-fix-certain        |    17.6 |        85.3 |  4.8 |    1.03 |          7 |     1.29 | False |
| nibabel            | tests-fix-likely         |    14.6 |        89.5 |  6.1 |    1.03 |          8 |      1.3 | False |
| nibabel            | tests-fix-unsafe         |    15.8 |        94.8 |  6.0 |    1.03 |          7 |     1.31 | False |
| nibabel            | tests-infer-basedpyright |    14.2 |        97.2 |  6.8 |    1.04 |          8 |     1.31 | False |
| nibabel            | tests-infer-ty           |    15.4 |        91.7 |  6.0 |    1.04 |          8 |     1.32 | False |
| nibabel            | tests-infer-pyrefly      |    13.8 |        86.7 |  6.3 |    1.04 |          8 |     1.32 | False |
| nibabel            | tests-infer-trace        |    13.6 |        84.9 |  6.2 |    1.03 |          8 |      1.3 | False |
| nibabel            | infer-union              |    18.3 |        42.5 |  2.3 |    1.03 |          2 |     1.74 | False |
| nibabel            | tests-infer-union        |    15.2 |        90.3 |  5.9 |    1.03 |          8 |     1.29 | False |
| nibabel            | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          8 |     1.41 | False |
| nibabel            | types-released           |     2.0 |         1.8 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-fix-certain        |     2.6 |         2.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-fix-likely         |     1.6 |         1.5 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-fix-unsafe         |     2.8 |         1.5 |  0.5 |    0.14 |          1 |     0.17 | False |
| nibabel            | types-infer-basedpyright |     2.8 |         2.4 |  0.9 |    0.16 |          1 |     0.21 | False |
| nibabel            | types-infer-ty           |     4.4 |         2.7 |  0.6 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-infer-pyrefly      |     2.6 |         2.2 |  0.8 |    0.17 |          1 |      0.2 | False |
| nibabel            | types-infer-trace        |     2.7 |         2.3 |  0.9 |    0.17 |          1 |     0.21 | False |
| nibabel            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | check                    |     3.2 |         7.5 |  2.3 |    0.51 |          2 |     0.64 | False |
| narwhals           | fix-certain              |    17.2 |        22.8 |  1.3 |    0.51 |          2 |     0.64 | False |
| narwhals           | fix-likely               |    21.2 |        36.9 |  1.7 |    1.02 |          2 |     1.27 | False |
| narwhals           | fix-unsafe               |    17.2 |        35.2 |  2.0 |    1.02 |          2 |     1.27 | False |
| narwhals           | infer-basedpyright       |    20.2 |        34.8 |  1.7 |    1.03 |          1 |     1.38 | False |
| narwhals           | infer-ty                 |    24.8 |        50.6 |  2.0 |    2.54 |          1 |     1.57 | False |
| narwhals           | infer-pyrefly            |    24.8 |        51.3 |  2.1 |    3.12 |          1 |      1.3 | False |
| narwhals           | census                   |     0.8 |         0.7 |  0.9 |    0.05 |          2 |     0.64 | False |
| narwhals           | coverage                 |     1.0 |         2.4 |  2.4 |     0.2 |          3 |     0.25 | False |
| narwhals           | timing                   |    10.8 |        15.5 |  1.4 |    0.51 |          2 |     0.64 | False |
| narwhals           | traced                   |    34.6 |       194.4 |  5.6 |    4.95 |          7 |     6.32 | False |
| narwhals           | tests-released           |    42.4 |       197.4 |  4.7 |    4.03 |          7 |     5.69 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | infer-union              |    37.5 |       123.4 |  3.3 |    2.84 |          4 |      3.6 | False |
| narwhals           | tests-infer-union        |    47.7 |       149.6 |  3.1 |    4.73 |          7 |     5.76 | False |
| narwhals           | tests                    |     1.2 |         1.0 |  0.8 |    0.17 |          2 |      0.2 | False |
| narwhals           | types-released           |    34.7 |        60.5 |  1.7 |    1.55 |          2 |     1.95 | False |
| narwhals           | types-fix-certain        |    32.6 |        49.4 |  1.5 |     1.6 |          3 |     1.99 | False |
| narwhals           | types-fix-likely         |    20.8 |        42.7 |  2.1 |    1.61 |          2 |     1.95 | False |
| narwhals           | types-fix-unsafe         |     0.8 |         0.3 |  0.4 |    0.04 |          2 |     1.91 | False |
| narwhals           | types-infer-basedpyright |    20.2 |        46.2 |  2.3 |    1.61 |          3 |     1.97 | False |
| narwhals           | types-infer-ty           |    26.2 |        54.4 |  2.1 |     1.6 |          3 |     2.36 | False |
| narwhals           | types-infer-pyrefly      |    23.0 |        49.0 |  2.1 |    1.59 |          3 |      2.0 | False |
| narwhals           | types-infer-trace        |    19.2 |        39.1 |  2.0 |    1.61 |          2 |     1.96 | False |
| narwhals           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| xarray             | check                    |    16.4 |        36.2 |  2.2 |    1.37 |          2 |     1.71 | False |
| xarray             | fix-certain              |    66.2 |       101.2 |  1.5 |    1.87 |          2 |     2.34 | False |
| xarray             | fix-likely               |    79.5 |       136.7 |  1.7 |    2.46 |          2 |     3.07 | False |
| xarray             | fix-unsafe               |    89.8 |       140.1 |  1.6 |    2.44 |          2 |     3.05 | False |
| xarray             | infer-basedpyright       |   265.6 |       412.5 |  1.6 |    5.71 |          1 |     3.55 | False |
| xarray             | infer-ty                 |    87.5 |       194.6 |  2.2 |    4.69 |          1 |     1.97 | False |
| xarray             | infer-pyrefly            |    82.5 |       136.2 |  1.7 |    2.44 |          1 |     2.18 | False |
| xarray             | census                   |     5.2 |         5.0 |  1.0 |    0.15 |          2 |     1.71 | False |
| xarray             | coverage                 |     2.6 |         7.0 |  2.7 |    0.45 |          3 |     0.57 | False |
| xarray             | timing                   |    50.4 |        69.3 |  1.4 |    1.37 |          2 |     1.71 | False |
| xarray             | traced                   |    65.4 |       212.8 |  3.3 |     2.5 |          5 |     3.12 | False |
| xarray             | tests-released           |    28.4 |       107.3 |  3.8 |    1.98 |          8 |     2.49 | False |
| xarray             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | infer-union              |   319.9 |       697.1 |  2.2 |    4.03 |          1 |     1.94 | False |
| xarray             | tests-infer-union        |    15.0 |        93.0 |  6.2 |    1.96 |          5 |     2.45 | False |
| xarray             | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          2 |     0.19 | False |
| litestar           | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.55 | False |
| litestar           | fix-certain              |     8.6 |        16.5 |  1.9 |    0.67 |          2 |     0.84 | False |
| litestar           | fix-likely               |    11.8 |        21.7 |  1.8 |    0.92 |          2 |     1.15 | False |
| litestar           | fix-unsafe               |    12.0 |        20.4 |  1.7 |    0.73 |          2 |      0.9 | False |
| litestar           | infer-basedpyright       |    12.2 |        21.8 |  1.8 |    0.72 |          1 |     1.12 | False |
| litestar           | infer-ty                 |    15.8 |        22.4 |  1.4 |    0.72 |          1 |     1.08 | False |
| litestar           | infer-pyrefly            |    11.8 |        20.7 |  1.8 |    0.71 |          1 |     1.51 | False |
| litestar           | census                   |     3.4 |         6.1 |  1.8 |    0.44 |          2 |     0.55 | False |
| litestar           | coverage                 |     1.2 |         2.2 |  1.8 |     0.2 |          2 |     0.25 | False |
| litestar           | timing                   |     6.0 |         8.2 |  1.4 |    0.44 |          2 |     0.55 | False |
| litestar           | traced                   |    29.6 |       142.1 |  4.8 |    4.24 |          7 |     5.36 | False |
| litestar           | tests-released           |    37.0 |       154.7 |  4.2 |    3.94 |          6 |     4.84 | False |
| litestar           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.79 | False |
| litestar           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.76 | False |
| litestar           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.81 | False |
| litestar           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     4.64 | False |
| litestar           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      4.8 | False |
| litestar           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     4.81 | False |
| litestar           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.67 | False |
| litestar           | infer-union              |    12.4 |        22.3 |  1.8 |    0.73 |          1 |     0.77 | False |
| litestar           | tests-infer-union        |    23.0 |       123.7 |  5.4 |    3.78 |          8 |     4.92 | False |
| litestar           | tests                    |     1.0 |         0.8 |  0.8 |    0.16 |          1 |     0.19 | False |
| litestar           | types-released           |    49.8 |        71.9 |  1.4 |    1.89 |          2 |     2.36 | False |
| litestar           | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     2.36 | False |
| litestar           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.36 | False |
| litestar           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.35 | False |
| litestar           | types-infer-basedpyright |    37.7 |        59.3 |  1.6 |    1.89 |          2 |     2.35 | False |
| litestar           | types-infer-ty           |    38.8 |        62.6 |  1.6 |     1.9 |          2 |     2.34 | False |
| litestar           | types-infer-pyrefly      |    38.2 |        61.3 |  1.6 |    1.88 |          2 |     2.36 | False |
| litestar           | types-infer-trace        |    40.2 |        55.3 |  1.4 |    1.93 |          2 |     2.32 | False |
| litestar           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| stripe             | check                    |     5.6 |        16.0 |  2.9 |    0.69 |          3 |     0.86 | False |
| stripe             | fix-certain              |    16.2 |        48.1 |  3.0 |    0.86 |          4 |     1.06 | False |
| stripe             | fix-likely               |    16.8 |        51.2 |  3.0 |    0.99 |          3 |     1.24 | False |
| stripe             | fix-unsafe               |    17.6 |        51.9 |  2.9 |    1.02 |          4 |     1.27 | False |
| stripe             | infer-basedpyright       |   946.3 |      2363.4 |  2.5 |    4.52 |          2 |     3.95 | False |
| stripe             | infer-ty                 |    29.4 |        67.6 |  2.3 |     2.1 |          1 |     0.65 | False |
| stripe             | infer-pyrefly            |    48.2 |       100.8 |  2.1 |    3.02 |          2 |     2.63 | False |
| stripe             | census                   |     1.4 |         1.3 |  0.9 |    0.07 |          3 |     0.86 | False |
| stripe             | coverage                 |     2.4 |         7.2 |  3.0 |    0.27 |          3 |     0.34 | False |
| stripe             | timing                   |    23.6 |        34.9 |  1.5 |    0.69 |          2 |     0.86 | False |
| celery             | check                    |     4.8 |         0.2 |  0.0 |    0.04 |          2 |     1.19 | False |
| celery             | fix-certain              |    21.0 |        27.9 |  1.3 |    1.18 |          2 |     1.47 | False |
| celery             | fix-likely               |    25.6 |        34.8 |  1.4 |    1.33 |          2 |     1.66 | False |
| celery             | fix-unsafe               |    30.5 |        33.7 |  1.1 |    1.24 |          2 |     1.55 | False |
| celery             | infer-basedpyright       |    28.4 |        37.3 |  1.3 |    1.29 |          1 |     1.45 | False |
| celery             | infer-ty                 |    26.6 |        33.1 |  1.2 |    1.19 |          1 |     1.24 | False |
| celery             | infer-pyrefly            |    26.2 |        34.6 |  1.3 |    1.19 |          1 |     1.81 | False |
| celery             | census                   |     7.4 |        11.0 |  1.5 |    0.95 |          2 |     1.19 | False |
| celery             | coverage                 |     1.2 |         1.9 |  1.6 |    0.21 |          2 |     0.26 | False |
| celery             | timing                   |    16.0 |        20.0 |  1.2 |    0.95 |          2 |     1.19 | False |
| celery             | traced                   |    72.2 |        99.3 |  1.4 |    3.84 |          2 |     4.79 | False |
| celery             | tests-released           |    50.7 |        59.9 |  1.2 |    3.25 |          2 |     4.12 | False |
| celery             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.12 | False |
| celery             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.12 | False |
| celery             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.12 | False |
| celery             | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          2 |     4.12 | False |
| celery             | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          2 |     4.12 | False |
| celery             | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          2 |     4.12 | False |
| celery             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.12 | False |
| celery             | infer-union              |    38.9 |        42.3 |  1.1 |     1.3 |          1 |     1.85 | False |
| celery             | tests-infer-union        |    49.2 |        58.4 |  1.2 |    3.24 |          2 |     4.11 | False |
| celery             | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          2 |     0.19 | False |
| optuna             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.92 | False |
| optuna             | fix-certain              |    16.6 |        26.9 |  1.6 |    1.17 |          2 |     1.46 | False |
| optuna             | fix-likely               |    27.4 |        45.9 |  1.7 |    1.62 |          2 |     2.02 | False |
| optuna             | fix-unsafe               |    18.6 |        34.2 |  1.8 |    1.21 |          3 |     1.52 | False |
| optuna             | infer-basedpyright       |    26.2 |        41.5 |  1.6 |    1.59 |          1 |     1.74 | False |
| optuna             | infer-ty                 |    24.8 |        40.9 |  1.6 |    1.59 |          1 |     1.79 | False |
| optuna             | infer-pyrefly            |    26.6 |        41.3 |  1.6 |    1.59 |          1 |      2.3 | False |
| optuna             | census                   |     6.0 |        11.2 |  1.9 |    0.74 |          2 |     0.92 | False |
| optuna             | coverage                 |     1.0 |         1.8 |  1.8 |     0.2 |          2 |     0.25 | False |
| optuna             | timing                   |    13.6 |        18.4 |  1.4 |    0.74 |          2 |     0.92 | False |
| optuna             | traced                   |   167.3 |      1812.9 | 10.8 |    4.79 |          8 |     6.11 | False |
| optuna             | tests-released           |   133.5 |      1431.3 | 10.7 |     4.1 |          8 |     5.14 | False |
| optuna             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.06 | False |
| optuna             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.06 | False |
| optuna             | infer-union              |    28.2 |        44.3 |  1.6 |     1.6 |          2 |     2.11 | False |
| optuna             | tests-infer-union        |   143.9 |      1631.2 | 11.3 |    3.91 |          8 |     5.06 | False |
| optuna             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          1 |     0.19 | False |
| optuna             | types-released           |     6.4 |         6.1 |  1.0 |    0.37 |          1 |     0.47 | False |
| optuna             | types-fix-certain        |     8.6 |         6.3 |  0.7 |    0.37 |          1 |     0.46 | False |
| optuna             | types-fix-likely         |     9.8 |         6.2 |  0.6 |    0.37 |          1 |     0.46 | False |
| optuna             | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.54 | False |
| optuna             | types-infer-basedpyright |     9.0 |         5.8 |  0.6 |    0.37 |          1 |     0.46 | False |
| optuna             | types-infer-ty           |     8.4 |         6.7 |  0.8 |    0.38 |          1 |     0.46 | False |
| optuna             | types-infer-pyrefly      |     5.4 |         5.2 |  1.0 |    0.37 |          1 |     0.47 | False |
| optuna             | types-infer-trace        |     4.2 |         3.5 |  0.8 |    0.37 |          1 |     0.46 | False |
| optuna             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | check                    |    23.6 |        49.8 |  2.1 |    1.75 |          2 |     2.19 | False |
| dask               | fix-certain              |    68.9 |       118.7 |  1.7 |    2.31 |          2 |     2.89 | False |
| dask               | fix-likely               |   108.1 |       159.9 |  1.5 |    3.05 |          2 |     3.81 | False |
| dask               | fix-unsafe               |    75.6 |       145.5 |  1.9 |    2.97 |          2 |     3.71 | False |
| dask               | infer-basedpyright       |   266.2 |       526.2 |  2.0 |    5.68 |          1 |      3.2 | False |
| dask               | infer-ty                 |    95.5 |       208.0 |  2.2 |    4.55 |          1 |     3.21 | False |
| dask               | infer-pyrefly            |   117.3 |       211.7 |  1.8 |    6.46 |          1 |     3.86 | False |
| dask               | census                   |     5.8 |         5.4 |  0.9 |    0.13 |          2 |     2.19 | False |
| dask               | coverage                 |     2.2 |         6.0 |  2.7 |    0.46 |          3 |     0.57 | False |
| dask               | timing                   |    80.9 |        95.5 |  1.2 |    1.75 |          2 |     2.19 | False |
| dask               | traced                   |   203.9 |      1313.1 |  6.4 |    4.87 |          8 |     5.74 | False |
| dask               | tests-released           |   134.2 |      1107.1 |  8.2 |    4.79 |          8 |     5.54 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.54 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.76 | False |
| dask               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     5.54 | False |
| dask               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.82 | False |
| dask               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.64 | False |
| dask               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     5.52 | False |
| dask               | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      5.4 | False |
| dask               | infer-union              |   288.6 |       666.0 |  2.3 |    5.49 |          1 |     3.28 | False |
| dask               | tests-infer-union        |   148.5 |      1122.1 |  7.6 |    4.54 |          8 |     5.69 | False |
| dask               | tests                    |     2.2 |         1.5 |  0.7 |    0.16 |          1 |     0.19 | False |
| mypy               | check                    |    11.4 |        14.4 |  1.3 |    0.52 |          3 |     0.65 | False |
| mypy               | fix-certain              |    14.2 |        42.3 |  3.0 |     0.8 |          4 |     0.99 | False |
| mypy               | fix-likely               |    24.2 |        52.9 |  2.2 |    0.96 |          2 |      1.2 | False |
| mypy               | fix-unsafe               |    19.6 |        50.5 |  2.6 |     0.9 |          3 |     1.12 | False |
| mypy               | infer-basedpyright       |    46.6 |        58.4 |  1.3 |    0.93 |          1 |     2.26 | False |
| mypy               | infer-ty                 |    22.2 |        52.9 |  2.4 |    0.92 |          1 |     1.01 | False |
| mypy               | infer-pyrefly            |    22.8 |        52.3 |  2.3 |    0.93 |          1 |     1.56 | False |
| mypy               | census                   |     3.4 |         3.2 |  0.9 |     0.1 |          3 |     0.65 | False |
| mypy               | coverage                 |     1.9 |         5.6 |  2.9 |    0.36 |          3 |     0.44 | False |
| mypy               | timing                   |    23.0 |        27.5 |  1.2 |    0.52 |          2 |     0.65 | False |
| mypy               | traced                   |   358.4 |      2210.1 |  6.2 |    6.42 |          7 |     8.06 | False |
| mypy               | tests-released           |   303.7 |      2040.7 |  6.7 |     5.8 |          8 |     7.69 | False |
| mypy               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     7.25 | False |
| mypy               | infer-union              |    25.1 |        50.4 |  2.0 |    0.95 |          2 |     2.14 | False |
| mypy               | tests-infer-union        |   299.0 |      2013.3 |  6.7 |    6.02 |          7 |      8.0 | False |
| mypy               | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          1 |     0.19 | False |
| mypy               | types-released           |    14.2 |        29.7 |  2.1 |     0.6 |          2 |     0.74 | False |
| mypy               | types-fix-certain        |    12.4 |        24.1 |  1.9 |     0.5 |          3 |     0.62 | False |
| mypy               | types-fix-likely         |    10.8 |        22.6 |  2.1 |     0.5 |          2 |     0.62 | False |
| mypy               | types-fix-unsafe         |     0.8 |         0.5 |  0.6 |    0.05 |          3 |     0.77 | False |
| mypy               | types-infer-basedpyright |     7.2 |        18.1 |  2.5 |    0.49 |          3 |     0.61 | False |
| mypy               | types-infer-ty           |    11.2 |        28.4 |  2.5 |    0.62 |          2 |     0.77 | False |
| mypy               | types-infer-pyrefly      |     8.2 |        19.3 |  2.4 |    0.48 |          3 |     0.62 | False |
| mypy               | types-infer-trace        |    14.6 |        28.9 |  2.0 |    0.63 |          3 |     0.79 | False |
| mypy               | types                    |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.04 | False |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,392 |       4,320 |     1 |
| sphinx | likely             |          929 | 3,930 |       4,858 |     1 |
| sphinx | unsafe             |          929 | 4,334 |       5,262 |     1 |
| sphinx | infer-basedpyright |          929 | 5,089 |       6,017 |     1 |
| sphinx | infer-ty           |          929 | 5,142 |       6,070 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,326 |       6,254 |     1 |
| sphinx | infer-trace        |          929 | 4,334 |       5,262 |     1 |
| mypy   | unsafe             |        2,300 | 6,758 |       9,057 |     1 |
| mypy   | infer-basedpyright |        2,300 | 8,392 |      10,690 |     2 |
| mypy   | infer-ty           |        2,300 | 8,696 |      10,994 |     2 |
| mypy   | infer-pyrefly      |        2,300 | 8,915 |      11,213 |     2 |
| mypy   | infer-trace        |        2,300 | 6,758 |       9,057 |     1 |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus             | released                                                              | traced                                                                | same failures |
| ------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------- |
| django             | 1 errors, 5 expected failures, 2 failures, 17,585 ran, 1,149 skipped  | 5 expected failures, 5 failures, 17,585 ran, 1,149 skipped            | False         |
| sqlalchemy         | 29,521 passed, 975 skipped                                            | 29,521 passed, 975 skipped                                            | True          |
| pydantic           | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      | True          |
| pandas             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               | True          |
| structlog          | 24 failed, 860 passed, 37 skipped                                     | 24 failed, 860 passed, 37 skipped                                     | True          |
| attrs              | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          | True          |
| click              | 1,991 passed, 24 skipped, 1 xfailed                                   | 1,991 passed, 24 skipped, 1 xfailed                                   | True          |
| hypercorn          | 2 failed, 194 passed                                                  | 2 failed, 194 passed                                                  | True          |
| starlette          | 1,271 passed, 2 skipped, 2 xfailed                                    | 1,271 passed, 2 skipped, 2 xfailed                                    | True          |
| werkzeug           | 1 failed, 979 passed, 1 skipped                                       | 1 failed, 979 passed, 1 skipped                                       | True          |
| mkdocs             | 2 errors, 2 failures, 724 ran, 4 skipped                              | 2 errors, 2 failures, 724 ran, 4 skipped                              | True          |
| httpx              | 1 failed, 1,416 passed, 1 skipped                                     | 1 failed, 1,416 passed, 1 skipped                                     | True          |
| black              | 519 passed, 1 skipped                                                 | 519 passed, 1 skipped                                                 | True          |
| fastapi            | 3,551 passed, 17 skipped, 4 xfailed                                   | 3,551 passed, 17 skipped, 4 xfailed                                   | True          |
| cattrs             | 994 passed, 15 xfailed                                                | 994 passed, 15 xfailed                                                | True          |
| pytest             | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  | True          |
| botocore           | 7 failed, 4,593 passed, 96 skipped                                    | 7 failed, 4,593 passed, 96 skipped                                    | True          |
| uvicorn            | 1,350 passed, 12 skipped                                              | 1,350 passed, 12 skipped                                              | True          |
| mcp                | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          | False         |
| pdm                | 1,472 passed, 1 skipped                                               | 1,472 passed, 1 skipped                                               | True          |
| strawberry-graphql | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | False         |
| pygments           | 5,330 passed, 16 skipped                                              | 5,330 passed, 16 skipped                                              | True          |
| streamlink         | 9 error, 15 failed, 7,233 passed, 36 skipped                          | 9 error, 15 failed, 7,233 passed, 36 skipped                          | True          |
| sphinx             | 7 failed, 2,394 passed, 23 skipped                                    | 7 failed, 2,394 passed, 23 skipped                                    | True          |
| tox                | 6 error, 17 failed, 8,525 passed, 31 skipped                          | 6 error, 17 failed, 8,525 passed, 31 skipped                          | True          |
| pint               | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | True          |
| altair             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             | True          |
| seaborn            | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | False         |
| aiohttp            | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | True          |
| websockets         | 2,589 ran, 8 skipped                                                  | 2,589 ran, 8 skipped                                                  | True          |
| anyio              | 3,824 passed, 19 skipped, 5 xfailed                                   | 3,824 passed, 19 skipped, 5 xfailed                                   | True          |
| zarr               | 8,422 passed, 1,205 skipped, 4 xfailed                                | 8,422 passed, 1,205 skipped, 4 xfailed                                | True          |
| joblib             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         | 10 failed, 1,482 passed, 45 skipped, 4 xpassed                        | False         |
| networkx           | 10,083 passed, 62 skipped, 741 xfailed                                | 10,083 passed, 62 skipped, 741 xfailed                                | True          |
| nibabel            | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           | 20 error, 111 failed, 5,166 passed, 303 skipped, 40 xfailed           | False         |
| narwhals           | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | True          |
| xarray             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed | 3 error, 3 failed, 6,333 passed, 9,626 skipped, 11 xfailed, 4 xpassed | False         |
| litestar           | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           | 7 failed, 5,644 passed, 256 skipped, 13 xfailed, 30 xpassed           | False         |
| celery             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         | 4 failed, 3,520 passed, 36 skipped, 3 xfailed                         | False         |
| optuna             | 16 error, 263 failed, 4,203 passed, 43 skipped                        | 16 error, 263 failed, 4,203 passed, 43 skipped                        | False         |
| dask               | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | 5 failed, 16,196 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | False         |
| mypy               | 14,464 passed, 366 skipped, 12 xfailed                                | 14,464 passed, 366 skipped, 12 xfailed                                | True          |

- standard library, mega+dev, infer-basedpyright: held 14.35 GB beside other steps
- standard library, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 5 rounds came from
  the store, so its seconds measure less of the checker
- standard library, mega+dev, infer-ty: held 10.26 GB beside other steps
- standard library, mega+dev, infer-ty: ty's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- standard library, mega+dev, infer-pyrefly: held 12.69 GB beside other steps
- standard library, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 6 rounds came from the store,
  so its seconds measure less of the checker
- django, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- django, mega+dev, infer-ty: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- django, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the
  store, so its seconds measure less of the checker
- sqlalchemy, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, mega+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, mega+dev, infer-union: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, mega+dev, infer-union: ty's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- pydantic, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pydantic, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, infer-basedpyright: held 11.87 GB beside other steps
- pandas, mega+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- pandas, mega+dev, infer-ty: held 9.41 GB beside other steps
- pandas, mega+dev, infer-ty: ty's hints for 3 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, infer-pyrefly: held 14.1 GB beside other steps
- pandas, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, traced: held 14.13 GB beside other steps
- pandas, mega+dev, tests-released: held 11.49 GB beside other steps
- pandas, mega+dev, infer-union: held 11.46 GB beside other steps
- pandas, mega+dev, infer-union: basedpyright's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: pyrefly's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: ty's hints for 2 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, tests-infer-union: held 13.0 GB beside other steps
- twisted, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- twisted, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- twisted, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pip, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store, so
  its seconds measure less of the checker
- pip, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds measure
  less of the checker
- pip, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- structlog, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- structlog, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- structlog, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- structlog, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- structlog, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- structlog, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- attrs, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the store,
  so its seconds measure less of the checker
- attrs, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- attrs, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, mega+dev, infer-union: basedpyright's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, mega+dev, infer-union: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, mega+dev, infer-union: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- click, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store,
  so its seconds measure less of the checker
- click, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- click, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- hypercorn, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- hypercorn, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- hypercorn, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- hypercorn, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- starlette, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- starlette, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- starlette, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- starlette, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- werkzeug, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- werkzeug, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- werkzeug, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- werkzeug, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- mkdocs, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the store,
  so its seconds measure less of the checker
- mkdocs, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- mkdocs, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, mega+dev, infer-union: basedpyright's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, mega+dev, infer-union: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, mega+dev, infer-union: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- httpx, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- httpx, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- httpx, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- httpx, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- httpx, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- httpx, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- black, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- black, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- black, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- black, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- fastapi, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- fastapi, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- fastapi, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- cattrs, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- cattrs, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- cattrs, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, mega+dev, infer-union: basedpyright's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, mega+dev, infer-union: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, mega+dev, infer-union: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pytest, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 4 rounds came from the store,
  so its seconds measure less of the checker
- pytest, mega+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- pytest, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pytest, mega+dev, infer-union: basedpyright's hints for 3 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, mega+dev, infer-union: pyrefly's hints for 3 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, mega+dev, infer-union: ty's hints for 3 of 4 rounds came from the store, so its seconds
  measure less of the checker
- botocore, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the
  store, so its seconds measure less of the checker
- botocore, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- botocore, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- botocore, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- botocore, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- botocore, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- uvicorn, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- uvicorn, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- uvicorn, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- mcp, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mcp, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- mcp, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mcp, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- textual, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 5 rounds came from the store,
  so its seconds measure less of the checker
- textual, mega+dev, infer-ty: ty's hints for 4 of 5 rounds came from the store, so its seconds
  measure less of the checker
- textual, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the store, so
  its seconds measure less of the checker
- pdm, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds measure
  less of the checker
- pdm, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: basedpyright's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: pyrefly's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pdm, mega+dev, infer-union: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- strawberry-graphql, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from
  the store, so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the
  store, so its seconds measure less of the checker
- pygments, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pygments, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pygments, mega+dev, infer-union: basedpyright's hints for 6 of 6 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-union: pyrefly's hints for 6 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pygments, mega+dev, infer-union: ty's hints for 6 of 6 rounds came from the store, so its seconds
  measure less of the checker
- streamlink, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- streamlink, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- streamlink, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, mega+dev, infer-union: basedpyright's hints for 4 of 4 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, mega+dev, infer-union: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, mega+dev, infer-union: ty's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 3 rounds came from the store,
  so its seconds measure less of the checker
- sphinx, mega+dev, infer-ty: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- sphinx, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: basedpyright's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- tox, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds measure
  less of the checker
- tox, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pint, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store, so
  its seconds measure less of the checker
- pint, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds measure
  less of the checker
- pint, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pint, mega+dev, infer-union: basedpyright's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pint, mega+dev, infer-union: pyrefly's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pint, mega+dev, infer-union: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- altair, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the store,
  so its seconds measure less of the checker
- altair, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- altair, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- altair, mega+dev, infer-union: basedpyright's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- altair, mega+dev, infer-union: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- altair, mega+dev, infer-union: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- seaborn, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- seaborn, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- seaborn, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 5 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- aiohttp, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 3 rounds came from the store,
  so its seconds measure less of the checker
- aiohttp, mega+dev, infer-ty: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- aiohttp, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: basedpyright's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- websockets, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- websockets, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- websockets, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- websockets, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- websockets, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- websockets, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- anyio, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- anyio, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- zarr, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 3 rounds came from the store, so
  its seconds measure less of the checker
- zarr, mega+dev, infer-ty: ty's hints for 2 of 3 rounds came from the store, so its seconds measure
  less of the checker
- zarr, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- zarr, mega+dev, infer-union: basedpyright's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- zarr, mega+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- zarr, mega+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- joblib, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 4 rounds came from the store,
  so its seconds measure less of the checker
- joblib, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- joblib, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- joblib, mega+dev, infer-union: basedpyright's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- joblib, mega+dev, infer-union: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- joblib, mega+dev, infer-union: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- networkx, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the
  store, so its seconds measure less of the checker
- networkx, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- networkx, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- networkx, mega+dev, infer-union: basedpyright's hints for 4 of 6 rounds came from the store, so
  its seconds measure less of the checker
- networkx, mega+dev, infer-union: pyrefly's hints for 4 of 6 rounds came from the store, so its
  seconds measure less of the checker
- networkx, mega+dev, infer-union: ty's hints for 4 of 6 rounds came from the store, so its seconds
  measure less of the checker
- nibabel, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- nibabel, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- nibabel, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, mega+dev, infer-union: basedpyright's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, mega+dev, infer-union: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, mega+dev, infer-union: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- narwhals, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- narwhals, mega+dev, infer-ty: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- narwhals, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- narwhals, mega+dev, infer-union: basedpyright's hints for 2 of 3 rounds came from the store, so
  its seconds measure less of the checker
- narwhals, mega+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so its
  seconds measure less of the checker
- narwhals, mega+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- xarray, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 5 rounds came from the store,
  so its seconds measure less of the checker
- xarray, mega+dev, infer-ty: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- xarray, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- litestar, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- litestar, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- litestar, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- litestar, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- litestar, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- litestar, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- stripe, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 4 rounds came from the store,
  so its seconds measure less of the checker
- stripe, mega+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- stripe, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the store,
  so its seconds measure less of the checker
- celery, mega+dev, infer-ty: ty's hints for 4 of 4 rounds came from the store, so its seconds
  measure less of the checker
- celery, mega+dev, infer-pyrefly: pyrefly's hints for 4 of 4 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: basedpyright's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- optuna, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store,
  so its seconds measure less of the checker
- optuna, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- optuna, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- dask, mega+dev, infer-basedpyright: basedpyright's hints for 4 of 5 rounds came from the store, so
  its seconds measure less of the checker
- dask, mega+dev, infer-ty: ty's hints for 4 of 5 rounds came from the store, so its seconds measure
  less of the checker
- dask, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- dask, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- dask, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- dask, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- mypy, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mypy, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- mypy, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mypy, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mypy, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mypy, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
