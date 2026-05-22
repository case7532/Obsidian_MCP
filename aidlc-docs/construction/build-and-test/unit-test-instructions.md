# Unit Test Instructions

> Hướng dẫn chạy unit tests với pytest và Hypothesis PBT.

## Contents
- [Run all unit tests](#run-all-unit-tests)
- [Run with coverage](#run-with-coverage)
- [Run PBT tests with more examples (CI)](#run-pbt-tests-with-more-examples-ci)
- [Test breakdown](#test-breakdown)
- [Fix failing tests](#fix-failing-tests)

## Run all unit tests
```bash
uv run pytest tests/unit/ -v
```

**Expected**: 79 passed, 0 failed

## Run with coverage
```bash
uv run pytest tests/unit/ --cov=obsidian_mcp --cov-report=term-missing
```

## Run PBT tests with more examples (CI)
```bash
uv run pytest tests/unit/ -v --hypothesis-seed=0
```

`--hypothesis-seed=0` ensures reproducible PBT runs in CI (per PBT-08).

## Test breakdown

| File | Tests | PBT Properties |
|---|---|---|
| `test_path_utils.py` | 14 + 3 PBT | round-trip, idempotence, invariant |
| `test_vault_config.py` | 9 | — |
| `test_note_reader.py` | 21 + 2 PBT | frontmatter round-trip, filter invariant |
| `test_note_writer.py` | 18 | — |
| `test_advanced_features.py` | 11 + 1 PBT | dataview round-trip |
| **Total** | **79** | **6 PBT properties** |

## Fix failing tests
1. Run with `--tb=long` for full tracebacks
2. For PBT failures: seed is logged — replay with `--hypothesis-seed=<seed>`
3. Hypothesis will shrink failing input to minimal reproducing case

## Related
- [[build-instructions]]
- [[integration-test-instructions]]
- [[build-and-test-summary]]
