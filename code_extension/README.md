[← Guide index](../README.md)

# Code extension: `ABT_Contact_DQ`

| Path | What it is |
|------|------------|
| [`payload/entrypoint.py`](payload/entrypoint.py) | The script you deploy. `transform()` holds every rule as plain PySpark, and `main()` is the only part that calls the SDK. |
| [`tests/test_entrypoint.py`](tests/test_entrypoint.py) | 24 unit tests against `mock_seed/abt_contacts_raw.csv` (generate it first with [`generate_seed.py`](../mock_seed/generate_seed.py)). They need no org and use no credits. |
| [`requirements-test.txt`](requirements-test.txt) | What the tests need locally: `pyspark` and `pytest`. |

This folder holds **only the script and its tests**. `sf data-code-extension script init`
generates the rest of the package (`config.json`, `requirements.txt`, `Dockerfile`).
[Section 4](../docs/04-build-and-test-locally.md) shows how to copy this script into it.

```bash
# from the repo root, with Python 3.11 and Java 17
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r code_extension/requirements-test.txt
python3 mock_seed/generate_seed.py      # the tests read the generated CSV
JAVA_HOME=$(/usr/libexec/java_home -v 17) python -m pytest code_extension/tests -q   # 24 passed
```

## Rules (version `abt-dq-1.0.0`)

| Field | MISSING | INVALID | REMEDIATED | VALID |
|-------|---------|---------|------------|-------|
| Email | blank | fails the address pattern, or the domain is a placeholder or disposable one (`example.com`, `test.com`, `yy.com`, `mailinator.com`) | `Name <a@b.com>` unwrapped, or stray `<>'";,.` stripped | only case or whitespace differs |
| Phone | blank | letters or `@;/&,\`, `..`, fewer than 7 or more than 15 digits, 7 repeated digits, or contains `123456789` | extension (`ext`, `x`, `#`) cut | unchanged |
| Country | blank | not in `COUNTRY_MAP` | alias mapped to ISO2 (`Deutschland` → `DE`) | already an ISO2 code (any case) |

`dq_hash__c` = SHA-256 of `rule_version | source_system | contact_id | email | phone | country`.
Blank values are replaced with `''` before hashing, so the hash is never null. Bump
`RULE_VERSION` whenever you change a rule: every hash then changes, which proves the new
rules reached every row.
