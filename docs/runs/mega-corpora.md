# Mega corpora

The run `mega` (`python -m tests.corpus`) on mega: constricter 0.4.7.dev1+gfa6079225.d20261118
(`fa607922510e`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 95 minutes. Timings don't compare across machines, nor their seconds across runs, taken
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
| requests           | 2.34.2   | mega+dev    |     19 |             305 |            62 |        0 |             32 |           10 |            0 |         0 |        0 |        0 |     409 |
| rich               | 15.0.0   | mega+dev    |    100 |           1,612 |           258 |        0 |            308 |            6 |            7 |         0 |        0 |        0 |   2,191 |
| urllib3            | 2.8.0    | mega+dev    |     36 |             443 |            57 |        0 |            134 |            5 |            1 |         2 |        0 |        0 |     642 |
| sqlmodel           | 0.0.48   | mega+dev    |     16 |              86 |            18 |        0 |             21 |           17 |            0 |         0 |        0 |        0 |     142 |
| marshmallow        | 4.3.1    | mega+dev    |     14 |             147 |            50 |        0 |            105 |           20 |            3 |         0 |        0 |        0 |     325 |
| textual            | 8.2.8    | mega+dev    |    247 |           4,979 |           718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| pdm                | 2.29.2   | mega+dev    |    128 |           2,114 |           417 |        0 |            182 |           37 |            2 |         0 |        0 |        0 |   2,752 |
| strawberry-graphql | 0.332.0  | mega+dev    |    244 |           1,436 |           243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| pygments           | 2.21.0   | mega+dev    |    343 |           1,124 |           539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| streamlink         | 8.6.1    | mega+dev    |    227 |           2,080 |           310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| sphinx             | 9.1.0    | mega+dev    |    243 |           5,505 |         1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| tox                | 4.64.9   | mega+dev    |    129 |           1,369 |           286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| trio               | 0.34.0   | mega+dev    |    144 |           2,540 |           245 |        0 |            199 |           39 |            2 |         0 |        0 |        0 |   3,025 |
| langchain-core     | 1.7.0    | mega+dev    |    182 |           2,872 |           632 |        0 |            226 |          182 |           10 |         0 |        0 |        0 |   3,922 |
| matplotlib         | 3.11.2   | mega+dev    |    256 |          20,464 |         2,224 |        0 |          1,392 |            7 |            4 |         3 |        0 |        1 |  24,095 |
| pint               | 0.26.1   | mega+dev    |    109 |           2,591 |           297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| altair             | 6.3.0    | mega+dev    |     55 |             814 |           130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| seaborn            | 0.13.2   | mega+dev    |     54 |           2,361 |           370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| aiohttp            | 3.14.4   | mega+dev    |     54 |           1,307 |           195 |        0 |            355 |           13 |            5 |         2 |        0 |        0 |   1,877 |
| websockets         | 17.2     | mega+dev    |     52 |             605 |            85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| anyio              | 4.15.1   | mega+dev    |     46 |             615 |            77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| zarr               | 3.4.0    | mega+dev    |     98 |           1,874 |           370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| joblib             | 1.6.0    | mega+dev    |     73 |           1,842 |           158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| networkx           | 3.7      | mega+dev    |    583 |          18,854 |         3,221 |        0 |            381 |            7 |            0 |         0 |        0 |        0 |  22,463 |
| nibabel            | 5.4.2    | mega+dev    |    229 |           6,504 |         1,032 |        0 |            930 |            5 |            1 |         0 |        0 |        0 |   8,472 |
| narwhals           | 2.26.0   | mega+dev    |    162 |           2,775 |           106 |        0 |            231 |           62 |            5 |         0 |        0 |        0 |   3,179 |
| xarray             | 2026.9.0 | mega+dev    |    199 |          18,968 |         1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| litestar           | 2.24.0   | mega+dev    |    374 |           1,474 |           306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| stripe             | 16.0.0   | mega+dev    |  1,460 |           1,772 |            49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| celery             | 5.6.3    | mega+dev    |    161 |           2,202 |           331 |        0 |          1,214 |            0 |            0 |         2 |        0 |        0 |   3,749 |
| optuna             | 5.0.0    | mega+dev    |    220 |           2,740 |           446 |        0 |            409 |           28 |            4 |         0 |        0 |        0 |   3,627 |
| dask               | 2026.8.0 | mega+dev    |    361 |          20,748 |         1,691 |        0 |          1,732 |           75 |            5 |         2 |        0 |        1 |  24,254 |
| mypy               | 2.4.0    | mega+dev    |    195 |           9,008 |         2,197 |        0 |            196 |           58 |           45 |         0 |        1 |        1 |  11,506 |
| **Total**          |          | mega+dev    | 13,229 | 359,551 (78.4%) | 44,262 (9.6%) | 1 (0.0%) | 50,914 (11.1%) | 2,756 (0.6%) | 1,300 (0.3%) | 33 (0.0%) | 1 (0.0%) | 8 (0.0%) | 458,826 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |           Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | ----------- | ----------: | ---------------: | --------------: | ----------: | --------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | mega+dev    | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,413 (32.9%) |   7,005 (6.2%) | 14,266 (12.5%) |      0 |    0 |            0 |
| django             | mega+dev    |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |   2,625 (15.3%) |     735 (4.3%) |  2,892 (16.8%) |      0 |    0 |            0 |
| sqlalchemy         | mega+dev    |  0 / 12,934 |   11,296 / 2,339 |    12,934 / 701 |  13,635 / 0 |   2,146 (15.7%) |     446 (3.3%) |   1,153 (8.5%) |      0 |    0 |            0 |
| pydantic           | mega+dev    |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |   1,203 (36.3%) |     151 (4.6%) |    414 (12.5%) |      0 |    0 |            0 |
| pandas             | mega+dev    |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  17,867 (22.9%) | 24,334 (31.2%) | 25,484 (32.7%) |      0 |    0 |            0 |
| twisted            | mega+dev    |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,435 (13.6%) |  3,742 (20.9%) |  4,830 (27.0%) |      0 |    0 |            0 |
| pip                | mega+dev    |   0 / 8,923 |    7,773 / 1,150 |       8,923 / 0 |   8,923 / 0 |   2,243 (25.1%) |     495 (5.5%) |  1,346 (15.1%) |      0 |    0 |            0 |
| structlog          | mega+dev    |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |      98 (29.8%) |      15 (4.6%) |      28 (8.5%) |      0 |    0 |            0 |
| attrs              | mega+dev    |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |      93 (23.5%) |       9 (2.3%) |      14 (3.5%) |      0 |    0 |            0 |
| click              | mega+dev    |     0 / 607 |         549 / 87 |        607 / 29 |     636 / 0 |     311 (48.9%) |      27 (4.2%) |     64 (10.1%) |      0 |    0 |            0 |
| hypercorn          | mega+dev    |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |     137 (37.7%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | mega+dev    |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |     322 (42.3%) |     76 (10.0%) |    117 (15.4%) |      0 |    0 |            0 |
| werkzeug           | mega+dev    |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |     545 (41.6%) |      72 (5.5%) |    138 (10.5%) |      0 |    0 |            0 |
| mkdocs             | mega+dev    |   0 / 2,331 |      2,133 / 206 |       2,331 / 8 |   2,339 / 0 |     826 (35.3%) |    430 (18.4%) |    552 (23.6%) |      0 |    0 |            0 |
| httpx              | mega+dev    |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |     240 (42.1%) |     69 (12.1%) |     84 (14.7%) |      0 |    0 |            0 |
| black              | mega+dev    |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |     714 (55.7%) |    128 (10.0%) |    169 (13.2%) |      0 |    0 |            0 |
| fastapi            | mega+dev    |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |     265 (31.4%) |      45 (5.3%) |      71 (8.4%) |      0 |    0 |            0 |
| cattrs             | mega+dev    |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     114 (21.5%) |      35 (6.6%) |     53 (10.0%) |      0 |    0 |            0 |
| pytest             | mega+dev    |   0 / 3,000 |      2,530 / 512 |      3,000 / 42 |   3,042 / 0 |   1,376 (45.2%) |     160 (5.3%) |    313 (10.3%) |      0 |    0 |            0 |
| botocore           | mega+dev    |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     548 (14.5%) |     183 (4.8%) |    656 (17.3%) |      0 |    0 |            0 |
| uvicorn            | mega+dev    |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     236 (46.8%) |      32 (6.3%) |     57 (11.3%) |      0 |    0 |            0 |
| mcp                | mega+dev    |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     720 (39.3%) |     162 (8.8%) |    248 (13.5%) |      0 |    0 |            0 |
| requests           | mega+dev    |     0 / 399 |         337 / 72 |        399 / 10 |     409 / 0 |      96 (23.5%) |       9 (2.2%) |      17 (4.2%) |      0 |    0 |            0 |
| rich               | mega+dev    |   0 / 2,178 |      1,920 / 271 |      2,178 / 13 |   2,191 / 0 |   1,022 (46.6%) |    306 (14.0%) |    433 (19.8%) |      0 |    0 |            0 |
| urllib3            | mega+dev    |     0 / 636 |         577 / 65 |         636 / 6 |     642 / 0 |     259 (40.3%) |      42 (6.5%) |     79 (12.3%) |      0 |    0 |            0 |
| sqlmodel           | mega+dev    |     0 / 125 |         107 / 35 |        125 / 17 |     142 / 0 |       11 (7.7%) |       5 (3.5%) |      10 (7.0%) |      0 |    0 |            0 |
| marshmallow        | mega+dev    |     0 / 302 |         252 / 73 |        302 / 23 |     325 / 0 |      51 (15.7%) |       5 (1.5%) |     52 (16.0%) |      0 |    0 |            0 |
| textual            | mega+dev    |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,800 (42.8%) |     507 (7.8%) |    774 (11.8%) |      0 |    0 |            0 |
| pdm                | mega+dev    |   0 / 2,713 |      2,296 / 456 |      2,713 / 39 |   2,752 / 0 |   1,246 (45.3%) |     218 (7.9%) |    364 (13.2%) |      0 |    0 |            0 |
| strawberry-graphql | mega+dev    |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     657 (33.8%) |     174 (8.9%) |    241 (12.4%) |      0 |    0 |            0 |
| pygments           | mega+dev    |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      736 (9.6%) |      81 (1.1%) |  4,617 (60.2%) |      0 |    0 |            0 |
| streamlink         | mega+dev    |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     701 (22.8%) |     138 (4.5%) |    579 (18.8%) |      0 |    0 |            0 |
| sphinx             | mega+dev    |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,392 (42.0%) |     539 (6.7%) |    943 (11.7%) |      0 |    0 |            0 |
| tox                | mega+dev    |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     985 (55.2%) |     103 (5.8%) |     158 (8.9%) |      0 |    0 |            0 |
| trio               | mega+dev    |   0 / 2,984 |      2,739 / 286 |      2,984 / 41 |   3,025 / 0 |   1,106 (36.6%) |     271 (9.0%) |    332 (11.0%) |      0 |    0 |            0 |
| langchain-core     | mega+dev    |   0 / 3,730 |      3,098 / 824 |     3,730 / 192 |   3,922 / 0 |   1,702 (43.4%) |     204 (5.2%) |     307 (7.8%) |      0 |    0 |            0 |
| matplotlib         | mega+dev    |  0 / 24,083 |   21,856 / 2,239 |     24,083 / 12 |  24,095 / 0 |   7,498 (31.1%) |   2,107 (8.7%) |  2,789 (11.6%) |      0 |    0 |            0 |
| pint               | mega+dev    |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     650 (21.0%) |     276 (8.9%) |    328 (10.6%) |      0 |    0 |            0 |
| altair             | mega+dev    |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     389 (22.0%) |      52 (2.9%) |      65 (3.7%) |      0 |    0 |            0 |
| seaborn            | mega+dev    |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     658 (22.5%) |     164 (5.6%) |     242 (8.3%) |      0 |    0 |            0 |
| aiohttp            | mega+dev    |   0 / 1,859 |      1,662 / 215 |      1,859 / 18 |   1,877 / 0 |     722 (38.5%) |     152 (8.1%) |    274 (14.6%) |      0 |    0 |            0 |
| websockets         | mega+dev    |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     362 (45.8%) |      77 (9.7%) |    130 (16.4%) |      0 |    0 |            0 |
| anyio              | mega+dev    |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     230 (30.8%) |      36 (4.8%) |      69 (9.2%) |      0 |    0 |            0 |
| zarr               | mega+dev    |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,169 (47.3%) |      79 (3.2%) |     118 (4.8%) |      0 |    0 |            0 |
| joblib             | mega+dev    |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     179 (8.0%) |    308 (13.8%) |      0 |    0 |            0 |
| networkx           | mega+dev    |  0 / 22,456 |   19,235 / 3,228 |      22,456 / 7 |  22,463 / 0 |   3,975 (17.7%) |  2,236 (10.0%) |  2,566 (11.4%) |      0 |    0 |            0 |
| nibabel            | mega+dev    |   0 / 8,466 |    7,434 / 1,038 |       8,466 / 6 |   8,472 / 0 |   1,874 (22.1%) |    845 (10.0%) |  1,175 (13.9%) |      0 |    0 |            0 |
| narwhals           | mega+dev    |   0 / 3,112 |      3,006 / 173 |      3,112 / 67 |   3,179 / 0 |   1,082 (34.0%) |      76 (2.4%) |     131 (4.1%) |      0 |    0 |            0 |
| xarray             | mega+dev    |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   4,651 (21.5%) |  5,178 (24.0%) |  5,530 (25.6%) |      0 |    0 |            0 |
| litestar           | mega+dev    |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     648 (31.0%) |     124 (5.9%) |     198 (9.5%) |      0 |    0 |            0 |
| stripe             | mega+dev    |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     781 (18.5%) |     166 (3.9%) |    671 (15.9%) |      0 |    0 |            0 |
| celery             | mega+dev    |   0 / 3,749 |      3,416 / 333 |       3,749 / 0 |   3,749 / 0 |     508 (13.6%) |     132 (3.5%) |     372 (9.9%) |      0 |    0 |            0 |
| optuna             | mega+dev    |   0 / 3,595 |      3,149 / 478 |      3,595 / 32 |   3,627 / 0 |   1,585 (43.7%) |     219 (6.0%) |     326 (9.0%) |      0 |    0 |            0 |
| dask               | mega+dev    |  0 / 24,173 |   22,480 / 1,774 |     24,173 / 81 |  24,254 / 0 |   3,272 (13.5%) |   2,024 (8.3%) |  2,944 (12.1%) |      0 |    0 |            0 |
| mypy               | mega+dev    |  0 / 11,401 |    9,204 / 2,301 |    11,401 / 105 |  11,506 / 0 |   5,775 (50.2%) |  1,274 (11.1%) |  1,723 (15.0%) |      0 |    0 |            0 |
| **Total**          | mega+dev    | 0 / 454,761 | 410,465 / 48,360 | 454,760 / 4,066 | 458,826 / 0 | 123,595 (26.9%) | 56,369 (12.3%) | 81,872 (17.8%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | mega+dev    |              1.2% |         33.7% |            39.8% |                  46.1% | +32.5 pts, 32.9% of untyped | +44.9 pts, 45.5% of untyped |
| django             | mega+dev    |              0.0% |         15.3% |            19.6% |                  32.1% | +15.3 pts, 15.3% of untyped | +32.1 pts, 32.1% of untyped |
| sqlalchemy         | mega+dev    |             15.3% |         29.3% |            32.2% |                  36.8% | +14.0 pts, 16.5% of untyped | +21.6 pts, 25.4% of untyped |
| pydantic           | mega+dev    |             22.4% |         52.4% |            56.1% |                  62.7% | +29.9 pts, 38.6% of untyped | +40.2 pts, 51.9% of untyped |
| pandas             | mega+dev    |              1.6% |         24.2% |            55.0% |                  56.4% | +22.6 pts, 23.0% of untyped | +54.8 pts, 55.7% of untyped |
| twisted            | mega+dev    |              0.0% |         13.6% |            34.6% |                  40.6% | +13.6 pts, 13.6% of untyped | +40.6 pts, 40.6% of untyped |
| pip                | mega+dev    |              1.5% |         26.3% |            31.7% |                  41.1% | +24.7 pts, 25.1% of untyped | +39.6 pts, 40.2% of untyped |
| structlog          | mega+dev    |             25.6% |         48.7% |            52.2% |                  55.3% | +23.1 pts, 31.0% of untyped | +29.6 pts, 39.9% of untyped |
| attrs              | mega+dev    |              0.8% |         24.2% |            26.5% |                  27.8% | +23.5 pts, 23.7% of untyped | +27.0 pts, 27.2% of untyped |
| click              | mega+dev    |             31.5% |         66.5% |            69.6% |                  73.7% | +35.1 pts, 51.2% of untyped | +42.3 pts, 61.7% of untyped |
| hypercorn          | mega+dev    |             32.4% |         58.5% |            62.3% |                  69.5% | +26.1 pts, 38.6% of untyped | +37.1 pts, 54.9% of untyped |
| starlette          | mega+dev    |             10.3% |         49.1% |            58.3% |                  63.2% | +38.8 pts, 43.3% of untyped | +53.0 pts, 59.0% of untyped |
| werkzeug           | mega+dev    |             14.3% |         50.4% |            55.2% |                  59.6% | +36.1 pts, 42.2% of untyped | +45.3 pts, 52.8% of untyped |
| mkdocs             | mega+dev    |              4.5% |         38.4% |            56.0% |                  60.9% | +33.8 pts, 35.4% of untyped | +56.4 pts, 59.1% of untyped |
| httpx              | mega+dev    |              6.3% |         45.8% |            57.2% |                  59.6% | +39.5 pts, 42.2% of untyped | +53.4 pts, 56.9% of untyped |
| black              | mega+dev    |             15.9% |         63.1% |            71.5% |                  74.2% | +47.2 pts, 56.1% of untyped | +58.4 pts, 69.4% of untyped |
| fastapi            | mega+dev    |             42.0% |         62.7% |            66.2% |                  68.3% | +20.7 pts, 35.7% of untyped | +26.3 pts, 45.3% of untyped |
| cattrs             | mega+dev    |              7.0% |         27.4% |            33.6% |                  36.9% | +20.4 pts, 21.9% of untyped | +29.9 pts, 32.1% of untyped |
| pytest             | mega+dev    |             12.1% |         52.4% |            57.1% |                  61.6% | +40.3 pts, 45.8% of untyped | +49.4 pts, 56.2% of untyped |
| botocore           | mega+dev    |              0.5% |         14.9% |            19.7% |                  32.1% | +14.4 pts, 14.5% of untyped | +31.6 pts, 31.8% of untyped |
| uvicorn            | mega+dev    |             23.6% |         60.5% |            65.5% |                  69.4% | +36.9 pts, 48.3% of untyped | +45.8 pts, 59.9% of untyped |
| mcp                | mega+dev    |             30.7% |         59.7% |            66.3% |                  69.7% | +29.0 pts, 41.9% of untyped | +39.0 pts, 56.3% of untyped |
| requests           | mega+dev    |             28.6% |         45.8% |            47.4% |                  48.8% | +17.2 pts, 24.1% of untyped | +20.2 pts, 28.3% of untyped |
| rich               | mega+dev    |             13.4% |         54.1% |            66.2% |                  71.3% | +40.6 pts, 46.9% of untyped | +57.8 pts, 66.8% of untyped |
| urllib3            | mega+dev    |             25.8% |         56.1% |            61.1% |                  65.4% | +30.3 pts, 40.9% of untyped | +39.5 pts, 53.3% of untyped |
| sqlmodel           | mega+dev    |             23.8% |         30.5% |            33.5% |                  36.6% |   +6.7 pts, 8.8% of untyped | +12.8 pts, 16.8% of untyped |
| marshmallow        | mega+dev    |             20.1% |         33.6% |            34.9% |                  47.4% | +13.5 pts, 16.9% of untyped | +27.2 pts, 34.1% of untyped |
| textual            | mega+dev    |             15.6% |         52.0% |            58.6% |                  62.1% | +36.5 pts, 43.2% of untyped | +46.6 pts, 55.1% of untyped |
| pdm                | mega+dev    |             11.7% |         52.2% |            59.3% |                  64.0% | +40.5 pts, 45.8% of untyped | +52.3 pts, 59.2% of untyped |
| strawberry-graphql | mega+dev    |             30.1% |         55.5% |            62.2% |                  64.8% | +25.4 pts, 36.4% of untyped | +34.8 pts, 49.7% of untyped |
| pygments           | mega+dev    |              0.0% |          9.6% |            10.7% |                  69.8% |   +9.6 pts, 9.6% of untyped | +69.8 pts, 69.8% of untyped |
| streamlink         | mega+dev    |             42.8% |         56.0% |            58.6% |                  66.9% | +13.2 pts, 23.1% of untyped | +24.2 pts, 42.3% of untyped |
| sphinx             | mega+dev    |             10.4% |         48.5% |            54.6% |                  59.1% | +38.1 pts, 42.5% of untyped | +48.7 pts, 54.4% of untyped |
| tox                | mega+dev    |             16.0% |         63.0% |            67.9% |                  70.5% | +46.9 pts, 55.9% of untyped | +54.5 pts, 64.9% of untyped |
| trio               | mega+dev    |             15.0% |         46.4% |            54.0% |                  55.8% | +31.3 pts, 36.9% of untyped | +40.7 pts, 47.9% of untyped |
| langchain-core     | mega+dev    |             20.6% |         56.8% |            61.2% |                  63.4% | +36.2 pts, 45.6% of untyped | +42.8 pts, 53.9% of untyped |
| matplotlib         | mega+dev    |              0.7% |         31.6% |            40.3% |                  43.1% | +30.9 pts, 31.1% of untyped | +42.4 pts, 42.7% of untyped |
| pint               | mega+dev    |              5.1% |         25.1% |            33.6% |                  35.2% | +20.0 pts, 21.1% of untyped | +30.2 pts, 31.8% of untyped |
| altair             | mega+dev    |             49.7% |         61.2% |            62.8% |                  63.1% | +11.5 pts, 22.9% of untyped | +13.4 pts, 26.7% of untyped |
| seaborn            | mega+dev    |              6.9% |         28.1% |            33.3% |                  35.9% | +21.2 pts, 22.7% of untyped | +28.9 pts, 31.1% of untyped |
| aiohttp            | mega+dev    |             23.7% |         53.3% |            59.6% |                  64.6% | +29.7 pts, 38.9% of untyped | +40.9 pts, 53.6% of untyped |
| websockets         | mega+dev    |             13.8% |         53.3% |            61.7% |                  67.4% | +39.4 pts, 45.8% of untyped | +53.6 pts, 62.2% of untyped |
| anyio              | mega+dev    |             27.8% |         51.0% |            54.6% |                  58.0% | +23.2 pts, 32.2% of untyped | +30.2 pts, 41.8% of untyped |
| zarr               | mega+dev    |             21.7% |         59.7% |            62.2% |                  63.5% | +38.0 pts, 48.5% of untyped | +41.8 pts, 53.4% of untyped |
| joblib             | mega+dev    |              0.0% |         23.5% |            31.5% |                  37.2% | +23.4 pts, 23.4% of untyped | +37.2 pts, 37.2% of untyped |
| networkx           | mega+dev    |              0.3% |         17.9% |            27.9% |                  29.3% | +17.7 pts, 17.7% of untyped | +29.0 pts, 29.1% of untyped |
| nibabel            | mega+dev    |              1.0% |         22.9% |            32.8% |                  36.6% | +21.9 pts, 22.1% of untyped | +35.7 pts, 36.0% of untyped |
| narwhals           | mega+dev    |             21.7% |         48.9% |            50.8% |                  52.1% | +27.2 pts, 34.7% of untyped | +30.4 pts, 38.9% of untyped |
| xarray             | mega+dev    |              4.6% |         25.4% |            48.5% |                  50.1% | +20.8 pts, 21.8% of untyped | +45.5 pts, 47.7% of untyped |
| litestar           | mega+dev    |             44.9% |         63.7% |            67.2% |                  69.4% | +18.7 pts, 34.0% of untyped | +24.5 pts, 44.4% of untyped |
| stripe             | mega+dev    |             89.5% |         92.0% |            92.5% |                  94.1% |  +2.4 pts, 23.3% of untyped |  +4.5 pts, 43.3% of untyped |
| celery             | mega+dev    |              0.4% |         13.9% |            17.4% |                  23.8% | +13.5 pts, 13.6% of untyped | +23.4 pts, 23.5% of untyped |
| optuna             | mega+dev    |              7.5% |         48.2% |            53.9% |                  56.6% | +40.8 pts, 44.1% of untyped | +49.1 pts, 53.1% of untyped |
| dask               | mega+dev    |              1.1% |         14.4% |            22.7% |                  26.5% | +13.4 pts, 13.5% of untyped | +25.4 pts, 25.7% of untyped |
| mypy               | mega+dev    |             16.8% |         58.9% |            68.2% |                  71.5% | +42.2 pts, 50.7% of untyped | +54.7 pts, 65.8% of untyped |
| **Total**          | mega+dev    |             11.0% |         35.2% |            46.2% |                  51.2% | +24.2 pts, 27.2% of untyped | +40.2 pts, 45.2% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,413 |  37,413 |        |        |      0 |    0 | 38,742 |  115,001 |    69.2 |
| standard library   | likely             | 44,418 |  37,689 |  6,729 |        |      0 |    0 | 45,747 |  115,001 |   117.2 |
| standard library   | unsafe             | 51,679 |  37,420 |  6,709 |  7,550 |      0 |    0 | 53,008 |  115,001 |   102.5 |
| standard library   | infer-basedpyright | 59,380 |  37,423 |  7,121 | 14,836 |      0 |    4 | 60,709 |  115,001 |   734.3 |
| standard library   | infer-ty           | 57,518 |  37,452 |  7,080 | 12,986 |      0 |   10 | 58,847 |  115,001 |   197.8 |
| standard library   | infer-pyrefly      | 59,792 |  37,412 |  7,177 | 15,203 |      0 |    9 | 61,121 |  115,001 |   169.9 |
| django             | certain            |  2,625 |   2,625 |        |        |      0 |    0 |  2,630 |   17,181 |    14.7 |
| django             | likely             |  3,360 |   2,630 |    730 |        |      0 |    0 |  3,365 |   17,181 |    15.2 |
| django             | unsafe             |  5,517 |   2,625 |    728 |  2,164 |      0 |    0 |  5,522 |   17,181 |    30.2 |
| django             | infer-basedpyright |  5,910 |   2,619 |    741 |  2,550 |      0 |    0 |  5,915 |   17,181 |   104.3 |
| django             | infer-ty           |  5,728 |   2,626 |    736 |  2,366 |      0 |    0 |  5,733 |   17,181 |    68.2 |
| django             | infer-pyrefly      |  6,182 |   2,614 |    748 |  2,820 |      0 |    3 |  6,187 |   17,181 |    47.2 |
| django             | infer-trace        |  6,058 |   2,625 |    758 |  2,675 |      0 |    0 |  6,063 |   17,181 |    18.1 |
| sqlalchemy         | certain            |  2,146 |   2,146 |        |        |      0 |    0 |  4,481 |   15,304 |    14.4 |
| sqlalchemy         | likely             |  2,592 |   2,154 |    438 |        |      0 |    0 |  4,927 |   15,304 |    24.6 |
| sqlalchemy         | unsafe             |  3,299 |   2,146 |    438 |    715 |      0 |    0 |  5,634 |   15,304 |    34.1 |
| sqlalchemy         | infer-basedpyright |  4,019 |   2,148 |    476 |  1,395 |      0 |    0 |  6,354 |   15,304 |    96.7 |
| sqlalchemy         | infer-ty           |  3,962 |   2,148 |    465 |  1,349 |      0 |    0 |  6,297 |   15,304 |    54.8 |
| sqlalchemy         | infer-pyrefly      |  4,284 |   2,147 |    478 |  1,659 |      0 |    0 |  6,619 |   15,304 |    38.8 |
| sqlalchemy         | infer-trace        |  3,453 |   2,146 |    438 |    869 |      0 |    0 |  5,788 |   15,304 |    12.7 |
| pydantic           | certain            |  1,203 |   1,203 |        |        |      0 |    0 |  2,105 |    4,019 |     2.6 |
| pydantic           | likely             |  1,354 |   1,210 |    144 |        |      0 |    0 |  2,256 |    4,019 |     3.2 |
| pydantic           | unsafe             |  1,617 |   1,203 |    143 |    271 |      0 |    0 |  2,519 |    4,019 |     4.4 |
| pydantic           | infer-basedpyright |  1,835 |   1,204 |    146 |    485 |      0 |    0 |  2,737 |    4,019 |    47.6 |
| pydantic           | infer-ty           |  1,784 |   1,204 |    143 |    437 |      0 |    0 |  2,686 |    4,019 |    15.4 |
| pydantic           | infer-pyrefly      |  1,867 |   1,204 |    144 |    519 |      0 |    0 |  2,769 |    4,019 |    15.2 |
| pydantic           | infer-trace        |  1,618 |   1,203 |    143 |    272 |      0 |    0 |  2,520 |    4,019 |     5.5 |
| pandas             | certain            | 17,867 |  17,867 |        |        |      0 |    0 | 19,136 |   79,062 |    81.2 |
| pandas             | likely             | 42,201 |  18,089 | 24,112 |        |      0 |    0 | 43,470 |   79,062 |   185.2 |
| pandas             | unsafe             | 43,351 |  17,865 | 24,083 |  1,403 |      0 |    0 | 44,620 |   79,062 |   168.3 |
| pandas             | infer-basedpyright | 48,922 |  17,861 | 24,078 |  6,983 |      0 |    0 | 50,191 |   79,062 |   521.8 |
| pandas             | infer-ty           | 48,686 |  17,873 | 24,091 |  6,722 |      0 |    3 | 49,955 |   79,062 |   325.3 |
| pandas             | infer-pyrefly      | 51,231 |  17,859 | 24,031 |  9,341 |      0 |    3 | 52,500 |   79,062 |   197.9 |
| pandas             | infer-trace        | 44,781 |  17,868 | 23,954 |  2,959 |      0 |    0 | 46,050 |   79,062 |   126.1 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     6.6 |
| twisted            | likely             |  6,177 |   2,453 |  3,724 |        |      0 |    0 |  6,177 |   17,874 |    12.9 |
| twisted            | unsafe             |  7,265 |   2,434 |  3,724 |  1,107 |      0 |    0 |  7,265 |   17,874 |    11.1 |
| twisted            | infer-basedpyright |  8,599 |   2,435 |  3,739 |  2,425 |      0 |    0 |  8,599 |   17,874 |    88.1 |
| twisted            | infer-ty           |  7,647 |   2,434 |  3,735 |  1,478 |      0 |    0 |  7,647 |   17,874 |    39.9 |
| twisted            | infer-pyrefly      |  8,465 |   2,434 |  3,744 |  2,287 |      0 |    0 |  8,465 |   17,874 |    35.8 |
| pip                | certain            |  2,243 |   2,243 |        |        |      0 |    0 |  2,380 |    9,064 |     7.0 |
| pip                | likely             |  2,738 |   2,250 |    488 |        |      0 |    0 |  2,875 |    9,064 |     8.6 |
| pip                | unsafe             |  3,589 |   2,243 |    486 |    860 |      0 |    0 |  3,726 |    9,064 |     7.9 |
| pip                | infer-basedpyright |  4,308 |   2,244 |    530 |  1,534 |      0 |    2 |  4,445 |    9,064 |    62.4 |
| pip                | infer-ty           |  3,876 |   2,244 |    501 |  1,131 |      0 |    7 |  4,013 |    9,064 |    25.9 |
| pip                | infer-pyrefly      |  4,168 |   2,242 |    518 |  1,408 |      0 |    3 |  4,305 |    9,064 |    19.9 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.6 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.8 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.6 |
| structlog          | infer-basedpyright |    150 |      98 |     16 |     36 |      0 |    0 |    259 |      425 |     7.0 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     2.0 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     2.3 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.9 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.9 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     2.0 |
| attrs              | unsafe             |    107 |      93 |      8 |      6 |      0 |    0 |    110 |      396 |     1.4 |
| attrs              | infer-basedpyright |    126 |      93 |      8 |     25 |      0 |    0 |    129 |      396 |     9.9 |
| attrs              | infer-ty           |    118 |      93 |      8 |     17 |      0 |    0 |    121 |      396 |     4.3 |
| attrs              | infer-pyrefly      |    123 |      93 |      8 |     22 |      0 |    0 |    126 |      396 |     4.0 |
| attrs              | infer-trace        |    110 |      93 |      9 |      8 |      0 |    0 |    113 |      396 |     1.2 |
| click              | certain            |    311 |     311 |        |        |      0 |    0 |    590 |      887 |     0.8 |
| click              | likely             |    338 |     312 |     26 |        |      0 |    0 |    617 |      887 |     2.5 |
| click              | unsafe             |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     1.6 |
| click              | infer-basedpyright |    437 |     311 |     30 |     96 |      0 |    0 |    716 |      887 |    14.1 |
| click              | infer-ty           |    453 |     311 |     28 |    114 |      0 |    0 |    732 |      887 |     2.8 |
| click              | infer-pyrefly      |    460 |     311 |     31 |    118 |      0 |    0 |    739 |      887 |     2.5 |
| click              | infer-trace        |    375 |     311 |     26 |     38 |      0 |    0 |    654 |      887 |     2.2 |
| hypercorn          | certain            |    137 |     137 |        |        |      0 |    0 |    307 |      525 |     0.9 |
| hypercorn          | likely             |    157 |     137 |     20 |        |      0 |    0 |    327 |      525 |     1.8 |
| hypercorn          | unsafe             |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     1.9 |
| hypercorn          | infer-basedpyright |    222 |     137 |     21 |     64 |      0 |    0 |    392 |      525 |     9.9 |
| hypercorn          | infer-ty           |    231 |     137 |     21 |     73 |      0 |    0 |    401 |      525 |     4.1 |
| hypercorn          | infer-pyrefly      |    247 |     138 |     26 |     83 |      0 |    0 |    417 |      525 |     3.1 |
| hypercorn          | infer-trace        |    195 |     137 |     20 |     38 |      0 |    0 |    365 |      525 |     1.5 |
| starlette          | certain            |    322 |     322 |        |        |      0 |    0 |    407 |      829 |     0.7 |
| starlette          | likely             |    398 |     323 |     75 |        |      0 |    0 |    483 |      829 |     1.2 |
| starlette          | unsafe             |    439 |     322 |     75 |     42 |      0 |    0 |    524 |      829 |     1.5 |
| starlette          | infer-basedpyright |    522 |     322 |     74 |    126 |      0 |    0 |    607 |      829 |    12.5 |
| starlette          | infer-ty           |    508 |     322 |     74 |    112 |      0 |    0 |    593 |      829 |     5.4 |
| starlette          | infer-pyrefly      |    510 |     322 |     74 |    114 |      0 |    0 |    595 |      829 |     2.4 |
| starlette          | infer-trace        |    439 |     322 |     75 |     42 |      0 |    0 |    524 |      829 |     2.4 |
| werkzeug           | certain            |    545 |     545 |        |        |      0 |    0 |    761 |    1,509 |     1.3 |
| werkzeug           | likely             |    617 |     546 |     71 |        |      0 |    0 |    833 |    1,509 |     1.6 |
| werkzeug           | unsafe             |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     1.8 |
| werkzeug           | infer-basedpyright |    798 |     545 |     82 |    171 |      0 |    0 |  1,014 |    1,509 |     8.6 |
| werkzeug           | infer-ty           |    824 |     545 |     84 |    195 |      0 |    0 |  1,040 |    1,509 |     4.2 |
| werkzeug           | infer-pyrefly      |    880 |     546 |     82 |    252 |      0 |    0 |  1,096 |    1,509 |     3.1 |
| werkzeug           | infer-trace        |    683 |     545 |     71 |     67 |      0 |    0 |    899 |    1,509 |     2.3 |
| mkdocs             | certain            |    826 |     826 |        |        |      0 |    0 |    937 |    2,443 |     1.4 |
| mkdocs             | likely             |  1,256 |     858 |    398 |        |      0 |    0 |  1,367 |    2,443 |     2.4 |
| mkdocs             | unsafe             |  1,378 |     826 |    398 |    154 |      0 |    0 |  1,489 |    2,443 |     2.2 |
| mkdocs             | infer-basedpyright |  1,474 |     826 |    405 |    243 |      0 |    0 |  1,585 |    2,443 |    10.9 |
| mkdocs             | infer-ty           |  1,501 |     826 |    410 |    265 |      0 |    0 |  1,612 |    2,443 |     5.0 |
| mkdocs             | infer-pyrefly      |  1,559 |     826 |    413 |    320 |      0 |    0 |  1,670 |    2,443 |     4.7 |
| mkdocs             | infer-trace        |  1,390 |     827 |    398 |    165 |      0 |    0 |  1,501 |    2,443 |     3.5 |
| httpx              | certain            |    240 |     240 |        |        |      0 |    0 |    278 |      607 |     1.1 |
| httpx              | likely             |    309 |     250 |     59 |        |      0 |    0 |    347 |      607 |     1.2 |
| httpx              | unsafe             |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     1.0 |
| httpx              | infer-basedpyright |    411 |     240 |     64 |    107 |      0 |    0 |    449 |      607 |     8.5 |
| httpx              | infer-ty           |    394 |     241 |     63 |     90 |      0 |    0 |    432 |      607 |     4.1 |
| httpx              | infer-pyrefly      |    408 |     241 |     64 |    103 |      0 |    0 |    446 |      607 |     2.1 |
| httpx              | infer-trace        |    324 |     240 |     59 |     25 |      0 |    0 |    362 |      607 |     1.5 |
| black              | certain            |    714 |     714 |        |        |      0 |    0 |    954 |    1,513 |     0.9 |
| black              | likely             |    842 |     727 |    115 |        |      0 |    0 |  1,082 |    1,513 |     1.2 |
| black              | unsafe             |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     1.4 |
| black              | infer-basedpyright |  1,042 |     714 |    121 |    207 |      0 |    0 |  1,282 |    1,513 |    12.4 |
| black              | infer-ty           |  1,072 |     714 |    121 |    237 |      0 |    0 |  1,312 |    1,513 |     4.0 |
| black              | infer-pyrefly      |  1,084 |     714 |    119 |    251 |      0 |    0 |  1,324 |    1,513 |     2.5 |
| black              | infer-trace        |    883 |     714 |    115 |     54 |      0 |    0 |  1,123 |    1,513 |     2.9 |
| fastapi            | certain            |    265 |     265 |        |        |      0 |    0 |    802 |    1,279 |     2.1 |
| fastapi            | likely             |    310 |     271 |     39 |        |      0 |    0 |    847 |    1,279 |     4.3 |
| fastapi            | unsafe             |    336 |     265 |     39 |     32 |      0 |    0 |    873 |    1,279 |     2.3 |
| fastapi            | infer-basedpyright |    379 |     265 |     38 |     76 |      0 |    0 |    916 |    1,279 |    11.8 |
| fastapi            | infer-ty           |    379 |     265 |     37 |     77 |      0 |    0 |    916 |    1,279 |     9.3 |
| fastapi            | infer-pyrefly      |    402 |     265 |     40 |     97 |      0 |    0 |    939 |    1,279 |     6.9 |
| fastapi            | infer-trace        |    336 |     265 |     39 |     32 |      0 |    0 |    873 |    1,279 |     2.8 |
| cattrs             | certain            |    114 |     114 |        |        |      0 |    0 |    153 |      559 |     0.7 |
| cattrs             | likely             |    149 |     121 |     28 |        |      0 |    0 |    188 |      559 |     1.6 |
| cattrs             | unsafe             |    167 |     117 |     27 |     23 |      0 |    0 |    206 |      559 |     1.3 |
| cattrs             | infer-basedpyright |    200 |     116 |     30 |     54 |      0 |    0 |    239 |      559 |     8.5 |
| cattrs             | infer-ty           |    203 |     114 |     28 |     61 |      0 |    0 |    242 |      559 |     4.1 |
| cattrs             | infer-pyrefly      |    211 |     114 |     32 |     65 |      0 |    0 |    250 |      559 |     3.6 |
| cattrs             | infer-trace        |    167 |     117 |     27 |     23 |      0 |    0 |    206 |      559 |     0.8 |
| pytest             | certain            |  1,376 |   1,376 |        |        |      0 |    0 |  1,791 |    3,418 |     2.0 |
| pytest             | likely             |  1,536 |   1,381 |    155 |        |      0 |    0 |  1,951 |    3,418 |     5.8 |
| pytest             | unsafe             |  1,689 |   1,376 |    155 |    158 |      0 |    0 |  2,104 |    3,418 |     3.5 |
| pytest             | infer-basedpyright |  2,020 |   1,376 |    173 |    471 |      0 |    0 |  2,435 |    3,418 |    23.3 |
| pytest             | infer-ty           |  2,027 |   1,376 |    175 |    476 |      0 |    0 |  2,442 |    3,418 |     7.4 |
| pytest             | infer-pyrefly      |  2,097 |   1,376 |    177 |    544 |      0 |    0 |  2,512 |    3,418 |     7.6 |
| pytest             | infer-trace        |  1,706 |   1,376 |    155 |    175 |      0 |    0 |  2,121 |    3,418 |     3.3 |
| botocore           | certain            |    548 |     548 |        |        |      0 |    0 |    566 |    3,806 |     2.5 |
| botocore           | likely             |    731 |     550 |    181 |        |      0 |    0 |    749 |    3,806 |     3.5 |
| botocore           | unsafe             |  1,204 |     546 |    179 |    479 |      0 |    0 |  1,222 |    3,806 |     7.3 |
| botocore           | infer-basedpyright |  1,339 |     541 |    178 |    620 |      0 |    0 |  1,357 |    3,806 |    26.7 |
| botocore           | infer-ty           |  1,261 |     546 |    180 |    535 |      0 |    0 |  1,279 |    3,806 |    12.0 |
| botocore           | infer-pyrefly      |  1,325 |     541 |    176 |    608 |      0 |    0 |  1,343 |    3,806 |    11.8 |
| botocore           | infer-trace        |  1,537 |     546 |    200 |    791 |      0 |    0 |  1,555 |    3,806 |     7.3 |
| uvicorn            | certain            |    236 |     236 |        |        |      0 |    0 |    387 |      640 |     0.7 |
| uvicorn            | likely             |    268 |     236 |     32 |        |      0 |    0 |    419 |      640 |     1.2 |
| uvicorn            | unsafe             |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     2.3 |
| uvicorn            | infer-basedpyright |    378 |     236 |     35 |    107 |      0 |    0 |    529 |      640 |     9.7 |
| uvicorn            | infer-ty           |    362 |     237 |     32 |     93 |      0 |    0 |    513 |      640 |     2.2 |
| uvicorn            | infer-pyrefly      |    383 |     237 |     35 |    111 |      0 |    0 |    534 |      640 |     4.6 |
| uvicorn            | infer-trace        |    293 |     236 |     32 |     25 |      0 |    0 |    444 |      640 |     2.9 |
| mcp                | certain            |    720 |     720 |        |        |      0 |    0 |  1,483 |    2,483 |     6.2 |
| mcp                | likely             |    882 |     726 |    156 |        |      0 |    0 |  1,645 |    2,483 |     2.9 |
| mcp                | unsafe             |    968 |     720 |    156 |     92 |      0 |    0 |  1,731 |    2,483 |     5.9 |
| mcp                | infer-basedpyright |  1,170 |     721 |    164 |    285 |      0 |    0 |  1,933 |    2,483 |    17.7 |
| mcp                | infer-ty           |  1,165 |     721 |    163 |    281 |      0 |    0 |  1,928 |    2,483 |     9.4 |
| mcp                | infer-pyrefly      |  1,211 |     721 |    159 |    331 |      0 |    0 |  1,974 |    2,483 |     8.0 |
| mcp                | infer-trace        |    968 |     720 |    156 |     92 |      0 |    0 |  1,731 |    2,483 |     2.8 |
| requests           | certain            |     96 |      96 |        |        |      0 |    0 |    256 |      559 |     0.7 |
| requests           | likely             |    105 |      96 |      9 |        |      0 |    0 |    265 |      559 |     1.0 |
| requests           | unsafe             |    113 |      96 |      9 |      8 |      0 |    0 |    273 |      559 |     0.8 |
| requests           | infer-basedpyright |    221 |      96 |     16 |    109 |      0 |    0 |    381 |      559 |     2.2 |
| requests           | infer-ty           |    223 |      96 |     13 |    114 |      0 |    0 |    383 |      559 |     2.6 |
| requests           | infer-pyrefly      |    242 |      96 |     15 |    131 |      0 |    0 |    402 |      559 |     1.1 |
| requests           | infer-trace        |    113 |      96 |      9 |      8 |      0 |    0 |    273 |      559 |     1.8 |
| rich               | certain            |  1,022 |   1,022 |        |        |      0 |    0 |  1,360 |    2,516 |     1.2 |
| rich               | likely             |  1,328 |   1,033 |    295 |        |      0 |    0 |  1,666 |    2,516 |     2.3 |
| rich               | unsafe             |  1,455 |   1,022 |    293 |    140 |      0 |    0 |  1,793 |    2,516 |     1.6 |
| rich               | infer-basedpyright |  1,773 |   1,022 |    296 |    455 |      0 |    0 |  2,111 |    2,516 |     4.0 |
| rich               | infer-ty           |  1,737 |   1,022 |    305 |    410 |      0 |    0 |  2,075 |    2,516 |     3.3 |
| rich               | infer-pyrefly      |  1,823 |   1,022 |    311 |    490 |      0 |    0 |  2,161 |    2,516 |     2.7 |
| rich               | infer-trace        |  1,455 |   1,022 |    293 |    140 |      0 |    0 |  1,793 |    2,516 |     2.7 |
| urllib3            | certain            |    259 |     259 |        |        |      0 |    0 |    480 |      855 |     0.8 |
| urllib3            | likely             |    301 |     261 |     40 |        |      0 |    0 |    522 |      855 |     1.3 |
| urllib3            | unsafe             |    338 |     259 |     40 |     39 |      0 |    0 |    559 |      855 |     2.2 |
| urllib3            | infer-basedpyright |    414 |     259 |     40 |    115 |      0 |    0 |    635 |      855 |     1.9 |
| urllib3            | infer-ty           |    419 |     259 |     40 |    120 |      0 |    0 |    640 |      855 |     3.2 |
| urllib3            | infer-pyrefly      |    434 |     259 |     40 |    135 |      0 |    0 |    655 |      855 |     3.5 |
| urllib3            | infer-trace        |    338 |     259 |     40 |     39 |      0 |    0 |    559 |      855 |     1.8 |
| sqlmodel           | certain            |     11 |      11 |        |        |      0 |    0 |     50 |      164 |     0.9 |
| sqlmodel           | likely             |     16 |      11 |      5 |        |      0 |    0 |     55 |      164 |     1.3 |
| sqlmodel           | unsafe             |     21 |      11 |      5 |      5 |      0 |    0 |     60 |      164 |     2.3 |
| sqlmodel           | infer-basedpyright |     23 |      11 |      5 |      7 |      0 |    0 |     62 |      164 |     1.7 |
| sqlmodel           | infer-ty           |     23 |      11 |      5 |      7 |      0 |    0 |     62 |      164 |     1.6 |
| sqlmodel           | infer-pyrefly      |     30 |      11 |      5 |     14 |      0 |    0 |     69 |      164 |     2.3 |
| sqlmodel           | infer-trace        |     21 |      11 |      5 |      5 |      0 |    0 |     60 |      164 |     2.6 |
| marshmallow        | certain            |     51 |      51 |        |        |      0 |    0 |    127 |      378 |     0.5 |
| marshmallow        | likely             |     56 |      51 |      5 |        |      0 |    0 |    132 |      378 |     1.9 |
| marshmallow        | unsafe             |    103 |      51 |      5 |     47 |      0 |    0 |    179 |      378 |     2.5 |
| marshmallow        | infer-basedpyright |    119 |      51 |      5 |     63 |      0 |    0 |    195 |      378 |     1.9 |
| marshmallow        | infer-ty           |    118 |      51 |      5 |     62 |      0 |    0 |    194 |      378 |     3.5 |
| marshmallow        | infer-pyrefly      |    125 |      51 |      5 |     69 |      0 |    0 |    201 |      378 |     2.5 |
| marshmallow        | infer-trace        |    103 |      51 |      5 |     47 |      0 |    0 |    179 |      378 |     1.1 |
| textual            | certain            |  2,800 |   2,800 |        |        |      0 |    0 |  3,994 |    7,677 |     3.0 |
| textual            | likely             |  3,307 |   2,823 |    484 |        |      0 |    0 |  4,501 |    7,677 |     4.9 |
| textual            | unsafe             |  3,574 |   2,800 |    483 |    291 |      0 |    0 |  4,768 |    7,677 |     4.5 |
| textual            | infer-basedpyright |  4,689 |   2,800 |    557 |  1,332 |      0 |    0 |  5,883 |    7,677 |    24.6 |
| textual            | infer-ty           |  4,824 |   2,800 |    565 |  1,459 |      0 |    0 |  6,018 |    7,677 |    20.0 |
| textual            | infer-pyrefly      |  4,935 |   2,800 |    565 |  1,570 |      0 |    0 |  6,129 |    7,677 |    13.7 |
| pdm                | certain            |  1,246 |   1,246 |        |        |      0 |    0 |  1,607 |    3,079 |     3.1 |
| pdm                | likely             |  1,464 |   1,262 |    202 |        |      0 |    0 |  1,825 |    3,079 |     6.8 |
| pdm                | unsafe             |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |    11.5 |
| pdm                | infer-basedpyright |  1,940 |   1,251 |    217 |    472 |      0 |    0 |  2,301 |    3,079 |    22.5 |
| pdm                | infer-ty           |  1,985 |   1,251 |    220 |    514 |      0 |    0 |  2,346 |    3,079 |    10.2 |
| pdm                | infer-pyrefly      |  2,045 |   1,251 |    224 |    570 |      0 |    0 |  2,406 |    3,079 |     9.8 |
| pdm                | infer-trace        |  1,610 |   1,246 |    201 |    163 |      0 |    0 |  1,971 |    3,079 |     7.1 |
| strawberry-graphql | certain            |    657 |     657 |        |        |      0 |    0 |  1,433 |    2,582 |     3.1 |
| strawberry-graphql | likely             |    831 |     659 |    172 |        |      0 |    0 |  1,607 |    2,582 |     4.7 |
| strawberry-graphql | unsafe             |    898 |     657 |    172 |     69 |      0 |    0 |  1,674 |    2,582 |     4.5 |
| strawberry-graphql | infer-basedpyright |  1,043 |     659 |    174 |    210 |      0 |    0 |  1,819 |    2,582 |    26.9 |
| strawberry-graphql | infer-ty           |  1,046 |     659 |    173 |    214 |      0 |    0 |  1,822 |    2,582 |    11.5 |
| strawberry-graphql | infer-pyrefly      |  1,045 |     658 |    171 |    216 |      0 |    0 |  1,821 |    2,582 |    18.1 |
| strawberry-graphql | infer-trace        |    898 |     657 |    172 |     69 |      0 |    0 |  1,674 |    2,582 |     3.1 |
| pygments           | certain            |    736 |     736 |        |        |      0 |    0 |    736 |    7,666 |     3.8 |
| pygments           | likely             |    817 |     739 |     78 |        |      0 |    0 |    817 |    7,666 |     4.5 |
| pygments           | unsafe             |  5,353 |     736 |     78 |  4,539 |      0 |    0 |  5,353 |    7,666 |     6.0 |
| pygments           | infer-basedpyright |  5,446 |     736 |     85 |  4,625 |      0 |    0 |  5,446 |    7,666 |    44.5 |
| pygments           | infer-ty           |  5,450 |     736 |     85 |  4,629 |      0 |    0 |  5,450 |    7,666 |    16.0 |
| pygments           | infer-pyrefly      |  5,514 |     736 |     85 |  4,693 |      0 |    1 |  5,514 |    7,666 |    17.0 |
| pygments           | infer-trace        |  5,461 |     731 |    103 |  4,627 |      0 |    0 |  5,461 |    7,666 |     8.6 |
| streamlink         | certain            |    701 |     701 |        |        |      0 |    0 |  2,963 |    5,291 |     2.3 |
| streamlink         | likely             |    839 |     704 |    135 |        |      0 |    0 |  3,101 |    5,291 |     3.5 |
| streamlink         | unsafe             |  1,280 |     701 |    135 |    444 |      0 |    0 |  3,542 |    5,291 |     5.5 |
| streamlink         | infer-basedpyright |  1,627 |     704 |    156 |    767 |      0 |    0 |  3,889 |    5,291 |    21.0 |
| streamlink         | infer-ty           |  1,523 |     703 |    151 |    669 |      0 |    0 |  3,785 |    5,291 |    11.2 |
| streamlink         | infer-pyrefly      |  1,555 |     704 |    153 |    698 |      0 |    0 |  3,817 |    5,291 |     9.0 |
| streamlink         | infer-trace        |  1,288 |     701 |    135 |    452 |      0 |    0 |  3,550 |    5,291 |     6.7 |
| sphinx             | certain            |  3,392 |   3,392 |        |        |      0 |    0 |  4,320 |    8,901 |     4.3 |
| sphinx             | likely             |  3,931 |   3,407 |    524 |        |      0 |    0 |  4,859 |    8,901 |     6.2 |
| sphinx             | unsafe             |  4,335 |   3,392 |    523 |    420 |      0 |    0 |  5,263 |    8,901 |     7.0 |
| sphinx             | infer-basedpyright |  5,091 |   3,393 |    551 |  1,147 |      0 |    0 |  6,019 |    8,901 |    47.4 |
| sphinx             | infer-ty           |  5,204 |   3,392 |    550 |  1,262 |      0 |    0 |  6,132 |    8,901 |    16.9 |
| sphinx             | infer-pyrefly      |  5,325 |   3,393 |    554 |  1,378 |      0 |    0 |  6,253 |    8,901 |    13.5 |
| sphinx             | infer-trace        |  4,335 |   3,392 |    523 |    420 |      0 |    0 |  5,263 |    8,901 |     5.7 |
| tox                | certain            |    985 |     985 |        |        |      0 |    0 |  1,321 |    2,098 |     1.6 |
| tox                | likely             |  1,088 |     986 |    102 |        |      0 |    0 |  1,424 |    2,098 |     2.1 |
| tox                | unsafe             |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     3.4 |
| tox                | infer-basedpyright |  1,357 |     987 |    118 |    252 |      0 |    0 |  1,693 |    2,098 |    13.1 |
| tox                | infer-ty           |  1,390 |     987 |    117 |    286 |      0 |    0 |  1,726 |    2,098 |     4.0 |
| tox                | infer-pyrefly      |  1,431 |     987 |    117 |    327 |      0 |    0 |  1,767 |    2,098 |     5.8 |
| tox                | infer-trace        |  1,143 |     985 |    102 |     56 |      0 |    0 |  1,479 |    2,098 |     1.8 |
| trio               | certain            |  1,106 |   1,106 |        |        |      0 |    0 |  1,637 |    3,531 |     2.5 |
| trio               | likely             |  1,377 |   1,110 |    267 |        |      0 |    0 |  1,908 |    3,531 |     4.7 |
| trio               | unsafe             |  1,438 |   1,106 |    267 |     65 |      0 |    0 |  1,969 |    3,531 |     5.6 |
| trio               | infer-basedpyright |  1,696 |   1,107 |    273 |    316 |      0 |    0 |  2,227 |    3,531 |     6.4 |
| trio               | infer-ty           |  1,822 |   1,107 |    273 |    442 |      0 |    0 |  2,353 |    3,531 |     9.3 |
| trio               | infer-pyrefly      |  1,927 |   1,107 |    274 |    546 |      0 |    0 |  2,458 |    3,531 |     5.0 |
| trio               | infer-trace        |  1,438 |   1,106 |    267 |     65 |      0 |    0 |  1,969 |    3,531 |     6.6 |
| langchain-core     | certain            |  1,702 |   1,702 |        |        |      0 |    0 |  2,668 |    4,696 |     5.4 |
| langchain-core     | likely             |  1,906 |   1,706 |    200 |        |      0 |    0 |  2,872 |    4,696 |     7.6 |
| langchain-core     | unsafe             |  2,009 |   1,702 |    200 |    107 |      0 |    0 |  2,975 |    4,696 |     7.1 |
| langchain-core     | infer-basedpyright |  2,246 |   1,702 |    209 |    335 |      0 |    0 |  3,212 |    4,696 |    15.1 |
| langchain-core     | infer-ty           |  2,260 |   1,702 |    210 |    348 |      0 |    0 |  3,226 |    4,696 |    15.2 |
| langchain-core     | infer-pyrefly      |  2,354 |   1,702 |    218 |    434 |      0 |    0 |  3,320 |    4,696 |    12.1 |
| langchain-core     | infer-trace        |  2,009 |   1,702 |    200 |    107 |      0 |    0 |  2,975 |    4,696 |     5.5 |
| matplotlib         | certain            |  7,498 |   7,498 |        |        |      0 |    0 |  7,676 |   24,261 |    38.0 |
| matplotlib         | likely             |  9,605 |   7,563 |  2,042 |        |      0 |    0 |  9,783 |   24,261 |    58.9 |
| matplotlib         | unsafe             | 10,287 |   7,507 |  2,037 |    743 |      0 |    0 | 10,465 |   24,261 |    46.2 |
| matplotlib         | infer-basedpyright | 11,871 |   7,517 |  2,131 |  2,223 |      0 |    0 | 12,049 |   24,261 |    86.4 |
| matplotlib         | infer-ty           | 11,910 |   7,507 |  2,143 |  2,260 |      0 |    0 | 12,088 |   24,261 |    93.5 |
| matplotlib         | infer-pyrefly      | 12,988 |   7,503 |  2,139 |  3,346 |      0 |    1 | 13,166 |   24,261 |    92.1 |
| pint               | certain            |    650 |     650 |        |        |      0 |    0 |    815 |    3,243 |     2.5 |
| pint               | likely             |    926 |     651 |    275 |        |      0 |    0 |  1,091 |    3,243 |     4.2 |
| pint               | unsafe             |    978 |     650 |    275 |     53 |      0 |    0 |  1,143 |    3,243 |     7.4 |
| pint               | infer-basedpyright |  1,225 |     651 |    283 |    291 |      0 |    0 |  1,390 |    3,243 |    56.7 |
| pint               | infer-ty           |  1,134 |     651 |    278 |    205 |      0 |    0 |  1,299 |    3,243 |    20.1 |
| pint               | infer-pyrefly      |  1,369 |     651 |    287 |    431 |      0 |    0 |  1,534 |    3,243 |     9.1 |
| pint               | infer-trace        |    985 |     650 |    275 |     60 |      0 |    0 |  1,150 |    3,243 |     6.0 |
| altair             | certain            |    389 |     389 |        |        |      0 |    0 |  2,071 |    3,383 |     8.4 |
| altair             | likely             |    441 |     389 |     52 |        |      0 |    0 |  2,123 |    3,383 |     9.9 |
| altair             | unsafe             |    454 |     389 |     52 |     13 |      0 |    0 |  2,136 |    3,383 |    13.1 |
| altair             | infer-basedpyright |    531 |     389 |     55 |     87 |      0 |    0 |  2,213 |    3,383 |    52.4 |
| altair             | infer-ty           |    517 |     389 |     53 |     75 |      0 |    0 |  2,199 |    3,383 |    32.1 |
| altair             | infer-pyrefly      |    555 |     389 |     54 |    112 |      0 |    0 |  2,237 |    3,383 |    28.3 |
| altair             | infer-trace        |    461 |     389 |     53 |     19 |      0 |    0 |  2,143 |    3,383 |    10.6 |
| seaborn            | certain            |    658 |     658 |        |        |      0 |    0 |    873 |    3,110 |     8.0 |
| seaborn            | likely             |    822 |     665 |    157 |        |      0 |    0 |  1,037 |    3,110 |    14.4 |
| seaborn            | unsafe             |    900 |     658 |    156 |     86 |      0 |    0 |  1,115 |    3,110 |     9.4 |
| seaborn            | infer-basedpyright |  1,051 |     658 |    159 |    234 |      0 |    0 |  1,266 |    3,110 |    78.9 |
| seaborn            | infer-ty           |    989 |     657 |    158 |    174 |      0 |    0 |  1,204 |    3,110 |    45.4 |
| seaborn            | infer-pyrefly      |  1,093 |     658 |    149 |    286 |      0 |    0 |  1,308 |    3,110 |    26.5 |
| seaborn            | infer-trace        |    945 |     662 |    158 |    125 |      0 |    0 |  1,160 |    3,110 |    12.2 |
| aiohttp            | certain            |    722 |     722 |        |        |      0 |    0 |  1,298 |    2,433 |     1.9 |
| aiohttp            | likely             |    874 |     729 |    145 |        |      0 |    0 |  1,450 |    2,433 |     2.3 |
| aiohttp            | unsafe             |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     4.9 |
| aiohttp            | infer-basedpyright |  1,253 |     724 |    158 |    371 |      0 |    0 |  1,829 |    2,433 |    35.4 |
| aiohttp            | infer-ty           |  1,276 |     724 |    159 |    393 |      0 |    0 |  1,852 |    2,433 |    14.5 |
| aiohttp            | infer-pyrefly      |  1,300 |     724 |    157 |    419 |      0 |    0 |  1,876 |    2,433 |     9.3 |
| aiohttp            | infer-trace        |    996 |     722 |    145 |    129 |      0 |    0 |  1,572 |    2,433 |     5.1 |
| websockets         | certain            |    362 |     362 |        |        |      0 |    0 |    489 |      918 |     0.7 |
| websockets         | likely             |    439 |     363 |     76 |        |      0 |    0 |    566 |      918 |     1.4 |
| websockets         | unsafe             |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     2.7 |
| websockets         | infer-basedpyright |    605 |     364 |     74 |    167 |      0 |    0 |    732 |      918 |    13.8 |
| websockets         | infer-ty           |    614 |     364 |     76 |    174 |      0 |    0 |    741 |      918 |     4.9 |
| websockets         | infer-pyrefly      |    605 |     364 |     76 |    165 |      0 |    0 |    732 |      918 |     6.1 |
| websockets         | infer-trace        |    492 |     362 |     76 |     54 |      0 |    0 |    619 |      918 |     5.1 |
| anyio              | certain            |    230 |     230 |        |        |      0 |    0 |    505 |      990 |     1.9 |
| anyio              | likely             |    266 |     230 |     36 |        |      0 |    0 |    541 |      990 |     2.1 |
| anyio              | unsafe             |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     5.4 |
| anyio              | infer-basedpyright |    385 |     230 |     42 |    113 |      0 |    0 |    660 |      990 |    10.5 |
| anyio              | infer-ty           |    408 |     230 |     47 |    131 |      0 |    0 |    683 |      990 |     9.8 |
| anyio              | infer-pyrefly      |    444 |     230 |     47 |    167 |      0 |    0 |    719 |      990 |     6.4 |
| anyio              | infer-trace        |    299 |     230 |     36 |     33 |      0 |    0 |    574 |      990 |     3.5 |
| zarr               | certain            |  1,169 |   1,169 |        |        |      0 |    0 |  1,837 |    3,079 |     2.3 |
| zarr               | likely             |  1,248 |   1,170 |     78 |        |      0 |    0 |  1,916 |    3,079 |     5.1 |
| zarr               | unsafe             |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     6.7 |
| zarr               | infer-basedpyright |  1,664 |   1,169 |     99 |    396 |      0 |    0 |  2,332 |    3,079 |    33.0 |
| zarr               | infer-ty           |  1,641 |   1,169 |     98 |    374 |      0 |    0 |  2,309 |    3,079 |    19.0 |
| zarr               | infer-pyrefly      |  1,753 |   1,169 |    101 |    483 |      0 |    0 |  2,421 |    3,079 |    20.4 |
| zarr               | infer-trace        |  1,287 |   1,169 |     78 |     40 |      0 |    0 |  1,955 |    3,079 |     6.5 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     2.7 |
| joblib             | likely             |    704 |     526 |    178 |        |      0 |    0 |    705 |    2,241 |     3.0 |
| joblib             | unsafe             |    833 |     524 |    176 |    133 |      0 |    0 |    834 |    2,241 |     6.4 |
| joblib             | infer-basedpyright |    946 |     524 |    179 |    243 |      0 |    0 |    947 |    2,241 |    25.7 |
| joblib             | infer-ty           |    893 |     524 |    177 |    192 |      0 |    0 |    894 |    2,241 |    16.6 |
| joblib             | infer-pyrefly      |    944 |     522 |    179 |    243 |      0 |    0 |    945 |    2,241 |    10.2 |
| joblib             | infer-trace        |    845 |     524 |    178 |    143 |      0 |    0 |    846 |    2,241 |     7.2 |
| networkx           | certain            |  3,975 |   3,975 |        |        |      0 |    0 |  4,037 |   22,518 |    13.1 |
| networkx           | likely             |  6,211 |   3,989 |  2,222 |        |      0 |    0 |  6,273 |   22,518 |    28.8 |
| networkx           | unsafe             |  6,541 |   3,980 |  2,218 |    343 |      0 |    0 |  6,603 |   22,518 |    47.6 |
| networkx           | infer-basedpyright |  7,551 |   3,980 |  2,275 |  1,296 |      0 |    0 |  7,613 |   22,518 |   254.8 |
| networkx           | infer-ty           |  6,988 |   3,980 |  2,232 |    776 |      0 |    0 |  7,050 |   22,518 |    71.3 |
| networkx           | infer-pyrefly      |  7,262 |   3,977 |  2,254 |  1,031 |      0 |    0 |  7,324 |   22,518 |    90.0 |
| networkx           | infer-trace        |  6,965 |   3,980 |  2,245 |    740 |      0 |    0 |  7,027 |   22,518 |    21.3 |
| nibabel            | certain            |  1,874 |   1,874 |        |        |      0 |    0 |  1,956 |    8,550 |     4.6 |
| nibabel            | likely             |  2,719 |   1,891 |    828 |        |      0 |    0 |  2,801 |    8,550 |     9.2 |
| nibabel            | unsafe             |  3,049 |   1,874 |    824 |    351 |      0 |    0 |  3,131 |    8,550 |    10.4 |
| nibabel            | infer-basedpyright |  3,612 |   1,874 |    859 |    879 |      0 |    0 |  3,694 |    8,550 |    77.3 |
| nibabel            | infer-ty           |  3,583 |   1,874 |    880 |    829 |      0 |    0 |  3,665 |    8,550 |    53.3 |
| nibabel            | infer-pyrefly      |  4,303 |   1,872 |    895 |  1,536 |      0 |    2 |  4,385 |    8,550 |    28.2 |
| nibabel            | infer-trace        |  3,127 |   1,875 |    830 |    422 |      0 |    0 |  3,209 |    8,550 |     9.9 |
| narwhals           | certain            |  1,082 |   1,082 |        |        |      0 |    0 |  1,947 |    3,985 |     3.0 |
| narwhals           | likely             |  1,158 |   1,083 |     75 |        |      0 |    0 |  2,023 |    3,985 |    10.6 |
| narwhals           | unsafe             |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |    11.7 |
| narwhals           | infer-basedpyright |  1,740 |   1,083 |     90 |    567 |      0 |    0 |  2,605 |    3,985 |    45.3 |
| narwhals           | infer-ty           |  1,674 |   1,083 |    100 |    491 |      0 |    0 |  2,539 |    3,985 |    38.9 |
| narwhals           | infer-pyrefly      |  1,724 |   1,082 |     92 |    550 |      0 |    0 |  2,589 |    3,985 |    38.7 |
| narwhals           | infer-trace        |  1,213 |   1,082 |     75 |     56 |      0 |    0 |  2,078 |    3,985 |    11.5 |
| xarray             | certain            |  4,651 |   4,651 |        |        |      0 |    0 |  5,680 |   22,373 |    21.8 |
| xarray             | likely             |  9,829 |   4,708 |  5,121 |        |      0 |    0 | 10,858 |   22,373 |    31.4 |
| xarray             | unsafe             | 10,181 |   4,651 |  5,114 |    416 |      0 |    0 | 11,210 |   22,373 |    84.1 |
| xarray             | infer-basedpyright | 12,678 |   4,651 |  5,152 |  2,875 |      0 |    0 | 13,707 |   22,373 |   290.2 |
| xarray             | infer-ty           | 12,695 |   4,651 |  5,143 |  2,901 |      0 |    0 | 13,724 |   22,373 |   167.4 |
| xarray             | infer-pyrefly      | 13,510 |   4,652 |  5,154 |  3,704 |      0 |    0 | 14,539 |   22,373 |   116.3 |
| xarray             | infer-trace        | 10,200 |   4,651 |  5,113 |    436 |      0 |    0 | 11,229 |   22,373 |    44.6 |
| litestar           | certain            |    648 |     648 |        |        |      0 |    0 |  2,202 |    3,459 |     5.3 |
| litestar           | likely             |    772 |     650 |    122 |        |      0 |    0 |  2,326 |    3,459 |     7.7 |
| litestar           | unsafe             |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     8.2 |
| litestar           | infer-basedpyright |  1,065 |     649 |    130 |    286 |      0 |    0 |  2,619 |    3,459 |    42.6 |
| litestar           | infer-ty           |  1,075 |     648 |    133 |    294 |      0 |    0 |  2,629 |    3,459 |    21.0 |
| litestar           | infer-pyrefly      |  1,129 |     649 |    134 |    346 |      0 |    0 |  2,683 |    3,459 |    13.4 |
| litestar           | infer-trace        |    846 |     648 |    122 |     76 |      0 |    0 |  2,400 |    3,459 |     4.6 |
| stripe             | certain            |    781 |     781 |        |        |      0 |    0 | 29,531 |   32,107 |     8.5 |
| stripe             | likely             |    947 |     781 |    166 |        |      0 |    0 | 29,697 |   32,107 |     9.6 |
| stripe             | unsafe             |  1,452 |     781 |    166 |    505 |      0 |    0 | 30,202 |   32,107 |    10.7 |
| stripe             | infer-basedpyright |  2,158 |     781 |    161 |  1,216 |      0 |    0 | 30,908 |   32,107 |  1043.0 |
| stripe             | infer-ty           |  1,499 |     781 |    161 |    557 |      0 |    0 | 30,249 |   32,107 |    29.7 |
| stripe             | infer-pyrefly      |  2,191 |     781 |    161 |  1,249 |      0 |    0 | 30,941 |   32,107 |    34.4 |
| celery             | certain            |    508 |     508 |        |        |      0 |    0 |    524 |    3,764 |    11.3 |
| celery             | likely             |    640 |     510 |    130 |        |      0 |    0 |    656 |    3,764 |    22.2 |
| celery             | unsafe             |    880 |     508 |    130 |    242 |      0 |    0 |    896 |    3,764 |    31.0 |
| celery             | infer-basedpyright |  1,116 |     508 |    138 |    470 |      0 |    6 |  1,132 |    3,764 |    56.4 |
| celery             | infer-ty           |    957 |     508 |    131 |    318 |      0 |    0 |    973 |    3,764 |    24.2 |
| celery             | infer-pyrefly      |  1,107 |     508 |    131 |    468 |      0 |    0 |  1,123 |    3,764 |    29.1 |
| celery             | infer-trace        |    946 |     508 |    129 |    309 |      0 |    0 |    962 |    3,764 |    16.4 |
| optuna             | certain            |  1,585 |   1,585 |        |        |      0 |    0 |  1,876 |    3,889 |     8.8 |
| optuna             | likely             |  1,804 |   1,593 |    211 |        |      0 |    0 |  2,095 |    3,889 |    19.8 |
| optuna             | unsafe             |  1,911 |   1,585 |    211 |    115 |      0 |    0 |  2,202 |    3,889 |    57.6 |
| optuna             | infer-basedpyright |  2,244 |   1,593 |    222 |    429 |      0 |    0 |  2,535 |    3,889 |    64.0 |
| optuna             | infer-ty           |  2,275 |   1,586 |    241 |    448 |      0 |    0 |  2,566 |    3,889 |    33.5 |
| optuna             | infer-pyrefly      |  2,501 |   1,587 |    237 |    677 |      0 |    0 |  2,792 |    3,889 |    23.5 |
| optuna             | infer-trace        |  1,911 |   1,585 |    211 |    115 |      0 |    0 |  2,202 |    3,889 |     8.7 |
| dask               | certain            |  3,272 |   3,272 |        |        |      0 |    0 |  3,530 |   24,430 |    33.0 |
| dask               | likely             |  5,296 |   3,315 |  1,981 |        |      0 |    0 |  5,554 |   24,430 |    58.9 |
| dask               | unsafe             |  6,216 |   3,280 |  1,978 |    958 |      0 |    0 |  6,474 |   24,430 |    77.4 |
| dask               | infer-basedpyright |  6,976 |   3,279 |  1,993 |  1,704 |      0 |    5 |  7,234 |   24,430 |   191.9 |
| dask               | infer-ty           |  6,617 |   3,280 |  1,994 |  1,343 |      0 |    0 |  6,875 |   24,430 |   134.1 |
| dask               | infer-pyrefly      |  7,508 |   3,284 |  1,985 |  2,239 |      0 |    5 |  7,766 |   24,430 |    95.1 |
| dask               | infer-trace        |  6,380 |   3,277 |  1,983 |  1,120 |      0 |    0 |  6,638 |   24,430 |    28.3 |
| mypy               | certain            |  5,775 |   5,775 |        |        |      0 |    0 |  8,075 |   13,701 |     4.9 |
| mypy               | likely             |  7,049 |   5,805 |  1,244 |        |      0 |    0 |  9,349 |   13,701 |    12.2 |
| mypy               | unsafe             |  7,498 |   5,775 |  1,242 |    481 |      0 |    0 |  9,797 |   13,701 |    10.2 |
| mypy               | infer-basedpyright |  9,140 |   5,777 |  1,359 |  2,004 |      0 |    0 | 11,438 |   13,701 |    69.8 |
| mypy               | infer-ty           |  9,445 |   5,776 |  1,363 |  2,306 |      0 |    0 | 11,743 |   13,701 |    32.5 |
| mypy               | infer-pyrefly      |  9,663 |   5,773 |  1,368 |  2,522 |      0 |    0 | 11,961 |   13,701 |    22.2 |
| mypy               | infer-trace        |  7,498 |   5,775 |  1,242 |    481 |      0 |    0 |  9,797 |   13,701 |    13.7 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms               |  fixed | certain | likely |  guess |
| ------------------ | ------------------------ | -----: | ------: | -----: | -----: |
| certain            | literal                  | 25,394 |  25,394 |        |        |
| certain            | stdlib                   | 16,912 |  16,912 |        |        |
| certain            | call                     | 12,642 |  12,642 |        |        |
| certain            | container+literal        |  7,650 |   7,650 |        |        |
| certain            | method                   |  5,370 |   5,370 |        |        |
| certain            | builtin                  |  4,721 |   4,721 |        |        |
| certain            | loop                     |  4,331 |   4,331 |        |        |
| certain            | copy+loop                |  4,136 |   4,136 |        |        |
| certain            | call+unpack              |  3,929 |   3,929 |        |        |
| certain            | container+literal+loop   |  2,260 |   2,260 |        |        |
| certain            | literal+method           |  1,698 |   1,698 |        |        |
| certain            | open                     |  1,537 |   1,537 |        |        |
| likely             | constructor              | 40,117 |     281 | 39,836 |        |
| likely             | literal                  | 25,402 |  25,402 |        |        |
| likely             | stdlib                   | 17,012 |  17,012 |        |        |
| likely             | call                     | 13,303 |  12,656 |    647 |        |
| likely             | container+literal        |  7,650 |   7,650 |        |        |
| likely             | method                   |  7,473 |   5,413 |  2,060 |        |
| likely             | copy+loop                |  4,802 |   4,166 |    636 |        |
| likely             | builtin                  |  4,722 |   4,722 |        |        |
| likely             | loop                     |  4,335 |   4,335 |        |        |
| likely             | call+unpack              |  3,929 |   3,929 |        |        |
| likely             | container+literal+loop   |  2,260 |   2,260 |        |        |
| likely             | attribute                |  1,731 |   1,302 |    429 |        |
| unsafe             | constructor              | 40,108 |     281 | 39,827 |        |
| unsafe             | literal                  | 25,397 |  25,392 |        |      5 |
| unsafe             | stdlib                   | 17,486 |  16,914 |        |    572 |
| unsafe             | call                     | 13,288 |  12,642 |    646 |        |
| unsafe             | literal+member           |  7,962 |         |        |  7,962 |
| unsafe             | container+literal        |  7,650 |   7,650 |        |        |
| unsafe             | method                   |  7,434 |   5,374 |  2,060 |        |
| unsafe             | copy+loop                |  4,769 |   4,136 |    633 |        |
| unsafe             | builtin                  |  4,723 |   4,721 |        |      2 |
| unsafe             | loop                     |  4,331 |   4,331 |        |        |
| unsafe             | call+unpack              |  3,932 |   3,929 |        |      3 |
| unsafe             | returned                 |  3,874 |   1,206 |        |  2,668 |
| infer-basedpyright | constructor              | 40,023 |     280 | 39,743 |        |
| infer-basedpyright | checker                  | 28,831 |         |        | 28,831 |
| infer-basedpyright | literal                  | 25,399 |  25,394 |        |      5 |
| infer-basedpyright | stdlib                   | 17,605 |  16,857 |        |    748 |
| infer-basedpyright | call                     | 13,424 |  12,639 |    785 |        |
| infer-basedpyright | literal+member           |  7,961 |         |        |  7,961 |
| infer-basedpyright | method                   |  7,757 |   5,390 |  2,367 |        |
| infer-basedpyright | container+literal        |  7,652 |   7,652 |        |        |
| infer-basedpyright | copy+loop                |  5,393 |   4,137 |  1,256 |        |
| infer-basedpyright | builtin                  |  4,723 |   4,721 |        |      2 |
| infer-basedpyright | loop                     |  4,331 |   4,331 |        |        |
| infer-basedpyright | returned                 |  4,073 |   1,188 |        |  2,885 |
| infer-ty           | constructor              | 40,030 |     281 | 39,749 |        |
| infer-ty           | literal                  | 25,398 |  25,393 |        |      5 |
| infer-ty           | checker                  | 24,241 |         |        | 24,241 |
| infer-ty           | stdlib                   | 17,607 |  16,872 |        |    735 |
| infer-ty           | call                     | 13,365 |  12,640 |    725 |        |
| infer-ty           | literal+member           |  7,962 |         |        |  7,962 |
| infer-ty           | method                   |  7,716 |   5,384 |  2,332 |        |
| infer-ty           | container+literal        |  7,651 |   7,651 |        |        |
| infer-ty           | copy+loop                |  5,331 |   4,137 |  1,194 |        |
| infer-ty           | builtin                  |  4,723 |   4,721 |        |      2 |
| infer-ty           | loop                     |  4,331 |   4,331 |        |        |
| infer-ty           | returned                 |  4,030 |   1,207 |        |  2,823 |
| infer-pyrefly      | constructor              | 39,938 |     280 | 39,658 |        |
| infer-pyrefly      | checker                  | 36,862 |         |        | 36,862 |
| infer-pyrefly      | literal                  | 25,398 |  25,393 |        |      5 |
| infer-pyrefly      | stdlib                   | 17,607 |  16,857 |        |    750 |
| infer-pyrefly      | call                     | 13,369 |  12,640 |    729 |        |
| infer-pyrefly      | literal+member           |  7,961 |         |        |  7,961 |
| infer-pyrefly      | method                   |  7,780 |   5,382 |  2,398 |        |
| infer-pyrefly      | container+literal        |  7,658 |   7,658 |        |        |
| infer-pyrefly      | copy+loop                |  5,472 |   4,136 |  1,336 |        |
| infer-pyrefly      | builtin                  |  4,723 |   4,721 |        |      2 |
| infer-pyrefly      | loop                     |  4,331 |   4,331 |        |        |
| infer-pyrefly      | returned                 |  4,072 |   1,190 |        |  2,882 |
| infer-trace        | constructor              | 31,193 |      27 | 31,166 |        |
| infer-trace        | literal                  | 14,613 |  14,611 |        |      2 |
| infer-trace        | call                     | 11,745 |  11,153 |    592 |        |
| infer-trace        | method                   |  6,139 |   4,278 |  1,861 |        |
| infer-trace        | literal+member           |  5,640 |         |        |  5,640 |
| infer-trace        | stdlib                   |  4,445 |   4,225 |        |    220 |
| infer-trace        | container+literal        |  4,436 |   4,436 |        |        |
| infer-trace        | traced                   |  3,194 |         |        |  3,194 |
| infer-trace        | copy+loop                |  3,083 |   2,675 |    408 |        |
| infer-trace        | builtin                  |  2,748 |   2,746 |        |      2 |
| infer-trace        | container+literal+member |  2,653 |         |        |  2,653 |
| infer-trace        | loop                     |  2,151 |   2,151 |        |        |
| infer-union        | constructor              | 31,048 |      27 | 31,021 |        |
| infer-union        | agreed+checker           | 18,158 |         | 18,158 |        |
| infer-union        | literal                  | 14,614 |  14,612 |        |      2 |
| infer-union        | call                     | 11,834 |  11,150 |    684 |        |
| infer-union        | checker                  |  9,698 |         |        |  9,698 |
| infer-union        | method                   |  6,422 |   4,285 |  2,137 |        |
| infer-union        | literal+member           |  5,640 |         |        |  5,640 |
| infer-union        | container+literal        |  4,443 |   4,443 |        |        |
| infer-union        | stdlib                   |  4,438 |   4,208 |        |    230 |
| infer-union        | copy+loop                |  3,536 |   2,675 |    861 |        |
| infer-union        | traced                   |  3,154 |         |        |  3,154 |
| infer-union        | builtin                  |  2,748 |   2,746 |        |      2 |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  14,257 |  62,002 |        0 |
| django             |  17,176 |   2,892 |  11,659 |        0 |
| sqlalchemy         |  12,932 |   1,153 |   9,633 |        0 |
| pydantic           |   3,117 |     414 |   1,500 |        0 |
| pandas             |  77,793 |  25,222 |  34,704 |        0 |
| twisted            |  17,874 |   4,827 |  10,612 |        0 |
| pip                |   8,923 |   1,346 |   5,334 |        0 |
| structlog          |     316 |      28 |     190 |        0 |
| attrs              |     393 |      14 |     286 |        0 |
| click              |     607 |      64 |     232 |        0 |
| hypercorn          |     355 |      58 |     160 |        0 |
| starlette          |     744 |     117 |     305 |        0 |
| werkzeug           |   1,293 |     138 |     610 |        0 |
| mkdocs             |   2,331 |     552 |     953 |        0 |
| httpx              |     569 |      84 |     245 |        0 |
| black              |   1,273 |     169 |     390 |        0 |
| fastapi            |     742 |      71 |     406 |        0 |
| cattrs             |     520 |      44 |     364 |        0 |
| pytest             |   3,000 |     313 |   1,311 |        0 |
| botocore           |   3,786 |     656 |   2,582 |        0 |
| uvicorn            |     489 |      57 |     196 |        0 |
| mcp                |   1,720 |     248 |     752 |        0 |
| requests           |     399 |      17 |     286 |        0 |
| rich               |   2,178 |     433 |     723 |        0 |
| urllib3            |     634 |      79 |     296 |        0 |
| sqlmodel           |     125 |      10 |     104 |        0 |
| marshmallow        |     302 |      52 |     199 |        0 |
| textual            |   6,483 |     774 |   2,909 |        0 |
| pdm                |   2,713 |     364 |   1,103 |        0 |
| strawberry-graphql |   1,806 |     241 |     908 |        0 |
| pygments           |   7,666 |   4,617 |   2,313 |        0 |
| streamlink         |   3,029 |     579 |   1,749 |        0 |
| sphinx             |   7,972 |     943 |   3,638 |        0 |
| tox                |   1,762 |     158 |     619 |        0 |
| trio               |   2,984 |     332 |   1,546 |        0 |
| langchain-core     |   3,730 |     307 |   1,721 |        0 |
| matplotlib         |  24,080 |   2,769 |  13,816 |        0 |
| pint               |   3,078 |     323 |   2,105 |        0 |
| altair             |   1,700 |      65 |   1,246 |        0 |
| seaborn            |   2,895 |     242 |   1,995 |        0 |
| aiohttp            |   1,857 |     274 |     861 |        0 |
| websockets         |     791 |     130 |     299 |        0 |
| anyio              |     715 |      69 |     416 |        0 |
| zarr               |   2,411 |     118 |   1,124 |        0 |
| joblib             |   2,239 |     308 |   1,406 |        0 |
| networkx           |  22,456 |   2,507 |  15,974 |        0 |
| nibabel            |   8,466 |   1,175 |   5,417 |        0 |
| narwhals           |   3,112 |     130 |   1,900 |        0 |
| xarray             |  21,344 |   5,527 |  11,166 |        0 |
| litestar           |   1,905 |     198 |   1,059 |        0 |
| stripe             |   3,357 |     671 |   1,905 |        0 |
| celery             |   3,747 |     372 |   2,867 |        0 |
| optuna             |   3,595 |     326 |   1,684 |        0 |
| dask               |  24,171 |   2,809 |  18,090 |        0 |
| mypy               |  11,401 |   1,722 |   3,905 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by | beside other steps |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: | -----------------: |
| standard library   |    4 |      139.26 |     74.03 |    1 |                       957.0 |    1001.6 | hyperfine |                yes |
| django             |    4 |       30.07 |      15.5 |    1 |                       196.6 |     209.5 | hyperfine |                yes |
| sqlalchemy         |    4 |       17.92 |      9.34 |    1 |                       170.3 |     178.4 | hyperfine |                yes |
| pydantic           |    4 |         3.0 |      1.34 |    1 |                        34.0 |      36.9 | hyperfine |                yes |
| pandas             |    4 |      220.17 |     71.35 |    1 |                      1180.8 |    1213.5 | hyperfine |                yes |
| twisted            |    4 |       16.13 |      6.14 |    1 |                       134.3 |     144.0 | hyperfine |                yes |
| pip                |    4 |       11.58 |      6.29 |    1 |                        97.0 |     103.7 | hyperfine |                yes |
| structlog          |    4 |        1.29 |      1.29 |    1 |                         5.1 |       6.4 | hyperfine |                yes |
| attrs              |    4 |         1.0 |      1.64 |    1 |                         4.1 |       5.2 | hyperfine |                yes |
| click              |    4 |        0.67 |      0.67 |    1 |                         7.5 |       8.7 | hyperfine |                yes |
| hypercorn          |    4 |        0.59 |      0.51 |    1 |                         5.9 |       7.3 | hyperfine |                yes |
| starlette          |    4 |        0.72 |      0.59 |    1 |                         7.7 |       9.3 | hyperfine |                yes |
| werkzeug           |    4 |         1.5 |      0.89 |    1 |                        14.5 |      16.1 | hyperfine |                yes |
| mkdocs             |    4 |        1.39 |      1.03 |    1 |                        17.3 |      20.0 | hyperfine |                yes |
| httpx              |    4 |        0.77 |      0.53 |    1 |                         7.5 |       8.7 | hyperfine |                yes |
| black              |    4 |        1.28 |      0.65 |    1 |                        11.6 |      13.0 | hyperfine |                yes |
| fastapi            |    4 |        1.28 |      1.13 |    1 |                        13.7 |      15.7 | hyperfine |                yes |
| cattrs             |    4 |        0.66 |      0.72 |    1 |                         7.4 |       9.1 | hyperfine |                yes |
| pytest             |    4 |        2.66 |      1.98 |    1 |                        29.1 |      31.8 | hyperfine |                yes |
| botocore           |    4 |        4.24 |      2.05 |    1 |                        39.3 |      42.1 | hyperfine |                yes |
| uvicorn            |    4 |        0.78 |       0.7 |    1 |                         8.7 |      10.3 | hyperfine |                yes |
| mcp                |    4 |        1.86 |      1.29 |    1 |                        22.5 |      25.3 | hyperfine |                yes |
| requests           |    4 |        0.43 |      0.36 |    1 |                         4.8 |       6.1 | hyperfine |                yes |
| rich               |    4 |        2.04 |      1.05 |    1 |                        24.8 |      26.5 | hyperfine |                yes |
| urllib3            |    4 |        2.15 |      1.35 |    1 |                         8.3 |       9.8 | hyperfine |                yes |
| sqlmodel           |    4 |        0.59 |      0.77 |    1 |                         6.8 |       9.7 | hyperfine |                yes |
| marshmallow        |    4 |        0.97 |      1.13 |    1 |                         3.8 |       4.9 | hyperfine |                yes |
| textual            |    4 |        6.56 |      2.85 |    1 |                        52.1 |      56.3 | hyperfine |                yes |
| pdm                |    4 |        3.94 |      2.26 |    1 |                        36.4 |      40.3 | hyperfine |                yes |
| strawberry-graphql |    4 |        3.39 |       2.2 |    1 |                        34.9 |      39.3 | hyperfine |                yes |
| pygments           |    4 |        4.84 |      2.49 |    1 |                        67.5 |      71.5 | hyperfine |                yes |
| streamlink         |    4 |         4.6 |      1.96 |    1 |                        40.8 |      43.9 | hyperfine |                yes |
| sphinx             |    4 |        9.33 |      3.33 |    1 |                        85.2 |      88.2 | hyperfine |                yes |
| tox                |    4 |        1.85 |      1.03 |    1 |                        20.3 |      21.6 | hyperfine |                yes |
| trio               |    4 |        2.96 |      1.47 |    1 |                        32.7 |      34.2 | hyperfine |                yes |
| langchain-core     |    4 |        4.46 |      2.44 |    1 |                        41.8 |      45.8 | hyperfine |                yes |
| matplotlib         |    4 |       66.92 |     36.39 |    1 |                       522.9 |     542.7 | hyperfine |                yes |
| pint               |    4 |        3.33 |       2.6 |    1 |                        36.2 |      41.4 | hyperfine |                yes |
| altair             |    4 |        6.44 |      6.89 |    1 |                        72.1 |      81.0 | hyperfine |                yes |
| seaborn            |    4 |        6.72 |      4.34 |    1 |                        63.5 |      76.0 | hyperfine |                yes |
| aiohttp            |    4 |        2.13 |      1.28 |    1 |                        24.3 |      26.3 | hyperfine |                yes |
| websockets         |    4 |        1.09 |      0.72 |    1 |                        11.0 |      13.0 | hyperfine |                yes |
| anyio              |    4 |        1.42 |      0.92 |    1 |                        12.7 |      14.4 | hyperfine |                yes |
| zarr               |    4 |        2.43 |      1.44 |    1 |                        31.2 |      34.6 | hyperfine |                yes |
| joblib             |    4 |        2.46 |      1.98 |    1 |                        28.0 |      32.1 | hyperfine |                yes |
| networkx           |    4 |       29.28 |      14.4 |    1 |                       268.4 |     268.4 | hyperfine |                yes |
| nibabel            |    4 |        7.27 |      4.12 |    1 |                        81.1 |      92.6 | hyperfine |                yes |
| narwhals           |    4 |        8.23 |      3.44 |    1 |                        66.0 |      75.6 | hyperfine |                yes |
| xarray             |    4 |       40.17 |     22.98 |    1 |                       327.6 |     346.8 | hyperfine |                yes |
| litestar           |    4 |        4.89 |      2.79 |    1 |                        42.0 |      46.7 | hyperfine |                yes |
| stripe             |    4 |       25.43 |       8.8 |    1 |                       159.1 |     164.7 | hyperfine |                yes |
| celery             |    4 |        8.67 |       8.0 |    1 |                        82.0 |      92.0 | hyperfine |                yes |
| optuna             |    4 |        7.84 |      5.82 |    1 |                        79.0 |      85.1 | hyperfine |                yes |
| dask               |    4 |       42.82 |     25.19 |    1 |                       442.5 |     462.4 | hyperfine |                yes |
| mypy               |    4 |       13.22 |      4.95 |    1 |                       123.1 |     126.3 | hyperfine |                yes |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier                |   told |   held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------------------- | -----: | -----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| django             |                     |        |        |          |                  482 |          Ran 17585 tests: FAILED (failures=5, skipped=1149, expected failures=5) |    70.9 |     64.4 |
| django             | certain             |    977 |    976 |        1 |                      |                                                                                  |         |          |
| django             | likely              |    340 |    339 |        1 |                      |                                                                                  |         |          |
| django             | guess               |    402 |    385 |       17 |                      |                                                                                  |         |          |
| django             | infer-union certain |    962 |    961 |        1 |                      |                                                                                  |         |          |
| django             | infer-union likely  |    563 |    554 |        9 |                      |                                                                                  |         |          |
| django             | infer-union guess   |    736 |    709 |       27 |                      |                                                                                  |         |          |
| sqlalchemy         |                     |        |        |          |                  152 |                                             29521 passed, 975 skipped, 1 warning |   121.6 |    127.1 |
| sqlalchemy         | certain             |  1,202 |  1,174 |       28 |                      |                                                                                  |         |          |
| sqlalchemy         | likely              |    187 |    183 |        4 |                      |                                                                                  |         |          |
| sqlalchemy         | guess               |    137 |    134 |        3 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union certain |  1,203 |  1,175 |       28 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union likely  |    574 |    556 |       18 |                      |                                                                                  |         |          |
| sqlalchemy         | infer-union guess   |    405 |    394 |       11 |                      |                                                                                  |         |          |
| pydantic           |                     |        |        |          |                    1 |                                  65 failed, 6900 passed, 350 skipped, 29 xfailed |    73.3 |     68.4 |
| pydantic           | certain             |    535 |    530 |        5 |                      |                                                                                  |         |          |
| pydantic           | likely              |     49 |     49 |        0 |                      |                                                                                  |         |          |
| pydantic           | guess               |     31 |     31 |        0 |                      |                                                                                  |         |          |
| pydantic           | infer-union certain |    535 |    530 |        5 |                      |                                                                                  |         |          |
| pydantic           | infer-union likely  |    104 |    104 |        0 |                      |                                                                                  |         |          |
| pydantic           | infer-union guess   |     99 |     99 |        0 |                      |                                                                                  |         |          |
| pandas             |                     |        |        |          |                1,555 |                            165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   131.6 |    110.6 |
| pandas             | certain             | 13,650 | 13,536 |      114 |                      |                                                                                  |         |          |
| pandas             | likely              | 20,625 | 20,550 |       75 |                      |                                                                                  |         |          |
| pandas             | guess               |    935 |    895 |       40 |                      |                                                                                  |         |          |
| pandas             | infer-union certain | 13,653 | 13,539 |      114 |                      |                                                                                  |         |          |
| pandas             | infer-union likely  | 24,708 | 24,308 |      400 |                      |                                                                                  |         |          |
| pandas             | infer-union guess   |  3,630 |  3,503 |      127 |                      |                                                                                  |         |          |
| structlog          |                     |        |        |          |                    0 |                                    24 failed, 860 passed, 37 skipped, 2 warnings |     2.0 |      2.7 |
| structlog          | certain             |     65 |     65 |        0 |                      |                                                                                  |         |          |
| structlog          | likely              |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess               |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union certain |     65 |     65 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union likely  |     16 |     16 |        0 |                      |                                                                                  |         |          |
| structlog          | infer-union guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| attrs              |                     |        |        |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.8 |      2.5 |
| attrs              | certain             |     73 |     73 |        0 |                      |                                                                                  |         |          |
| attrs              | likely              |      8 |      8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess               |      4 |      4 |        0 |                      |                                                                                  |         |          |
| attrs              | infer-union certain |     73 |     73 |        0 |                      |                                                                                  |         |          |
| attrs              | infer-union likely  |     15 |     13 |        2 |                      |                                                                                  |         |          |
| attrs              | infer-union guess   |     14 |     14 |        0 |                      |                                                                                  |         |          |
| click              |                     |        |        |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     7.5 |      8.2 |
| click              | certain             |    229 |    229 |        0 |                      |                                                                                  |         |          |
| click              | likely              |     18 |     17 |        1 |                      |                                                                                  |         |          |
| click              | guess               |     26 |     26 |        0 |                      |                                                                                  |         |          |
| click              | infer-union certain |    229 |    229 |        0 |                      |                                                                                  |         |          |
| click              | infer-union likely  |     78 |     77 |        1 |                      |                                                                                  |         |          |
| click              | infer-union guess   |     36 |     36 |        0 |                      |                                                                                  |         |          |
| hypercorn          |                     |        |        |          |                    0 |                                                             2 failed, 194 passed |     9.0 |      8.7 |
| hypercorn          | certain             |     63 |     63 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely              |     12 |     12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess               |     11 |     11 |        0 |                      |                                                                                  |         |          |
| hypercorn          | infer-union certain |     64 |     64 |        0 |                      |                                                                                  |         |          |
| hypercorn          | infer-union likely  |     33 |     32 |        1 |                      |                                                                                  |         |          |
| hypercorn          | infer-union guess   |     24 |     24 |        0 |                      |                                                                                  |         |          |
| starlette          |                     |        |        |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |    16.7 |     19.5 |
| starlette          | certain             |    201 |    200 |        1 |                      |                                                                                  |         |          |
| starlette          | likely              |     64 |     64 |        0 |                      |                                                                                  |         |          |
| starlette          | guess               |     31 |     31 |        0 |                      |                                                                                  |         |          |
| starlette          | infer-union certain |    201 |    200 |        1 |                      |                                                                                  |         |          |
| starlette          | infer-union likely  |    122 |    122 |        0 |                      |                                                                                  |         |          |
| starlette          | infer-union guess   |     62 |     62 |        0 |                      |                                                                                  |         |          |
| werkzeug           |                     |        |        |          |                    0 |                                       1 failed, 979 passed, 1 skipped, 1 warning |    12.2 |     10.6 |
| werkzeug           | certain             |    366 |    362 |        4 |                      |                                                                                  |         |          |
| werkzeug           | likely              |     49 |     49 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess               |     34 |     34 |        0 |                      |                                                                                  |         |          |
| werkzeug           | infer-union certain |    367 |    363 |        4 |                      |                                                                                  |         |          |
| werkzeug           | infer-union likely  |    134 |    134 |        0 |                      |                                                                                  |         |          |
| werkzeug           | infer-union guess   |     87 |     87 |        0 |                      |                                                                                  |         |          |
| mkdocs             |                     |        |        |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    11.2 |     10.5 |
| mkdocs             | certain             |    643 |    642 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely              |    378 |    378 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess               |    129 |    129 |        0 |                      |                                                                                  |         |          |
| mkdocs             | infer-union certain |    643 |    642 |        1 |                      |                                                                                  |         |          |
| mkdocs             | infer-union likely  |    483 |    482 |        1 |                      |                                                                                  |         |          |
| mkdocs             | infer-union guess   |    189 |    189 |        0 |                      |                                                                                  |         |          |
| httpx              |                     |        |        |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |     6.5 |     10.2 |
| httpx              | certain             |    187 |    187 |        0 |                      |                                                                                  |         |          |
| httpx              | likely              |     50 |     50 |        0 |                      |                                                                                  |         |          |
| httpx              | guess               |     16 |     16 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union certain |    188 |    188 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union likely  |    100 |    100 |        0 |                      |                                                                                  |         |          |
| httpx              | infer-union guess   |     58 |     57 |        1 |                      |                                                                                  |         |          |
| black              |                     |        |        |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |    14.8 |      5.8 |
| black              | certain             |    606 |    606 |        0 |                      |                                                                                  |         |          |
| black              | likely              |    103 |    103 |        0 |                      |                                                                                  |         |          |
| black              | guess               |     42 |     42 |        0 |                      |                                                                                  |         |          |
| black              | infer-union certain |    606 |    606 |        0 |                      |                                                                                  |         |          |
| black              | infer-union likely  |    229 |    229 |        0 |                      |                                                                                  |         |          |
| black              | infer-union guess   |    101 |    101 |        0 |                      |                                                                                  |         |          |
| fastapi            |                     |        |        |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    17.1 |     14.5 |
| fastapi            | certain             |    230 |    230 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely              |     32 |     32 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess               |     23 |     23 |        0 |                      |                                                                                  |         |          |
| fastapi            | infer-union certain |    230 |    230 |        0 |                      |                                                                                  |         |          |
| fastapi            | infer-union likely  |     82 |     81 |        1 |                      |                                                                                  |         |          |
| fastapi            | infer-union guess   |     38 |     38 |        0 |                      |                                                                                  |         |          |
| cattrs             |                     |        |        |          |                    0 |                                                           994 passed, 15 xfailed |    18.8 |     20.6 |
| cattrs             | certain             |    104 |    102 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely              |     22 |     22 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess               |     19 |     19 |        0 |                      |                                                                                  |         |          |
| cattrs             | infer-union certain |    101 |     99 |        2 |                      |                                                                                  |         |          |
| cattrs             | infer-union likely  |     64 |     60 |        4 |                      |                                                                                  |         |          |
| cattrs             | infer-union guess   |     32 |     32 |        0 |                      |                                                                                  |         |          |
| pytest             |                     |        |        |          |                   14 |              46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    83.8 |     22.3 |
| pytest             | certain             |  1,130 |  1,118 |       12 |                      |                                                                                  |         |          |
| pytest             | likely              |    125 |    125 |        0 |                      |                                                                                  |         |          |
| pytest             | guess               |    115 |    115 |        0 |                      |                                                                                  |         |          |
| pytest             | infer-union certain |  1,130 |  1,118 |       12 |                      |                                                                                  |         |          |
| pytest             | infer-union likely  |    362 |    361 |        1 |                      |                                                                                  |         |          |
| pytest             | infer-union guess   |    219 |    218 |        1 |                      |                                                                                  |         |          |
| botocore           |                     |        |        |          |                  290 |                                                7 failed, 4593 passed, 96 skipped |    33.2 |     29.1 |
| botocore           | certain             |    332 |    331 |        1 |                      |                                                                                  |         |          |
| botocore           | likely              |    148 |    148 |        0 |                      |                                                                                  |         |          |
| botocore           | guess               |    135 |    127 |        8 |                      |                                                                                  |         |          |
| botocore           | infer-union certain |    329 |    328 |        1 |                      |                                                                                  |         |          |
| botocore           | infer-union likely  |    208 |    207 |        1 |                      |                                                                                  |         |          |
| botocore           | infer-union guess   |    239 |    230 |        9 |                      |                                                                                  |         |          |
| uvicorn            |                     |        |        |          |                    0 |                                                          1350 passed, 12 skipped |    32.0 |     30.1 |
| uvicorn            | certain             |    170 |    166 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely              |     27 |     27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess               |     16 |     16 |        0 |                      |                                                                                  |         |          |
| uvicorn            | infer-union certain |    171 |    167 |        4 |                      |                                                                                  |         |          |
| uvicorn            | infer-union likely  |     86 |     83 |        3 |                      |                                                                                  |         |          |
| uvicorn            | infer-union guess   |     41 |     40 |        1 |                      |                                                                                  |         |          |
| mcp                |                     |        |        |          |                    0 |                                      3 failed, 6092 passed, 8 skipped, 1 xfailed |    18.1 |     13.7 |
| mcp                | certain             |    533 |    533 |        0 |                      |                                                                                  |         |          |
| mcp                | likely              |    135 |    134 |        1 |                      |                                                                                  |         |          |
| mcp                | guess               |     59 |     58 |        1 |                      |                                                                                  |         |          |
| mcp                | infer-union certain |    533 |    533 |        0 |                      |                                                                                  |         |          |
| mcp                | infer-union likely  |    316 |    315 |        1 |                      |                                                                                  |         |          |
| mcp                | infer-union guess   |    103 |     99 |        4 |                      |                                                                                  |         |          |
| requests           |                     |        |        |          |                    0 |                                   617 passed, 15 skipped, 1 xpassed, 18 warnings |    23.1 |     24.1 |
| requests           | certain             |     63 |     62 |        1 |                      |                                                                                  |         |          |
| requests           | likely              |      8 |      8 |        0 |                      |                                                                                  |         |          |
| requests           | guess               |      5 |      5 |        0 |                      |                                                                                  |         |          |
| requests           | infer-union certain |     63 |     62 |        1 |                      |                                                                                  |         |          |
| requests           | infer-union likely  |    106 |    106 |        0 |                      |                                                                                  |         |          |
| requests           | infer-union guess   |     21 |     21 |        0 |                      |                                                                                  |         |          |
| rich               |                     |        |        |          |                    0 |                                                           956 passed, 25 skipped |     6.8 |      6.0 |
| rich               | certain             |    810 |    810 |        0 |                      |                                                                                  |         |          |
| rich               | likely              |    148 |    147 |        1 |                      |                                                                                  |         |          |
| rich               | guess               |     71 |     71 |        0 |                      |                                                                                  |         |          |
| rich               | infer-union certain |    810 |    810 |        0 |                      |                                                                                  |         |          |
| rich               | infer-union likely  |    332 |    331 |        1 |                      |                                                                                  |         |          |
| rich               | infer-union guess   |    253 |    253 |        0 |                      |                                                                                  |         |          |
| urllib3            |                     |        |        |          |                    0 |                                 2418 passed, 288 skipped, 4 xfailed, 71 warnings |    71.4 |     54.9 |
| urllib3            | certain             |    151 |    150 |        1 |                      |                                                                                  |         |          |
| urllib3            | likely              |     32 |     31 |        1 |                      |                                                                                  |         |          |
| urllib3            | guess               |     13 |     13 |        0 |                      |                                                                                  |         |          |
| urllib3            | infer-union certain |    151 |    150 |        1 |                      |                                                                                  |         |          |
| urllib3            | infer-union likely  |     83 |     80 |        3 |                      |                                                                                  |         |          |
| urllib3            | infer-union guess   |     40 |     40 |        0 |                      |                                                                                  |         |          |
| sqlmodel           |                     |        |        |          |                    0 |                                                1 failed, 267 passed, 41 warnings |    16.1 |      7.3 |
| sqlmodel           | certain             |      6 |      6 |        0 |                      |                                                                                  |         |          |
| sqlmodel           | likely              |      4 |      4 |        0 |                      |                                                                                  |         |          |
| sqlmodel           | guess               |      1 |      1 |        0 |                      |                                                                                  |         |          |
| sqlmodel           | infer-union certain |      6 |      6 |        0 |                      |                                                                                  |         |          |
| sqlmodel           | infer-union likely  |      6 |      6 |        0 |                      |                                                                                  |         |          |
| sqlmodel           | infer-union guess   |      6 |      6 |        0 |                      |                                                                                  |         |          |
| marshmallow        |                     |        |        |          |                    0 |                                                                      1188 passed |     2.4 |      2.2 |
| marshmallow        | certain             |     35 |     34 |        1 |                      |                                                                                  |         |          |
| marshmallow        | likely              |      3 |      3 |        0 |                      |                                                                                  |         |          |
| marshmallow        | guess               |      0 |      0 |        0 |                      |                                                                                  |         |          |
| marshmallow        | infer-union certain |     35 |     34 |        1 |                      |                                                                                  |         |          |
| marshmallow        | infer-union likely  |     18 |     18 |        0 |                      |                                                                                  |         |          |
| marshmallow        | infer-union guess   |      6 |      5 |        1 |                      |                                                                                  |         |          |
| pdm                |                     |        |        |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    30.0 |     20.0 |
| pdm                | certain             |    931 |    927 |        4 |                      |                                                                                  |         |          |
| pdm                | likely              |    136 |    136 |        0 |                      |                                                                                  |         |          |
| pdm                | guess               |    100 |     99 |        1 |                      |                                                                                  |         |          |
| pdm                | infer-union certain |    932 |    928 |        4 |                      |                                                                                  |         |          |
| pdm                | infer-union likely  |    407 |    405 |        2 |                      |                                                                                  |         |          |
| pdm                | infer-union guess   |    164 |    162 |        2 |                      |                                                                                  |         |          |
| strawberry-graphql |                     |        |        |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    15.5 |     12.3 |
| strawberry-graphql | certain             |    417 |    411 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | likely              |     99 |     98 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql | guess               |     42 |     42 |        0 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union certain |    419 |    413 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union likely  |    187 |    182 |        5 |                      |                                                                                  |         |          |
| strawberry-graphql | infer-union guess   |     58 |     57 |        1 |                      |                                                                                  |         |          |
| pygments           |                     |        |        |          |                   87 |                                                          5330 passed, 16 skipped |    24.4 |     21.3 |
| pygments           | certain             |    290 |    290 |        0 |                      |                                                                                  |         |          |
| pygments           | likely              |     61 |     61 |        0 |                      |                                                                                  |         |          |
| pygments           | guess               |     90 |     90 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union certain |    285 |    285 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union likely  |    125 |    125 |        0 |                      |                                                                                  |         |          |
| pygments           | infer-union guess   |    145 |    145 |        0 |                      |                                                                                  |         |          |
| streamlink         |                     |        |        |          |                    8 |                                     15 failed, 7233 passed, 36 skipped, 9 errors |    19.7 |     21.7 |
| streamlink         | certain             |    287 |    286 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely              |     47 |     47 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess               |     46 |     46 |        0 |                      |                                                                                  |         |          |
| streamlink         | infer-union certain |    289 |    288 |        1 |                      |                                                                                  |         |          |
| streamlink         | infer-union likely  |    157 |    151 |        6 |                      |                                                                                  |         |          |
| streamlink         | infer-union guess   |    110 |    109 |        1 |                      |                                                                                  |         |          |
| sphinx             |                     |        |        |          |                    0 |                                   7 failed, 2394 passed, 23 skipped, 35 warnings |    15.2 |     18.0 |
| sphinx             | certain             |  2,125 |  2,094 |       31 |                      |                                                                                  |         |          |
| sphinx             | likely              |    426 |    425 |        1 |                      |                                                                                  |         |          |
| sphinx             | guess               |    218 |    214 |        4 |                      |                                                                                  |         |          |
| sphinx             | infer-union certain |  2,126 |  2,095 |       31 |                      |                                                                                  |         |          |
| sphinx             | infer-union likely  |    982 |    952 |       30 |                      |                                                                                  |         |          |
| sphinx             | infer-union guess   |    394 |    385 |        9 |                      |                                                                                  |         |          |
| tox                |                     |        |        |          |                    0 |                                     17 failed, 8525 passed, 31 skipped, 6 errors |    29.6 |     17.5 |
| tox                | certain             |    747 |    744 |        3 |                      |                                                                                  |         |          |
| tox                | likely              |     76 |     76 |        0 |                      |                                                                                  |         |          |
| tox                | guess               |     28 |     27 |        1 |                      |                                                                                  |         |          |
| tox                | infer-union certain |    749 |    746 |        3 |                      |                                                                                  |         |          |
| tox                | infer-union likely  |    264 |    264 |        0 |                      |                                                                                  |         |          |
| tox                | infer-union guess   |     84 |     81 |        3 |                      |                                                                                  |         |          |
| trio               |                     |        |        |          |                    0 |                                                871 passed, 23 skipped, 3 xfailed |    80.5 |     65.2 |
| trio               | certain             |    878 |    876 |        2 |                      |                                                                                  |         |          |
| trio               | likely              |    225 |    225 |        0 |                      |                                                                                  |         |          |
| trio               | guess               |     38 |     38 |        0 |                      |                                                                                  |         |          |
| trio               | infer-union certain |    879 |    877 |        2 |                      |                                                                                  |         |          |
| trio               | infer-union likely  |    546 |    544 |        2 |                      |                                                                                  |         |          |
| trio               | infer-union guess   |    156 |    152 |        4 |                      |                                                                                  |         |          |
| langchain-core     |                     |        |        |          |                    0 |              1 failed, 2409 passed, 20 skipped, 9 xfailed, 1 xpassed, 9 warnings |    10.8 |     12.0 |
| langchain-core     | certain             |  1,021 |  1,016 |        5 |                      |                                                                                  |         |          |
| langchain-core     | likely              |    141 |    141 |        0 |                      |                                                                                  |         |          |
| langchain-core     | guess               |     65 |     62 |        3 |                      |                                                                                  |         |          |
| langchain-core     | infer-union certain |  1,021 |  1,016 |        5 |                      |                                                                                  |         |          |
| langchain-core     | infer-union likely  |    320 |    319 |        1 |                      |                                                                                  |         |          |
| langchain-core     | infer-union guess   |    155 |    150 |        5 |                      |                                                                                  |         |          |
| pint               |                     |        |        |          |                    5 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    47.2 |     63.7 |
| pint               | certain             |    218 |    215 |        3 |                      |                                                                                  |         |          |
| pint               | likely              |     12 |     12 |        0 |                      |                                                                                  |         |          |
| pint               | guess               |     24 |     22 |        2 |                      |                                                                                  |         |          |
| pint               | infer-union certain |    219 |    216 |        3 |                      |                                                                                  |         |          |
| pint               | infer-union likely  |     66 |     65 |        1 |                      |                                                                                  |         |          |
| pint               | infer-union guess   |     74 |     72 |        2 |                      |                                                                                  |         |          |
| altair             |                     |        |        |          |                    6 |            28 failed, 1866 passed, 12 skipped, 6 xfailed, 4 xpassed, 93 warnings |    33.6 |     16.9 |
| altair             | certain             |    204 |    203 |        1 |                      |                                                                                  |         |          |
| altair             | likely              |     35 |     35 |        0 |                      |                                                                                  |         |          |
| altair             | guess               |      6 |      5 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union certain |    204 |    203 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union likely  |     75 |     74 |        1 |                      |                                                                                  |         |          |
| altair             | infer-union guess   |     39 |     38 |        1 |                      |                                                                                  |         |          |
| seaborn            |                     |        |        |          |                   37 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    43.1 |     43.3 |
| seaborn            | certain             |    507 |    505 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely              |    133 |    131 |        2 |                      |                                                                                  |         |          |
| seaborn            | guess               |     46 |     44 |        2 |                      |                                                                                  |         |          |
| seaborn            | infer-union certain |    506 |    504 |        2 |                      |                                                                                  |         |          |
| seaborn            | infer-union likely  |    203 |    197 |        6 |                      |                                                                                  |         |          |
| seaborn            | infer-union guess   |    211 |    205 |        6 |                      |                                                                                  |         |          |
| aiohttp            |                     |        |        |          |                    0 |                 3 failed, 4840 passed, 535 skipped, 2 xfailed, 4 subtests passed |   101.9 |     98.0 |
| aiohttp            | certain             |    536 |    518 |       18 |                      |                                                                                  |         |          |
| aiohttp            | likely              |    115 |    113 |        2 |                      |                                                                                  |         |          |
| aiohttp            | guess               |     83 |     77 |        6 |                      |                                                                                  |         |          |
| aiohttp            | infer-union certain |    538 |    520 |       18 |                      |                                                                                  |         |          |
| aiohttp            | infer-union likely  |    319 |    314 |        5 |                      |                                                                                  |         |          |
| aiohttp            | infer-union guess   |    161 |    155 |        6 |                      |                                                                                  |         |          |
| websockets         |                     |        |        |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    36.8 |     27.1 |
| websockets         | certain             |    259 |    258 |        1 |                      |                                                                                  |         |          |
| websockets         | likely              |     68 |     68 |        0 |                      |                                                                                  |         |          |
| websockets         | guess               |     36 |     36 |        0 |                      |                                                                                  |         |          |
| websockets         | infer-union certain |    261 |    260 |        1 |                      |                                                                                  |         |          |
| websockets         | infer-union likely  |    146 |    146 |        0 |                      |                                                                                  |         |          |
| websockets         | infer-union guess   |     52 |     52 |        0 |                      |                                                                                  |         |          |
| anyio              |                     |        |        |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   157.2 |    118.5 |
| anyio              | certain             |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | likely              |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | guess               |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union certain |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union likely  |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | infer-union guess   |      0 |      0 |        0 |                      |                                                                                  |         |          |
| zarr               |                     |        |        |          |                    0 |                                   1 failed, 8421 passed, 1205 skipped, 4 xfailed |   171.6 |    134.6 |
| zarr               | certain             |    778 |    765 |       13 |                      |                                                                                  |         |          |
| zarr               | likely              |     52 |     52 |        0 |                      |                                                                                  |         |          |
| zarr               | guess               |     24 |     22 |        2 |                      |                                                                                  |         |          |
| zarr               | infer-union certain |    778 |    765 |       13 |                      |                                                                                  |         |          |
| zarr               | infer-union likely  |    274 |    272 |        2 |                      |                                                                                  |         |          |
| zarr               | infer-union guess   |    151 |    144 |        7 |                      |                                                                                  |         |          |
| joblib             |                     |        |        |          |                   10 |                       10 failed, 1482 passed, 45 skipped, 4 xpassed, 84 warnings |   216.3 |    217.6 |
| joblib             | certain             |    127 |    127 |        0 |                      |                                                                                  |         |          |
| joblib             | likely              |     16 |     16 |        0 |                      |                                                                                  |         |          |
| joblib             | guess               |     29 |     29 |        0 |                      |                                                                                  |         |          |
| joblib             | infer-union certain |    125 |    125 |        0 |                      |                                                                                  |         |          |
| joblib             | infer-union likely  |     40 |     39 |        1 |                      |                                                                                  |         |          |
| joblib             | infer-union guess   |     62 |     60 |        2 |                      |                                                                                  |         |          |
| networkx           |                     |        |        |          |                  362 |                                            10083 passed, 62 skipped, 741 xfailed |    23.1 |     29.0 |
| networkx           | certain             |    933 |    932 |        1 |                      |                                                                                  |         |          |
| networkx           | likely              |    195 |    194 |        1 |                      |                                                                                  |         |          |
| networkx           | guess               |    156 |    153 |        3 |                      |                                                                                  |         |          |
| networkx           | infer-union certain |    930 |    929 |        1 |                      |                                                                                  |         |          |
| networkx           | infer-union likely  |    476 |    456 |       20 |                      |                                                                                  |         |          |
| networkx           | infer-union guess   |    477 |    447 |       30 |                      |                                                                                  |         |          |
| nibabel            |                     |        |        |          |                   76 |                      110 failed, 5167 passed, 303 skipped, 40 xfailed, 20 errors |    16.8 |     12.9 |
| nibabel            | certain             |    416 |    413 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely              |    178 |    178 |        0 |                      |                                                                                  |         |          |
| nibabel            | guess               |     99 |     98 |        1 |                      |                                                                                  |         |          |
| nibabel            | infer-union certain |    416 |    413 |        3 |                      |                                                                                  |         |          |
| nibabel            | infer-union likely  |    300 |    297 |        3 |                      |                                                                                  |         |          |
| nibabel            | infer-union guess   |    285 |    264 |       21 |                      |                                                                                  |         |          |
| narwhals           |                     |        |        |          |                    0 |                               972 failed, 11116 passed, 235 skipped, 699 xfailed |    40.2 |     41.9 |
| narwhals           | certain             |    560 |    558 |        2 |                      |                                                                                  |         |          |
| narwhals           | likely              |     40 |     40 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess               |     25 |     25 |        0 |                      |                                                                                  |         |          |
| narwhals           | infer-union certain |    560 |    558 |        2 |                      |                                                                                  |         |          |
| narwhals           | infer-union likely  |    287 |    281 |        6 |                      |                                                                                  |         |          |
| narwhals           | infer-union guess   |     91 |     86 |        5 |                      |                                                                                  |         |          |
| xarray             |                     |        |        |          |                   20 |  3 failed, 6333 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    19.6 |     25.7 |
| xarray             | certain             |    971 |    961 |       10 |                      |                                                                                  |         |          |
| xarray             | likely              |    151 |    150 |        1 |                      |                                                                                  |         |          |
| xarray             | guess               |     88 |     87 |        1 |                      |                                                                                  |         |          |
| xarray             | infer-union certain |    972 |    962 |       10 |                      |                                                                                  |         |          |
| xarray             | infer-union likely  |    465 |    458 |        7 |                      |                                                                                  |         |          |
| xarray             | infer-union guess   |    406 |    401 |        5 |                      |                                                                                  |         |          |
| litestar           |                     |        |        |          |                    0 |           5 failed, 5646 passed, 256 skipped, 13 xfailed, 30 xpassed, 3 warnings |    33.4 |     37.7 |
| litestar           | certain             |    492 |    491 |        1 |                      |                                                                                  |         |          |
| litestar           | likely              |     94 |     94 |        0 |                      |                                                                                  |         |          |
| litestar           | guess               |     51 |     51 |        0 |                      |                                                                                  |         |          |
| litestar           | infer-union certain |    493 |    492 |        1 |                      |                                                                                  |         |          |
| litestar           | infer-union likely  |    279 |    278 |        1 |                      |                                                                                  |         |          |
| litestar           | infer-union guess   |    104 |    104 |        0 |                      |                                                                                  |         |          |
| celery             |                     |        |        |          |                   66 |                                     4 failed, 3520 passed, 36 skipped, 3 xfailed |    70.5 |     56.4 |
| celery             | certain             |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | likely              |     47 |     46 |        1 |                      |                                                                                  |         |          |
| celery             | guess               |     28 |     24 |        4 |                      |                                                                                  |         |          |
| celery             | infer-union certain |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | infer-union likely  |     94 |     91 |        3 |                      |                                                                                  |         |          |
| celery             | infer-union guess   |    122 |    104 |       18 |                      |                                                                                  |         |          |
| optuna             |                     |        |        |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 336 warnings, 16 errors |   163.9 |    120.1 |
| optuna             | certain             |    700 |    700 |        0 |                      |                                                                                  |         |          |
| optuna             | likely              |    122 |    122 |        0 |                      |                                                                                  |         |          |
| optuna             | guess               |     56 |     56 |        0 |                      |                                                                                  |         |          |
| optuna             | infer-union certain |    701 |    701 |        0 |                      |                                                                                  |         |          |
| optuna             | infer-union likely  |    340 |    337 |        3 |                      |                                                                                  |         |          |
| optuna             | infer-union guess   |    281 |    280 |        1 |                      |                                                                                  |         |          |
| dask               |                     |        |        |          |                  155 |         5 failed, 16196 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   133.9 |    166.7 |
| dask               | certain             |  1,075 |  1,068 |        7 |                      |                                                                                  |         |          |
| dask               | likely              |    188 |    185 |        3 |                      |                                                                                  |         |          |
| dask               | guess               |    118 |    115 |        3 |                      |                                                                                  |         |          |
| dask               | infer-union certain |  1,073 |  1,066 |        7 |                      |                                                                                  |         |          |
| dask               | infer-union likely  |    384 |    371 |       13 |                      |                                                                                  |         |          |
| dask               | infer-union guess   |    469 |    450 |       19 |                      |                                                                                  |         |          |
| mypy               |                     |        |        |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   279.7 |    303.3 |
| mypy               | certain             |  3,820 |  3,820 |        0 |                      |                                                                                  |         |          |
| mypy               | likely              |    766 |    766 |        0 |                      |                                                                                  |         |          |
| mypy               | guess               |    302 |    302 |        0 |                      |                                                                                  |         |          |
| mypy               | infer-union certain |  3,820 |  3,820 |        0 |                      |                                                                                  |         |          |
| mypy               | infer-union likely  |  1,964 |  1,963 |        1 |                      |                                                                                  |         |          |
| mypy               | infer-union guess   |    675 |    675 |        0 |                      |                                                                                  |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus             | shape                                        | no fix | traced | one type |
| ------------------ | -------------------------------------------- | -----: | -----: | -------: |
| django             | `call: chained .method()`                    |  1,346 |    948 |      602 |
| django             | `call: self.method()`                        |    978 |    652 |      417 |
| django             | `call: param.method()`                       |    654 |    473 |      372 |
| django             | `call: imported function`                    |    654 |    275 |      202 |
| django             | `call: local.method()`                       |    545 |    385 |      266 |
| django             | `empty list`                                 |    449 |      0 |        0 |
| django             | `copy: local`                                |    434 |    319 |      223 |
| django             | `attr: chained`                              |    406 |    279 |      183 |
| django             | `copy: param (unannotated)`                  |    348 |    237 |      140 |
| django             | `attr: self.x`                               |    342 |    270 |      144 |
| django             | `other constant`                             |    330 |     22 |       22 |
| django             | `None literal`                               |    319 |    103 |      103 |
| django             | `call: imported.attr()`                      |    301 |    147 |       98 |
| django             | `subscript: other`                           |    265 |    196 |      161 |
| django             | `dict (mixed/unknown elements)`              |    237 |    104 |       73 |
| django             | `empty dict`                                 |    201 |      0 |        0 |
| django             | `call: module function (unannotated)`        |    185 |    132 |       95 |
| django             | `tuple (mixed/unknown elements)`             |    176 |     94 |       72 |
| django             | `copy: imported`                             |    175 |      8 |        7 |
| django             | `call: builtin getattr()`                    |    174 |    154 |       73 |
| django             | `subscript: local[...]`                      |    173 |    108 |       90 |
| django             | `attr: local.x`                              |    170 |    130 |       93 |
| django             | `ListComp (unknown elements)`                |    165 |    119 |       82 |
| django             | `list (mixed/unknown elements)`              |    159 |     56 |       44 |
| django             | `conditional`                                |    157 |    126 |       64 |
| django             | `subscript: param[...]`                      |    136 |    111 |       93 |
| django             | `binop (unknown operands)`                   |    130 |     84 |       78 |
| django             | `attr: param.x`                              |    124 |    102 |       73 |
| django             | `boolop (or)`                                |    112 |     95 |       72 |
| django             | `call: builtin set()`                        |    109 |     16 |       12 |
| django             | `attr: imported.x`                           |    105 |     21 |       17 |
| django             | `call: imported class`                       |     95 |     14 |       14 |
| django             | `call: module.func()`                        |     94 |     68 |       58 |
| django             | `call: builtin enumerate()`                  |     85 |     66 |       38 |
| django             | `call: builtin sorted()`                     |     77 |     64 |       58 |
| django             | `call: builtin list()`                       |     62 |     47 |       34 |
| django             | `subscript: imported[...]`                   |     59 |     40 |       36 |
| django             | `DictComp (unknown elements)`                |     57 |     35 |       19 |
| django             | `call: builtin zip()`                        |     56 |     38 |       16 |
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
| django             | `binop (one side literal)`                   |     29 |      6 |        6 |
| django             | `copy: modclass`                             |     27 |      0 |        0 |
| django             | `copy: moddef`                               |     26 |      0 |        0 |
| django             | `copy: global`                               |     25 |      4 |        4 |
| django             | `call: other callee`                         |     24 |     17 |       13 |
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
| django             | `copy: self`                                 |      9 |      7 |        4 |
| django             | `call: capitalised`                          |      9 |      6 |        3 |
| django             | `await: call: other name`                    |      9 |      9 |        8 |
| django             | `call: cls.method()`                         |      9 |      6 |        4 |
| django             | `call: builtin dict()`                       |      8 |      7 |        3 |
| django             | `set (mixed/unknown elements)`               |      7 |      4 |        4 |
| django             | `call: builtin map()`                        |      7 |      3 |        2 |
| django             | `call: builtin min()`                        |      6 |      2 |        2 |
| django             | `call: builtin frozenset()`                  |      6 |      1 |        1 |
| django             | `attr: global.x`                             |      6 |      1 |        1 |
| django             | `await: call: module.func()`                 |      6 |      0 |        0 |
| django             | `call: builtin.method()`                     |      5 |      3 |        3 |
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
| sqlalchemy         | `call: chained .method()`                    |    940 |    454 |      306 |
| sqlalchemy         | `other constant`                             |    602 |      8 |        8 |
| sqlalchemy         | `attr: chained`                              |    570 |    284 |      216 |
| sqlalchemy         | `call: self.method()`                        |    567 |    297 |      162 |
| sqlalchemy         | `call: local.method()`                       |    521 |    283 |      180 |
| sqlalchemy         | `call: param.method()`                       |    446 |    272 |      165 |
| sqlalchemy         | `attr: self.x`                               |    358 |    278 |      155 |
| sqlalchemy         | `subscript: other`                           |    354 |    215 |      137 |
| sqlalchemy         | `copy: local`                                |    351 |    219 |      136 |
| sqlalchemy         | `call: imported function`                    |    334 |    155 |       85 |
| sqlalchemy         | `call: imported.attr()`                      |    317 |    167 |      108 |
| sqlalchemy         | `attr: param.x`                              |    312 |    249 |      148 |
| sqlalchemy         | `attr: local.x`                              |    253 |    203 |      128 |
| sqlalchemy         | `tuple (mixed/unknown elements)`             |    202 |    134 |       90 |
| sqlalchemy         | `copy: param (unannotated)`                  |    183 |    135 |       91 |
| sqlalchemy         | `subscript: local[...]`                      |    173 |     93 |       54 |
| sqlalchemy         | `None literal`                               |    172 |     73 |       73 |
| sqlalchemy         | `ListComp (unknown elements)`                |    158 |    119 |       71 |
| sqlalchemy         | `copy: modclass`                             |    147 |      1 |        1 |
| sqlalchemy         | `attr: imported.x`                           |    145 |     17 |       17 |
| sqlalchemy         | `copy: imported`                             |    118 |      1 |        1 |
| sqlalchemy         | `call: builtin list()`                       |    117 |     75 |       45 |
| sqlalchemy         | `empty list`                                 |    114 |      0 |        0 |
| sqlalchemy         | `call: module.func()`                        |    107 |     52 |       43 |
| sqlalchemy         | `copy: param (annotated)`                    |    106 |     87 |       50 |
| sqlalchemy         | `dict (mixed/unknown elements)`              |    103 |     16 |       14 |
| sqlalchemy         | `call: builtin getattr()`                    |    100 |     82 |       37 |
| sqlalchemy         | `call: param name`                           |     90 |     36 |       14 |
| sqlalchemy         | `empty dict`                                 |     82 |      0 |        0 |
| sqlalchemy         | `call: builtin set()`                        |     82 |     34 |       23 |
| sqlalchemy         | `binop (unknown operands)`                   |     81 |     43 |       32 |
| sqlalchemy         | `call: other name`                           |     76 |     58 |       34 |
| sqlalchemy         | `subscript: param[...]`                      |     74 |     60 |       37 |
| sqlalchemy         | `boolop (or)`                                |     73 |     59 |       47 |
| sqlalchemy         | `conditional`                                |     71 |     40 |       21 |
| sqlalchemy         | `call: local name`                           |     63 |     51 |       23 |
| sqlalchemy         | `copy: other`                                |     63 |     20 |       15 |
| sqlalchemy         | `list (mixed/unknown elements)`              |     62 |     18 |       10 |
| sqlalchemy         | `DictComp (unknown elements)`                |     61 |     35 |       15 |
| sqlalchemy         | `call: module function (unannotated)`        |     59 |     49 |       37 |
| sqlalchemy         | `call: builtin zip()`                        |     57 |     39 |       20 |
| sqlalchemy         | `copy: global`                               |     50 |      6 |        6 |
| sqlalchemy         | `call: builtin dict()`                       |     49 |     24 |       13 |
| sqlalchemy         | `call: builtin enumerate()`                  |     39 |     29 |        6 |
| sqlalchemy         | `call: builtin tuple()`                      |     38 |     15 |        5 |
| sqlalchemy         | `call: other.method()`                       |     36 |     20 |       10 |
| sqlalchemy         | `SetComp (unknown elements)`                 |     35 |     22 |       16 |
| sqlalchemy         | `call: imported class`                       |     33 |      7 |        7 |
| sqlalchemy         | `call: module function (annotated)`          |     32 |     29 |       14 |
| sqlalchemy         | `call: cls.method()`                         |     30 |     24 |       15 |
| sqlalchemy         | `boolop (and)`                               |     25 |     25 |       21 |
| sqlalchemy         | `call: builtin.method()`                     |     24 |     23 |       10 |
| sqlalchemy         | `call: module class`                         |     23 |     15 |       15 |
| sqlalchemy         | `attr: modclass.x`                           |     21 |      0 |        0 |
| sqlalchemy         | `attr: cls.x`                                |     21 |     21 |       11 |
| sqlalchemy         | `empty tuple`                                |     16 |      0 |        0 |
| sqlalchemy         | `compare`                                    |     15 |      9 |        9 |
| sqlalchemy         | `call: builtin type()`                       |     15 |     10 |        3 |
| sqlalchemy         | `call: other callee`                         |     15 |     11 |        5 |
| sqlalchemy         | `await: call: imported function`             |     15 |     13 |        9 |
| sqlalchemy         | `attr: global.x`                             |     14 |      0 |        0 |
| sqlalchemy         | `GeneratorExp (unknown elements)`            |     13 |      7 |        7 |
| sqlalchemy         | `call: global.method()`                      |     13 |     11 |       11 |
| sqlalchemy         | `copy: moddef`                               |     13 |      0 |        0 |
| sqlalchemy         | `call: builtin sorted()`                     |     12 |      5 |        4 |
| sqlalchemy         | `subscript: global[...]`                     |     12 |     11 |        9 |
| sqlalchemy         | `call: global name`                          |     12 |     12 |        3 |
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
| pydantic           | `call: chained .method()`                    |    124 |     53 |       35 |
| pydantic           | `call: imported function`                    |    111 |     61 |       42 |
| pydantic           | `call: local.method()`                       |    111 |     55 |       30 |
| pydantic           | `call: param.method()`                       |     98 |     59 |       31 |
| pydantic           | `call: self.method()`                        |     55 |     32 |        9 |
| pydantic           | `call: builtin getattr()`                    |     53 |     29 |       17 |
| pydantic           | `call: module function (annotated)`          |     53 |     14 |        8 |
| pydantic           | `attr: param.x`                              |     45 |     25 |       12 |
| pydantic           | `conditional`                                |     37 |     18 |       10 |
| pydantic           | `copy: param (annotated)`                    |     36 |     20 |       12 |
| pydantic           | `copy: local`                                |     35 |     16 |       12 |
| pydantic           | `tuple (mixed/unknown elements)`             |     35 |      8 |        6 |
| pydantic           | `call: imported.attr()`                      |     33 |     28 |       10 |
| pydantic           | `attr: chained`                              |     33 |      5 |        4 |
| pydantic           | `subscript: other`                           |     31 |     11 |        3 |
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
| pandas             | `call: local.method()`                       |  5,920 |  4,895 |    4,546 |
| pandas             | `call: chained .method()`                    |  4,525 |  3,478 |    3,153 |
| pandas             | `call: module.func()`                        |  3,333 |  2,203 |    2,096 |
| pandas             | `copy: param (unannotated)`                  |  1,955 |  1,735 |      788 |
| pandas             | `subscript: other`                           |  1,510 |  1,222 |    1,090 |
| pandas             | `call: imported function`                    |  1,438 |  1,031 |      875 |
| pandas             | `call: param.method()`                       |  1,404 |    977 |      768 |
| pandas             | `binop (unknown operands)`                   |  1,100 |    950 |      802 |
| pandas             | `subscript: local[...]`                      |    948 |    756 |      708 |
| pandas             | `list (mixed/unknown elements)`              |    778 |    532 |      399 |
| pandas             | `call: param name`                           |    769 |    726 |      269 |
| pandas             | `attr: chained`                              |    768 |    511 |      415 |
| pandas             | `call: imported class`                       |    736 |    631 |      626 |
| pandas             | `call: self.method()`                        |    585 |    394 |      238 |
| pandas             | `call: other callee`                         |    503 |    418 |      340 |
| pandas             | `conditional`                                |    470 |    377 |      200 |
| pandas             | `attr: local.x`                              |    424 |    315 |      254 |
| pandas             | `copy: local`                                |    412 |    274 |      194 |
| pandas             | `subscript: param[...]`                      |    384 |    276 |      163 |
| pandas             | `tuple (mixed/unknown elements)`             |    370 |    224 |      173 |
| pandas             | `ListComp (unknown elements)`                |    359 |    187 |      135 |
| pandas             | `compare`                                    |    347 |    271 |      250 |
| pandas             | `dict (mixed/unknown elements)`              |    331 |    207 |      181 |
| pandas             | `call: imported.attr()`                      |    328 |    232 |      162 |
| pandas             | `call: builtin getattr()`                    |    307 |    225 |      155 |
| pandas             | `call: builtin zip()`                        |    306 |    209 |      152 |
| pandas             | `call: local name`                           |    293 |    252 |      145 |
| pandas             | `attr: param.x`                              |    281 |    190 |      104 |
| pandas             | `empty list`                                 |    276 |      0 |        0 |
| pandas             | `call: module function (unannotated)`        |    275 |    133 |       82 |
| pandas             | `attr: self.x`                               |    274 |    192 |      106 |
| pandas             | `binop (one side literal)`                   |    253 |    200 |      179 |
| pandas             | `call: builtin enumerate()`                  |    233 |    156 |      107 |
| pandas             | `other constant`                             |    177 |     47 |       47 |
| pandas             | `call: builtin list()`                       |    170 |    124 |       84 |
| pandas             | `None literal`                               |    157 |    113 |      113 |
| pandas             | `Lambda`                                     |    120 |     76 |       76 |
| pandas             | `call: global.method()`                      |    118 |      4 |        2 |
| pandas             | `attr: module.x`                             |    116 |     79 |       77 |
| pandas             | `call: other name`                           |    113 |     75 |       52 |
| pandas             | `attr: imported.x`                           |     93 |     22 |       22 |
| pandas             | `empty dict`                                 |     90 |      0 |        0 |
| pandas             | `copy: imported`                             |     89 |     50 |       50 |
| pandas             | `call: module function (annotated)`          |     85 |     47 |       23 |
| pandas             | `copy: other`                                |     78 |      7 |        4 |
| pandas             | `copy: param (annotated)`                    |     70 |     47 |       33 |
| pandas             | `GeneratorExp (unknown elements)`            |     70 |     60 |       60 |
| pandas             | `call: capitalised`                          |     60 |     59 |       58 |
| pandas             | `copy: builtin`                              |     59 |     42 |       42 |
| pandas             | `DictComp (unknown elements)`                |     57 |     42 |       32 |
| pandas             | `call: builtin set()`                        |     49 |     18 |       13 |
| pandas             | `unaryop Invert`                             |     40 |     30 |       28 |
| pandas             | `call: other.method()`                       |     39 |     20 |       15 |
| pandas             | `boolop (and)`                               |     35 |     21 |       19 |
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
| structlog          | `call: builtin getattr()`                    |      3 |      3 |        2 |
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
| attrs              | `ListComp (unknown elements)`                |      8 |      5 |        3 |
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
| starlette          | `call: local.method()`                       |     30 |     22 |       17 |
| starlette          | `call: chained .method()`                    |     22 |     20 |       14 |
| starlette          | `call: builtin reversed()`                   |     15 |      4 |        2 |
| starlette          | `subscript: param[...]`                      |     14 |     14 |       13 |
| starlette          | `attr: self.x`                               |     11 |      8 |        4 |
| starlette          | `await: call: self.method()`                 |     10 |      9 |        2 |
| starlette          | `call: module.func()`                        |      9 |      9 |        7 |
| starlette          | `other constant`                             |      9 |      0 |        0 |
| starlette          | `call: imported function`                    |      9 |      9 |        7 |
| starlette          | `tuple (mixed/unknown elements)`             |      8 |      7 |        6 |
| starlette          | `call: self.method()`                        |      8 |      7 |        6 |
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
| black              | `boolop (and)`                               |     11 |      8 |        6 |
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
| fastapi            | `call: module function (annotated)`          |     41 |     28 |       15 |
| fastapi            | `call: chained .method()`                    |     41 |     39 |       19 |
| fastapi            | `call: imported function`                    |     38 |     32 |        9 |
| fastapi            | `call: local.method()`                       |     27 |     19 |       15 |
| fastapi            | `call: param.method()`                       |     27 |     24 |       10 |
| fastapi            | `call: builtin getattr()`                    |     25 |     22 |       19 |
| fastapi            | `copy: local`                                |     18 |     18 |       12 |
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
| fastapi            | `call: self.method()`                        |      1 |      1 |        1 |
| fastapi            | `other constant`                             |      1 |      0 |        0 |
| fastapi            | `call: imported.attr()`                      |      1 |      1 |        1 |
| fastapi            | `call: builtin type()`                       |      1 |      1 |        0 |
| fastapi            | `compare`                                    |      1 |      1 |        1 |
| fastapi            | `attr: other.x`                              |      1 |      1 |        0 |
| cattrs             | `call: imported function`                    |     54 |     42 |       12 |
| cattrs             | `attr: local.x`                              |     20 |     18 |       12 |
| cattrs             | `empty dict`                                 |     20 |      0 |        0 |
| cattrs             | `copy: local`                                |     19 |     19 |        9 |
| cattrs             | `call: builtin getattr()`                    |     18 |     16 |        4 |
| cattrs             | `empty list`                                 |     18 |      0 |        0 |
| cattrs             | `attr: param.x`                              |     15 |     15 |        7 |
| cattrs             | `call: chained .method()`                    |     13 |     11 |        7 |
| cattrs             | `copy: imported`                             |     11 |      3 |        3 |
| cattrs             | `conditional`                                |     10 |     10 |        5 |
| cattrs             | `attr: global.x`                             |      9 |      1 |        0 |
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
| cattrs             | `copy: param (annotated)`                    |      6 |      5 |        2 |
| cattrs             | `None literal`                               |      6 |      5 |        5 |
| cattrs             | `call: module function (annotated)`          |      6 |      6 |        2 |
| cattrs             | `attr: imported.x`                           |      5 |      4 |        0 |
| cattrs             | `attr: chained`                              |      5 |      5 |        5 |
| cattrs             | `call: other.method()`                       |      5 |      5 |        3 |
| cattrs             | `dict (mixed/unknown elements)`              |      5 |      5 |        0 |
| cattrs             | `DictComp (unknown elements)`                |      4 |      1 |        0 |
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
| pytest             | `call: chained .method()`                    |    157 |    123 |       98 |
| pytest             | `call: self.method()`                        |     88 |     73 |       60 |
| pytest             | `attr: chained`                              |     68 |     52 |       45 |
| pytest             | `copy: local`                                |     61 |     48 |       37 |
| pytest             | `call: local.method()`                       |     55 |     43 |       36 |
| pytest             | `attr: param.x`                              |     55 |     41 |       33 |
| pytest             | `call: builtin getattr()`                    |     51 |     42 |       26 |
| pytest             | `call: param.method()`                       |     51 |     44 |       40 |
| pytest             | `empty list`                                 |     49 |      0 |        0 |
| pytest             | `call: module.func()`                        |     45 |     30 |       25 |
| pytest             | `attr: local.x`                              |     45 |     36 |       25 |
| pytest             | `subscript: other`                           |     42 |     29 |       19 |
| pytest             | `attr: self.x`                               |     28 |     26 |       17 |
| pytest             | `None literal`                               |     27 |     23 |       23 |
| pytest             | `conditional`                                |     27 |     22 |       15 |
| pytest             | `tuple (mixed/unknown elements)`             |     23 |     22 |       19 |
| pytest             | `copy: param (annotated)`                    |     23 |     15 |        8 |
| pytest             | `call: module function (annotated)`          |     22 |     21 |       10 |
| pytest             | `binop (unknown operands)`                   |     20 |     17 |       16 |
| pytest             | `call: imported class`                       |     19 |      3 |        3 |
| pytest             | `other constant`                             |     17 |      5 |        5 |
| pytest             | `boolop (or)`                                |     17 |     11 |       10 |
| pytest             | `call: other callee`                         |     17 |      4 |        4 |
| pytest             | `ListComp (unknown elements)`                |     15 |     10 |        8 |
| pytest             | `call: imported.attr()`                      |     15 |      8 |        7 |
| pytest             | `call: other name`                           |     14 |     12 |       10 |
| pytest             | `call: builtin list()`                       |     12 |     10 |        9 |
| pytest             | `call: module class`                         |     12 |      7 |        7 |
| pytest             | `call: imported function`                    |     11 |      8 |        6 |
| pytest             | `call: builtin enumerate()`                  |     10 |      9 |        4 |
| pytest             | `Yield`                                      |     10 |      7 |        7 |
| pytest             | `copy: other`                                |     10 |      1 |        1 |
| pytest             | `subscript: local[...]`                      |      9 |      6 |        4 |
| pytest             | `DictComp (unknown elements)`                |      9 |      6 |        3 |
| pytest             | `list (mixed/unknown elements)`              |      9 |      6 |        5 |
| pytest             | `call: builtin reversed()`                   |      9 |      8 |        6 |
| pytest             | `dict (mixed/unknown elements)`              |      8 |      4 |        4 |
| pytest             | `call: module function (unannotated)`        |      8 |      4 |        3 |
| pytest             | `call: builtin sorted()`                     |      8 |      7 |        7 |
| pytest             | `compare`                                    |      7 |      7 |        7 |
| pytest             | `unaryop USub`                               |      7 |      5 |        5 |
| pytest             | `attr: module.x`                             |      7 |      5 |        2 |
| pytest             | `subscript: global[...]`                     |      7 |      7 |        7 |
| pytest             | `subscript: param[...]`                      |      6 |      4 |        2 |
| pytest             | `binop (one side literal)`                   |      6 |      6 |        6 |
| pytest             | `-`                                          |      6 |      0 |        0 |
| pytest             | `copy: param (unannotated)`                  |      5 |      5 |        2 |
| pytest             | `empty dict`                                 |      5 |      0 |        0 |
| pytest             | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| pytest             | `call: builtin type()`                       |      4 |      4 |        0 |
| pytest             | `call: builtin zip()`                        |      4 |      4 |        3 |
| pytest             | `call: other.method()`                       |      4 |      4 |        3 |
| pytest             | `call: modclass.method()`                    |      4 |      4 |        4 |
| pytest             | `call: builtin.method()`                     |      4 |      3 |        2 |
| pytest             | `call: builtin dict()`                       |      3 |      3 |        2 |
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
| pytest             | `call: builtin abs()`                        |      2 |      1 |        0 |
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
| pytest             | `call: param name`                           |      1 |      0 |        0 |
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
| botocore           | `call: self.method()`                        |    362 |    318 |      205 |
| botocore           | `call: chained .method()`                    |    345 |    297 |      186 |
| botocore           | `call: param.method()`                       |    245 |    214 |      141 |
| botocore           | `call: local.method()`                       |    233 |    197 |      123 |
| botocore           | `copy: param (unannotated)`                  |    100 |     92 |       66 |
| botocore           | `subscript: other`                           |     97 |     78 |       63 |
| botocore           | `call: imported function`                    |     84 |     66 |       55 |
| botocore           | `attr: param.x`                              |     79 |     74 |       37 |
| botocore           | `empty dict`                                 |     76 |      0 |        0 |
| botocore           | `subscript: local[...]`                      |     75 |     69 |       47 |
| botocore           | `copy: local`                                |     71 |     66 |       50 |
| botocore           | `dict (mixed/unknown elements)`              |     70 |     36 |       27 |
| botocore           | `subscript: param[...]`                      |     65 |     53 |       32 |
| botocore           | `attr: self.x`                               |     60 |     56 |       31 |
| botocore           | `attr: chained`                              |     55 |     38 |       32 |
| botocore           | `empty list`                                 |     48 |      0 |        0 |
| botocore           | `call: module.func()`                        |     37 |     26 |       14 |
| botocore           | `call: module function (unannotated)`        |     33 |     26 |       19 |
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
| uvicorn            | `call: builtin hasattr()`                    |      1 |      1 |        1 |
| uvicorn            | `await: call: other name`                    |      1 |      1 |        0 |
| uvicorn            | `other constant`                             |      1 |      1 |        1 |
| uvicorn            | `subscript: local[...]`                      |      1 |      1 |        1 |
| uvicorn            | `call: local name`                           |      1 |      1 |        0 |
| uvicorn            | `call: builtin bytearray()`                  |      1 |      1 |        1 |
| uvicorn            | `copy: self`                                 |      1 |      1 |        0 |
| uvicorn            | `call: builtin list()`                       |      1 |      1 |        1 |
| mcp                | `call: chained .method()`                    |     73 |     66 |       41 |
| mcp                | `call: other callee`                         |     50 |     44 |       44 |
| mcp                | `call: imported function`                    |     46 |     39 |       21 |
| mcp                | `call: param.method()`                       |     42 |     41 |       15 |
| mcp                | `conditional`                                |     41 |     39 |       18 |
| mcp                | `call: module.func()`                        |     39 |     34 |       23 |
| mcp                | `copy: local`                                |     36 |     30 |       21 |
| mcp                | `call: local.method()`                       |     35 |     31 |       10 |
| mcp                | `call: module function (annotated)`          |     20 |     19 |        8 |
| mcp                | `attr: param.x`                              |     19 |     19 |        9 |
| mcp                | `call: imported class`                       |     18 |      6 |        6 |
| mcp                | `call: imported.attr()`                      |     17 |     17 |       13 |
| mcp                | `await: call: param.method()`                |     16 |     13 |       10 |
| mcp                | `await: call: self.method()`                 |     16 |     16 |        7 |
| mcp                | `await: call: local.method()`                |     15 |     12 |        9 |
| mcp                | `attr: local.x`                              |     14 |     14 |        9 |
| mcp                | `boolop (or)`                                |     13 |     10 |        9 |
| mcp                | `attr: self.x`                               |     12 |     12 |        7 |
| mcp                | `attr: chained`                              |     12 |     12 |        6 |
| mcp                | `await: call: chained .method()`             |     12 |     12 |        5 |
| mcp                | `None literal`                               |     11 |      8 |        8 |
| mcp                | `tuple (mixed/unknown elements)`             |     11 |      8 |        6 |
| mcp                | `subscript: other`                           |     10 |     10 |        9 |
| mcp                | `call: builtin getattr()`                    |     10 |      7 |        3 |
| mcp                | `copy: param (annotated)`                    |     10 |      9 |        7 |
| mcp                | `ListComp (unknown elements)`                |     10 |     10 |        9 |
| mcp                | `Yield`                                      |     10 |      9 |        9 |
| mcp                | `dict (mixed/unknown elements)`              |     10 |      9 |        9 |
| mcp                | `call: self.method()`                        |      9 |      8 |        6 |
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
| requests           | `call: imported function`                    |     43 |     40 |       36 |
| requests           | `copy: local`                                |     30 |     25 |       14 |
| requests           | `call: chained .method()`                    |     16 |     15 |       12 |
| requests           | `call: local.method()`                       |     15 |     13 |       11 |
| requests           | `None literal`                               |     14 |     11 |       11 |
| requests           | `call: param.method()`                       |     13 |     13 |        9 |
| requests           | `call: module.func()`                        |     13 |     11 |       10 |
| requests           | `subscript: other`                           |     10 |      8 |        8 |
| requests           | `call: self.method()`                        |     10 |      9 |        6 |
| requests           | `call: builtin iter()`                       |      9 |      4 |        4 |
| requests           | `dict (mixed/unknown elements)`              |      8 |      6 |        5 |
| requests           | `copy: param (annotated)`                    |      8 |      5 |        5 |
| requests           | `tuple (mixed/unknown elements)`             |      8 |      5 |        5 |
| requests           | `attr: local.x`                              |      7 |      7 |        4 |
| requests           | `call: builtin getattr()`                    |      7 |      6 |        2 |
| requests           | `other constant`                             |      6 |      6 |        6 |
| requests           | `JoinedStr`                                  |      5 |      5 |        5 |
| requests           | `attr: chained`                              |      4 |      4 |        4 |
| requests           | `boolop (or)`                                |      4 |      4 |        3 |
| requests           | `compare`                                    |      4 |      2 |        2 |
| requests           | `call: module class`                         |      4 |      4 |        4 |
| requests           | `call: imported class`                       |      3 |      2 |        2 |
| requests           | `binop (one side literal)`                   |      3 |      1 |        1 |
| requests           | `call: local name`                           |      3 |      3 |        2 |
| requests           | `attr: module.x`                             |      3 |      1 |        1 |
| requests           | `copy: global`                               |      3 |      0 |        0 |
| requests           | `attr: param.x`                              |      3 |      3 |        3 |
| requests           | `binop (unknown operands)`                   |      3 |      2 |        2 |
| requests           | `call: module function (annotated)`          |      3 |      2 |        2 |
| requests           | `boolop (and)`                               |      2 |      2 |        1 |
| requests           | `call: builtin list()`                       |      2 |      2 |        2 |
| requests           | `ListComp (unknown elements)`                |      2 |      1 |        1 |
| requests           | `conditional`                                |      2 |      1 |        1 |
| requests           | `DictComp (unknown elements)`                |      2 |      0 |        0 |
| requests           | `call: global.method()`                      |      2 |      2 |        2 |
| requests           | `call: capitalised`                          |      1 |      0 |        0 |
| requests           | `attr: self.x`                               |      1 |      1 |        0 |
| requests           | `attr: imported.x`                           |      1 |      0 |        0 |
| requests           | `call: param name`                           |      1 |      1 |        1 |
| requests           | `call: global name`                          |      1 |      1 |        1 |
| requests           | `call: other callee`                         |      1 |      1 |        1 |
| requests           | `call: builtin chr()`                        |      1 |      1 |        1 |
| requests           | `GeneratorExp (unknown elements)`            |      1 |      0 |        0 |
| requests           | `list (mixed/unknown elements)`              |      1 |      1 |        1 |
| requests           | `call: str-literal.method()`                 |      1 |      0 |        0 |
| requests           | `subscript: param[...]`                      |      1 |      1 |        1 |
| requests           | `subscript: imported[...]`                   |      1 |      1 |        1 |
| rich               | `attr: local.x`                              |     59 |     51 |       51 |
| rich               | `call: imported function`                    |     56 |     36 |       34 |
| rich               | `conditional`                                |     40 |     33 |       27 |
| rich               | `copy: local`                                |     39 |     35 |       28 |
| rich               | `attr: self.x`                               |     37 |     33 |       28 |
| rich               | `attr: chained`                              |     35 |     21 |       21 |
| rich               | `call: local.method()`                       |     33 |     23 |       20 |
| rich               | `binop (unknown operands)`                   |     28 |     23 |       23 |
| rich               | `call: chained .method()`                    |     25 |     13 |       12 |
| rich               | `copy: imported`                             |     23 |     22 |       22 |
| rich               | `call: module.func()`                        |     22 |      8 |        5 |
| rich               | `copy: param (annotated)`                    |     21 |     19 |       12 |
| rich               | `call: other name`                           |     18 |     11 |       10 |
| rich               | `copy: modclass`                             |     18 |     16 |       16 |
| rich               | `call: local name`                           |     16 |     11 |       10 |
| rich               | `call: module class`                         |     16 |      1 |        1 |
| rich               | `other constant`                             |     14 |      6 |        6 |
| rich               | `attr: imported.x`                           |     11 |      9 |        9 |
| rich               | `call: imported.attr()`                      |     11 |      6 |        6 |
| rich               | `attr: param.x`                              |     11 |      7 |        6 |
| rich               | `subscript: local[...]`                      |     11 |     10 |        9 |
| rich               | `call: self.method()`                        |     11 |     10 |        8 |
| rich               | `dict (mixed/unknown elements)`              |     10 |      1 |        1 |
| rich               | `call: param.method()`                       |     10 |      9 |        9 |
| rich               | `boolop (or)`                                |     10 |     10 |        5 |
| rich               | `ListComp (unknown elements)`                |     10 |     10 |        6 |
| rich               | `call: builtin enumerate()`                  |      8 |      6 |        6 |
| rich               | `list (mixed/unknown elements)`              |      7 |      1 |        1 |
| rich               | `binop (one side literal)`                   |      7 |      7 |        7 |
| rich               | `call: builtin getattr()`                    |      7 |      5 |        2 |
| rich               | `copy: other`                                |      6 |      6 |        6 |
| rich               | `call: builtin iter()`                       |      6 |      6 |        6 |
| rich               | `subscript: other`                           |      5 |      3 |        3 |
| rich               | `call: global.method()`                      |      5 |      0 |        0 |
| rich               | `call: builtin zip()`                        |      5 |      5 |        5 |
| rich               | `copy: builtin`                              |      5 |      1 |        1 |
| rich               | `call: imported class`                       |      4 |      1 |        1 |
| rich               | `compare`                                    |      4 |      4 |        4 |
| rich               | `call: builtin list()`                       |      4 |      3 |        3 |
| rich               | `tuple (mixed/unknown elements)`             |      4 |      1 |        1 |
| rich               | `boolop (and)`                               |      4 |      4 |        3 |
| rich               | `call: builtin next()`                       |      4 |      3 |        3 |
| rich               | `call: modclass.method()`                    |      4 |      0 |        0 |
| rich               | `call: other.method()`                       |      4 |      3 |        2 |
| rich               | `call: builtin divmod()`                     |      3 |      3 |        3 |
| rich               | `subscript: imported[...]`                   |      3 |      2 |        2 |
| rich               | `DictComp (unknown elements)`                |      3 |      2 |        2 |
| rich               | `GeneratorExp (unknown elements)`            |      3 |      3 |        3 |
| rich               | `call: builtin tuple()`                      |      3 |      2 |        2 |
| rich               | `call: module function (annotated)`          |      2 |      1 |        1 |
| rich               | `call: builtin sum()`                        |      2 |      2 |        2 |
| rich               | `copy: global`                               |      2 |      1 |        0 |
| rich               | `call: builtin type()`                       |      2 |      1 |        0 |
| rich               | `call: param name`                           |      1 |      1 |        1 |
| rich               | `call: builtin frozenset()`                  |      1 |      0 |        0 |
| rich               | `call: builtin min()`                        |      1 |      1 |        1 |
| rich               | `subscript: self[...]`                       |      1 |      1 |        1 |
| rich               | `None literal`                               |      1 |      1 |        1 |
| rich               | `attr: modclass.x`                           |      1 |      1 |        1 |
| rich               | `subscript: param[...]`                      |      1 |      0 |        0 |
| rich               | `Yield`                                      |      1 |      1 |        1 |
| rich               | `call: cls name`                             |      1 |      1 |        0 |
| rich               | `attr: cls.x`                                |      1 |      1 |        1 |
| rich               | `empty dict`                                 |      1 |      0 |        0 |
| rich               | `attr: module.x`                             |      1 |      1 |        1 |
| urllib3            | `call: chained .method()`                    |     37 |     22 |       17 |
| urllib3            | `call: local.method()`                       |     24 |      7 |        6 |
| urllib3            | `call: module.func()`                        |     21 |      7 |        5 |
| urllib3            | `None literal`                               |     20 |     17 |       17 |
| urllib3            | `call: param.method()`                       |     20 |     11 |        7 |
| urllib3            | `attr: self.x`                               |     12 |     12 |        9 |
| urllib3            | `copy: local`                                |      9 |      6 |        5 |
| urllib3            | `dict (mixed/unknown elements)`              |      8 |      2 |        1 |
| urllib3            | `attr: local.x`                              |      8 |      7 |        5 |
| urllib3            | `copy: param (annotated)`                    |      7 |      7 |        4 |
| urllib3            | `subscript: other`                           |      7 |      4 |        4 |
| urllib3            | `call: imported function`                    |      7 |      6 |        5 |
| urllib3            | `call: self.method()`                        |      6 |      3 |        1 |
| urllib3            | `subscript: param[...]`                      |      6 |      3 |        3 |
| urllib3            | `attr: chained`                              |      5 |      2 |        2 |
| urllib3            | `copy: other`                                |      4 |      0 |        0 |
| urllib3            | `subscript: local[...]`                      |      4 |      2 |        2 |
| urllib3            | `attr: module.x`                             |      4 |      2 |        2 |
| urllib3            | `call: builtin getattr()`                    |      4 |      4 |        1 |
| urllib3            | `call: module function (annotated)`          |      4 |      2 |        2 |
| urllib3            | `copy: modclass`                             |      4 |      0 |        0 |
| urllib3            | `other constant`                             |      4 |      2 |        2 |
| urllib3            | `tuple (mixed/unknown elements)`             |      4 |      3 |        3 |
| urllib3            | `attr: param.x`                              |      4 |      2 |        2 |
| urllib3            | `ListComp (unknown elements)`                |      4 |      2 |        2 |
| urllib3            | `call: local name`                           |      4 |      3 |        3 |
| urllib3            | `call: global.method()`                      |      4 |      4 |        2 |
| urllib3            | `copy: global`                               |      3 |      0 |        0 |
| urllib3            | `call: builtin min()`                        |      3 |      0 |        0 |
| urllib3            | `list (mixed/unknown elements)`              |      3 |      1 |        1 |
| urllib3            | `empty list`                                 |      3 |      0 |        0 |
| urllib3            | `copy: self`                                 |      2 |      2 |        2 |
| urllib3            | `call: builtin enumerate()`                  |      2 |      2 |        2 |
| urllib3            | `call: builtin staticmethod()`               |      2 |      0 |        0 |
| urllib3            | `binop: literal % formatting`                |      2 |      0 |        0 |
| urllib3            | `compare`                                    |      2 |      2 |        2 |
| urllib3            | `boolop (and)`                               |      2 |      2 |        0 |
| urllib3            | `call: builtin dict()`                       |      2 |      0 |        0 |
| urllib3            | `DictComp (unknown elements)`                |      2 |      0 |        0 |
| urllib3            | `copy: imported`                             |      2 |      0 |        0 |
| urllib3            | `attr: global.x`                             |      2 |      0 |        0 |
| urllib3            | `call: builtin bytearray()`                  |      2 |      1 |        1 |
| urllib3            | `call: builtin memoryview()`                 |      2 |      1 |        1 |
| urllib3            | `boolop (or)`                                |      2 |      2 |        2 |
| urllib3            | `conditional`                                |      1 |      1 |        0 |
| urllib3            | `subscript: global[...]`                     |      1 |      0 |        0 |
| urllib3            | `subscript: imported[...]`                   |      1 |      0 |        0 |
| urllib3            | `call: other name`                           |      1 |      1 |        1 |
| urllib3            | `attr: other.x`                              |      1 |      1 |        0 |
| urllib3            | `JoinedStr`                                  |      1 |      0 |        0 |
| urllib3            | `call: imported.attr()`                      |      1 |      1 |        1 |
| urllib3            | `binop (one side literal)`                   |      1 |      0 |        0 |
| urllib3            | `GeneratorExp (unknown elements)`            |      1 |      1 |        1 |
| urllib3            | `call: other.method()`                       |      1 |      1 |        0 |
| urllib3            | `binop (unknown operands)`                   |      1 |      1 |        1 |
| urllib3            | `call: imported class`                       |      1 |      1 |        0 |
| urllib3            | `call: builtin len()`                        |      1 |      1 |        1 |
| sqlmodel           | `call: chained .method()`                    |     19 |     17 |       12 |
| sqlmodel           | `call: imported function`                    |     14 |     11 |        3 |
| sqlmodel           | `call: param.method()`                       |     12 |     11 |        7 |
| sqlmodel           | `call: module function (annotated)`          |     12 |     11 |        7 |
| sqlmodel           | `other constant`                             |      6 |      0 |        0 |
| sqlmodel           | `call: builtin getattr()`                    |      5 |      3 |        2 |
| sqlmodel           | `copy: param (annotated)`                    |      5 |      5 |        0 |
| sqlmodel           | `copy: local`                                |      4 |      4 |        3 |
| sqlmodel           | `copy: imported`                             |      3 |      1 |        1 |
| sqlmodel           | `call: local.method()`                       |      3 |      3 |        3 |
| sqlmodel           | `empty dict`                                 |      3 |      0 |        0 |
| sqlmodel           | `await: call: imported function`             |      2 |      2 |        0 |
| sqlmodel           | `dict (mixed/unknown elements)`              |      2 |      1 |        0 |
| sqlmodel           | `call: other name`                           |      2 |      2 |        0 |
| sqlmodel           | `subscript: other`                           |      2 |      0 |        0 |
| sqlmodel           | `attr: imported.x`                           |      2 |      0 |        0 |
| sqlmodel           | `call: builtin type()`                       |      1 |      0 |        0 |
| sqlmodel           | `conditional`                                |      1 |      1 |        0 |
| sqlmodel           | `attr: param.x`                              |      1 |      1 |        1 |
| sqlmodel           | `boolop (or)`                                |      1 |      0 |        0 |
| sqlmodel           | `DictComp (unknown elements)`                |      1 |      0 |        0 |
| sqlmodel           | `call: other.method()`                       |      1 |      1 |        0 |
| sqlmodel           | `empty list`                                 |      1 |      0 |        0 |
| sqlmodel           | `call: imported class`                       |      1 |      0 |        0 |
| marshmallow        | `dict (mixed/unknown elements)`              |     28 |      0 |        0 |
| marshmallow        | `call: self.method()`                        |     14 |      9 |        3 |
| marshmallow        | `call: param.method()`                       |     12 |      9 |        2 |
| marshmallow        | `call: chained .method()`                    |     11 |     11 |        6 |
| marshmallow        | `subscript: other`                           |      9 |      9 |        7 |
| marshmallow        | `attr: self.x`                               |      9 |      5 |        4 |
| marshmallow        | `conditional`                                |      7 |      6 |        6 |
| marshmallow        | `call: module.func()`                        |      7 |      5 |        2 |
| marshmallow        | `boolop (or)`                                |      6 |      6 |        4 |
| marshmallow        | `empty list`                                 |      6 |      0 |        0 |
| marshmallow        | `call: builtin enumerate()`                  |      6 |      5 |        2 |
| marshmallow        | `copy: local`                                |      6 |      6 |        5 |
| marshmallow        | `other constant`                             |      6 |      0 |        0 |
| marshmallow        | `empty dict`                                 |      5 |      0 |        0 |
| marshmallow        | `attr: module.x`                             |      5 |      0 |        0 |
| marshmallow        | `copy: modclass`                             |      5 |      0 |        0 |
| marshmallow        | `subscript: local[...]`                      |      5 |      3 |        3 |
| marshmallow        | `call: local.method()`                       |      5 |      4 |        3 |
| marshmallow        | `call: builtin getattr()`                    |      5 |      5 |        4 |
| marshmallow        | `ListComp (unknown elements)`                |      4 |      3 |        3 |
| marshmallow        | `copy: builtin`                              |      3 |      0 |        0 |
| marshmallow        | `SetComp (unknown elements)`                 |      3 |      1 |        1 |
| marshmallow        | `call: builtin reversed()`                   |      2 |      2 |        0 |
| marshmallow        | `set (mixed/unknown elements)`               |      2 |      0 |        0 |
| marshmallow        | `DictComp (unknown elements)`                |      2 |      1 |        1 |
| marshmallow        | `call: imported.attr()`                      |      2 |      2 |        2 |
| marshmallow        | `call: imported function`                    |      2 |      1 |        1 |
| marshmallow        | `call: builtin iter()`                       |      2 |      2 |        2 |
| marshmallow        | `tuple (mixed/unknown elements)`             |      2 |      0 |        0 |
| marshmallow        | `call: builtin tuple()`                      |      2 |      2 |        2 |
| marshmallow        | `copy: param (annotated)`                    |      2 |      2 |        1 |
| marshmallow        | `attr: cls.x`                                |      1 |      1 |        1 |
| marshmallow        | `subscript: global[...]`                     |      1 |      1 |        0 |
| marshmallow        | `attr: local.x`                              |      1 |      0 |        0 |
| marshmallow        | `attr: chained`                              |      1 |      0 |        0 |
| marshmallow        | `copy: param (unannotated)`                  |      1 |      1 |        0 |
| marshmallow        | `attr: param.x`                              |      1 |      1 |        0 |
| marshmallow        | `call: module function (annotated)`          |      1 |      1 |        0 |
| marshmallow        | `call: module function (unannotated)`        |      1 |      1 |        0 |
| marshmallow        | `copy: imported`                             |      1 |      0 |        0 |
| marshmallow        | `call: builtin type()`                       |      1 |      1 |        1 |
| marshmallow        | `call: param name`                           |      1 |      1 |        0 |
| marshmallow        | `attr: other.x`                              |      1 |      1 |        1 |
| marshmallow        | `call: capitalised`                          |      1 |      0 |        0 |
| marshmallow        | `binop (unknown operands)`                   |      1 |      1 |        1 |
| pdm                | `call: chained .method()`                    |    144 |    118 |       95 |
| pdm                | `call: local.method()`                       |    107 |     85 |       75 |
| pdm                | `attr: chained`                              |     66 |     53 |       39 |
| pdm                | `call: module.func()`                        |     60 |     39 |       36 |
| pdm                | `call: imported function`                    |     56 |     50 |       48 |
| pdm                | `call: param.method()`                       |     54 |     48 |       37 |
| pdm                | `conditional`                                |     50 |     43 |       25 |
| pdm                | `tuple (mixed/unknown elements)`             |     40 |     12 |        8 |
| pdm                | `call: imported.attr()`                      |     35 |     32 |       27 |
| pdm                | `copy: local`                                |     33 |     28 |       23 |
| pdm                | `attr: local.x`                              |     30 |     25 |       11 |
| pdm                | `boolop (or)`                                |     30 |     27 |       22 |
| pdm                | `subscript: other`                           |     28 |     22 |       20 |
| pdm                | `attr: param.x`                              |     26 |     20 |       15 |
| pdm                | `dict (mixed/unknown elements)`              |     19 |     11 |       10 |
| pdm                | `attr: self.x`                               |     19 |     16 |        7 |
| pdm                | `ListComp (unknown elements)`                |     18 |     11 |       10 |
| pdm                | `other constant`                             |     17 |      3 |        3 |
| pdm                | `binop (unknown operands)`                   |     16 |      9 |        8 |
| pdm                | `copy: param (annotated)`                    |     16 |     13 |        4 |
| pdm                | `call: builtin list()`                       |     16 |     11 |        8 |
| pdm                | `call: builtin sorted()`                     |     15 |     10 |        9 |
| pdm                | `list (mixed/unknown elements)`              |     14 |     11 |       11 |
| pdm                | `call: module function (annotated)`          |     14 |     11 |        9 |
| pdm                | `call: builtin next()`                       |     13 |     11 |        9 |
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
| strawberry-graphql | `call: imported function`                    |     64 |     48 |       14 |
| strawberry-graphql | `attr: chained`                              |     56 |     43 |       31 |
| strawberry-graphql | `call: builtin getattr()`                    |     43 |     31 |       14 |
| strawberry-graphql | `attr: param.x`                              |     42 |     34 |       21 |
| strawberry-graphql | `conditional`                                |     41 |     33 |       11 |
| strawberry-graphql | `call: self.method()`                        |     39 |     20 |       15 |
| strawberry-graphql | `call: local.method()`                       |     39 |     23 |       11 |
| strawberry-graphql | `attr: local.x`                              |     39 |     33 |       19 |
| strawberry-graphql | `subscript: other`                           |     35 |     22 |       18 |
| strawberry-graphql | `copy: local`                                |     28 |     19 |       13 |
| strawberry-graphql | `call: module function (annotated)`          |     23 |     17 |        3 |
| strawberry-graphql | `call: module.func()`                        |     23 |     18 |       12 |
| strawberry-graphql | `call: param.method()`                       |     21 |     11 |        4 |
| strawberry-graphql | `ListComp (unknown elements)`                |     17 |      8 |        4 |
| strawberry-graphql | `empty list`                                 |     17 |      0 |        0 |
| strawberry-graphql | `copy: imported`                             |     16 |      1 |        1 |
| strawberry-graphql | `attr: self.x`                               |     15 |     13 |        5 |
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
| pygments           | `call: imported function`                    |     91 |     25 |       19 |
| pygments           | `call: local.method()`                       |     90 |     68 |       64 |
| pygments           | `call: param.method()`                       |     78 |     74 |       70 |
| pygments           | `attr: module.x`                             |     64 |      0 |        0 |
| pygments           | `call: chained .method()`                    |     63 |     49 |       39 |
| pygments           | `copy: local`                                |     60 |     45 |       41 |
| pygments           | `call: self.method()`                        |     52 |     42 |       37 |
| pygments           | `tuple (mixed/unknown elements)`             |     51 |     11 |       11 |
| pygments           | `attr: self.x`                               |     42 |     35 |       27 |
| pygments           | `empty dict`                                 |     38 |      0 |        0 |
| pygments           | `call: module.func()`                        |     35 |      8 |        8 |
| pygments           | `subscript: local[...]`                      |     29 |     23 |       23 |
| pygments           | `copy: global`                               |     27 |      1 |        1 |
| pygments           | `call: builtin set()`                        |     26 |      0 |        0 |
| pygments           | `None literal`                               |     26 |     17 |       17 |
| pygments           | `other constant`                             |     26 |      0 |        0 |
| pygments           | `list (mixed/unknown elements)`              |     24 |      6 |        6 |
| pygments           | `call: other name`                           |     23 |      3 |        1 |
| pygments           | `call: module function (unannotated)`        |     22 |     14 |        9 |
| pygments           | `subscript: other`                           |     19 |     13 |       13 |
| pygments           | `subscript: global[...]`                     |     17 |      5 |        3 |
| pygments           | `attr: imported.x`                           |     16 |      3 |        3 |
| pygments           | `call: modclass.method()`                    |     16 |     16 |       16 |
| pygments           | `attr: chained`                              |     15 |      8 |        8 |
| pygments           | `attr: param.x`                              |     14 |     14 |       11 |
| pygments           | `attr: global.x`                             |     14 |      0 |        0 |
| pygments           | `call: builtin enumerate()`                  |     13 |      9 |        9 |
| pygments           | `copy: modclass`                             |     13 |      2 |        2 |
| pygments           | `empty tuple`                                |     13 |      0 |        0 |
| pygments           | `call: builtin sorted()`                     |     12 |      2 |        2 |
| pygments           | `boolop (or)`                                |     11 |      9 |        9 |
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
| pygments           | `call: local name`                           |      4 |      3 |        2 |
| pygments           | `attr: modclass.x`                           |      4 |      0 |        0 |
| pygments           | `set (mixed/unknown elements)`               |      4 |      0 |        0 |
| pygments           | `attr: cls.x`                                |      3 |      3 |        2 |
| pygments           | `call: cls.method()`                         |      3 |      2 |        1 |
| pygments           | `boolop (and)`                               |      2 |      2 |        2 |
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
| tox                | `call: chained .method()`                    |    117 |    100 |       85 |
| tox                | `call: local.method()`                       |     40 |     32 |       24 |
| tox                | `call: param.method()`                       |     30 |     28 |       15 |
| tox                | `conditional`                                |     30 |     27 |       22 |
| tox                | `tuple (mixed/unknown elements)`             |     29 |     21 |       17 |
| tox                | `subscript: other`                           |     27 |     22 |       21 |
| tox                | `attr: chained`                              |     27 |     23 |       21 |
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
| tox                | `subscript: local[...]`                      |     10 |      8 |        4 |
| tox                | `attr: local.x`                              |     10 |     10 |        8 |
| tox                | `dict (mixed/unknown elements)`              |      7 |      4 |        4 |
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
| tox                | `attr: param.x`                              |      4 |      4 |        4 |
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
| tox                | `call: builtin vars()`                       |      1 |      0 |        0 |
| tox                | `call: cls.method()`                         |      1 |      1 |        1 |
| tox                | `call: other.method()`                       |      1 |      1 |        1 |
| trio               | `call: imported.attr()`                      |    317 |    293 |      292 |
| trio               | `call: module.func()`                        |    222 |    186 |      183 |
| trio               | `call: module function (annotated)`          |     84 |     44 |       42 |
| trio               | `empty list`                                 |     61 |      0 |        0 |
| trio               | `call: imported class`                       |     48 |     38 |       38 |
| trio               | `call: other callee`                         |     47 |     43 |       43 |
| trio               | `call: imported function`                    |     46 |     30 |       29 |
| trio               | `await: call: local.method()`                |     45 |     40 |       38 |
| trio               | `call: local.method()`                       |     44 |     43 |       35 |
| trio               | `call: other name`                           |     38 |     36 |       35 |
| trio               | `await: call: module function (annotated)`   |     36 |     36 |       36 |
| trio               | `call: chained .method()`                    |     35 |     28 |       18 |
| trio               | `call: param.method()`                       |     29 |     28 |       27 |
| trio               | `await: call: imported function`             |     29 |     29 |       29 |
| trio               | `attr: chained`                              |     27 |     23 |       21 |
| trio               | `copy: local`                                |     25 |     21 |       21 |
| trio               | `subscript: other`                           |     24 |     20 |       18 |
| trio               | `tuple (mixed/unknown elements)`             |     24 |     21 |       15 |
| trio               | `attr: local.x`                              |     21 |     15 |       12 |
| trio               | `call: param name`                           |     18 |     18 |       13 |
| trio               | `copy: param (annotated)`                    |     17 |     16 |       14 |
| trio               | `binop (unknown operands)`                   |     16 |     11 |       10 |
| trio               | `await: call: param.method()`                |     15 |      8 |        6 |
| trio               | `call: builtin set()`                        |     14 |      4 |        2 |
| trio               | `list (mixed/unknown elements)`              |     14 |     13 |        9 |
| trio               | `ListComp (unknown elements)`                |     14 |      5 |        5 |
| trio               | `None literal`                               |     13 |     11 |       11 |
| trio               | `attr: self.x`                               |     12 |     11 |       10 |
| trio               | `call: global.method()`                      |     12 |      9 |        9 |
| trio               | `call: other.method()`                       |     11 |     11 |        9 |
| trio               | `call: builtin getattr()`                    |     11 |     10 |        8 |
| trio               | `call: module class`                         |     10 |     10 |        4 |
| trio               | `subscript: local[...]`                      |     10 |      5 |        5 |
| trio               | `other constant`                             |      9 |      4 |        4 |
| trio               | `await: call: chained .method()`             |      9 |      8 |        8 |
| trio               | `await: call: module.func()`                 |      9 |      9 |        7 |
| trio               | `call: builtin list()`                       |      8 |      7 |        3 |
| trio               | `call: capitalised`                          |      7 |      7 |        7 |
| trio               | `await: call: other.method()`                |      7 |      7 |        6 |
| trio               | `copy: other`                                |      7 |      3 |        3 |
| trio               | `await: call: other name`                    |      7 |      7 |        7 |
| trio               | `copy: imported`                             |      6 |      5 |        5 |
| trio               | `call: self.method()`                        |      5 |      5 |        3 |
| trio               | `await: call: imported.attr()`               |      5 |      2 |        2 |
| trio               | `attr: imported.x`                           |      5 |      3 |        3 |
| trio               | `attr: other.x`                              |      5 |      5 |        5 |
| trio               | `attr: module.x`                             |      5 |      3 |        3 |
| trio               | `attr: param.x`                              |      5 |      5 |        3 |
| trio               | `call: modclass.method()`                    |      4 |      4 |        4 |
| trio               | `call: builtin memoryview()`                 |      4 |      3 |        3 |
| trio               | `await: call: self.method()`                 |      4 |      4 |        3 |
| trio               | `call: builtin next()`                       |      3 |      2 |        2 |
| trio               | `dict (mixed/unknown elements)`              |      3 |      2 |        2 |
| trio               | `subscript: other[...]`                      |      3 |      3 |        3 |
| trio               | `subscript: param[...]`                      |      3 |      3 |        3 |
| trio               | `conditional`                                |      3 |      3 |        3 |
| trio               | `await: call: local name`                    |      3 |      3 |        3 |
| trio               | `call: local name`                           |      3 |      3 |        3 |
| trio               | `set (mixed/unknown elements)`               |      3 |      3 |        3 |
| trio               | `subscript: imported[...]`                   |      2 |      0 |        0 |
| trio               | `subscript: global[...]`                     |      2 |      2 |        2 |
| trio               | `call: builtin enumerate()`                  |      2 |      2 |        1 |
| trio               | `empty dict`                                 |      2 |      0 |        0 |
| trio               | `call: builtin bytearray()`                  |      2 |      2 |        2 |
| trio               | `call: builtin open()`                       |      2 |      2 |        2 |
| trio               | `subscript: builtin[...]`                    |      1 |      0 |        0 |
| trio               | `call: builtin reversed()`                   |      1 |      1 |        1 |
| trio               | `Yield`                                      |      1 |      1 |        1 |
| trio               | `await: call: global name`                   |      1 |      1 |        1 |
| trio               | `unaryop Invert`                             |      1 |      0 |        0 |
| trio               | `compare`                                    |      1 |      1 |        1 |
| trio               | `call: moddef.method()`                      |      1 |      1 |        1 |
| trio               | `call: builtin eval()`                       |      1 |      1 |        1 |
| trio               | `call: builtin object()`                     |      1 |      1 |        1 |
| trio               | `copy: modclass`                             |      1 |      0 |        0 |
| langchain-core     | `call: local.method()`                       |    187 |    159 |      106 |
| langchain-core     | `call: param.method()`                       |    125 |    109 |       66 |
| langchain-core     | `call: imported function`                    |    115 |     95 |       47 |
| langchain-core     | `call: chained .method()`                    |    113 |     75 |       46 |
| langchain-core     | `copy: local`                                |     87 |     71 |       38 |
| langchain-core     | `call: self.method()`                        |     69 |     39 |       19 |
| langchain-core     | `boolop (or)`                                |     56 |     46 |       29 |
| langchain-core     | `dict (mixed/unknown elements)`              |     54 |     37 |       19 |
| langchain-core     | `conditional`                                |     52 |     43 |       22 |
| langchain-core     | `copy: param (annotated)`                    |     50 |     34 |       18 |
| langchain-core     | `call: module function (annotated)`          |     46 |     33 |       12 |
| langchain-core     | `DictComp (unknown elements)`                |     43 |     33 |       22 |
| langchain-core     | `subscript: other`                           |     41 |     37 |       29 |
| langchain-core     | `ListComp (unknown elements)`                |     38 |     29 |       26 |
| langchain-core     | `empty list`                                 |     36 |      0 |        0 |
| langchain-core     | `attr: self.x`                               |     33 |     29 |       13 |
| langchain-core     | `call: module.func()`                        |     31 |     24 |       22 |
| langchain-core     | `call: imported class`                       |     31 |      6 |        6 |
| langchain-core     | `None literal`                               |     29 |     26 |       26 |
| langchain-core     | `list (mixed/unknown elements)`              |     28 |     20 |       16 |
| langchain-core     | `subscript: param[...]`                      |     28 |     23 |       14 |
| langchain-core     | `attr: local.x`                              |     26 |     19 |       13 |
| langchain-core     | `call: builtin enumerate()`                  |     24 |     17 |        4 |
| langchain-core     | `JoinedStr`                                  |     23 |      1 |        1 |
| langchain-core     | `binop (unknown operands)`                   |     22 |      9 |        7 |
| langchain-core     | `attr: chained`                              |     20 |     16 |       14 |
| langchain-core     | `call: builtin getattr()`                    |     19 |     15 |       10 |
| langchain-core     | `other constant`                             |     19 |      7 |        7 |
| langchain-core     | `call: builtin dict()`                       |     17 |     15 |        7 |
| langchain-core     | `subscript: local[...]`                      |     17 |     15 |        8 |
| langchain-core     | `empty dict`                                 |     15 |      0 |        0 |
| langchain-core     | `call: builtin list()`                       |     14 |     11 |       11 |
| langchain-core     | `await: call: imported function`             |     13 |      6 |        3 |
| langchain-core     | `attr: param.x`                              |     12 |     10 |        6 |
| langchain-core     | `await: call: local.method()`                |     11 |      8 |        5 |
| langchain-core     | `call: other name`                           |     10 |      5 |        5 |
| langchain-core     | `call: other.method()`                       |     10 |      5 |        5 |
| langchain-core     | `call: builtin object()`                     |      8 |      5 |        5 |
| langchain-core     | `call: builtin next()`                       |      8 |      7 |        5 |
| langchain-core     | `call: builtin set()`                        |      8 |      4 |        4 |
| langchain-core     | `call: builtin zip()`                        |      8 |      8 |        2 |
| langchain-core     | `call: global.method()`                      |      7 |      7 |        5 |
| langchain-core     | `copy: other`                                |      7 |      5 |        2 |
| langchain-core     | `await: call: module.func()`                 |      6 |      2 |        2 |
| langchain-core     | `copy: imported`                             |      6 |      5 |        5 |
| langchain-core     | `await: call: chained .method()`             |      6 |      5 |        4 |
| langchain-core     | `await: call: self.method()`                 |      6 |      6 |        5 |
| langchain-core     | `SetComp (unknown elements)`                 |      6 |      5 |        5 |
| langchain-core     | `call: other callee`                         |      5 |      4 |        3 |
| langchain-core     | `call: imported.attr()`                      |      4 |      2 |        1 |
| langchain-core     | `await: call: param.method()`                |      4 |      3 |        2 |
| langchain-core     | `compare`                                    |      4 |      3 |        3 |
| langchain-core     | `tuple (mixed/unknown elements)`             |      4 |      4 |        2 |
| langchain-core     | `call: builtin tuple()`                      |      4 |      4 |        2 |
| langchain-core     | `attr: other.x`                              |      4 |      3 |        2 |
| langchain-core     | `copy: modclass`                             |      4 |      0 |        0 |
| langchain-core     | `call: builtin round()`                      |      4 |      4 |        4 |
| langchain-core     | `copy: self`                                 |      3 |      3 |        2 |
| langchain-core     | `boolop (and)`                               |      3 |      3 |        2 |
| langchain-core     | `call: builtin map()`                        |      3 |      2 |        2 |
| langchain-core     | `call: local name`                           |      2 |      1 |        0 |
| langchain-core     | `call: param name`                           |      2 |      2 |        1 |
| langchain-core     | `call: builtin frozenset()`                  |      2 |      1 |        1 |
| langchain-core     | `call: builtin sorted()`                     |      2 |      2 |        2 |
| langchain-core     | `call: module class`                         |      2 |      2 |        2 |
| langchain-core     | `attr: cls.x`                                |      2 |      2 |        2 |
| langchain-core     | `call: builtin type()`                       |      2 |      2 |        0 |
| langchain-core     | `await: call: builtin anext()`               |      2 |      0 |        0 |
| langchain-core     | `call: cls name`                             |      2 |      2 |        2 |
| langchain-core     | `await: call: module function (annotated)`   |      1 |      1 |        1 |
| langchain-core     | `subscript: global[...]`                     |      1 |      1 |        1 |
| langchain-core     | `call: builtin repr()`                       |      1 |      0 |        0 |
| langchain-core     | `subscript: imported[...]`                   |      1 |      1 |        1 |
| langchain-core     | `copy: builtin`                              |      1 |      0 |        0 |
| langchain-core     | `await: call: param name`                    |      1 |      1 |        0 |
| langchain-core     | `GeneratorExp (unknown elements)`            |      1 |      0 |        0 |
| langchain-core     | `subscript: other[...]`                      |      1 |      1 |        1 |
| langchain-core     | `call: builtin min()`                        |      1 |      1 |        1 |
| langchain-core     | `call: str-literal.method()`                 |      1 |      0 |        0 |
| langchain-core     | `call: builtin.method()`                     |      1 |      0 |        0 |
| langchain-core     | `await: copy: local`                         |      1 |      0 |        0 |
| langchain-core     | `call: builtin reversed()`                   |      1 |      1 |        1 |
| langchain-core     | `await: call: other.method()`                |      1 |      0 |        0 |
| langchain-core     | `attr: module.x`                             |      1 |      0 |        0 |
| langchain-core     | `unaryop USub`                               |      1 |      1 |        1 |
| langchain-core     | `call: builtin max()`                        |      1 |      1 |        1 |
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
| altair             | `call: chained .method()`                    |     57 |     27 |       16 |
| altair             | `call: param.method()`                       |     46 |     42 |       32 |
| altair             | `call: local.method()`                       |     46 |     38 |       17 |
| altair             | `call: module function (annotated)`          |     23 |     19 |       13 |
| altair             | `call: module.func()`                        |     22 |     13 |       11 |
| altair             | `copy: param (annotated)`                    |     21 |     15 |        9 |
| altair             | `call: imported function`                    |     20 |     14 |       14 |
| altair             | `conditional`                                |     17 |     12 |       10 |
| altair             | `call: builtin getattr()`                    |     15 |     13 |        5 |
| altair             | `call: imported.attr()`                      |     12 |      8 |        7 |
| altair             | `attr: param.x`                              |     12 |     11 |        8 |
| altair             | `copy: local`                                |     11 |      9 |        4 |
| altair             | `attr: local.x`                              |     10 |      6 |        4 |
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
| seaborn            | `call: self.method()`                        |    149 |    137 |       97 |
| seaborn            | `call: module.func()`                        |    139 |    116 |      110 |
| seaborn            | `call: local.method()`                       |    125 |    110 |       91 |
| seaborn            | `call: chained .method()`                    |    124 |    112 |       96 |
| seaborn            | `call: param.method()`                       |    124 |    117 |       69 |
| seaborn            | `call: imported function`                    |     89 |     73 |       58 |
| seaborn            | `tuple (mixed/unknown elements)`             |     81 |     58 |       46 |
| seaborn            | `binop (unknown operands)`                   |     79 |     70 |       56 |
| seaborn            | `subscript: other`                           |     70 |     62 |       52 |
| seaborn            | `copy: param (unannotated)`                  |     68 |     48 |       25 |
| seaborn            | `copy: local`                                |     59 |     48 |       31 |
| seaborn            | `empty list`                                 |     55 |      0 |        0 |
| seaborn            | `attr: self.x`                               |     49 |     47 |       20 |
| seaborn            | `conditional`                                |     48 |     42 |       26 |
| seaborn            | `ListComp (unknown elements)`                |     45 |     44 |       40 |
| seaborn            | `subscript: local[...]`                      |     42 |     39 |       29 |
| seaborn            | `attr: chained`                              |     41 |     33 |       30 |
| seaborn            | `call: local name`                           |     39 |     39 |       36 |
| seaborn            | `subscript: imported[...]`                   |     33 |      1 |        0 |
| seaborn            | `dict (mixed/unknown elements)`              |     32 |     30 |       12 |
| seaborn            | `empty dict`                                 |     30 |      0 |        0 |
| seaborn            | `binop (one side literal)`                   |     30 |     21 |       19 |
| seaborn            | `call: builtin getattr()`                    |     29 |     24 |       10 |
| seaborn            | `call: builtin enumerate()`                  |     29 |     25 |       21 |
| seaborn            | `call: builtin zip()`                        |     29 |     28 |       23 |
| seaborn            | `subscript: param[...]`                      |     26 |     25 |       21 |
| seaborn            | `None literal`                               |     25 |     12 |       12 |
| seaborn            | `call: param name`                           |     25 |     25 |       18 |
| seaborn            | `list (mixed/unknown elements)`              |     25 |     21 |       17 |
| seaborn            | `DictComp (unknown elements)`                |     25 |     22 |       18 |
| seaborn            | `call: builtin dict()`                       |     24 |     22 |       10 |
| seaborn            | `other constant`                             |     20 |      9 |        9 |
| seaborn            | `call: imported.attr()`                      |     19 |     14 |       13 |
| seaborn            | `call: module function (unannotated)`        |     16 |     15 |        5 |
| seaborn            | `compare`                                    |     14 |     12 |       10 |
| seaborn            | `attr: local.x`                              |     13 |     13 |       13 |
| seaborn            | `call: other name`                           |     12 |      7 |        6 |
| seaborn            | `attr: param.x`                              |     10 |      8 |        7 |
| seaborn            | `boolop (or)`                                |      9 |      9 |        7 |
| seaborn            | `call: builtin min()`                        |      8 |      7 |        4 |
| seaborn            | `boolop (and)`                               |      7 |      6 |        5 |
| seaborn            | `call: builtin tuple()`                      |      7 |      6 |        1 |
| seaborn            | `subscript: self[...]`                       |      7 |      3 |        3 |
| seaborn            | `call: builtin list()`                       |      6 |      6 |        5 |
| seaborn            | `attr: module.x`                             |      6 |      6 |        6 |
| seaborn            | `copy: param (annotated)`                    |      5 |      5 |        3 |
| seaborn            | `call: builtin max()`                        |      5 |      5 |        4 |
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
| seaborn            | `call: builtin reversed()`                   |      1 |      1 |        0 |
| seaborn            | `call: builtin slice()`                      |      1 |      1 |        1 |
| seaborn            | `copy: builtin`                              |      1 |      0 |        0 |
| seaborn            | `call: builtin str()`                        |      1 |      0 |        0 |
| seaborn            | `call: builtin map()`                        |      1 |      1 |        1 |
| seaborn            | `call: self name`                            |      1 |      1 |        1 |
| aiohttp            | `call: chained .method()`                    |    106 |    100 |       69 |
| aiohttp            | `attr: self.x`                               |     80 |     76 |       39 |
| aiohttp            | `other constant`                             |     74 |      2 |        2 |
| aiohttp            | `call: local.method()`                       |     66 |     59 |       43 |
| aiohttp            | `call: module.func()`                        |     43 |     28 |       28 |
| aiohttp            | `attr: local.x`                              |     34 |     32 |       21 |
| aiohttp            | `copy: local`                                |     27 |     27 |       22 |
| aiohttp            | `attr: chained`                              |     25 |     14 |       12 |
| aiohttp            | `conditional`                                |     25 |     23 |       13 |
| aiohttp            | `attr: param.x`                              |     25 |     23 |        9 |
| aiohttp            | `tuple (mixed/unknown elements)`             |     19 |     12 |       10 |
| aiohttp            | `subscript: other`                           |     18 |     17 |       17 |
| aiohttp            | `call: self.method()`                        |     16 |     14 |       10 |
| aiohttp            | `call: param.method()`                       |     16 |     16 |       10 |
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
| zarr               | `call: local.method()`                       |     52 |     44 |       27 |
| zarr               | `copy: local`                                |     50 |     36 |       26 |
| zarr               | `call: self.method()`                        |     42 |     28 |       14 |
| zarr               | `attr: chained`                              |     41 |     18 |       17 |
| zarr               | `subscript: param[...]`                      |     31 |     30 |       26 |
| zarr               | `call: builtin tuple()`                      |     31 |     25 |       24 |
| zarr               | `subscript: other`                           |     29 |     22 |       21 |
| zarr               | `subscript: local[...]`                      |     25 |     20 |       11 |
| zarr               | `call: module function (annotated)`          |     23 |     18 |        6 |
| zarr               | `other constant`                             |     22 |      8 |        8 |
| zarr               | `await: call: chained .method()`             |     22 |     14 |        3 |
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
| joblib             | `call: imported function`                    |    118 |     19 |       16 |
| joblib             | `call: imported.attr()`                      |    109 |      7 |        4 |
| joblib             | `call: local.method()`                       |    106 |      8 |        6 |
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
| networkx           | `call: module.func()`                        |  4,473 |    582 |      502 |
| networkx           | `call: local.method()`                       |    791 |    401 |      301 |
| networkx           | `call: imported function`                    |    725 |    200 |      141 |
| networkx           | `copy: local`                                |    667 |    468 |      343 |
| networkx           | `call: param.method()`                       |    603 |    482 |      373 |
| networkx           | `copy: param (unannotated)`                  |    503 |    372 |      215 |
| networkx           | `call: module function (unannotated)`        |    474 |    346 |      255 |
| networkx           | `call: chained .method()`                    |    451 |    215 |      160 |
| networkx           | `binop (unknown operands)`                   |    383 |    317 |      276 |
| networkx           | `call: builtin list()`                       |    373 |    150 |      104 |
| networkx           | `call: self.method()`                        |    333 |    113 |       55 |
| networkx           | `subscript: other`                           |    326 |    213 |      149 |
| networkx           | `subscript: local[...]`                      |    307 |    263 |      202 |
| networkx           | `attr: self.x`                               |    296 |     75 |       34 |
| networkx           | `list (mixed/unknown elements)`              |    276 |     97 |       64 |
| networkx           | `call: builtin set()`                        |    274 |    121 |       82 |
| networkx           | `ListComp (unknown elements)`                |    267 |    159 |      112 |
| networkx           | `call: builtin sorted()`                     |    256 |     42 |       35 |
| networkx           | `DictComp (unknown elements)`                |    219 |    117 |       54 |
| networkx           | `empty dict`                                 |    219 |      0 |        0 |
| networkx           | `tuple (mixed/unknown elements)`             |    218 |    126 |       86 |
| networkx           | `empty list`                                 |    198 |      0 |        0 |
| networkx           | `call: global.method()`                      |    170 |      0 |        0 |
| networkx           | `dict (mixed/unknown elements)`              |    169 |     74 |       46 |
| networkx           | `call: local name`                           |    168 |     73 |       62 |
| networkx           | `call: imported.attr()`                      |    157 |      4 |        4 |
| networkx           | `call: param name`                           |    157 |     21 |       15 |
| networkx           | `call: builtin zip()`                        |    144 |     72 |       50 |
| networkx           | `subscript: param[...]`                      |    142 |    113 |       87 |
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
| networkx           | `call: builtin enumerate()`                  |     87 |     71 |       48 |
| networkx           | `call: builtin next()`                       |     79 |     67 |       44 |
| networkx           | `attr: chained`                              |     79 |     30 |       27 |
| networkx           | `other constant`                             |     69 |     53 |       53 |
| networkx           | `call: builtin.method()`                     |     61 |     40 |       28 |
| networkx           | `call: builtin min()`                        |     60 |     56 |       43 |
| networkx           | `None literal`                               |     60 |     50 |       50 |
| networkx           | `copy: global`                               |     58 |      0 |        0 |
| networkx           | `call: capitalised`                          |     53 |      6 |        5 |
| networkx           | `call: builtin max()`                        |     47 |     43 |       38 |
| networkx           | `set (mixed/unknown elements)`               |     45 |     29 |       12 |
| networkx           | `copy: other`                                |     32 |     19 |        9 |
| networkx           | `call: other.method()`                       |     32 |     25 |       17 |
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
| networkx           | `call: builtin compile()`                    |      1 |      1 |        1 |
| networkx           | `call: builtin getattr()`                    |      1 |      0 |        0 |
| networkx           | `call: cls name`                             |      1 |      0 |        0 |
| nibabel            | `call: module.func()`                        |    549 |    130 |      119 |
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
| nibabel            | `attr: chained`                              |     83 |     15 |       11 |
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
| nibabel            | `copy: modclass`                             |     24 |      0 |        0 |
| nibabel            | `call: global.method()`                      |     24 |      3 |        1 |
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
| narwhals           | `call: imported function`                    |    204 |    127 |       90 |
| narwhals           | `attr: chained`                              |    135 |    113 |       89 |
| narwhals           | `conditional`                                |    133 |    117 |       72 |
| narwhals           | `call: module.func()`                        |    129 |    113 |      108 |
| narwhals           | `call: local.method()`                       |     98 |     87 |       69 |
| narwhals           | `attr: self.x`                               |     93 |     86 |       77 |
| narwhals           | `call: self.method()`                        |     84 |     71 |       61 |
| narwhals           | `call: param.method()`                       |     80 |     51 |       30 |
| narwhals           | `ListComp (unknown elements)`                |     65 |     50 |       38 |
| narwhals           | `tuple (mixed/unknown elements)`             |     59 |     50 |       32 |
| narwhals           | `call: module function (annotated)`          |     55 |     34 |       32 |
| narwhals           | `attr: param.x`                              |     45 |     41 |       30 |
| narwhals           | `binop (unknown operands)`                   |     38 |     31 |       31 |
| narwhals           | `call: imported class`                       |     38 |      7 |        7 |
| narwhals           | `GeneratorExp (unknown elements)`            |     28 |     22 |       22 |
| narwhals           | `attr: local.x`                              |     27 |     23 |       22 |
| narwhals           | `attr: imported.x`                           |     24 |      1 |        1 |
| narwhals           | `call: builtin list()`                       |     19 |     15 |       15 |
| narwhals           | `call: other.method()`                       |     19 |     17 |       10 |
| narwhals           | `copy: param (annotated)`                    |     18 |     18 |        9 |
| narwhals           | `copy: local`                                |     18 |     16 |       12 |
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
| xarray             | `call: chained .method()`                    |  1,400 |    170 |      111 |
| xarray             | `call: module.func()`                        |  1,369 |    105 |      101 |
| xarray             | `call: imported function`                    |    933 |    175 |      122 |
| xarray             | `call: local.method()`                       |    915 |    103 |       72 |
| xarray             | `binop (unknown operands)`                   |    737 |     94 |       77 |
| xarray             | `call: self.method()`                        |    449 |    105 |       93 |
| xarray             | `call: module function (unannotated)`        |    392 |     64 |       43 |
| xarray             | `call: param.method()`                       |    333 |    151 |      105 |
| xarray             | `subscript: local[...]`                      |    298 |     31 |       24 |
| xarray             | `subscript: other`                           |    250 |     41 |       34 |
| xarray             | `attr: chained`                              |    236 |     44 |       35 |
| xarray             | `dict (mixed/unknown elements)`              |    204 |     10 |        8 |
| xarray             | `ListComp (unknown elements)`                |    203 |     73 |       61 |
| xarray             | `call: imported.attr()`                      |    179 |     51 |       31 |
| xarray             | `call: param name`                           |    170 |      6 |        4 |
| xarray             | `list (mixed/unknown elements)`              |    162 |     20 |       18 |
| xarray             | `conditional`                                |    149 |     56 |       38 |
| xarray             | `DictComp (unknown elements)`                |    148 |     56 |       41 |
| xarray             | `copy: local`                                |    148 |     55 |       42 |
| xarray             | `call: builtin zip()`                        |    144 |     47 |       33 |
| xarray             | `attr: local.x`                              |    131 |     43 |       33 |
| xarray             | `empty dict`                                 |    120 |      0 |        0 |
| xarray             | `copy: param (unannotated)`                  |    116 |     40 |       29 |
| xarray             | `call: local name`                           |    116 |      6 |        3 |
| xarray             | `binop (one side literal)`                   |    108 |      9 |        9 |
| xarray             | `call: imported class`                       |    101 |      5 |        4 |
| xarray             | `attr: self.x`                               |     86 |     40 |       32 |
| xarray             | `call: module function (annotated)`          |     84 |     27 |       18 |
| xarray             | `call: builtin tuple()`                      |     83 |     45 |       38 |
| xarray             | `attr: param.x`                              |     82 |     33 |       26 |
| xarray             | `call: builtin getattr()`                    |     80 |     31 |       18 |
| xarray             | `empty list`                                 |     80 |      0 |        0 |
| xarray             | `call: other name`                           |     80 |     10 |       10 |
| xarray             | `subscript: param[...]`                      |     76 |     28 |       12 |
| xarray             | `call: builtin dict()`                       |     73 |     13 |        5 |
| xarray             | `call: other callee`                         |     65 |      9 |        3 |
| xarray             | `tuple (mixed/unknown elements)`             |     61 |      9 |        7 |
| xarray             | `call: builtin set()`                        |     55 |     20 |       17 |
| xarray             | `compare`                                    |     53 |     19 |       17 |
| xarray             | `other constant`                             |     52 |      1 |        1 |
| xarray             | `copy: param (annotated)`                    |     44 |     26 |       18 |
| xarray             | `call: global.method()`                      |     41 |      1 |        1 |
| xarray             | `call: builtin list()`                       |     40 |     17 |       14 |
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
| xarray             | `call: builtin next()`                       |     16 |     11 |        6 |
| xarray             | `call: builtin.method()`                     |     14 |      8 |        7 |
| xarray             | `boolop (and)`                               |     12 |      4 |        3 |
| xarray             | `call: builtin sorted()`                     |     11 |      5 |        3 |
| xarray             | `call: modclass.method()`                    |     10 |      0 |        0 |
| xarray             | `copy: other`                                |     10 |      2 |        2 |
| xarray             | `copy: self`                                 |     10 |      7 |        7 |
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
| litestar           | `conditional`                                |     63 |     59 |       36 |
| litestar           | `call: local.method()`                       |     57 |     43 |       28 |
| litestar           | `subscript: other`                           |     56 |     50 |       32 |
| litestar           | `call: param.method()`                       |     54 |     36 |       22 |
| litestar           | `call: builtin getattr()`                    |     47 |     43 |       15 |
| litestar           | `attr: chained`                              |     36 |     32 |       19 |
| litestar           | `attr: self.x`                               |     34 |     32 |       12 |
| litestar           | `await: call: self.method()`                 |     33 |     31 |       25 |
| litestar           | `call: self.method()`                        |     33 |     29 |       19 |
| litestar           | `attr: param.x`                              |     28 |     19 |        6 |
| litestar           | `attr: local.x`                              |     28 |     20 |       12 |
| litestar           | `copy: local`                                |     25 |     20 |       16 |
| litestar           | `boolop (or)`                                |     24 |     21 |       17 |
| litestar           | `call: module function (annotated)`          |     23 |     20 |        4 |
| litestar           | `copy: param (annotated)`                    |     21 |     18 |       12 |
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
| litestar           | `SetComp (unknown elements)`                 |      6 |      3 |        3 |
| litestar           | `binop (unknown operands)`                   |      6 |      4 |        4 |
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
| optuna             | `call: module.func()`                        |    278 |    230 |      221 |
| optuna             | `call: chained .method()`                    |    209 |    155 |      118 |
| optuna             | `call: imported.attr()`                      |    108 |     41 |       41 |
| optuna             | `binop (unknown operands)`                   |     87 |     76 |       74 |
| optuna             | `call: imported function`                    |     79 |      5 |        3 |
| optuna             | `empty list`                                 |     71 |      0 |        0 |
| optuna             | `attr: param.x`                              |     65 |     59 |       50 |
| optuna             | `call: local.method()`                       |     62 |     34 |       28 |
| optuna             | `subscript: other`                           |     54 |     44 |       36 |
| optuna             | `call: module function (annotated)`          |     39 |     34 |       33 |
| optuna             | `subscript: param[...]`                      |     35 |     35 |       33 |
| optuna             | `call: builtin zip()`                        |     35 |     24 |       18 |
| optuna             | `call: imported class`                       |     35 |      0 |        0 |
| optuna             | `call: param.method()`                       |     33 |     17 |       14 |
| optuna             | `subscript: local[...]`                      |     32 |     28 |       24 |
| optuna             | `ListComp (unknown elements)`                |     32 |     23 |       21 |
| optuna             | `attr: chained`                              |     31 |     19 |       15 |
| optuna             | `binop (one side literal)`                   |     28 |     26 |       26 |
| optuna             | `conditional`                                |     28 |     20 |       13 |
| optuna             | `None literal`                               |     28 |      5 |        5 |
| optuna             | `attr: local.x`                              |     28 |     16 |       13 |
| optuna             | `tuple (mixed/unknown elements)`             |     24 |     15 |       12 |
| optuna             | `compare`                                    |     23 |     22 |       22 |
| optuna             | `empty dict`                                 |     20 |      0 |        0 |
| optuna             | `call: global.method()`                      |     20 |      0 |        0 |
| optuna             | `copy: local`                                |     18 |      6 |        6 |
| optuna             | `call: builtin enumerate()`                  |     15 |      8 |        7 |
| optuna             | `call: other name`                           |     13 |      8 |        8 |
| optuna             | `other constant`                             |     12 |      4 |        4 |
| optuna             | `DictComp (unknown elements)`                |     11 |      6 |        0 |
| optuna             | `copy: param (annotated)`                    |     11 |      6 |        4 |
| optuna             | `list (mixed/unknown elements)`              |     10 |      5 |        5 |
| optuna             | `unaryop USub`                               |      9 |      9 |        8 |
| optuna             | `call: self.method()`                        |      9 |      7 |        4 |
| optuna             | `call: builtin max()`                        |      9 |      4 |        2 |
| optuna             | `attr: self.x`                               |      8 |      8 |        4 |
| optuna             | `dict (mixed/unknown elements)`              |      7 |      2 |        2 |
| optuna             | `call: builtin getattr()`                    |      6 |      4 |        4 |
| optuna             | `call: builtin set()`                        |      6 |      5 |        5 |
| optuna             | `unaryop Invert`                             |      5 |      4 |        4 |
| optuna             | `subscript: imported[...]`                   |      5 |      0 |        0 |
| optuna             | `call: builtin list()`                       |      4 |      1 |        1 |
| optuna             | `copy: other`                                |      4 |      3 |        2 |
| optuna             | `call: builtin tuple()`                      |      4 |      0 |        0 |
| optuna             | `boolop (or)`                                |      3 |      1 |        1 |
| optuna             | `copy: global`                               |      2 |      1 |        0 |
| optuna             | `subscript: other[...]`                      |      2 |      2 |        2 |
| optuna             | `boolop (and)`                               |      2 |      2 |        0 |
| optuna             | `copy: imported`                             |      2 |      1 |        1 |
| optuna             | `call: builtin next()`                       |      2 |      2 |        0 |
| optuna             | `attr: imported.x`                           |      2 |      1 |        1 |
| optuna             | `call: param name`                           |      2 |      2 |        1 |
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
| dask               | `call: module.func()`                        |  3,970 |    194 |      181 |
| dask               | `call: imported function`                    |  1,742 |    333 |      246 |
| dask               | `call: local.method()`                       |  1,382 |    163 |      104 |
| dask               | `call: chained .method()`                    |  1,381 |    180 |      148 |
| dask               | `call: global.method()`                      |    908 |     11 |        9 |
| dask               | `call: module function (unannotated)`        |    491 |    216 |      151 |
| dask               | `call: param.method()`                       |    470 |    213 |      144 |
| dask               | `dict (mixed/unknown elements)`              |    446 |     57 |       46 |
| dask               | `binop (unknown operands)`                   |    405 |    213 |      169 |
| dask               | `copy: param (unannotated)`                  |    390 |    160 |      104 |
| dask               | `list (mixed/unknown elements)`              |    366 |     58 |       32 |
| dask               | `ListComp (unknown elements)`                |    350 |    194 |      141 |
| dask               | `subscript: other`                           |    333 |     89 |       67 |
| dask               | `empty list`                                 |    296 |      0 |        0 |
| dask               | `tuple (mixed/unknown elements)`             |    269 |     83 |       73 |
| dask               | `subscript: local[...]`                      |    247 |     99 |       71 |
| dask               | `call: builtin zip()`                        |    235 |    119 |       92 |
| dask               | `copy: local`                                |    232 |    113 |       83 |
| dask               | `call: builtin list()`                       |    211 |    109 |       84 |
| dask               | `binop (one side literal)`                   |    195 |     27 |       27 |
| dask               | `empty dict`                                 |    193 |      0 |        0 |
| dask               | `subscript: param[...]`                      |    180 |    113 |       86 |
| dask               | `attr: chained`                              |    178 |     75 |       54 |
| dask               | `DictComp (unknown elements)`                |    168 |     89 |       66 |
| dask               | `call: module class`                         |    168 |      6 |        5 |
| dask               | `attr: self.x`                               |    166 |    129 |       61 |
| dask               | `call: other callee`                         |    152 |     22 |       14 |
| dask               | `conditional`                                |    148 |     80 |       44 |
| dask               | `call: builtin getattr()`                    |    146 |     33 |       19 |
| dask               | `call: local name`                           |    143 |     34 |       18 |
| dask               | `attr: local.x`                              |    141 |     67 |       54 |
| dask               | `call: builtin enumerate()`                  |    135 |     92 |       67 |
| dask               | `call: param name`                           |    131 |     25 |       10 |
| dask               | `call: self.method()`                        |    129 |    111 |       60 |
| dask               | `attr: imported.x`                           |    112 |      1 |        1 |
| dask               | `other constant`                             |    100 |     26 |       26 |
| dask               | `attr: param.x`                              |     98 |     66 |       47 |
| dask               | `call: builtin tuple()`                      |     96 |     58 |       44 |
| dask               | `call: builtin set()`                        |     83 |     21 |       15 |
| dask               | `call: builtin staticmethod()`               |     79 |      0 |        0 |
| dask               | `call: builtin dict()`                       |     72 |     19 |        9 |
| dask               | `call: imported.attr()`                      |     70 |     36 |       23 |
| dask               | `None literal`                               |     67 |     36 |       36 |
| dask               | `attr: module.x`                             |     59 |      1 |        1 |
| dask               | `boolop (or)`                                |     56 |     46 |       38 |
| dask               | `Lambda`                                     |     53 |      3 |        3 |
| dask               | `call: other name`                           |     51 |     20 |       14 |
| dask               | `compare`                                    |     48 |     18 |       17 |
| dask               | `call: imported class`                       |     46 |     10 |       10 |
| dask               | `call: module function (annotated)`          |     31 |     28 |        9 |
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
| dask               | `copy: param (annotated)`                    |     14 |     13 |        7 |
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
| dask               | `call: builtin any()`                        |      1 |      1 |        1 |
| dask               | `await: call: chained .method()`             |      1 |      0 |        0 |
| dask               | `call: builtin reversed()`                   |      1 |      1 |        1 |
| dask               | `call: builtin len()`                        |      1 |      1 |        1 |
| dask               | `call: builtin frozenset()`                  |      1 |      1 |        0 |
| dask               | `await: call: local.method()`                |      1 |      0 |        0 |
| mypy               | `call: imported function`                    |    391 |    279 |      102 |
| mypy               | `call: chained .method()`                    |    309 |    206 |      140 |
| mypy               | `attr: chained`                              |    249 |    168 |      132 |
| mypy               | `copy: local`                                |    234 |    152 |       97 |
| mypy               | `empty list`                                 |    223 |      0 |        0 |
| mypy               | `attr: local.x`                              |    222 |    132 |       95 |
| mypy               | `attr: param.x`                              |    208 |    174 |       95 |
| mypy               | `subscript: other`                           |    194 |    122 |       76 |
| mypy               | `call: local.method()`                       |    168 |    110 |       79 |
| mypy               | `call: self.method()`                        |    143 |    105 |       58 |
| mypy               | `call: param.method()`                       |     96 |     78 |       46 |
| mypy               | `None literal`                               |     91 |     66 |       66 |
| mypy               | `conditional`                                |     89 |     59 |       33 |
| mypy               | `ListComp (unknown elements)`                |     84 |     50 |       34 |
| mypy               | `binop (unknown operands)`                   |     75 |     34 |       27 |
| mypy               | `call: module.func()`                        |     73 |     27 |       17 |
| mypy               | `call: module function (annotated)`          |     70 |     45 |       21 |
| mypy               | `call: builtin zip()`                        |     70 |     50 |       22 |
| mypy               | `attr: self.x`                               |     62 |     53 |       37 |
| mypy               | `copy: param (annotated)`                    |     61 |     52 |       36 |
| mypy               | `subscript: local[...]`                      |     58 |     41 |       26 |
| mypy               | `subscript: param[...]`                      |     56 |     34 |       27 |
| mypy               | `call: builtin enumerate()`                  |     49 |     45 |       21 |
| mypy               | `tuple (mixed/unknown elements)`             |     48 |     31 |       24 |
| mypy               | `boolop (or)`                                |     47 |     33 |       29 |
| mypy               | `other constant`                             |     42 |     11 |       11 |
| mypy               | `call: builtin set()`                        |     40 |      8 |        7 |
| mypy               | `boolop (and)`                               |     33 |     28 |       26 |
| mypy               | `call: builtin sorted()`                     |     32 |     11 |       11 |
| mypy               | `list (mixed/unknown elements)`              |     32 |     12 |        8 |
| mypy               | `call: imported.attr()`                      |     27 |     19 |       13 |
| mypy               | `empty dict`                                 |     27 |      0 |        0 |
| mypy               | `SetComp (unknown elements)`                 |     27 |     14 |       13 |
| mypy               | `call: builtin list()`                       |     23 |     12 |        9 |
| mypy               | `DictComp (unknown elements)`                |     22 |     13 |        9 |
| mypy               | `call: builtin getattr()`                    |     21 |     15 |        8 |
| mypy               | `call: global.method()`                      |     17 |      1 |        1 |
| mypy               | `binop (one side literal)`                   |     16 |      4 |        4 |
| mypy               | `attr: imported.x`                           |     15 |      7 |        7 |
| mypy               | `copy: imported`                             |     15 |      5 |        5 |
| mypy               | `call: other name`                           |     13 |     10 |        9 |
| mypy               | `attr: module.x`                             |     11 |      0 |        0 |
| mypy               | `dict (mixed/unknown elements)`              |     11 |      6 |        4 |
| mypy               | `compare`                                    |      8 |      7 |        7 |
| mypy               | `copy: global`                               |      8 |      2 |        2 |
| mypy               | `call: imported class`                       |      8 |      7 |        7 |
| mypy               | `subscript: imported[...]`                   |      7 |      6 |        5 |
| mypy               | `call: local name`                           |      7 |      2 |        0 |
| mypy               | `call: builtin next()`                       |      6 |      4 |        3 |
| mypy               | `call: builtin dict()`                       |      5 |      1 |        1 |
| mypy               | `call: builtin open()`                       |      4 |      1 |        1 |
| mypy               | `call: builtin reversed()`                   |      4 |      0 |        0 |
| mypy               | `subscript: global[...]`                     |      4 |      4 |        3 |
| mypy               | `GeneratorExp (unknown elements)`            |      4 |      4 |        4 |
| mypy               | `call: modclass.method()`                    |      4 |      4 |        4 |
| mypy               | `copy: other`                                |      3 |      3 |        3 |
| mypy               | `call: builtin any()`                        |      3 |      3 |        3 |
| mypy               | `JoinedStr`                                  |      3 |      0 |        0 |
| mypy               | `subscript: other[...]`                      |      3 |      3 |        2 |
| mypy               | `call: builtin tuple()`                      |      3 |      1 |        1 |
| mypy               | `attr: modclass.x`                           |      2 |      1 |        1 |
| mypy               | `call: param name`                           |      2 |      1 |        0 |
| mypy               | `call: builtin type()`                       |      2 |      2 |        1 |
| mypy               | `call: builtin.method()`                     |      2 |      1 |        0 |
| mypy               | `call: builtin format()`                     |      2 |      1 |        1 |
| mypy               | `set (mixed/unknown elements)`               |      2 |      2 |        2 |
| mypy               | `call: other.method()`                       |      2 |      2 |        1 |
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
| requests           | released (from alt-11-08-2026-1133)   |                  | 617 passed, 15 skipped, 1 xpassed                                     |              |      |       |              |                 |
| requests           | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| requests           | infer-union                           | True             | 617 passed, 15 skipped, 1 xpassed                                     |            0 |    0 |     0 |            0 |               0 |
| rich               | released (from mega-11-16-2026-1443)  |                  | 956 passed, 25 skipped                                                |              |      |       |              |                 |
| rich               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| rich               | infer-union                           | True             | 956 passed, 25 skipped                                                |            0 |    0 |     0 |            0 |               0 |
| urllib3            | released (from alt-11-08-2026-1157)   |                  | 2,418 passed, 288 skipped, 4 xfailed                                  |              |      |       |              |                 |
| urllib3            | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| urllib3            | infer-union                           | True             | 2,418 passed, 288 skipped, 4 xfailed                                  |            0 |    0 |     0 |            0 |               0 |
| sqlmodel           | released (from alt-11-08-2026-1157)   |                  | 1 failed, 267 passed                                                  |              |      |       |              |                 |
| sqlmodel           | fix-certain                           | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | fix-likely                            | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | infer-basedpyright                    | True             | as infer-ty's (implied)                                               |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | infer-pyrefly                         | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | infer-trace                           | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | infer-ty                              | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| sqlmodel           | infer-union                           | True             | 2 failed, 266 passed                                                  |            0 |    0 |     1 |            0 |               0 |
| marshmallow        | released (from alt-11-08-2026-1133)   |                  | 1,188 passed                                                          |              |      |       |              |                 |
| marshmallow        | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| marshmallow        | infer-union                           | True             | 1,188 passed                                                          |            0 |    0 |     0 |            0 |               0 |
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
| sphinx             | released                              |                  | 8 failed, 2,393 passed, 23 skipped                                    |              |      |       |              |                 |
| sphinx             | fix-certain                           | True             | 8 failed, 2,393 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-likely                            | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-basedpyright                    | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-pyrefly                         | True             | 8 failed, 2,393 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-trace                           | True             | 7 failed, 2,394 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
| sphinx             | infer-ty                              | True             | 8 failed, 2,393 passed, 23 skipped                                    |            0 |    0 |     0 |            0 |               0 |
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
| trio               | released (from alt-11-08-2026-1133)   |                  | 871 passed, 23 skipped, 3 xfailed                                     |              |      |       |              |                 |
| trio               | fix-certain                           | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | fix-likely                            | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | fix-unsafe                            | True             | as infer-trace's (implied)                                            |            0 |    0 |     1 |            0 |               0 |
| trio               | infer-basedpyright                    | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | infer-pyrefly                         | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | infer-trace                           | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | infer-ty                              | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| trio               | infer-union                           | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed                           |            0 |    0 |     1 |            0 |               0 |
| langchain-core     | released                              |                  | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed              |              |      |       |              |                 |
| langchain-core     | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| langchain-core     | infer-union                           | True             | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed              |            0 |    0 |     0 |            0 |               0 |
| pint               | released (from mega-10-26-2026-2120)  |                  | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |              |      |       |              |                 |
| pint               | fix-certain                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | fix-likely                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | fix-unsafe                            | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-basedpyright                    | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-pyrefly                         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-trace                           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-ty                              | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |            0 |               0 |
| pint               | infer-union                           | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |            0 |               0 |
| altair             | released (from mega-11-10-2026-2235)  |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |              |                 |
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
| websockets         | released (from mega-11-11-2026-1113)  |                  | 2,589 ran, 8 skipped                                                  |              |      |       |              |                 |
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
| zarr               | released                              |                  | 8,422 passed, 1,205 skipped, 4 xfailed                                |              |      |       |              |                 |
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
| nibabel            | released                              |                  | 19 error, 108 failed, 5,169 passed, 303 skipped, 40 xfailed           |              |      |       |              |                 |
| nibabel            | fix-certain                           | True             | 19 error, 109 failed, 5,168 passed, 303 skipped, 40 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | fix-likely                            | True             | 19 error, 109 failed, 5,168 passed, 303 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | fix-unsafe                            | True             | 20 error, 107 failed, 5,169 passed, 303 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-basedpyright                    | True             | 20 error, 108 failed, 5,169 passed, 303 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | infer-pyrefly                         | True             | 19 error, 110 failed, 5,168 passed, 303 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
| nibabel            | infer-trace                           | True             | 21 error, 108 failed, 5,168 passed, 303 skipped, 40 xfailed           |            0 |    0 |     2 |            0 |               0 |
| nibabel            | infer-ty                              | True             | 19 error, 108 failed, 5,169 passed, 303 skipped, 41 xfailed           |            0 |    0 |     1 |            0 |               0 |
| nibabel            | infer-union                           | True             | 19 error, 109 failed, 5,168 passed, 303 skipped, 40 xfailed           |            0 |    0 |     0 |            0 |               0 |
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
| sqlalchemy         | fix-certain        |      1 |   1 |    0 |    183 files changed, 2267 insertions(+), 1723 deletions(-) |
| sqlalchemy         | fix-likely         |      1 |   1 |    0 |    193 files changed, 2732 insertions(+), 2143 deletions(-) |
| sqlalchemy         | fix-unsafe         |      1 |   1 |    0 |    206 files changed, 3446 insertions(+), 2819 deletions(-) |
| sqlalchemy         | infer-basedpyright |      4 |   4 |    0 |    210 files changed, 4191 insertions(+), 3518 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      4 |   4 |    0 |    211 files changed, 4456 insertions(+), 3562 deletions(-) |
| sqlalchemy         | infer-trace        |      7 |   7 |    0 |    208 files changed, 3649 insertions(+), 2959 deletions(-) |
| sqlalchemy         | infer-ty           |      3 |   3 |    0 |    208 files changed, 4141 insertions(+), 3363 deletions(-) |
| sqlalchemy         | infer-union        |     11 |  11 |    0 |    214 files changed, 4828 insertions(+), 3840 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1699 insertions(+), 1285 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1699 insertions(+), 1285 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1699 insertions(+), 1285 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1932 insertions(+), 1500 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 2021 insertions(+), 1461 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1699 insertions(+), 1285 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1876 insertions(+), 1445 deletions(-) |
| pydantic           | infer-union        |      3 |   3 |    0 |     79 files changed, 2031 insertions(+), 1527 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    261 |   3 |    1 | 1078 files changed, 19366 insertions(+), 15962 deletions(-) |
| pandas             | fix-likely         |    261 |   3 |    1 | 1205 files changed, 44004 insertions(+), 39925 deletions(-) |
| pandas             | fix-unsafe         |    268 |  10 |    1 | 1209 files changed, 45202 insertions(+), 40937 deletions(-) |
| pandas             | infer-basedpyright |    290 |  32 |    1 | 1217 files changed, 51317 insertions(+), 46421 deletions(-) |
| pandas             | infer-pyrefly      |    292 |  34 |    1 | 1221 files changed, 53625 insertions(+), 48321 deletions(-) |
| pandas             | infer-trace        |    268 |  10 |    1 | 1213 files changed, 46719 insertions(+), 42330 deletions(-) |
| pandas             | infer-ty           |    274 |  16 |    1 | 1219 files changed, 50904 insertions(+), 46033 deletions(-) |
| pandas             | infer-union        |    308 |  50 |    1 | 1226 files changed, 55647 insertions(+), 50170 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 165 insertions(+), 129 deletions(-) |
| structlog          | infer-union        |      8 |   0 |    0 |       16 files changed, 174 insertions(+), 130 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 468 insertions(+), 365 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 350 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 461 insertions(+), 360 deletions(-) |
| click              | infer-union        |      0 |   0 |    0 |       15 files changed, 473 insertions(+), 369 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 244 insertions(+), 172 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 244 insertions(+), 172 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 244 insertions(+), 172 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 244 insertions(+), 172 deletions(-) |
| hypercorn          | infer-pyrefly      |     14 |   2 |    0 |       26 files changed, 268 insertions(+), 174 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 244 insertions(+), 172 deletions(-) |
| hypercorn          | infer-ty           |     14 |   2 |    0 |       25 files changed, 252 insertions(+), 173 deletions(-) |
| hypercorn          | infer-union        |     14 |   2 |    0 |       26 files changed, 273 insertions(+), 178 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 557 insertions(+), 437 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 557 insertions(+), 437 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 557 insertions(+), 437 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 557 insertions(+), 437 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 536 insertions(+), 413 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 557 insertions(+), 437 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 534 insertions(+), 415 deletions(-) |
| starlette          | infer-union        |      0 |   0 |    0 |       33 files changed, 571 insertions(+), 439 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 906 insertions(+), 595 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 575 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 849 insertions(+), 582 deletions(-) |
| werkzeug           | infer-union        |      0 |   0 |    0 |       45 files changed, 916 insertions(+), 604 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 418 insertions(+), 347 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       17 files changed, 415 insertions(+), 325 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 325 insertions(+), 268 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 401 insertions(+), 322 deletions(-) |
| httpx              | infer-union        |      1 |   1 |    0 |       17 files changed, 451 insertions(+), 353 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       29 files changed, 409 insertions(+), 305 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       29 files changed, 409 insertions(+), 305 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       29 files changed, 409 insertions(+), 305 deletions(-) |
| uvicorn            | infer-basedpyright |      4 |   4 |    0 |       29 files changed, 405 insertions(+), 312 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       29 files changed, 409 insertions(+), 305 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       29 files changed, 409 insertions(+), 305 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 388 insertions(+), 299 deletions(-) |
| uvicorn            | infer-union        |      4 |   4 |    0 |       29 files changed, 420 insertions(+), 315 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 974 insertions(+), 693 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 974 insertions(+), 693 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1071 insertions(+), 768 deletions(-) |
| mcp                | infer-basedpyright |      1 |   1 |    0 |      84 files changed, 1290 insertions(+), 965 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      85 files changed, 1350 insertions(+), 967 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1071 insertions(+), 768 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      84 files changed, 1308 insertions(+), 936 deletions(-) |
| mcp                | infer-union        |      1 |   1 |    0 |      85 files changed, 1366 insertions(+), 979 deletions(-) |
| requests           | released           |      0 |     |      |                                                             |
| requests           | fix-certain        |      0 |   0 |    0 |        13 files changed, 119 insertions(+), 77 deletions(-) |
| requests           | fix-likely         |      0 |   0 |    0 |        13 files changed, 119 insertions(+), 77 deletions(-) |
| requests           | fix-unsafe         |      0 |   0 |    0 |        13 files changed, 119 insertions(+), 77 deletions(-) |
| requests           | infer-basedpyright |     17 |  17 |    0 |       13 files changed, 233 insertions(+), 176 deletions(-) |
| requests           | infer-pyrefly      |     10 |  10 |    0 |       13 files changed, 254 insertions(+), 174 deletions(-) |
| requests           | infer-trace        |      0 |   0 |    0 |        13 files changed, 119 insertions(+), 77 deletions(-) |
| requests           | infer-ty           |     10 |  10 |    0 |       13 files changed, 235 insertions(+), 162 deletions(-) |
| requests           | infer-union        |     17 |  17 |    0 |       13 files changed, 259 insertions(+), 179 deletions(-) |
| rich               | released           |      0 |     |      |                                                             |
| rich               | fix-certain        |      2 |   2 |    0 |      62 files changed, 1077 insertions(+), 680 deletions(-) |
| rich               | fix-likely         |      5 |   5 |    0 |      92 files changed, 1389 insertions(+), 971 deletions(-) |
| rich               | fix-unsafe         |      5 |   5 |    0 |     93 files changed, 1540 insertions(+), 1090 deletions(-) |
| rich               | infer-basedpyright |      6 |   6 |    0 |     93 files changed, 1873 insertions(+), 1390 deletions(-) |
| rich               | infer-pyrefly      |      7 |   7 |    0 |     93 files changed, 1920 insertions(+), 1311 deletions(-) |
| rich               | infer-trace        |      5 |   5 |    0 |     93 files changed, 1540 insertions(+), 1090 deletions(-) |
| rich               | infer-ty           |      7 |   7 |    0 |     93 files changed, 1830 insertions(+), 1284 deletions(-) |
| rich               | infer-union        |     10 |  10 |    0 |     93 files changed, 2021 insertions(+), 1403 deletions(-) |
| urllib3            | released           |      6 |     |      |                                                             |
| urllib3            | fix-certain        |      6 |   0 |    0 |       28 files changed, 310 insertions(+), 249 deletions(-) |
| urllib3            | fix-likely         |      6 |   0 |    0 |       28 files changed, 310 insertions(+), 249 deletions(-) |
| urllib3            | fix-unsafe         |      7 |   1 |    0 |       28 files changed, 348 insertions(+), 282 deletions(-) |
| urllib3            | infer-basedpyright |     15 |   9 |    0 |       29 files changed, 430 insertions(+), 351 deletions(-) |
| urllib3            | infer-pyrefly      |     19 |  13 |    0 |       29 files changed, 450 insertions(+), 351 deletions(-) |
| urllib3            | infer-trace        |      7 |   1 |    0 |       28 files changed, 348 insertions(+), 282 deletions(-) |
| urllib3            | infer-ty           |     18 |  12 |    0 |       29 files changed, 435 insertions(+), 348 deletions(-) |
| urllib3            | infer-union        |     20 |  14 |    0 |       29 files changed, 462 insertions(+), 362 deletions(-) |
| marshmallow        | released           |      0 |     |      |                                                             |
| marshmallow        | fix-certain        |      0 |   0 |    0 |         9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow        | fix-likely         |      0 |   0 |    0 |         9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow        | fix-unsafe         |      0 |   0 |    0 |         9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow        | infer-basedpyright |      2 |   2 |    0 |         9 files changed, 119 insertions(+), 99 deletions(-) |
| marshmallow        | infer-pyrefly      |      0 |   0 |    0 |        9 files changed, 125 insertions(+), 104 deletions(-) |
| marshmallow        | infer-trace        |      0 |   0 |    0 |         9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow        | infer-ty           |      0 |   0 |    0 |         9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow        | infer-union        |      2 |   2 |    0 |        9 files changed, 126 insertions(+), 105 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |     153 files changed, 1002 insertions(+), 743 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |     153 files changed, 1002 insertions(+), 743 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |     153 files changed, 1002 insertions(+), 743 deletions(-) |
| strawberry-graphql | infer-basedpyright |     12 |   2 |    0 |     156 files changed, 1173 insertions(+), 884 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     12 |   2 |    0 |     155 files changed, 1172 insertions(+), 878 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |     153 files changed, 1002 insertions(+), 743 deletions(-) |
| strawberry-graphql | infer-ty           |     10 |   0 |    0 |     156 files changed, 1176 insertions(+), 882 deletions(-) |
| strawberry-graphql | infer-union        |     13 |   3 |    0 |     156 files changed, 1217 insertions(+), 909 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    190 files changed, 2063 insertions(+), 1431 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |    179 files changed, 1986 insertions(+), 1307 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |    177 files changed, 1669 insertions(+), 1103 deletions(-) |
| streamlink         | infer-ty           |      0 |   0 |    0 |    178 files changed, 1950 insertions(+), 1285 deletions(-) |
| streamlink         | infer-union        |      0 |   0 |    0 |    190 files changed, 2166 insertions(+), 1457 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    196 files changed, 3475 insertions(+), 2361 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    198 files changed, 4018 insertions(+), 2792 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    213 files changed, 4440 insertions(+), 3143 deletions(-) |
| sphinx             | infer-basedpyright |      6 |   3 |    0 |    216 files changed, 5231 insertions(+), 3852 deletions(-) |
| sphinx             | infer-pyrefly      |      5 |   2 |    0 |    217 files changed, 5467 insertions(+), 3902 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    213 files changed, 4440 insertions(+), 3143 deletions(-) |
| sphinx             | infer-ty           |      4 |   1 |    0 |    217 files changed, 5341 insertions(+), 3869 deletions(-) |
| sphinx             | infer-union        |      6 |   3 |    0 |    217 files changed, 5521 insertions(+), 3951 deletions(-) |
| trio               | released           |      1 |     |      |                                                             |
| trio               | fix-certain        |      1 |   0 |    0 |    107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio               | fix-likely         |      1 |   0 |    0 |     107 files changed, 1441 insertions(+), 996 deletions(-) |
| trio               | fix-unsafe         |      1 |   0 |    0 |    107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio               | infer-basedpyright |      1 |   0 |    0 |    114 files changed, 1807 insertions(+), 1301 deletions(-) |
| trio               | infer-pyrefly      |      1 |   0 |    0 |    114 files changed, 2043 insertions(+), 1346 deletions(-) |
| trio               | infer-trace        |      1 |   0 |    0 |    107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio               | infer-ty           |      1 |   0 |    0 |    114 files changed, 1932 insertions(+), 1282 deletions(-) |
| trio               | infer-union        |      1 |   0 |    0 |    115 files changed, 2076 insertions(+), 1374 deletions(-) |
| langchain-core     | released           |      0 |     |      |                                                             |
| langchain-core     | fix-certain        |      1 |   1 |    0 |    147 files changed, 1787 insertions(+), 1335 deletions(-) |
| langchain-core     | fix-likely         |      1 |   1 |    0 |    150 files changed, 1994 insertions(+), 1503 deletions(-) |
| langchain-core     | fix-unsafe         |      1 |   1 |    0 |    150 files changed, 2108 insertions(+), 1594 deletions(-) |
| langchain-core     | infer-basedpyright |      2 |   2 |    0 |    152 files changed, 2372 insertions(+), 1825 deletions(-) |
| langchain-core     | infer-pyrefly      |      7 |   7 |    0 |    152 files changed, 2475 insertions(+), 1847 deletions(-) |
| langchain-core     | infer-trace        |      1 |   1 |    0 |    150 files changed, 2108 insertions(+), 1594 deletions(-) |
| langchain-core     | infer-ty           |      1 |   1 |    0 |    151 files changed, 2382 insertions(+), 1805 deletions(-) |
| langchain-core     | infer-union        |      7 |   7 |    0 |    152 files changed, 2515 insertions(+), 1874 deletions(-) |
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | fix-unsafe         |    659 |   0 |    0 |      78 files changed, 1025 insertions(+), 759 deletions(-) |
| pint               | infer-basedpyright |    661 |   2 |    0 |      81 files changed, 1326 insertions(+), 984 deletions(-) |
| pint               | infer-pyrefly      |    660 |   1 |    0 |     81 files changed, 1470 insertions(+), 1043 deletions(-) |
| pint               | infer-trace        |    662 |   3 |    0 |      78 files changed, 1038 insertions(+), 764 deletions(-) |
| pint               | infer-ty           |    660 |   2 |    1 |      79 files changed, 1204 insertions(+), 899 deletions(-) |
| pint               | infer-union        |    664 |   6 |    1 |     81 files changed, 1536 insertions(+), 1078 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 479 insertions(+), 381 deletions(-) |
| altair             | infer-basedpyright |      5 |   4 |    0 |       40 files changed, 578 insertions(+), 454 deletions(-) |
| altair             | infer-pyrefly      |      4 |   3 |    0 |       40 files changed, 599 insertions(+), 458 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 489 insertions(+), 388 deletions(-) |
| altair             | infer-ty           |      4 |   3 |    0 |       40 files changed, 561 insertions(+), 440 deletions(-) |
| altair             | infer-union        |      6 |   5 |    0 |       40 files changed, 620 insertions(+), 474 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |       46 files changed, 869 insertions(+), 654 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |       46 files changed, 869 insertions(+), 654 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |      46 files changed, 1046 insertions(+), 808 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      47 files changed, 1128 insertions(+), 874 deletions(-) |
| seaborn            | infer-pyrefly      |     39 |   0 |    0 |      47 files changed, 1160 insertions(+), 881 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |      47 files changed, 1011 insertions(+), 763 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |      46 files changed, 1046 insertions(+), 808 deletions(-) |
| seaborn            | infer-union        |     39 |   0 |    0 |      48 files changed, 1311 insertions(+), 999 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 378 insertions(+), 250 deletions(-) |
| websockets         | fix-likely         |      1 |   1 |    0 |       39 files changed, 467 insertions(+), 323 deletions(-) |
| websockets         | fix-unsafe         |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 639 insertions(+), 467 deletions(-) |
| websockets         | infer-pyrefly      |      4 |   4 |    0 |       40 files changed, 642 insertions(+), 462 deletions(-) |
| websockets         | infer-trace        |      1 |   1 |    0 |       39 files changed, 526 insertions(+), 360 deletions(-) |
| websockets         | infer-ty           |      4 |   4 |    0 |       40 files changed, 651 insertions(+), 467 deletions(-) |
| websockets         | infer-union        |      5 |   5 |    0 |       40 files changed, 670 insertions(+), 485 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    460 files changed, 6611 insertions(+), 5628 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    460 files changed, 6611 insertions(+), 5628 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    460 files changed, 6611 insertions(+), 5628 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    476 files changed, 7949 insertions(+), 6601 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    472 files changed, 7458 insertions(+), 6201 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    476 files changed, 7148 insertions(+), 5917 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    466 files changed, 7164 insertions(+), 6026 deletions(-) |
| networkx           | infer-union        |      0 |   0 |    0 |    488 files changed, 8942 insertions(+), 7127 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    184 files changed, 2090 insertions(+), 1393 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    195 files changed, 2951 insertions(+), 2157 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    200 files changed, 3313 insertions(+), 2460 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    203 files changed, 3982 insertions(+), 3005 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    204 files changed, 4672 insertions(+), 3488 deletions(-) |
| nibabel            | infer-trace        |     14 |   2 |    0 |    200 files changed, 3411 insertions(+), 2526 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    201 files changed, 3923 insertions(+), 2942 deletions(-) |
| nibabel            | infer-union        |     18 |   6 |    0 |    205 files changed, 4945 insertions(+), 3700 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     20 |   1 |    0 |     100 files changed, 1132 insertions(+), 929 deletions(-) |
| narwhals           | fix-likely         |     20 |   1 |    0 |    100 files changed, 1212 insertions(+), 1001 deletions(-) |
| narwhals           | fix-unsafe         |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-basedpyright |     22 |   3 |    0 |    101 files changed, 1897 insertions(+), 1558 deletions(-) |
| narwhals           | infer-pyrefly      |     34 |  15 |    0 |    102 files changed, 1868 insertions(+), 1490 deletions(-) |
| narwhals           | infer-trace        |     21 |   2 |    0 |    101 files changed, 1277 insertions(+), 1045 deletions(-) |
| narwhals           | infer-ty           |     34 |  15 |    0 |    102 files changed, 1811 insertions(+), 1460 deletions(-) |
| narwhals           | infer-union        |     39 |  20 |    0 |    102 files changed, 2012 insertions(+), 1613 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-basedpyright |     88 |   2 |    0 |     178 files changed, 1158 insertions(+), 836 deletions(-) |
| litestar           | infer-pyrefly      |     94 |   8 |    0 |     178 files changed, 1233 insertions(+), 851 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      172 files changed, 897 insertions(+), 626 deletions(-) |
| litestar           | infer-ty           |     91 |   5 |    0 |     179 files changed, 1163 insertions(+), 832 deletions(-) |
| litestar           | infer-union        |     90 |   4 |    0 |     178 files changed, 1250 insertions(+), 866 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    141 files changed, 1693 insertions(+), 1166 deletions(-) |
| optuna             | fix-likely         |     53 |   1 |    0 |    144 files changed, 1916 insertions(+), 1355 deletions(-) |
| optuna             | fix-unsafe         |     54 |   2 |    0 |    144 files changed, 2043 insertions(+), 1450 deletions(-) |
| optuna             | infer-basedpyright |     54 |   2 |    0 |    164 files changed, 2436 insertions(+), 1773 deletions(-) |
| optuna             | infer-pyrefly      |     58 |   6 |    0 |    164 files changed, 2687 insertions(+), 1960 deletions(-) |
| optuna             | infer-trace        |     54 |   2 |    0 |    144 files changed, 2043 insertions(+), 1450 deletions(-) |
| optuna             | infer-ty           |     56 |   4 |    0 |    162 files changed, 2439 insertions(+), 1767 deletions(-) |
| optuna             | infer-union        |     58 |   6 |    0 |    164 files changed, 2753 insertions(+), 2002 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    161 files changed, 6040 insertions(+), 3684 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    167 files changed, 7344 insertions(+), 4811 deletions(-) |
| mypy               | fix-unsafe         |     14 |  14 |    0 |    168 files changed, 7804 insertions(+), 5192 deletions(-) |
| mypy               | infer-basedpyright |     20 |  20 |    0 |    170 files changed, 9543 insertions(+), 6744 deletions(-) |
| mypy               | infer-pyrefly      |     20 |  20 |    0 |   170 files changed, 10083 insertions(+), 6899 deletions(-) |
| mypy               | infer-trace        |     14 |  14 |    0 |    168 files changed, 7804 insertions(+), 5192 deletions(-) |
| mypy               | infer-ty           |     19 |  19 |    0 |    170 files changed, 9851 insertions(+), 6917 deletions(-) |
| mypy               | infer-union        |     23 |  23 |    0 |   170 files changed, 10174 insertions(+), 6959 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    50.8 |       128.7 |  2.5 |    3.73 |          3 |     4.69 | False |
| standard library   | fix-certain              |   146.2 |       367.4 |  2.5 |    5.07 |          3 |      6.3 | False |
| standard library   | fix-likely               |   203.5 |       482.7 |  2.4 |    6.97 |          3 |     8.74 | False |
| standard library   | fix-unsafe               |   157.6 |       434.7 |  2.8 |    6.92 |          3 |     8.65 | False |
| standard library   | infer-basedpyright       |   822.5 |      1315.8 |  1.6 |   14.37 |          2 |    17.42 | False |
| standard library   | infer-ty                 |   273.2 |       745.6 |  2.7 |   14.26 |          3 |    15.75 | False |
| standard library   | infer-pyrefly            |   232.4 |       653.5 |  2.8 |    16.4 |          3 |    15.04 | False |
| standard library   | census                   |    32.8 |        32.0 |  1.0 |    0.48 |          3 |     4.69 | False |
| standard library   | coverage                 |    10.0 |        35.4 |  3.5 |    0.78 |          4 |     0.97 | False |
| standard library   | timing                   |   215.5 |       269.1 |  1.2 |    3.69 |          2 |     4.62 | False |
| django             | check                    |     7.2 |         0.3 |  0.0 |    0.06 |          3 |     1.35 | False |
| django             | fix-certain              |    26.3 |        65.1 |  2.5 |     1.4 |          3 |     1.75 | False |
| django             | fix-likely               |    24.0 |        67.0 |  2.8 |    1.79 |          3 |     2.24 | False |
| django             | fix-unsafe               |    58.6 |        84.2 |  1.4 |    1.69 |          2 |     2.24 | False |
| django             | infer-basedpyright       |   160.7 |       355.8 |  2.2 |    6.31 |          1 |     3.49 | False |
| django             | infer-ty                 |   104.4 |       154.8 |  1.5 |     3.9 |          1 |     1.17 | False |
| django             | infer-pyrefly            |    78.3 |       129.8 |  1.7 |    4.19 |          1 |     2.39 | False |
| django             | census                   |    11.2 |        23.7 |  2.1 |    1.08 |          3 |     1.35 | False |
| django             | coverage                 |     2.0 |         5.8 |  2.9 |    0.34 |          3 |     0.42 | False |
| django             | timing                   |    46.1 |        56.8 |  1.2 |    1.08 |          2 |     1.35 | False |
| django             | traced                   |    99.6 |       614.9 |  6.2 |    6.96 |          7 |     8.79 | False |
| django             | tests-released           |    64.9 |       484.9 |  7.5 |    5.42 |          8 |     7.98 | False |
| django             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.04 |          8 |     5.44 | False |
| django             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     4.21 | False |
| django             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          8 |     8.47 | False |
| django             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.04 |          9 |      5.8 | False |
| django             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     8.58 | False |
| django             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.04 |          9 |     6.58 | False |
| django             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.04 |         11 |      7.1 | False |
| django             | infer-union              |   155.2 |       475.7 |  3.1 |    5.69 |          4 |     6.29 | False |
| django             | tests-infer-union        |    65.7 |       446.0 |  6.8 |    5.27 |          8 |      7.1 | False |
| django             | tests                    |     3.0 |         2.7 |  0.9 |    0.17 |          2 |     0.21 | False |
| sqlalchemy         | check                    |     7.6 |         0.3 |  0.0 |    0.06 |          2 |     1.11 | False |
| sqlalchemy         | fix-certain              |    30.5 |        58.9 |  1.9 |    1.02 |          3 |     1.26 | False |
| sqlalchemy         | fix-likely               |    36.1 |        74.5 |  2.1 |    1.33 |          3 |     1.66 | False |
| sqlalchemy         | fix-unsafe               |    55.3 |        77.6 |  1.4 |    1.25 |          3 |      1.6 | False |
| sqlalchemy         | infer-basedpyright       |   130.9 |       311.3 |  2.4 |     6.9 |          1 |     1.67 | False |
| sqlalchemy         | infer-ty                 |    78.8 |       149.9 |  1.9 |    3.96 |          1 |     0.84 | False |
| sqlalchemy         | infer-pyrefly            |    63.3 |       110.0 |  1.7 |    3.87 |          1 |     1.67 | False |
| sqlalchemy         | census                   |    13.0 |        23.7 |  1.8 |    0.89 |          2 |     1.11 | False |
| sqlalchemy         | coverage                 |     4.4 |         7.7 |  1.8 |    0.37 |          3 |     0.46 | False |
| sqlalchemy         | timing                   |    27.8 |        37.5 |  1.3 |    0.89 |          2 |     1.11 | False |
| sqlalchemy         | traced                   |   141.9 |      1200.4 |  8.5 |    6.41 |         10 |     8.04 | False |
| sqlalchemy         | tests-released           |   127.7 |       914.7 |  7.2 |     5.2 |          8 |     7.06 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     8.11 | False |
| sqlalchemy         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.99 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.27 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          9 |      6.6 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.45 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.14 | False |
| sqlalchemy         | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |         11 |      7.4 | False |
| sqlalchemy         | infer-union              |   133.1 |       313.3 |  2.4 |    6.07 |          3 |     6.96 | False |
| sqlalchemy         | tests-infer-union        |   164.0 |       783.1 |  4.8 |     4.6 |          8 |     6.12 | False |
| sqlalchemy         | tests                    |     2.0 |         1.8 |  0.9 |    0.17 |          2 |     0.21 | False |
| sqlalchemy         | types-released           |    12.7 |         6.8 |  0.5 |    0.35 |          1 |     0.44 | False |
| sqlalchemy         | types-fix-certain        |     8.8 |         6.4 |  0.7 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-likely         |    10.4 |         6.9 |  0.7 |    0.32 |          1 |      0.4 | False |
| sqlalchemy         | types-fix-unsafe         |     6.6 |         6.2 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-basedpyright |     9.2 |         7.4 |  0.8 |    0.33 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |    12.1 |         7.6 |  0.6 |    0.31 |          1 |     0.41 | False |
| sqlalchemy         | types-infer-pyrefly      |    13.0 |         8.2 |  0.6 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-trace        |     4.4 |         4.2 |  1.0 |    0.32 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     1.8 |         3.9 |  2.2 |    0.32 |          2 |      0.4 | False |
| pydantic           | fix-certain              |     5.2 |        12.4 |  2.4 |    0.42 |          2 |     0.52 | False |
| pydantic           | fix-likely               |     5.0 |        12.7 |  2.5 |     0.5 |          3 |     0.62 | False |
| pydantic           | fix-unsafe               |     7.8 |        16.7 |  2.1 |    0.45 |          3 |     0.56 | False |
| pydantic           | infer-basedpyright       |    51.1 |       101.4 |  2.0 |    2.94 |          1 |     0.32 | False |
| pydantic           | infer-ty                 |    19.3 |        36.6 |  1.9 |    1.84 |          1 |     0.36 | False |
| pydantic           | infer-pyrefly            |    18.7 |        36.4 |  1.9 |    2.06 |          1 |     0.32 | False |
| pydantic           | census                   |     1.6 |         0.9 |  0.6 |    0.05 |          2 |      0.4 | False |
| pydantic           | coverage                 |     1.0 |         2.1 |  2.1 |    0.22 |          2 |     0.27 | False |
| pydantic           | timing                   |     4.6 |         6.7 |  1.5 |    0.32 |          2 |      0.4 | False |
| pydantic           | traced                   |    82.4 |        70.6 |  0.9 |    0.59 |          1 |     0.72 | False |
| pydantic           | tests-released           |    69.1 |        44.1 |  0.6 |    0.29 |          1 |      0.4 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pydantic           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.35 | False |
| pydantic           | infer-union              |    44.1 |        88.9 |  2.0 |    2.36 |          1 |     0.29 | False |
| pydantic           | tests-infer-union        |    60.5 |        44.1 |  0.7 |    0.33 |          1 |      0.4 | False |
| pydantic           | tests                    |     3.6 |         3.0 |  0.8 |    0.17 |          1 |     0.21 | False |
| pydantic           | types-released           |    10.6 |        15.1 |  1.4 |    0.54 |          2 |     0.67 | False |
| pydantic           | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |          2 |     0.67 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pydantic           | types-infer-basedpyright |    15.8 |        20.0 |  1.3 |    0.55 |          2 |     0.66 | False |
| pydantic           | types-infer-ty           |    11.6 |        17.0 |  1.5 |    0.56 |          2 |     0.67 | False |
| pydantic           | types-infer-pyrefly      |    11.8 |        16.7 |  1.4 |    0.54 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |    16.2 |        19.3 |  1.2 |    0.56 |          2 |     0.69 | False |
| pydantic           | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |    30.8 |         0.9 |  0.0 |     0.2 |          3 |     4.76 | False |
| pandas             | fix-certain              |   154.5 |       406.2 |  2.6 |    4.48 |          3 |      5.6 | False |
| pandas             | fix-likely               |   272.7 |       696.0 |  2.6 |    7.09 |          3 |     8.86 | False |
| pandas             | fix-unsafe               |   243.9 |       664.5 |  2.7 |     7.0 |          2 |     8.74 | False |
| pandas             | infer-basedpyright       |   612.7 |      1458.2 |  2.4 |   13.07 |          2 |     5.36 | False |
| pandas             | infer-ty                 |   449.2 |      1444.0 |  3.2 |   11.97 |          1 |     2.74 | False |
| pandas             | infer-pyrefly            |   283.5 |       851.9 |  3.0 |   13.82 |          2 |     5.47 | False |
| pandas             | census                   |    73.1 |       178.2 |  2.4 |    3.79 |          3 |     4.76 | False |
| pandas             | coverage                 |     7.2 |        22.4 |  3.1 |     0.8 |          4 |      1.0 | False |
| pandas             | timing                   |   292.0 |       351.9 |  1.2 |    3.79 |          2 |     4.74 | False |
| pandas             | traced                   |   309.3 |      1469.9 |  4.8 |    14.4 |          6 |    18.58 | False |
| pandas             | tests-released           |   111.0 |       673.0 |  6.1 |   11.49 |          9 |    14.08 | False |
| pandas             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |    17.44 | False |
| pandas             | tests-fix-likely         |     0.3 |         0.1 |  0.3 |    0.03 |          7 |     17.4 | False |
| pandas             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    17.29 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |    16.67 | False |
| pandas             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          6 |    16.67 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |    16.67 | False |
| pandas             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |    14.48 | False |
| pandas             | infer-union              |   638.2 |      2087.8 |  3.3 |   12.75 |          4 |    13.34 | False |
| pandas             | tests-infer-union        |   153.4 |       834.0 |  5.4 |   13.52 |          6 |    16.67 | False |
| pandas             | tests                    |     3.4 |         2.7 |  0.8 |    0.17 |          2 |      0.2 | False |
| pandas             | types-released           |    92.8 |       109.7 |  1.2 |    2.12 |          2 |     2.74 | False |
| pandas             | types-fix-certain        |    64.1 |        99.7 |  1.6 |    2.35 |          2 |     2.84 | False |
| pandas             | types-fix-likely         |    59.0 |        91.3 |  1.5 |     2.3 |          2 |     2.85 | False |
| pandas             | types-fix-unsafe         |    71.3 |       102.7 |  1.4 |    2.26 |          2 |     2.97 | False |
| pandas             | types-infer-basedpyright |    51.5 |        82.8 |  1.6 |     2.3 |          2 |     2.72 | False |
| pandas             | types-infer-ty           |    59.5 |        89.5 |  1.5 |    2.28 |          2 |     2.75 | False |
| pandas             | types-infer-pyrefly      |    63.9 |        97.1 |  1.5 |    2.32 |          2 |      2.8 | False |
| pandas             | types-infer-trace        |    57.8 |        92.1 |  1.6 |    2.26 |          2 |     2.81 | False |
| pandas             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     8.0 |        18.7 |  2.3 |    0.83 |          3 |     1.06 | False |
| twisted            | fix-certain              |    14.4 |        43.8 |  3.0 |    0.97 |          3 |     1.21 | False |
| twisted            | fix-likely               |    22.9 |        61.5 |  2.7 |    1.31 |          2 |     1.62 | False |
| twisted            | fix-unsafe               |    20.4 |        57.7 |  2.8 |    1.26 |          3 |     1.55 | False |
| twisted            | infer-basedpyright       |   114.7 |       273.9 |  2.4 |    6.14 |          1 |     2.82 | False |
| twisted            | infer-ty                 |    60.3 |       122.3 |  2.0 |    3.61 |          1 |     1.99 | False |
| twisted            | infer-pyrefly            |    50.2 |       101.4 |  2.0 |    3.64 |          1 |     2.31 | False |
| twisted            | census                   |     3.6 |         3.4 |  0.9 |    0.12 |          3 |     1.06 | False |
| twisted            | coverage                 |     4.6 |         8.1 |  1.8 |    0.37 |          2 |     0.46 | False |
| twisted            | timing                   |    26.7 |        32.7 |  1.2 |    0.83 |          2 |     1.04 | False |
| pip                | check                    |     7.9 |        13.5 |  1.7 |    0.64 |          2 |     0.87 | False |
| pip                | fix-certain              |    14.3 |        34.2 |  2.4 |    0.79 |          3 |     0.97 | False |
| pip                | fix-likely               |    13.8 |        37.9 |  2.7 |    1.01 |          3 |     1.26 | False |
| pip                | fix-unsafe               |    13.8 |        37.0 |  2.7 |    0.95 |          3 |     1.17 | False |
| pip                | infer-basedpyright       |    98.3 |       213.6 |  2.2 |     4.0 |          1 |     1.63 | False |
| pip                | infer-ty                 |    43.2 |        90.7 |  2.1 |    2.59 |          2 |     2.42 | False |
| pip                | infer-pyrefly            |    31.2 |        64.1 |  2.1 |    2.79 |          1 |     1.72 | False |
| pip                | census                   |     3.9 |         3.3 |  0.8 |     0.1 |          2 |     0.87 | False |
| pip                | coverage                 |     3.6 |         5.4 |  1.5 |    0.31 |          2 |     0.39 | False |
| pip                | timing                   |    18.2 |        24.9 |  1.4 |    0.63 |          2 |     0.79 | False |
| structlog          | check                    |     0.8 |         0.9 |  1.1 |    0.18 |          2 |     0.21 | False |
| structlog          | fix-certain              |     1.6 |         2.7 |  1.7 |    0.26 |          2 |     0.32 | False |
| structlog          | fix-likely               |     1.8 |         3.2 |  1.8 |    0.26 |          2 |     0.37 | False |
| structlog          | fix-unsafe               |     1.4 |         2.5 |  1.8 |    0.26 |          2 |     0.32 | False |
| structlog          | infer-basedpyright       |     9.6 |        10.1 |  1.1 |    0.56 |          1 |     0.14 | False |
| structlog          | infer-ty                 |     4.0 |         4.6 |  1.1 |    0.27 |          1 |     0.17 | False |
| structlog          | infer-pyrefly            |     3.6 |         4.3 |  1.2 |    0.31 |          1 |     0.17 | False |
| structlog          | census                   |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.21 | False |
| structlog          | coverage                 |     1.6 |         1.0 |  0.6 |    0.15 |          1 |     0.19 | False |
| structlog          | timing                   |     3.0 |         2.1 |  0.7 |    0.18 |          1 |     0.22 | False |
| structlog          | traced                   |     4.0 |         5.4 |  1.4 |    0.27 |          1 |     0.34 | False |
| structlog          | tests-released           |     3.6 |         2.0 |  0.6 |    0.08 |          1 |      0.1 | False |
| structlog          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | infer-union              |     4.7 |         7.0 |  1.5 |     0.5 |          1 |     0.16 | False |
| structlog          | tests-infer-union        |     1.6 |         1.5 |  0.9 |    0.08 |          1 |      0.1 | False |
| structlog          | tests                    |     2.4 |         2.1 |  0.9 |    0.17 |          1 |     0.21 | False |
| structlog          | types-released           |     2.0 |         0.6 |  0.3 |    0.11 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-infer-basedpyright |     1.2 |         0.6 |  0.5 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types-infer-pyrefly      |     0.6 |         0.5 |  0.8 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     2.3 |         0.2 |  0.1 |    0.03 |          1 |     0.21 | False |
| attrs              | fix-certain              |     2.0 |         2.8 |  1.4 |    0.29 |          2 |     0.34 | False |
| attrs              | fix-likely               |     3.6 |         3.3 |  0.9 |    0.29 |          1 |     0.35 | False |
| attrs              | fix-unsafe               |     3.1 |         3.4 |  1.1 |    0.28 |          2 |     0.35 | False |
| attrs              | infer-basedpyright       |    12.4 |        10.6 |  0.9 |    0.59 |          1 |      0.3 | False |
| attrs              | infer-ty                 |     7.0 |         5.0 |  0.7 |     0.3 |          1 |     0.37 | False |
| attrs              | infer-pyrefly            |     6.9 |         5.0 |  0.7 |    0.41 |          1 |     0.34 | False |
| attrs              | census                   |     2.5 |         1.4 |  0.6 |    0.17 |          1 |     0.21 | False |
| attrs              | coverage                 |     1.4 |         0.9 |  0.6 |    0.16 |          1 |      0.2 | False |
| attrs              | timing                   |     3.6 |         1.9 |  0.5 |    0.17 |          1 |     0.21 | False |
| attrs              | traced                   |     7.4 |        26.2 |  3.5 |    0.75 |          3 |     0.92 | False |
| attrs              | tests-released           |     2.8 |        13.6 |  4.9 |     0.6 |          6 |     0.77 | False |
| attrs              | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-fix-unsafe         |     0.9 |         0.2 |  0.2 |    0.03 |          5 |     0.76 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.74 | False |
| attrs              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.75 | False |
| attrs              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     0.76 | False |
| attrs              | infer-union              |    11.3 |        13.5 |  1.2 |    0.52 |          1 |     0.32 | False |
| attrs              | tests-infer-union        |     4.0 |        14.6 |  3.6 |     0.6 |          5 |     0.76 | False |
| attrs              | tests                    |     3.8 |         2.9 |  0.8 |    0.17 |          2 |     0.21 | False |
| click              | check                    |     1.0 |         1.3 |  1.3 |    0.18 |          2 |     0.22 | False |
| click              | fix-certain              |     2.0 |         3.6 |  1.8 |    0.31 |          2 |     0.36 | False |
| click              | fix-likely               |     5.2 |         5.5 |  1.1 |    0.32 |          1 |     0.36 | False |
| click              | fix-unsafe               |     3.0 |         5.0 |  1.7 |    0.32 |          2 |     0.39 | False |
| click              | infer-basedpyright       |    18.1 |        16.7 |  0.9 |    0.67 |          1 |     0.29 | False |
| click              | infer-ty                 |     4.4 |         6.6 |  1.5 |    0.33 |          1 |      0.2 | False |
| click              | infer-pyrefly            |     4.2 |         5.8 |  1.4 |    0.45 |          1 |      0.2 | False |
| click              | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.22 | False |
| click              | coverage                 |     0.6 |         0.9 |  1.5 |    0.17 |          2 |     0.21 | False |
| click              | timing                   |     1.6 |         1.9 |  1.2 |    0.18 |          2 |     0.22 | False |
| click              | traced                   |    11.7 |        12.1 |  1.0 |    0.33 |          1 |     0.39 | False |
| click              | tests-released           |     8.6 |         6.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-basedpyright |     0.3 |         0.2 |  0.7 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-pyrefly      |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | infer-union              |    11.3 |        13.6 |  1.2 |     0.6 |          1 |     0.17 | False |
| click              | tests-infer-union        |     7.2 |         6.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     3.2 |         2.9 |  0.9 |    0.17 |          1 |     0.21 | False |
| click              | types-released           |     3.2 |         1.0 |  0.3 |    0.13 |          1 |     0.16 | False |
| click              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| click              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| click              | types-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.12 | False |
| click              | types-infer-basedpyright |     1.2 |         0.8 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-ty           |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-pyrefly      |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.12 | False |
| click              | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     1.0 |         1.2 |  1.2 |    0.18 |          2 |     0.24 | False |
| hypercorn          | fix-certain              |     2.0 |         3.4 |  1.7 |    0.26 |          2 |     0.34 | False |
| hypercorn          | fix-likely               |     3.8 |         4.3 |  1.1 |    0.27 |          1 |     0.32 | False |
| hypercorn          | fix-unsafe               |     5.4 |         4.6 |  0.9 |    0.27 |          2 |     0.32 | False |
| hypercorn          | infer-basedpyright       |    12.9 |        16.4 |  1.3 |    0.94 |          1 |     0.56 | False |
| hypercorn          | infer-ty                 |     6.5 |         7.2 |  1.1 |    0.69 |          1 |     0.34 | False |
| hypercorn          | infer-pyrefly            |     6.1 |         6.4 |  1.0 |    0.66 |          1 |     0.37 | False |
| hypercorn          | census                   |     0.6 |         0.3 |  0.5 |    0.03 |          2 |     0.24 | False |
| hypercorn          | coverage                 |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.19 | False |
| hypercorn          | timing                   |     1.4 |         1.7 |  1.2 |    0.19 |          2 |     0.24 | False |
| hypercorn          | traced                   |    12.5 |         6.5 |  0.5 |    0.28 |          1 |     0.35 | False |
| hypercorn          | tests-released           |     9.2 |         1.6 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.11 | False |
| hypercorn          | infer-union              |     8.1 |        15.7 |  1.9 |    0.93 |          1 |     0.16 | False |
| hypercorn          | tests-infer-union        |     8.2 |         1.6 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests                    |     3.0 |         2.7 |  0.9 |    0.17 |          1 |     0.21 | False |
| hypercorn          | types-released           |     3.1 |         1.4 |  0.5 |    0.15 |          1 |     0.15 | False |
| hypercorn          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| hypercorn          | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| hypercorn          | types-fix-unsafe         |     0.5 |         0.1 |  0.2 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-infer-basedpyright |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-ty           |     1.2 |         0.6 |  0.5 |    0.09 |          1 |     0.11 | False |
| hypercorn          | types-infer-pyrefly      |     1.6 |         1.1 |  0.7 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     1.0 |         1.5 |  1.5 |     0.2 |          2 |     0.25 | False |
| starlette          | fix-certain              |     1.8 |         3.7 |  2.1 |    0.28 |          2 |     0.35 | False |
| starlette          | fix-likely               |     2.4 |         4.9 |  2.0 |    0.28 |          2 |     0.34 | False |
| starlette          | fix-unsafe               |     2.9 |         5.0 |  1.7 |    0.28 |          2 |     0.34 | False |
| starlette          | infer-basedpyright       |    15.0 |        20.6 |  1.4 |    1.07 |          1 |     0.17 | False |
| starlette          | infer-ty                 |     8.1 |         8.0 |  1.0 |    0.69 |          1 |     0.17 | False |
| starlette          | infer-pyrefly            |     4.3 |         6.4 |  1.5 |    0.49 |          1 |     0.17 | False |
| starlette          | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          2 |     0.25 | False |
| starlette          | coverage                 |     0.6 |         0.8 |  1.3 |    0.16 |          2 |      0.2 | False |
| starlette          | timing                   |     1.6 |         2.0 |  1.2 |     0.2 |          2 |     0.25 | False |
| starlette          | traced                   |    21.6 |        14.6 |  0.7 |    0.26 |          1 |     0.36 | False |
| starlette          | tests-released           |    19.9 |         7.6 |  0.4 |    0.22 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | infer-union              |    13.9 |        18.5 |  1.3 |    0.91 |          1 |     0.16 | False |
| starlette          | tests-infer-union        |    14.7 |         7.7 |  0.5 |    0.23 |          1 |     0.29 | False |
| starlette          | tests                    |     3.0 |         2.7 |  0.9 |    0.17 |          1 |     0.21 | False |
| starlette          | types-released           |     4.4 |         1.9 |  0.4 |    0.15 |          1 |     0.19 | False |
| starlette          | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.19 | False |
| starlette          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| starlette          | types-fix-unsafe         |     0.9 |         0.2 |  0.2 |    0.03 |          1 |     0.16 | False |
| starlette          | types-infer-basedpyright |     1.8 |         1.6 |  0.9 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-ty           |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.16 | False |
| starlette          | types-infer-pyrefly      |     1.8 |         1.4 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     0.9 |         0.2 |  0.2 |    0.03 |          1 |     0.16 | False |
| starlette          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.2 |         2.2 |  1.8 |    0.22 |          2 |     0.26 | False |
| werkzeug           | fix-certain              |     3.0 |         6.4 |  2.1 |    0.31 |          2 |     0.39 | False |
| werkzeug           | fix-likely               |     3.4 |         7.6 |  2.2 |    0.31 |          3 |     0.39 | False |
| werkzeug           | fix-unsafe               |     3.6 |         7.7 |  2.1 |    0.33 |          2 |     0.39 | False |
| werkzeug           | infer-basedpyright       |    10.6 |        25.1 |  2.4 |    1.24 |          1 |     0.19 | False |
| werkzeug           | infer-ty                 |     6.4 |        12.2 |  1.9 |    0.79 |          1 |     0.19 | False |
| werkzeug           | infer-pyrefly            |     5.0 |         9.8 |  2.0 |    0.81 |          1 |     0.21 | False |
| werkzeug           | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.26 | False |
| werkzeug           | coverage                 |     0.6 |         1.0 |  1.7 |    0.17 |          2 |     0.21 | False |
| werkzeug           | timing                   |     2.6 |         3.5 |  1.3 |    0.22 |          2 |     0.26 | False |
| werkzeug           | traced                   |    16.3 |        15.5 |  1.0 |    0.33 |          1 |     0.46 | False |
| werkzeug           | tests-released           |    11.0 |         7.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-ty           |     1.7 |         0.2 |  0.1 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-pyrefly      |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-trace        |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.21 | False |
| werkzeug           | infer-union              |    12.4 |        26.1 |  2.1 |    1.15 |          1 |     0.17 | False |
| werkzeug           | tests-infer-union        |    17.9 |         8.1 |  0.5 |    0.18 |          1 |     0.21 | False |
| werkzeug           | tests                    |     2.6 |         2.4 |  0.9 |    0.17 |          1 |     0.21 | False |
| werkzeug           | types-released           |     3.8 |         1.4 |  0.4 |    0.13 |          1 |     0.14 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-infer-basedpyright |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-ty           |     1.4 |         1.1 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-pyrefly      |     1.4 |         1.1 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     0.6 |         0.2 |  0.3 |    0.04 |          2 |     0.36 | False |
| mkdocs             | fix-certain              |     3.4 |         7.2 |  2.1 |    0.35 |          3 |     0.47 | False |
| mkdocs             | fix-likely               |     4.4 |         8.9 |  2.0 |    0.35 |          3 |     0.44 | False |
| mkdocs             | fix-unsafe               |     4.1 |         8.9 |  2.2 |    0.38 |          2 |     0.44 | False |
| mkdocs             | infer-basedpyright       |    13.6 |        31.2 |  2.3 |    1.42 |          1 |     0.22 | False |
| mkdocs             | infer-ty                 |     8.2 |        14.3 |  1.7 |    0.93 |          1 |     0.22 | False |
| mkdocs             | infer-pyrefly            |     7.6 |        13.0 |  1.7 |    0.98 |          1 |     0.24 | False |
| mkdocs             | census                   |     1.8 |         2.8 |  1.6 |    0.29 |          2 |     0.36 | False |
| mkdocs             | coverage                 |     0.8 |         1.2 |  1.5 |     0.2 |          2 |     0.25 | False |
| mkdocs             | timing                   |     2.8 |         3.7 |  1.3 |    0.29 |          2 |     0.36 | False |
| mkdocs             | traced                   |    18.0 |        14.5 |  0.8 |     0.4 |          1 |     0.52 | False |
| mkdocs             | tests-released           |    11.2 |         2.7 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-ty           |     0.5 |         0.2 |  0.4 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    24.3 |        35.1 |  1.4 |    1.24 |          1 |     0.22 | False |
| mkdocs             | tests-infer-union        |    12.8 |         3.0 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     2.6 |         2.4 |  0.9 |    0.17 |          1 |     0.21 | False |
| httpx              | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.24 | False |
| httpx              | fix-certain              |     2.4 |         3.6 |  1.5 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-likely               |     2.4 |         4.5 |  1.9 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-unsafe               |     2.4 |         4.1 |  1.7 |    0.27 |          2 |     0.34 | False |
| httpx              | infer-basedpyright       |    11.1 |        13.3 |  1.2 |    0.78 |          1 |     0.42 | False |
| httpx              | infer-ty                 |     5.8 |         6.9 |  1.2 |    0.53 |          1 |     0.35 | False |
| httpx              | infer-pyrefly            |     3.6 |         5.5 |  1.5 |    0.53 |          1 |     0.17 | False |
| httpx              | census                   |     1.0 |         1.4 |  1.4 |    0.19 |          2 |     0.24 | False |
| httpx              | coverage                 |     1.4 |         1.0 |  0.7 |    0.16 |          1 |      0.2 | False |
| httpx              | timing                   |     1.6 |         1.8 |  1.1 |    0.19 |          2 |     0.24 | False |
| httpx              | traced                   |     9.4 |         9.9 |  1.1 |     0.3 |          1 |     0.37 | False |
| httpx              | tests-released           |    11.0 |         6.4 |  0.6 |    0.23 |          1 |     0.27 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-basedpyright |     0.7 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| httpx              | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.26 | False |
| httpx              | infer-union              |    16.0 |        18.8 |  1.2 |    0.67 |          1 |     0.39 | False |
| httpx              | tests-infer-union        |     5.6 |         3.9 |  0.7 |    0.22 |          1 |     0.27 | False |
| httpx              | tests                    |     2.0 |         1.8 |  0.9 |    0.17 |          1 |     0.21 | False |
| httpx              | types-released           |    13.1 |         7.0 |  0.5 |    0.25 |          1 |     0.31 | False |
| httpx              | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-unsafe         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.25 | False |
| httpx              | types-infer-basedpyright |     8.0 |         6.5 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-ty           |     6.6 |         6.1 |  0.9 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-pyrefly      |     6.6 |         6.3 |  1.0 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-trace        |     6.6 |         6.0 |  0.9 |     0.2 |          1 |     0.25 | False |
| httpx              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.25 | False |
| black              | fix-certain              |     2.2 |         4.7 |  2.1 |    0.31 |          2 |      0.4 | False |
| black              | fix-likely               |     2.6 |         5.8 |  2.2 |    0.31 |          2 |     0.39 | False |
| black              | fix-unsafe               |     3.8 |         6.6 |  1.7 |    0.31 |          3 |     0.39 | False |
| black              | infer-basedpyright       |    15.6 |        18.9 |  1.2 |    0.76 |          1 |     0.17 | False |
| black              | infer-ty                 |     5.8 |         9.5 |  1.6 |    0.57 |          1 |     0.19 | False |
| black              | infer-pyrefly            |     4.4 |         7.6 |  1.7 |    0.57 |          1 |     0.21 | False |
| black              | census                   |     1.4 |         2.1 |  1.5 |     0.2 |          2 |     0.25 | False |
| black              | coverage                 |     0.8 |         1.0 |  1.2 |    0.18 |          2 |     0.22 | False |
| black              | timing                   |     2.2 |         2.9 |  1.3 |     0.2 |          2 |     0.25 | False |
| black              | traced                   |    20.0 |        72.6 |  3.6 |    0.92 |          6 |     1.14 | False |
| black              | tests-released           |     6.2 |        37.8 |  6.1 |     0.8 |          8 |     0.94 | False |
| black              | tests-fix-certain        |     7.2 |        48.5 |  6.7 |    0.77 |          8 |     0.94 | False |
| black              | tests-fix-likely         |     7.0 |        47.7 |  6.8 |    0.79 |          8 |     0.97 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.97 | False |
| black              | tests-infer-basedpyright |     7.4 |        44.3 |  6.0 |    0.77 |          8 |     0.94 | False |
| black              | tests-infer-ty           |     7.0 |        45.8 |  6.5 |    0.76 |          8 |     0.97 | False |
| black              | tests-infer-pyrefly      |     7.4 |        48.8 |  6.6 |    0.74 |          8 |     0.95 | False |
| black              | tests-infer-trace        |     7.8 |        44.5 |  5.7 |    0.79 |          8 |     0.97 | False |
| black              | infer-union              |    10.0 |        19.1 |  1.9 |    0.68 |          2 |      0.8 | False |
| black              | tests-infer-union        |     7.2 |        46.8 |  6.5 |    0.78 |          7 |     0.96 | False |
| black              | tests                    |     2.4 |         2.2 |  0.9 |    0.17 |          2 |     0.21 | False |
| fastapi            | check                    |     1.4 |         1.9 |  1.4 |    0.25 |          2 |     0.31 | False |
| fastapi            | fix-certain              |     4.2 |         6.3 |  1.5 |    0.33 |          2 |     0.41 | False |
| fastapi            | fix-likely               |     6.2 |         9.0 |  1.5 |    0.52 |          2 |     0.65 | False |
| fastapi            | fix-unsafe               |     4.0 |         6.3 |  1.6 |    0.36 |          2 |     0.45 | False |
| fastapi            | infer-basedpyright       |    14.2 |        26.2 |  1.8 |    1.35 |          1 |     0.22 | False |
| fastapi            | infer-ty                 |    11.4 |        13.3 |  1.2 |    0.98 |          1 |     0.29 | False |
| fastapi            | infer-pyrefly            |     9.2 |        11.3 |  1.2 |    1.02 |          1 |     0.22 | False |
| fastapi            | census                   |     0.4 |         0.3 |  0.7 |    0.05 |          2 |     0.31 | False |
| fastapi            | coverage                 |     1.0 |         1.2 |  1.2 |    0.18 |          2 |     0.22 | False |
| fastapi            | timing                   |     2.8 |         3.2 |  1.1 |    0.25 |          2 |     0.31 | False |
| fastapi            | traced                   |    21.7 |       119.3 |  5.5 |    2.35 |          7 |     2.95 | False |
| fastapi            | tests-released           |    14.8 |        92.6 |  6.3 |    2.11 |          8 |     2.62 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | infer-union              |     8.8 |        18.7 |  2.1 |    1.15 |          2 |     0.45 | False |
| fastapi            | tests-infer-union        |    11.2 |        79.9 |  7.1 |    2.13 |          8 |     2.62 | False |
| fastapi            | tests                    |     2.4 |         2.2 |  0.9 |    0.17 |          2 |     0.21 | False |
| cattrs             | check                    |     1.2 |         1.4 |  1.2 |     0.2 |          2 |     0.25 | False |
| cattrs             | fix-certain              |     2.0 |         3.2 |  1.6 |    0.27 |          2 |     0.32 | False |
| cattrs             | fix-likely               |     2.8 |         4.1 |  1.5 |    0.26 |          2 |     0.34 | False |
| cattrs             | fix-unsafe               |     2.6 |         4.2 |  1.6 |    0.27 |          2 |     0.34 | False |
| cattrs             | infer-basedpyright       |    12.4 |        20.6 |  1.7 |    1.01 |          1 |     0.15 | False |
| cattrs             | infer-ty                 |     6.0 |         6.8 |  1.1 |    0.66 |          1 |     0.17 | False |
| cattrs             | infer-pyrefly            |     5.8 |         6.4 |  1.1 |     0.5 |          1 |     0.34 | False |
| cattrs             | census                   |     0.4 |         0.3 |  0.7 |    0.04 |          2 |     0.25 | False |
| cattrs             | coverage                 |     1.2 |         1.0 |  0.8 |    0.15 |          1 |     0.19 | False |
| cattrs             | timing                   |     1.8 |         1.9 |  1.1 |     0.2 |          2 |     0.25 | False |
| cattrs             | traced                   |    20.4 |       129.3 |  6.3 |    1.37 |          8 |     1.66 | False |
| cattrs             | tests-released           |    20.8 |       126.5 |  6.1 |    1.01 |          8 |     1.26 | False |
| cattrs             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.25 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.24 | False |
| cattrs             | infer-union              |    12.0 |        18.1 |  1.5 |    0.85 |          2 |     0.32 | False |
| cattrs             | tests-infer-union        |    15.6 |        92.8 |  5.9 |    1.01 |          6 |     1.25 | False |
| cattrs             | tests                    |     2.2 |         2.0 |  0.9 |    0.17 |          2 |     0.21 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.39 | False |
| pytest             | fix-certain              |     4.4 |         9.7 |  2.2 |     0.4 |          3 |      0.5 | False |
| pytest             | fix-likely               |    10.4 |        16.7 |  1.6 |    0.46 |          2 |     0.59 | False |
| pytest             | fix-unsafe               |     7.2 |        14.0 |  1.9 |    0.41 |          2 |     0.51 | False |
| pytest             | infer-basedpyright       |    31.3 |        51.3 |  1.6 |    2.07 |          1 |     0.55 | False |
| pytest             | infer-ty                 |    10.6 |        20.9 |  2.0 |    1.24 |          2 |     0.52 | False |
| pytest             | infer-pyrefly            |    12.4 |        20.5 |  1.7 |    1.33 |          1 |     0.27 | False |
| pytest             | census                   |     2.8 |         4.5 |  1.6 |     0.3 |          2 |     0.39 | False |
| pytest             | coverage                 |     1.0 |         2.0 |  2.0 |    0.22 |          3 |     0.27 | False |
| pytest             | timing                   |     5.0 |         6.7 |  1.3 |    0.31 |          2 |     0.39 | False |
| pytest             | traced                   |    90.3 |       412.1 |  4.6 |    1.82 |          6 |     2.15 | False |
| pytest             | tests-released           |    22.6 |       160.2 |  7.1 |    1.41 |          8 |     1.71 | False |
| pytest             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| pytest             | infer-union              |    19.2 |        46.6 |  2.4 |     1.8 |          2 |     0.55 | False |
| pytest             | tests-infer-union        |    15.4 |       116.3 |  7.6 |    1.37 |          8 |      1.7 | False |
| pytest             | tests                    |     2.2 |         2.0 |  0.9 |    0.17 |          2 |     0.21 | False |
| botocore           | check                    |     3.0 |         5.8 |  1.9 |    0.36 |          2 |     0.42 | False |
| botocore           | fix-certain              |     4.8 |        11.5 |  2.4 |    0.43 |          3 |     0.54 | False |
| botocore           | fix-likely               |     6.4 |        15.9 |  2.5 |    0.52 |          3 |     0.65 | False |
| botocore           | fix-unsafe               |    11.4 |        18.0 |  1.6 |    0.51 |          2 |     0.65 | False |
| botocore           | infer-basedpyright       |    34.1 |        69.0 |  2.0 |    2.27 |          1 |     0.34 | False |
| botocore           | infer-ty                 |    17.9 |        27.9 |  1.6 |    1.32 |          1 |     0.22 | False |
| botocore           | infer-pyrefly            |    19.3 |        26.3 |  1.4 |    1.37 |          1 |     0.79 | False |
| botocore           | census                   |     0.8 |         0.7 |  0.9 |    0.05 |          2 |     0.42 | False |
| botocore           | coverage                 |     1.0 |         1.7 |  1.7 |    0.21 |          2 |     0.26 | False |
| botocore           | timing                   |     6.6 |         9.5 |  1.4 |    0.34 |          2 |     0.42 | False |
| botocore           | traced                   |    44.2 |       125.8 |  2.8 |    5.15 |          4 |     6.51 | False |
| botocore           | tests-released           |    29.7 |        93.5 |  3.1 |    4.92 |          4 |     6.15 | False |
| botocore           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.15 | False |
| botocore           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     6.01 | False |
| botocore           | infer-union              |    53.9 |        99.9 |  1.9 |    1.93 |          1 |     0.76 | False |
| botocore           | tests-infer-union        |    28.6 |        85.2 |  3.0 |    4.97 |          4 |     6.17 | False |
| botocore           | tests                    |     2.2 |         1.9 |  0.9 |    0.17 |          2 |     0.21 | False |
| uvicorn            | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.25 | False |
| uvicorn            | fix-certain              |     2.0 |         3.8 |  1.9 |    0.28 |          2 |     0.35 | False |
| uvicorn            | fix-likely               |     2.6 |         4.8 |  1.8 |    0.28 |          2 |     0.35 | False |
| uvicorn            | fix-unsafe               |     5.0 |         5.3 |  1.1 |    0.28 |          2 |     0.35 | False |
| uvicorn            | infer-basedpyright       |    12.0 |        20.1 |  1.7 |    1.07 |          1 |     0.15 | False |
| uvicorn            | infer-ty                 |     4.6 |         7.5 |  1.6 |     0.7 |          1 |     0.17 | False |
| uvicorn            | infer-pyrefly            |     6.7 |         8.1 |  1.2 |    0.72 |          1 |     0.35 | False |
| uvicorn            | census                   |     1.2 |         1.7 |  1.4 |     0.2 |          2 |     0.25 | False |
| uvicorn            | coverage                 |     1.2 |         1.0 |  0.8 |    0.16 |          1 |      0.2 | False |
| uvicorn            | timing                   |     1.8 |         2.2 |  1.2 |     0.2 |          2 |     0.25 | False |
| uvicorn            | traced                   |    37.9 |        31.2 |  0.8 |    0.95 |          1 |     1.17 | False |
| uvicorn            | tests-released           |    30.9 |        21.3 |  0.7 |    0.83 |          1 |     1.05 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | infer-union              |    15.6 |        20.5 |  1.3 |    0.95 |          1 |     0.16 | False |
| uvicorn            | tests-infer-union        |    29.9 |        20.9 |  0.7 |    0.84 |          1 |      1.0 | False |
| uvicorn            | tests                    |     2.4 |         2.3 |  1.0 |    0.17 |          1 |     0.21 | False |
| uvicorn            | types-released           |     4.8 |         2.1 |  0.4 |    0.16 |          1 |      0.2 | False |
| uvicorn            | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| uvicorn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| uvicorn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-infer-basedpyright |     2.2 |         1.5 |  0.7 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-ty           |     2.6 |         1.6 |  0.6 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-pyrefly      |     3.0 |         1.8 |  0.6 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     1.6 |         3.0 |  1.9 |    0.28 |          2 |     0.35 | False |
| mcp                | fix-certain              |    10.4 |        10.9 |  1.0 |    0.44 |          1 |     0.44 | False |
| mcp                | fix-likely               |     5.4 |        12.2 |  2.3 |    0.45 |          3 |     0.56 | False |
| mcp                | fix-unsafe               |    10.0 |        13.0 |  1.3 |    0.39 |          2 |     0.49 | False |
| mcp                | infer-basedpyright       |    21.3 |        54.5 |  2.6 |    2.31 |          1 |     0.81 | False |
| mcp                | infer-ty                 |    14.6 |        23.4 |  1.6 |    1.55 |          1 |     0.84 | False |
| mcp                | infer-pyrefly            |    11.6 |        19.0 |  1.6 |    1.63 |          1 |     0.86 | False |
| mcp                | census                   |     1.0 |         0.6 |  0.6 |    0.04 |          2 |     0.35 | False |
| mcp                | coverage                 |     0.8 |         1.4 |  1.7 |    0.19 |          2 |     0.24 | False |
| mcp                | timing                   |     3.4 |         4.9 |  1.4 |    0.28 |          2 |     0.35 | False |
| mcp                | traced                   |    22.9 |        96.6 |  4.2 |    2.08 |          5 |      2.6 | False |
| mcp                | tests-released           |    14.1 |        64.3 |  4.6 |    1.83 |          6 |      2.3 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-fix-likely         |     0.3 |         0.1 |  0.3 |    0.03 |          6 |     2.25 | False |
| mcp                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-infer-basedpyright |     0.3 |         0.1 |  0.3 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | infer-union              |    23.8 |        90.2 |  3.8 |    2.36 |          2 |      1.8 | False |
| mcp                | tests-infer-union        |    17.2 |        66.6 |  3.9 |     1.8 |          6 |     2.24 | False |
| mcp                | tests                    |     4.8 |         3.3 |  0.7 |    0.17 |          2 |     0.21 | False |
| mcp                | types-released           |    23.5 |        28.3 |  1.2 |    1.26 |          2 |     1.56 | False |
| mcp                | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     1.57 | False |
| mcp                | types-fix-likely         |    13.4 |        22.1 |  1.6 |    1.26 |          2 |     1.56 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      1.6 | False |
| mcp                | types-infer-basedpyright |    16.2 |        24.5 |  1.5 |    1.24 |          2 |     1.59 | False |
| mcp                | types-infer-ty           |    18.2 |        25.9 |  1.4 |    1.25 |          2 |     1.57 | False |
| mcp                | types-infer-pyrefly      |    15.2 |        23.5 |  1.5 |    1.29 |          2 |     1.57 | False |
| mcp                | types-infer-trace        |    22.6 |        28.5 |  1.3 |    1.23 |          1 |     1.45 | False |
| mcp                | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| requests           | check                    |     0.8 |         0.9 |  1.1 |    0.17 |          2 |     0.21 | False |
| requests           | fix-certain              |     1.6 |         2.8 |  1.7 |    0.26 |          2 |     0.32 | False |
| requests           | fix-likely               |     2.0 |         3.4 |  1.7 |    0.27 |          2 |     0.32 | False |
| requests           | fix-unsafe               |     2.2 |         3.4 |  1.5 |    0.26 |          2 |     0.32 | False |
| requests           | infer-basedpyright       |     4.0 |         4.5 |  1.1 |    0.24 |          1 |     0.14 | False |
| requests           | infer-ty                 |     4.8 |         4.3 |  0.9 |    0.21 |          1 |     0.35 | False |
| requests           | infer-pyrefly            |     2.4 |         3.8 |  1.6 |    0.26 |          1 |     0.16 | False |
| requests           | census                   |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.21 | False |
| requests           | coverage                 |     1.4 |         0.9 |  0.6 |    0.15 |          1 |     0.19 | False |
| requests           | timing                   |     1.2 |         1.3 |  1.1 |    0.17 |          2 |     0.21 | False |
| requests           | traced                   |    26.2 |        14.5 |  0.6 |    0.64 |          1 |      0.8 | False |
| requests           | tests-released           |    24.6 |        10.6 |  0.4 |    0.57 |          8 |      8.0 | False |
| requests           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests           | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.71 | False |
| requests           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.71 | False |
| requests           | infer-union              |     4.9 |         5.2 |  1.1 |    0.23 |          1 |     0.16 | False |
| requests           | tests-infer-union        |    22.9 |         7.4 |  0.3 |     0.5 |          1 |     0.62 | False |
| requests           | tests                    |     2.2 |         2.1 |  1.0 |    0.17 |          2 |     0.21 | False |
| requests           | types-released           |     4.2 |         4.1 |  1.0 |    0.36 |          1 |     0.45 | False |
| requests           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.45 | False |
| requests           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.45 | False |
| requests           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.46 | False |
| requests           | types-infer-basedpyright |     2.0 |         3.1 |  1.6 |    0.36 |          2 |     0.44 | False |
| requests           | types-infer-ty           |     2.0 |         3.2 |  1.6 |    0.36 |          2 |     0.45 | False |
| requests           | types-infer-pyrefly      |     2.2 |         3.4 |  1.5 |    0.37 |          2 |     0.44 | False |
| requests           | types-infer-trace        |     2.4 |         3.6 |  1.5 |    0.35 |          2 |     0.45 | False |
| requests           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| rich               | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |      0.3 | False |
| rich               | fix-certain              |     3.2 |         8.2 |  2.6 |    0.36 |          3 |     0.46 | False |
| rich               | fix-likely               |     4.4 |        11.2 |  2.5 |     0.4 |          3 |     0.49 | False |
| rich               | fix-unsafe               |     3.6 |         9.6 |  2.7 |    0.39 |          3 |     0.49 | False |
| rich               | infer-basedpyright       |     6.7 |        13.9 |  2.1 |    0.36 |          1 |     0.15 | False |
| rich               | infer-ty                 |     7.0 |        13.7 |  2.0 |    0.41 |          1 |     0.23 | False |
| rich               | infer-pyrefly            |     5.4 |        12.9 |  2.4 |     0.4 |          1 |     0.16 | False |
| rich               | census                   |     2.4 |         3.8 |  1.6 |    0.24 |          3 |      0.3 | False |
| rich               | coverage                 |     1.0 |         1.5 |  1.5 |    0.19 |          2 |     0.24 | False |
| rich               | timing                   |     3.4 |         5.0 |  1.5 |    0.24 |          2 |      0.3 | False |
| rich               | traced                   |    12.2 |        15.8 |  1.3 |    0.41 |          1 |     0.47 | False |
| rich               | tests-released           |     6.4 |         2.6 |  0.4 |    0.11 |          1 |     0.11 | False |
| rich               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.14 | False |
| rich               | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.14 | False |
| rich               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| rich               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| rich               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| rich               | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.14 | False |
| rich               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| rich               | infer-union              |     6.6 |        13.7 |  2.1 |    0.35 |          1 |     0.21 | False |
| rich               | tests-infer-union        |     5.2 |         2.5 |  0.5 |    0.11 |          1 |     0.12 | False |
| rich               | tests                    |     2.4 |         2.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| rich               | types-released           |     5.0 |         2.7 |  0.5 |    0.18 |          1 |     0.22 | False |
| rich               | types-fix-certain        |     2.2 |         1.9 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-fix-likely         |     1.8 |         1.6 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-fix-unsafe         |     2.2 |         2.0 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-infer-basedpyright |     2.8 |         2.4 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-infer-ty           |     2.8 |         2.4 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-infer-pyrefly      |     2.6 |         2.3 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types-infer-trace        |     2.4 |         2.1 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich               | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| urllib3            | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.24 | False |
| urllib3            | fix-certain              |     2.0 |         3.8 |  1.9 |    0.28 |          2 |     0.35 | False |
| urllib3            | fix-likely               |     2.6 |         5.2 |  2.0 |    0.29 |          2 |     0.36 | False |
| urllib3            | fix-unsafe               |     4.4 |         5.8 |  1.3 |    0.31 |          2 |      0.4 | False |
| urllib3            | infer-basedpyright       |     4.0 |         6.1 |  1.5 |    0.23 |          1 |     0.55 | False |
| urllib3            | infer-ty                 |     6.2 |         6.7 |  1.1 |     0.3 |          1 |      0.4 | False |
| urllib3            | infer-pyrefly            |     6.8 |         6.3 |  0.9 |    0.29 |          1 |     0.18 | False |
| urllib3            | census                   |     1.2 |         1.5 |  1.2 |    0.19 |          2 |     0.24 | False |
| urllib3            | coverage                 |     0.6 |         0.9 |  1.5 |    0.16 |          2 |      0.2 | False |
| urllib3            | timing                   |     4.1 |         3.2 |  0.8 |     0.2 |          1 |     0.24 | False |
| urllib3            | traced                   |    74.8 |        19.4 |  0.3 |    0.31 |          1 |      0.4 | False |
| urllib3            | tests-released           |    55.2 |         6.0 |  0.1 |    0.19 |          1 |     0.29 | False |
| urllib3            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| urllib3            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| urllib3            | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| urllib3            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.24 | False |
| urllib3            | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| urllib3            | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| urllib3            | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.24 | False |
| urllib3            | infer-union              |     7.3 |         7.7 |  1.1 |    0.24 |          2 |     0.34 | False |
| urllib3            | tests-infer-union        |    70.9 |        12.5 |  0.2 |    0.21 |          1 |     0.26 | False |
| urllib3            | tests                    |     2.8 |         2.5 |  0.9 |    0.17 |          1 |     0.21 | False |
| urllib3            | types-released           |     5.4 |         2.5 |  0.5 |    0.23 |          1 |     0.29 | False |
| urllib3            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| urllib3            | types-fix-likely         |     2.0 |         1.8 |  0.9 |    0.21 |          1 |     0.26 | False |
| urllib3            | types-fix-unsafe         |     0.7 |         0.2 |  0.3 |    0.03 |          1 |     0.26 | False |
| urllib3            | types-infer-basedpyright |     2.2 |         1.9 |  0.9 |     0.2 |          1 |     0.26 | False |
| urllib3            | types-infer-ty           |     3.0 |         2.2 |  0.7 |    0.21 |          1 |     0.26 | False |
| urllib3            | types-infer-pyrefly      |     1.8 |         1.7 |  0.9 |     0.2 |          1 |     0.24 | False |
| urllib3            | types-infer-trace        |     3.2 |         2.2 |  0.7 |     0.2 |          1 |     0.25 | False |
| urllib3            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlmodel           | check                    |     0.6 |         0.1 |  0.2 |    0.03 |          2 |     0.29 | False |
| sqlmodel           | fix-certain              |     2.2 |         3.5 |  1.6 |    0.25 |          2 |     0.31 | False |
| sqlmodel           | fix-likely               |     2.6 |         4.0 |  1.5 |    0.29 |          2 |     0.36 | False |
| sqlmodel           | fix-unsafe               |     4.1 |         4.9 |  1.2 |    0.29 |          2 |     0.36 | False |
| sqlmodel           | infer-basedpyright       |     3.5 |         5.0 |  1.4 |    0.29 |          1 |     0.36 | False |
| sqlmodel           | infer-ty                 |     3.5 |         4.8 |  1.4 |    0.29 |          1 |     0.49 | False |
| sqlmodel           | infer-pyrefly            |     3.9 |         5.4 |  1.4 |    0.35 |          1 |     0.42 | False |
| sqlmodel           | census                   |     1.0 |         1.2 |  1.2 |    0.23 |          2 |     0.29 | False |
| sqlmodel           | coverage                 |     1.2 |         0.8 |  0.7 |    0.14 |          1 |     0.17 | False |
| sqlmodel           | timing                   |     1.6 |         1.9 |  1.2 |    0.23 |          2 |     0.29 | False |
| sqlmodel           | traced                   |    21.0 |        16.2 |  0.8 |    0.33 |          1 |     0.41 | False |
| sqlmodel           | tests-released           |     7.6 |         7.2 |  0.9 |    0.24 |          1 |      0.2 | False |
| sqlmodel           | tests-fix-certain        |     9.2 |         8.4 |  0.9 |    0.24 |          1 |      0.3 | False |
| sqlmodel           | tests-fix-likely         |     8.4 |         7.6 |  0.9 |    0.24 |          1 |      0.3 | False |
| sqlmodel           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| sqlmodel           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.3 | False |
| sqlmodel           | tests-infer-ty           |     7.3 |         7.0 |  1.0 |    0.24 |          1 |      0.3 | False |
| sqlmodel           | tests-infer-pyrefly      |     8.2 |         7.9 |  1.0 |    0.24 |          1 |      0.3 | False |
| sqlmodel           | tests-infer-trace        |     8.8 |         8.3 |  0.9 |    0.24 |          1 |      0.3 | False |
| sqlmodel           | infer-union              |     7.7 |         6.6 |  0.9 |    0.35 |          1 |     0.21 | False |
| sqlmodel           | tests-infer-union        |    13.1 |         9.4 |  0.7 |    0.27 |          1 |     0.32 | False |
| sqlmodel           | tests                    |     2.4 |         2.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| marshmallow        | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| marshmallow        | fix-certain              |     1.6 |         2.3 |  1.4 |    0.28 |          2 |     0.35 | False |
| marshmallow        | fix-likely               |     4.4 |         3.4 |  0.8 |    0.24 |          1 |     0.35 | False |
| marshmallow        | fix-unsafe               |     5.5 |         3.6 |  0.7 |    0.27 |          2 |     0.35 | False |
| marshmallow        | infer-basedpyright       |     4.6 |         4.2 |  0.9 |    0.22 |          1 |      0.6 | False |
| marshmallow        | infer-ty                 |     6.3 |         4.0 |  0.6 |    0.23 |          1 |      0.3 | False |
| marshmallow        | infer-pyrefly            |     5.4 |         3.6 |  0.7 |    0.29 |          1 |     0.35 | False |
| marshmallow        | census                   |     2.0 |         1.3 |  0.7 |    0.17 |          1 |     0.21 | False |
| marshmallow        | coverage                 |     0.8 |         0.8 |  1.0 |    0.16 |          1 |      0.2 | False |
| marshmallow        | timing                   |     2.6 |         1.7 |  0.7 |    0.17 |          1 |     0.21 | False |
| marshmallow        | traced                   |     4.7 |         5.2 |  1.1 |    0.29 |          1 |     0.35 | False |
| marshmallow        | tests-released           |     2.7 |         2.2 |  0.8 |    0.09 |          1 |      1.0 | False |
| marshmallow        | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-fix-likely         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-infer-basedpyright |     0.7 |         0.2 |  0.3 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-infer-pyrefly      |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.11 | False |
| marshmallow        | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow        | infer-union              |     3.7 |         4.0 |  1.1 |    0.27 |          1 |      0.3 | False |
| marshmallow        | tests-infer-union        |     2.1 |         1.7 |  0.8 |    0.08 |          1 |      0.1 | False |
| marshmallow        | tests                    |     2.6 |         2.4 |  0.9 |    0.17 |          1 |     0.21 | False |
| marshmallow        | types-released           |     2.4 |         1.4 |  0.6 |    0.14 |          1 |     0.16 | False |
| marshmallow        | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| marshmallow        | types-fix-likely         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.12 | False |
| marshmallow        | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| marshmallow        | types-infer-basedpyright |     1.2 |         0.6 |  0.5 |    0.07 |          1 |      0.1 | False |
| marshmallow        | types-infer-ty           |     1.8 |         1.3 |  0.7 |     0.1 |          1 |     0.12 | False |
| marshmallow        | types-infer-pyrefly      |     0.6 |         0.4 |  0.7 |    0.08 |          1 |     0.09 | False |
| marshmallow        | types-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| marshmallow        | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     3.9 |         7.9 |  2.0 |    0.43 |          2 |     0.54 | False |
| textual            | fix-certain              |     6.4 |        17.2 |  2.7 |    0.54 |          3 |     0.69 | False |
| textual            | fix-likely               |     8.8 |        24.5 |  2.8 |    0.57 |          3 |     0.71 | False |
| textual            | fix-unsafe               |     8.2 |        23.2 |  2.8 |    0.55 |          3 |     0.69 | False |
| textual            | infer-basedpyright       |    31.7 |        98.4 |  3.1 |    3.13 |          2 |      1.9 | False |
| textual            | infer-ty                 |    27.3 |        51.0 |  1.9 |    1.96 |          1 |     0.83 | False |
| textual            | infer-pyrefly            |    21.1 |        38.8 |  1.8 |    2.19 |          1 |     1.32 | False |
| textual            | census                   |     2.0 |         1.7 |  0.8 |    0.07 |          2 |     0.54 | False |
| textual            | coverage                 |     4.1 |         3.8 |  0.9 |    0.25 |          1 |     0.31 | False |
| textual            | timing                   |     9.8 |        14.1 |  1.4 |    0.43 |          2 |     0.54 | False |
| pdm                | check                    |     2.4 |         4.5 |  1.9 |    0.49 |          2 |     0.61 | False |
| pdm                | fix-certain              |     7.1 |        13.4 |  1.9 |    0.53 |          2 |     0.66 | False |
| pdm                | fix-likely               |    11.8 |        19.9 |  1.7 |    0.58 |          2 |     0.74 | False |
| pdm                | fix-unsafe               |    17.0 |        20.6 |  1.2 |    0.65 |          2 |     0.81 | False |
| pdm                | infer-basedpyright       |    26.9 |        59.7 |  2.2 |    2.32 |          1 |     0.89 | False |
| pdm                | infer-ty                 |    14.2 |        27.6 |  1.9 |    1.68 |          2 |     2.02 | False |
| pdm                | infer-pyrefly            |    14.4 |        23.7 |  1.6 |    1.79 |          2 |     2.09 | False |
| pdm                | census                   |     1.2 |         0.7 |  0.6 |    0.05 |          2 |     0.61 | False |
| pdm                | coverage                 |     1.0 |         1.5 |  1.5 |     0.2 |          2 |     0.25 | False |
| pdm                | timing                   |     6.6 |         8.7 |  1.3 |    0.49 |          2 |     0.61 | False |
| pdm                | traced                   |    44.1 |       147.3 |  3.3 |    1.61 |          7 |     2.01 | False |
| pdm                | tests-released           |    20.4 |       101.5 |  5.0 |    1.22 |          8 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      1.6 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.5 | False |
| pdm                | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |      1.6 | False |
| pdm                | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          6 |      1.6 | False |
| pdm                | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          6 |      1.6 | False |
| pdm                | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          6 |      1.6 | False |
| pdm                | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     1.51 | False |
| pdm                | infer-union              |    33.2 |        98.1 |  3.0 |    2.57 |          3 |     2.61 | False |
| pdm                | tests-infer-union        |    25.0 |       121.3 |  4.9 |    1.23 |          6 |      1.6 | False |
| pdm                | tests                    |     3.0 |         2.7 |  0.9 |    0.17 |          2 |     0.21 | False |
| strawberry-graphql | check                    |     2.6 |         0.2 |  0.1 |    0.04 |          2 |      0.5 | False |
| strawberry-graphql | fix-certain              |     6.0 |        12.3 |  2.1 |    0.52 |          2 |     0.65 | False |
| strawberry-graphql | fix-likely               |     7.6 |        17.4 |  2.3 |    0.66 |          3 |     0.86 | False |
| strawberry-graphql | fix-unsafe               |     9.3 |        17.4 |  1.9 |    0.56 |          2 |      0.7 | False |
| strawberry-graphql | infer-basedpyright       |    32.3 |        85.6 |  2.7 |    3.31 |          1 |     0.34 | False |
| strawberry-graphql | infer-ty                 |    15.8 |        32.4 |  2.1 |    1.89 |          1 |     0.34 | False |
| strawberry-graphql | infer-pyrefly            |    23.1 |        29.7 |  1.3 |    1.94 |          1 |      0.4 | False |
| strawberry-graphql | census                   |     2.8 |         5.3 |  1.9 |    0.39 |          2 |      0.5 | False |
| strawberry-graphql | coverage                 |     1.0 |         1.7 |  1.7 |    0.19 |          2 |     0.24 | False |
| strawberry-graphql | timing                   |     5.8 |         8.4 |  1.4 |     0.4 |          2 |      0.5 | False |
| strawberry-graphql | traced                   |    21.0 |       110.9 |  5.3 |    1.51 |          6 |     1.88 | False |
| strawberry-graphql | tests-released           |    12.6 |        72.5 |  5.8 |     1.3 |          7 |      1.6 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.6 | False |
| strawberry-graphql | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.55 | False |
| strawberry-graphql | infer-union              |    29.3 |       115.8 |  4.0 |    2.68 |          2 |     0.47 | False |
| strawberry-graphql | tests-infer-union        |    29.6 |        86.5 |  2.9 |    1.22 |          7 |     1.55 | False |
| strawberry-graphql | tests                    |     3.0 |         2.7 |  0.9 |    0.17 |          2 |     0.21 | False |
| strawberry-graphql | types-released           |     5.0 |         2.4 |  0.5 |    0.25 |          1 |     0.31 | False |
| strawberry-graphql | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-basedpyright |     3.0 |         2.0 |  0.7 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-ty           |     2.6 |         1.8 |  0.7 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-pyrefly      |     2.8 |         2.2 |  0.8 |     0.2 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-trace        |     1.8 |         1.7 |  0.9 |    0.21 |          1 |     0.26 | False |
| strawberry-graphql | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     3.2 |         7.7 |  2.4 |    0.42 |          3 |     0.52 | False |
| pygments           | fix-certain              |     8.4 |        20.3 |  2.4 |     0.5 |          3 |     0.62 | False |
| pygments           | fix-likely               |     8.2 |        23.2 |  2.8 |    0.64 |          3 |     0.79 | False |
| pygments           | fix-unsafe               |    12.2 |        29.0 |  2.4 |    0.63 |          3 |     0.79 | False |
| pygments           | infer-basedpyright       |    59.7 |       118.4 |  2.0 |    2.83 |          1 |     0.38 | False |
| pygments           | infer-ty                 |    24.7 |        44.9 |  1.8 |    1.81 |          1 |      0.4 | False |
| pygments           | infer-pyrefly            |    24.3 |        44.7 |  1.8 |    2.16 |          1 |      0.4 | False |
| pygments           | census                   |     2.2 |         2.1 |  1.0 |    0.07 |          3 |     0.52 | False |
| pygments           | coverage                 |     1.6 |         3.8 |  2.4 |    0.22 |          3 |     0.27 | False |
| pygments           | timing                   |     7.6 |        11.4 |  1.5 |    0.43 |          2 |     0.52 | False |
| pygments           | traced                   |    40.9 |        53.3 |  1.3 |    0.73 |          1 |     0.91 | False |
| pygments           | tests-released           |    21.8 |        15.8 |  0.7 |     0.3 |          1 |     0.35 | False |
| pygments           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.32 | False |
| pygments           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| pygments           | infer-union              |    91.2 |       191.0 |  2.1 |    1.99 |          1 |     0.99 | False |
| pygments           | tests-infer-union        |    19.2 |        14.9 |  0.8 |     0.3 |          1 |     0.37 | False |
| pygments           | tests                    |     2.8 |         2.7 |  1.0 |    0.17 |          1 |     0.21 | False |
| streamlink         | check                    |     5.4 |         6.8 |  1.3 |    0.34 |          3 |     0.44 | False |
| streamlink         | fix-certain              |     5.2 |        14.6 |  2.8 |    0.44 |          3 |     0.59 | False |
| streamlink         | fix-likely               |     6.4 |        17.2 |  2.7 |    0.51 |          3 |     0.64 | False |
| streamlink         | fix-unsafe               |    11.0 |        20.5 |  1.9 |    0.47 |          3 |     0.62 | False |
| streamlink         | infer-basedpyright       |    27.4 |        79.5 |  2.9 |    2.82 |          1 |     0.33 | False |
| streamlink         | infer-ty                 |    16.7 |        33.0 |  2.0 |    1.63 |          1 |     0.29 | False |
| streamlink         | infer-pyrefly            |    14.8 |        27.7 |  1.9 |    1.72 |          1 |     0.29 | False |
| streamlink         | census                   |     1.2 |         0.9 |  0.8 |    0.06 |          3 |     0.44 | False |
| streamlink         | coverage                 |     1.0 |         1.9 |  1.9 |    0.23 |          2 |     0.29 | False |
| streamlink         | timing                   |     7.0 |        10.4 |  1.5 |    0.35 |          2 |     0.44 | False |
| streamlink         | traced                   |    31.0 |        36.4 |  1.2 |    0.55 |          1 |      0.7 | False |
| streamlink         | tests-released           |    22.3 |        14.0 |  0.6 |    0.18 |          1 |     0.25 | False |
| streamlink         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | infer-union              |    30.2 |       105.8 |  3.5 |    2.48 |          1 |     0.31 | False |
| streamlink         | tests-infer-union        |    18.6 |        13.2 |  0.7 |     0.2 |          1 |     0.25 | False |
| streamlink         | tests                    |     2.2 |         2.1 |  1.0 |    0.17 |          1 |     0.21 | False |
| streamlink         | types-released           |    19.5 |         8.2 |  0.4 |    0.38 |          1 |     0.47 | False |
| streamlink         | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.49 | False |
| streamlink         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.47 | False |
| streamlink         | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.45 | False |
| streamlink         | types-infer-basedpyright |     8.4 |         6.9 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-ty           |     8.4 |         7.1 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |    10.4 |         7.8 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |     8.4 |         6.9 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     3.2 |         0.3 |  0.1 |    0.05 |          3 |     0.59 | False |
| sphinx             | fix-certain              |     8.6 |        27.3 |  3.2 |    0.64 |          3 |     0.81 | False |
| sphinx             | fix-likely               |    10.2 |        31.4 |  3.1 |    0.82 |          4 |     1.04 | False |
| sphinx             | fix-unsafe               |    12.6 |        37.3 |  3.0 |    0.73 |          3 |      0.9 | False |
| sphinx             | infer-basedpyright       |    54.5 |       141.6 |  2.6 |    4.07 |          1 |     1.59 | False |
| sphinx             | infer-ty                 |    24.3 |        65.3 |  2.7 |    2.33 |          1 |     0.86 | False |
| sphinx             | infer-pyrefly            |    22.0 |        53.9 |  2.4 |    2.69 |          1 |     1.01 | False |
| sphinx             | census                   |     5.0 |        11.2 |  2.2 |    0.47 |          3 |     0.59 | False |
| sphinx             | coverage                 |     1.8 |         4.2 |  2.3 |    0.27 |          3 |     0.34 | False |
| sphinx             | timing                   |    13.0 |        19.8 |  1.5 |    0.47 |          2 |     0.59 | False |
| sphinx             | traced                   |    24.4 |       140.2 |  5.7 |    1.69 |          7 |     2.12 | False |
| sphinx             | tests-released           |    18.3 |       114.0 |  6.2 |    1.34 |          7 |     1.67 | False |
| sphinx             | tests-fix-certain        |    15.2 |       107.3 |  7.1 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-fix-likely         |    14.0 |       101.6 |  7.3 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          7 |     1.67 | False |
| sphinx             | tests-infer-basedpyright |    10.8 |        77.4 |  7.2 |    1.34 |          8 |     1.65 | False |
| sphinx             | tests-infer-ty           |    14.2 |       101.8 |  7.2 |    1.34 |          8 |     1.66 | False |
| sphinx             | tests-infer-pyrefly      |    15.4 |       108.3 |  7.0 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-infer-trace        |    14.6 |       100.1 |  6.9 |    1.33 |          8 |     1.66 | False |
| sphinx             | infer-union              |    50.8 |       176.8 |  3.5 |    3.38 |          2 |     1.93 | False |
| sphinx             | tests-infer-union        |    10.6 |        78.4 |  7.4 |    1.33 |          8 |     1.69 | False |
| sphinx             | tests                    |     1.4 |         1.3 |  0.9 |    0.17 |          2 |     0.21 | False |
| sphinx             | types-released           |    18.2 |         7.9 |  0.4 |    0.33 |          1 |     0.41 | False |
| sphinx             | types-fix-certain        |    10.6 |         7.6 |  0.7 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-likely         |     9.8 |         7.2 |  0.7 |    0.27 |          1 |     0.34 | False |
| sphinx             | types-fix-unsafe         |     1.0 |         0.4 |  0.4 |    0.04 |          1 |     0.41 | False |
| sphinx             | types-infer-basedpyright |     7.3 |         5.9 |  0.8 |    0.26 |          1 |     0.35 | False |
| sphinx             | types-infer-ty           |     7.6 |         6.4 |  0.8 |    0.26 |          1 |     0.31 | False |
| sphinx             | types-infer-pyrefly      |     8.8 |         6.6 |  0.7 |    0.29 |          1 |     0.32 | False |
| sphinx             | types-infer-trace        |     4.5 |         3.8 |  0.8 |    0.27 |          1 |     0.34 | False |
| sphinx             | types                    |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.32 | False |
| tox                | fix-certain              |     3.4 |         8.0 |  2.4 |    0.33 |          3 |     0.41 | False |
| tox                | fix-likely               |     3.8 |         9.5 |  2.5 |     0.4 |          3 |      0.5 | False |
| tox                | fix-unsafe               |     6.6 |        11.0 |  1.7 |    0.36 |          2 |     0.55 | False |
| tox                | infer-basedpyright       |    16.7 |        44.5 |  2.7 |    2.12 |          1 |     0.69 | False |
| tox                | infer-ty                 |     7.1 |        15.9 |  2.2 |    1.29 |          1 |     0.79 | False |
| tox                | infer-pyrefly            |     9.1 |        16.0 |  1.8 |    1.71 |          1 |     0.96 | False |
| tox                | census                   |     1.8 |         3.4 |  1.9 |    0.26 |          2 |     0.32 | False |
| tox                | coverage                 |     0.8 |         1.4 |  1.7 |    0.18 |          2 |     0.22 | False |
| tox                | timing                   |     3.2 |         4.5 |  1.4 |    0.26 |          2 |     0.32 | False |
| tox                | traced                   |    33.2 |       153.2 |  4.6 |    1.59 |          4 |     1.88 | False |
| tox                | tests-released           |    17.8 |       104.5 |  5.9 |    1.36 |          8 |     1.67 | False |
| tox                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| tox                | infer-union              |    23.4 |        68.8 |  2.9 |    2.02 |          1 |     0.74 | False |
| tox                | tests-infer-union        |    29.5 |       138.4 |  4.7 |    1.32 |          6 |      1.7 | False |
| tox                | tests                    |     1.4 |         1.3 |  0.9 |    0.17 |          2 |     0.21 | False |
| trio               | check                    |     2.2 |         4.7 |  2.1 |    0.33 |          3 |     0.41 | False |
| trio               | fix-certain              |     4.8 |        11.0 |  2.3 |    0.47 |          3 |     0.59 | False |
| trio               | fix-likely               |     7.2 |        16.0 |  2.2 |    0.68 |          3 |     0.91 | False |
| trio               | fix-unsafe               |    10.6 |        18.9 |  1.8 |    0.53 |          2 |     0.79 | False |
| trio               | infer-basedpyright       |    11.7 |        19.5 |  1.7 |    0.55 |          1 |     0.34 | False |
| trio               | infer-ty                 |    13.0 |        22.2 |  1.7 |    0.68 |          1 |     0.41 | False |
| trio               | infer-pyrefly            |     9.6 |        19.3 |  2.0 |    0.54 |          1 |     0.22 | False |
| trio               | census                   |     1.2 |         1.1 |  0.9 |    0.05 |          3 |     0.41 | False |
| trio               | coverage                 |     1.0 |         1.7 |  1.7 |    0.21 |          2 |     0.26 | False |
| trio               | timing                   |     4.8 |         6.8 |  1.4 |    0.33 |          2 |     0.41 | False |
| trio               | traced                   |    91.7 |        66.5 |  0.7 |    0.66 |          1 |     0.81 | False |
| trio               | tests-released           |    65.7 |        48.0 |  0.7 |    0.66 |          1 |      1.0 | False |
| trio               | tests-fix-certain        |    52.5 |        38.3 |  0.7 |    0.57 |          1 |     0.72 | False |
| trio               | tests-fix-likely         |    55.0 |        39.8 |  0.7 |    0.57 |          1 |     0.71 | False |
| trio               | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.04 |          1 |     0.82 | False |
| trio               | tests-infer-basedpyright |    69.9 |        44.5 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio               | tests-infer-ty           |    70.0 |        42.6 |  0.6 |    0.58 |          1 |     0.71 | False |
| trio               | tests-infer-pyrefly      |    66.5 |        42.7 |  0.6 |    0.58 |          1 |     0.71 | False |
| trio               | tests-infer-trace        |    71.1 |        45.3 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio               | infer-union              |    14.5 |        22.3 |  1.5 |    0.55 |          1 |     0.34 | False |
| trio               | tests-infer-union        |    70.4 |        43.7 |  0.6 |    0.62 |          1 |     0.76 | False |
| trio               | tests                    |     2.2 |         2.1 |  1.0 |    0.17 |          1 |     0.21 | False |
| trio               | types-released           |     1.8 |         2.5 |  1.4 |    0.27 |          2 |     0.32 | False |
| trio               | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.37 | False |
| trio               | types-fix-likely         |     1.2 |         2.2 |  1.8 |    0.24 |          2 |     0.32 | False |
| trio               | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.37 | False |
| trio               | types-infer-basedpyright |     1.4 |         2.3 |  1.6 |    0.24 |          2 |     0.31 | False |
| trio               | types-infer-ty           |     1.4 |         2.3 |  1.6 |    0.25 |          2 |      0.3 | False |
| trio               | types-infer-pyrefly      |     1.4 |         2.3 |  1.6 |    0.24 |          2 |      0.3 | False |
| trio               | types-infer-trace        |     2.2 |         2.7 |  1.2 |    0.24 |          2 |      0.3 | False |
| trio               | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| langchain-core     | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      0.5 | False |
| langchain-core     | fix-certain              |    10.0 |        18.2 |  1.8 |    0.59 |          3 |     0.74 | False |
| langchain-core     | fix-likely               |    11.2 |        25.8 |  2.3 |    0.84 |          2 |     1.07 | False |
| langchain-core     | fix-unsafe               |    13.8 |        23.4 |  1.7 |    0.66 |          2 |     0.94 | False |
| langchain-core     | infer-basedpyright       |    22.3 |        33.8 |  1.5 |    0.85 |          1 |     1.32 | False |
| langchain-core     | infer-ty                 |    22.0 |        32.3 |  1.5 |    0.86 |          1 |     1.27 | False |
| langchain-core     | infer-pyrefly            |    17.9 |        31.2 |  1.7 |    0.85 |          2 |     2.76 | False |
| langchain-core     | census                   |     3.2 |         5.8 |  1.8 |     0.4 |          2 |      0.5 | False |
| langchain-core     | coverage                 |     1.0 |         2.2 |  2.2 |    0.23 |          2 |     0.29 | False |
| langchain-core     | timing                   |     7.2 |        10.3 |  1.4 |     0.4 |          2 |      0.5 | False |
| langchain-core     | traced                   |    19.6 |        74.8 |  3.8 |    1.48 |          5 |     1.84 | False |
| langchain-core     | tests-released           |    12.6 |        41.2 |  3.3 |    1.18 |          5 |     1.49 | False |
| langchain-core     | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.44 | False |
| langchain-core     | infer-union              |    17.1 |        33.5 |  2.0 |    0.86 |          1 |     1.17 | False |
| langchain-core     | tests-infer-union        |     8.6 |        38.8 |  4.5 |    1.15 |          5 |     1.44 | False |
| langchain-core     | tests                    |     2.2 |         2.1 |  1.0 |    0.17 |          2 |     0.21 | False |
| langchain-core     | types-released           |     5.0 |         3.5 |  0.7 |    0.32 |          1 |      0.4 | False |
| langchain-core     | types-fix-certain        |     3.2 |         3.1 |  1.0 |    0.27 |          1 |     0.34 | False |
| langchain-core     | types-fix-likely         |     5.2 |         4.3 |  0.8 |    0.27 |          1 |     0.34 | False |
| langchain-core     | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.32 | False |
| langchain-core     | types-infer-basedpyright |     6.0 |         4.3 |  0.7 |    0.27 |          1 |     0.34 | False |
| langchain-core     | types-infer-ty           |     5.6 |         4.4 |  0.8 |    0.27 |          1 |     0.34 | False |
| langchain-core     | types-infer-pyrefly      |     5.4 |         4.5 |  0.8 |    0.26 |          1 |     0.32 | False |
| langchain-core     | types-infer-trace        |     3.8 |         3.5 |  0.9 |    0.27 |          1 |     0.34 | False |
| langchain-core     | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| matplotlib         | check                    |    22.6 |        59.5 |  2.6 |    1.69 |          3 |     2.09 | False |
| matplotlib         | fix-certain              |    64.8 |       172.2 |  2.7 |    2.88 |          3 |     3.64 | False |
| matplotlib         | fix-likely               |    94.7 |       212.0 |  2.2 |    3.27 |          3 |     4.09 | False |
| matplotlib         | fix-unsafe               |    83.6 |       199.6 |  2.4 |     3.3 |          3 |     4.12 | False |
| matplotlib         | infer-basedpyright       |   130.7 |       255.0 |  2.0 |    3.52 |          1 |     3.55 | False |
| matplotlib         | infer-ty                 |   131.7 |       251.8 |  1.9 |    3.67 |          1 |     3.66 | False |
| matplotlib         | infer-pyrefly            |   124.9 |       257.9 |  2.1 |     3.7 |          1 |     4.76 | False |
| matplotlib         | census                   |    24.8 |         5.2 |  0.2 |    0.16 |          3 |     2.09 | False |
| matplotlib         | coverage                 |     3.0 |         7.4 |  2.5 |    0.45 |          3 |     0.56 | False |
| matplotlib         | timing                   |   107.0 |       136.3 |  1.3 |    1.67 |          1 |      2.1 | False |
| pint               | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.52 | False |
| pint               | fix-certain              |     5.8 |        11.8 |  2.0 |    0.47 |          2 |     0.59 | False |
| pint               | fix-likely               |     7.4 |        15.6 |  2.1 |    0.53 |          2 |     0.66 | False |
| pint               | fix-unsafe               |    13.3 |        19.6 |  1.5 |    0.53 |          2 |     0.72 | False |
| pint               | infer-basedpyright       |    64.8 |       112.6 |  1.7 |     3.0 |          1 |     0.33 | False |
| pint               | infer-ty                 |    25.7 |        46.6 |  1.8 |    3.29 |          1 |     0.34 | False |
| pint               | infer-pyrefly            |    14.5 |        26.2 |  1.8 |    1.89 |          1 |     0.33 | False |
| pint               | census                   |     3.4 |         5.3 |  1.6 |    0.42 |          2 |     0.52 | False |
| pint               | coverage                 |     0.8 |         1.6 |  2.0 |    0.22 |          2 |     0.27 | False |
| pint               | timing                   |     6.2 |         8.4 |  1.4 |    0.42 |          2 |     0.52 | False |
| pint               | traced                   |    57.8 |        53.5 |  0.9 |    0.55 |          1 |     0.69 | False |
| pint               | tests-released           |    64.4 |        32.8 |  0.5 |    0.15 |          1 |     0.19 | False |
| pint               | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-likely         |     0.3 |         0.2 |  0.7 |    0.03 |          1 |     0.19 | False |
| pint               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.19 | False |
| pint               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| pint               | infer-union              |   104.6 |       215.1 |  2.1 |    2.87 |          1 |     0.34 | False |
| pint               | tests-infer-union        |    35.1 |        31.7 |  0.9 |    0.15 |          1 |     0.19 | False |
| pint               | tests                    |     4.0 |         3.0 |  0.8 |    0.17 |          1 |     0.21 | False |
| pint               | types-released           |     6.0 |         9.9 |  1.7 |    0.53 |          2 |     0.67 | False |
| pint               | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-fix-unsafe         |     5.4 |         9.5 |  1.8 |    0.53 |          2 |     0.69 | False |
| pint               | types-infer-basedpyright |     6.2 |         9.9 |  1.6 |    0.55 |          2 |     0.66 | False |
| pint               | types-infer-ty           |     6.4 |        10.1 |  1.6 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-pyrefly      |     5.8 |         9.7 |  1.7 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-trace        |     5.4 |         9.2 |  1.7 |    0.54 |          2 |     0.69 | False |
| pint               | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.05 | False |
| altair             | fix-certain              |    16.8 |        23.1 |  1.4 |    0.96 |          2 |     1.19 | False |
| altair             | fix-likely               |    18.4 |        26.3 |  1.4 |    1.05 |          2 |      1.3 | False |
| altair             | fix-unsafe               |    26.5 |        29.2 |  1.1 |    1.05 |          2 |      1.3 | False |
| altair             | infer-basedpyright       |    67.8 |        86.9 |  1.3 |    3.26 |          1 |     1.37 | False |
| altair             | infer-ty                 |    45.7 |        43.6 |  1.0 |    1.84 |          1 |     1.31 | False |
| altair             | infer-pyrefly            |    38.3 |        40.9 |  1.1 |    2.26 |          1 |     1.32 | False |
| altair             | census                   |     7.2 |         9.6 |  1.3 |    0.84 |          2 |     1.05 | False |
| altair             | coverage                 |     1.2 |         2.0 |  1.7 |    0.28 |          2 |     0.36 | False |
| altair             | timing                   |    13.6 |        15.6 |  1.1 |    0.84 |          2 |     1.05 | False |
| altair             | traced                   |    50.4 |       204.2 |  4.1 |    6.62 |          4 |     6.74 | False |
| altair             | tests-released           |    17.2 |       121.6 |  7.1 |    4.89 |          8 |     5.85 | False |
| altair             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     5.71 | False |
| altair             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.56 | False |
| altair             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     5.89 | False |
| altair             | tests-infer-basedpyright |    22.7 |       137.1 |  6.0 |    4.62 |          7 |     5.74 | False |
| altair             | tests-infer-ty           |    21.2 |       136.6 |  6.4 |    4.68 |          8 |     5.74 | False |
| altair             | tests-infer-pyrefly      |    21.6 |       139.7 |  6.5 |    4.72 |          8 |     5.51 | False |
| altair             | tests-infer-trace        |    18.4 |       129.8 |  7.1 |    4.71 |          8 |     5.77 | False |
| altair             | infer-union              |    55.3 |        94.1 |  1.7 |     2.6 |          2 |     1.39 | False |
| altair             | tests-infer-union        |    83.9 |       137.8 |  1.6 |    4.51 |          8 |      6.1 | False |
| altair             | tests                    |     3.0 |         2.8 |  0.9 |    0.17 |          2 |     0.21 | False |
| altair             | types-released           |    11.2 |         7.1 |  0.6 |    0.43 |          1 |     0.54 | False |
| altair             | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.49 | False |
| altair             | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.49 | False |
| altair             | types-fix-unsafe         |     4.8 |         4.5 |  0.9 |    0.39 |          1 |     0.47 | False |
| altair             | types-infer-basedpyright |    11.3 |         7.0 |  0.6 |    0.39 |          1 |     0.49 | False |
| altair             | types-infer-ty           |     9.3 |         6.9 |  0.7 |    0.39 |          1 |     0.47 | False |
| altair             | types-infer-pyrefly      |    10.8 |         7.1 |  0.7 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-trace        |     6.6 |         6.1 |  0.9 |    0.38 |          1 |     0.49 | False |
| altair             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | check                    |     1.4 |         0.2 |  0.1 |    0.04 |          2 |     0.97 | False |
| seaborn            | fix-certain              |    14.6 |        22.1 |  1.5 |    0.93 |          2 |     1.17 | False |
| seaborn            | fix-likely               |    21.3 |        33.1 |  1.6 |    1.04 |          2 |      1.3 | False |
| seaborn            | fix-unsafe               |    17.9 |        27.8 |  1.6 |    0.97 |          2 |     1.21 | False |
| seaborn            | infer-basedpyright       |    92.9 |       141.4 |  1.5 |    4.18 |          2 |     1.47 | False |
| seaborn            | infer-ty                 |    62.5 |        57.0 |  0.9 |    1.94 |          1 |     0.65 | False |
| seaborn            | infer-pyrefly            |    37.7 |        45.1 |  1.2 |    2.15 |          2 |     1.36 | False |
| seaborn            | census                   |     5.2 |         8.1 |  1.6 |    0.78 |          2 |     0.97 | False |
| seaborn            | coverage                 |     0.8 |         1.5 |  1.9 |    0.21 |          2 |     0.26 | False |
| seaborn            | timing                   |    11.4 |        14.0 |  1.2 |    0.78 |          2 |     0.97 | False |
| seaborn            | traced                   |    61.5 |       439.8 |  7.2 |    3.67 |          8 |     4.65 | False |
| seaborn            | tests-released           |    43.6 |       403.7 |  9.3 |    3.39 |          8 |      4.3 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.26 | False |
| seaborn            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.29 | False |
| seaborn            | infer-union              |    98.4 |       160.6 |  1.6 |    3.32 |          1 |     1.93 | False |
| seaborn            | tests-infer-union        |    38.1 |       397.8 | 10.4 |    3.39 |          8 |     4.25 | False |
| seaborn            | tests                    |     1.8 |         1.5 |  0.8 |    0.17 |          2 |     0.21 | False |
| seaborn            | types-released           |     3.1 |         1.4 |  0.5 |    0.17 |          1 |     0.24 | False |
| seaborn            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| seaborn            | types-fix-likely         |     1.2 |         1.0 |  0.8 |    0.16 |          1 |     0.19 | False |
| seaborn            | types-fix-unsafe         |     0.3 |         0.1 |  0.3 |    0.03 |          1 |     0.21 | False |
| seaborn            | types-infer-basedpyright |     1.0 |         0.8 |  0.8 |    0.14 |          1 |     0.17 | False |
| seaborn            | types-infer-ty           |     1.2 |         1.0 |  0.8 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-pyrefly      |     1.4 |         1.2 |  0.9 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-trace        |     1.0 |         0.8 |  0.8 |    0.15 |          1 |     0.19 | False |
| seaborn            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.32 | False |
| aiohttp            | fix-certain              |     4.4 |         9.5 |  2.2 |    0.36 |          2 |     0.45 | False |
| aiohttp            | fix-likely               |     3.8 |         8.9 |  2.3 |    0.44 |          3 |     0.55 | False |
| aiohttp            | fix-unsafe               |     9.4 |        14.7 |  1.6 |    0.37 |          2 |     0.56 | False |
| aiohttp            | infer-basedpyright       |    40.3 |        61.2 |  1.5 |    1.65 |          1 |     0.18 | False |
| aiohttp            | infer-ty                 |    18.7 |        26.8 |  1.4 |    1.17 |          1 |     0.18 | False |
| aiohttp            | infer-pyrefly            |    14.4 |        19.6 |  1.4 |    0.84 |          1 |     0.27 | False |
| aiohttp            | census                   |     2.2 |         3.8 |  1.7 |    0.26 |          2 |     0.32 | False |
| aiohttp            | coverage                 |     0.8 |         1.5 |  1.9 |     0.2 |          2 |     0.25 | False |
| aiohttp            | timing                   |     3.8 |         5.2 |  1.4 |    0.26 |          2 |     0.32 | False |
| aiohttp            | traced                   |   109.7 |       748.2 |  6.8 |     3.0 |          1 |     3.74 | False |
| aiohttp            | tests-released           |    98.4 |       643.0 |  6.5 |    2.58 |          1 |     3.24 | False |
| aiohttp            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      3.2 | False |
| aiohttp            | infer-union              |    73.6 |        99.9 |  1.4 |     1.4 |          1 |     0.27 | False |
| aiohttp            | tests-infer-union        |   102.3 |       639.6 |  6.3 |    2.58 |          1 |     3.24 | False |
| aiohttp            | tests                    |     2.8 |         2.5 |  0.9 |    0.17 |          1 |     0.21 | False |
| websockets         | check                    |     1.2 |         1.9 |  1.6 |    0.21 |          2 |     0.26 | False |
| websockets         | fix-certain              |     2.0 |         4.5 |  2.2 |     0.3 |          3 |     0.37 | False |
| websockets         | fix-likely               |     2.8 |         6.2 |  2.2 |     0.3 |          3 |     0.37 | False |
| websockets         | fix-unsafe               |     4.5 |         6.8 |  1.5 |     0.3 |          2 |     0.37 | False |
| websockets         | infer-basedpyright       |    17.2 |        24.6 |  1.4 |    1.21 |          1 |     0.17 | False |
| websockets         | infer-ty                 |     7.8 |        11.0 |  1.4 |    0.76 |          1 |      0.2 | False |
| websockets         | infer-pyrefly            |     8.8 |        10.7 |  1.2 |    0.83 |          1 |     0.12 | False |
| websockets         | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.26 | False |
| websockets         | coverage                 |     0.6 |         0.8 |  1.3 |    0.17 |          2 |     0.21 | False |
| websockets         | timing                   |     2.2 |         2.8 |  1.3 |    0.21 |          2 |     0.26 | False |
| websockets         | traced                   |    45.5 |        16.2 |  0.4 |    0.34 |          1 |     0.42 | False |
| websockets         | tests-released           |    27.5 |         5.5 |  0.2 |    0.15 |          1 |     0.17 | False |
| websockets         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| websockets         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | infer-union              |    17.3 |        24.4 |  1.4 |    1.14 |          1 |     0.18 | False |
| websockets         | tests-infer-union        |    33.6 |         6.2 |  0.2 |    0.15 |          1 |     0.19 | False |
| websockets         | tests                    |     2.4 |         2.3 |  1.0 |    0.17 |          1 |     0.21 | False |
| websockets         | types-released           |     3.0 |         1.1 |  0.4 |    0.12 |          1 |     0.15 | False |
| websockets         | types-fix-certain        |     0.8 |         0.7 |  0.9 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-likely         |     1.0 |         0.9 |  0.9 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| websockets         | types-infer-basedpyright |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-ty           |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-pyrefly      |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.14 | False |
| websockets         | types-infer-trace        |     1.4 |         0.8 |  0.6 |    0.11 |          1 |     0.14 | False |
| websockets         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.27 | False |
| anyio              | fix-certain              |     3.6 |         6.3 |  1.8 |     0.3 |          2 |     0.37 | False |
| anyio              | fix-likely               |     3.8 |         7.0 |  1.8 |    0.31 |          2 |     0.37 | False |
| anyio              | fix-unsafe               |     8.6 |         8.6 |  1.0 |    0.35 |          2 |     0.39 | False |
| anyio              | infer-basedpyright       |    13.6 |        25.0 |  1.8 |     1.3 |          1 |     0.39 | False |
| anyio              | infer-ty                 |    13.6 |        13.5 |  1.0 |    0.85 |          1 |     0.22 | False |
| anyio              | infer-pyrefly            |    11.3 |        10.7 |  0.9 |    0.81 |          1 |     0.22 | False |
| anyio              | census                   |     1.6 |         2.1 |  1.3 |    0.22 |          2 |     0.27 | False |
| anyio              | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| anyio              | timing                   |     2.6 |         3.2 |  1.2 |    0.22 |          2 |     0.27 | False |
| anyio              | traced                   |   163.9 |        65.1 |  0.4 |    0.41 |          1 |      0.5 | False |
| anyio              | tests-released           |   119.3 |        48.2 |  0.4 |    0.26 |          1 |     0.34 | False |
| anyio              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.34 | False |
| anyio              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| anyio              | infer-union              |    22.7 |        24.8 |  1.1 |     1.1 |          1 |     0.19 | False |
| anyio              | tests-infer-union        |   160.3 |        56.5 |  0.4 |    0.27 |          1 |     0.34 | False |
| anyio              | tests                    |     3.6 |         3.0 |  0.8 |    0.17 |          1 |     0.21 | False |
| zarr               | check                    |     1.8 |         3.7 |  2.1 |    0.33 |          3 |     0.41 | False |
| zarr               | fix-certain              |     4.8 |        11.7 |  2.4 |    0.42 |          3 |     0.52 | False |
| zarr               | fix-likely               |     7.4 |        16.6 |  2.2 |    0.56 |          2 |      0.8 | False |
| zarr               | fix-unsafe               |    11.6 |        17.4 |  1.5 |    0.48 |          2 |     0.71 | False |
| zarr               | infer-basedpyright       |    39.3 |        75.1 |  1.9 |    2.69 |          2 |     1.76 | False |
| zarr               | infer-ty                 |    25.9 |        31.7 |  1.2 |    1.85 |          2 |     1.89 | False |
| zarr               | infer-pyrefly            |    25.3 |        29.1 |  1.2 |    1.99 |          1 |     0.34 | False |
| zarr               | census                   |     2.2 |         0.6 |  0.3 |    0.05 |          3 |     0.41 | False |
| zarr               | coverage                 |     1.0 |         1.6 |  1.6 |     0.2 |          2 |     0.26 | False |
| zarr               | timing                   |     4.2 |         6.3 |  1.5 |    0.33 |          2 |     0.41 | False |
| zarr               | traced                   |   182.4 |       295.8 |  1.6 |    2.59 |          3 |     3.32 | False |
| zarr               | tests-released           |   135.1 |       234.2 |  1.7 |    2.23 |          3 |     2.91 | False |
| zarr               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.04 |          4 |     3.01 | False |
| zarr               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.04 |          4 |     3.04 | False |
| zarr               | tests-fix-unsafe         |     0.5 |         0.2 |  0.4 |    0.03 |          3 |     2.91 | False |
| zarr               | tests-infer-basedpyright |    89.2 |       217.5 |  2.4 |    2.29 |          3 |     2.92 | False |
| zarr               | tests-infer-ty           |   106.5 |       232.2 |  2.2 |    2.35 |          3 |     2.99 | False |
| zarr               | tests-infer-pyrefly      |   103.6 |       215.2 |  2.1 |    2.34 |          3 |     2.97 | False |
| zarr               | tests-infer-trace        |   139.1 |       236.8 |  1.7 |    2.26 |          3 |     3.02 | False |
| zarr               | infer-union              |    37.8 |       110.9 |  2.9 |    2.48 |          3 |     0.69 | False |
| zarr               | tests-infer-union        |   143.4 |       235.7 |  1.6 |    2.42 |          3 |     2.76 | False |
| zarr               | tests                    |     2.0 |         1.9 |  0.9 |    0.17 |          2 |     0.21 | False |
| joblib             | check                    |     2.6 |         4.0 |  1.5 |    0.37 |          2 |     0.46 | False |
| joblib             | fix-certain              |     5.4 |        10.2 |  1.9 |    0.43 |          2 |     0.55 | False |
| joblib             | fix-likely               |     5.4 |        10.8 |  2.0 |    0.46 |          2 |     0.57 | False |
| joblib             | fix-unsafe               |    11.4 |        14.3 |  1.3 |    0.47 |          2 |     0.57 | False |
| joblib             | infer-basedpyright       |    41.5 |        68.6 |  1.7 |    2.32 |          1 |     0.29 | False |
| joblib             | infer-ty                 |    27.3 |        29.6 |  1.1 |     1.0 |          1 |     0.29 | False |
| joblib             | infer-pyrefly            |    14.7 |        20.6 |  1.4 |    1.41 |          1 |     0.32 | False |
| joblib             | census                   |     0.8 |         0.6 |  0.7 |    0.05 |          2 |     0.46 | False |
| joblib             | coverage                 |     0.8 |         1.2 |  1.5 |     0.2 |          2 |     0.25 | False |
| joblib             | timing                   |     4.8 |         6.2 |  1.3 |    0.37 |          2 |     0.46 | False |
| joblib             | traced                   |   231.5 |       503.9 |  2.2 |    1.12 |          1 |     1.39 | False |
| joblib             | tests-released           |   218.0 |       494.7 |  2.3 |     1.1 |          1 |     1.36 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-fix-likely         |     0.3 |         0.2 |  0.7 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-infer-basedpyright |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.32 | False |
| joblib             | tests-infer-ty           |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-infer-pyrefly      |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     1.34 | False |
| joblib             | infer-union              |   121.4 |       122.4 |  1.0 |    1.96 |          1 |     0.31 | False |
| joblib             | tests-infer-union        |   179.5 |       505.2 |  2.8 |    1.08 |          1 |     1.37 | False |
| joblib             | tests                    |     2.4 |         2.1 |  0.9 |    0.17 |          1 |     0.21 | False |
| networkx           | check                    |    13.2 |         0.4 |  0.0 |    0.07 |          2 |      1.7 | False |
| networkx           | fix-certain              |    31.6 |        72.4 |  2.3 |    1.62 |          3 |     2.04 | False |
| networkx           | fix-likely               |    43.7 |       106.7 |  2.4 |    2.17 |          3 |     2.71 | False |
| networkx           | fix-unsafe               |    79.7 |       127.0 |  1.6 |    2.17 |          2 |     2.87 | False |
| networkx           | infer-basedpyright       |   289.6 |       429.3 |  1.5 |    5.23 |          1 |     1.32 | False |
| networkx           | infer-ty                 |   103.9 |       180.8 |  1.7 |    4.16 |          2 |     2.62 | False |
| networkx           | infer-pyrefly            |   130.0 |       203.9 |  1.6 |    5.64 |          1 |     1.32 | False |
| networkx           | census                   |    17.2 |        34.5 |  2.0 |    1.36 |          2 |      1.7 | False |
| networkx           | coverage                 |     2.4 |         6.2 |  2.6 |     0.4 |          3 |      0.5 | False |
| networkx           | timing                   |    44.1 |        60.7 |  1.4 |    1.36 |          2 |      1.7 | False |
| networkx           | traced                   |    63.3 |       294.7 |  4.7 |    2.61 |          7 |      3.2 | False |
| networkx           | tests-released           |    29.5 |       236.9 |  8.0 |    2.39 |          8 |     2.94 | False |
| networkx           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      3.0 | False |
| networkx           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.02 | False |
| networkx           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.99 | False |
| networkx           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.01 | False |
| networkx           | infer-union              |   228.1 |       709.6 |  3.1 |    6.32 |          3 |     5.99 | False |
| networkx           | tests-infer-union        |    22.2 |       203.7 |  9.2 |    2.34 |          8 |     2.95 | False |
| networkx           | tests                    |     2.0 |         1.8 |  0.9 |    0.17 |          2 |     0.21 | False |
| networkx           | types-released           |     7.4 |         3.6 |  0.5 |    0.35 |          1 |     0.44 | False |
| networkx           | types-fix-certain        |     0.6 |         0.5 |  0.8 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-likely         |     0.6 |         0.5 |  0.8 |    0.05 |          1 |     0.44 | False |
| networkx           | types-fix-unsafe         |     4.1 |         2.9 |  0.7 |    0.26 |          1 |     0.32 | False |
| networkx           | types-infer-basedpyright |     3.6 |         3.3 |  0.9 |    0.31 |          1 |     0.39 | False |
| networkx           | types-infer-ty           |     5.0 |         3.7 |  0.7 |     0.3 |          1 |     0.39 | False |
| networkx           | types-infer-pyrefly      |     6.5 |         4.1 |  0.6 |    0.33 |          1 |     0.41 | False |
| networkx           | types-infer-trace        |     6.2 |         4.4 |  0.7 |    0.32 |          1 |     0.36 | False |
| networkx           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| nibabel            | check                    |     5.2 |        11.6 |  2.2 |    0.64 |          3 |      0.8 | False |
| nibabel            | fix-certain              |    11.0 |        26.1 |  2.4 |    0.76 |          3 |     0.94 | False |
| nibabel            | fix-likely               |    14.4 |        33.1 |  2.3 |    0.99 |          3 |     1.24 | False |
| nibabel            | fix-unsafe               |    17.2 |        37.3 |  2.2 |     0.9 |          3 |     1.19 | False |
| nibabel            | infer-basedpyright       |    96.0 |       292.8 |  3.1 |    4.28 |          1 |     0.62 | False |
| nibabel            | infer-ty                 |    68.5 |       184.9 |  2.7 |    3.09 |          1 |     0.62 | False |
| nibabel            | infer-pyrefly            |    39.4 |        74.2 |  1.9 |    3.24 |          1 |     0.64 | False |
| nibabel            | census                   |     1.6 |         1.5 |  0.9 |    0.07 |          3 |      0.8 | False |
| nibabel            | coverage                 |     1.2 |         2.6 |  2.2 |    0.26 |          2 |     0.32 | False |
| nibabel            | timing                   |    11.6 |        17.3 |  1.5 |    0.64 |          2 |      0.8 | False |
| nibabel            | traced                   |    32.3 |       131.9 |  4.1 |    1.19 |          6 |     1.46 | False |
| nibabel            | tests-released           |    13.2 |        83.4 |  6.3 |    1.04 |          8 |      1.3 | False |
| nibabel            | tests-fix-certain        |    14.6 |        87.2 |  6.0 |    1.03 |          7 |     1.29 | False |
| nibabel            | tests-fix-likely         |    13.4 |        88.4 |  6.6 |    1.05 |          7 |      1.3 | False |
| nibabel            | tests-fix-unsafe         |    11.8 |        87.5 |  7.4 |    1.04 |          7 |     1.29 | False |
| nibabel            | tests-infer-basedpyright |    14.0 |        95.8 |  6.8 |    1.05 |          7 |      1.3 | False |
| nibabel            | tests-infer-ty           |    15.2 |        88.9 |  5.8 |    1.05 |          7 |     1.32 | False |
| nibabel            | tests-infer-pyrefly      |    16.4 |        93.3 |  5.7 |    1.07 |          5 |     1.27 | False |
| nibabel            | tests-infer-trace        |    15.3 |        93.8 |  6.1 |    1.04 |          5 |      1.3 | False |
| nibabel            | infer-union              |   111.0 |       413.8 |  3.7 |     4.5 |          2 |     0.87 | False |
| nibabel            | tests-infer-union        |    14.2 |        93.1 |  6.6 |    1.02 |          7 |     1.32 | False |
| nibabel            | tests                    |    31.9 |       184.1 |  5.8 |    1.13 |          8 |      1.4 | False |
| nibabel            | types-released           |     5.0 |         2.6 |  0.5 |    0.18 |          1 |     0.22 | False |
| nibabel            | types-fix-certain        |     2.4 |         2.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-fix-likely         |     2.6 |         2.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-fix-unsafe         |     1.7 |         1.5 |  0.9 |    0.14 |          1 |     0.17 | False |
| nibabel            | types-infer-basedpyright |     3.5 |         2.5 |  0.7 |    0.16 |          1 |     0.21 | False |
| nibabel            | types-infer-ty           |     3.4 |         2.6 |  0.8 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-infer-pyrefly      |     3.6 |         2.4 |  0.7 |    0.17 |          1 |     0.21 | False |
| nibabel            | types-infer-trace        |     2.4 |         2.1 |  0.9 |    0.17 |          1 |     0.21 | False |
| nibabel            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.65 | False |
| narwhals           | fix-certain              |     6.8 |        17.3 |  2.5 |    0.53 |          3 |     0.66 | False |
| narwhals           | fix-likely               |    15.0 |        34.9 |  2.3 |    1.06 |          2 |     1.31 | False |
| narwhals           | fix-unsafe               |    17.2 |        36.4 |  2.1 |    1.05 |          2 |     1.42 | False |
| narwhals           | infer-basedpyright       |    52.3 |       137.9 |  2.6 |    4.71 |          1 |     0.66 | False |
| narwhals           | infer-ty                 |    45.9 |        84.5 |  1.8 |    3.71 |          1 |     0.66 | False |
| narwhals           | infer-pyrefly            |    45.9 |        61.4 |  1.3 |    3.46 |          1 |     0.66 | False |
| narwhals           | census                   |     5.4 |        10.5 |  1.9 |    0.53 |          3 |     0.65 | False |
| narwhals           | coverage                 |     1.2 |         2.6 |  2.2 |    0.21 |          3 |     0.26 | False |
| narwhals           | timing                   |    12.0 |        15.8 |  1.3 |    0.53 |          2 |     0.66 | False |
| narwhals           | traced                   |    56.7 |       245.5 |  4.3 |    4.88 |          6 |     5.96 | False |
| narwhals           | tests-released           |    42.4 |       197.4 |  4.7 |    4.03 |          7 |     5.69 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-fix-unsafe         |     0.3 |         0.1 |  0.3 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.04 | False |
| narwhals           | tests-infer-trace        |     0.3 |         0.2 |  0.7 |    0.03 |          8 |     5.51 | False |
| narwhals           | infer-union              |    58.1 |       208.2 |  3.6 |    4.13 |          1 |     0.67 | False |
| narwhals           | tests-infer-union        |    40.1 |       154.3 |  3.8 |    4.51 |          8 |     5.64 | False |
| narwhals           | tests                    |     2.0 |         1.8 |  0.9 |    0.17 |          2 |     0.21 | False |
| narwhals           | types-released           |    32.3 |        55.6 |  1.7 |    1.57 |          2 |     1.99 | False |
| narwhals           | types-fix-certain        |    25.0 |        52.1 |  2.1 |    1.62 |          2 |      2.0 | False |
| narwhals           | types-fix-likely         |    21.6 |        46.7 |  2.2 |    1.62 |          2 |     1.94 | False |
| narwhals           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.91 | False |
| narwhals           | types-infer-basedpyright |    22.2 |        48.7 |  2.2 |    1.59 |          2 |      2.1 | False |
| narwhals           | types-infer-ty           |    33.5 |        58.7 |  1.8 |    1.56 |          2 |     1.91 | False |
| narwhals           | types-infer-pyrefly      |    21.8 |        47.6 |  2.2 |    1.58 |          2 |     1.96 | False |
| narwhals           | types-infer-trace        |    30.5 |        55.5 |  1.8 |     1.6 |          2 |     1.94 | False |
| narwhals           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| xarray             | check                    |    17.6 |         0.4 |  0.0 |    0.08 |          2 |     1.77 | False |
| xarray             | fix-certain              |    47.4 |        97.1 |  2.0 |    1.94 |          2 |     2.41 | False |
| xarray             | fix-likely               |    50.1 |       114.9 |  2.3 |    2.54 |          3 |     3.17 | False |
| xarray             | fix-unsafe               |   137.9 |       157.5 |  1.1 |    2.51 |          2 |     3.26 | False |
| xarray             | infer-basedpyright       |   359.6 |       561.0 |  1.6 |     6.1 |          1 |     1.66 | False |
| xarray             | infer-ty                 |   214.6 |       319.9 |  1.5 |    5.68 |          1 |     1.62 | False |
| xarray             | infer-pyrefly            |   188.9 |       226.3 |  1.2 |     6.7 |          1 |     1.69 | False |
| xarray             | census                   |    23.6 |        43.5 |  1.8 |    1.42 |          2 |     1.77 | False |
| xarray             | coverage                 |     5.0 |         8.8 |  1.8 |    0.46 |          3 |     0.59 | False |
| xarray             | timing                   |    63.4 |        82.9 |  1.3 |    1.42 |          2 |     1.77 | False |
| xarray             | traced                   |    85.8 |       237.9 |  2.8 |     2.6 |          4 |     3.25 | False |
| xarray             | tests-released           |    26.2 |       127.2 |  4.9 |    1.97 |          6 |      2.5 | False |
| xarray             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-trace        |     0.3 |         0.2 |  0.7 |    0.03 |          8 |      2.5 | False |
| xarray             | infer-union              |   244.4 |       607.5 |  2.5 |    5.86 |          1 |     1.74 | False |
| xarray             | tests-infer-union        |    15.6 |        93.8 |  6.0 |    1.95 |          8 |     2.45 | False |
| xarray             | tests                    |     2.6 |         2.4 |  0.9 |    0.17 |          2 |     0.21 | False |
| litestar           | check                    |     2.0 |         0.2 |  0.1 |    0.04 |          2 |     0.57 | False |
| litestar           | fix-certain              |     9.4 |        18.3 |  1.9 |    0.69 |          3 |     0.86 | False |
| litestar           | fix-likely               |    11.6 |        22.8 |  2.0 |    0.94 |          3 |      1.2 | False |
| litestar           | fix-unsafe               |    14.5 |        21.9 |  1.5 |    0.74 |          2 |     0.92 | False |
| litestar           | infer-basedpyright       |    49.2 |       124.2 |  2.5 |    4.29 |          1 |     0.51 | False |
| litestar           | infer-ty                 |    27.1 |        45.9 |  1.7 |    2.24 |          1 |     0.51 | False |
| litestar           | infer-pyrefly            |    21.1 |        35.5 |  1.7 |    2.66 |          1 |     0.46 | False |
| litestar           | census                   |     3.2 |         6.3 |  2.0 |    0.45 |          2 |     0.57 | False |
| litestar           | coverage                 |     1.0 |         2.2 |  2.2 |     0.2 |          2 |     0.25 | False |
| litestar           | timing                   |     8.0 |        11.1 |  1.4 |    0.46 |          2 |     0.57 | False |
| litestar           | traced                   |    41.8 |       189.7 |  4.5 |    4.22 |          6 |      5.3 | False |
| litestar           | tests-released           |    38.1 |       168.6 |  4.4 |    3.87 |          5 |     4.84 | False |
| litestar           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.66 | False |
| litestar           | tests-fix-likely         |     0.3 |         0.1 |  0.3 |    0.03 |          6 |     4.67 | False |
| litestar           | tests-fix-unsafe         |     0.3 |         0.1 |  0.3 |    0.03 |          5 |     4.84 | False |
| litestar           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.61 | False |
| litestar           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          7 |     4.84 | False |
| litestar           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.61 | False |
| litestar           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.76 | False |
| litestar           | infer-union              |    41.5 |       162.4 |  3.9 |    3.57 |          2 |     0.92 | False |
| litestar           | tests-infer-union        |    25.6 |       143.0 |  5.6 |    3.77 |          7 |     4.72 | False |
| litestar           | tests                    |     1.8 |         1.6 |  0.9 |    0.17 |          7 |     4.74 | False |
| litestar           | types-released           |    54.0 |        71.6 |  1.3 |    2.04 |          2 |     2.55 | False |
| litestar           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     2.55 | False |
| litestar           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.55 | False |
| litestar           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.45 | False |
| litestar           | types-infer-basedpyright |    45.3 |        67.9 |  1.5 |    1.89 |          2 |     2.39 | False |
| litestar           | types-infer-ty           |    37.1 |        60.6 |  1.6 |    1.88 |          2 |     2.36 | False |
| litestar           | types-infer-pyrefly      |    44.1 |        66.9 |  1.5 |    1.88 |          2 |     2.35 | False |
| litestar           | types-infer-trace        |    46.0 |        64.6 |  1.4 |    1.89 |          2 |     2.36 | False |
| litestar           | types                    |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.04 | False |
| stripe             | check                    |     5.2 |        13.9 |  2.7 |     0.7 |          3 |     0.87 | False |
| stripe             | fix-certain              |    17.4 |        51.1 |  2.9 |    0.87 |          3 |     1.09 | False |
| stripe             | fix-likely               |    18.0 |        54.2 |  3.0 |     1.0 |          3 |      1.3 | False |
| stripe             | fix-unsafe               |    18.0 |        55.5 |  3.1 |    1.04 |          3 |      1.3 | False |
| stripe             | infer-basedpyright       |  1061.2 |      2673.1 |  2.5 |    4.36 |          3 |     5.59 | False |
| stripe             | infer-ty                 |    44.6 |        87.7 |  2.0 |    2.01 |          2 |     2.44 | False |
| stripe             | infer-pyrefly            |    50.5 |        91.9 |  1.8 |    3.13 |          1 |     1.27 | False |
| stripe             | census                   |     4.8 |         1.6 |  0.3 |    0.07 |          3 |     0.87 | False |
| stripe             | coverage                 |     6.1 |        10.1 |  1.7 |    0.27 |          2 |     0.34 | False |
| stripe             | timing                   |    35.1 |        40.2 |  1.1 |    0.71 |          2 |     0.87 | False |
| celery             | check                    |     3.4 |         0.2 |  0.1 |    0.04 |          2 |     1.21 | False |
| celery             | fix-certain              |    21.6 |        31.2 |  1.4 |    1.21 |          2 |     1.51 | False |
| celery             | fix-likely               |    33.2 |        40.7 |  1.2 |    1.35 |          2 |     1.79 | False |
| celery             | fix-unsafe               |    55.9 |        37.5 |  0.7 |    1.26 |          2 |     1.57 | False |
| celery             | infer-basedpyright       |    85.2 |       136.9 |  1.6 |    4.31 |          1 |     1.64 | False |
| celery             | infer-ty                 |    37.9 |        49.4 |  1.3 |     2.4 |          1 |     0.76 | False |
| celery             | infer-pyrefly            |    48.4 |        47.5 |  1.0 |    2.59 |          1 |     0.76 | False |
| celery             | census                   |     7.8 |        11.6 |  1.5 |    0.97 |          2 |     1.21 | False |
| celery             | coverage                 |     1.0 |         1.8 |  1.8 |    0.22 |          2 |     0.27 | False |
| celery             | timing                   |    17.0 |        20.6 |  1.2 |    0.97 |          2 |     1.21 | False |
| celery             | traced                   |    96.8 |       112.3 |  1.2 |    3.97 |          2 |     4.96 | False |
| celery             | tests-released           |    56.9 |        60.7 |  1.1 |    3.33 |          2 |     4.16 | False |
| celery             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     4.16 | False |
| celery             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     4.04 | False |
| celery             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.16 | False |
| celery             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.16 | False |
| celery             | tests-infer-ty           |     0.2 |         0.2 |  1.0 |    0.03 |          2 |     4.16 | False |
| celery             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     4.16 | False |
| celery             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      4.0 | False |
| celery             | infer-union              |    78.5 |       162.5 |  2.1 |    3.53 |          2 |     1.65 | False |
| celery             | tests-infer-union        |    58.5 |        59.5 |  1.0 |    3.29 |          2 |      4.1 | False |
| celery             | tests                    |     2.4 |         2.3 |  1.0 |    0.17 |          2 |     0.21 | False |
| optuna             | check                    |     5.2 |        10.3 |  2.0 |    0.76 |          2 |     0.95 | False |
| optuna             | fix-certain              |    14.0 |        26.0 |  1.9 |    1.19 |          3 |     1.49 | False |
| optuna             | fix-likely               |    28.3 |        50.8 |  1.8 |    1.66 |          2 |     2.16 | False |
| optuna             | fix-unsafe               |    73.3 |        66.7 |  0.9 |    1.38 |          2 |     1.77 | False |
| optuna             | infer-basedpyright       |    74.5 |       162.2 |  2.2 |    6.03 |          2 |     2.04 | False |
| optuna             | infer-ty                 |    41.3 |        74.1 |  1.8 |    3.31 |          2 |     2.04 | False |
| optuna             | infer-pyrefly            |    33.7 |        63.7 |  1.9 |    3.86 |          1 |     2.05 | False |
| optuna             | census                   |     5.4 |         1.0 |  0.2 |    0.05 |          2 |     0.95 | False |
| optuna             | coverage                 |     1.0 |         1.6 |  1.6 |     0.2 |          2 |     0.25 | False |
| optuna             | timing                   |    14.0 |        19.3 |  1.4 |    0.76 |          2 |     0.95 | False |
| optuna             | traced                   |   176.9 |      1402.1 |  7.9 |    5.06 |          8 |     5.95 | False |
| optuna             | tests-released           |   120.5 |       925.9 |  7.7 |    3.77 |          8 |     5.29 | False |
| optuna             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     4.89 | False |
| optuna             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.89 | False |
| optuna             | infer-union              |    60.3 |       182.4 |  3.0 |    4.45 |          2 |     2.05 | False |
| optuna             | tests-infer-union        |   170.6 |      1577.7 |  9.2 |     4.2 |          8 |      5.3 | False |
| optuna             | tests                    |     2.2 |         1.8 |  0.8 |    0.17 |          2 |     0.21 | False |
| optuna             | types-released           |    16.0 |         7.3 |  0.5 |    0.47 |          1 |     0.62 | False |
| optuna             | types-fix-certain        |     4.6 |         4.4 |  1.0 |    0.37 |          1 |      0.5 | False |
| optuna             | types-fix-likely         |     7.4 |         5.7 |  0.8 |    0.37 |          1 |     0.46 | False |
| optuna             | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          1 |     0.59 | False |
| optuna             | types-infer-basedpyright |     8.6 |         6.8 |  0.8 |    0.38 |          1 |     0.46 | False |
| optuna             | types-infer-ty           |    12.0 |         7.1 |  0.6 |    0.39 |          1 |     0.47 | False |
| optuna             | types-infer-pyrefly      |     9.8 |         6.2 |  0.6 |    0.39 |          1 |     0.47 | False |
| optuna             | types-infer-trace        |     2.8 |         2.8 |  1.0 |    0.37 |          1 |      0.5 | False |
| optuna             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | check                    |    29.0 |        56.0 |  1.9 |     1.8 |          2 |     2.25 | False |
| dask               | fix-certain              |    68.2 |       124.6 |  1.8 |    2.36 |          2 |     2.96 | False |
| dask               | fix-likely               |   100.6 |       169.8 |  1.7 |    3.11 |          2 |     3.89 | False |
| dask               | fix-unsafe               |   118.2 |       183.5 |  1.6 |     3.1 |          2 |     3.89 | False |
| dask               | infer-basedpyright       |   239.4 |       732.1 |  3.1 |    9.86 |          1 |     3.83 | False |
| dask               | infer-ty                 |   172.3 |       384.6 |  2.2 |    6.63 |          1 |     1.98 | False |
| dask               | infer-pyrefly            |   131.7 |       256.8 |  1.9 |    8.01 |          1 |     4.25 | False |
| dask               | census                   |    30.7 |         5.3 |  0.2 |    0.14 |          2 |     2.25 | False |
| dask               | coverage                 |     3.8 |         8.1 |  2.1 |    0.46 |          3 |     0.57 | False |
| dask               | timing                   |    68.5 |        94.9 |  1.4 |     1.8 |          2 |     2.25 | False |
| dask               | traced                   |   178.5 |      1182.2 |  6.6 |    4.62 |          8 |     5.96 | False |
| dask               | tests-released           |   167.1 |      1257.3 |  7.5 |    4.45 |          7 |     5.69 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.82 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.76 | False |
| dask               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.82 | False |
| dask               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.82 | False |
| dask               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.64 | False |
| dask               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     5.52 | False |
| dask               | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      5.4 | False |
| dask               | infer-union              |   271.7 |       831.9 |  3.1 |    9.09 |          3 |    10.11 | False |
| dask               | tests-infer-union        |   176.3 |      1070.8 |  6.1 |    4.49 |          8 |     5.59 | False |
| dask               | tests                    |     2.0 |         1.9 |  0.9 |    0.17 |          2 |     0.21 | False |
| mypy               | check                    |     0.4 |         0.3 |  0.7 |    0.06 |          3 |     0.69 | False |
| mypy               | fix-certain              |    11.4 |        38.2 |  3.4 |    0.82 |          4 |     1.05 | False |
| mypy               | fix-likely               |    22.2 |        60.4 |  2.7 |     1.0 |          4 |     1.25 | False |
| mypy               | fix-unsafe               |    18.6 |        56.3 |  3.0 |    0.96 |          3 |     1.17 | False |
| mypy               | infer-basedpyright       |    80.8 |       162.6 |  2.0 |    3.13 |          1 |     0.42 | False |
| mypy               | infer-ty                 |    43.9 |        99.3 |  2.3 |    2.35 |          1 |     1.08 | False |
| mypy               | infer-pyrefly            |    35.7 |        78.0 |  2.2 |    2.93 |          1 |      0.4 | False |
| mypy               | census                   |     6.6 |        15.2 |  2.3 |    0.54 |          3 |     0.69 | False |
| mypy               | coverage                 |     4.0 |         7.5 |  1.9 |    0.36 |          3 |     0.46 | False |
| mypy               | timing                   |    18.6 |        29.0 |  1.6 |    0.55 |          2 |     0.69 | False |
| mypy               | traced                   |   301.0 |      2072.5 |  6.9 |    6.42 |          8 |     8.14 | False |
| mypy               | tests-released           |   303.7 |      2040.7 |  6.7 |     5.8 |          8 |     7.69 | False |
| mypy               | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     7.61 | False |
| mypy               | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     7.47 | False |
| mypy               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     7.61 | False |
| mypy               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.61 | False |
| mypy               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.61 | False |
| mypy               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.61 | False |
| mypy               | tests-infer-trace        |     0.3 |         0.1 |  0.3 |    0.03 |          7 |     7.65 | False |
| mypy               | infer-union              |    63.7 |       185.1 |  2.9 |    2.84 |          1 |      1.1 | False |
| mypy               | tests-infer-union        |   280.0 |      1991.7 |  7.1 |     6.0 |          8 |     7.61 | False |
| mypy               | tests                    |     2.8 |         2.4 |  0.9 |    0.17 |          2 |     0.21 | False |
| mypy               | types-released           |    10.8 |        26.8 |  2.5 |    0.62 |          3 |     0.77 | False |
| mypy               | types-fix-certain        |     7.8 |        20.1 |  2.6 |     0.5 |          3 |     0.62 | False |
| mypy               | types-fix-likely         |     8.2 |        20.2 |  2.5 |     0.5 |          3 |     0.77 | False |
| mypy               | types-fix-unsafe         |     0.6 |         0.4 |  0.7 |    0.05 |          3 |     0.77 | False |
| mypy               | types-infer-basedpyright |    10.6 |        26.9 |  2.5 |    0.62 |          3 |     0.79 | False |
| mypy               | types-infer-ty           |     8.2 |        19.4 |  2.4 |     0.5 |          3 |     0.61 | False |
| mypy               | types-infer-pyrefly      |     8.2 |        18.4 |  2.2 |    0.49 |          3 |     0.62 | False |
| mypy               | types-infer-trace        |    11.6 |        28.7 |  2.5 |    0.63 |          3 |     0.77 | False |
| mypy               | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |

The likely fixes the unsafe fixes leave out or write otherwise, where there are any (the fixes
interact, so unsafe isn't likely with more):

| corpus     | likely | absent from unsafe | annotated otherwise |
| ---------- | -----: | -----------------: | ------------------: |
| matplotlib |  9,605 |                  0 |                   1 |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,392 |       4,320 |     1 |
| sphinx | likely             |          929 | 3,931 |       4,859 |     1 |
| sphinx | unsafe             |          929 | 4,335 |       5,263 |     1 |
| sphinx | infer-basedpyright |          929 | 5,091 |       6,019 |     1 |
| sphinx | infer-ty           |          929 | 5,204 |       6,132 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,325 |       6,253 |     1 |
| sphinx | infer-trace        |          929 | 4,335 |       5,263 |     1 |
| mypy   | unsafe             |        2,300 | 7,498 |       9,797 |     1 |
| mypy   | infer-basedpyright |        2,300 | 9,140 |      11,438 |     2 |
| mypy   | infer-ty           |        2,300 | 9,445 |      11,743 |     2 |
| mypy   | infer-pyrefly      |        2,300 | 9,663 |      11,961 |     2 |
| mypy   | infer-trace        |        2,300 | 7,498 |       9,797 |     1 |

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
| requests           | 617 passed, 15 skipped, 1 xpassed                                     | 617 passed, 15 skipped, 1 xpassed                                     | True          |
| rich               | 956 passed, 25 skipped                                                | 956 passed, 25 skipped                                                | True          |
| urllib3            | 2,418 passed, 288 skipped, 4 xfailed                                  | 2,418 passed, 288 skipped, 4 xfailed                                  | True          |
| sqlmodel           | 1 failed, 267 passed                                                  | 1 failed, 267 passed                                                  | True          |
| marshmallow        | 1,188 passed                                                          | 1,188 passed                                                          | True          |
| pdm                | 1,472 passed, 1 skipped                                               | 1,472 passed, 1 skipped                                               | True          |
| strawberry-graphql | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | False         |
| pygments           | 5,330 passed, 16 skipped                                              | 5,330 passed, 16 skipped                                              | True          |
| streamlink         | 9 error, 15 failed, 7,233 passed, 36 skipped                          | 9 error, 15 failed, 7,233 passed, 36 skipped                          | True          |
| sphinx             | 8 failed, 2,393 passed, 23 skipped                                    | 7 failed, 2,394 passed, 23 skipped                                    | False         |
| tox                | 6 error, 17 failed, 8,525 passed, 31 skipped                          | 6 error, 17 failed, 8,525 passed, 31 skipped                          | True          |
| trio               | 871 passed, 23 skipped, 3 xfailed                                     | 871 passed, 23 skipped, 3 xfailed                                     | True          |
| langchain-core     | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed              | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed              | False         |
| pint               | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | True          |
| altair             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             | True          |
| seaborn            | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | False         |
| aiohttp            | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | True          |
| websockets         | 2,589 ran, 8 skipped                                                  | 2,589 ran, 8 skipped                                                  | True          |
| anyio              | 3,824 passed, 19 skipped, 5 xfailed                                   | 3,824 passed, 19 skipped, 5 xfailed                                   | True          |
| zarr               | 8,422 passed, 1,205 skipped, 4 xfailed                                | 1 failed, 8,421 passed, 1,205 skipped, 4 xfailed                      | False         |
| joblib             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         | 10 failed, 1,482 passed, 45 skipped, 4 xpassed                        | False         |
| networkx           | 10,083 passed, 62 skipped, 741 xfailed                                | 10,083 passed, 62 skipped, 741 xfailed                                | True          |
| nibabel            | 19 error, 108 failed, 5,169 passed, 303 skipped, 40 xfailed           | 20 error, 110 failed, 5,167 passed, 303 skipped, 40 xfailed           | False         |
| narwhals           | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | True          |
| xarray             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed | 3 error, 3 failed, 6,333 passed, 9,626 skipped, 11 xfailed, 4 xpassed | False         |
| litestar           | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           | True          |
| celery             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         | 4 failed, 3,520 passed, 36 skipped, 3 xfailed                         | False         |
| optuna             | 16 error, 263 failed, 4,203 passed, 43 skipped                        | 16 error, 263 failed, 4,203 passed, 43 skipped                        | False         |
| dask               | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | 5 failed, 16,196 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | False         |
| mypy               | 14,464 passed, 366 skipped, 12 xfailed                                | 14,464 passed, 366 skipped, 12 xfailed                                | True          |

- standard library, mega+dev, infer-basedpyright: held 14.37 GB beside other steps
- standard library, mega+dev, infer-ty: held 14.26 GB beside other steps
- standard library, mega+dev, infer-pyrefly: held 16.4 GB beside other steps
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
- pydantic, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, infer-basedpyright: held 13.07 GB beside other steps
- pandas, mega+dev, infer-ty: held 11.97 GB beside other steps
- pandas, mega+dev, infer-pyrefly: held 13.82 GB beside other steps
- pandas, mega+dev, traced: held 14.4 GB beside other steps
- pandas, mega+dev, tests-released: held 11.49 GB beside other steps
- pandas, mega+dev, infer-union: held 12.75 GB beside other steps
- pandas, mega+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, mega+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pandas, mega+dev, tests-infer-union: held 13.52 GB beside other steps
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
- pytest, mega+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
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
- mcp, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- requests, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- requests, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- requests, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- requests, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- rich, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- rich, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- rich, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- rich, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- urllib3, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- urllib3, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- urllib3, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- sqlmodel, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- sqlmodel, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- sqlmodel, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- sqlmodel, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- marshmallow, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- marshmallow, mega+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- marshmallow, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- marshmallow, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- marshmallow, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- marshmallow, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, mega+dev, infer-union: pyrefly's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pdm, mega+dev, infer-union: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- strawberry-graphql, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- strawberry-graphql, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store, so
  its seconds measure less of the checker
- pygments, mega+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pygments, mega+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its seconds
  measure less of the checker
- streamlink, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- tox, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- trio, mega+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- trio, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- trio, mega+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- trio, mega+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- trio, mega+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- trio, mega+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- langchain-core, mega+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- langchain-core, mega+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- langchain-core, mega+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- langchain-core, mega+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store,
  so its seconds measure less of the checker
- langchain-core, mega+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- langchain-core, mega+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- matplotlib, mega+dev, infer-basedpyright: basedpyright's hints for 5 of 5 rounds came from the
  store, so its seconds measure less of the checker
- matplotlib, mega+dev, infer-ty: ty's hints for 5 of 5 rounds came from the store, so its seconds
  measure less of the checker
- matplotlib, mega+dev, infer-pyrefly: pyrefly's hints for 5 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pint, mega+dev, infer-union: basedpyright's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pint, mega+dev, infer-union: pyrefly's hints for 2 of 6 rounds came from the store, so its seconds
  measure less of the checker
- pint, mega+dev, infer-union: ty's hints for 2 of 6 rounds came from the store, so its seconds
  measure less of the checker
- altair, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
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
- aiohttp, mega+dev, infer-union: basedpyright's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, mega+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its seconds
  measure less of the checker
- websockets, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- websockets, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- websockets, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- anyio, mega+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
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
- xarray, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- xarray, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- litestar, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- litestar, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- litestar, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- celery, mega+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, mega+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its seconds
  measure less of the checker
- optuna, mega+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, mega+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- dask, mega+dev, infer-basedpyright: held 9.86 GB beside other steps
- dask, mega+dev, infer-pyrefly: held 8.01 GB beside other steps
- dask, mega+dev, infer-union: held 9.09 GB beside other steps
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
