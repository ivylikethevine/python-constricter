# A coverage run's `report.json`, as the Corpus coverage workflow's comment reads it: each side's
# bindings typed (`[typed, total]`, `null` where a fix crashed) as released, after `--fix` and after
# `--fix --unsafe-fixes`, and the milliseconds a check takes it in one process. `$corpus` names the corpus.
def side: {
  released: .coverage.typed,
  fixed: .["fix-certain"].typed,
  guessed: .["fix-unsafe"].typed
};
def milliseconds: (.timing["median one"] * 1000 | round);
.records[$corpus] as $found
| {
    corpus: $corpus,
    version: .corpora[$corpus].version,
    head: ($found["coverage+dev"] | side),
    base: ($found.base | side),
    timed: {head: ($found["coverage+dev"] | milliseconds), base: ($found.base | milliseconds)}
  }
