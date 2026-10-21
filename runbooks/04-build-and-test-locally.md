[← Guide index](../README.md)

# 4. Build and test locally

This is where a code extension earns its keep. The rules are plain Python, so you can
prove they're right on a laptop **before** spending any credits.

## Step 4.1: Create the package (5 min)

```bash
cd ~/dev                                    # anywhere outside this repo
sf data-code-extension script init --package-dir abt_contact_dq
cd abt_contact_dq
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# replace the generated script with this repo's script
cp <this-repo>/code_extension/payload/entrypoint.py payload/entrypoint.py
```

`init` creates:

| Path | What it is | Edit it? |
|------|------------|----------|
| `payload/entrypoint.py` | The script. **This is what gets deployed** | ✅ |
| `payload/config.json` | Which DLOs the script may read and write. `scan` fills it in | Only if `scan` misses something |
| `requirements.txt` | Packages the deployed script needs | Only to add a library |
| `Dockerfile`, `requirements-dev.txt` | Build plumbing | ❌ Never |
| `examples/`, `.devcontainer/` | Samples | Optional |

## Step 4.2: Read the script with the room (10 min)

Open [`code_extension/payload/entrypoint.py`](../code_extension/payload/entrypoint.py) on screen.

- **`transform(raw)`** is pure PySpark. It:
  1. selects 6 columns;
  2. applies `_email`, `_phone` and `_country`. Each adds a `*_status__c` field (VALID / REMEDIATED / INVALID / MISSING) and a cleaned value;
  3. builds `dq_key__c` and `dq_hash__c`.
- **`main()`** is the **only** part that calls the SDK:

  ```python
  client = Client()
  result = transform(client.read_dlo("ABT_Contact_Raw__dll"))
  client.write_to_dlo("ABT_Contact_DQ__dll", result, write_mode=WriteMode.OVERWRITE)
  ```

- **Every column name is lowercase** (`email__c`). Data 360 resolves script columns in lowercase, so a mixed-case name fails with `column does not exist`.
- **Only Spark built-ins** (`pyspark.sql.functions`). Custom UDFs, RDDs, SparkContext patterns and Spark listeners aren't supported in the Data 360 runtime.

The rules table is in [`code_extension/README.md`](../code_extension/README.md#rules-version-abt-dq-100). This is the moment for the **rules owner** to sign off on each rule.

## Step 4.3: Unit tests (no org, no credits)

```bash
cd <this-repo>
pip install -r code_extension/requirements-test.txt
JAVA_HOME=$(/usr/libexec/java_home -v 17) python -m pytest code_extension/tests -q
# 24 passed
```

The 24 tests cover:
- **20 spot-check rows**, each with an exact expected (email, phone, country) status;
- the **remediated values** (for example `Raj Patel <raj.patel@…>` becomes `raj.patel@…`, and `02 9374 4000 x 15` becomes `02 9374 4000`);
- **one row per contact**, and **no null hashes**;
- **identity uplift:** the cleaned emails resolve 30,000 rows to exactly **18,000 people**;
- **placeholder emails** (`noemail@example.com`) are never a match key.

> 🔤 On macOS, if Spark complains about mismatched Python versions, set `PYSPARK_PYTHON=$(which python)`.

## Step 4.4: Scan (writes permissions into `config.json`)

```bash
cd ~/dev/abt_contact_dq
sf data-code-extension script scan --entrypoint ./payload/entrypoint.py
cat payload/config.json        # read: ABT_Contact_Raw__dll   write: ABT_Contact_DQ__dll
```

Run the scan again after **every** code change. It finds object names written as string literals. If it misses one (here they're module constants), add it to `config.json` by hand.

## Step 4.5: Run locally against the org (uses Data Queries credits)

```bash
sf data-code-extension script run --entrypoint ./payload/entrypoint.py --target-org abt-demo
```

- Reads come from the org through the Query API. This proves your object names, column names and types against the **real** DLO.
- **Expected:** no `column does not exist` errors and no permission errors, with 1,000 rows processed.
- **The row limit:** local runs read only **1,000 of the 30,000 rows** by default, and that's fine. A local run proves names, types and permissions; the unit tests (4.3) already proved the rules on all 30,000. Don't raise the limit to read everything: every local read uses Data Queries credits. If you do raise it (`config.reader_config.options["default_row_limit"]`, from `datacustomcode.config import config`), **remove it before you deploy**, or the limit ships with the package.

## ✅ Exit check for section 4

- [ ] `pytest`: **24 passed**
- [ ] `config.json` lists `ABT_Contact_Raw__dll` (read) and `ABT_Contact_DQ__dll` (write)
- [ ] `script run` completes without errors
- [ ] The rules owner has agreed the rules (or written down what to change in [section 6](06-verify-and-iterate.md#step-65-change-a-rule-and-redeploy))

---

[← 3. Create the target DLO](03-create-target-dlo.md) · [Guide index](../README.md) · **Next: [5. Deploy and run →](05-deploy-and-run.md)**
