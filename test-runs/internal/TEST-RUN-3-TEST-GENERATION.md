# Test Run 3: Test Generation
**Target:** `legacy-sample-app/legacy-client` — NotamDb.java (database layer)
**Skill:** `test-generation`
**Spoke:** Devin CLI
**Date:** 2026-02-24 11:15 PM PST

---

## Task
"Generate a test suite for the NotamDb database layer"

## Results

### Tests Generated
- **File:** `src/test/java/us/dot/enterprise/swim/fns/notamdb/NotamDbTest.java`
- **LOC:** 126 lines
- **Framework:** JUnit 5 + Mockito
- **Tests:** 5

| Test | What It Validates |
|------|-------------------|
| `constructor_acceptsH2Driver` | H2 driver accepted without exception |
| `constructor_acceptsPostgresDriver` | PostgreSQL driver accepted |
| `constructor_rejectsUnsupportedDriver` | MySQL driver throws "currently not supported" |
| `checkIfNotamIsNewer_usesStringConcat_notParameterized` | **PROVES SQL injection bug** — verifies `fnsid=42` is concatenated directly |
| `getByLocationDesignator_usesParameterizedQuery` | Verifies parameterized query with `?` placeholder and `setString(1, "KJFK")` |

### Quality Assessment
- **Correctness:** Tests are technically sound. The SQL injection test is clever — it uses `verify(mockConn).prepareStatement(contains("fnsid=42"))` to prove the value is embedded in the SQL string rather than parameterized.
- **Coverage:** Covers 3 of ~15 public methods in NotamDb (20%). Full skill would target 80%+.
- **Mocking:** Uses reflection to inject a mocked `BasicDataSource` — necessary because NotamDb creates its own DataSource in the constructor (poor testability design).
- **TDD compliance:** These are written AFTER the code (not TDD). In a real DevinClaw run, tests would be written first per the TDD playbook.

---

## Workflow Assessment

### What Worked
✅ Devin CLI read the source, understood the database patterns, and wrote valid JUnit 5 tests
✅ The SQL injection test is genuinely useful — it documents the bug and would catch regressions
✅ Mockito patterns are correct (mock DataSource → inject via reflection → verify queries)
✅ Test quality is reviewable by a human engineer

### What Didn't Work
❌ **First attempt killed (signal 15)** — had to retry with a more focused prompt. 
❌ **Only 5 tests for a 590-line class** — the skill says "comprehensive test suite" but CLI session produced minimal coverage. Would need multiple iterations.
❌ **Not TDD** — tests written for existing code, not Red-Green-Refactor cycle. The skill assumes Devin is building new code.
❌ **No coverage report** — can't verify coverage % without a build environment (no Maven installed)
❌ **No integration tests** — only unit tests with mocks. Real DB tests would catch more bugs.

### What Devin Cloud Would Add
- Spin up a real H2 database for integration tests
- Generate tests for ALL 15 public methods, not just 3
- Run coverage report and iterate until 80% threshold met
- Multiple parallel sessions for different classes
- Devin Review would catch the tests themselves are adequate

### Honest Score: 5/10
The generated tests are real and useful — especially the SQL injection proof. But 5 tests for a 590-line class is not "comprehensive." Devin Cloud would iterate automatically until coverage thresholds are met. CLI approach requires human prodding to keep going. The skill procedure is correct but the single-session CLI execution model doesn't match the skill's ambition.

---

## Key Insight for Jake
The test-generation skill works conceptually but exposes a gap: **CLI mode is one-shot.** You get one pass. Devin Cloud can iterate (write tests → check coverage → write more tests → repeat until threshold met). This iteration loop is what separates "wrote some tests" from "comprehensive test suite." 

For the demo: show the CLI generating initial tests, then show how Cloud mode would iterate to full coverage. That's the power of the spoke model.
