# Mega corpora

The run `mega` (`python -m tests.corpus`) on mega: constricter 0.4.5.dev41+g28434383f.d20261107
(`edcaba3d1126`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 86 minutes. Timings don't compare across machines, nor their seconds across runs, taken
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
| standard library   | mega+dev    | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,386 (32.9%) |   6,986 (6.1%) | 14,240 (12.5%) |      0 |    0 |            0 |
| django             | mega+dev    |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |   2,625 (15.3%) |     734 (4.3%) |  2,891 (16.8%) |      0 |    0 |            0 |
| sqlalchemy         | mega+dev    |  0 / 12,934 |   11,296 / 2,339 |    12,934 / 701 |  13,635 / 0 |   2,145 (15.7%) |     446 (3.3%) |   1,153 (8.5%) |      0 |    0 |            0 |
| pydantic           | mega+dev    |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |   1,199 (36.2%) |     150 (4.5%) |    413 (12.5%) |      0 |    0 |            0 |
| pandas             | mega+dev    |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  17,188 (22.1%) | 24,513 (31.5%) | 25,851 (33.2%) |      0 |    0 |            0 |
| twisted            | mega+dev    |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,435 (13.6%) |  3,741 (20.9%) |  4,829 (27.0%) |      0 |    0 |            0 |
| pip                | mega+dev    |   0 / 8,923 |    7,773 / 1,150 |       8,923 / 0 |   8,923 / 0 |   2,243 (25.1%) |     490 (5.5%) |  1,343 (15.1%) |      0 |    0 |            0 |
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
| cattrs             | mega+dev    |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     114 (21.5%) |      35 (6.6%) |     53 (10.0%) |      0 |    0 |            0 |
| pytest             | mega+dev    |   0 / 3,000 |      2,530 / 512 |      3,000 / 42 |   3,042 / 0 |   1,375 (45.2%) |     160 (5.3%) |    313 (10.3%) |      0 |    0 |            0 |
| botocore           | mega+dev    |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     548 (14.5%) |     182 (4.8%) |    656 (17.3%) |      0 |    0 |            0 |
| uvicorn            | mega+dev    |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     236 (46.8%) |      32 (6.3%) |     57 (11.3%) |      0 |    0 |            0 |
| mcp                | mega+dev    |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     718 (39.2%) |     162 (8.8%) |    248 (13.5%) |      0 |    0 |            0 |
| textual            | mega+dev    |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,796 (42.8%) |     507 (7.8%) |    773 (11.8%) |      0 |    0 |            0 |
| pdm                | mega+dev    |   0 / 2,713 |      2,296 / 456 |      2,713 / 39 |   2,752 / 0 |   1,246 (45.3%) |     218 (7.9%) |    364 (13.2%) |      0 |    0 |            0 |
| strawberry-graphql | mega+dev    |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     656 (33.7%) |     174 (8.9%) |    241 (12.4%) |      0 |    0 |            0 |
| pygments           | mega+dev    |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      736 (9.6%) |      81 (1.1%) |  4,617 (60.2%) |      0 |    0 |            0 |
| streamlink         | mega+dev    |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     701 (22.8%) |     137 (4.5%) |    579 (18.8%) |      0 |    0 |            0 |
| sphinx             | mega+dev    |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,392 (42.0%) |     539 (6.7%) |    943 (11.7%) |      0 |    0 |            0 |
| tox                | mega+dev    |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     985 (55.2%) |     103 (5.8%) |     158 (8.9%) |      0 |    0 |            0 |
| pint               | mega+dev    |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     650 (21.0%) |     276 (8.9%) |    328 (10.6%) |      0 |    0 |            0 |
| altair             | mega+dev    |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     389 (22.0%) |      52 (2.9%) |      65 (3.7%) |      0 |    0 |            0 |
| seaborn            | mega+dev    |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     657 (22.5%) |     164 (5.6%) |     242 (8.3%) |      0 |    0 |            0 |
| aiohttp            | mega+dev    |   0 / 1,859 |      1,662 / 215 |      1,859 / 18 |   1,877 / 0 |     722 (38.5%) |     152 (8.1%) |    274 (14.6%) |      0 |    0 |            0 |
| websockets         | mega+dev    |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     362 (45.8%) |      77 (9.7%) |    130 (16.4%) |      0 |    0 |            0 |
| anyio              | mega+dev    |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     230 (30.8%) |      36 (4.8%) |      69 (9.2%) |      0 |    0 |            0 |
| zarr               | mega+dev    |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,169 (47.3%) |      79 (3.2%) |     118 (4.8%) |      0 |    0 |            0 |
| joblib             | mega+dev    |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     179 (8.0%) |    304 (13.6%) |      0 |    0 |            0 |
| networkx           | mega+dev    |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |   3,971 (17.7%) |   2,208 (9.8%) |  2,562 (11.4%) |      0 |    0 |            0 |
| nibabel            | mega+dev    |   0 / 8,466 |    7,434 / 1,038 |       8,466 / 6 |   8,472 / 0 |   1,871 (22.1%) |     841 (9.9%) |  1,175 (13.9%) |      0 |    0 |            0 |
| narwhals           | mega+dev    |   0 / 3,112 |      3,006 / 173 |      3,112 / 67 |   3,179 / 0 |   1,082 (34.0%) |      76 (2.4%) |     131 (4.1%) |      0 |    0 |            0 |
| xarray             | mega+dev    |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   4,623 (21.4%) |  5,152 (23.8%) |  5,528 (25.6%) |      0 |    0 |            0 |
| litestar           | mega+dev    |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     648 (31.0%) |     124 (5.9%) |     198 (9.5%) |      0 |    0 |            0 |
| stripe             | mega+dev    |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     781 (18.5%) |     166 (3.9%) |    671 (15.9%) |      0 |    0 |            0 |
| celery             | mega+dev    |   0 / 3,749 |      3,416 / 333 |       3,749 / 0 |   3,749 / 0 |     508 (13.6%) |     130 (3.5%) |     372 (9.9%) |      0 |    0 |            0 |
| optuna             | mega+dev    |   0 / 3,595 |      3,149 / 478 |      3,595 / 32 |   3,627 / 0 |   1,583 (43.6%) |     219 (6.0%) |     327 (9.0%) |      0 |    0 |            0 |
| dask               | mega+dev    |  0 / 24,173 |   22,480 / 1,775 |     24,173 / 82 |  24,255 / 0 |   3,161 (13.0%) |   1,986 (8.2%) |  2,907 (12.0%) |      0 |    0 |            0 |
| mypy               | mega+dev    |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |   5,142 (43.6%) |  1,209 (10.3%) |  1,616 (13.7%) |      0 |    0 |            0 |
| **Total**          | mega+dev    | 0 / 420,324 | 379,579 / 44,779 | 420,323 / 4,036 | 424,359 / 0 | 110,341 (26.0%) | 53,406 (12.6%) | 78,033 (18.4%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | mega+dev    |              1.2% |         33.7% |            39.7% |                  46.0% | +32.5 pts, 32.9% of untyped | +44.9 pts, 45.4% of untyped |
| django             | mega+dev    |              0.0% |         15.3% |            19.6% |                  32.1% | +15.3 pts, 15.3% of untyped | +32.1 pts, 32.1% of untyped |
| sqlalchemy         | mega+dev    |             15.3% |         29.3% |            32.2% |                  36.8% | +14.0 pts, 16.5% of untyped | +21.5 pts, 25.4% of untyped |
| pydantic           | mega+dev    |             22.4% |         52.3% |            56.0% |                  62.6% | +29.8 pts, 38.5% of untyped | +40.1 pts, 51.7% of untyped |
| pandas             | mega+dev    |              1.6% |         23.3% |            54.3% |                  56.0% | +21.7 pts, 22.1% of untyped | +54.4 pts, 55.3% of untyped |
| twisted            | mega+dev    |              0.0% |         13.6% |            34.6% |                  40.6% | +13.6 pts, 13.6% of untyped | +40.6 pts, 40.6% of untyped |
| pip                | mega+dev    |              1.5% |         26.3% |            31.7% |                  41.1% | +24.7 pts, 25.1% of untyped | +39.6 pts, 40.2% of untyped |
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
| cattrs             | mega+dev    |              7.0% |         27.4% |            33.6% |                  36.9% | +20.4 pts, 21.9% of untyped | +29.9 pts, 32.1% of untyped |
| pytest             | mega+dev    |             12.1% |         52.4% |            57.1% |                  61.5% | +40.2 pts, 45.8% of untyped | +49.4 pts, 56.2% of untyped |
| botocore           | mega+dev    |              0.5% |         14.9% |            19.7% |                  32.1% | +14.4 pts, 14.5% of untyped | +31.6 pts, 31.8% of untyped |
| uvicorn            | mega+dev    |             23.6% |         60.5% |            65.5% |                  69.4% | +36.9 pts, 48.3% of untyped | +45.8 pts, 59.9% of untyped |
| mcp                | mega+dev    |             30.7% |         59.6% |            66.2% |                  69.6% | +28.9 pts, 41.7% of untyped | +38.9 pts, 56.2% of untyped |
| textual            | mega+dev    |             15.6% |         52.0% |            58.6% |                  62.0% | +36.4 pts, 43.1% of untyped | +46.5 pts, 55.1% of untyped |
| pdm                | mega+dev    |             11.7% |         52.2% |            59.3% |                  64.0% | +40.5 pts, 45.8% of untyped | +52.3 pts, 59.2% of untyped |
| strawberry-graphql | mega+dev    |             30.1% |         55.5% |            62.2% |                  64.8% | +25.4 pts, 36.3% of untyped | +34.7 pts, 49.7% of untyped |
| pygments           | mega+dev    |              0.0% |          9.6% |            10.7% |                  69.8% |   +9.6 pts, 9.6% of untyped | +69.8 pts, 69.8% of untyped |
| streamlink         | mega+dev    |             42.8% |         56.0% |            58.6% |                  66.9% | +13.2 pts, 23.1% of untyped | +24.2 pts, 42.3% of untyped |
| sphinx             | mega+dev    |             10.4% |         48.5% |            54.6% |                  59.1% | +38.1 pts, 42.5% of untyped | +48.7 pts, 54.4% of untyped |
| tox                | mega+dev    |             16.0% |         63.0% |            67.9% |                  70.5% | +46.9 pts, 55.9% of untyped | +54.5 pts, 64.9% of untyped |
| pint               | mega+dev    |              5.1% |         25.1% |            33.6% |                  35.2% | +20.0 pts, 21.1% of untyped | +30.2 pts, 31.8% of untyped |
| altair             | mega+dev    |             49.7% |         61.2% |            62.8% |                  63.1% | +11.5 pts, 22.9% of untyped | +13.4 pts, 26.7% of untyped |
| seaborn            | mega+dev    |              6.9% |         28.0% |            33.3% |                  35.8% | +21.1 pts, 22.7% of untyped | +28.9 pts, 31.1% of untyped |
| aiohttp            | mega+dev    |             23.7% |         53.3% |            59.6% |                  64.6% | +29.7 pts, 38.9% of untyped | +40.9 pts, 53.6% of untyped |
| websockets         | mega+dev    |             13.8% |         53.3% |            61.7% |                  67.4% | +39.4 pts, 45.8% of untyped | +53.6 pts, 62.2% of untyped |
| anyio              | mega+dev    |             27.8% |         51.0% |            54.6% |                  58.0% | +23.2 pts, 32.2% of untyped | +30.2 pts, 41.8% of untyped |
| zarr               | mega+dev    |             21.7% |         59.7% |            62.2% |                  63.5% | +38.0 pts, 48.5% of untyped | +41.8 pts, 53.4% of untyped |
| joblib             | mega+dev    |              0.0% |         23.5% |            31.5% |                  37.0% | +23.4 pts, 23.4% of untyped | +37.0 pts, 37.0% of untyped |
| networkx           | mega+dev    |              0.3% |         17.9% |            27.7% |                  29.3% | +17.6 pts, 17.7% of untyped | +29.0 pts, 29.1% of untyped |
| nibabel            | mega+dev    |              1.0% |         22.8% |            32.7% |                  36.6% | +21.9 pts, 22.1% of untyped | +35.6 pts, 36.0% of untyped |
| narwhals           | mega+dev    |             21.7% |         48.9% |            50.8% |                  52.1% | +27.2 pts, 34.7% of untyped | +30.4 pts, 38.9% of untyped |
| xarray             | mega+dev    |              4.6% |         25.3% |            48.3% |                  50.0% | +20.7 pts, 21.7% of untyped | +45.4 pts, 47.6% of untyped |
| litestar           | mega+dev    |             44.9% |         63.7% |            67.2% |                  69.4% | +18.7 pts, 34.0% of untyped | +24.5 pts, 44.4% of untyped |
| stripe             | mega+dev    |             89.5% |         92.0% |            92.5% |                  94.1% |  +2.4 pts, 23.3% of untyped |  +4.5 pts, 43.3% of untyped |
| celery             | mega+dev    |              0.4% |         13.9% |            17.4% |                  23.8% | +13.5 pts, 13.6% of untyped | +23.4 pts, 23.5% of untyped |
| optuna             | mega+dev    |              7.5% |         48.2% |            53.8% |                  56.6% | +40.7 pts, 44.0% of untyped | +49.1 pts, 53.1% of untyped |
| dask               | mega+dev    |              1.1% |         14.0% |            22.1% |                  25.9% | +12.9 pts, 13.1% of untyped | +24.8 pts, 25.1% of untyped |
| mypy               | mega+dev    |             16.8% |         54.3% |            63.1% |                  66.1% | +37.5 pts, 45.1% of untyped | +49.3 pts, 59.3% of untyped |
| **Total**          | mega+dev    |             11.4% |         34.6% |            45.9% |                  51.1% | +23.3 pts, 26.2% of untyped | +39.7 pts, 44.8% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,386 |  37,386 |        |        |      0 |    0 | 38,715 |  115,001 |    93.5 |
| standard library   | likely             | 44,372 |  37,662 |  6,710 |        |      0 |    0 | 45,701 |  115,001 |   128.7 |
| standard library   | unsafe             | 51,626 |  37,393 |  6,690 |  7,543 |      0 |    0 | 52,955 |  115,001 |   117.0 |
| standard library   | infer-basedpyright | 59,345 |  37,396 |  7,103 | 14,846 |      0 |    7 | 60,674 |  115,001 |   895.0 |
| standard library   | infer-ty           | 57,099 |  37,430 |  7,085 | 12,584 |      0 |   23 | 58,428 |  115,001 |   153.7 |
| standard library   | infer-pyrefly      | 59,479 |  37,385 |  7,140 | 14,954 |      0 |   39 | 60,808 |  115,001 |   234.7 |
| django             | certain            |  2,625 |   2,625 |        |        |      0 |    0 |  2,630 |   17,181 |    14.5 |
| django             | likely             |  3,359 |   2,630 |    729 |        |      0 |    0 |  3,364 |   17,181 |    32.6 |
| django             | unsafe             |  5,516 |   2,625 |    727 |  2,164 |      0 |    0 |  5,521 |   17,181 |    33.8 |
| django             | infer-basedpyright |  5,898 |   2,619 |    740 |  2,539 |      0 |    2 |  5,903 |   17,181 |   105.6 |
| django             | infer-ty           |  5,718 |   2,626 |    735 |  2,357 |      0 |    0 |  5,723 |   17,181 |    43.4 |
| django             | infer-pyrefly      |  6,182 |   2,614 |    747 |  2,821 |      0 |   25 |  6,187 |   17,181 |    50.7 |
| django             | infer-trace        |  6,062 |   2,625 |    757 |  2,680 |      0 |    0 |  6,067 |   17,181 |    20.1 |
| sqlalchemy         | certain            |  2,145 |   2,145 |        |        |      0 |    0 |  4,480 |   15,304 |    19.0 |
| sqlalchemy         | likely             |  2,591 |   2,153 |    438 |        |      0 |    0 |  4,926 |   15,304 |    23.7 |
| sqlalchemy         | unsafe             |  3,298 |   2,145 |    438 |    715 |      0 |    0 |  5,633 |   15,304 |    27.3 |
| sqlalchemy         | infer-basedpyright |  4,018 |   2,147 |    476 |  1,395 |      0 |    0 |  6,353 |   15,304 |   132.9 |
| sqlalchemy         | infer-ty           |  3,958 |   2,147 |    465 |  1,346 |      0 |    0 |  6,293 |   15,304 |    48.0 |
| sqlalchemy         | infer-pyrefly      |  3,760 |   2,146 |    458 |  1,156 |      0 |    0 |  6,095 |   15,304 |    47.1 |
| sqlalchemy         | infer-trace        |  3,451 |   2,145 |    438 |    868 |      0 |    0 |  5,786 |   15,304 |    12.3 |
| pydantic           | certain            |  1,199 |   1,199 |        |        |      0 |    0 |  2,101 |    4,019 |     1.8 |
| pydantic           | likely             |  1,349 |   1,206 |    143 |        |      0 |    0 |  2,251 |    4,019 |     4.3 |
| pydantic           | unsafe             |  1,612 |   1,199 |    142 |    271 |      0 |    0 |  2,514 |    4,019 |     4.5 |
| pydantic           | infer-basedpyright |  1,827 |   1,200 |    144 |    483 |      0 |    0 |  2,729 |    4,019 |    50.4 |
| pydantic           | infer-ty           |  1,743 |   1,199 |    140 |    404 |      0 |    0 |  2,645 |    4,019 |    13.1 |
| pydantic           | infer-pyrefly      |  1,807 |   1,199 |    141 |    467 |      0 |    0 |  2,709 |    4,019 |    24.2 |
| pydantic           | infer-trace        |  1,613 |   1,199 |    142 |    272 |      0 |    0 |  2,515 |    4,019 |     5.7 |
| pandas             | certain            | 17,188 |  17,188 |        |        |      0 |    0 | 18,457 |   79,062 |    85.6 |
| pandas             | likely             | 41,701 |  17,400 | 24,301 |        |      0 |    0 | 42,970 |   79,062 |   180.8 |
| pandas             | unsafe             | 43,039 |  17,184 | 24,281 |  1,574 |      0 |    0 | 44,308 |   79,062 |   187.0 |
| pandas             | infer-basedpyright | 48,532 |  17,175 | 24,262 |  7,095 |      0 |   23 | 49,801 |   79,062 |   497.6 |
| pandas             | infer-ty           | 48,498 |  17,184 | 24,270 |  7,044 |      0 |   21 | 49,767 |   79,062 |   200.9 |
| pandas             | infer-pyrefly      | 50,982 |  17,183 | 24,211 |  9,588 |      0 |   25 | 52,251 |   79,062 |   168.8 |
| pandas             | infer-trace        | 44,469 |  17,189 | 24,150 |  3,130 |      0 |    0 | 45,738 |   79,062 |   124.4 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     6.2 |
| twisted            | likely             |  6,176 |   2,453 |  3,723 |        |      0 |    0 |  6,176 |   17,874 |    11.1 |
| twisted            | unsafe             |  7,264 |   2,434 |  3,723 |  1,107 |      0 |    0 |  7,264 |   17,874 |    10.0 |
| twisted            | infer-basedpyright |  8,627 |   2,435 |  3,739 |  2,453 |      0 |    0 |  8,627 |   17,874 |   153.0 |
| twisted            | infer-ty           |  7,630 |   2,434 |  3,734 |  1,462 |      0 |    0 |  7,630 |   17,874 |    30.7 |
| twisted            | infer-pyrefly      |  7,665 |   2,434 |  3,733 |  1,498 |      0 |    0 |  7,665 |   17,874 |    29.2 |
| pip                | certain            |  2,243 |   2,243 |        |        |      0 |    0 |  2,380 |    9,064 |     5.2 |
| pip                | likely             |  2,733 |   2,250 |    483 |        |      0 |    0 |  2,870 |    9,064 |     7.1 |
| pip                | unsafe             |  3,586 |   2,243 |    481 |    862 |      0 |    0 |  3,723 |    9,064 |     6.6 |
| pip                | infer-basedpyright |  4,310 |   2,244 |    526 |  1,540 |      0 |    5 |  4,447 |    9,064 |    55.0 |
| pip                | infer-ty           |  3,882 |   2,244 |    500 |  1,138 |      0 |    7 |  4,019 |    9,064 |    20.5 |
| pip                | infer-pyrefly      |  4,100 |   2,242 |    510 |  1,348 |      0 |    0 |  4,237 |    9,064 |    24.1 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.7 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.6 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.9 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |    10.4 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     4.0 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     3.8 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.8 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.8 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     0.9 |
| attrs              | unsafe             |    107 |      93 |      8 |      6 |      0 |    0 |    110 |      396 |     1.0 |
| attrs              | infer-basedpyright |    126 |      93 |      8 |     25 |      0 |    0 |    129 |      396 |    11.7 |
| attrs              | infer-ty           |    118 |      93 |      8 |     17 |      0 |    0 |    121 |      396 |     2.8 |
| attrs              | infer-pyrefly      |    122 |      93 |      8 |     21 |      0 |    0 |    125 |      396 |     4.4 |
| attrs              | infer-trace        |    110 |      93 |      9 |      8 |      0 |    0 |    113 |      396 |     1.1 |
| click              | certain            |    311 |     311 |        |        |      0 |    0 |    590 |      887 |     0.5 |
| click              | likely             |    338 |     312 |     26 |        |      0 |    0 |    617 |      887 |     1.3 |
| click              | unsafe             |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     1.8 |
| click              | infer-basedpyright |    437 |     311 |     30 |     96 |      0 |    0 |    716 |      887 |    10.5 |
| click              | infer-ty           |    455 |     311 |     28 |    116 |      0 |    0 |    734 |      887 |     2.2 |
| click              | infer-pyrefly      |    449 |     311 |     31 |    107 |      0 |    0 |    728 |      887 |     3.7 |
| click              | infer-trace        |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     2.4 |
| hypercorn          | certain            |    137 |     137 |        |        |      0 |    0 |    307 |      525 |     0.8 |
| hypercorn          | likely             |    157 |     137 |     20 |        |      0 |    0 |    327 |      525 |     0.8 |
| hypercorn          | unsafe             |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     1.5 |
| hypercorn          | infer-basedpyright |    216 |     137 |     21 |     58 |      0 |    0 |    386 |      525 |     8.5 |
| hypercorn          | infer-ty           |    219 |     137 |     21 |     61 |      0 |    0 |    389 |      525 |     2.5 |
| hypercorn          | infer-pyrefly      |    204 |     137 |     20 |     47 |      0 |    0 |    374 |      525 |     2.6 |
| hypercorn          | infer-trace        |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     3.2 |
| starlette          | certain            |    321 |     321 |        |        |      0 |    0 |    406 |      829 |     0.8 |
| starlette          | likely             |    396 |     322 |     74 |        |      0 |    0 |    481 |      829 |     0.7 |
| starlette          | unsafe             |    437 |     321 |     74 |     42 |      0 |    0 |    522 |      829 |     2.6 |
| starlette          | infer-basedpyright |    497 |     321 |     73 |    103 |      0 |    0 |    582 |      829 |     9.5 |
| starlette          | infer-ty           |    483 |     321 |     73 |     89 |      0 |    0 |    568 |      829 |     2.6 |
| starlette          | infer-pyrefly      |    465 |     321 |     73 |     71 |      0 |    0 |    550 |      829 |     2.8 |
| starlette          | infer-trace        |    437 |     321 |     74 |     42 |      0 |    0 |    522 |      829 |     2.6 |
| werkzeug           | certain            |    545 |     545 |        |        |      0 |    0 |    761 |    1,509 |     1.0 |
| werkzeug           | likely             |    617 |     546 |     71 |        |      0 |    0 |    833 |    1,509 |     1.0 |
| werkzeug           | unsafe             |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     3.2 |
| werkzeug           | infer-basedpyright |    798 |     545 |     82 |    171 |      0 |    0 |  1,014 |    1,509 |    12.7 |
| werkzeug           | infer-ty           |    823 |     545 |     84 |    194 |      0 |    0 |  1,039 |    1,509 |     4.1 |
| werkzeug           | infer-pyrefly      |    817 |     546 |     72 |    199 |      0 |    0 |  1,033 |    1,509 |     4.4 |
| werkzeug           | infer-trace        |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     4.6 |
| mkdocs             | certain            |    826 |     826 |        |        |      0 |    0 |    937 |    2,443 |     1.1 |
| mkdocs             | likely             |  1,256 |     858 |    398 |        |      0 |    0 |  1,367 |    2,443 |     2.1 |
| mkdocs             | unsafe             |  1,378 |     826 |    398 |    154 |      0 |    0 |  1,489 |    2,443 |     2.4 |
| mkdocs             | infer-basedpyright |  1,472 |     826 |    405 |    241 |      0 |    0 |  1,583 |    2,443 |    14.6 |
| mkdocs             | infer-ty           |  1,500 |     826 |    410 |    264 |      0 |    0 |  1,611 |    2,443 |     6.1 |
| mkdocs             | infer-pyrefly      |  1,472 |     826 |    406 |    240 |      0 |    0 |  1,583 |    2,443 |     6.3 |
| mkdocs             | infer-trace        |  1,390 |     827 |    398 |    165 |      0 |    0 |  1,501 |    2,443 |     4.3 |
| httpx              | certain            |    240 |     240 |        |        |      0 |    0 |    278 |      607 |     0.8 |
| httpx              | likely             |    309 |     250 |     59 |        |      0 |    0 |    347 |      607 |     1.1 |
| httpx              | unsafe             |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     3.4 |
| httpx              | infer-basedpyright |    408 |     240 |     64 |    104 |      0 |    0 |    446 |      607 |     8.7 |
| httpx              | infer-ty           |    392 |     241 |     63 |     88 |      0 |    0 |    430 |      607 |     3.7 |
| httpx              | infer-pyrefly      |    367 |     240 |     62 |     65 |      0 |    0 |    405 |      607 |     3.6 |
| httpx              | infer-trace        |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     2.6 |
| black              | certain            |    714 |     714 |        |        |      0 |    0 |    954 |    1,513 |     1.0 |
| black              | likely             |    842 |     727 |    115 |        |      0 |    0 |  1,082 |    1,513 |     1.1 |
| black              | unsafe             |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     1.4 |
| black              | infer-basedpyright |    938 |     714 |    116 |    108 |      0 |    0 |  1,178 |    1,513 |     9.7 |
| black              | infer-ty           |    938 |     714 |    116 |    108 |      0 |    0 |  1,178 |    1,513 |     2.6 |
| black              | infer-pyrefly      |    924 |     714 |    115 |     95 |      0 |    0 |  1,164 |    1,513 |     2.6 |
| black              | infer-trace        |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     0.9 |
| fastapi            | certain            |    258 |     258 |        |        |      0 |    0 |    795 |    1,279 |     1.5 |
| fastapi            | likely             |    303 |     264 |     39 |        |      0 |    0 |    840 |    1,279 |     3.8 |
| fastapi            | unsafe             |    329 |     258 |     39 |     32 |      0 |    0 |    866 |    1,279 |     3.8 |
| fastapi            | infer-basedpyright |    355 |     258 |     38 |     59 |      0 |    0 |    892 |    1,279 |    24.9 |
| fastapi            | infer-ty           |    372 |     258 |     37 |     77 |      0 |    0 |    909 |    1,279 |     9.5 |
| fastapi            | infer-pyrefly      |    352 |     258 |     39 |     55 |      0 |    0 |    889 |    1,279 |     7.4 |
| fastapi            | infer-trace        |    329 |     258 |     39 |     32 |      0 |    0 |    866 |    1,279 |     2.8 |
| cattrs             | certain            |    114 |     114 |        |        |      0 |    0 |    153 |      559 |     0.8 |
| cattrs             | likely             |    149 |     121 |     28 |        |      0 |    0 |    188 |      559 |     1.0 |
| cattrs             | unsafe             |    167 |     117 |     27 |     23 |      0 |    0 |    206 |      559 |     2.0 |
| cattrs             | infer-basedpyright |    200 |     116 |     30 |     54 |      0 |    0 |    239 |      559 |     9.8 |
| cattrs             | infer-ty           |    208 |     114 |     28 |     66 |      0 |    0 |    247 |      559 |     2.2 |
| cattrs             | infer-pyrefly      |    194 |     114 |     29 |     51 |      0 |    0 |    233 |      559 |     4.8 |
| cattrs             | infer-trace        |    167 |     117 |     27 |     23 |      0 |    0 |    206 |      559 |     1.2 |
| pytest             | certain            |  1,375 |   1,375 |        |        |      0 |    0 |  1,790 |    3,418 |     2.9 |
| pytest             | likely             |  1,535 |   1,380 |    155 |        |      0 |    0 |  1,950 |    3,418 |     3.4 |
| pytest             | unsafe             |  1,688 |   1,375 |    155 |    158 |      0 |    0 |  2,103 |    3,418 |     5.5 |
| pytest             | infer-basedpyright |  2,019 |   1,375 |    173 |    471 |      0 |    0 |  2,434 |    3,418 |    20.0 |
| pytest             | infer-ty           |  2,028 |   1,375 |    175 |    478 |      0 |    0 |  2,443 |    3,418 |    10.5 |
| pytest             | infer-pyrefly      |  2,086 |   1,375 |    175 |    536 |      0 |    0 |  2,501 |    3,418 |    10.7 |
| pytest             | infer-trace        |  1,705 |   1,375 |    155 |    175 |      0 |    0 |  2,120 |    3,418 |     8.5 |
| botocore           | certain            |    548 |     548 |        |        |      0 |    0 |    566 |    3,806 |     2.5 |
| botocore           | likely             |    730 |     550 |    180 |        |      0 |    0 |    748 |    3,806 |     3.9 |
| botocore           | unsafe             |  1,204 |     546 |    178 |    480 |      0 |    0 |  1,222 |    3,806 |     5.0 |
| botocore           | infer-basedpyright |  1,339 |     541 |    177 |    621 |      0 |    0 |  1,357 |    3,806 |    26.4 |
| botocore           | infer-ty           |  1,261 |     546 |    179 |    536 |      0 |    0 |  1,279 |    3,806 |    11.3 |
| botocore           | infer-pyrefly      |  1,322 |     541 |    175 |    606 |      0 |    0 |  1,340 |    3,806 |     9.5 |
| botocore           | infer-trace        |  1,537 |     546 |    199 |    792 |      0 |    0 |  1,555 |    3,806 |     4.3 |
| uvicorn            | certain            |    236 |     236 |        |        |      0 |    0 |    387 |      640 |     1.1 |
| uvicorn            | likely             |    268 |     236 |     32 |        |      0 |    0 |    419 |      640 |     1.1 |
| uvicorn            | unsafe             |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     2.5 |
| uvicorn            | infer-basedpyright |    354 |     236 |     35 |     83 |      0 |    0 |    505 |      640 |     9.3 |
| uvicorn            | infer-ty           |    334 |     236 |     32 |     66 |      0 |    0 |    485 |      640 |     5.3 |
| uvicorn            | infer-pyrefly      |    316 |     236 |     35 |     45 |      0 |    0 |    467 |      640 |     7.2 |
| uvicorn            | infer-trace        |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     2.0 |
| mcp                | certain            |    718 |     718 |        |        |      0 |    0 |  1,481 |    2,483 |     1.8 |
| mcp                | likely             |    880 |     724 |    156 |        |      0 |    0 |  1,643 |    2,483 |     2.3 |
| mcp                | unsafe             |    966 |     718 |    156 |     92 |      0 |    0 |  1,729 |    2,483 |     6.5 |
| mcp                | infer-basedpyright |  1,079 |     718 |    167 |    194 |      0 |    0 |  1,842 |    2,483 |    27.6 |
| mcp                | infer-ty           |  1,069 |     718 |    164 |    187 |      0 |    0 |  1,832 |    2,483 |     6.5 |
| mcp                | infer-pyrefly      |  1,048 |     718 |    161 |    169 |      0 |    0 |  1,811 |    2,483 |    11.8 |
| mcp                | infer-trace        |    966 |     718 |    156 |     92 |      0 |    0 |  1,729 |    2,483 |     3.7 |
| textual            | certain            |  2,796 |   2,796 |        |        |      0 |    0 |  3,990 |    7,677 |     2.0 |
| textual            | likely             |  3,303 |   2,820 |    483 |        |      0 |    0 |  4,497 |    7,677 |     3.7 |
| textual            | unsafe             |  3,569 |   2,796 |    482 |    291 |      0 |    0 |  4,763 |    7,677 |     4.3 |
| textual            | infer-basedpyright |  4,684 |   2,796 |    556 |  1,332 |      0 |    0 |  5,878 |    7,677 |    34.7 |
| textual            | infer-ty           |  4,756 |   2,796 |    554 |  1,406 |      0 |    0 |  5,950 |    7,677 |    14.6 |
| textual            | infer-pyrefly      |  3,922 |   2,796 |    499 |    627 |      0 |    0 |  5,116 |    7,677 |    12.9 |
| pdm                | certain            |  1,246 |   1,246 |        |        |      0 |    0 |  1,607 |    3,079 |     3.2 |
| pdm                | likely             |  1,464 |   1,262 |    202 |        |      0 |    0 |  1,825 |    3,079 |     3.8 |
| pdm                | unsafe             |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |     6.5 |
| pdm                | infer-basedpyright |  1,895 |   1,248 |    220 |    427 |      0 |    2 |  2,256 |    3,079 |    24.2 |
| pdm                | infer-ty           |  1,902 |   1,248 |    221 |    433 |      0 |    0 |  2,263 |    3,079 |    15.7 |
| pdm                | infer-pyrefly      |  1,760 |   1,248 |    211 |    301 |      0 |    0 |  2,121 |    3,079 |     9.6 |
| pdm                | infer-trace        |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |     4.6 |
| strawberry-graphql | certain            |    656 |     656 |        |        |      0 |    0 |  1,432 |    2,582 |     2.7 |
| strawberry-graphql | likely             |    830 |     658 |    172 |        |      0 |    0 |  1,606 |    2,582 |     4.8 |
| strawberry-graphql | unsafe             |    897 |     656 |    172 |     69 |      0 |    0 |  1,673 |    2,582 |     5.7 |
| strawberry-graphql | infer-basedpyright |  1,014 |     656 |    172 |    186 |      0 |    2 |  1,790 |    2,582 |    29.7 |
| strawberry-graphql | infer-ty           |  1,011 |     656 |    171 |    184 |      0 |    2 |  1,787 |    2,582 |    11.5 |
| strawberry-graphql | infer-pyrefly      |    948 |     656 |    172 |    120 |      0 |    0 |  1,724 |    2,582 |    15.0 |
| strawberry-graphql | infer-trace        |    897 |     656 |    172 |     69 |      0 |    0 |  1,673 |    2,582 |     4.8 |
| pygments           | certain            |    736 |     736 |        |        |      0 |    0 |    736 |    7,666 |     2.9 |
| pygments           | likely             |    817 |     739 |     78 |        |      0 |    0 |    817 |    7,666 |     3.7 |
| pygments           | unsafe             |  5,353 |     736 |     78 |  4,539 |      0 |    0 |  5,353 |    7,666 |     8.0 |
| pygments           | infer-basedpyright |  5,446 |     736 |     85 |  4,625 |      0 |    0 |  5,446 |    7,666 |    59.5 |
| pygments           | infer-ty           |  5,450 |     736 |     85 |  4,629 |      0 |    0 |  5,450 |    7,666 |    12.6 |
| pygments           | infer-pyrefly      |  5,514 |     736 |     85 |  4,693 |      0 |    4 |  5,514 |    7,666 |    18.6 |
| pygments           | infer-trace        |  5,463 |     731 |    103 |  4,629 |      0 |    0 |  5,463 |    7,666 |     8.3 |
| streamlink         | certain            |    701 |     701 |        |        |      0 |    0 |  2,963 |    5,291 |     2.1 |
| streamlink         | likely             |    838 |     704 |    134 |        |      0 |    0 |  3,100 |    5,291 |     3.5 |
| streamlink         | unsafe             |  1,280 |     701 |    134 |    445 |      0 |    0 |  3,542 |    5,291 |     6.3 |
| streamlink         | infer-basedpyright |  1,609 |     703 |    155 |    751 |      0 |    1 |  3,871 |    5,291 |    21.2 |
| streamlink         | infer-ty           |  1,776 |     702 |    167 |    907 |      0 |    2 |  4,038 |    5,291 |    13.5 |
| streamlink         | infer-pyrefly      |  1,424 |     702 |    146 |    576 |      0 |    0 |  3,686 |    5,291 |    12.6 |
| streamlink         | infer-trace        |  1,288 |     701 |    134 |    453 |      0 |    0 |  3,550 |    5,291 |     7.9 |
| sphinx             | certain            |  3,392 |   3,392 |        |        |      0 |    0 |  4,320 |    8,901 |     3.8 |
| sphinx             | likely             |  3,931 |   3,407 |    524 |        |      0 |    0 |  4,859 |    8,901 |     6.5 |
| sphinx             | unsafe             |  4,335 |   3,392 |    523 |    420 |      0 |    0 |  5,263 |    8,901 |     9.4 |
| sphinx             | infer-basedpyright |  5,092 |   3,393 |    551 |  1,148 |      0 |    0 |  6,020 |    8,901 |    30.0 |
| sphinx             | infer-ty           |  5,146 |   3,392 |    546 |  1,208 |      0 |    1 |  6,074 |    8,901 |    22.8 |
| sphinx             | infer-pyrefly      |  5,326 |   3,393 |    554 |  1,379 |      0 |    1 |  6,254 |    8,901 |    26.4 |
| sphinx             | infer-trace        |  4,335 |   3,392 |    523 |    420 |      0 |    0 |  5,263 |    8,901 |     8.0 |
| tox                | certain            |    985 |     985 |        |        |      0 |    0 |  1,321 |    2,098 |     1.7 |
| tox                | likely             |  1,088 |     986 |    102 |        |      0 |    0 |  1,424 |    2,098 |     2.2 |
| tox                | unsafe             |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     2.9 |
| tox                | infer-basedpyright |  1,359 |     987 |    118 |    254 |      0 |    2 |  1,695 |    2,098 |    13.3 |
| tox                | infer-ty           |  1,392 |     987 |    117 |    288 |      0 |    0 |  1,728 |    2,098 |     9.0 |
| tox                | infer-pyrefly      |  1,433 |     987 |    117 |    329 |      0 |    0 |  1,769 |    2,098 |     7.6 |
| tox                | infer-trace        |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     3.0 |
| pint               | certain            |    650 |     650 |        |        |      0 |    0 |    815 |    3,243 |     2.8 |
| pint               | likely             |    926 |     651 |    275 |        |      0 |    0 |  1,091 |    3,243 |     4.9 |
| pint               | unsafe             |    978 |     650 |    275 |     53 |      0 |    0 |  1,143 |    3,243 |    17.7 |
| pint               | infer-basedpyright |  1,206 |     651 |    283 |    272 |      0 |   15 |  1,371 |    3,243 |    64.8 |
| pint               | infer-ty           |  1,117 |     651 |    278 |    188 |      0 |   19 |  1,282 |    3,243 |    19.9 |
| pint               | infer-pyrefly      |  1,042 |     651 |    275 |    116 |      0 |    0 |  1,207 |    3,243 |    12.9 |
| pint               | infer-trace        |    985 |     650 |    275 |     60 |      0 |    0 |  1,150 |    3,243 |     4.6 |
| altair             | certain            |    389 |     389 |        |        |      0 |    0 |  2,071 |    3,383 |     8.7 |
| altair             | likely             |    441 |     389 |     52 |        |      0 |    0 |  2,123 |    3,383 |    10.4 |
| altair             | unsafe             |    454 |     389 |     52 |     13 |      0 |    0 |  2,136 |    3,383 |    10.8 |
| altair             | infer-basedpyright |    523 |     389 |     55 |     79 |      0 |    0 |  2,205 |    3,383 |    47.2 |
| altair             | infer-ty           |    517 |     389 |     53 |     75 |      0 |    0 |  2,199 |    3,383 |    18.2 |
| altair             | infer-pyrefly      |    515 |     389 |     53 |     73 |      0 |    0 |  2,197 |    3,383 |    24.7 |
| altair             | infer-trace        |    461 |     389 |     53 |     19 |      0 |    0 |  2,143 |    3,383 |    10.2 |
| seaborn            | certain            |    657 |     657 |        |        |      0 |    0 |    872 |    3,110 |     8.6 |
| seaborn            | likely             |    821 |     664 |    157 |        |      0 |    0 |  1,036 |    3,110 |    11.0 |
| seaborn            | unsafe             |    899 |     657 |    156 |     86 |      0 |    0 |  1,114 |    3,110 |    25.1 |
| seaborn            | infer-basedpyright |  1,006 |     657 |    158 |    191 |      0 |    3 |  1,221 |    3,110 |    86.1 |
| seaborn            | infer-ty           |    983 |     656 |    158 |    169 |      0 |    0 |  1,198 |    3,110 |    13.2 |
| seaborn            | infer-pyrefly      |  1,092 |     657 |    149 |    286 |      0 |    0 |  1,307 |    3,110 |    23.6 |
| seaborn            | infer-trace        |    949 |     661 |    158 |    130 |      0 |    0 |  1,164 |    3,110 |    10.1 |
| aiohttp            | certain            |    722 |     722 |        |        |      0 |    0 |  1,298 |    2,433 |     2.0 |
| aiohttp            | likely             |    874 |     729 |    145 |        |      0 |    0 |  1,450 |    2,433 |     2.9 |
| aiohttp            | unsafe             |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     2.6 |
| aiohttp            | infer-basedpyright |  1,179 |     724 |    152 |    303 |      0 |    0 |  1,755 |    2,433 |    24.8 |
| aiohttp            | infer-ty           |  1,199 |     724 |    152 |    323 |      0 |    0 |  1,775 |    2,433 |    11.5 |
| aiohttp            | infer-pyrefly      |  1,300 |     724 |    157 |    419 |      0 |    0 |  1,876 |    2,433 |     4.3 |
| aiohttp            | infer-trace        |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     5.3 |
| websockets         | certain            |    362 |     362 |        |        |      0 |    0 |    489 |      918 |     0.7 |
| websockets         | likely             |    439 |     363 |     76 |        |      0 |    0 |    566 |      918 |     1.2 |
| websockets         | unsafe             |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     3.0 |
| websockets         | infer-basedpyright |    597 |     364 |     74 |    159 |      0 |    0 |    724 |      918 |    11.6 |
| websockets         | infer-ty           |    606 |     364 |     76 |    166 |      0 |    0 |    733 |      918 |     4.2 |
| websockets         | infer-pyrefly      |    605 |     364 |     76 |    165 |      0 |    0 |    732 |      918 |     6.3 |
| websockets         | infer-trace        |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     2.9 |
| anyio              | certain            |    230 |     230 |        |        |      0 |    0 |    505 |      990 |     1.3 |
| anyio              | likely             |    266 |     230 |     36 |        |      0 |    0 |    541 |      990 |     6.4 |
| anyio              | unsafe             |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     4.6 |
| anyio              | infer-basedpyright |    382 |     230 |     42 |    110 |      0 |    0 |    657 |      990 |    17.9 |
| anyio              | infer-ty           |    397 |     230 |     44 |    123 |      0 |    0 |    672 |      990 |     8.9 |
| anyio              | infer-pyrefly      |    387 |     230 |     42 |    115 |      0 |    0 |    662 |      990 |     7.4 |
| anyio              | infer-trace        |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     4.7 |
| zarr               | certain            |  1,169 |   1,169 |        |        |      0 |    0 |  1,837 |    3,079 |     2.5 |
| zarr               | likely             |  1,248 |   1,170 |     78 |        |      0 |    0 |  1,916 |    3,079 |     6.4 |
| zarr               | unsafe             |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     6.5 |
| zarr               | infer-basedpyright |  1,666 |   1,169 |     99 |    398 |      0 |    1 |  2,334 |    3,079 |    28.1 |
| zarr               | infer-ty           |  1,635 |   1,169 |     98 |    368 |      0 |    0 |  2,303 |    3,079 |    12.1 |
| zarr               | infer-pyrefly      |  1,477 |   1,169 |     86 |    222 |      0 |    0 |  2,145 |    3,079 |    12.5 |
| zarr               | infer-trace        |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     7.3 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     2.5 |
| joblib             | likely             |    704 |     526 |    178 |        |      0 |    0 |    705 |    2,241 |     3.8 |
| joblib             | unsafe             |    829 |     524 |    176 |    129 |      0 |    0 |    830 |    2,241 |     6.6 |
| joblib             | infer-basedpyright |    945 |     524 |    179 |    242 |      0 |    0 |    946 |    2,241 |    23.1 |
| joblib             | infer-ty           |    893 |     524 |    177 |    192 |      0 |    0 |    894 |    2,241 |     8.1 |
| joblib             | infer-pyrefly      |    940 |     522 |    179 |    239 |      0 |    0 |    941 |    2,241 |     7.6 |
| joblib             | infer-trace        |    841 |     524 |    178 |    139 |      0 |    0 |    842 |    2,241 |    10.5 |
| networkx           | certain            |  3,971 |   3,971 |        |        |      0 |    0 |  4,033 |   22,518 |    19.6 |
| networkx           | likely             |  6,179 |   3,985 |  2,194 |        |      0 |    0 |  6,241 |   22,518 |    30.1 |
| networkx           | unsafe             |  6,533 |   3,976 |  2,191 |    366 |      0 |    0 |  6,595 |   22,518 |    55.5 |
| networkx           | infer-basedpyright |  7,541 |   3,976 |  2,245 |  1,320 |      0 |    0 |  7,603 |   22,518 |   150.5 |
| networkx           | infer-ty           |  6,979 |   3,976 |  2,205 |    798 |      0 |    0 |  7,041 |   22,518 |    56.5 |
| networkx           | infer-pyrefly      |  7,092 |   3,978 |  2,213 |    901 |      0 |    1 |  7,154 |   22,518 |    70.1 |
| networkx           | infer-trace        |  6,954 |   3,976 |  2,215 |    763 |      0 |    0 |  7,016 |   22,518 |    22.8 |
| nibabel            | certain            |  1,871 |   1,871 |        |        |      0 |    0 |  1,953 |    8,550 |     5.8 |
| nibabel            | likely             |  2,712 |   1,888 |    824 |        |      0 |    0 |  2,794 |    8,550 |    10.1 |
| nibabel            | unsafe             |  3,046 |   1,871 |    820 |    355 |      0 |    0 |  3,128 |    8,550 |    12.8 |
| nibabel            | infer-basedpyright |  3,604 |   1,871 |    855 |    878 |      0 |    6 |  3,686 |    8,550 |    87.7 |
| nibabel            | infer-ty           |  3,587 |   1,871 |    875 |    841 |      0 |    8 |  3,669 |    8,550 |    56.2 |
| nibabel            | infer-pyrefly      |  3,627 |   1,869 |    835 |    923 |      0 |    0 |  3,709 |    8,550 |    25.5 |
| nibabel            | infer-trace        |  3,124 |   1,872 |    826 |    426 |      0 |    0 |  3,206 |    8,550 |     8.2 |
| narwhals           | certain            |  1,082 |   1,082 |        |        |      0 |    0 |  1,947 |    3,985 |     4.1 |
| narwhals           | likely             |  1,158 |   1,083 |     75 |        |      0 |    0 |  2,023 |    3,985 |    10.5 |
| narwhals           | unsafe             |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |    32.0 |
| narwhals           | infer-basedpyright |  1,516 |   1,082 |     87 |    347 |      0 |    5 |  2,381 |    3,985 |    51.5 |
| narwhals           | infer-ty           |  1,492 |   1,082 |     97 |    313 |      0 |    1 |  2,357 |    3,985 |    37.2 |
| narwhals           | infer-pyrefly      |  1,721 |   1,082 |     92 |    547 |      0 |    2 |  2,586 |    3,985 |    44.6 |
| narwhals           | infer-trace        |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |     8.1 |
| xarray             | certain            |  4,623 |   4,623 |        |        |      0 |    0 |  5,652 |   22,373 |    30.2 |
| xarray             | likely             |  9,775 |   4,679 |  5,096 |        |      0 |    0 | 10,804 |   22,373 |    61.0 |
| xarray             | unsafe             | 10,151 |   4,623 |  5,089 |    439 |      0 |    0 | 11,180 |   22,373 |    39.1 |
| xarray             | infer-basedpyright | 12,649 |   4,623 |  5,143 |  2,883 |      0 |    0 | 13,678 |   22,373 |   174.7 |
| xarray             | infer-ty           | 12,678 |   4,623 |  5,134 |  2,921 |      0 |    2 | 13,707 |   22,373 |    84.8 |
| xarray             | infer-pyrefly      | 10,838 |   4,624 |  5,074 |  1,140 |      0 |    0 | 11,867 |   22,373 |    76.6 |
| xarray             | infer-trace        | 10,170 |   4,623 |  5,088 |    459 |      0 |    0 | 11,199 |   22,373 |    60.0 |
| litestar           | certain            |    648 |     648 |        |        |      0 |    0 |  2,202 |    3,459 |     3.8 |
| litestar           | likely             |    772 |     650 |    122 |        |      0 |    0 |  2,326 |    3,459 |     7.6 |
| litestar           | unsafe             |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     7.5 |
| litestar           | infer-basedpyright |  1,039 |     648 |    130 |    261 |      0 |    1 |  2,593 |    3,459 |    20.8 |
| litestar           | infer-ty           |  1,051 |     648 |    133 |    270 |      0 |    0 |  2,605 |    3,459 |    32.8 |
| litestar           | infer-pyrefly      |    931 |     648 |    126 |    157 |      0 |    0 |  2,485 |    3,459 |    31.9 |
| litestar           | infer-trace        |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     5.4 |
| stripe             | certain            |    781 |     781 |        |        |      0 |    0 | 29,531 |   32,107 |     8.1 |
| stripe             | likely             |    947 |     781 |    166 |        |      0 |    0 | 29,697 |   32,107 |     8.5 |
| stripe             | unsafe             |  1,452 |     781 |    166 |    505 |      0 |    0 | 30,202 |   32,107 |     8.6 |
| stripe             | infer-basedpyright |  2,158 |     781 |    161 |  1,216 |      0 |    0 | 30,908 |   32,107 |  1389.5 |
| stripe             | infer-ty           |  1,499 |     781 |    161 |    557 |      0 |    0 | 30,249 |   32,107 |    23.4 |
| stripe             | infer-pyrefly      |  1,488 |     781 |    164 |    543 |      0 |    0 | 30,238 |   32,107 |    27.9 |
| celery             | certain            |    508 |     508 |        |        |      0 |    0 |    524 |    3,764 |    12.4 |
| celery             | likely             |    638 |     510 |    128 |        |      0 |    0 |    654 |    3,764 |    12.2 |
| celery             | unsafe             |    880 |     508 |    128 |    244 |      0 |    0 |    896 |    3,764 |    14.6 |
| celery             | infer-basedpyright |  1,036 |     508 |    137 |    391 |      0 |   10 |  1,052 |    3,764 |    43.4 |
| celery             | infer-ty           |    950 |     508 |    129 |    313 |      0 |    0 |    966 |    3,764 |    24.5 |
| celery             | infer-pyrefly      |    988 |     508 |    129 |    351 |      0 |    0 |  1,004 |    3,764 |    37.8 |
| celery             | infer-trace        |    946 |     508 |    127 |    311 |      0 |    0 |    962 |    3,764 |    20.7 |
| optuna             | certain            |  1,583 |   1,583 |        |        |      0 |    0 |  1,874 |    3,889 |    12.1 |
| optuna             | likely             |  1,802 |   1,591 |    211 |        |      0 |    0 |  2,093 |    3,889 |    20.7 |
| optuna             | unsafe             |  1,910 |   1,583 |    211 |    116 |      0 |    0 |  2,201 |    3,889 |    23.7 |
| optuna             | infer-basedpyright |  2,196 |   1,583 |    222 |    391 |      0 |   11 |  2,487 |    3,889 |    51.8 |
| optuna             | infer-ty           |  2,233 |   1,583 |    240 |    410 |      0 |    6 |  2,524 |    3,889 |    64.9 |
| optuna             | infer-pyrefly      |  2,194 |   1,583 |    227 |    384 |      0 |    6 |  2,485 |    3,889 |    31.2 |
| optuna             | infer-trace        |  1,910 |   1,583 |    211 |    116 |      0 |    0 |  2,201 |    3,889 |     7.2 |
| dask               | certain            |  3,161 |   3,161 |        |        |      0 |    0 |  3,419 |   24,430 |    32.9 |
| dask               | likely             |  5,147 |   3,204 |  1,943 |        |      0 |    0 |  5,405 |   24,430 |    59.8 |
| dask               | unsafe             |  6,068 |   3,169 |  1,940 |    959 |      0 |    0 |  6,326 |   24,430 |    71.5 |
| dask               | infer-basedpyright |  6,823 |   3,169 |  1,959 |  1,695 |      0 |    9 |  7,081 |   24,430 |   168.0 |
| dask               | infer-ty           |  6,543 |   3,169 |  1,932 |  1,442 |      0 |    0 |  6,801 |   24,430 |    94.5 |
| dask               | infer-pyrefly      |  7,003 |   3,173 |  1,950 |  1,880 |      0 |    2 |  7,261 |   24,430 |    98.9 |
| dask               | infer-trace        |  6,231 |   3,166 |  1,943 |  1,122 |      0 |    0 |  6,489 |   24,430 |    24.5 |
| mypy               | certain            |  5,142 |   5,142 |        |        |      0 |    0 |  7,442 |   13,701 |     6.6 |
| mypy               | likely             |  6,351 |   5,172 |  1,179 |        |      0 |    0 |  8,651 |   13,701 |    16.2 |
| mypy               | unsafe             |  6,758 |   5,142 |  1,177 |    439 |      0 |    0 |  9,057 |   13,701 |    14.7 |
| mypy               | infer-basedpyright |  8,392 |   5,143 |  1,291 |  1,958 |      0 |    4 | 10,690 |   13,701 |    47.1 |
| mypy               | infer-ty           |  8,696 |   5,142 |  1,293 |  2,261 |      0 |    3 | 10,994 |   13,701 |    19.1 |
| mypy               | infer-pyrefly      |  8,915 |   5,139 |  1,299 |  2,477 |      0 |    4 | 11,213 |   13,701 |    19.8 |
| mypy               | infer-trace        |  6,758 |   5,142 |  1,177 |    439 |      0 |    0 |  9,057 |   13,701 |     9.8 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms               |  fixed | certain | likely |  guess |
| ------------------ | ------------------------ | -----: | ------: | -----: | -----: |
| certain            | literal                  | 23,998 |  23,998 |        |        |
| certain            | stdlib                   | 16,072 |  16,072 |        |        |
| certain            | call                     | 10,879 |  10,879 |        |        |
| certain            | container+literal        |  6,846 |   6,846 |        |        |
| certain            | builtin                  |  4,402 |   4,402 |        |        |
| certain            | method                   |  4,358 |   4,358 |        |        |
| certain            | loop                     |  3,942 |   3,942 |        |        |
| certain            | copy+loop                |  3,690 |   3,690 |        |        |
| certain            | container+literal+loop   |  2,079 |   2,079 |        |        |
| certain            | literal+method           |  1,616 |   1,616 |        |        |
| certain            | call+unpack              |  1,601 |   1,601 |        |        |
| certain            | open                     |  1,493 |   1,493 |        |        |
| likely             | constructor              | 38,146 |     257 | 37,889 |        |
| likely             | literal                  | 24,006 |  24,006 |        |        |
| likely             | stdlib                   | 16,172 |  16,172 |        |        |
| likely             | call                     | 11,526 |  10,892 |    634 |        |
| likely             | container+literal        |  6,846 |   6,846 |        |        |
| likely             | method                   |  6,191 |   4,395 |  1,796 |        |
| likely             | builtin                  |  4,403 |   4,403 |        |        |
| likely             | copy+loop                |  4,282 |   3,717 |    565 |        |
| likely             | loop                     |  3,946 |   3,946 |        |        |
| likely             | container+literal+loop   |  2,079 |   2,079 |        |        |
| likely             | literal+method           |  1,616 |   1,616 |        |        |
| likely             | call+unpack              |  1,601 |   1,601 |        |        |
| unsafe             | constructor              | 38,139 |     257 | 37,882 |        |
| unsafe             | literal                  | 24,001 |  23,996 |        |      5 |
| unsafe             | stdlib                   | 16,631 |  16,074 |        |    557 |
| unsafe             | call                     | 11,512 |  10,879 |    633 |        |
| unsafe             | literal+member           |  7,834 |         |        |  7,834 |
| unsafe             | container+literal        |  6,846 |   6,846 |        |        |
| unsafe             | method                   |  6,155 |   4,359 |  1,796 |        |
| unsafe             | builtin                  |  4,404 |   4,402 |        |      2 |
| unsafe             | copy+loop                |  4,252 |   3,690 |    562 |        |
| unsafe             | loop                     |  3,942 |   3,942 |        |        |
| unsafe             | returned                 |  3,858 |   1,189 |        |  2,669 |
| unsafe             | container+literal+member |  3,044 |         |        |  3,044 |
| infer-basedpyright | constructor              | 38,072 |     256 | 37,816 |        |
| infer-basedpyright | checker                  | 25,858 |         |        | 25,858 |
| infer-basedpyright | literal                  | 24,003 |  23,998 |        |      5 |
| infer-basedpyright | stdlib                   | 16,744 |  16,016 |        |    728 |
| infer-basedpyright | call                     | 11,636 |  10,876 |    760 |        |
| infer-basedpyright | literal+member           |  7,833 |         |        |  7,833 |
| infer-basedpyright | container+literal        |  6,848 |   6,848 |        |        |
| infer-basedpyright | method                   |  6,403 |   4,358 |  2,045 |        |
| infer-basedpyright | copy+loop                |  4,824 |   3,691 |  1,133 |        |
| infer-basedpyright | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-basedpyright | returned                 |  4,059 |   1,169 |        |  2,890 |
| infer-basedpyright | loop                     |  3,942 |   3,942 |        |        |
| infer-ty           | constructor              | 38,071 |     257 | 37,814 |        |
| infer-ty           | literal                  | 24,002 |  23,997 |        |      5 |
| infer-ty           | checker                  | 21,192 |         |        | 21,192 |
| infer-ty           | stdlib                   | 16,743 |  16,037 |        |    706 |
| infer-ty           | call                     | 11,587 |  10,877 |    710 |        |
| infer-ty           | literal+member           |  7,834 |         |        |  7,834 |
| infer-ty           | container+literal        |  6,847 |   6,847 |        |        |
| infer-ty           | method                   |  6,363 |   4,358 |  2,005 |        |
| infer-ty           | copy+loop                |  4,739 |   3,691 |  1,048 |        |
| infer-ty           | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-ty           | returned                 |  4,008 |   1,190 |        |  2,818 |
| infer-ty           | loop                     |  3,942 |   3,942 |        |        |
| infer-pyrefly      | constructor              | 38,011 |     256 | 37,755 |        |
| infer-pyrefly      | checker                  | 24,538 |         |        | 24,538 |
| infer-pyrefly      | literal                  | 24,002 |  23,997 |        |      5 |
| infer-pyrefly      | stdlib                   | 16,764 |  16,028 |        |    736 |
| infer-pyrefly      | call                     | 11,564 |  10,877 |    687 |        |
| infer-pyrefly      | literal+member           |  7,833 |         |        |  7,833 |
| infer-pyrefly      | container+literal        |  6,853 |   6,853 |        |        |
| infer-pyrefly      | method                   |  6,308 |   4,358 |  1,950 |        |
| infer-pyrefly      | copy+loop                |  4,751 |   3,690 |  1,061 |        |
| infer-pyrefly      | builtin                  |  4,404 |   4,402 |        |      2 |
| infer-pyrefly      | returned                 |  4,028 |   1,187 |        |  2,841 |
| infer-pyrefly      | loop                     |  3,942 |   3,942 |        |        |
| infer-trace        | constructor              | 30,603 |      25 | 30,578 |        |
| infer-trace        | literal                  | 13,903 |  13,901 |        |      2 |
| infer-trace        | call                     | 10,691 |  10,105 |    586 |        |
| infer-trace        | literal+member           |  5,572 |         |        |  5,572 |
| infer-trace        | method                   |  5,474 |   3,764 |  1,710 |        |
| infer-trace        | container+literal        |  4,351 |   4,351 |        |        |
| infer-trace        | stdlib                   |  4,114 |   3,898 |        |    216 |
| infer-trace        | traced                   |  3,203 |         |        |  3,203 |
| infer-trace        | copy+loop                |  2,736 |   2,373 |    363 |        |
| infer-trace        | container+literal+member |  2,643 |         |        |  2,643 |
| infer-trace        | builtin                  |  2,617 |   2,615 |        |      2 |
| infer-trace        | loop                     |  2,024 |   2,024 |        |        |
| infer-union        | constructor              | 30,462 |      25 | 30,437 |        |
| infer-union        | agreed+checker           | 14,491 |         | 14,491 |        |
| infer-union        | literal                  | 13,904 |  13,902 |        |      2 |
| infer-union        | checker                  | 11,618 |         |        | 11,618 |
| infer-union        | call                     | 10,776 |  10,102 |    674 |        |
| infer-union        | method                   |  5,706 |   3,758 |  1,948 |        |
| infer-union        | literal+member           |  5,572 |         |        |  5,572 |
| infer-union        | container+literal        |  4,358 |   4,358 |        |        |
| infer-union        | stdlib                   |  4,105 |   3,881 |        |    224 |
| infer-union        | traced                   |  3,147 |         |        |  3,147 |
| infer-union        | copy+loop                |  3,137 |   2,373 |    764 |        |
| infer-union        | container+literal+member |  2,643 |         |        |  2,643 |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  14,231 |  62,055 |        0 |
| django             |  17,176 |   2,891 |  11,660 |        0 |
| sqlalchemy         |  12,932 |   1,153 |   9,634 |        0 |
| pydantic           |   3,117 |     413 |   1,505 |        0 |
| pandas             |  77,793 |  25,591 |  35,014 |        0 |
| twisted            |  17,874 |   4,826 |  10,613 |        0 |
| pip                |   8,923 |   1,343 |   5,337 |        0 |
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
| cattrs             |     520 |      44 |     364 |        0 |
| pytest             |   3,000 |     313 |   1,312 |        0 |
| botocore           |   3,786 |     656 |   2,582 |        0 |
| uvicorn            |     489 |      57 |     196 |        0 |
| mcp                |   1,720 |     248 |     754 |        0 |
| textual            |   6,483 |     773 |   2,914 |        0 |
| pdm                |   2,713 |     364 |   1,103 |        0 |
| strawberry-graphql |   1,806 |     241 |     909 |        0 |
| pygments           |   7,666 |   4,617 |   2,313 |        0 |
| streamlink         |   3,029 |     579 |   1,749 |        0 |
| sphinx             |   7,972 |     943 |   3,638 |        0 |
| tox                |   1,762 |     158 |     619 |        0 |
| pint               |   3,078 |     323 |   2,105 |        0 |
| altair             |   1,700 |      65 |   1,246 |        0 |
| seaborn            |   2,895 |     242 |   1,996 |        0 |
| aiohttp            |   1,857 |     274 |     861 |        0 |
| websockets         |     791 |     130 |     299 |        0 |
| anyio              |     715 |      69 |     416 |        0 |
| zarr               |   2,411 |     118 |   1,124 |        0 |
| joblib             |   2,239 |     304 |   1,410 |        0 |
| networkx           |  22,456 |   2,503 |  15,982 |        0 |
| nibabel            |   8,466 |   1,175 |   5,420 |        0 |
| narwhals           |   3,112 |     130 |   1,900 |        0 |
| xarray             |  21,344 |   5,525 |  11,196 |        0 |
| litestar           |   1,905 |     198 |   1,059 |        0 |
| stripe             |   3,357 |     671 |   1,905 |        0 |
| celery             |   3,747 |     372 |   2,867 |        0 |
| optuna             |   3,595 |     327 |   1,685 |        0 |
| dask               |  24,171 |   2,772 |  18,238 |        0 |
| mypy               |  11,401 |   1,615 |   4,645 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by | beside other steps |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: | -----------------: |
| standard library   |    4 |      152.16 |     60.35 |    1 |                       880.2 |     927.6 | hyperfine |                yes |
| django             |    4 |       17.78 |      8.37 |    1 |                       185.3 |     198.7 | hyperfine |                yes |
| sqlalchemy         |    4 |       17.34 |      9.76 |    1 |                       162.1 |     170.1 | hyperfine |                yes |
| pydantic           |    4 |        2.42 |      1.61 |    1 |                        30.6 |      33.4 | hyperfine |                yes |
| pandas             |    4 |       197.0 |     53.56 |    1 |                      1105.3 |    1137.7 | hyperfine |                yes |
| twisted            |    4 |       21.78 |     11.32 |    1 |                       126.4 |     136.4 | hyperfine |                yes |
| pip                |    4 |        9.01 |      4.63 |    1 |                        89.5 |      95.9 | hyperfine |                yes |
| structlog          |    4 |         0.7 |      1.09 |    1 |                         4.9 |       6.2 | hyperfine |                yes |
| attrs              |    4 |        0.59 |      1.12 |    1 |                         3.7 |       4.8 | hyperfine |                yes |
| click              |    4 |        1.83 |      1.22 |    1 |                         7.2 |       8.4 | hyperfine |                yes |
| hypercorn          |    4 |        1.11 |      1.77 |    1 |                         7.9 |       7.1 | hyperfine |                yes |
| starlette          |    4 |        0.72 |      0.67 |    1 |                         7.2 |       8.8 | hyperfine |                yes |
| werkzeug           |    4 |        1.57 |      0.88 |    1 |                        14.0 |      15.5 | hyperfine |                yes |
| mkdocs             |    4 |        1.72 |      1.23 |    1 |                        16.4 |      19.0 | hyperfine |                yes |
| httpx              |    4 |        0.69 |      0.78 |    1 |                         7.2 |       8.5 | hyperfine |                yes |
| black              |    4 |        1.06 |      0.75 |    1 |                        10.4 |      11.8 | hyperfine |                yes |
| fastapi            |    4 |        1.42 |      1.23 |    1 |                        12.6 |      14.6 | hyperfine |                yes |
| cattrs             |    4 |        0.61 |      0.84 |    1 |                         7.1 |       8.7 | hyperfine |                yes |
| pytest             |    4 |        2.82 |      1.44 |    1 |                        26.5 |      29.2 | hyperfine |                yes |
| botocore           |    4 |        3.67 |      2.38 |    1 |                        35.8 |      38.7 | hyperfine |                yes |
| uvicorn            |    4 |        0.88 |      0.79 |    1 |                         8.3 |       9.8 | hyperfine |                yes |
| mcp                |    4 |        2.41 |      1.63 |    1 |                        20.9 |      23.6 | hyperfine |                yes |
| textual            |    4 |        5.08 |      2.28 |    1 |                        47.3 |      51.5 | hyperfine |                yes |
| pdm                |    4 |        3.19 |      3.17 |    1 |                        33.9 |      37.9 | hyperfine |                yes |
| strawberry-graphql |    4 |        2.75 |      1.86 |    1 |                        32.6 |      37.1 | hyperfine |                yes |
| pygments           |    4 |        4.81 |      3.26 |    1 |                        64.8 |      68.8 | hyperfine |                yes |
| streamlink         |    4 |        3.97 |      2.57 |    1 |                        38.8 |      42.0 | hyperfine |                yes |
| sphinx             |    4 |        7.42 |      2.95 |    1 |                        79.5 |      82.7 | hyperfine |                yes |
| tox                |    4 |        2.24 |      1.06 |    1 |                        19.2 |      20.5 | hyperfine |                yes |
| pint               |    4 |        3.04 |      2.43 |    1 |                        35.2 |      40.4 | hyperfine |                yes |
| altair             |    4 |        5.71 |      5.95 |    1 |                        69.7 |      78.8 | hyperfine |                yes |
| seaborn            |    4 |         5.2 |       5.1 |    1 |                        61.0 |      73.5 | hyperfine |                yes |
| aiohttp            |    4 |         2.4 |      1.45 |    1 |                        22.7 |      24.7 | hyperfine |                yes |
| websockets         |    4 |        0.97 |      0.63 |    1 |                        10.5 |      12.5 | hyperfine |                yes |
| anyio              |    4 |        1.03 |      0.88 |    1 |                        12.1 |      13.7 | hyperfine |                yes |
| zarr               |    4 |         3.0 |      1.83 |    1 |                        28.9 |      32.2 | hyperfine |                yes |
| joblib             |    4 |        2.11 |      2.07 |    1 |                        26.5 |      30.7 | hyperfine |                yes |
| networkx           |    4 |       31.53 |     13.71 |    1 |                       255.9 |     256.0 | hyperfine |                yes |
| nibabel            |    4 |        7.67 |      4.34 |    1 |                        78.2 |      89.6 | hyperfine |                yes |
| narwhals           |    4 |        5.44 |      2.93 |    1 |                        63.5 |      73.1 | hyperfine |                yes |
| xarray             |    4 |       34.84 |     18.89 |    1 |                       297.0 |     315.6 | hyperfine |                yes |
| litestar           |    4 |        4.07 |      2.51 |    1 |                        39.8 |      44.5 | hyperfine |                yes |
| stripe             |    4 |       22.41 |     10.97 |    1 |                       152.5 |     159.4 | hyperfine |                yes |
| celery             |    4 |        8.24 |      6.19 |    1 |                        78.8 |      89.0 | hyperfine |                yes |
| optuna             |    4 |         7.6 |      4.43 |    1 |                        73.5 |      79.1 | hyperfine |                yes |
| dask               |    4 |       41.67 |     24.38 |    1 |                       422.4 |     442.6 | hyperfine |                yes |
| mypy               |    4 |       10.81 |      4.14 |    1 |                        98.6 |     101.7 | hyperfine |                yes |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier                |   told |   held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------------------- | -----: | -----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| django             |                     |        |        |          |                  487 |          Ran 17585 tests: FAILED (failures=5, skipped=1149, expected failures=5) |   100.1 |     65.1 |
| django             | certain             |    981 |    980 |        1 |                      |                                                                                  |         |          |
| django             | likely              |    340 |    339 |        1 |                      |                                                                                  |         |          |
| django             | guess               |    400 |    383 |       17 |                      |                                                                                  |         |          |
| django             | infer-union certain |    966 |    965 |        1 |                      |                                                                                  |         |          |
| django             | infer-union likely  |    563 |    553 |       10 |                      |                                                                                  |         |          |
| django             | infer-union guess   |    738 |    710 |       28 |                      |                                                                                  |         |          |
| sqlalchemy         |                     |        |        |          |                  151 |                                             29521 passed, 975 skipped, 1 warning |   103.3 |    127.1 |
| sqlalchemy         | certain             |  1,189 |  1,166 |       23 |                      |                                                                                  |         |          |
| sqlalchemy         | likely              |    186 |    182 |        4 |                      |                                                                                  |         |          |
| sqlalchemy         | guess               |    137 |    134 |        3 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union certain |  1,190 |  1,167 |       23 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union likely  |    502 |    490 |       12 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union guess   |    409 |    396 |       13 |                      |                                                                                  |         |          |
| pydantic           |                     |        |        |          |                    1 |                                  65 failed, 6900 passed, 350 skipped, 29 xfailed |    77.5 |     68.4 |
| pydantic           | certain             |    533 |    528 |        5 |                      |                                                                                  |         |          |
| pydantic           | likely              |     49 |     49 |        0 |                      |                                                                                  |         |          |
| pydantic           | guess               |     31 |     31 |        0 |                      |                                                                                  |         |          |
| pydantic           | infer-union certain |    533 |    528 |        5 |                      |                                                                                  |         |          |
| pydantic           | infer-union likely  |     84 |     84 |        0 |                      |                                                                                  |         |          |
| pydantic           | infer-union guess   |    108 |    108 |        0 |                      |                                                                                  |         |          |
| pandas             |                     |        |        |          |                1,553 |                            165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   155.5 |    110.6 |
| pandas             | certain             | 13,074 | 12,970 |      104 |                      |                                                                                  |         |          |
| pandas             | likely              | 20,795 | 20,717 |       78 |                      |                                                                                  |         |          |
| pandas             | guess               |  1,088 |  1,044 |       44 |                      |                                                                                  |         |          |
| pandas             | infer-union certain | 13,072 | 12,968 |      104 |                      |                                                                                  |         |          |
| pandas             | infer-union likely  | 24,525 | 24,349 |      176 |                      |                                                                                  |         |          |
| pandas             | infer-union guess   |  5,177 |  4,484 |      693 |                      |                                                                                  |         |          |
| structlog          |                     |        |        |          |                    0 |                                    24 failed, 860 passed, 37 skipped, 2 warnings |     1.8 |      2.7 |
| structlog          | certain             |     64 |     64 |        0 |                      |                                                                                  |         |          |
| structlog          | likely              |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess               |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union certain |     64 |     64 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union likely  |     16 |     16 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| attrs              |                     |        |        |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     3.8 |      2.5 |
| attrs              | certain             |     72 |     72 |        0 |                      |                                                                                  |         |          |
| attrs              | likely              |      8 |      8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess               |      4 |      4 |        0 |                      |                                                                                  |         |          |
| attrs              | infer-union certain |     72 |     72 |        0 |                      |                                                                                  |         |          |
| attrs              | infer-union likely  |     14 |     12 |        2 |                      |                                                                                  |         |          |
| attrs              | infer-union guess   |     15 |     15 |        0 |                      |                                                                                  |         |          |
| click              |                     |        |        |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     8.7 |      8.2 |
| click              | certain             |    229 |    229 |        0 |                      |                                                                                  |         |          |
| click              | likely              |     18 |     17 |        1 |                      |                                                                                  |         |          |
| click              | guess               |     26 |     26 |        0 |                      |                                                                                  |         |          |
| click              | infer-union certain |    229 |    229 |        0 |                      |                                                                                  |         |          |
| click              | infer-union likely  |     76 |     75 |        1 |                      |                                                                                  |         |          |
| click              | infer-union guess   |     38 |     38 |        0 |                      |                                                                                  |         |          |
| hypercorn          |                     |        |        |          |                    0 |                                                             2 failed, 194 passed |     8.4 |      8.7 |
| hypercorn          | certain             |     63 |     63 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely              |     12 |     12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess               |     11 |     11 |        0 |                      |                                                                                  |         |          |
| hypercorn          | infer-union certain |     63 |     63 |        0 |                      |                                                                                  |         |          |
| hypercorn          | infer-union likely  |     20 |     20 |        0 |                      |                                                                                  |         |          |
| hypercorn          | infer-union guess   |     21 |     21 |        0 |                      |                                                                                  |         |          |
| starlette          |                     |        |        |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |    17.4 |     19.5 |
| starlette          | certain             |    200 |    199 |        1 |                      |                                                                                  |         |          |
| starlette          | likely              |     63 |     63 |        0 |                      |                                                                                  |         |          |
| starlette          | guess               |     31 |     31 |        0 |                      |                                                                                  |         |          |
| starlette          | infer-union certain |    200 |    199 |        1 |                      |                                                                                  |         |          |
| starlette          | infer-union likely  |    101 |    101 |        0 |                      |                                                                                  |         |          |
| starlette          | infer-union guess   |     52 |     52 |        0 |                      |                                                                                  |         |          |
| werkzeug           |                     |        |        |          |                    0 |                                       1 failed, 979 passed, 1 skipped, 1 warning |    14.0 |     10.6 |
| werkzeug           | certain             |    366 |    362 |        4 |                      |                                                                                  |         |          |
| werkzeug           | likely              |     49 |     49 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess               |     34 |     34 |        0 |                      |                                                                                  |         |          |
| werkzeug           | infer-union certain |    367 |    363 |        4 |                      |                                                                                  |         |          |
| werkzeug           | infer-union likely  |    123 |    123 |        0 |                      |                                                                                  |         |          |
| werkzeug           | infer-union guess   |     81 |     81 |        0 |                      |                                                                                  |         |          |
| mkdocs             |                     |        |        |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    11.5 |     10.5 |
| mkdocs             | certain             |    643 |    642 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely              |    378 |    378 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess               |    129 |    129 |        0 |                      |                                                                                  |         |          |
| mkdocs             | infer-union certain |    643 |    642 |        1 |                      |                                                                                  |         |          |
| mkdocs             | infer-union likely  |    444 |    443 |        1 |                      |                                                                                  |         |          |
| mkdocs             | infer-union guess   |    226 |    226 |        0 |                      |                                                                                  |         |          |
| httpx              |                     |        |        |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |     8.7 |     10.2 |
| httpx              | certain             |    187 |    187 |        0 |                      |                                                                                  |         |          |
| httpx              | likely              |     50 |     50 |        0 |                      |                                                                                  |         |          |
| httpx              | guess               |     16 |     16 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union certain |    188 |    188 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union likely  |     95 |     95 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union guess   |     52 |     52 |        0 |                      |                                                                                  |         |          |
| black              |                     |        |        |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |     5.9 |      5.8 |
| black              | certain             |    606 |    606 |        0 |                      |                                                                                  |         |          |
| black              | likely              |    103 |    103 |        0 |                      |                                                                                  |         |          |
| black              | guess               |     42 |     42 |        0 |                      |                                                                                  |         |          |
| black              | infer-union certain |    606 |    606 |        0 |                      |                                                                                  |         |          |
| black              | infer-union likely  |    139 |    139 |        0 |                      |                                                                                  |         |          |
| black              | infer-union guess   |     71 |     69 |        2 |                      |                                                                                  |         |          |
| fastapi            |                     |        |        |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    24.4 |     14.5 |
| fastapi            | certain             |    215 |    215 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely              |     32 |     32 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess               |     23 |     23 |        0 |                      |                                                                                  |         |          |
| fastapi            | infer-union certain |    215 |    215 |        0 |                      |                                                                                  |         |          |
| fastapi            | infer-union likely  |     52 |     52 |        0 |                      |                                                                                  |         |          |
| fastapi            | infer-union guess   |     59 |     59 |        0 |                      |                                                                                  |         |          |
| cattrs             |                     |        |        |          |                    0 |                                                           994 passed, 15 xfailed |    22.7 |     20.6 |
| cattrs             | certain             |    105 |    103 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely              |     23 |     23 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess               |     19 |     19 |        0 |                      |                                                                                  |         |          |
| cattrs             | infer-union certain |    102 |    100 |        2 |                      |                                                                                  |         |          |
| cattrs             | infer-union likely  |     61 |     58 |        3 |                      |                                                                                  |         |          |
| cattrs             | infer-union guess   |     39 |     39 |        0 |                      |                                                                                  |         |          |
| pytest             |                     |        |        |          |                   14 |              46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    53.2 |     22.3 |
| pytest             | certain             |  1,116 |  1,104 |       12 |                      |                                                                                  |         |          |
| pytest             | likely              |    125 |    125 |        0 |                      |                                                                                  |         |          |
| pytest             | guess               |    120 |    120 |        0 |                      |                                                                                  |         |          |
| pytest             | infer-union certain |  1,116 |  1,104 |       12 |                      |                                                                                  |         |          |
| pytest             | infer-union likely  |    367 |    366 |        1 |                      |                                                                                  |         |          |
| pytest             | infer-union guess   |    223 |    223 |        0 |                      |                                                                                  |         |          |
| botocore           |                     |        |        |          |                  290 |                                                7 failed, 4593 passed, 96 skipped |    32.7 |     29.1 |
| botocore           | certain             |    331 |    330 |        1 |                      |                                                                                  |         |          |
| botocore           | likely              |    147 |    147 |        0 |                      |                                                                                  |         |          |
| botocore           | guess               |    136 |    128 |        8 |                      |                                                                                  |         |          |
| botocore           | infer-union certain |    328 |    327 |        1 |                      |                                                                                  |         |          |
| botocore           | infer-union likely  |    207 |    206 |        1 |                      |                                                                                  |         |          |
| botocore           | infer-union guess   |    237 |    228 |        9 |                      |                                                                                  |         |          |
| uvicorn            |                     |        |        |          |                    0 |                                                          1350 passed, 12 skipped |    31.4 |     30.1 |
| uvicorn            | certain             |    171 |    167 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely              |     27 |     27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess               |     16 |     16 |        0 |                      |                                                                                  |         |          |
| uvicorn            | infer-union certain |    171 |    167 |        4 |                      |                                                                                  |         |          |
| uvicorn            | infer-union likely  |     63 |     60 |        3 |                      |                                                                                  |         |          |
| uvicorn            | infer-union guess   |     32 |     31 |        1 |                      |                                                                                  |         |          |
| mcp                |                     |        |        |          |                    0 |                                      3 failed, 6092 passed, 8 skipped, 1 xfailed |    24.9 |     12.7 |
| mcp                | certain             |    530 |    530 |        0 |                      |                                                                                  |         |          |
| mcp                | likely              |    135 |    134 |        1 |                      |                                                                                  |         |          |
| mcp                | guess               |     59 |     58 |        1 |                      |                                                                                  |         |          |
| mcp                | infer-union certain |    530 |    530 |        0 |                      |                                                                                  |         |          |
| mcp                | infer-union likely  |    223 |    221 |        2 |                      |                                                                                  |         |          |
| mcp                | infer-union guess   |     93 |     92 |        1 |                      |                                                                                  |         |          |
| pdm                |                     |        |        |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    24.7 |     20.0 |
| pdm                | certain             |    933 |    930 |        3 |                      |                                                                                  |         |          |
| pdm                | likely              |    136 |    136 |        0 |                      |                                                                                  |         |          |
| pdm                | guess               |    100 |     99 |        1 |                      |                                                                                  |         |          |
| pdm                | infer-union certain |    933 |    930 |        3 |                      |                                                                                  |         |          |
| pdm                | infer-union likely  |    330 |    330 |        0 |                      |                                                                                  |         |          |
| pdm                | infer-union guess   |    183 |    181 |        2 |                      |                                                                                  |         |          |
| strawberry-graphql |                     |        |        |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    17.5 |     14.5 |
| strawberry-graphql | certain             |    415 |    409 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | likely              |     99 |     98 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql | guess               |     42 |     42 |        0 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union certain |    415 |    409 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union likely  |    158 |    155 |        3 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union guess   |     60 |     59 |        1 |                      |                                                                                  |         |          |
| pygments           |                     |        |        |          |                   89 |                                                          5330 passed, 16 skipped |    29.9 |     21.3 |
| pygments           | certain             |    291 |    291 |        0 |                      |                                                                                  |         |          |
| pygments           | likely              |     61 |     61 |        0 |                      |                                                                                  |         |          |
| pygments           | guess               |     90 |     90 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union certain |    286 |    286 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union likely  |    126 |    126 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union guess   |    145 |    145 |        0 |                      |                                                                                  |         |          |
| streamlink         |                     |        |        |          |                    8 |                                     15 failed, 7233 passed, 36 skipped, 9 errors |    18.8 |     21.7 |
| streamlink         | certain             |    287 |    286 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely              |     47 |     47 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess               |     46 |     46 |        0 |                      |                                                                                  |         |          |
| streamlink         | infer-union certain |    289 |    288 |        1 |                      |                                                                                  |         |          |
| streamlink         | infer-union likely  |    138 |    131 |        7 |                      |                                                                                  |         |          |
| streamlink         | infer-union guess   |    132 |    126 |        6 |                      |                                                                                  |         |          |
| sphinx             |                     |        |        |          |                    0 |                                   7 failed, 2394 passed, 23 skipped, 35 warnings |    22.8 |     16.1 |
| sphinx             | certain             |  2,125 |  2,094 |       31 |                      |                                                                                  |         |          |
| sphinx             | likely              |    426 |    425 |        1 |                      |                                                                                  |         |          |
| sphinx             | guess               |    218 |    214 |        4 |                      |                                                                                  |         |          |
| sphinx             | infer-union certain |  2,126 |  2,095 |       31 |                      |                                                                                  |         |          |
| sphinx             | infer-union likely  |    976 |    946 |       30 |                      |                                                                                  |         |          |
| sphinx             | infer-union guess   |    409 |    400 |        9 |                      |                                                                                  |         |          |
| tox                |                     |        |        |          |                    0 |                                     17 failed, 8525 passed, 31 skipped, 6 errors |    30.4 |     17.5 |
| tox                | certain             |    747 |    744 |        3 |                      |                                                                                  |         |          |
| tox                | likely              |     76 |     76 |        0 |                      |                                                                                  |         |          |
| tox                | guess               |     29 |     29 |        0 |                      |                                                                                  |         |          |
| tox                | infer-union certain |    749 |    746 |        3 |                      |                                                                                  |         |          |
| tox                | infer-union likely  |    265 |    265 |        0 |                      |                                                                                  |         |          |
| tox                | infer-union guess   |     85 |     84 |        1 |                      |                                                                                  |         |          |
| pint               |                     |        |        |          |                    5 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    37.6 |     63.7 |
| pint               | certain             |    217 |    214 |        3 |                      |                                                                                  |         |          |
| pint               | likely              |     12 |     12 |        0 |                      |                                                                                  |         |          |
| pint               | guess               |     24 |     22 |        2 |                      |                                                                                  |         |          |
| pint               | infer-union certain |    218 |    215 |        3 |                      |                                                                                  |         |          |
| pint               | infer-union likely  |     59 |     58 |        1 |                      |                                                                                  |         |          |
| pint               | infer-union guess   |     59 |     56 |        3 |                      |                                                                                  |         |          |
| altair             |                     |        |        |          |                    6 |            28 failed, 1866 passed, 12 skipped, 6 xfailed, 4 xpassed, 88 warnings |    45.5 |     21.9 |
| altair             | certain             |    204 |    203 |        1 |                      |                                                                                  |         |          |
| altair             | likely              |     35 |     35 |        0 |                      |                                                                                  |         |          |
| altair             | guess               |      6 |      5 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union certain |    204 |    203 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union likely  |     71 |     70 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union guess   |     34 |     33 |        1 |                      |                                                                                  |         |          |
| seaborn            |                     |        |        |          |                   42 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    58.9 |     35.3 |
| seaborn            | certain             |    501 |    499 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely              |    133 |    131 |        2 |                      |                                                                                  |         |          |
| seaborn            | guess               |     46 |     44 |        2 |                      |                                                                                  |         |          |
| seaborn            | infer-union certain |    500 |    498 |        2 |                      |                                                                                  |         |          |
| seaborn            | infer-union likely  |    188 |    184 |        4 |                      |                                                                                  |         |          |
| seaborn            | infer-union guess   |    204 |    200 |        4 |                      |                                                                                  |         |          |
| aiohttp            |                     |        |        |          |                    0 |                 3 failed, 4840 passed, 535 skipped, 2 xfailed, 4 subtests passed |   101.8 |     98.0 |
| aiohttp            | certain             |    537 |    522 |       15 |                      |                                                                                  |         |          |
| aiohttp            | likely              |    116 |    114 |        2 |                      |                                                                                  |         |          |
| aiohttp            | guess               |     86 |     82 |        4 |                      |                                                                                  |         |          |
| aiohttp            | infer-union certain |    539 |    524 |       15 |                      |                                                                                  |         |          |
| aiohttp            | infer-union likely  |    261 |    256 |        5 |                      |                                                                                  |         |          |
| aiohttp            | infer-union guess   |    217 |    209 |        8 |                      |                                                                                  |         |          |
| websockets         |                     |        |        |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    43.5 |     32.2 |
| websockets         | certain             |    259 |    258 |        1 |                      |                                                                                  |         |          |
| websockets         | likely              |     68 |     68 |        0 |                      |                                                                                  |         |          |
| websockets         | guess               |     36 |     36 |        0 |                      |                                                                                  |         |          |
| websockets         | infer-union certain |    261 |    260 |        1 |                      |                                                                                  |         |          |
| websockets         | infer-union likely  |    143 |    143 |        0 |                      |                                                                                  |         |          |
| websockets         | infer-union guess   |     55 |     55 |        0 |                      |                                                                                  |         |          |
| anyio              |                     |        |        |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   141.4 |    118.5 |
| anyio              | certain             |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | likely              |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | guess               |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union certain |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union likely  |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union guess   |      0 |      0 |        0 |                      |                                                                                  |         |          |
| zarr               |                     |        |        |          |                    0 |                                             8422 passed, 1205 skipped, 4 xfailed |   151.6 |    114.5 |
| zarr               | certain             |    779 |    766 |       13 |                      |                                                                                  |         |          |
| zarr               | likely              |     52 |     52 |        0 |                      |                                                                                  |         |          |
| zarr               | guess               |     24 |     22 |        2 |                      |                                                                                  |         |          |
| zarr               | infer-union certain |    779 |    766 |       13 |                      |                                                                                  |         |          |
| zarr               | infer-union likely  |    249 |    247 |        2 |                      |                                                                                  |         |          |
| zarr               | infer-union guess   |    140 |    134 |        6 |                      |                                                                                  |         |          |
| joblib             |                     |        |        |          |                   10 |                       10 failed, 1482 passed, 45 skipped, 4 xpassed, 85 warnings |   214.2 |    174.9 |
| joblib             | certain             |    127 |    127 |        0 |                      |                                                                                  |         |          |
| joblib             | likely              |     16 |     16 |        0 |                      |                                                                                  |         |          |
| joblib             | guess               |     29 |     29 |        0 |                      |                                                                                  |         |          |
| joblib             | infer-union certain |    125 |    125 |        0 |                      |                                                                                  |         |          |
| joblib             | infer-union likely  |     41 |     40 |        1 |                      |                                                                                  |         |          |
| joblib             | infer-union guess   |     61 |     59 |        2 |                      |                                                                                  |         |          |
| networkx           |                     |        |        |          |                  363 |                                            10083 passed, 62 skipped, 741 xfailed |    34.1 |     29.0 |
| networkx           | certain             |    933 |    932 |        1 |                      |                                                                                  |         |          |
| networkx           | likely              |    190 |    189 |        1 |                      |                                                                                  |         |          |
| networkx           | guess               |    162 |    159 |        3 |                      |                                                                                  |         |          |
| networkx           | infer-union certain |    933 |    932 |        1 |                      |                                                                                  |         |          |
| networkx           | infer-union likely  |    455 |    434 |       21 |                      |                                                                                  |         |          |
| networkx           | infer-union guess   |    500 |    468 |       32 |                      |                                                                                  |         |          |
| nibabel            |                     |        |        |          |                   76 |                      110 failed, 5165 passed, 304 skipped, 40 xfailed, 21 errors |    18.1 |     12.7 |
| nibabel            | certain             |    416 |    413 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely              |    177 |    177 |        0 |                      |                                                                                  |         |          |
| nibabel            | guess               |    100 |     99 |        1 |                      |                                                                                  |         |          |
| nibabel            | infer-union certain |    416 |    413 |        3 |                      |                                                                                  |         |          |
| nibabel            | infer-union likely  |    278 |    274 |        4 |                      |                                                                                  |         |          |
| nibabel            | infer-union guess   |    271 |    254 |       17 |                      |                                                                                  |         |          |
| narwhals           |                     |        |        |          |                    0 |                               972 failed, 11116 passed, 235 skipped, 699 xfailed |    38.2 |     41.9 |
| narwhals           | certain             |    565 |    562 |        3 |                      |                                                                                  |         |          |
| narwhals           | likely              |     41 |     41 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess               |     24 |     24 |        0 |                      |                                                                                  |         |          |
| narwhals           | infer-union certain |    565 |    562 |        3 |                      |                                                                                  |         |          |
| narwhals           | infer-union likely  |    235 |    231 |        4 |                      |                                                                                  |         |          |
| narwhals           | infer-union guess   |    149 |    141 |        8 |                      |                                                                                  |         |          |
| xarray             |                     |        |        |          |                   20 |  3 failed, 6333 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    34.5 |     16.1 |
| xarray             | certain             |    972 |    961 |       11 |                      |                                                                                  |         |          |
| xarray             | likely              |    144 |    143 |        1 |                      |                                                                                  |         |          |
| xarray             | guess               |     89 |     87 |        2 |                      |                                                                                  |         |          |
| xarray             | infer-union certain |    973 |    962 |       11 |                      |                                                                                  |         |          |
| xarray             | infer-union likely  |    361 |    354 |        7 |                      |                                                                                  |         |          |
| xarray             | infer-union guess   |    345 |    342 |        3 |                      |                                                                                  |         |          |
| litestar           |                     |        |        |          |                    0 |  6 failed, 5645 passed, 256 skipped, 13 xfailed, 30 xpassed, 3 warnings, 1 rerun |    30.4 |     31.9 |
| litestar           | certain             |    496 |    495 |        1 |                      |                                                                                  |         |          |
| litestar           | likely              |     94 |     94 |        0 |                      |                                                                                  |         |          |
| litestar           | guess               |     51 |     51 |        0 |                      |                                                                                  |         |          |
| litestar           | infer-union certain |    496 |    495 |        1 |                      |                                                                                  |         |          |
| litestar           | infer-union likely  |    238 |    237 |        1 |                      |                                                                                  |         |          |
| litestar           | infer-union guess   |    100 |    100 |        0 |                      |                                                                                  |         |          |
| celery             |                     |        |        |          |                   66 |                                     4 failed, 3520 passed, 36 skipped, 3 xfailed |    80.8 |     46.2 |
| celery             | certain             |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | likely              |     45 |     44 |        1 |                      |                                                                                  |         |          |
| celery             | guess               |     30 |     26 |        4 |                      |                                                                                  |         |          |
| celery             | infer-union certain |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | infer-union likely  |     86 |     82 |        4 |                      |                                                                                  |         |          |
| celery             | infer-union guess   |     96 |     87 |        9 |                      |                                                                                  |         |          |
| optuna             |                     |        |        |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 327 warnings, 16 errors |   156.8 |    109.5 |
| optuna             | certain             |    694 |    694 |        0 |                      |                                                                                  |         |          |
| optuna             | likely              |    122 |    122 |        0 |                      |                                                                                  |         |          |
| optuna             | guess               |     56 |     56 |        0 |                      |                                                                                  |         |          |
| optuna             | infer-union certain |    694 |    694 |        0 |                      |                                                                                  |         |          |
| optuna             | infer-union likely  |    284 |    281 |        3 |                      |                                                                                  |         |          |
| optuna             | infer-union guess   |    249 |    247 |        2 |                      |                                                                                  |         |          |
| dask               |                     |        |        |          |                  156 |         5 failed, 16196 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   136.5 |    148.9 |
| dask               | certain             |  1,075 |  1,068 |        7 |                      |                                                                                  |         |          |
| dask               | likely              |    186 |    183 |        3 |                      |                                                                                  |         |          |
| dask               | guess               |    118 |    115 |        3 |                      |                                                                                  |         |          |
| dask               | infer-union certain |  1,073 |  1,066 |        7 |                      |                                                                                  |         |          |
| dask               | infer-union likely  |    359 |    348 |       11 |                      |                                                                                  |         |          |
| dask               | infer-union guess   |    500 |    480 |       20 |                      |                                                                                  |         |          |
| mypy               |                     |        |        |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   311.0 |    303.3 |
| mypy               | certain             |  3,346 |  3,346 |        0 |                      |                                                                                  |         |          |
| mypy               | likely              |    712 |    712 |        0 |                      |                                                                                  |         |          |
| mypy               | guess               |    266 |    266 |        0 |                      |                                                                                  |         |          |
| mypy               | infer-union certain |  3,346 |  3,346 |        0 |                      |                                                                                  |         |          |
| mypy               | infer-union likely  |  1,910 |  1,909 |        1 |                      |                                                                                  |         |          |
| mypy               | infer-union guess   |    641 |    639 |        2 |                      |                                                                                  |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus             | shape                                        | no fix | traced | one type |
| ------------------ | -------------------------------------------- | -----: | -----: | -------: |
| django             | `call: chained .method()`                    |  1,346 |    946 |      596 |
| django             | `call: self.method()`                        |    978 |    652 |      413 |
| django             | `call: param.method()`                       |    654 |    475 |      376 |
| django             | `call: imported function`                    |    654 |    274 |      198 |
| django             | `call: local.method()`                       |    545 |    384 |      265 |
| django             | `empty list`                                 |    450 |      0 |        0 |
| django             | `copy: local`                                |    434 |    322 |      225 |
| django             | `attr: chained`                              |    406 |    280 |      184 |
| django             | `copy: param (unannotated)`                  |    348 |    240 |      145 |
| django             | `attr: self.x`                               |    342 |    270 |      141 |
| django             | `other constant`                             |    330 |     22 |       22 |
| django             | `None literal`                               |    319 |    104 |      104 |
| django             | `call: imported.attr()`                      |    301 |    146 |       98 |
| django             | `subscript: other`                           |    265 |    196 |      159 |
| django             | `dict (mixed/unknown elements)`              |    237 |    104 |       73 |
| django             | `empty dict`                                 |    201 |      0 |        0 |
| django             | `call: module function (unannotated)`        |    185 |    134 |       94 |
| django             | `tuple (mixed/unknown elements)`             |    176 |     95 |       72 |
| django             | `copy: imported`                             |    175 |      8 |        7 |
| django             | `call: builtin getattr()`                    |    174 |    153 |       70 |
| django             | `subscript: local[...]`                      |    173 |    110 |       90 |
| django             | `attr: local.x`                              |    170 |    129 |       92 |
| django             | `ListComp (unknown elements)`                |    165 |    119 |       82 |
| django             | `list (mixed/unknown elements)`              |    159 |     56 |       44 |
| django             | `conditional`                                |    157 |    128 |       65 |
| django             | `subscript: param[...]`                      |    136 |    112 |       94 |
| django             | `binop (unknown operands)`                   |    130 |     85 |       78 |
| django             | `attr: param.x`                              |    124 |    102 |       74 |
| django             | `boolop (or)`                                |    112 |     95 |       72 |
| django             | `call: builtin set()`                        |    109 |     16 |       12 |
| django             | `attr: imported.x`                           |    105 |     21 |       17 |
| django             | `call: imported class`                       |     95 |     14 |       14 |
| django             | `call: module.func()`                        |     94 |     69 |       59 |
| django             | `call: builtin enumerate()`                  |     85 |     66 |       39 |
| django             | `call: builtin sorted()`                     |     77 |     64 |       58 |
| django             | `call: builtin list()`                       |     62 |     48 |       35 |
| django             | `subscript: imported[...]`                   |     59 |     40 |       36 |
| django             | `DictComp (unknown elements)`                |     57 |     36 |       21 |
| django             | `call: builtin zip()`                        |     56 |     36 |       14 |
| django             | `call: other name`                           |     52 |     36 |       21 |
| django             | `call: local name`                           |     51 |     36 |       17 |
| django             | `call: builtin property()`                   |     49 |      0 |        0 |
| django             | `boolop (and)`                               |     42 |     29 |       21 |
| django             | `call: global.method()`                      |     42 |     29 |       17 |
| django             | `SetComp (unknown elements)`                 |     40 |     21 |       17 |
| django             | `copy: other`                                |     40 |      7 |        6 |
| django             | `empty tuple`                                |     39 |      0 |        0 |
| django             | `compare`                                    |     35 |     20 |       20 |
| django             | `call: builtin next()`                       |     32 |     31 |       27 |
| django             | `call: module class`                         |     31 |      6 |        6 |
| django             | `GeneratorExp (unknown elements)`            |     29 |     26 |       25 |
| django             | `binop (one side literal)`                   |     29 |      6 |        6 |
| django             | `copy: modclass`                             |     27 |      0 |        0 |
| django             | `copy: moddef`                               |     26 |      0 |        0 |
| django             | `copy: global`                               |     25 |      4 |        4 |
| django             | `call: other callee`                         |     24 |     16 |       12 |
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
| django             | `binop: literal % formatting`                |     13 |      8 |        8 |
| django             | `attr: cls.x`                                |     12 |     12 |       10 |
| django             | `copy: builtin`                              |     12 |      1 |        1 |
| django             | `call: builtin staticmethod()`               |     11 |      0 |        0 |
| django             | `call: builtin max()`                        |     11 |      7 |        7 |
| django             | `copy: self`                                 |      9 |      7 |        4 |
| django             | `call: capitalised`                          |      9 |      6 |        3 |
| django             | `await: call: other name`                    |      9 |      9 |        8 |
| django             | `call: cls.method()`                         |      9 |      7 |        5 |
| django             | `call: builtin dict()`                       |      8 |      7 |        3 |
| django             | `set (mixed/unknown elements)`               |      7 |      4 |        4 |
| django             | `call: builtin map()`                        |      7 |      3 |        2 |
| django             | `call: builtin min()`                        |      6 |      2 |        2 |
| django             | `call: builtin frozenset()`                  |      6 |      1 |        1 |
| django             | `attr: global.x`                             |      6 |      1 |        1 |
| django             | `await: call: module.func()`                 |      6 |      0 |        0 |
| django             | `call: builtin.method()`                     |      5 |      4 |        4 |
| django             | `call: param name`                           |      5 |      5 |        1 |
| django             | `await: call: param name`                    |      4 |      4 |        3 |
| django             | `call: builtin sum()`                        |      4 |      4 |        4 |
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
| django             | `call: bytes-literal.method()`               |      2 |      2 |        2 |
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
| sqlalchemy         | `call: chained .method()`                    |    940 |    453 |      304 |
| sqlalchemy         | `other constant`                             |    602 |      8 |        8 |
| sqlalchemy         | `attr: chained`                              |    571 |    281 |      213 |
| sqlalchemy         | `call: self.method()`                        |    567 |    296 |      161 |
| sqlalchemy         | `call: local.method()`                       |    521 |    283 |      180 |
| sqlalchemy         | `call: param.method()`                       |    446 |    272 |      159 |
| sqlalchemy         | `attr: self.x`                               |    358 |    276 |      154 |
| sqlalchemy         | `subscript: other`                           |    354 |    214 |      137 |
| sqlalchemy         | `copy: local`                                |    351 |    219 |      134 |
| sqlalchemy         | `call: imported function`                    |    334 |    155 |       84 |
| sqlalchemy         | `call: imported.attr()`                      |    317 |    166 |      109 |
| sqlalchemy         | `attr: param.x`                              |    312 |    249 |      151 |
| sqlalchemy         | `attr: local.x`                              |    253 |    206 |      129 |
| sqlalchemy         | `tuple (mixed/unknown elements)`             |    202 |    135 |       91 |
| sqlalchemy         | `copy: param (unannotated)`                  |    183 |    135 |       89 |
| sqlalchemy         | `subscript: local[...]`                      |    173 |     93 |       54 |
| sqlalchemy         | `None literal`                               |    172 |     73 |       73 |
| sqlalchemy         | `ListComp (unknown elements)`                |    158 |    119 |       70 |
| sqlalchemy         | `copy: modclass`                             |    147 |      1 |        1 |
| sqlalchemy         | `attr: imported.x`                           |    145 |     17 |       17 |
| sqlalchemy         | `copy: imported`                             |    118 |      1 |        1 |
| sqlalchemy         | `call: builtin list()`                       |    117 |     74 |       44 |
| sqlalchemy         | `empty list`                                 |    114 |      0 |        0 |
| sqlalchemy         | `call: module.func()`                        |    107 |     52 |       43 |
| sqlalchemy         | `copy: param (annotated)`                    |    106 |     87 |       50 |
| sqlalchemy         | `dict (mixed/unknown elements)`              |    103 |     16 |       14 |
| sqlalchemy         | `call: builtin getattr()`                    |    100 |     82 |       37 |
| sqlalchemy         | `call: param name`                           |     90 |     36 |       14 |
| sqlalchemy         | `empty dict`                                 |     82 |      0 |        0 |
| sqlalchemy         | `call: builtin set()`                        |     82 |     34 |       23 |
| sqlalchemy         | `binop (unknown operands)`                   |     81 |     43 |       32 |
| sqlalchemy         | `call: other name`                           |     76 |     57 |       33 |
| sqlalchemy         | `subscript: param[...]`                      |     74 |     59 |       36 |
| sqlalchemy         | `boolop (or)`                                |     73 |     59 |       47 |
| sqlalchemy         | `conditional`                                |     71 |     41 |       22 |
| sqlalchemy         | `call: local name`                           |     63 |     51 |       24 |
| sqlalchemy         | `copy: other`                                |     63 |     20 |       15 |
| sqlalchemy         | `list (mixed/unknown elements)`              |     62 |     18 |       10 |
| sqlalchemy         | `DictComp (unknown elements)`                |     61 |     35 |       15 |
| sqlalchemy         | `call: module function (unannotated)`        |     59 |     49 |       37 |
| sqlalchemy         | `call: builtin zip()`                        |     57 |     39 |       19 |
| sqlalchemy         | `copy: global`                               |     50 |      6 |        6 |
| sqlalchemy         | `call: builtin dict()`                       |     49 |     24 |       13 |
| sqlalchemy         | `call: builtin enumerate()`                  |     39 |     29 |        6 |
| sqlalchemy         | `call: builtin tuple()`                      |     38 |     15 |        5 |
| sqlalchemy         | `call: other.method()`                       |     36 |     21 |       11 |
| sqlalchemy         | `SetComp (unknown elements)`                 |     35 |     22 |       16 |
| sqlalchemy         | `call: imported class`                       |     33 |      7 |        7 |
| sqlalchemy         | `call: module function (annotated)`          |     32 |     29 |       15 |
| sqlalchemy         | `call: cls.method()`                         |     30 |     24 |       16 |
| sqlalchemy         | `boolop (and)`                               |     25 |     25 |       21 |
| sqlalchemy         | `call: builtin.method()`                     |     24 |     23 |       10 |
| sqlalchemy         | `call: module class`                         |     23 |     15 |       15 |
| sqlalchemy         | `attr: modclass.x`                           |     21 |      0 |        0 |
| sqlalchemy         | `attr: cls.x`                                |     21 |     21 |       11 |
| sqlalchemy         | `empty tuple`                                |     16 |      0 |        0 |
| sqlalchemy         | `compare`                                    |     15 |      9 |        9 |
| sqlalchemy         | `call: builtin type()`                       |     15 |     10 |        3 |
| sqlalchemy         | `call: other callee`                         |     15 |     11 |        5 |
| sqlalchemy         | `await: call: imported function`             |     15 |     13 |        8 |
| sqlalchemy         | `attr: global.x`                             |     14 |      0 |        0 |
| sqlalchemy         | `GeneratorExp (unknown elements)`            |     13 |      6 |        6 |
| sqlalchemy         | `call: global.method()`                      |     13 |     11 |       10 |
| sqlalchemy         | `copy: moddef`                               |     13 |      0 |        0 |
| sqlalchemy         | `call: builtin sorted()`                     |     12 |      5 |        4 |
| sqlalchemy         | `subscript: global[...]`                     |     12 |     11 |        9 |
| sqlalchemy         | `call: global name`                          |     12 |     12 |        4 |
| sqlalchemy         | `attr: module.x`                             |     11 |      9 |        9 |
| sqlalchemy         | `copy: builtin`                              |     11 |      0 |        0 |
| sqlalchemy         | `attr: other.x`                              |     10 |      7 |        7 |
| sqlalchemy         | `call: builtin object()`                     |     10 |      6 |        6 |
| sqlalchemy         | `call: modclass.method()`                    |      8 |      8 |        5 |
| sqlalchemy         | `subscript: other[...]`                      |      8 |      8 |        4 |
| sqlalchemy         | `call: builtin reversed()`                   |      8 |      6 |        6 |
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
| pydantic           | `call: param.method()`                       |     98 |     59 |       31 |
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
| pandas             | `call: local.method()`                       |  5,926 |  4,899 |    4,555 |
| pandas             | `call: chained .method()`                    |  4,665 |  3,598 |    3,277 |
| pandas             | `call: module.func()`                        |  3,372 |  2,229 |    2,120 |
| pandas             | `copy: param (unannotated)`                  |  1,956 |  1,736 |      791 |
| pandas             | `subscript: other`                           |  1,510 |  1,222 |    1,093 |
| pandas             | `call: imported function`                    |  1,446 |  1,039 |      883 |
| pandas             | `call: param.method()`                       |  1,407 |    979 |      775 |
| pandas             | `binop (unknown operands)`                   |  1,112 |    955 |      807 |
| pandas             | `subscript: local[...]`                      |    948 |    755 |      707 |
| pandas             | `attr: chained`                              |    792 |    529 |      434 |
| pandas             | `list (mixed/unknown elements)`              |    780 |    534 |      401 |
| pandas             | `call: param name`                           |    769 |    726 |      269 |
| pandas             | `call: imported class`                       |    736 |    631 |      626 |
| pandas             | `call: self.method()`                        |    588 |    397 |      239 |
| pandas             | `call: other callee`                         |    503 |    418 |      340 |
| pandas             | `conditional`                                |    470 |    377 |      200 |
| pandas             | `attr: local.x`                              |    439 |    330 |      269 |
| pandas             | `copy: local`                                |    412 |    274 |      194 |
| pandas             | `subscript: param[...]`                      |    384 |    276 |      163 |
| pandas             | `tuple (mixed/unknown elements)`             |    372 |    225 |      177 |
| pandas             | `call: imported.attr()`                      |    367 |    266 |      195 |
| pandas             | `ListComp (unknown elements)`                |    360 |    187 |      136 |
| pandas             | `compare`                                    |    347 |    271 |      250 |
| pandas             | `dict (mixed/unknown elements)`              |    332 |    208 |      182 |
| pandas             | `call: builtin getattr()`                    |    307 |    224 |      154 |
| pandas             | `call: builtin zip()`                        |    306 |    209 |      152 |
| pandas             | `call: local name`                           |    296 |    255 |      149 |
| pandas             | `attr: param.x`                              |    281 |    190 |      104 |
| pandas             | `empty list`                                 |    276 |      0 |        0 |
| pandas             | `call: module function (unannotated)`        |    275 |    133 |       82 |
| pandas             | `attr: self.x`                               |    274 |    191 |      106 |
| pandas             | `binop (one side literal)`                   |    254 |    201 |      180 |
| pandas             | `call: builtin enumerate()`                  |    233 |    155 |      108 |
| pandas             | `other constant`                             |    178 |     48 |       48 |
| pandas             | `call: builtin list()`                       |    170 |    124 |       84 |
| pandas             | `None literal`                               |    157 |    112 |      112 |
| pandas             | `attr: module.x`                             |    121 |     84 |       82 |
| pandas             | `Lambda`                                     |    120 |     76 |       76 |
| pandas             | `call: global.method()`                      |    118 |      4 |        2 |
| pandas             | `call: other name`                           |    113 |     75 |       52 |
| pandas             | `attr: imported.x`                           |     94 |     23 |       23 |
| pandas             | `empty dict`                                 |     90 |      0 |        0 |
| pandas             | `copy: imported`                             |     89 |     50 |       50 |
| pandas             | `call: module function (annotated)`          |     85 |     47 |       23 |
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
| pandas             | `call: cls.method()`                         |     13 |     12 |        9 |
| pandas             | `set (mixed/unknown elements)`               |     12 |      5 |        5 |
| pandas             | `call: builtin min()`                        |     12 |      7 |        6 |
| pandas             | `call: modclass.method()`                    |     11 |      8 |        8 |
| pandas             | `call: builtin len()`                        |     11 |      4 |        4 |
| pandas             | `copy: modclass`                             |     10 |      0 |        0 |
| pandas             | `call: builtin.method()`                     |      9 |      8 |        7 |
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
| structlog          | `call: module.func()`                        |      4 |      3 |        2 |
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
| attrs              | `ListComp (unknown elements)`                |      8 |      4 |        3 |
| attrs              | `attr: local.x`                              |      8 |      7 |        5 |
| attrs              | `conditional`                                |      7 |      3 |        3 |
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
| black              | `attr: param.x`                              |     59 |     56 |       30 |
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
| black              | `conditional`                                |     10 |      9 |        5 |
| black              | `empty list`                                 |     10 |      0 |        0 |
| black              | `call: builtin enumerate()`                  |      8 |      7 |        3 |
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
| fastapi            | `call: param.method()`                       |     27 |     23 |       10 |
| fastapi            | `call: builtin getattr()`                    |     25 |     22 |       18 |
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
| fastapi            | `ListComp (unknown elements)`                |      5 |      4 |        1 |
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
| cattrs             | `call: imported function`                    |     54 |     44 |       15 |
| cattrs             | `attr: local.x`                              |     20 |     19 |       13 |
| cattrs             | `empty dict`                                 |     20 |      0 |        0 |
| cattrs             | `copy: local`                                |     19 |     19 |       10 |
| cattrs             | `call: builtin getattr()`                    |     18 |     16 |        5 |
| cattrs             | `empty list`                                 |     18 |      0 |        0 |
| cattrs             | `attr: param.x`                              |     15 |     15 |        7 |
| cattrs             | `call: chained .method()`                    |     13 |     11 |        7 |
| cattrs             | `copy: imported`                             |     11 |      3 |        3 |
| cattrs             | `conditional`                                |     10 |     10 |        5 |
| cattrs             | `attr: global.x`                             |      9 |      1 |        1 |
| cattrs             | `call: builtin set()`                        |      8 |      3 |        0 |
| cattrs             | `subscript: local[...]`                      |      8 |      6 |        5 |
| cattrs             | `call: local.method()`                       |      8 |      8 |        4 |
| cattrs             | `boolop (or)`                                |      7 |      6 |        2 |
| cattrs             | `SetComp (unknown elements)`                 |      7 |      7 |        0 |
| cattrs             | `copy: builtin`                              |      6 |      4 |        4 |
| cattrs             | `call: param.method()`                       |      6 |      5 |        4 |
| cattrs             | `subscript: other`                           |      6 |      5 |        0 |
| cattrs             | `call: builtin zip()`                        |      6 |      6 |        3 |
| cattrs             | `subscript: param[...]`                      |      6 |      6 |        4 |
| cattrs             | `copy: param (annotated)`                    |      6 |      6 |        3 |
| cattrs             | `None literal`                               |      6 |      6 |        6 |
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
| pytest             | `call: chained .method()`                    |    157 |    128 |       99 |
| pytest             | `call: self.method()`                        |     88 |     75 |       61 |
| pytest             | `attr: chained`                              |     68 |     55 |       49 |
| pytest             | `copy: local`                                |     61 |     47 |       37 |
| pytest             | `call: local.method()`                       |     55 |     43 |       37 |
| pytest             | `attr: param.x`                              |     55 |     48 |       39 |
| pytest             | `call: builtin getattr()`                    |     51 |     46 |       30 |
| pytest             | `call: param.method()`                       |     51 |     46 |       42 |
| pytest             | `empty list`                                 |     49 |      0 |        0 |
| pytest             | `call: module.func()`                        |     46 |     32 |       28 |
| pytest             | `attr: local.x`                              |     45 |     35 |       24 |
| pytest             | `subscript: other`                           |     42 |     28 |       21 |
| pytest             | `attr: self.x`                               |     28 |     26 |       17 |
| pytest             | `None literal`                               |     27 |     22 |       22 |
| pytest             | `conditional`                                |     27 |     23 |       17 |
| pytest             | `tuple (mixed/unknown elements)`             |     23 |     20 |       18 |
| pytest             | `copy: param (annotated)`                    |     23 |     17 |       10 |
| pytest             | `call: module function (annotated)`          |     22 |     21 |        7 |
| pytest             | `binop (unknown operands)`                   |     20 |     17 |       14 |
| pytest             | `call: imported class`                       |     19 |      5 |        5 |
| pytest             | `other constant`                             |     17 |      4 |        4 |
| pytest             | `boolop (or)`                                |     17 |     11 |       10 |
| pytest             | `call: other callee`                         |     17 |      4 |        4 |
| pytest             | `ListComp (unknown elements)`                |     15 |     12 |       10 |
| pytest             | `call: imported.attr()`                      |     15 |      8 |        7 |
| pytest             | `call: other name`                           |     14 |     12 |       10 |
| pytest             | `call: builtin list()`                       |     12 |     10 |        9 |
| pytest             | `call: module class`                         |     12 |     10 |       10 |
| pytest             | `call: imported function`                    |     11 |      9 |        7 |
| pytest             | `call: builtin enumerate()`                  |     10 |      6 |        2 |
| pytest             | `Yield`                                      |     10 |      7 |        7 |
| pytest             | `copy: other`                                |     10 |      1 |        1 |
| pytest             | `subscript: local[...]`                      |      9 |      7 |        6 |
| pytest             | `DictComp (unknown elements)`                |      9 |      6 |        3 |
| pytest             | `list (mixed/unknown elements)`              |      9 |      7 |        6 |
| pytest             | `call: builtin reversed()`                   |      9 |      8 |        6 |
| pytest             | `dict (mixed/unknown elements)`              |      8 |      4 |        4 |
| pytest             | `call: module function (unannotated)`        |      8 |      3 |        3 |
| pytest             | `call: builtin sorted()`                     |      8 |      7 |        7 |
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
| pytest             | `call: builtin max()`                        |      3 |      2 |        2 |
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
| pytest             | `call: builtin eval()`                       |      1 |      1 |        1 |
| pytest             | `call: builtin min()`                        |      1 |      0 |        0 |
| botocore           | `call: self.method()`                        |    362 |    317 |      205 |
| botocore           | `call: chained .method()`                    |    345 |    297 |      189 |
| botocore           | `call: param.method()`                       |    245 |    214 |      141 |
| botocore           | `call: local.method()`                       |    233 |    197 |      124 |
| botocore           | `copy: param (unannotated)`                  |    100 |     92 |       67 |
| botocore           | `subscript: other`                           |     97 |     77 |       62 |
| botocore           | `call: imported function`                    |     84 |     66 |       56 |
| botocore           | `attr: param.x`                              |     79 |     74 |       36 |
| botocore           | `empty dict`                                 |     76 |      0 |        0 |
| botocore           | `subscript: local[...]`                      |     75 |     69 |       47 |
| botocore           | `copy: local`                                |     71 |     66 |       51 |
| botocore           | `dict (mixed/unknown elements)`              |     70 |     36 |       27 |
| botocore           | `subscript: param[...]`                      |     65 |     53 |       32 |
| botocore           | `attr: self.x`                               |     60 |     56 |       31 |
| botocore           | `attr: chained`                              |     55 |     38 |       33 |
| botocore           | `empty list`                                 |     48 |      0 |        0 |
| botocore           | `call: module.func()`                        |     37 |     26 |       15 |
| botocore           | `call: module function (unannotated)`        |     33 |     26 |       20 |
| botocore           | `binop (unknown operands)`                   |     30 |     26 |       22 |
| botocore           | `tuple (mixed/unknown elements)`             |     25 |     16 |       16 |
| botocore           | `None literal`                               |     25 |     20 |       20 |
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
| botocore           | `compare`                                    |     12 |      8 |        8 |
| botocore           | `boolop (and)`                               |     11 |      8 |        8 |
| botocore           | `call: builtin sorted()`                     |     10 |     10 |        9 |
| botocore           | `copy: modclass`                             |     10 |      0 |        0 |
| botocore           | `call: imported class`                       |     10 |      1 |        1 |
| botocore           | `copy: global`                               |      9 |      1 |        1 |
| botocore           | `call: modclass.method()`                    |      9 |      9 |        9 |
| botocore           | `copy: other`                                |      9 |      0 |        0 |
| botocore           | `call: builtin type()`                       |      8 |      7 |        2 |
| botocore           | `attr: module.x`                             |      8 |      1 |        1 |
| botocore           | `copy: imported`                             |      7 |      1 |        1 |
| botocore           | `conditional`                                |      6 |      4 |        2 |
| botocore           | `call: builtin iter()`                       |      6 |      5 |        5 |
| botocore           | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| botocore           | `call: builtin list()`                       |      5 |      3 |        3 |
| botocore           | `call: builtin zip()`                        |      5 |      5 |        2 |
| botocore           | `copy: builtin`                              |      5 |      0 |        0 |
| botocore           | `binop (one side literal)`                   |      4 |      4 |        4 |
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
| uvicorn            | `call: chained .method()`                    |     32 |     31 |       26 |
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
| mcp                | `call: chained .method()`                    |     73 |     66 |       41 |
| mcp                | `call: other callee`                         |     50 |     44 |       44 |
| mcp                | `call: imported function`                    |     46 |     38 |       20 |
| mcp                | `call: param.method()`                       |     42 |     41 |       15 |
| mcp                | `call: module.func()`                        |     41 |     35 |       19 |
| mcp                | `conditional`                                |     41 |     39 |       17 |
| mcp                | `copy: local`                                |     36 |     30 |       21 |
| mcp                | `call: local.method()`                       |     35 |     31 |       10 |
| mcp                | `call: module function (annotated)`          |     20 |     19 |        8 |
| mcp                | `attr: param.x`                              |     19 |     19 |        9 |
| mcp                | `call: imported class`                       |     18 |      6 |        6 |
| mcp                | `call: imported.attr()`                      |     17 |     17 |       14 |
| mcp                | `await: call: param.method()`                |     16 |     12 |        9 |
| mcp                | `await: call: self.method()`                 |     16 |     16 |        7 |
| mcp                | `await: call: local.method()`                |     15 |     13 |       10 |
| mcp                | `attr: local.x`                              |     14 |     14 |       11 |
| mcp                | `boolop (or)`                                |     13 |     10 |        9 |
| mcp                | `attr: self.x`                               |     12 |     12 |        7 |
| mcp                | `attr: chained`                              |     12 |     12 |        6 |
| mcp                | `await: call: chained .method()`             |     12 |     12 |        5 |
| mcp                | `None literal`                               |     11 |      8 |        8 |
| mcp                | `tuple (mixed/unknown elements)`             |     11 |      8 |        6 |
| mcp                | `subscript: other`                           |     10 |      9 |        8 |
| mcp                | `call: builtin getattr()`                    |     10 |      7 |        3 |
| mcp                | `copy: param (annotated)`                    |     10 |      9 |        7 |
| mcp                | `ListComp (unknown elements)`                |     10 |      9 |        8 |
| mcp                | `Yield`                                      |     10 |      9 |        9 |
| mcp                | `dict (mixed/unknown elements)`              |     10 |      9 |        9 |
| mcp                | `call: self.method()`                        |      9 |      7 |        6 |
| mcp                | `copy: other`                                |      9 |      7 |        7 |
| mcp                | `call: global.method()`                      |      9 |      7 |        3 |
| mcp                | `await: call: param name`                    |      5 |      5 |        2 |
| mcp                | `call: other.method()`                       |      5 |      4 |        3 |
| mcp                | `call: module class`                         |      5 |      5 |        5 |
| mcp                | `copy: imported`                             |      4 |      1 |        1 |
| mcp                | `boolop (and)`                               |      4 |      4 |        3 |
| mcp                | `subscript: local[...]`                      |      4 |      3 |        3 |
| mcp                | `SetComp (unknown elements)`                 |      4 |      4 |        4 |
| mcp                | `-`                                          |      4 |      0 |        0 |
| mcp                | `await: call: module function (annotated)`   |      4 |      4 |        0 |
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
| pdm                | `call: chained .method()`                    |    144 |    119 |       96 |
| pdm                | `call: local.method()`                       |    107 |     86 |       76 |
| pdm                | `attr: chained`                              |     66 |     53 |       39 |
| pdm                | `call: module.func()`                        |     60 |     40 |       37 |
| pdm                | `call: imported function`                    |     56 |     50 |       48 |
| pdm                | `call: param.method()`                       |     54 |     48 |       37 |
| pdm                | `conditional`                                |     50 |     44 |       26 |
| pdm                | `tuple (mixed/unknown elements)`             |     40 |     12 |        8 |
| pdm                | `call: imported.attr()`                      |     35 |     32 |       27 |
| pdm                | `copy: local`                                |     33 |     28 |       23 |
| pdm                | `attr: local.x`                              |     30 |     25 |       10 |
| pdm                | `boolop (or)`                                |     30 |     27 |       22 |
| pdm                | `subscript: other`                           |     28 |     22 |       20 |
| pdm                | `attr: param.x`                              |     26 |     20 |       14 |
| pdm                | `dict (mixed/unknown elements)`              |     19 |     11 |       10 |
| pdm                | `attr: self.x`                               |     19 |     16 |        7 |
| pdm                | `ListComp (unknown elements)`                |     18 |     11 |       10 |
| pdm                | `other constant`                             |     17 |      3 |        3 |
| pdm                | `binop (unknown operands)`                   |     16 |      9 |        8 |
| pdm                | `copy: param (annotated)`                    |     16 |     13 |        4 |
| pdm                | `call: builtin list()`                       |     16 |     10 |        7 |
| pdm                | `call: builtin sorted()`                     |     15 |     10 |        9 |
| pdm                | `list (mixed/unknown elements)`              |     14 |     11 |       11 |
| pdm                | `call: module function (annotated)`          |     14 |     11 |        9 |
| pdm                | `call: builtin next()`                       |     13 |     11 |        8 |
| pdm                | `empty dict`                                 |     13 |      0 |        0 |
| pdm                | `empty list`                                 |     13 |      0 |        0 |
| pdm                | `call: cls.method()`                         |     12 |     12 |        0 |
| pdm                | `call: self.method()`                        |     11 |     11 |        9 |
| pdm                | `call: other name`                           |      9 |      6 |        5 |
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
| pdm                | `call: builtin min()`                        |      1 |      1 |        0 |
| strawberry-graphql | `call: chained .method()`                    |     67 |     44 |       23 |
| strawberry-graphql | `call: imported function`                    |     64 |     48 |       13 |
| strawberry-graphql | `attr: chained`                              |     56 |     44 |       32 |
| strawberry-graphql | `call: builtin getattr()`                    |     43 |     31 |       14 |
| strawberry-graphql | `attr: param.x`                              |     42 |     34 |       21 |
| strawberry-graphql | `conditional`                                |     41 |     32 |        9 |
| strawberry-graphql | `call: self.method()`                        |     39 |     20 |       15 |
| strawberry-graphql | `call: local.method()`                       |     39 |     23 |       11 |
| strawberry-graphql | `attr: local.x`                              |     39 |     32 |       18 |
| strawberry-graphql | `subscript: other`                           |     35 |     22 |       18 |
| strawberry-graphql | `copy: local`                                |     28 |     19 |       14 |
| strawberry-graphql | `call: module function (annotated)`          |     24 |     18 |        3 |
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
| pygments           | `binop (one side literal)`                   |    102 |     19 |       19 |
| pygments           | `copy: param (unannotated)`                  |     97 |     89 |       89 |
| pygments           | `call: imported function`                    |     91 |     24 |       19 |
| pygments           | `call: local.method()`                       |     90 |     69 |       66 |
| pygments           | `call: param.method()`                       |     78 |     74 |       70 |
| pygments           | `attr: module.x`                             |     64 |      0 |        0 |
| pygments           | `call: chained .method()`                    |     63 |     49 |       40 |
| pygments           | `copy: local`                                |     60 |     46 |       42 |
| pygments           | `call: self.method()`                        |     52 |     43 |       38 |
| pygments           | `tuple (mixed/unknown elements)`             |     51 |     11 |       10 |
| pygments           | `attr: self.x`                               |     42 |     35 |       24 |
| pygments           | `empty dict`                                 |     38 |      0 |        0 |
| pygments           | `call: module.func()`                        |     35 |      8 |        8 |
| pygments           | `subscript: local[...]`                      |     29 |     23 |       23 |
| pygments           | `copy: global`                               |     27 |      1 |        1 |
| pygments           | `call: builtin set()`                        |     26 |      0 |        0 |
| pygments           | `None literal`                               |     26 |     17 |       17 |
| pygments           | `other constant`                             |     26 |      0 |        0 |
| pygments           | `list (mixed/unknown elements)`              |     24 |      6 |        6 |
| pygments           | `call: other name`                           |     23 |      3 |        1 |
| pygments           | `call: module function (unannotated)`        |     22 |     14 |       10 |
| pygments           | `subscript: other`                           |     19 |     13 |       13 |
| pygments           | `subscript: global[...]`                     |     17 |      5 |        3 |
| pygments           | `attr: imported.x`                           |     16 |      5 |        5 |
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
| pygments           | `boolop (and)`                               |      2 |      2 |        0 |
| pygments           | `call: imported class`                       |      2 |      0 |        0 |
| pygments           | `call: builtin dict()`                       |      2 |      0 |        0 |
| pygments           | `call: builtin next()`                       |      2 |      2 |        2 |
| pygments           | `call: builtin max()`                        |      2 |      1 |        1 |
| pygments           | `call: builtin zip()`                        |      2 |      0 |        0 |
| pygments           | `call: builtin open()`                       |      1 |      1 |        1 |
| pygments           | `subscript: imported[...]`                   |      1 |      1 |        1 |
| pygments           | `call: builtin staticmethod()`               |      1 |      0 |        0 |
| pygments           | `call: module class`                         |      1 |      1 |        1 |
| pygments           | `call: builtin sum()`                        |      1 |      0 |        0 |
| pygments           | `call: builtin min()`                        |      1 |      1 |        1 |
| streamlink         | `call: chained .method()`                    |    440 |     58 |       49 |
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
| sphinx             | `call: chained .method()`                    |    428 |    320 |      253 |
| sphinx             | `other constant`                             |    356 |      4 |        4 |
| sphinx             | `call: imported function`                    |    242 |    112 |       92 |
| sphinx             | `call: local.method()`                       |    228 |    162 |      134 |
| sphinx             | `attr: chained`                              |    178 |    136 |      121 |
| sphinx             | `copy: local`                                |    160 |    124 |      107 |
| sphinx             | `call: imported.attr()`                      |    113 |     77 |       66 |
| sphinx             | `call: param.method()`                       |    112 |     93 |       60 |
| sphinx             | `subscript: other`                           |    109 |     86 |       74 |
| sphinx             | `empty list`                                 |    104 |      0 |        0 |
| sphinx             | `binop (unknown operands)`                   |     98 |     64 |       63 |
| sphinx             | `list (mixed/unknown elements)`              |     89 |     50 |       50 |
| sphinx             | `attr: self.x`                               |     83 |     65 |       63 |
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
| sphinx             | `None literal`                               |     42 |     32 |       32 |
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
| tox                | `call: chained .method()`                    |    117 |    101 |       86 |
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
| tox                | `dict (mixed/unknown elements)`              |      7 |      5 |        5 |
| tox                | `empty list`                                 |      6 |      0 |        0 |
| tox                | `DictComp (unknown elements)`                |      6 |      3 |        3 |
| tox                | `attr: imported.x`                           |      6 |      4 |        4 |
| tox                | `binop (unknown operands)`                   |      6 |      6 |        6 |
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
| tox                | `call: imported.attr()`                      |      3 |      3 |        3 |
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
| tox                | `call: builtin vars()`                       |      1 |      1 |        1 |
| tox                | `call: cls.method()`                         |      1 |      1 |        1 |
| tox                | `call: other.method()`                       |      1 |      1 |        1 |
| pint               | `call: self.method()`                        |    274 |     40 |       34 |
| pint               | `call: local.method()`                       |    164 |     26 |       22 |
| pint               | `call: chained .method()`                    |    150 |     48 |       39 |
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
| pint               | `compare`                                    |      3 |      1 |        0 |
| pint               | `attr: builtin.x`                            |      3 |      0 |        0 |
| pint               | `empty tuple`                                |      3 |      0 |        0 |
| pint               | `call: builtin.method()`                     |      3 |      1 |        1 |
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
| altair             | `call: chained .method()`                    |     57 |     26 |       15 |
| altair             | `call: param.method()`                       |     46 |     42 |       32 |
| altair             | `call: local.method()`                       |     46 |     38 |       17 |
| altair             | `call: module function (annotated)`          |     23 |     19 |       13 |
| altair             | `call: module.func()`                        |     22 |     13 |       12 |
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
| seaborn            | `call: self.method()`                        |    149 |    135 |       95 |
| seaborn            | `call: module.func()`                        |    140 |    123 |      117 |
| seaborn            | `call: local.method()`                       |    125 |    109 |       92 |
| seaborn            | `call: chained .method()`                    |    124 |    111 |       94 |
| seaborn            | `call: param.method()`                       |    124 |    116 |       65 |
| seaborn            | `call: imported function`                    |     89 |     73 |       58 |
| seaborn            | `tuple (mixed/unknown elements)`             |     81 |     58 |       46 |
| seaborn            | `binop (unknown operands)`                   |     79 |     69 |       55 |
| seaborn            | `subscript: other`                           |     70 |     60 |       53 |
| seaborn            | `copy: param (unannotated)`                  |     68 |     49 |       27 |
| seaborn            | `copy: local`                                |     59 |     49 |       30 |
| seaborn            | `empty list`                                 |     55 |      0 |        0 |
| seaborn            | `attr: self.x`                               |     49 |     47 |       20 |
| seaborn            | `conditional`                                |     48 |     42 |       25 |
| seaborn            | `ListComp (unknown elements)`                |     45 |     43 |       39 |
| seaborn            | `subscript: local[...]`                      |     42 |     40 |       29 |
| seaborn            | `attr: chained`                              |     41 |     33 |       29 |
| seaborn            | `call: local name`                           |     39 |     35 |       32 |
| seaborn            | `subscript: imported[...]`                   |     33 |      1 |        0 |
| seaborn            | `dict (mixed/unknown elements)`              |     32 |     30 |       12 |
| seaborn            | `empty dict`                                 |     30 |      0 |        0 |
| seaborn            | `binop (one side literal)`                   |     30 |     21 |       19 |
| seaborn            | `call: builtin getattr()`                    |     29 |     24 |       10 |
| seaborn            | `call: builtin enumerate()`                  |     29 |     25 |       21 |
| seaborn            | `call: builtin zip()`                        |     29 |     28 |       22 |
| seaborn            | `subscript: param[...]`                      |     26 |     25 |       21 |
| seaborn            | `None literal`                               |     25 |     12 |       12 |
| seaborn            | `call: param name`                           |     25 |     25 |       18 |
| seaborn            | `list (mixed/unknown elements)`              |     25 |     21 |       17 |
| seaborn            | `DictComp (unknown elements)`                |     25 |     21 |       17 |
| seaborn            | `call: builtin dict()`                       |     24 |     22 |       10 |
| seaborn            | `other constant`                             |     20 |      9 |        9 |
| seaborn            | `call: imported.attr()`                      |     19 |     14 |       13 |
| seaborn            | `call: module function (unannotated)`        |     16 |     15 |        5 |
| seaborn            | `compare`                                    |     14 |     12 |       10 |
| seaborn            | `attr: local.x`                              |     13 |     13 |       13 |
| seaborn            | `call: other name`                           |     12 |      7 |        6 |
| seaborn            | `attr: param.x`                              |     10 |      8 |        7 |
| seaborn            | `boolop (or)`                                |      9 |      9 |        7 |
| seaborn            | `call: builtin min()`                        |      8 |      8 |        5 |
| seaborn            | `boolop (and)`                               |      7 |      6 |        5 |
| seaborn            | `call: builtin tuple()`                      |      7 |      7 |        1 |
| seaborn            | `subscript: self[...]`                       |      7 |      3 |        3 |
| seaborn            | `call: builtin list()`                       |      6 |      6 |        5 |
| seaborn            | `attr: module.x`                             |      6 |      4 |        4 |
| seaborn            | `copy: param (annotated)`                    |      5 |      5 |        3 |
| seaborn            | `call: builtin max()`                        |      5 |      5 |        4 |
| seaborn            | `call: other.method()`                       |      4 |      3 |        2 |
| seaborn            | `SetComp (unknown elements)`                 |      3 |      2 |        2 |
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
| seaborn            | `call: builtin reversed()`                   |      1 |      1 |        0 |
| seaborn            | `call: builtin slice()`                      |      1 |      1 |        1 |
| seaborn            | `copy: builtin`                              |      1 |      0 |        0 |
| seaborn            | `call: builtin str()`                        |      1 |      0 |        0 |
| seaborn            | `call: builtin map()`                        |      1 |      1 |        1 |
| seaborn            | `call: self name`                            |      1 |      1 |        1 |
| aiohttp            | `call: chained .method()`                    |    106 |    102 |       71 |
| aiohttp            | `attr: self.x`                               |     80 |     76 |       42 |
| aiohttp            | `other constant`                             |     74 |      2 |        2 |
| aiohttp            | `call: local.method()`                       |     66 |     59 |       42 |
| aiohttp            | `call: module.func()`                        |     43 |     28 |       27 |
| aiohttp            | `attr: local.x`                              |     34 |     32 |       21 |
| aiohttp            | `copy: local`                                |     27 |     27 |       22 |
| aiohttp            | `attr: chained`                              |     25 |     13 |       11 |
| aiohttp            | `conditional`                                |     25 |     23 |       13 |
| aiohttp            | `attr: param.x`                              |     25 |     24 |       11 |
| aiohttp            | `tuple (mixed/unknown elements)`             |     19 |     12 |       10 |
| aiohttp            | `subscript: other`                           |     18 |     18 |       18 |
| aiohttp            | `call: self.method()`                        |     16 |     14 |       11 |
| aiohttp            | `call: param.method()`                       |     16 |     16 |       11 |
| aiohttp            | `copy: param (annotated)`                    |     15 |     14 |        9 |
| aiohttp            | `binop (unknown operands)`                   |     15 |      9 |        7 |
| aiohttp            | `await: call: chained .method()`             |     15 |     10 |        8 |
| aiohttp            | `None literal`                               |     14 |      8 |        8 |
| aiohttp            | `await: call: local.method()`                |     14 |      6 |        4 |
| aiohttp            | `subscript: imported[...]`                   |     13 |      0 |        0 |
| aiohttp            | `empty list`                                 |     12 |      0 |        0 |
| aiohttp            | `call: imported class`                       |     12 |      8 |        7 |
| aiohttp            | `copy: imported`                             |     11 |      0 |        0 |
| aiohttp            | `await: call: self.method()`                 |     11 |     11 |        5 |
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
| aiohttp            | `JoinedStr`                                  |      1 |      0 |        0 |
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
| zarr               | `call: param name`                           |     53 |     52 |       36 |
| zarr               | `call: local.method()`                       |     52 |     44 |       27 |
| zarr               | `copy: local`                                |     50 |     36 |       26 |
| zarr               | `call: self.method()`                        |     42 |     28 |       14 |
| zarr               | `attr: chained`                              |     41 |     18 |       17 |
| zarr               | `subscript: param[...]`                      |     31 |     30 |       27 |
| zarr               | `call: builtin tuple()`                      |     31 |     25 |       24 |
| zarr               | `subscript: other`                           |     29 |     22 |       21 |
| zarr               | `subscript: local[...]`                      |     25 |     20 |       12 |
| zarr               | `call: module function (annotated)`          |     23 |     18 |        5 |
| zarr               | `other constant`                             |     22 |      8 |        8 |
| zarr               | `await: call: chained .method()`             |     22 |     14 |        3 |
| zarr               | `ListComp (unknown elements)`                |     20 |      8 |        7 |
| zarr               | `copy: param (annotated)`                    |     20 |     14 |        8 |
| zarr               | `conditional`                                |     17 |      9 |        6 |
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
| zarr               | `tuple (mixed/unknown elements)`             |      9 |      9 |        6 |
| zarr               | `attr: self.x`                               |      8 |      8 |        2 |
| zarr               | `binop (one side literal)`                   |      8 |      4 |        4 |
| zarr               | `empty dict`                                 |      6 |      0 |        0 |
| zarr               | `boolop (or)`                                |      6 |      5 |        3 |
| zarr               | `call: builtin enumerate()`                  |      6 |      5 |        5 |
| zarr               | `compare`                                    |      6 |      6 |        6 |
| zarr               | `list (mixed/unknown elements)`              |      6 |      3 |        3 |
| zarr               | `JoinedStr`                                  |      6 |      3 |        3 |
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
| zarr               | `subscript: self[...]`                       |      3 |      3 |        3 |
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
| joblib             | `call: imported function`                    |    118 |     19 |       16 |
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
| networkx           | `call: module.func()`                        |  4,476 |    583 |      504 |
| networkx           | `call: local.method()`                       |    791 |    401 |      301 |
| networkx           | `call: imported function`                    |    725 |    200 |      140 |
| networkx           | `copy: local`                                |    667 |    468 |      333 |
| networkx           | `call: param.method()`                       |    602 |    481 |      372 |
| networkx           | `copy: param (unannotated)`                  |    503 |    373 |      216 |
| networkx           | `call: module function (unannotated)`        |    474 |    346 |      255 |
| networkx           | `call: chained .method()`                    |    456 |    215 |      160 |
| networkx           | `binop (unknown operands)`                   |    383 |    317 |      273 |
| networkx           | `call: builtin list()`                       |    373 |    150 |      103 |
| networkx           | `call: self.method()`                        |    334 |    113 |       57 |
| networkx           | `subscript: other`                           |    326 |    213 |      154 |
| networkx           | `subscript: local[...]`                      |    307 |    263 |      193 |
| networkx           | `attr: self.x`                               |    296 |     75 |       33 |
| networkx           | `list (mixed/unknown elements)`              |    276 |     97 |       59 |
| networkx           | `call: builtin set()`                        |    274 |    121 |       82 |
| networkx           | `ListComp (unknown elements)`                |    267 |    159 |      111 |
| networkx           | `call: builtin sorted()`                     |    256 |     42 |       36 |
| networkx           | `DictComp (unknown elements)`                |    219 |    117 |       54 |
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
| networkx           | `attr: local.x`                              |    139 |     56 |       52 |
| networkx           | `call: builtin dict()`                       |    137 |     71 |       38 |
| networkx           | `call: builtin sum()`                        |    126 |     80 |       72 |
| networkx           | `conditional`                                |    126 |     85 |       46 |
| networkx           | `call: other name`                           |    123 |     93 |       56 |
| networkx           | `GeneratorExp (unknown elements)`            |    106 |     74 |       73 |
| networkx           | `attr: param.x`                              |    105 |     91 |       70 |
| networkx           | `binop (one side literal)`                   |    102 |     79 |       78 |
| networkx           | `SetComp (unknown elements)`                 |     95 |     51 |       33 |
| networkx           | `attr: module.x`                             |     91 |     30 |       30 |
| networkx           | `call: builtin enumerate()`                  |     87 |     71 |       48 |
| networkx           | `call: builtin next()`                       |     79 |     67 |       46 |
| networkx           | `attr: chained`                              |     79 |     30 |       25 |
| networkx           | `other constant`                             |     69 |     53 |       53 |
| networkx           | `call: builtin.method()`                     |     61 |     40 |       28 |
| networkx           | `call: builtin min()`                        |     60 |     56 |       42 |
| networkx           | `None literal`                               |     60 |     50 |       50 |
| networkx           | `copy: global`                               |     58 |      0 |        0 |
| networkx           | `call: capitalised`                          |     53 |      6 |        5 |
| networkx           | `call: builtin max()`                        |     47 |     43 |       38 |
| networkx           | `set (mixed/unknown elements)`               |     45 |     29 |       12 |
| networkx           | `copy: other`                                |     32 |     19 |        9 |
| networkx           | `call: other.method()`                       |     32 |     25 |       17 |
| networkx           | `subscript: other[...]`                      |     28 |     28 |        8 |
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
| networkx           | `call: builtin compile()`                    |      1 |      1 |        1 |
| networkx           | `call: builtin getattr()`                    |      1 |      0 |        0 |
| networkx           | `call: cls name`                             |      1 |      0 |        0 |
| nibabel            | `call: module.func()`                        |    551 |    130 |      119 |
| nibabel            | `call: chained .method()`                    |    411 |    125 |      113 |
| nibabel            | `call: imported function`                    |    366 |     48 |       36 |
| nibabel            | `tuple (mixed/unknown elements)`             |    337 |     67 |       33 |
| nibabel            | `call: local.method()`                       |    320 |     65 |       60 |
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
| nibabel            | `other constant`                             |     56 |     10 |       10 |
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
| nibabel            | `DictComp (unknown elements)`                |      5 |      3 |        3 |
| nibabel            | `SetComp (unknown elements)`                 |      4 |      1 |        1 |
| nibabel            | `call: builtin min()`                        |      4 |      1 |        1 |
| nibabel            | `call: modclass.method()`                    |      4 |      4 |        4 |
| nibabel            | `call: builtin.method()`                     |      4 |      1 |        1 |
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
| narwhals           | `call: chained .method()`                    |    214 |    169 |      147 |
| narwhals           | `call: imported function`                    |    204 |    128 |       90 |
| narwhals           | `attr: chained`                              |    135 |    113 |       89 |
| narwhals           | `conditional`                                |    133 |    117 |       72 |
| narwhals           | `call: module.func()`                        |    129 |    113 |      108 |
| narwhals           | `call: local.method()`                       |     98 |     85 |       68 |
| narwhals           | `attr: self.x`                               |     93 |     85 |       77 |
| narwhals           | `call: self.method()`                        |     84 |     71 |       60 |
| narwhals           | `call: param.method()`                       |     80 |     51 |       30 |
| narwhals           | `ListComp (unknown elements)`                |     65 |     48 |       36 |
| narwhals           | `tuple (mixed/unknown elements)`             |     59 |     50 |       32 |
| narwhals           | `call: module function (annotated)`          |     55 |     34 |       32 |
| narwhals           | `attr: param.x`                              |     45 |     41 |       30 |
| narwhals           | `binop (unknown operands)`                   |     38 |     31 |       31 |
| narwhals           | `call: imported class`                       |     38 |      8 |        8 |
| narwhals           | `GeneratorExp (unknown elements)`            |     28 |     22 |       22 |
| narwhals           | `attr: local.x`                              |     27 |     23 |       22 |
| narwhals           | `attr: imported.x`                           |     24 |      1 |        1 |
| narwhals           | `call: builtin list()`                       |     19 |     15 |       15 |
| narwhals           | `call: other.method()`                       |     19 |     17 |       10 |
| narwhals           | `copy: param (annotated)`                    |     18 |     18 |       10 |
| narwhals           | `copy: local`                                |     18 |     16 |       13 |
| narwhals           | `subscript: other`                           |     17 |     15 |       13 |
| narwhals           | `call: builtin tuple()`                      |     16 |     16 |       12 |
| narwhals           | `DictComp (unknown elements)`                |     15 |     14 |        5 |
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
| xarray             | `call: chained .method()`                    |  1,401 |    172 |      112 |
| xarray             | `call: module.func()`                        |  1,388 |    106 |      102 |
| xarray             | `call: imported function`                    |    933 |    172 |      118 |
| xarray             | `call: local.method()`                       |    923 |    106 |       71 |
| xarray             | `binop (unknown operands)`                   |    737 |     93 |       77 |
| xarray             | `call: self.method()`                        |    449 |    106 |       94 |
| xarray             | `call: module function (unannotated)`        |    392 |     65 |       44 |
| xarray             | `call: param.method()`                       |    333 |    152 |      104 |
| xarray             | `subscript: local[...]`                      |    298 |     32 |       23 |
| xarray             | `subscript: other`                           |    250 |     41 |       34 |
| xarray             | `attr: chained`                              |    236 |     45 |       35 |
| xarray             | `dict (mixed/unknown elements)`              |    204 |     10 |        8 |
| xarray             | `ListComp (unknown elements)`                |    203 |     73 |       61 |
| xarray             | `call: imported.attr()`                      |    179 |     51 |       32 |
| xarray             | `call: param name`                           |    170 |      6 |        4 |
| xarray             | `list (mixed/unknown elements)`              |    162 |     20 |       18 |
| xarray             | `conditional`                                |    149 |     56 |       39 |
| xarray             | `DictComp (unknown elements)`                |    148 |     56 |       41 |
| xarray             | `copy: local`                                |    148 |     55 |       42 |
| xarray             | `call: builtin zip()`                        |    144 |     49 |       35 |
| xarray             | `attr: local.x`                              |    131 |     43 |       33 |
| xarray             | `empty dict`                                 |    120 |      0 |        0 |
| xarray             | `copy: param (unannotated)`                  |    116 |     40 |       28 |
| xarray             | `call: local name`                           |    116 |      6 |        3 |
| xarray             | `binop (one side literal)`                   |    108 |      9 |        9 |
| xarray             | `call: imported class`                       |    101 |      5 |        4 |
| xarray             | `attr: self.x`                               |     86 |     40 |       31 |
| xarray             | `call: module function (annotated)`          |     84 |     27 |       17 |
| xarray             | `call: builtin tuple()`                      |     83 |     44 |       36 |
| xarray             | `attr: param.x`                              |     82 |     32 |       24 |
| xarray             | `call: builtin getattr()`                    |     80 |     29 |       16 |
| xarray             | `empty list`                                 |     80 |      0 |        0 |
| xarray             | `call: other name`                           |     80 |     10 |       10 |
| xarray             | `subscript: param[...]`                      |     76 |     29 |       13 |
| xarray             | `call: builtin dict()`                       |     73 |     13 |        5 |
| xarray             | `call: other callee`                         |     65 |      9 |        3 |
| xarray             | `tuple (mixed/unknown elements)`             |     62 |      9 |        7 |
| xarray             | `call: builtin set()`                        |     55 |     20 |       17 |
| xarray             | `compare`                                    |     53 |     19 |       18 |
| xarray             | `other constant`                             |     52 |      1 |        1 |
| xarray             | `copy: param (annotated)`                    |     44 |     26 |       18 |
| xarray             | `call: global.method()`                      |     41 |      1 |        1 |
| xarray             | `call: builtin list()`                       |     40 |     18 |       15 |
| xarray             | `call: builtin enumerate()`                  |     40 |     17 |        8 |
| xarray             | `copy: imported`                             |     39 |      0 |        0 |
| xarray             | `attr: global.x`                             |     36 |      0 |        0 |
| xarray             | `Lambda`                                     |     34 |     21 |       21 |
| xarray             | `None literal`                               |     30 |     16 |       16 |
| xarray             | `attr: module.x`                             |     26 |      0 |        0 |
| xarray             | `SetComp (unknown elements)`                 |     25 |     16 |       12 |
| xarray             | `subscript: imported[...]`                   |     21 |     13 |       13 |
| xarray             | `boolop (or)`                                |     18 |      8 |        7 |
| xarray             | `call: other.method()`                       |     18 |      3 |        3 |
| xarray             | `call: builtin next()`                       |     16 |     11 |        6 |
| xarray             | `call: builtin.method()`                     |     15 |      8 |        7 |
| xarray             | `boolop (and)`                               |     12 |      4 |        3 |
| xarray             | `call: builtin sorted()`                     |     11 |      5 |        3 |
| xarray             | `call: modclass.method()`                    |     10 |      0 |        0 |
| xarray             | `copy: other`                                |     10 |      2 |        2 |
| xarray             | `copy: self`                                 |     10 |      7 |        6 |
| xarray             | `GeneratorExp (unknown elements)`            |      9 |      5 |        5 |
| xarray             | `copy: global`                               |      9 |      0 |        0 |
| xarray             | `subscript: global[...]`                     |      8 |      4 |        1 |
| xarray             | `subscript: other[...]`                      |      8 |      5 |        5 |
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
| xarray             | `unaryop USub`                               |      2 |      0 |        0 |
| xarray             | `empty tuple`                                |      1 |      0 |        0 |
| xarray             | `await: call: imported.attr()`               |      1 |      0 |        0 |
| xarray             | `JoinedStr`                                  |      1 |      1 |        1 |
| xarray             | `call: builtin property()`                   |      1 |      0 |        0 |
| xarray             | `call: cls.method()`                         |      1 |      1 |        1 |
| xarray             | `call: builtin compile()`                    |      1 |      1 |        1 |
| xarray             | `call: builtin any()`                        |      1 |      1 |        1 |
| xarray             | `await: call: param name`                    |      1 |      0 |        0 |
| xarray             | `await: call: local.method()`                |      1 |      0 |        0 |
| xarray             | `await: call: module.func()`                 |      1 |      0 |        0 |
| xarray             | `await: copy: local`                         |      1 |      0 |        0 |
| xarray             | `attr: other.x`                              |      1 |      1 |        1 |
| litestar           | `call: imported function`                    |     84 |     64 |       45 |
| litestar           | `call: chained .method()`                    |     79 |     64 |       43 |
| litestar           | `conditional`                                |     63 |     59 |       35 |
| litestar           | `call: local.method()`                       |     57 |     43 |       28 |
| litestar           | `subscript: other`                           |     56 |     50 |       33 |
| litestar           | `call: param.method()`                       |     54 |     36 |       22 |
| litestar           | `call: builtin getattr()`                    |     47 |     43 |       15 |
| litestar           | `attr: chained`                              |     36 |     32 |       19 |
| litestar           | `attr: self.x`                               |     34 |     32 |       12 |
| litestar           | `await: call: self.method()`                 |     33 |     31 |       25 |
| litestar           | `call: self.method()`                        |     33 |     29 |       19 |
| litestar           | `attr: param.x`                              |     28 |     20 |        7 |
| litestar           | `attr: local.x`                              |     28 |     20 |       13 |
| litestar           | `copy: local`                                |     25 |     18 |       14 |
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
| litestar           | `await: call: chained .method()`             |     13 |     13 |       11 |
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
| litestar           | `list (mixed/unknown elements)`              |      6 |      4 |        3 |
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
| litestar           | `attr: other.x`                              |      2 |      2 |        1 |
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
| celery             | `call: self.method()`                        |    185 |    138 |      101 |
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
| optuna             | `call: chained .method()`                    |    209 |    154 |      119 |
| optuna             | `call: imported.attr()`                      |    108 |     41 |       41 |
| optuna             | `binop (unknown operands)`                   |     87 |     76 |       74 |
| optuna             | `call: imported function`                    |     79 |      5 |        3 |
| optuna             | `empty list`                                 |     71 |      0 |        0 |
| optuna             | `attr: param.x`                              |     65 |     59 |       49 |
| optuna             | `call: local.method()`                       |     62 |     33 |       27 |
| optuna             | `subscript: other`                           |     54 |     43 |       36 |
| optuna             | `call: module function (annotated)`          |     39 |     34 |       33 |
| optuna             | `subscript: param[...]`                      |     35 |     35 |       33 |
| optuna             | `call: builtin zip()`                        |     35 |     24 |       18 |
| optuna             | `call: imported class`                       |     35 |      0 |        0 |
| optuna             | `call: param.method()`                       |     33 |     18 |       14 |
| optuna             | `subscript: local[...]`                      |     32 |     27 |       24 |
| optuna             | `ListComp (unknown elements)`                |     32 |     23 |       21 |
| optuna             | `attr: chained`                              |     31 |     19 |       15 |
| optuna             | `binop (one side literal)`                   |     28 |     26 |       26 |
| optuna             | `conditional`                                |     28 |     21 |       13 |
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
| optuna             | `call: self.method()`                        |      9 |      7 |        4 |
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
| optuna             | `subscript: other[...]`                      |      2 |      1 |        1 |
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
| dask               | `call: imported function`                    |  1,742 |    334 |      248 |
| dask               | `call: chained .method()`                    |  1,446 |    177 |      145 |
| dask               | `call: local.method()`                       |  1,411 |    164 |      104 |
| dask               | `call: global.method()`                      |    908 |     11 |        9 |
| dask               | `call: module function (unannotated)`        |    491 |    215 |      151 |
| dask               | `call: param.method()`                       |    470 |    213 |      142 |
| dask               | `dict (mixed/unknown elements)`              |    446 |     56 |       45 |
| dask               | `binop (unknown operands)`                   |    405 |    215 |      171 |
| dask               | `copy: param (unannotated)`                  |    390 |    159 |      105 |
| dask               | `list (mixed/unknown elements)`              |    366 |     58 |       32 |
| dask               | `ListComp (unknown elements)`                |    350 |    194 |      140 |
| dask               | `subscript: other`                           |    333 |     89 |       68 |
| dask               | `empty list`                                 |    296 |      0 |        0 |
| dask               | `tuple (mixed/unknown elements)`             |    269 |     83 |       73 |
| dask               | `subscript: local[...]`                      |    247 |     98 |       71 |
| dask               | `call: builtin zip()`                        |    235 |    119 |       92 |
| dask               | `copy: local`                                |    232 |    109 |       79 |
| dask               | `call: builtin list()`                       |    211 |    109 |       83 |
| dask               | `binop (one side literal)`                   |    195 |     29 |       29 |
| dask               | `empty dict`                                 |    193 |      0 |        0 |
| dask               | `subscript: param[...]`                      |    180 |    113 |       86 |
| dask               | `attr: chained`                              |    178 |     75 |       56 |
| dask               | `call: module class`                         |    173 |      6 |        5 |
| dask               | `DictComp (unknown elements)`                |    168 |     88 |       66 |
| dask               | `attr: self.x`                               |    166 |    129 |       62 |
| dask               | `call: other callee`                         |    152 |     22 |       14 |
| dask               | `conditional`                                |    149 |     80 |       44 |
| dask               | `call: builtin getattr()`                    |    146 |     33 |       19 |
| dask               | `call: local name`                           |    143 |     34 |       18 |
| dask               | `attr: local.x`                              |    141 |     67 |       53 |
| dask               | `call: builtin enumerate()`                  |    135 |     92 |       68 |
| dask               | `call: param name`                           |    131 |     25 |       10 |
| dask               | `call: self.method()`                        |    129 |    112 |       64 |
| dask               | `attr: imported.x`                           |    112 |      1 |        1 |
| dask               | `other constant`                             |    100 |     26 |       26 |
| dask               | `attr: param.x`                              |     98 |     66 |       47 |
| dask               | `call: builtin tuple()`                      |     96 |     58 |       44 |
| dask               | `call: builtin set()`                        |     83 |     21 |       15 |
| dask               | `call: builtin staticmethod()`               |     79 |      0 |        0 |
| dask               | `call: builtin dict()`                       |     72 |     19 |        9 |
| dask               | `call: imported.attr()`                      |     70 |     36 |       24 |
| dask               | `None literal`                               |     67 |     36 |       36 |
| dask               | `call: imported class`                       |     64 |     10 |       10 |
| dask               | `attr: module.x`                             |     59 |      1 |        1 |
| dask               | `boolop (or)`                                |     56 |     46 |       38 |
| dask               | `Lambda`                                     |     53 |      3 |        3 |
| dask               | `call: other name`                           |     51 |     20 |       14 |
| dask               | `compare`                                    |     48 |     18 |       17 |
| dask               | `call: module function (annotated)`          |     36 |     28 |       11 |
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
| dask               | `empty tuple`                                |      5 |      0 |        0 |
| dask               | `call: builtin range()`                      |      5 |      4 |        4 |
| dask               | `call: builtin open()`                       |      5 |      0 |        0 |
| dask               | `call: builtin object()`                     |      4 |      0 |        0 |
| dask               | `call: builtin.method()`                     |      3 |      1 |        1 |
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
| dask               | `call: builtin any()`                        |      1 |      0 |        0 |
| dask               | `await: call: chained .method()`             |      1 |      0 |        0 |
| dask               | `call: builtin reversed()`                   |      1 |      1 |        1 |
| dask               | `call: builtin len()`                        |      1 |      1 |        1 |
| dask               | `call: builtin frozenset()`                  |      1 |      1 |        0 |
| dask               | `await: call: local.method()`                |      1 |      0 |        0 |
| mypy               | `call: imported function`                    |    515 |    335 |      117 |
| mypy               | `call: chained .method()`                    |    370 |    259 |      149 |
| mypy               | `call: self.method()`                        |    339 |    262 |       87 |
| mypy               | `copy: local`                                |    256 |    170 |      103 |
| mypy               | `attr: chained`                              |    253 |    173 |      135 |
| mypy               | `attr: param.x`                              |    236 |    199 |      101 |
| mypy               | `empty list`                                 |    229 |      0 |        0 |
| mypy               | `subscript: other`                           |    224 |    143 |       81 |
| mypy               | `attr: local.x`                              |    224 |    133 |       93 |
| mypy               | `call: local.method()`                       |    193 |    131 |       83 |
| mypy               | `call: module function (annotated)`          |    124 |     89 |       30 |
| mypy               | `call: param.method()`                       |    106 |     87 |       46 |
| mypy               | `ListComp (unknown elements)`                |    102 |     62 |       40 |
| mypy               | `copy: param (annotated)`                    |    101 |     87 |       42 |
| mypy               | `call: builtin zip()`                        |     99 |     73 |       29 |
| mypy               | `conditional`                                |     99 |     66 |       37 |
| mypy               | `None literal`                               |     92 |     67 |       67 |
| mypy               | `call: module.func()`                        |     86 |     35 |       19 |
| mypy               | `binop (unknown operands)`                   |     75 |     34 |       27 |
| mypy               | `attr: self.x`                               |     71 |     60 |       39 |
| mypy               | `subscript: local[...]`                      |     67 |     45 |       27 |
| mypy               | `subscript: param[...]`                      |     66 |     42 |       29 |
| mypy               | `call: builtin enumerate()`                  |     64 |     58 |       25 |
| mypy               | `boolop (or)`                                |     51 |     34 |       28 |
| mypy               | `tuple (mixed/unknown elements)`             |     48 |     31 |       24 |
| mypy               | `other constant`                             |     42 |     11 |       11 |
| mypy               | `call: builtin set()`                        |     40 |      8 |        7 |
| mypy               | `boolop (and)`                               |     33 |     28 |       26 |
| mypy               | `call: builtin sorted()`                     |     33 |     12 |       11 |
| mypy               | `list (mixed/unknown elements)`              |     33 |     13 |        8 |
| mypy               | `call: imported.attr()`                      |     29 |     21 |       14 |
| mypy               | `empty dict`                                 |     28 |      0 |        0 |
| mypy               | `SetComp (unknown elements)`                 |     27 |     14 |       13 |
| mypy               | `call: builtin list()`                       |     24 |     13 |        9 |
| mypy               | `DictComp (unknown elements)`                |     22 |     13 |        9 |
| mypy               | `call: builtin getattr()`                    |     21 |     15 |        7 |
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
| mypy               | `call: other.method()`                       |      6 |      6 |        3 |
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
| django             | released                              |                  | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |              |      |       |              |                 |
| django             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |              |                 |
| django             | infer-union                           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            |            0 |    0 |     0 |              |                 |
| sqlalchemy         | released (from mega-11-06-2026-0441)  |                  | 29,521 passed, 975 skipped                                            |              |      |       |              |                 |
| sqlalchemy         | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sqlalchemy         | infer-union                           | True             | 29,521 passed, 975 skipped                                            |            0 |    0 |     0 |            0 |               0 |
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
| sphinx             | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-union                           | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
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
| altair             | released (from mega-11-06-2026-0441)  |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |              |                 |
| altair             | fix-certain                           | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | fix-likely                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-basedpyright                    | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-pyrefly                         | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-trace                           | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-ty                              | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |            0 |               0 |
| altair             | infer-union                           | True             | 28 failed, 1,866 passed, 12 skipped, 7 xfailed, 3 xpassed             |            0 |    0 |     0 |            0 |               0 |
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
| zarr               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| zarr               | infer-union                           | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |            0 |               0 |
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
| nibabel            | released                              |                  | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |              |      |       |              |                 |
| nibabel            | fix-certain                           | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | fix-likely                            | True             | 20 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | fix-unsafe                            | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | infer-basedpyright                    | True             | 21 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | infer-pyrefly                         | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-trace                           | True             | 19 error, 109 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | infer-ty                              | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | infer-union                           | False            | 20 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            1 |    0 |     0 |            0 |               0 |
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
| sqlalchemy         | fix-certain        |      1 |   1 |    0 |    183 files changed, 2265 insertions(+), 1722 deletions(-) |
| sqlalchemy         | fix-likely         |      1 |   1 |    0 |    193 files changed, 2730 insertions(+), 2142 deletions(-) |
| sqlalchemy         | fix-unsafe         |      1 |   1 |    0 |    206 files changed, 3444 insertions(+), 2818 deletions(-) |
| sqlalchemy         | infer-basedpyright |      4 |   4 |    0 |    210 files changed, 4188 insertions(+), 3517 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      2 |   2 |    0 |    209 files changed, 3924 insertions(+), 3141 deletions(-) |
| sqlalchemy         | infer-trace        |      7 |   7 |    0 |    208 files changed, 3642 insertions(+), 2957 deletions(-) |
| sqlalchemy         | infer-ty           |      3 |   3 |    0 |    208 files changed, 4133 insertions(+), 3362 deletions(-) |
| sqlalchemy         | infer-union        |     11 |  11 |    0 |    214 files changed, 4699 insertions(+), 3770 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1694 insertions(+), 1280 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1694 insertions(+), 1280 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1694 insertions(+), 1280 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1920 insertions(+), 1493 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1953 insertions(+), 1412 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1694 insertions(+), 1280 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1827 insertions(+), 1405 deletions(-) |
| pydantic           | infer-union        |      3 |   3 |    0 |     79 files changed, 2013 insertions(+), 1524 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    261 |   3 |    1 | 1072 files changed, 18527 insertions(+), 15425 deletions(-) |
| pandas             | fix-likely         |    261 |   3 |    1 | 1204 files changed, 43375 insertions(+), 39441 deletions(-) |
| pandas             | fix-unsafe         |    266 |   8 |    1 | 1208 files changed, 44781 insertions(+), 40645 deletions(-) |
| pandas             | infer-basedpyright |    298 |  40 |    1 | 1216 files changed, 50817 insertions(+), 46056 deletions(-) |
| pandas             | infer-pyrefly      |    318 |  60 |    1 | 1217 files changed, 53226 insertions(+), 48143 deletions(-) |
| pandas             | infer-trace        |    266 |   8 |    1 | 1212 files changed, 46298 insertions(+), 42038 deletions(-) |
| pandas             | infer-ty           |    273 |  15 |    1 | 1218 files changed, 50615 insertions(+), 45861 deletions(-) |
| pandas             | infer-union        |    337 |  79 |    1 | 1226 files changed, 56523 insertions(+), 51078 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 151 insertions(+), 116 deletions(-) |
| structlog          | infer-union        |      8 |   0 |    0 |       16 files changed, 176 insertions(+), 132 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 456 insertions(+), 356 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 463 insertions(+), 362 deletions(-) |
| click              | infer-union        |      0 |   0 |    0 |       15 files changed, 472 insertions(+), 368 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 222 insertions(+), 151 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 238 insertions(+), 166 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 162 deletions(-) |
| hypercorn          | infer-union        |     12 |   0 |    0 |       25 files changed, 249 insertions(+), 168 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 489 insertions(+), 377 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 526 insertions(+), 414 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 509 insertions(+), 398 deletions(-) |
| starlette          | infer-union        |      0 |   0 |    0 |       33 files changed, 533 insertions(+), 415 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 843 insertions(+), 566 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 848 insertions(+), 581 deletions(-) |
| werkzeug           | infer-union        |      0 |   0 |    0 |       45 files changed, 896 insertions(+), 603 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 415 insertions(+), 344 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 370 insertions(+), 298 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 399 insertions(+), 320 deletions(-) |
| httpx              | infer-union        |      1 |   1 |    0 |       17 files changed, 438 insertions(+), 350 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | infer-basedpyright |      4 |   4 |    0 |       29 files changed, 378 insertions(+), 288 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 339 insertions(+), 246 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 313 insertions(+), 232 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 360 insertions(+), 273 deletions(-) |
| uvicorn            | infer-union        |      4 |   4 |    0 |       29 files changed, 382 insertions(+), 288 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 972 insertions(+), 693 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 972 insertions(+), 693 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1069 insertions(+), 768 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1185 insertions(+), 877 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1151 insertions(+), 832 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1069 insertions(+), 768 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1188 insertions(+), 850 deletions(-) |
| mcp                | infer-union        |      3 |   3 |    0 |      83 files changed, 1232 insertions(+), 881 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-basedpyright |     12 |   2 |    0 |     156 files changed, 1135 insertions(+), 857 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |     154 files changed, 1052 insertions(+), 787 deletions(-) |
| strawberry-graphql | infer-ty           |     10 |   0 |    0 |     156 files changed, 1133 insertions(+), 850 deletions(-) |
| strawberry-graphql | infer-union        |     12 |   2 |    0 |     156 files changed, 1160 insertions(+), 871 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    190 files changed, 2039 insertions(+), 1413 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |    178 files changed, 1804 insertions(+), 1198 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | infer-ty           |     24 |  24 |    0 |    187 files changed, 2304 insertions(+), 1419 deletions(-) |
| streamlink         | infer-union        |     25 |  25 |    0 |    198 files changed, 2509 insertions(+), 1585 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    196 files changed, 3475 insertions(+), 2361 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    198 files changed, 4018 insertions(+), 2792 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    213 files changed, 4440 insertions(+), 3143 deletions(-) |
| sphinx             | infer-basedpyright |      6 |   3 |    0 |    216 files changed, 5232 insertions(+), 3853 deletions(-) |
| sphinx             | infer-pyrefly      |     11 |   8 |    0 |    217 files changed, 5468 insertions(+), 3903 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    213 files changed, 4440 insertions(+), 3143 deletions(-) |
| sphinx             | infer-ty           |      4 |   1 |    0 |    215 files changed, 5277 insertions(+), 3826 deletions(-) |
| sphinx             | infer-union        |     12 |   9 |    0 |    217 files changed, 5534 insertions(+), 3964 deletions(-) |
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | fix-unsafe         |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | infer-basedpyright |    660 |   1 |    0 |      81 files changed, 1304 insertions(+), 967 deletions(-) |
| pint               | infer-pyrefly      |    664 |   5 |    0 |      79 files changed, 1095 insertions(+), 803 deletions(-) |
| pint               | infer-trace        |    662 |   3 |    0 |      78 files changed, 1038 insertions(+), 764 deletions(-) |
| pint               | infer-ty           |    660 |   2 |    1 |      79 files changed, 1185 insertions(+), 882 deletions(-) |
| pint               | infer-union        |    666 |   8 |    1 |     81 files changed, 1376 insertions(+), 1001 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |       40 files changed, 565 insertions(+), 446 deletions(-) |
| altair             | infer-pyrefly      |      4 |   3 |    0 |       40 files changed, 547 insertions(+), 426 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 489 insertions(+), 388 deletions(-) |
| altair             | infer-ty           |      4 |   3 |    0 |       40 files changed, 561 insertions(+), 440 deletions(-) |
| altair             | infer-union        |      5 |   4 |    0 |       40 files changed, 602 insertions(+), 464 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |      46 files changed, 1068 insertions(+), 831 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |       46 files changed, 865 insertions(+), 653 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |      46 files changed, 1068 insertions(+), 831 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      46 files changed, 1068 insertions(+), 831 deletions(-) |
| seaborn            | infer-pyrefly      |     39 |   0 |    0 |      47 files changed, 1158 insertions(+), 880 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |      47 files changed, 1012 insertions(+), 767 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |      46 files changed, 1035 insertions(+), 804 deletions(-) |
| seaborn            | infer-union        |     39 |   0 |    0 |      48 files changed, 1290 insertions(+), 984 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 378 insertions(+), 250 deletions(-) |
| websockets         | fix-likely         |      1 |   1 |    0 |       39 files changed, 467 insertions(+), 323 deletions(-) |
| websockets         | fix-unsafe         |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 631 insertions(+), 459 deletions(-) |
| websockets         | infer-pyrefly      |      4 |   4 |    0 |       40 files changed, 642 insertions(+), 462 deletions(-) |
| websockets         | infer-trace        |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-ty           |      4 |   4 |    0 |       40 files changed, 643 insertions(+), 459 deletions(-) |
| websockets         | infer-union        |      5 |   5 |    0 |       40 files changed, 670 insertions(+), 485 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    460 files changed, 6601 insertions(+), 5620 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    460 files changed, 6601 insertions(+), 5620 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    460 files changed, 6601 insertions(+), 5620 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    476 files changed, 7939 insertions(+), 6593 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    473 files changed, 7250 insertions(+), 6033 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    476 files changed, 7135 insertions(+), 5909 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    466 files changed, 7153 insertions(+), 6017 deletions(-) |
| networkx           | infer-union        |      0 |   0 |    0 |    489 files changed, 8910 insertions(+), 7098 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    183 files changed, 2082 insertions(+), 1390 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    194 files changed, 2936 insertions(+), 2150 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    199 files changed, 3305 insertions(+), 2457 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    203 files changed, 3968 insertions(+), 2999 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    204 files changed, 3909 insertions(+), 2884 deletions(-) |
| nibabel            | infer-trace        |     14 |   2 |    0 |    199 files changed, 3403 insertions(+), 2523 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    201 files changed, 3921 insertions(+), 2948 deletions(-) |
| nibabel            | infer-union        |     18 |   6 |    0 |    205 files changed, 4778 insertions(+), 3590 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     20 |   1 |    0 |     100 files changed, 1132 insertions(+), 929 deletions(-) |
| narwhals           | fix-likely         |     20 |   1 |    0 |    100 files changed, 1212 insertions(+), 1001 deletions(-) |
| narwhals           | fix-unsafe         |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-basedpyright |     27 |   8 |    0 |    101 files changed, 1644 insertions(+), 1338 deletions(-) |
| narwhals           | infer-pyrefly      |     34 |  15 |    0 |    102 files changed, 1865 insertions(+), 1489 deletions(-) |
| narwhals           | infer-trace        |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-ty           |     34 |  15 |    0 |    102 files changed, 1572 insertions(+), 1284 deletions(-) |
| narwhals           | infer-union        |     45 |  26 |    0 |    102 files changed, 1931 insertions(+), 1537 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-basedpyright |     88 |   2 |    0 |     177 files changed, 1124 insertions(+), 811 deletions(-) |
| litestar           | infer-pyrefly      |     87 |   1 |    0 |      175 files changed, 988 insertions(+), 690 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-ty           |     91 |   5 |    0 |     179 files changed, 1129 insertions(+), 808 deletions(-) |
| litestar           | infer-union        |     90 |   4 |    0 |     178 files changed, 1179 insertions(+), 838 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    141 files changed, 1691 insertions(+), 1165 deletions(-) |
| optuna             | fix-likely         |     53 |   1 |    0 |    144 files changed, 1914 insertions(+), 1354 deletions(-) |
| optuna             | fix-unsafe         |     54 |   2 |    0 |    144 files changed, 2042 insertions(+), 1449 deletions(-) |
| optuna             | infer-basedpyright |     54 |   2 |    0 |    164 files changed, 2383 insertions(+), 1726 deletions(-) |
| optuna             | infer-pyrefly      |     56 |   4 |    0 |    147 files changed, 2337 insertions(+), 1689 deletions(-) |
| optuna             | infer-trace        |     54 |   2 |    0 |    144 files changed, 2042 insertions(+), 1449 deletions(-) |
| optuna             | infer-ty           |     57 |   5 |    0 |    162 files changed, 2394 insertions(+), 1726 deletions(-) |
| optuna             | infer-union        |     59 |   7 |    0 |    164 files changed, 2645 insertions(+), 1919 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    160 files changed, 5400 insertions(+), 3339 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    166 files changed, 6639 insertions(+), 4417 deletions(-) |
| mypy               | fix-unsafe         |     14 |  14 |    0 |    167 files changed, 7057 insertions(+), 4768 deletions(-) |
| mypy               | infer-basedpyright |     20 |  20 |    0 |    170 files changed, 8789 insertions(+), 6312 deletions(-) |
| mypy               | infer-pyrefly      |     20 |  20 |    0 |    170 files changed, 9329 insertions(+), 6467 deletions(-) |
| mypy               | infer-trace        |     14 |  14 |    0 |    167 files changed, 7057 insertions(+), 4768 deletions(-) |
| mypy               | infer-ty           |     26 |  26 |    0 |    170 files changed, 9096 insertions(+), 6485 deletions(-) |
| mypy               | infer-union        |     30 |  30 |    0 |    170 files changed, 9421 insertions(+), 6529 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    63.9 |       134.3 |  2.1 |    3.68 |          3 |     4.52 | False |
| standard library   | fix-certain              |   159.7 |       359.8 |  2.3 |    4.95 |          3 |      6.2 | False |
| standard library   | fix-likely               |   187.2 |       441.1 |  2.4 |     6.9 |          3 |     8.61 | False |
| standard library   | fix-unsafe               |   173.0 |       423.5 |  2.4 |    6.85 |          3 |     8.55 | False |
| standard library   | infer-basedpyright       |  1282.8 |      1572.8 |  1.2 |   11.12 |          2 |      5.7 | False |
| standard library   | infer-ty                 |   266.9 |       639.0 |  2.4 |    11.5 |          1 |     2.87 | False |
| standard library   | infer-pyrefly            |   332.6 |       723.2 |  2.2 |   13.86 |          2 |     6.02 | False |
| standard library   | census                   |    31.6 |        30.7 |  1.0 |    0.53 |          3 |     4.52 | False |
| standard library   | coverage                 |    12.4 |        42.3 |  3.4 |    0.75 |          4 |     0.94 | False |
| standard library   | timing                   |   213.8 |       252.1 |  1.2 |    3.64 |          2 |     4.52 | False |
| django             | check                    |     8.6 |        22.1 |  2.6 |    1.07 |          3 |     1.32 | False |
| django             | fix-certain              |    31.8 |        68.4 |  2.2 |    1.38 |          3 |     1.72 | False |
| django             | fix-likely               |    52.3 |        88.7 |  1.7 |    1.85 |          2 |     2.21 | False |
| django             | fix-unsafe               |    53.2 |        85.7 |  1.6 |    1.67 |          2 |     2.09 | False |
| django             | infer-basedpyright       |   183.5 |       377.0 |  2.1 |    5.19 |          1 |      1.2 | False |
| django             | infer-ty                 |    72.1 |       127.0 |  1.8 |    3.68 |          1 |     1.16 | False |
| django             | infer-pyrefly            |    76.3 |       134.0 |  1.8 |    4.06 |          2 |     2.36 | False |
| django             | census                   |     8.2 |         2.7 |  0.3 |     0.1 |          3 |     1.32 | False |
| django             | coverage                 |     2.0 |         5.2 |  2.6 |    0.33 |          3 |     0.41 | False |
| django             | timing                   |    26.4 |        39.3 |  1.5 |    1.07 |          2 |     1.32 | False |
| django             | traced                   |   130.6 |       549.1 |  4.2 |    7.11 |          8 |     9.05 | False |
| django             | tests-released           |    65.5 |       450.2 |  6.9 |    4.63 |          8 |     5.18 | False |
| django             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.04 |          8 |     5.44 | False |
| django             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |         10 |     5.26 | False |
| django             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     4.12 | False |
| django             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     6.84 | False |
| django             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.04 |         12 |     6.24 | False |
| django             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     7.06 | False |
| django             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     7.64 | False |
| django             | infer-union              |   162.9 |       338.0 |  2.1 |    2.93 |          1 |     1.59 | False |
| django             | tests-infer-union        |    64.5 |       436.0 |  6.8 |    4.67 |          8 |     5.26 | False |
| django             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |      0.2 | False |
| sqlalchemy         | check                    |     9.2 |        19.0 |  2.1 |    0.88 |          2 |      1.1 | False |
| sqlalchemy         | fix-certain              |    45.8 |        62.9 |  1.4 |     1.0 |          2 |     1.25 | False |
| sqlalchemy         | fix-likely               |    42.6 |        78.3 |  1.8 |    1.31 |          2 |     1.65 | False |
| sqlalchemy         | fix-unsafe               |    49.7 |        76.2 |  1.5 |    1.26 |          1 |     1.52 | False |
| sqlalchemy         | infer-basedpyright       |   192.0 |       322.4 |  1.7 |    4.41 |          1 |     1.74 | False |
| sqlalchemy         | infer-ty                 |    74.1 |       125.4 |  1.7 |    3.52 |          1 |     1.96 | False |
| sqlalchemy         | infer-pyrefly            |    71.7 |       119.6 |  1.7 |    4.02 |          2 |     3.65 | False |
| sqlalchemy         | census                   |     8.6 |         3.7 |  0.4 |    0.09 |          2 |      1.1 | False |
| sqlalchemy         | coverage                 |     1.8 |         4.9 |  2.7 |    0.37 |          3 |     0.46 | False |
| sqlalchemy         | timing                   |    27.4 |        37.7 |  1.4 |    0.88 |          2 |     1.09 | False |
| sqlalchemy         | traced                   |   122.5 |      1155.3 |  9.4 |     6.4 |          9 |      8.2 | False |
| sqlalchemy         | tests-released           |   127.7 |       914.7 |  7.2 |     5.2 |          8 |     7.06 | False |
| sqlalchemy         | tests-fix-certain        |     0.3 |         0.1 |  0.3 |    0.03 |          7 |     8.11 | False |
| sqlalchemy         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     7.86 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.27 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.12 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.16 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.95 | False |
| sqlalchemy         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     6.07 | False |
| sqlalchemy         | infer-union              |   105.1 |       332.2 |  3.2 |    5.59 |          4 |     4.52 | False |
| sqlalchemy         | tests-infer-union        |   126.8 |       996.3 |  7.9 |    5.82 |          7 |      8.0 | False |
| sqlalchemy         | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          1 |      0.2 | False |
| sqlalchemy         | types-released           |    10.0 |         7.0 |  0.7 |    0.34 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-certain        |     7.8 |         6.7 |  0.9 |    0.33 |          1 |     0.41 | False |
| sqlalchemy         | types-fix-likely         |     7.2 |         6.5 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-unsafe         |     8.0 |         7.2 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-basedpyright |     6.4 |         6.0 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |     9.6 |         7.0 |  0.7 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-pyrefly      |     6.0 |         5.6 |  0.9 |    0.33 |          1 |     0.41 | False |
| sqlalchemy         | types-infer-trace        |     6.0 |         5.3 |  0.9 |    0.32 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     1.8 |         3.7 |  2.1 |    0.31 |          2 |     0.39 | False |
| pydantic           | fix-certain              |     3.8 |         9.4 |  2.5 |    0.41 |          3 |     0.51 | False |
| pydantic           | fix-likely               |     7.2 |        16.3 |  2.3 |     0.5 |          3 |     0.61 | False |
| pydantic           | fix-unsafe               |    10.4 |        17.0 |  1.6 |    0.44 |          3 |     0.55 | False |
| pydantic           | infer-basedpyright       |    78.2 |       132.0 |  1.7 |    2.23 |          1 |      0.2 | False |
| pydantic           | infer-ty                 |    23.6 |        31.7 |  1.3 |    1.65 |          2 |     0.61 | False |
| pydantic           | infer-pyrefly            |    36.5 |        60.0 |  1.6 |    2.73 |          1 |     0.31 | False |
| pydantic           | census                   |     0.8 |         0.6 |  0.7 |    0.05 |          2 |     0.39 | False |
| pydantic           | coverage                 |     0.8 |         1.5 |  1.9 |    0.22 |          2 |     0.27 | False |
| pydantic           | timing                   |     4.4 |         6.6 |  1.5 |    0.31 |          2 |     0.39 | False |
| pydantic           | traced                   |    86.7 |        70.8 |  0.8 |    0.55 |          1 |     0.56 | False |
| pydantic           | tests-released           |    69.1 |        44.1 |  0.6 |    0.29 |          1 |      0.4 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.35 | False |
| pydantic           | infer-union              |    95.3 |       162.7 |  1.7 |    1.98 |          1 |     0.31 | False |
| pydantic           | tests-infer-union        |    42.8 |        39.1 |  0.9 |    0.33 |          1 |     0.35 | False |
| pydantic           | tests                    |     1.4 |         1.3 |  0.9 |    0.16 |          1 |      0.2 | False |
| pydantic           | types-released           |     9.8 |        15.0 |  1.5 |    0.57 |          2 |     0.69 | False |
| pydantic           | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.66 | False |
| pydantic           | types-infer-basedpyright |    12.4 |        18.0 |  1.5 |    0.55 |          2 |     0.67 | False |
| pydantic           | types-infer-ty           |    10.8 |        16.0 |  1.5 |    0.55 |          2 |     0.67 | False |
| pydantic           | types-infer-pyrefly      |    11.2 |        16.7 |  1.5 |    0.54 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |     9.0 |        14.2 |  1.6 |    0.55 |          2 |     0.67 | False |
| pydantic           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |    27.2 |         0.9 |  0.0 |    0.21 |          3 |     4.38 | False |
| pandas             | fix-certain              |   179.7 |       397.9 |  2.2 |    4.36 |          3 |      5.2 | False |
| pandas             | fix-likely               |   244.7 |       617.8 |  2.5 |    6.97 |          3 |      8.3 | False |
| pandas             | fix-unsafe               |   239.8 |       609.1 |  2.5 |     6.9 |          2 |     8.16 | False |
| pandas             | infer-basedpyright       |   650.8 |      1310.4 |  2.0 |   12.26 |          2 |    14.52 | False |
| pandas             | infer-ty                 |   304.4 |       847.1 |  2.8 |   10.38 |          2 |     6.67 | False |
| pandas             | infer-pyrefly            |   247.7 |       743.9 |  3.0 |   16.64 |          2 |     8.09 | False |
| pandas             | census                   |    54.0 |       141.2 |  2.6 |    3.72 |          3 |     4.38 | False |
| pandas             | coverage                 |     6.0 |        20.5 |  3.4 |    0.79 |          4 |     0.99 | False |
| pandas             | timing                   |   250.9 |       305.4 |  1.2 |    3.73 |          2 |     4.38 | False |
| pandas             | traced                   |   335.2 |      1573.3 |  4.7 |   14.38 |          7 |    17.78 | False |
| pandas             | tests-released           |   111.0 |       673.0 |  6.1 |   11.49 |          9 |    14.08 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    17.44 | False |
| pandas             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     17.4 | False |
| pandas             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          7 |    17.29 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    14.48 | False |
| pandas             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    16.29 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    14.48 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    16.29 | False |
| pandas             | infer-union              |   484.2 |      1577.7 |  3.3 |   11.69 |          4 |     14.2 | False |
| pandas             | tests-infer-union        |   146.9 |       852.8 |  5.8 |   13.03 |          6 |    16.08 | False |
| pandas             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |     0.19 | False |
| pandas             | types-released           |   126.6 |       120.4 |  1.0 |     2.1 |          2 |     2.65 | False |
| pandas             | types-fix-certain        |    61.1 |        95.2 |  1.6 |    2.26 |          2 |     2.77 | False |
| pandas             | types-fix-likely         |    74.0 |       108.1 |  1.5 |    2.22 |          2 |     2.87 | False |
| pandas             | types-fix-unsafe         |    57.0 |        83.9 |  1.5 |    2.32 |          2 |     2.85 | False |
| pandas             | types-infer-basedpyright |    66.4 |       102.9 |  1.5 |    2.18 |          2 |     2.77 | False |
| pandas             | types-infer-ty           |    56.8 |        89.9 |  1.6 |    2.33 |          2 |     2.77 | False |
| pandas             | types-infer-pyrefly      |    69.5 |       105.4 |  1.5 |    2.27 |          2 |     2.89 | False |
| pandas             | types-infer-trace        |    66.3 |        97.7 |  1.5 |    2.29 |          2 |     2.89 | False |
| pandas             | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |    10.8 |        18.8 |  1.7 |    0.82 |          3 |     1.01 | False |
| twisted            | fix-certain              |    14.4 |        43.5 |  3.0 |    0.95 |          3 |     1.19 | False |
| twisted            | fix-likely               |    18.6 |        55.8 |  3.0 |    1.28 |          3 |      1.6 | False |
| twisted            | fix-unsafe               |    17.4 |        52.8 |  3.0 |    1.22 |          3 |     1.52 | False |
| twisted            | infer-basedpyright       |   193.8 |       242.3 |  1.3 |    3.73 |          1 |     0.56 | False |
| twisted            | infer-ty                 |    48.7 |       102.5 |  2.1 |    3.06 |          1 |     0.55 | False |
| twisted            | infer-pyrefly            |    53.3 |       111.3 |  2.1 |    3.72 |          1 |     0.54 | False |
| twisted            | census                   |     3.8 |         3.5 |  0.9 |    0.12 |          3 |     1.01 | False |
| twisted            | coverage                 |     2.8 |         7.2 |  2.6 |    0.37 |          3 |     0.46 | False |
| twisted            | timing                   |    33.5 |        37.6 |  1.1 |    0.82 |          2 |     1.02 | False |
| pip                | check                    |     5.0 |        12.2 |  2.4 |    0.62 |          2 |     0.77 | False |
| pip                | fix-certain              |    10.4 |        29.1 |  2.8 |    0.77 |          2 |     0.96 | False |
| pip                | fix-likely               |    12.2 |        34.7 |  2.8 |     1.0 |          3 |     1.24 | False |
| pip                | fix-unsafe               |    11.4 |        32.8 |  2.9 |    0.93 |          3 |     1.16 | False |
| pip                | infer-basedpyright       |    90.3 |       220.6 |  2.4 |    3.93 |          1 |     0.62 | False |
| pip                | infer-ty                 |    34.8 |        71.8 |  2.1 |    2.68 |          1 |     0.61 | False |
| pip                | infer-pyrefly            |    42.2 |        87.1 |  2.1 |    3.29 |          1 |     0.62 | False |
| pip                | census                   |     3.6 |         2.4 |  0.7 |     0.1 |          2 |     0.77 | False |
| pip                | coverage                 |     1.6 |         4.3 |  2.7 |    0.31 |          2 |     0.36 | False |
| pip                | timing                   |    14.0 |        21.1 |  1.5 |    0.62 |          2 |     0.77 | False |
| structlog          | check                    |     1.5 |         1.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| structlog          | fix-certain              |     2.0 |         2.9 |  1.4 |    0.26 |          2 |     0.32 | False |
| structlog          | fix-likely               |     1.4 |         2.6 |  1.9 |    0.26 |          2 |     0.32 | False |
| structlog          | fix-unsafe               |     2.2 |         3.3 |  1.5 |    0.26 |          2 |     0.32 | False |
| structlog          | infer-basedpyright       |    18.4 |        15.1 |  0.8 |    0.61 |          1 |     0.14 | False |
| structlog          | infer-ty                 |     7.9 |         5.5 |  0.7 |    0.41 |          1 |     0.32 | False |
| structlog          | infer-pyrefly            |     7.0 |         5.2 |  0.7 |    0.44 |          1 |     0.16 | False |
| structlog          | census                   |     0.5 |         0.3 |  0.6 |    0.04 |          1 |     0.21 | False |
| structlog          | coverage                 |     1.3 |         0.9 |  0.7 |    0.15 |          1 |     0.19 | False |
| structlog          | timing                   |     2.2 |         1.9 |  0.9 |    0.17 |          1 |     0.21 | False |
| structlog          | traced                   |     3.4 |         4.6 |  1.4 |    0.27 |          1 |     0.32 | False |
| structlog          | tests-released           |     3.6 |         2.0 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | infer-union              |     6.7 |        11.2 |  1.7 |    0.54 |          2 |     0.32 | False |
| structlog          | tests-infer-union        |     2.0 |         1.8 |  0.9 |    0.08 |          1 |     0.09 | False |
| structlog          | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |      0.2 | False |
| structlog          | types-released           |     1.2 |         0.5 |  0.4 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.1 | False |
| structlog          | types-infer-basedpyright |     1.0 |         0.5 |  0.5 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.8 |         0.5 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-pyrefly      |     1.4 |         0.6 |  0.4 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |      0.1 | False |
| structlog          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.2 | False |
| attrs              | fix-certain              |     2.0 |         2.6 |  1.3 |    0.27 |          2 |     0.35 | False |
| attrs              | fix-likely               |     2.0 |         2.7 |  1.4 |    0.28 |          2 |     0.35 | False |
| attrs              | fix-unsafe               |     2.4 |         3.0 |  1.2 |    0.26 |          2 |     0.35 | False |
| attrs              | infer-basedpyright       |    20.6 |        16.2 |  0.8 |    0.59 |          1 |     0.15 | False |
| attrs              | infer-ty                 |     7.8 |         5.2 |  0.7 |    0.41 |          1 |     0.34 | False |
| attrs              | infer-pyrefly            |     9.0 |         9.2 |  1.0 |    0.57 |          1 |     0.32 | False |
| attrs              | census                   |     1.6 |         1.2 |  0.7 |    0.16 |          1 |      0.2 | False |
| attrs              | coverage                 |     1.3 |         0.8 |  0.6 |    0.15 |          1 |     0.19 | False |
| attrs              | timing                   |     2.2 |         1.6 |  0.7 |    0.17 |          1 |      0.2 | False |
| attrs              | traced                   |     6.0 |        21.1 |  3.5 |    0.75 |          6 |     0.92 | False |
| attrs              | tests-released           |     2.8 |        13.6 |  4.9 |     0.6 |          6 |     0.77 | False |
| attrs              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.74 | False |
| attrs              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     0.75 | False |
| attrs              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | infer-union              |     9.4 |        18.2 |  1.9 |    0.56 |          2 |     0.32 | False |
| attrs              | tests-infer-union        |     4.0 |        18.0 |  4.5 |     0.6 |          6 |     0.74 | False |
| attrs              | tests                    |     1.8 |         1.7 |  0.9 |    0.16 |          2 |      0.2 | False |
| click              | check                    |     1.2 |         0.2 |  0.2 |    0.03 |          1 |     0.22 | False |
| click              | fix-certain              |     1.8 |         3.3 |  1.8 |    0.29 |          2 |     0.37 | False |
| click              | fix-likely               |     2.6 |         4.6 |  1.8 |     0.3 |          2 |     0.36 | False |
| click              | fix-unsafe               |     3.8 |         5.2 |  1.4 |    0.29 |          2 |     0.36 | False |
| click              | infer-basedpyright       |    16.3 |        20.5 |  1.3 |    0.68 |          1 |     0.17 | False |
| click              | infer-ty                 |     4.3 |         6.4 |  1.5 |    0.46 |          1 |     0.19 | False |
| click              | infer-pyrefly            |     6.3 |        10.3 |  1.6 |    0.64 |          1 |     0.19 | False |
| click              | census                   |     2.2 |         1.8 |  0.8 |    0.18 |          1 |     0.22 | False |
| click              | coverage                 |     0.6 |         0.9 |  1.5 |    0.17 |          2 |     0.21 | False |
| click              | timing                   |     3.6 |         2.6 |  0.7 |    0.18 |          1 |     0.22 | False |
| click              | traced                   |    13.0 |        12.8 |  1.0 |    0.31 |          1 |      0.4 | False |
| click              | tests-released           |     8.6 |         6.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| click              | infer-union              |    15.4 |        23.2 |  1.5 |     0.6 |          1 |     0.16 | False |
| click              | tests-infer-union        |     7.0 |         6.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     2.2 |         2.0 |  0.9 |    0.16 |          1 |      0.2 | False |
| click              | types-released           |     2.6 |         0.8 |  0.3 |    0.13 |          1 |     0.12 | False |
| click              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-infer-basedpyright |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-ty           |     0.9 |         0.7 |  0.8 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-pyrefly      |     1.1 |         0.7 |  0.6 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-trace        |     0.3 |         0.2 |  0.7 |    0.03 |          1 |     0.12 | False |
| click              | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.22 | False |
| hypercorn          | fix-certain              |     2.0 |         3.3 |  1.6 |    0.26 |          2 |     0.32 | False |
| hypercorn          | fix-likely               |     1.8 |         3.5 |  1.9 |    0.26 |          2 |     0.32 | False |
| hypercorn          | fix-unsafe               |     3.6 |         4.4 |  1.2 |    0.26 |          2 |     0.32 | False |
| hypercorn          | infer-basedpyright       |    14.3 |        20.7 |  1.4 |    0.91 |          1 |     0.16 | False |
| hypercorn          | infer-ty                 |     5.3 |         5.9 |  1.1 |    0.65 |          1 |     0.16 | False |
| hypercorn          | infer-pyrefly            |     5.3 |        13.7 |  2.6 |    0.95 |          1 |     0.16 | False |
| hypercorn          | census                   |     1.0 |         1.2 |  1.2 |    0.18 |          2 |     0.22 | False |
| hypercorn          | coverage                 |     0.8 |         0.8 |  1.0 |    0.15 |          1 |     0.19 | False |
| hypercorn          | timing                   |     3.4 |         2.6 |  0.8 |    0.18 |          1 |     0.22 | False |
| hypercorn          | traced                   |    13.4 |         6.8 |  0.5 |    0.27 |          1 |     0.32 | False |
| hypercorn          | tests-released           |     9.2 |         1.6 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | infer-union              |    21.2 |        25.7 |  1.2 |    0.79 |          1 |     0.16 | False |
| hypercorn          | tests-infer-union        |     9.4 |         2.0 |  0.2 |     0.1 |          1 |     0.11 | False |
| hypercorn          | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          1 |      0.2 | False |
| hypercorn          | types-released           |     4.0 |         1.3 |  0.3 |    0.12 |          1 |     0.14 | False |
| hypercorn          | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-unsafe         |     0.7 |         0.2 |  0.3 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-infer-basedpyright |     2.2 |         1.1 |  0.5 |    0.12 |          1 |     0.14 | False |
| hypercorn          | types-infer-ty           |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.14 | False |
| hypercorn          | types-infer-pyrefly      |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-trace        |     0.9 |         0.2 |  0.2 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.24 | False |
| starlette          | fix-certain              |     1.8 |         3.5 |  1.9 |    0.27 |          3 |     0.34 | False |
| starlette          | fix-likely               |     1.6 |         3.3 |  2.1 |    0.27 |          3 |     0.34 | False |
| starlette          | fix-unsafe               |     5.0 |         5.4 |  1.1 |    0.27 |          2 |     0.34 | False |
| starlette          | infer-basedpyright       |    19.4 |        25.8 |  1.3 |    1.07 |          1 |      0.3 | False |
| starlette          | infer-ty                 |     5.6 |         7.1 |  1.3 |    0.65 |          1 |     0.16 | False |
| starlette          | infer-pyrefly            |     5.4 |        14.8 |  2.7 |    0.99 |          1 |     0.17 | False |
| starlette          | census                   |     1.0 |         1.5 |  1.5 |    0.19 |          2 |     0.24 | False |
| starlette          | coverage                 |     1.0 |         1.0 |  1.0 |    0.16 |          1 |     0.19 | False |
| starlette          | timing                   |     1.6 |         2.1 |  1.3 |    0.19 |          2 |     0.24 | False |
| starlette          | traced                   |    23.7 |        14.8 |  0.6 |    0.29 |          1 |     0.34 | False |
| starlette          | tests-released           |    19.9 |         7.6 |  0.4 |    0.22 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | infer-union              |    22.5 |        35.0 |  1.6 |    0.94 |          1 |     0.16 | False |
| starlette          | tests-infer-union        |    14.2 |         7.8 |  0.5 |    0.23 |          1 |     0.27 | False |
| starlette          | tests                    |     2.0 |         1.8 |  0.9 |    0.16 |          1 |      0.2 | False |
| starlette          | types-released           |     2.8 |         1.8 |  0.6 |    0.14 |          1 |     0.16 | False |
| starlette          | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.16 | False |
| starlette          | types-infer-basedpyright |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.14 | False |
| starlette          | types-infer-ty           |     1.8 |         1.3 |  0.7 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-pyrefly      |     2.8 |         1.7 |  0.6 |    0.14 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.16 | False |
| starlette          | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.0 |         1.6 |  1.6 |    0.21 |          2 |     0.26 | False |
| werkzeug           | fix-certain              |     2.2 |         5.2 |  2.4 |    0.31 |          3 |     0.39 | False |
| werkzeug           | fix-likely               |     2.0 |         4.8 |  2.4 |    0.31 |          3 |     0.39 | False |
| werkzeug           | fix-unsafe               |     6.6 |         8.6 |  1.3 |    0.35 |          2 |     0.39 | False |
| werkzeug           | infer-basedpyright       |    20.5 |        38.3 |  1.9 |    1.17 |          1 |     0.18 | False |
| werkzeug           | infer-ty                 |     7.9 |        12.2 |  1.5 |    0.76 |          1 |     0.19 | False |
| werkzeug           | infer-pyrefly            |     7.6 |        19.1 |  2.5 |    0.87 |          1 |     0.13 | False |
| werkzeug           | census                   |     0.4 |         0.3 |  0.7 |    0.04 |          2 |     0.26 | False |
| werkzeug           | coverage                 |     0.6 |         1.0 |  1.7 |    0.17 |          2 |     0.21 | False |
| werkzeug           | timing                   |     2.8 |         3.7 |  1.3 |    0.21 |          2 |     0.26 | False |
| werkzeug           | traced                   |    22.4 |        18.0 |  0.8 |    0.32 |          1 |     0.39 | False |
| werkzeug           | tests-released           |    11.0 |         7.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-basedpyright |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| werkzeug           | infer-union              |    25.8 |        48.8 |  1.9 |    1.13 |          1 |      0.2 | False |
| werkzeug           | tests-infer-union        |    10.6 |         7.8 |  0.7 |    0.17 |          1 |      0.2 | False |
| werkzeug           | tests                    |     2.2 |         2.0 |  0.9 |    0.16 |          1 |      0.2 | False |
| werkzeug           | types-released           |     3.2 |         1.3 |  0.4 |    0.11 |          1 |     0.12 | False |
| werkzeug           | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-unsafe         |     0.9 |         0.2 |  0.2 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-infer-basedpyright |     1.0 |         0.9 |  0.9 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-ty           |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-pyrefly      |     2.6 |         1.3 |  0.5 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     1.4 |         2.4 |  1.7 |    0.28 |          2 |     0.35 | False |
| mkdocs             | fix-certain              |     3.0 |         6.3 |  2.1 |    0.34 |          3 |     0.42 | False |
| mkdocs             | fix-likely               |     4.0 |         8.8 |  2.2 |    0.35 |          3 |     0.44 | False |
| mkdocs             | fix-unsafe               |     6.0 |         9.7 |  1.6 |    0.35 |          2 |     0.42 | False |
| mkdocs             | infer-basedpyright       |    27.1 |        46.4 |  1.7 |    1.43 |          1 |     0.21 | False |
| mkdocs             | infer-ty                 |     9.6 |        14.0 |  1.5 |    0.89 |          2 |     0.42 | False |
| mkdocs             | infer-pyrefly            |    11.2 |        21.9 |  2.0 |    1.28 |          1 |     0.21 | False |
| mkdocs             | census                   |     0.6 |         0.5 |  0.8 |    0.05 |          2 |     0.35 | False |
| mkdocs             | coverage                 |     0.8 |         1.3 |  1.6 |    0.19 |          2 |     0.24 | False |
| mkdocs             | timing                   |     3.2 |         4.2 |  1.3 |    0.28 |          2 |     0.35 | False |
| mkdocs             | traced                   |    19.2 |        14.1 |  0.7 |    0.36 |          1 |     0.45 | False |
| mkdocs             | tests-released           |    11.2 |         2.7 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    35.1 |        60.9 |  1.7 |    1.22 |          1 |     0.21 | False |
| mkdocs             | tests-infer-union        |    12.6 |         3.1 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     2.0 |         1.7 |  0.8 |    0.16 |          1 |      0.2 | False |
| httpx              | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.24 | False |
| httpx              | fix-certain              |     1.8 |         3.1 |  1.7 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-likely               |     2.0 |         3.8 |  1.9 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-unsafe               |     6.0 |         5.7 |  1.0 |    0.29 |          2 |     0.32 | False |
| httpx              | infer-basedpyright       |    16.0 |        17.9 |  1.1 |     0.7 |          1 |     0.15 | False |
| httpx              | infer-ty                 |     6.4 |         6.9 |  1.1 |    0.51 |          1 |     0.16 | False |
| httpx              | infer-pyrefly            |     6.6 |        10.8 |  1.6 |    0.69 |          1 |     0.17 | False |
| httpx              | census                   |     1.2 |         1.4 |  1.2 |    0.19 |          2 |     0.24 | False |
| httpx              | coverage                 |     0.9 |         0.9 |  1.0 |    0.15 |          1 |     0.19 | False |
| httpx              | timing                   |     1.8 |         2.0 |  1.1 |    0.19 |          2 |     0.24 | False |
| httpx              | traced                   |    13.2 |        11.0 |  0.8 |    0.29 |          1 |     0.34 | False |
| httpx              | tests-released           |    11.0 |         6.4 |  0.6 |    0.23 |          1 |     0.27 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-unsafe         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-ty           |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | infer-union              |    18.1 |        26.2 |  1.4 |    0.61 |          1 |     0.16 | False |
| httpx              | tests-infer-union        |     8.8 |         5.3 |  0.6 |    0.22 |          1 |     0.26 | False |
| httpx              | tests                    |     1.8 |         1.7 |  0.9 |    0.16 |          1 |      0.2 | False |
| httpx              | types-released           |    13.6 |         7.1 |  0.5 |    0.24 |          1 |     0.25 | False |
| httpx              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-infer-basedpyright |     7.2 |         6.3 |  0.9 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-ty           |     7.8 |         6.5 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-pyrefly      |     7.8 |         6.4 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-trace        |     8.8 |         6.7 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.25 | False |
| black              | fix-certain              |     2.2 |         4.7 |  2.1 |    0.31 |          3 |     0.39 | False |
| black              | fix-likely               |     2.2 |         5.2 |  2.4 |    0.31 |          3 |     0.39 | False |
| black              | fix-unsafe               |     3.0 |         6.0 |  2.0 |    0.31 |          2 |     0.41 | False |
| black              | infer-basedpyright       |    21.7 |        25.6 |  1.2 |    0.78 |          1 |     0.16 | False |
| black              | infer-ty                 |     5.2 |         8.8 |  1.7 |    0.53 |          1 |     0.19 | False |
| black              | infer-pyrefly            |     5.0 |        12.1 |  2.4 |    0.72 |          1 |     0.19 | False |
| black              | census                   |     1.4 |         2.1 |  1.5 |     0.2 |          2 |     0.25 | False |
| black              | coverage                 |     0.8 |         0.9 |  1.1 |    0.17 |          2 |     0.21 | False |
| black              | timing                   |     2.2 |         2.8 |  1.3 |     0.2 |          2 |     0.25 | False |
| black              | traced                   |     7.6 |        46.3 |  6.1 |    0.89 |          8 |      1.1 | False |
| black              | tests-released           |     6.2 |        37.8 |  6.1 |     0.8 |          8 |     0.94 | False |
| black              | tests-fix-certain        |     5.8 |        36.2 |  6.2 |    0.74 |          8 |     0.96 | False |
| black              | tests-fix-likely         |     7.2 |        47.6 |  6.6 |    0.76 |          8 |     0.96 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.96 | False |
| black              | tests-infer-basedpyright |     7.2 |        47.9 |  6.7 |    0.78 |          8 |     0.97 | False |
| black              | tests-infer-ty           |     7.0 |        47.9 |  6.8 |    0.76 |          8 |     0.97 | False |
| black              | tests-infer-pyrefly      |     5.4 |        35.4 |  6.6 |    0.75 |          8 |     0.95 | False |
| black              | tests-infer-trace        |     5.0 |        35.0 |  7.0 |    0.75 |          8 |     0.96 | False |
| black              | infer-union              |    23.4 |        32.3 |  1.4 |    0.67 |          1 |     0.17 | False |
| black              | tests-infer-union        |     6.6 |        43.1 |  6.5 |    0.75 |          8 |     0.95 | False |
| black              | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          2 |      0.2 | False |
| fastapi            | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      0.3 | False |
| fastapi            | fix-certain              |     3.4 |         5.1 |  1.5 |    0.32 |          2 |      0.4 | False |
| fastapi            | fix-likely               |     5.6 |         8.2 |  1.5 |    0.51 |          2 |     0.54 | False |
| fastapi            | fix-unsafe               |     6.3 |         7.9 |  1.3 |    0.35 |          2 |     0.44 | False |
| fastapi            | infer-basedpyright       |    34.6 |        41.2 |  1.2 |    1.37 |          1 |     0.44 | False |
| fastapi            | infer-ty                 |    18.0 |        13.7 |  0.8 |    0.89 |          1 |     0.22 | False |
| fastapi            | infer-pyrefly            |    11.8 |        20.8 |  1.8 |    1.21 |          1 |     0.22 | False |
| fastapi            | census                   |     1.4 |         1.7 |  1.2 |    0.24 |          2 |      0.3 | False |
| fastapi            | coverage                 |     0.6 |         0.8 |  1.3 |    0.17 |          2 |     0.21 | False |
| fastapi            | timing                   |     3.0 |         3.4 |  1.1 |    0.24 |          2 |      0.3 | False |
| fastapi            | traced                   |    29.0 |       137.0 |  4.7 |    2.37 |          7 |     2.89 | False |
| fastapi            | tests-released           |    14.8 |        92.6 |  6.3 |    2.11 |          8 |     2.62 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | infer-union              |    22.6 |        40.5 |  1.8 |    0.89 |          2 |     0.44 | False |
| fastapi            | tests-infer-union        |    15.2 |        89.9 |  5.9 |    2.11 |          8 |     2.55 | False |
| fastapi            | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          2 |      0.2 | False |
| cattrs             | check                    |     1.8 |         1.6 |  0.9 |     0.2 |          1 |     0.25 | False |
| cattrs             | fix-certain              |     2.0 |         3.5 |  1.8 |    0.26 |          2 |     0.32 | False |
| cattrs             | fix-likely               |     2.2 |         3.9 |  1.8 |    0.26 |          2 |     0.32 | False |
| cattrs             | fix-unsafe               |     4.4 |         4.8 |  1.1 |    0.26 |          2 |     0.32 | False |
| cattrs             | infer-basedpyright       |    15.6 |        24.6 |  1.6 |    0.98 |          2 |      1.0 | False |
| cattrs             | infer-ty                 |     6.2 |         6.7 |  1.1 |    0.65 |          1 |     0.38 | False |
| cattrs             | infer-pyrefly            |     7.6 |        15.8 |  2.1 |    0.96 |          1 |     0.58 | False |
| cattrs             | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.25 | False |
| cattrs             | coverage                 |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.19 | False |
| cattrs             | timing                   |     1.8 |         1.9 |  1.1 |     0.2 |          2 |     0.25 | False |
| cattrs             | traced                   |    24.8 |       149.9 |  6.0 |    1.33 |          8 |     1.66 | False |
| cattrs             | tests-released           |    20.8 |       126.5 |  6.1 |    1.01 |          8 |     1.26 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.24 | False |
| cattrs             | infer-union              |    11.5 |        26.9 |  2.3 |    0.79 |          3 |     0.99 | False |
| cattrs             | tests-infer-union        |    16.6 |       113.2 |  6.8 |     1.0 |          8 |     1.25 | False |
| cattrs             | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          2 |      0.2 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.37 | False |
| pytest             | fix-certain              |     5.4 |        10.9 |  2.0 |     0.4 |          3 |      0.5 | False |
| pytest             | fix-likely               |     6.0 |        13.0 |  2.2 |    0.45 |          3 |     0.56 | False |
| pytest             | fix-unsafe               |    10.2 |        15.5 |  1.5 |     0.4 |          2 |      0.5 | False |
| pytest             | infer-basedpyright       |    42.4 |        72.2 |  1.7 |    2.12 |          1 |     0.26 | False |
| pytest             | infer-ty                 |    18.6 |        22.5 |  1.2 |    1.24 |          1 |     0.26 | False |
| pytest             | infer-pyrefly            |    18.6 |        33.4 |  1.8 |    1.74 |          1 |     0.27 | False |
| pytest             | census                   |     2.6 |         4.2 |  1.6 |     0.3 |          2 |     0.37 | False |
| pytest             | coverage                 |     1.0 |         1.7 |  1.7 |    0.22 |          2 |     0.27 | False |
| pytest             | timing                   |     4.6 |         5.9 |  1.3 |     0.3 |          2 |     0.37 | False |
| pytest             | traced                   |    66.8 |       337.5 |  5.1 |    1.82 |          8 |      2.2 | False |
| pytest             | tests-released           |    22.6 |       160.2 |  7.1 |    1.41 |          8 |     1.71 | False |
| pytest             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | infer-union              |    29.5 |        79.9 |  2.7 |    1.84 |          3 |     2.32 | False |
| pytest             | tests-infer-union        |    20.4 |       142.6 |  7.0 |    1.35 |          8 |     1.67 | False |
| pytest             | tests                    |     1.4 |         1.1 |  0.8 |    0.16 |          1 |      0.2 | False |
| botocore           | check                    |     2.0 |         3.9 |  1.9 |    0.34 |          3 |     0.41 | False |
| botocore           | fix-certain              |     5.0 |        12.1 |  2.4 |    0.43 |          3 |     0.52 | False |
| botocore           | fix-likely               |     6.6 |        15.4 |  2.3 |    0.52 |          3 |     0.65 | False |
| botocore           | fix-unsafe               |    12.2 |        17.2 |  1.4 |     0.5 |          2 |     0.61 | False |
| botocore           | infer-basedpyright       |    44.0 |        77.4 |  1.8 |     2.3 |          1 |     0.34 | False |
| botocore           | infer-ty                 |    18.4 |        26.2 |  1.4 |    0.89 |          1 |     0.32 | False |
| botocore           | infer-pyrefly            |    20.6 |        25.9 |  1.3 |    1.36 |          1 |     0.22 | False |
| botocore           | census                   |     0.8 |         0.6 |  0.7 |    0.05 |          3 |     0.41 | False |
| botocore           | coverage                 |     1.0 |         1.5 |  1.5 |    0.21 |          2 |     0.26 | False |
| botocore           | timing                   |     6.4 |         9.0 |  1.4 |    0.34 |          2 |     0.41 | False |
| botocore           | traced                   |    39.7 |       124.4 |  3.1 |    5.17 |          4 |      6.3 | False |
| botocore           | tests-released           |    29.7 |        93.5 |  3.1 |    4.92 |          4 |     6.15 | False |
| botocore           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     6.01 | False |
| botocore           | infer-union              |    40.7 |        96.1 |  2.4 |    1.77 |          1 |     0.77 | False |
| botocore           | tests-infer-union        |    28.0 |        92.5 |  3.3 |    4.98 |          4 |     6.01 | False |
| botocore           | tests                    |     1.6 |         1.4 |  0.9 |    0.17 |          2 |      0.2 | False |
| uvicorn            | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.24 | False |
| uvicorn            | fix-certain              |     2.4 |         4.0 |  1.7 |    0.27 |          2 |     0.34 | False |
| uvicorn            | fix-likely               |     2.2 |         4.5 |  2.0 |    0.27 |          2 |     0.34 | False |
| uvicorn            | fix-unsafe               |     5.0 |         5.3 |  1.1 |    0.31 |          2 |     0.34 | False |
| uvicorn            | infer-basedpyright       |    17.0 |        27.8 |  1.6 |    1.06 |          1 |     0.15 | False |
| uvicorn            | infer-ty                 |    11.4 |         8.3 |  0.7 |    0.68 |          1 |     0.17 | False |
| uvicorn            | infer-pyrefly            |    11.9 |        16.8 |  1.4 |    1.01 |          1 |     0.17 | False |
| uvicorn            | census                   |     1.0 |         1.4 |  1.4 |    0.19 |          2 |     0.24 | False |
| uvicorn            | coverage                 |     0.8 |         0.9 |  1.1 |    0.16 |          1 |      0.2 | False |
| uvicorn            | timing                   |     2.0 |         2.4 |  1.2 |    0.19 |          2 |     0.24 | False |
| uvicorn            | traced                   |    35.6 |        32.4 |  0.9 |    0.94 |          1 |     1.16 | False |
| uvicorn            | tests-released           |    30.9 |        21.3 |  0.7 |    0.83 |          1 |     1.05 | False |
| uvicorn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-infer-trace        |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     1.01 | False |
| uvicorn            | infer-union              |    19.0 |        29.2 |  1.5 |     0.8 |          1 |     0.15 | False |
| uvicorn            | tests-infer-union        |    43.6 |        23.0 |  0.5 |    0.83 |          1 |     1.01 | False |
| uvicorn            | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |      0.2 | False |
| uvicorn            | types-released           |     2.2 |         1.6 |  0.7 |    0.13 |          1 |     0.15 | False |
| uvicorn            | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-infer-basedpyright |     2.0 |         1.5 |  0.8 |    0.13 |          1 |     0.15 | False |
| uvicorn            | types-infer-ty           |     3.0 |         1.8 |  0.6 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-pyrefly      |     1.6 |         0.9 |  0.6 |    0.11 |          1 |     0.14 | False |
| uvicorn            | types-infer-trace        |     1.6 |         1.4 |  0.9 |    0.13 |          1 |     0.15 | False |
| uvicorn            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     1.8 |         3.1 |  1.7 |    0.28 |          2 |     0.34 | False |
| mcp                | fix-certain              |     3.8 |         8.7 |  2.3 |    0.34 |          3 |     0.42 | False |
| mcp                | fix-likely               |     3.8 |         9.3 |  2.4 |    0.44 |          3 |     0.54 | False |
| mcp                | fix-unsafe               |    12.5 |        13.1 |  1.0 |    0.38 |          2 |     0.47 | False |
| mcp                | infer-basedpyright       |    38.1 |        77.7 |  2.0 |    2.36 |          2 |     0.54 | False |
| mcp                | infer-ty                 |    10.6 |        18.3 |  1.7 |    1.37 |          1 |     0.18 | False |
| mcp                | infer-pyrefly            |    18.0 |        37.1 |  2.1 |    2.17 |          1 |     0.27 | False |
| mcp                | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.34 | False |
| mcp                | coverage                 |     0.8 |         1.4 |  1.7 |    0.19 |          2 |     0.24 | False |
| mcp                | timing                   |     4.4 |         5.9 |  1.3 |    0.28 |          2 |     0.34 | False |
| mcp                | traced                   |    30.4 |       110.8 |  3.6 |    2.08 |          6 |     2.49 | False |
| mcp                | tests-released           |    13.0 |        62.3 |  4.8 |    1.84 |          6 |     2.24 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | infer-union              |    22.4 |        86.1 |  3.8 |    1.74 |          1 |     0.27 | False |
| mcp                | tests-infer-union        |    22.9 |        63.4 |  2.8 |    1.79 |          7 |     2.24 | False |
| mcp                | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |      0.2 | False |
| mcp                | types-released           |    43.0 |        33.6 |  0.8 |    1.24 |          2 |     1.59 | False |
| mcp                | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.61 | False |
| mcp                | types-fix-likely         |    17.8 |        26.1 |  1.5 |    1.27 |          1 |     1.52 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      1.6 | False |
| mcp                | types-infer-basedpyright |    15.6 |        24.3 |  1.6 |    1.28 |          2 |     1.57 | False |
| mcp                | types-infer-ty           |    15.6 |        24.3 |  1.6 |    1.25 |          2 |     1.55 | False |
| mcp                | types-infer-pyrefly      |    14.8 |        23.2 |  1.6 |    1.26 |          2 |      1.6 | False |
| mcp                | types-infer-trace        |    21.4 |        29.4 |  1.4 |     1.3 |          2 |     1.59 | False |
| mcp                | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          2 |     0.52 | False |
| textual            | fix-certain              |     5.0 |        14.3 |  2.9 |    0.53 |          3 |     0.67 | False |
| textual            | fix-likely               |     7.4 |        20.9 |  2.8 |    0.56 |          3 |      0.7 | False |
| textual            | fix-unsafe               |     7.4 |        20.8 |  2.8 |    0.54 |          3 |     0.66 | False |
| textual            | infer-basedpyright       |    52.8 |       117.0 |  2.2 |    2.24 |          1 |     0.22 | False |
| textual            | infer-ty                 |    24.6 |        45.6 |  1.9 |    1.94 |          1 |     0.36 | False |
| textual            | infer-pyrefly            |    22.8 |        53.5 |  2.3 |    2.47 |          1 |     0.24 | False |
| textual            | census                   |     3.6 |         7.3 |  2.0 |    0.42 |          2 |     0.52 | False |
| textual            | coverage                 |     1.6 |         3.0 |  1.9 |    0.24 |          3 |      0.3 | False |
| textual            | timing                   |     7.6 |        11.3 |  1.5 |    0.42 |          2 |     0.52 | False |
| pdm                | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.59 | False |
| pdm                | fix-certain              |     6.0 |        11.6 |  1.9 |    0.51 |          3 |     0.64 | False |
| pdm                | fix-likely               |     7.0 |        15.0 |  2.1 |    0.57 |          3 |     0.71 | False |
| pdm                | fix-unsafe               |    11.0 |        17.7 |  1.6 |    0.55 |          3 |     0.69 | False |
| pdm                | infer-basedpyright       |    43.2 |        92.2 |  2.1 |    2.47 |          1 |     0.32 | False |
| pdm                | infer-ty                 |    21.8 |        29.7 |  1.4 |    1.66 |          1 |     0.35 | False |
| pdm                | infer-pyrefly            |    17.4 |        41.5 |  2.4 |    2.24 |          1 |     0.35 | False |
| pdm                | census                   |     3.0 |         4.8 |  1.6 |    0.48 |          2 |     0.59 | False |
| pdm                | coverage                 |     0.8 |         1.3 |  1.6 |     0.2 |          2 |     0.25 | False |
| pdm                | timing                   |     6.6 |         8.7 |  1.3 |    0.48 |          2 |     0.59 | False |
| pdm                | traced                   |    32.6 |       140.0 |  4.3 |    1.53 |          7 |     1.69 | False |
| pdm                | tests-released           |    20.4 |       101.5 |  5.0 |    1.22 |          8 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.51 | False |
| pdm                | infer-union              |    23.8 |        97.2 |  4.1 |    2.31 |          2 |     0.65 | False |
| pdm                | tests-infer-union        |    17.0 |       103.2 |  6.1 |    1.24 |          8 |      1.5 | False |
| pdm                | tests                    |     1.6 |         1.5 |  0.9 |    0.16 |          2 |      0.2 | False |
| strawberry-graphql | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.45 | False |
| strawberry-graphql | fix-certain              |     5.4 |        12.1 |  2.2 |    0.51 |          3 |     0.57 | False |
| strawberry-graphql | fix-likely               |     7.6 |        16.7 |  2.2 |    0.67 |          3 |     0.74 | False |
| strawberry-graphql | fix-unsafe               |    10.0 |        17.6 |  1.8 |    0.54 |          3 |     0.62 | False |
| strawberry-graphql | infer-basedpyright       |    48.5 |       117.1 |  2.4 |    3.02 |          1 |     0.32 | False |
| strawberry-graphql | infer-ty                 |    20.4 |        28.2 |  1.4 |     1.6 |          1 |     0.31 | False |
| strawberry-graphql | infer-pyrefly            |    21.2 |        47.4 |  2.2 |    2.47 |          1 |     0.31 | False |
| strawberry-graphql | census                   |     3.2 |         5.0 |  1.6 |    0.38 |          2 |     0.45 | False |
| strawberry-graphql | coverage                 |     0.8 |         1.5 |  1.9 |    0.19 |          2 |     0.24 | False |
| strawberry-graphql | timing                   |     4.8 |         7.2 |  1.5 |    0.39 |          2 |     0.45 | False |
| strawberry-graphql | traced                   |    25.6 |       119.0 |  4.6 |    1.51 |          5 |     1.85 | False |
| strawberry-graphql | tests-released           |    14.8 |        80.5 |  5.4 |    1.28 |          8 |     1.55 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.55 | False |
| strawberry-graphql | tests-infer-trace        |     0.3 |         0.2 |  0.7 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | infer-union              |    31.6 |       108.8 |  3.4 |    2.39 |          3 |     0.65 | False |
| strawberry-graphql | tests-infer-union        |    14.0 |        89.2 |  6.4 |    1.25 |          7 |     1.55 | False |
| strawberry-graphql | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          2 |      0.2 | False |
| strawberry-graphql | types-released           |     3.0 |         2.0 |  0.7 |    0.24 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-basedpyright |     2.8 |         1.9 |  0.7 |    0.19 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-ty           |     2.0 |         1.7 |  0.8 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-pyrefly      |     3.0 |         2.1 |  0.7 |    0.22 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| strawberry-graphql | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          2 |     0.52 | False |
| pygments           | fix-certain              |     6.8 |        19.6 |  2.9 |    0.54 |          3 |     0.62 | False |
| pygments           | fix-likely               |     7.4 |        21.0 |  2.8 |    0.63 |          3 |     0.79 | False |
| pygments           | fix-unsafe               |    14.4 |        29.1 |  2.0 |    0.62 |          3 |     0.77 | False |
| pygments           | infer-basedpyright       |    89.5 |       136.3 |  1.5 |    2.17 |          1 |     0.25 | False |
| pygments           | infer-ty                 |    23.6 |        40.5 |  1.7 |    1.18 |          1 |     0.39 | False |
| pygments           | infer-pyrefly            |    33.6 |        47.3 |  1.4 |     1.6 |          1 |     0.39 | False |
| pygments           | census                   |     4.4 |         8.7 |  2.0 |    0.42 |          2 |     0.52 | False |
| pygments           | coverage                 |     1.4 |         3.5 |  2.5 |    0.22 |          3 |     0.26 | False |
| pygments           | timing                   |     8.4 |        13.0 |  1.5 |    0.42 |          2 |     0.52 | False |
| pygments           | traced                   |    44.6 |        53.2 |  1.2 |    0.73 |          1 |     0.82 | False |
| pygments           | tests-released           |    21.8 |        15.8 |  0.7 |     0.3 |          1 |     0.35 | False |
| pygments           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| pygments           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| pygments           | infer-union              |   104.3 |       160.9 |  1.5 |    1.76 |          1 |     0.72 | False |
| pygments           | tests-infer-union        |    26.0 |        17.4 |  0.7 |     0.3 |          1 |     0.31 | False |
| pygments           | tests                    |     2.2 |         2.0 |  0.9 |    0.16 |          1 |      0.2 | False |
| streamlink         | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          3 |     0.42 | False |
| streamlink         | fix-certain              |     4.6 |        12.2 |  2.7 |    0.43 |          3 |     0.54 | False |
| streamlink         | fix-likely               |     6.4 |        17.1 |  2.7 |    0.51 |          3 |     0.62 | False |
| streamlink         | fix-unsafe               |    11.5 |        19.9 |  1.7 |    0.45 |          3 |     0.56 | False |
| streamlink         | infer-basedpyright       |    37.0 |       106.4 |  2.9 |    2.58 |          1 |     0.33 | False |
| streamlink         | infer-ty                 |    23.6 |        37.0 |  1.6 |    1.54 |          1 |     0.21 | False |
| streamlink         | infer-pyrefly            |    20.0 |        43.8 |  2.2 |    2.15 |          1 |     0.21 | False |
| streamlink         | census                   |     3.0 |         6.0 |  2.0 |    0.34 |          3 |     0.42 | False |
| streamlink         | coverage                 |     1.2 |         2.1 |  1.8 |    0.23 |          2 |     0.29 | False |
| streamlink         | timing                   |     6.8 |         9.8 |  1.4 |    0.34 |          2 |     0.42 | False |
| streamlink         | traced                   |    32.1 |        36.1 |  1.1 |    0.55 |          1 |     0.64 | False |
| streamlink         | tests-released           |    22.3 |        14.0 |  0.6 |    0.18 |          1 |     0.25 | False |
| streamlink         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.7 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.22 | False |
| streamlink         | infer-union              |    55.8 |       127.1 |  2.3 |    1.86 |          1 |     0.24 | False |
| streamlink         | tests-infer-union        |    22.8 |        14.3 |  0.6 |     0.2 |          1 |     0.22 | False |
| streamlink         | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          1 |      0.2 | False |
| streamlink         | types-released           |    15.2 |         8.8 |  0.6 |     0.4 |          1 |     0.44 | False |
| streamlink         | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.49 | False |
| streamlink         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.47 | False |
| streamlink         | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.45 | False |
| streamlink         | types-infer-basedpyright |     8.2 |         7.0 |  0.9 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-ty           |     8.4 |         7.0 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |     8.2 |         7.0 |  0.9 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |     8.4 |         7.0 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     3.2 |         8.9 |  2.8 |    0.46 |          3 |     0.56 | False |
| sphinx             | fix-certain              |     8.0 |        24.5 |  3.1 |    0.63 |          4 |     0.75 | False |
| sphinx             | fix-likely               |    10.6 |        33.5 |  3.2 |    0.81 |          4 |     1.01 | False |
| sphinx             | fix-unsafe               |    16.9 |        39.8 |  2.4 |    0.71 |          3 |     0.89 | False |
| sphinx             | infer-basedpyright       |    55.6 |       170.0 |  3.1 |    3.66 |          2 |      2.0 | False |
| sphinx             | infer-ty                 |    34.4 |        60.2 |  1.8 |    2.25 |          2 |     1.42 | False |
| sphinx             | infer-pyrefly            |    37.0 |        57.0 |  1.5 |    2.71 |          1 |     0.94 | False |
| sphinx             | census                   |     3.4 |         1.6 |  0.5 |    0.08 |          3 |     0.56 | False |
| sphinx             | coverage                 |     1.6 |         4.2 |  2.6 |    0.27 |          3 |     0.34 | False |
| sphinx             | timing                   |    10.8 |        17.0 |  1.6 |    0.46 |          2 |     0.56 | False |
| sphinx             | traced                   |    35.6 |       196.0 |  5.5 |    1.71 |          7 |     2.05 | False |
| sphinx             | tests-released           |    16.4 |       115.4 |  7.0 |    1.35 |          8 |     1.69 | False |
| sphinx             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.66 | False |
| sphinx             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.66 | False |
| sphinx             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.65 | False |
| sphinx             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.65 | False |
| sphinx             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.66 | False |
| sphinx             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.65 | False |
| sphinx             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.66 | False |
| sphinx             | infer-union              |    64.4 |       147.8 |  2.3 |    2.13 |          1 |     0.88 | False |
| sphinx             | tests-infer-union        |    15.0 |       108.7 |  7.2 |    1.35 |          8 |     1.65 | False |
| sphinx             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |      0.2 | False |
| sphinx             | types-released           |    11.4 |         7.5 |  0.7 |    0.33 |          1 |     0.32 | False |
| sphinx             | types-fix-certain        |    11.8 |         7.2 |  0.6 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-likely         |     3.8 |         3.7 |  1.0 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.34 | False |
| sphinx             | types-infer-basedpyright |    11.8 |         7.3 |  0.6 |    0.26 |          1 |     0.35 | False |
| sphinx             | types-infer-ty           |     7.6 |         6.2 |  0.8 |    0.26 |          1 |     0.32 | False |
| sphinx             | types-infer-pyrefly      |     8.2 |         6.8 |  0.8 |    0.29 |          1 |     0.32 | False |
| sphinx             | types-infer-trace        |     8.6 |         6.9 |  0.8 |    0.27 |          1 |     0.34 | False |
| sphinx             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     1.4 |         2.7 |  1.9 |    0.25 |          3 |     0.31 | False |
| tox                | fix-certain              |     3.4 |         7.9 |  2.3 |    0.33 |          3 |     0.41 | False |
| tox                | fix-likely               |     4.0 |         9.3 |  2.3 |     0.4 |          3 |     0.49 | False |
| tox                | fix-unsafe               |     5.9 |        10.9 |  1.8 |    0.35 |          2 |     0.44 | False |
| tox                | infer-basedpyright       |    24.8 |        69.0 |  2.8 |    2.14 |          1 |     0.25 | False |
| tox                | infer-ty                 |    13.8 |        22.0 |  1.6 |    1.37 |          1 |     0.22 | False |
| tox                | infer-pyrefly            |    12.0 |        18.3 |  1.5 |    1.59 |          1 |     0.25 | False |
| tox                | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          3 |     0.31 | False |
| tox                | coverage                 |     0.8 |         1.3 |  1.6 |    0.18 |          2 |     0.22 | False |
| tox                | timing                   |     3.6 |         5.0 |  1.4 |    0.25 |          2 |     0.31 | False |
| tox                | traced                   |    35.5 |       166.0 |  4.7 |    1.61 |          6 |     1.84 | False |
| tox                | tests-released           |    17.8 |       104.5 |  5.9 |    1.36 |          8 |     1.67 | False |
| tox                | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          6 |     1.66 | False |
| tox                | infer-union              |    18.2 |        67.0 |  3.7 |    1.92 |          3 |      0.5 | False |
| tox                | tests-infer-union        |    23.9 |       127.0 |  5.3 |    1.34 |          6 |     1.64 | False |
| tox                | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |      0.2 | False |
| pint               | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.51 | False |
| pint               | fix-certain              |     5.8 |        11.9 |  2.1 |    0.46 |          3 |     0.57 | False |
| pint               | fix-likely               |     8.2 |        16.7 |  2.0 |    0.52 |          2 |     0.65 | False |
| pint               | fix-unsafe               |    29.6 |        22.6 |  0.8 |    0.57 |          2 |     0.65 | False |
| pint               | infer-basedpyright       |    87.6 |       156.7 |  1.8 |    2.96 |          1 |     0.33 | False |
| pint               | infer-ty                 |    33.2 |        36.5 |  1.1 |    2.64 |          2 |     0.66 | False |
| pint               | infer-pyrefly            |    21.7 |        40.6 |  1.9 |    2.14 |          1 |     0.32 | False |
| pint               | census                   |     3.6 |         5.7 |  1.6 |    0.41 |          2 |     0.51 | False |
| pint               | coverage                 |     1.0 |         1.7 |  1.7 |    0.22 |          2 |     0.27 | False |
| pint               | timing                   |     5.8 |         7.7 |  1.3 |    0.42 |          2 |     0.51 | False |
| pint               | traced                   |    46.3 |        49.3 |  1.1 |    0.54 |          1 |     0.65 | False |
| pint               | tests-released           |    64.4 |        32.8 |  0.5 |    0.15 |          1 |     0.19 | False |
| pint               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | infer-union              |    88.1 |       156.1 |  1.8 |    2.09 |          1 |     0.33 | False |
| pint               | tests-infer-union        |    49.0 |        33.8 |  0.7 |    0.15 |          1 |     0.17 | False |
| pint               | tests                    |     1.6 |         1.4 |  0.9 |    0.16 |          1 |      0.2 | False |
| pint               | types-released           |     5.4 |         9.1 |  1.7 |    0.54 |          2 |     0.66 | False |
| pint               | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-unsafe         |     6.0 |        10.2 |  1.7 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-basedpyright |     6.4 |         9.8 |  1.5 |    0.54 |          2 |     0.69 | False |
| pint               | types-infer-ty           |     5.8 |         9.5 |  1.6 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-pyrefly      |     5.6 |         9.4 |  1.7 |    0.53 |          2 |     0.67 | False |
| pint               | types-infer-trace        |     6.2 |        10.1 |  1.6 |    0.55 |          2 |     0.67 | False |
| pint               | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | check                    |     3.8 |         0.2 |  0.1 |    0.03 |          2 |     0.94 | False |
| altair             | fix-certain              |    15.4 |        22.8 |  1.5 |    0.94 |          2 |     1.09 | False |
| altair             | fix-likely               |    18.0 |        25.9 |  1.4 |    1.03 |          2 |      1.2 | False |
| altair             | fix-unsafe               |    18.4 |        26.9 |  1.5 |    1.03 |          2 |      1.2 | False |
| altair             | infer-basedpyright       |    68.5 |       105.7 |  1.5 |    2.87 |          1 |     0.57 | False |
| altair             | infer-ty                 |    29.9 |        37.3 |  1.2 |    1.68 |          1 |     0.55 | False |
| altair             | infer-pyrefly            |    43.8 |        46.5 |  1.1 |    1.75 |          1 |     0.61 | False |
| altair             | census                   |     7.4 |         9.3 |  1.3 |    0.82 |          2 |     0.94 | False |
| altair             | coverage                 |     1.2 |         2.2 |  1.8 |    0.28 |          2 |     0.35 | False |
| altair             | timing                   |    12.0 |        14.1 |  1.2 |    0.83 |          2 |     0.94 | False |
| altair             | traced                   |    64.2 |       212.6 |  3.3 |    6.17 |          6 |     6.11 | False |
| altair             | tests-released           |    22.2 |       154.7 |  7.0 |    4.68 |          8 |     6.22 | False |
| altair             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     5.71 | False |
| altair             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.56 | False |
| altair             | tests-fix-unsafe         |     0.3 |         0.2 |  0.7 |    0.03 |          6 |     5.89 | False |
| altair             | tests-infer-basedpyright |    29.8 |       155.7 |  5.2 |    4.59 |          7 |     6.04 | False |
| altair             | tests-infer-ty           |    22.6 |       141.3 |  6.3 |    4.59 |          8 |     5.85 | False |
| altair             | tests-infer-pyrefly      |    19.8 |       130.1 |  6.6 |    4.41 |          8 |     5.84 | False |
| altair             | tests-infer-trace        |    23.6 |       150.3 |  6.4 |    4.62 |          8 |     5.95 | False |
| altair             | infer-union              |    41.7 |        87.5 |  2.1 |    2.24 |          2 |     1.27 | False |
| altair             | tests-infer-union        |    22.8 |       144.4 |  6.3 |    5.65 |          8 |     5.66 | False |
| altair             | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          2 |      0.2 | False |
| altair             | types-released           |    12.4 |         7.7 |  0.6 |    0.42 |          1 |     0.47 | False |
| altair             | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.47 | False |
| altair             | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.49 | False |
| altair             | types-fix-unsafe         |     4.2 |         3.9 |  0.9 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-basedpyright |     9.6 |         6.6 |  0.7 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-ty           |     7.1 |         6.0 |  0.8 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-pyrefly      |     8.8 |         6.6 |  0.7 |    0.41 |          1 |      0.5 | False |
| altair             | types-infer-trace        |     7.5 |         5.6 |  0.7 |    0.38 |          1 |     0.47 | False |
| altair             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | check                    |     4.2 |         6.9 |  1.6 |    0.76 |          2 |     0.86 | False |
| seaborn            | fix-certain              |    15.0 |        23.0 |  1.5 |    0.92 |          2 |     1.01 | False |
| seaborn            | fix-likely               |    17.9 |        31.3 |  1.7 |    1.03 |          2 |     1.15 | False |
| seaborn            | fix-unsafe               |    39.9 |        30.9 |  0.8 |    0.96 |          2 |     1.06 | False |
| seaborn            | infer-basedpyright       |   112.5 |       131.6 |  1.2 |    3.52 |          2 |     1.12 | False |
| seaborn            | infer-ty                 |    20.8 |        35.4 |  1.7 |    1.66 |          1 |     0.51 | False |
| seaborn            | infer-pyrefly            |    36.0 |        47.7 |  1.3 |     2.2 |          1 |     0.59 | False |
| seaborn            | census                   |     3.4 |         0.6 |  0.2 |    0.05 |          2 |     0.86 | False |
| seaborn            | coverage                 |     0.8 |         1.5 |  1.9 |     0.2 |          2 |     0.25 | False |
| seaborn            | timing                   |    10.6 |        13.9 |  1.3 |    0.76 |          2 |     0.85 | False |
| seaborn            | traced                   |    75.8 |       439.3 |  5.8 |    3.67 |          8 |     4.51 | False |
| seaborn            | tests-released           |    35.6 |       396.8 | 11.1 |    3.47 |          8 |     4.34 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.26 | False |
| seaborn            | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | infer-union              |    66.5 |       114.2 |  1.7 |    2.59 |          3 |     3.14 | False |
| seaborn            | tests-infer-union        |    37.4 |       378.7 | 10.1 |    3.42 |          8 |     4.26 | False |
| seaborn            | tests                    |     1.8 |         1.4 |  0.8 |    0.16 |          2 |      0.2 | False |
| seaborn            | types-released           |     1.4 |         1.1 |  0.8 |    0.17 |          1 |     0.19 | False |
| seaborn            | types-fix-certain        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.19 | False |
| seaborn            | types-fix-likely         |     1.4 |         1.1 |  0.8 |    0.16 |          1 |      0.2 | False |
| seaborn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| seaborn            | types-infer-basedpyright |     1.6 |         1.0 |  0.6 |    0.17 |          1 |     0.19 | False |
| seaborn            | types-infer-ty           |     1.6 |         1.2 |  0.7 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-pyrefly      |     1.2 |         1.0 |  0.8 |    0.15 |          1 |      0.2 | False |
| seaborn            | types-infer-trace        |     1.6 |         1.1 |  0.7 |    0.15 |          1 |     0.19 | False |
| seaborn            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.31 | False |
| aiohttp            | fix-certain              |     4.0 |         8.8 |  2.2 |    0.35 |          2 |     0.44 | False |
| aiohttp            | fix-likely               |     5.0 |        11.7 |  2.3 |    0.43 |          3 |     0.54 | False |
| aiohttp            | fix-unsafe               |     5.0 |        11.2 |  2.2 |    0.36 |          2 |     0.45 | False |
| aiohttp            | infer-basedpyright       |    43.1 |        71.0 |  1.6 |    1.81 |          2 |     0.52 | False |
| aiohttp            | infer-ty                 |    18.0 |        22.0 |  1.2 |    0.83 |          2 |     0.52 | False |
| aiohttp            | infer-pyrefly            |     7.4 |        16.1 |  2.2 |    1.07 |          1 |     0.26 | False |
| aiohttp            | census                   |     2.0 |         3.3 |  1.6 |    0.26 |          2 |     0.31 | False |
| aiohttp            | coverage                 |     0.8 |         1.4 |  1.7 |     0.2 |          2 |     0.24 | False |
| aiohttp            | timing                   |     4.2 |         5.7 |  1.4 |    0.25 |          2 |     0.31 | False |
| aiohttp            | traced                   |   110.2 |       773.2 |  7.0 |     3.0 |          1 |     3.69 | False |
| aiohttp            | tests-released           |    98.4 |       643.0 |  6.5 |    2.58 |          1 |     3.24 | False |
| aiohttp            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-trace        |     0.9 |         0.2 |  0.2 |    0.03 |          1 |      3.2 | False |
| aiohttp            | infer-union              |    61.9 |        75.9 |  1.2 |     1.2 |          1 |     0.26 | False |
| aiohttp            | tests-infer-union        |    99.1 |       652.5 |  6.6 |    2.58 |          1 |      3.2 | False |
| aiohttp            | tests                    |     2.0 |         1.9 |  0.9 |    0.16 |          1 |      0.2 | False |
| websockets         | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.26 | False |
| websockets         | fix-certain              |     1.8 |         4.2 |  2.3 |     0.3 |          3 |     0.36 | False |
| websockets         | fix-likely               |     2.4 |         5.4 |  2.3 |     0.3 |          3 |     0.37 | False |
| websockets         | fix-unsafe               |     8.0 |         7.3 |  0.9 |    0.29 |          2 |     0.36 | False |
| websockets         | infer-basedpyright       |    20.4 |        31.8 |  1.6 |    1.05 |          1 |     0.11 | False |
| websockets         | infer-ty                 |     8.4 |        10.6 |  1.3 |    0.74 |          1 |     0.19 | False |
| websockets         | infer-pyrefly            |    10.0 |        11.2 |  1.1 |    0.81 |          1 |     0.19 | False |
| websockets         | census                   |     1.2 |         1.9 |  1.6 |    0.21 |          2 |     0.26 | False |
| websockets         | coverage                 |     0.6 |         0.9 |  1.5 |    0.17 |          2 |     0.21 | False |
| websockets         | timing                   |     2.0 |         2.6 |  1.3 |    0.21 |          2 |     0.26 | False |
| websockets         | traced                   |    48.7 |        17.0 |  0.3 |    0.34 |          1 |     0.37 | False |
| websockets         | tests-released           |    32.6 |         5.6 |  0.2 |    0.14 |          1 |     0.17 | False |
| websockets         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| websockets         | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| websockets         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | infer-union              |    19.2 |        34.2 |  1.8 |    0.93 |          1 |     0.17 | False |
| websockets         | tests-infer-union        |    28.6 |         5.6 |  0.2 |    0.15 |          1 |     0.16 | False |
| websockets         | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          1 |      0.2 | False |
| websockets         | types-released           |     2.7 |         1.1 |  0.4 |    0.14 |          1 |     0.14 | False |
| websockets         | types-fix-certain        |     0.8 |         0.7 |  0.9 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-likely         |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| websockets         | types-infer-basedpyright |     1.4 |         0.9 |  0.6 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-ty           |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-pyrefly      |     2.0 |         1.0 |  0.5 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-trace        |     1.4 |         0.9 |  0.6 |    0.11 |          1 |     0.14 | False |
| websockets         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | check                    |     1.4 |         2.0 |  1.4 |    0.22 |          2 |     0.26 | False |
| anyio              | fix-certain              |     2.6 |         4.9 |  1.9 |     0.3 |          2 |     0.37 | False |
| anyio              | fix-likely               |    10.2 |         8.3 |  0.8 |     0.3 |          2 |     0.37 | False |
| anyio              | fix-unsafe               |     8.0 |         8.0 |  1.0 |    0.34 |          2 |     0.37 | False |
| anyio              | infer-basedpyright       |    29.4 |        36.1 |  1.2 |    1.16 |          1 |     0.37 | False |
| anyio              | infer-ty                 |    15.4 |        13.7 |  0.9 |     0.6 |          1 |     0.42 | False |
| anyio              | infer-pyrefly            |    12.0 |        19.4 |  1.6 |    0.96 |          2 |     0.44 | False |
| anyio              | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.26 | False |
| anyio              | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| anyio              | timing                   |     2.2 |         2.9 |  1.3 |    0.22 |          2 |     0.27 | False |
| anyio              | traced                   |   150.5 |        66.3 |  0.4 |    0.44 |          1 |      0.4 | False |
| anyio              | tests-released           |   119.3 |        48.2 |  0.4 |    0.26 |          1 |     0.34 | False |
| anyio              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-fix-likely         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.34 | False |
| anyio              | infer-union              |    41.2 |        45.5 |  1.1 |    0.83 |          2 |     0.42 | False |
| anyio              | tests-infer-union        |   131.2 |        56.7 |  0.4 |    0.27 |          1 |     0.32 | False |
| anyio              | tests                    |     2.0 |         1.8 |  0.9 |    0.16 |          1 |      0.2 | False |
| zarr               | check                    |     1.6 |         3.4 |  2.1 |    0.32 |          2 |      0.4 | False |
| zarr               | fix-certain              |     5.2 |        11.7 |  2.2 |     0.4 |          3 |     0.51 | False |
| zarr               | fix-likely               |     9.8 |        18.6 |  1.9 |    0.63 |          3 |     0.67 | False |
| zarr               | fix-unsafe               |    12.6 |        16.7 |  1.3 |    0.46 |          2 |     0.56 | False |
| zarr               | infer-basedpyright       |    49.0 |       114.9 |  2.3 |    2.74 |          1 |     0.29 | False |
| zarr               | infer-ty                 |    20.6 |        32.9 |  1.6 |    1.75 |          2 |     0.66 | False |
| zarr               | infer-pyrefly            |    20.6 |        42.0 |  2.0 |    1.77 |          1 |     0.33 | False |
| zarr               | census                   |     1.2 |         0.9 |  0.8 |    0.05 |          2 |      0.4 | False |
| zarr               | coverage                 |     0.8 |         1.3 |  1.6 |     0.2 |          2 |     0.25 | False |
| zarr               | timing                   |     5.2 |         7.4 |  1.4 |    0.32 |          2 |      0.4 | False |
| zarr               | traced                   |   163.7 |       283.4 |  1.7 |    2.61 |          2 |     3.17 | False |
| zarr               | tests-released           |   115.0 |       212.3 |  1.8 |    2.41 |          3 |      3.0 | False |
| zarr               | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     3.01 | False |
| zarr               | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     3.04 | False |
| zarr               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     2.97 | False |
| zarr               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     2.92 | False |
| zarr               | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          3 |     2.99 | False |
| zarr               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     2.97 | False |
| zarr               | tests-infer-trace        |     1.2 |         0.2 |  0.2 |    0.03 |          3 |     3.02 | False |
| zarr               | infer-union              |    62.7 |       130.3 |  2.1 |     2.0 |          1 |     0.34 | False |
| zarr               | tests-infer-union        |   125.9 |       237.6 |  1.9 |    2.36 |          3 |     2.75 | False |
| zarr               | tests                    |     1.4 |         1.3 |  0.9 |    0.16 |          2 |      0.2 | False |
| joblib             | check                    |     2.6 |         4.0 |  1.5 |    0.36 |          2 |     0.45 | False |
| joblib             | fix-certain              |     5.2 |         9.7 |  1.9 |    0.43 |          2 |     0.52 | False |
| joblib             | fix-likely               |     8.0 |        12.9 |  1.6 |    0.45 |          2 |     0.56 | False |
| joblib             | fix-unsafe               |    10.8 |        14.8 |  1.4 |     0.5 |          1 |     0.56 | False |
| joblib             | infer-basedpyright       |    45.4 |        88.9 |  2.0 |    2.33 |          1 |     0.28 | False |
| joblib             | infer-ty                 |    13.0 |        21.6 |  1.7 |     1.3 |          1 |     0.28 | False |
| joblib             | infer-pyrefly            |    12.4 |        20.8 |  1.7 |    1.35 |          2 |     0.56 | False |
| joblib             | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.45 | False |
| joblib             | coverage                 |     1.0 |         1.4 |  1.4 |     0.2 |          2 |     0.24 | False |
| joblib             | timing                   |     4.4 |         5.8 |  1.3 |    0.36 |          2 |     0.45 | False |
| joblib             | traced                   |   233.2 |       480.9 |  2.1 |    1.05 |          1 |     1.34 | False |
| joblib             | tests-released           |   175.3 |       482.1 |  2.8 |    1.08 |          1 |     1.37 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-unsafe         |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.32 | False |
| joblib             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.34 | False |
| joblib             | infer-union              |    83.0 |       104.0 |  1.3 |    1.59 |          1 |     0.61 | False |
| joblib             | tests-infer-union        |   156.6 |       486.5 |  3.1 |    1.07 |          1 |     1.34 | False |
| joblib             | tests                    |     2.0 |         1.8 |  0.9 |    0.16 |          1 |      0.2 | False |
| networkx           | check                    |     8.0 |         0.3 |  0.0 |    0.08 |          3 |     1.57 | False |
| networkx           | fix-certain              |    37.8 |        80.9 |  2.1 |    1.61 |          3 |     1.88 | False |
| networkx           | fix-likely               |    45.8 |       111.9 |  2.4 |    2.15 |          3 |     2.56 | False |
| networkx           | fix-unsafe               |    79.0 |       124.4 |  1.6 |    2.15 |          2 |     2.55 | False |
| networkx           | infer-basedpyright       |   242.1 |       431.1 |  1.8 |    4.97 |          1 |     1.24 | False |
| networkx           | infer-ty                 |   107.9 |       154.5 |  1.4 |    3.98 |          1 |     1.22 | False |
| networkx           | infer-pyrefly            |   103.2 |       157.1 |  1.5 |    4.69 |          1 |     1.22 | False |
| networkx           | census                   |    13.4 |        27.6 |  2.1 |    1.34 |          3 |     1.57 | False |
| networkx           | coverage                 |     2.0 |         5.2 |  2.6 |     0.4 |          3 |      0.5 | False |
| networkx           | timing                   |    45.7 |        61.2 |  1.3 |    1.34 |          2 |     1.57 | False |
| networkx           | traced                   |    74.5 |       321.4 |  4.3 |    2.62 |          6 |     3.16 | False |
| networkx           | tests-released           |    29.5 |       236.9 |  8.0 |    2.39 |          8 |     2.94 | False |
| networkx           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      3.0 | False |
| networkx           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.02 | False |
| networkx           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.99 | False |
| networkx           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | infer-union              |   158.4 |       437.4 |  2.8 |    4.66 |          2 |     2.19 | False |
| networkx           | tests-infer-union        |    32.0 |       260.0 |  8.1 |    2.39 |          8 |      2.9 | False |
| networkx           | tests                    |     1.6 |         1.3 |  0.8 |    0.16 |          2 |      0.2 | False |
| networkx           | types-released           |     4.2 |         3.3 |  0.8 |    0.34 |          1 |     0.37 | False |
| networkx           | types-fix-certain        |     1.0 |         0.5 |  0.5 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-likely         |     1.8 |         0.7 |  0.4 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-unsafe         |     5.0 |         3.1 |  0.6 |    0.26 |          1 |      0.4 | False |
| networkx           | types-infer-basedpyright |     5.0 |         3.8 |  0.8 |    0.31 |          1 |     0.39 | False |
| networkx           | types-infer-ty           |     5.4 |         3.3 |  0.6 |    0.29 |          1 |      0.4 | False |
| networkx           | types-infer-pyrefly      |     3.9 |         3.4 |  0.9 |    0.33 |          1 |     0.39 | False |
| networkx           | types-infer-trace        |     7.4 |         4.3 |  0.6 |    0.33 |          1 |     0.36 | False |
| networkx           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| nibabel            | check                    |     3.8 |         8.6 |  2.3 |    0.63 |          3 |     0.77 | False |
| nibabel            | fix-certain              |    11.6 |        26.7 |  2.3 |    0.74 |          3 |     0.91 | False |
| nibabel            | fix-likely               |    16.8 |        38.7 |  2.3 |    0.97 |          3 |      1.2 | False |
| nibabel            | fix-unsafe               |    21.0 |        38.4 |  1.8 |    0.88 |          3 |     1.09 | False |
| nibabel            | infer-basedpyright       |   111.9 |       333.6 |  3.0 |    4.22 |          1 |     0.61 | False |
| nibabel            | infer-ty                 |    78.7 |       163.2 |  2.1 |    2.15 |          1 |      0.6 | False |
| nibabel            | infer-pyrefly            |    41.0 |        82.8 |  2.0 |    3.47 |          1 |     0.41 | False |
| nibabel            | census                   |     2.6 |         1.3 |  0.5 |    0.07 |          3 |     0.77 | False |
| nibabel            | coverage                 |     1.4 |         2.6 |  1.9 |    0.26 |          2 |     0.32 | False |
| nibabel            | timing                   |    12.4 |        18.4 |  1.5 |    0.63 |          2 |     0.77 | False |
| nibabel            | traced                   |    31.8 |       124.1 |  3.9 |    1.18 |          6 |     1.44 | False |
| nibabel            | tests-released           |    12.9 |        89.4 |  6.9 |    1.05 |          8 |     1.29 | False |
| nibabel            | tests-fix-certain        |    12.4 |        87.1 |  7.0 |    1.04 |          8 |     1.31 | False |
| nibabel            | tests-fix-likely         |    17.0 |        89.5 |  5.3 |    1.03 |          8 |     1.29 | False |
| nibabel            | tests-fix-unsafe         |    16.4 |        92.2 |  5.6 |    1.05 |          8 |     1.31 | False |
| nibabel            | tests-infer-basedpyright |    13.6 |        93.8 |  6.9 |    1.04 |          8 |     1.29 | False |
| nibabel            | tests-infer-ty           |    15.6 |        93.0 |  6.0 |    1.03 |          8 |     1.27 | False |
| nibabel            | tests-infer-pyrefly      |    16.8 |        90.4 |  5.4 |    1.05 |          8 |      1.3 | False |
| nibabel            | tests-infer-trace        |    14.2 |        88.4 |  6.2 |    1.02 |          8 |      1.3 | False |
| nibabel            | infer-union              |   122.1 |       433.8 |  3.6 |    4.51 |          2 |     0.86 | False |
| nibabel            | tests-infer-union        |    15.6 |        91.3 |  5.9 |    1.03 |          8 |     1.26 | False |
| nibabel            | tests                    |     1.0 |         1.0 |  1.0 |    0.16 |          8 |     1.39 | False |
| nibabel            | types-released           |     2.1 |         1.8 |  0.9 |    0.18 |          1 |      0.2 | False |
| nibabel            | types-fix-certain        |     3.4 |         2.6 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-fix-likely         |     2.8 |         2.5 |  0.9 |    0.17 |          1 |      0.2 | False |
| nibabel            | types-fix-unsafe         |     2.0 |         1.4 |  0.7 |    0.13 |          1 |     0.17 | False |
| nibabel            | types-infer-basedpyright |     3.8 |         2.6 |  0.7 |    0.18 |          1 |     0.21 | False |
| nibabel            | types-infer-ty           |     2.6 |         2.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-infer-pyrefly      |     3.4 |         2.5 |  0.7 |    0.17 |          1 |      0.2 | False |
| nibabel            | types-infer-trace        |     3.0 |         2.5 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | check                    |     3.4 |         7.1 |  2.1 |    0.52 |          3 |     0.64 | False |
| narwhals           | fix-certain              |     9.6 |        22.7 |  2.4 |    0.52 |          3 |     0.64 | False |
| narwhals           | fix-likely               |    15.0 |        33.9 |  2.3 |    1.04 |          3 |      1.2 | False |
| narwhals           | fix-unsafe               |    43.6 |        41.7 |  1.0 |    1.05 |          2 |      1.2 | False |
| narwhals           | infer-basedpyright       |    70.1 |       138.3 |  2.0 |    3.48 |          1 |      0.5 | False |
| narwhals           | infer-ty                 |    59.0 |        66.0 |  1.1 |    2.94 |          1 |      0.6 | False |
| narwhals           | infer-pyrefly            |    62.9 |        64.0 |  1.0 |     3.4 |          1 |      0.6 | False |
| narwhals           | census                   |     1.0 |         0.8 |  0.8 |    0.05 |          3 |     0.64 | False |
| narwhals           | coverage                 |     1.0 |         2.0 |  2.0 |     0.2 |          3 |     0.25 | False |
| narwhals           | timing                   |     8.6 |        12.6 |  1.5 |    0.52 |          2 |     0.64 | False |
| narwhals           | traced                   |    49.7 |       219.7 |  4.4 |    5.08 |          6 |      6.1 | False |
| narwhals           | tests-released           |    42.4 |       197.4 |  4.7 |    4.03 |          7 |     5.69 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.51 | False |
| narwhals           | infer-union              |    57.9 |       151.9 |  2.6 |    2.84 |          2 |      0.8 | False |
| narwhals           | tests-infer-union        |    29.5 |       177.1 |  6.0 |    4.65 |          7 |     5.67 | False |
| narwhals           | tests                    |     1.9 |         1.7 |  0.9 |    0.17 |          2 |      0.2 | False |
| narwhals           | types-released           |    60.7 |        68.0 |  1.1 |    1.57 |          2 |     2.09 | False |
| narwhals           | types-fix-certain        |    15.2 |        34.4 |  2.3 |    1.67 |          3 |     1.99 | False |
| narwhals           | types-fix-likely         |    24.7 |        46.1 |  1.9 |    1.58 |          2 |     1.96 | False |
| narwhals           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     1.91 | False |
| narwhals           | types-infer-basedpyright |    22.2 |        48.2 |  2.2 |    1.63 |          3 |      2.0 | False |
| narwhals           | types-infer-ty           |    21.6 |        47.8 |  2.2 |    1.59 |          3 |      2.0 | False |
| narwhals           | types-infer-pyrefly      |    19.8 |        44.9 |  2.3 |    1.69 |          3 |     2.02 | False |
| narwhals           | types-infer-trace        |    43.8 |        62.1 |  1.4 |    1.54 |          3 |      2.1 | False |
| narwhals           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| xarray             | check                    |    16.8 |        35.0 |  2.1 |    1.39 |          2 |     1.62 | False |
| xarray             | fix-certain              |    69.8 |       111.8 |  1.6 |    1.91 |          2 |     2.21 | False |
| xarray             | fix-likely               |    87.7 |       148.9 |  1.7 |    2.51 |          2 |     2.97 | False |
| xarray             | fix-unsafe               |    55.5 |       119.9 |  2.2 |    2.48 |          2 |     2.94 | False |
| xarray             | infer-basedpyright       |   230.1 |       473.4 |  2.1 |    6.23 |          1 |     1.56 | False |
| xarray             | infer-ty                 |   114.5 |       233.1 |  2.0 |    5.07 |          1 |     1.52 | False |
| xarray             | infer-pyrefly            |   103.2 |       188.5 |  1.8 |    6.15 |          2 |     2.92 | False |
| xarray             | census                   |    20.6 |         5.2 |  0.3 |    0.16 |          2 |     1.62 | False |
| xarray             | coverage                 |     2.2 |         6.2 |  2.8 |    0.47 |          3 |     0.56 | False |
| xarray             | timing                   |    54.0 |        73.8 |  1.4 |    1.39 |          2 |     1.62 | False |
| xarray             | traced                   |   132.3 |       270.2 |  2.0 |    2.57 |          4 |      3.0 | False |
| xarray             | tests-released           |    16.4 |        96.9 |  5.9 |    1.97 |          8 |     2.44 | False |
| xarray             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      2.5 | False |
| xarray             | infer-union              |   374.1 |       647.3 |  1.7 |    4.86 |          1 |     1.05 | False |
| xarray             | tests-infer-union        |    21.2 |       121.9 |  5.8 |    1.98 |          5 |     2.41 | False |
| xarray             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |      0.2 | False |
| litestar           | check                    |     2.6 |         5.2 |  2.0 |    0.44 |          2 |     0.55 | False |
| litestar           | fix-certain              |     6.8 |        14.3 |  2.1 |    0.67 |          3 |     0.84 | False |
| litestar           | fix-likely               |    10.8 |        21.9 |  2.0 |    0.94 |          2 |     1.15 | False |
| litestar           | fix-unsafe               |    12.2 |        21.0 |  1.7 |    0.73 |          2 |      0.9 | False |
| litestar           | infer-basedpyright       |    35.2 |       139.2 |  4.0 |    3.23 |          1 |     0.45 | False |
| litestar           | infer-ty                 |    44.6 |        43.3 |  1.0 |    1.35 |          1 |     0.45 | False |
| litestar           | infer-pyrefly            |    44.2 |        58.9 |  1.3 |    2.09 |          1 |     0.45 | False |
| litestar           | census                   |     2.4 |         0.8 |  0.3 |    0.04 |          2 |     0.55 | False |
| litestar           | coverage                 |     1.0 |         1.9 |  1.9 |     0.2 |          2 |     0.25 | False |
| litestar           | timing                   |     7.0 |         9.9 |  1.4 |    0.44 |          2 |     0.55 | False |
| litestar           | traced                   |    39.2 |       194.5 |  5.0 |    4.25 |          7 |     5.12 | False |
| litestar           | tests-released           |    32.2 |       165.9 |  5.2 |    3.88 |          6 |     4.92 | False |
| litestar           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.79 | False |
| litestar           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.76 | False |
| litestar           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.81 | False |
| litestar           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.64 | False |
| litestar           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      4.8 | False |
| litestar           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     4.81 | False |
| litestar           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.67 | False |
| litestar           | infer-union              |    37.0 |       133.0 |  3.6 |    2.13 |          1 |      0.3 | False |
| litestar           | tests-infer-union        |    23.8 |       137.8 |  5.8 |    3.81 |          8 |     4.85 | False |
| litestar           | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          2 |      0.2 | False |
| litestar           | types-released           |    70.5 |        78.7 |  1.1 |    2.06 |          2 |     2.35 | False |
| litestar           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.35 | False |
| litestar           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     2.35 | False |
| litestar           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.36 | False |
| litestar           | types-infer-basedpyright |    33.2 |        55.1 |  1.7 |    1.88 |          2 |     2.35 | False |
| litestar           | types-infer-ty           |    38.0 |        62.2 |  1.6 |    1.89 |          2 |     2.36 | False |
| litestar           | types-infer-pyrefly      |    37.6 |        60.2 |  1.6 |    1.89 |          2 |     2.39 | False |
| litestar           | types-infer-trace        |    39.6 |        65.7 |  1.7 |    1.91 |          2 |     2.35 | False |
| litestar           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| stripe             | check                    |     6.0 |        16.3 |  2.7 |    0.69 |          3 |     0.86 | False |
| stripe             | fix-certain              |    16.0 |        47.0 |  2.9 |    0.86 |          4 |     1.07 | False |
| stripe             | fix-likely               |    15.8 |        48.8 |  3.1 |     1.0 |          4 |     1.24 | False |
| stripe             | fix-unsafe               |    16.6 |        51.5 |  3.1 |    1.02 |          4 |     1.27 | False |
| stripe             | infer-basedpyright       |  2205.4 |      2122.4 |  1.0 |    2.68 |          1 |     0.46 | False |
| stripe             | infer-ty                 |    42.2 |        81.3 |  1.9 |    2.33 |          1 |     0.42 | False |
| stripe             | infer-pyrefly            |    51.1 |       114.9 |  2.2 |    3.42 |          1 |     0.77 | False |
| stripe             | census                   |     4.2 |         1.4 |  0.3 |    0.07 |          3 |     0.86 | False |
| stripe             | coverage                 |     2.4 |         7.1 |  3.0 |    0.26 |          3 |     0.34 | False |
| stripe             | timing                   |    33.9 |        39.6 |  1.2 |    0.69 |          2 |     0.86 | False |
| celery             | check                    |     1.4 |         0.1 |  0.1 |    0.04 |          2 |     1.06 | False |
| celery             | fix-certain              |    23.4 |        30.7 |  1.3 |    1.19 |          2 |     1.31 | False |
| celery             | fix-likely               |    19.2 |        32.5 |  1.7 |    1.34 |          2 |     1.47 | False |
| celery             | fix-unsafe               |    33.4 |        34.2 |  1.0 |    1.25 |          2 |     1.37 | False |
| celery             | infer-basedpyright       |    68.7 |       141.1 |  2.1 |    4.05 |          1 |     1.44 | False |
| celery             | infer-ty                 |    41.4 |        46.8 |  1.1 |    2.26 |          1 |     1.32 | False |
| celery             | infer-pyrefly            |    56.6 |        70.7 |  1.2 |    2.75 |          1 |     1.31 | False |
| celery             | census                   |     7.2 |        10.9 |  1.5 |    0.96 |          2 |     1.06 | False |
| celery             | coverage                 |     1.0 |         1.7 |  1.7 |    0.21 |          2 |     0.26 | False |
| celery             | timing                   |    14.8 |        18.7 |  1.3 |    0.96 |          2 |     1.06 | False |
| celery             | traced                   |   115.5 |       121.8 |  1.1 |    3.65 |          2 |     4.85 | False |
| celery             | tests-released           |    46.6 |        56.1 |  1.2 |    3.31 |          2 |     4.07 | False |
| celery             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      4.0 | False |
| celery             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     4.04 | False |
| celery             | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          2 |      4.0 | False |
| celery             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      4.0 | False |
| celery             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      4.0 | False |
| celery             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      4.0 | False |
| celery             | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          2 |      4.0 | False |
| celery             | infer-union              |    69.2 |       166.7 |  2.4 |    3.13 |          1 |     0.72 | False |
| celery             | tests-infer-union        |    47.5 |        56.2 |  1.2 |    3.19 |          2 |     4.06 | False |
| celery             | tests                    |     1.8 |         1.6 |  0.9 |    0.16 |          2 |      0.2 | False |
| optuna             | check                    |     3.8 |         0.2 |  0.1 |    0.04 |          3 |     0.92 | False |
| optuna             | fix-certain              |    18.8 |        30.0 |  1.6 |    1.18 |          2 |     1.45 | False |
| optuna             | fix-likely               |    28.2 |        50.2 |  1.8 |     1.7 |          2 |     2.02 | False |
| optuna             | fix-unsafe               |    36.0 |        40.2 |  1.1 |    1.23 |          2 |     1.51 | False |
| optuna             | infer-basedpyright       |    75.7 |       176.7 |  2.3 |    4.79 |          1 |     0.99 | False |
| optuna             | infer-ty                 |    74.5 |        80.6 |  1.1 |    2.89 |          1 |     0.99 | False |
| optuna             | infer-pyrefly            |    48.3 |        77.7 |  1.6 |    3.39 |          1 |     0.99 | False |
| optuna             | census                   |     5.0 |         9.5 |  1.9 |    0.75 |          3 |     0.92 | False |
| optuna             | coverage                 |     1.0 |         1.9 |  1.9 |     0.2 |          2 |     0.25 | False |
| optuna             | timing                   |    12.4 |        17.5 |  1.4 |    0.75 |          2 |     0.92 | False |
| optuna             | traced                   |   167.9 |      1764.1 | 10.5 |    4.94 |          8 |     5.81 | False |
| optuna             | tests-released           |   109.7 |       848.6 |  7.7 |     3.9 |          8 |     5.02 | False |
| optuna             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | infer-union              |    63.8 |       189.4 |  3.0 |     3.4 |          2 |      2.0 | False |
| optuna             | tests-infer-union        |   154.4 |      1574.6 | 10.2 |    3.93 |          8 |     4.89 | False |
| optuna             | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |      0.2 | False |
| optuna             | types-released           |    10.9 |         7.4 |  0.7 |    0.47 |          1 |     0.46 | False |
| optuna             | types-fix-certain        |     9.4 |         7.0 |  0.7 |    0.37 |          1 |     0.46 | False |
| optuna             | types-fix-likely         |     8.0 |         6.6 |  0.8 |    0.37 |          1 |     0.46 | False |
| optuna             | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.47 | False |
| optuna             | types-infer-basedpyright |     8.6 |         5.9 |  0.7 |    0.37 |          1 |     0.46 | False |
| optuna             | types-infer-ty           |     6.4 |         5.9 |  0.9 |    0.38 |          1 |     0.46 | False |
| optuna             | types-infer-pyrefly      |     5.4 |         5.0 |  0.9 |    0.37 |          1 |     0.47 | False |
| optuna             | types-infer-trace        |     7.5 |         6.2 |  0.8 |    0.39 |          1 |     0.46 | False |
| optuna             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| dask               | check                    |     0.4 |         0.3 |  0.7 |    0.08 |          3 |     2.07 | False |
| dask               | fix-certain              |    80.8 |       130.0 |  1.6 |    2.33 |          3 |     2.74 | False |
| dask               | fix-likely               |    97.4 |       170.1 |  1.7 |    3.08 |          3 |     3.66 | False |
| dask               | fix-unsafe               |   105.3 |       166.4 |  1.6 |    3.01 |          2 |     3.57 | False |
| dask               | infer-basedpyright       |   231.6 |       744.8 |  3.2 |    7.34 |          1 |     1.85 | False |
| dask               | infer-ty                 |   139.1 |       264.3 |  1.9 |     5.5 |          1 |     1.82 | False |
| dask               | infer-pyrefly            |   139.9 |       245.3 |  1.8 |    6.59 |          1 |     1.89 | False |
| dask               | census                   |    23.6 |        47.6 |  2.0 |    1.77 |          3 |     2.07 | False |
| dask               | coverage                 |     2.6 |         7.1 |  2.7 |    0.46 |          3 |     0.57 | False |
| dask               | timing                   |    66.4 |        93.2 |  1.4 |    1.77 |          2 |     2.07 | False |
| dask               | traced                   |   176.3 |      1187.0 |  6.7 |    5.01 |          8 |     6.17 | False |
| dask               | tests-released           |   149.2 |      1127.4 |  7.6 |    4.55 |          8 |      5.8 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      5.8 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.76 | False |
| dask               | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      5.8 | False |
| dask               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.82 | False |
| dask               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.64 | False |
| dask               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     5.52 | False |
| dask               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |      5.4 | False |
| dask               | infer-union              |   251.5 |       696.9 |  2.8 |    7.77 |          4 |     9.25 | False |
| dask               | tests-infer-union        |   140.1 |      1109.4 |  7.9 |    4.46 |          8 |     5.54 | False |
| dask               | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          2 |      0.2 | False |
| mypy               | check                    |     3.2 |         9.3 |  2.9 |    0.52 |          3 |     0.65 | False |
| mypy               | fix-certain              |    12.6 |        40.2 |  3.2 |    0.81 |          4 |     0.99 | False |
| mypy               | fix-likely               |    23.2 |        52.7 |  2.3 |    0.96 |          4 |      1.2 | False |
| mypy               | fix-unsafe               |    22.8 |        51.5 |  2.3 |     0.9 |          2 |     1.12 | False |
| mypy               | infer-basedpyright       |    76.8 |       208.6 |  2.7 |    4.37 |          3 |     0.87 | False |
| mypy               | infer-ty                 |    31.6 |        78.1 |  2.5 |    2.39 |          1 |     0.57 | False |
| mypy               | infer-pyrefly            |    31.0 |        71.0 |  2.3 |    2.58 |          1 |     0.58 | False |
| mypy               | census                   |     4.8 |         2.3 |  0.5 |     0.1 |          3 |     0.65 | False |
| mypy               | coverage                 |     1.8 |         5.5 |  3.1 |    0.35 |          3 |     0.44 | False |
| mypy               | timing                   |    15.2 |        24.3 |  1.6 |    0.52 |          2 |     0.65 | False |
| mypy               | traced                   |   325.9 |      2284.1 |  7.0 |    6.39 |          8 |      7.8 | False |
| mypy               | tests-released           |   303.7 |      2040.7 |  6.7 |     5.8 |          8 |     7.69 | False |
| mypy               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.47 | False |
| mypy               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.25 | False |
| mypy               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     7.65 | False |
| mypy               | infer-union              |    63.4 |       177.1 |  2.8 |     2.4 |          1 |      0.4 | False |
| mypy               | tests-infer-union        |   332.2 |      2184.4 |  6.6 |    6.17 |          7 |     7.56 | False |
| mypy               | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          2 |      0.2 | False |
| mypy               | types-released           |    10.2 |        27.3 |  2.7 |    0.62 |          3 |     0.74 | False |
| mypy               | types-fix-certain        |     7.0 |        17.7 |  2.5 |    0.49 |          3 |     0.61 | False |
| mypy               | types-fix-likely         |     9.6 |        21.5 |  2.2 |     0.5 |          3 |     0.79 | False |
| mypy               | types-fix-unsafe         |     0.6 |         0.5 |  0.8 |    0.05 |          3 |     0.76 | False |
| mypy               | types-infer-basedpyright |     7.6 |        19.3 |  2.5 |    0.49 |          3 |      0.6 | False |
| mypy               | types-infer-ty           |    10.6 |        26.4 |  2.5 |    0.62 |          3 |     0.76 | False |
| mypy               | types-infer-pyrefly      |     7.2 |        16.8 |  2.3 |    0.49 |          3 |     0.62 | False |
| mypy               | types-infer-trace        |    10.6 |        27.5 |  2.6 |    0.62 |          3 |     0.77 | False |
| mypy               | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,392 |       4,320 |     1 |
| sphinx | likely             |          929 | 3,931 |       4,859 |     1 |
| sphinx | unsafe             |          929 | 4,335 |       5,263 |     1 |
| sphinx | infer-basedpyright |          929 | 5,092 |       6,020 |     1 |
| sphinx | infer-ty           |          929 | 5,146 |       6,074 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,326 |       6,254 |     1 |
| sphinx | infer-trace        |          929 | 4,335 |       5,263 |     1 |
| mypy   | unsafe             |        2,300 | 6,758 |       9,057 |     1 |
| mypy   | infer-basedpyright |        2,300 | 8,392 |      10,690 |     2 |
| mypy   | infer-ty           |        2,300 | 8,696 |      10,994 |     2 |
| mypy   | infer-pyrefly      |        2,300 | 8,915 |      11,213 |     2 |
| mypy   | infer-trace        |        2,300 | 6,758 |       9,057 |     1 |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus             | released                                                              | traced                                                                | same failures |
| ------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------- |
| django             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped            | 5 expected failures, 5 failures, 17,585 ran, 1,149 skipped            | False         |
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
| nibabel            | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           | 21 error, 110 failed, 5,165 passed, 304 skipped, 40 xfailed           | False         |
| narwhals           | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | True          |
| xarray             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed | 3 error, 3 failed, 6,333 passed, 9,626 skipped, 11 xfailed, 4 xpassed | False         |
| litestar           | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           | 6 failed, 5,645 passed, 256 skipped, 13 xfailed, 30 xpassed           | False         |
| celery             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         | 4 failed, 3,520 passed, 36 skipped, 3 xfailed                         | False         |
| optuna             | 16 error, 263 failed, 4,203 passed, 43 skipped                        | 16 error, 263 failed, 4,203 passed, 43 skipped                        | False         |
| dask               | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | 5 failed, 16,196 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | False         |
| mypy               | 14,464 passed, 366 skipped, 12 xfailed                                | 14,464 passed, 366 skipped, 12 xfailed                                | True          |

- standard library, mega+dev, infer-basedpyright: held 11.12 GB beside other steps
- standard library, mega+dev, infer-ty: held 11.5 GB beside other steps
- standard library, mega+dev, infer-pyrefly: held 13.86 GB beside other steps
- django, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- sqlalchemy, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, infer-basedpyright: held 12.26 GB beside other steps
- pandas, mega+dev, infer-ty: held 10.38 GB beside other steps
- pandas, mega+dev, infer-pyrefly: held 16.64 GB beside other steps
- pandas, mega+dev, traced: held 14.38 GB beside other steps
- pandas, mega+dev, tests-released: held 11.49 GB beside other steps
- pandas, mega+dev, infer-union: held 11.69 GB beside other steps
- pandas, mega+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, tests-infer-union: held 13.03 GB beside other steps
- structlog, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- structlog, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- structlog, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- attrs, mega+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, mega+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, mega+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- click, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- click, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- hypercorn, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- hypercorn, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- starlette, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- starlette, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- werkzeug, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- werkzeug, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- mkdocs, mega+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, mega+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- mkdocs, mega+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- httpx, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- httpx, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- httpx, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- black, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- fastapi, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- cattrs, mega+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, mega+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, mega+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pytest, mega+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, mega+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, mega+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its seconds
  measure less of the checker
- botocore, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- botocore, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- botocore, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- uvicorn, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- mcp, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mcp, mega+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- textual, mega+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- textual, mega+dev, infer-ty: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- textual, mega+dev, infer-pyrefly: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: basedpyright's hints for 3 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: pyrefly's hints for 3 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pdm, mega+dev, infer-union: ty's hints for 3 of 4 rounds came from the store, so its seconds
  measure less of the checker
- strawberry-graphql, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pygments, mega+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- streamlink, mega+dev, infer-union: basedpyright's hints for 1 of 4 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, mega+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, mega+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, mega+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pint, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pint, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pint, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- altair, mega+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- altair, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- altair, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- seaborn, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- aiohttp, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- websockets, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- websockets, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- websockets, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- zarr, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- zarr, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- zarr, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- joblib, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- joblib, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- joblib, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- networkx, mega+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so
  its seconds measure less of the checker
- networkx, mega+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- networkx, mega+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- nibabel, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- narwhals, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- narwhals, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- narwhals, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- xarray, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- litestar, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- litestar, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- litestar, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- stripe, mega+dev, infer-basedpyright: basedpyright's hints for 1 of 4 rounds came from the store,
  so its seconds measure less of the checker
- celery, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its seconds
  measure less of the checker
- optuna, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- dask, mega+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- dask, mega+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- dask, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- mypy, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mypy, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mypy, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
