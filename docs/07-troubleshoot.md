[← Guide index](../README.md)

# 7. Troubleshoot

| Symptom | Fix |
|---------|-----|
| `command data-code-extension not found` | `sf plugins install @salesforce/plugin-data-code-extension`, then `sf plugins update` |
| `column does not exist` | Make the column name **lowercase** in the script (`email__c`, not `Email__c`). Check the API name on the DLO's **Fields** tab |
| `DLO not found` / permission denied on write | The target DLO doesn't exist yet or isn't **Active**, or `config.json` doesn't list it. Run `script scan` again, or add it by hand |
| Write fails on schema | The DataFrame has a column the target DLO doesn't, or the types don't match (for example, a timestamp written to a Text field). Compare `transform()`'s `select` with [section 3](03-create-target-dlo.md) |
| Python version mismatch | Activate the 3.11 venv. On macOS, `PYSPARK_PYTHON=$(which python)` fixes local Spark worker mismatches |
| `JAVA_HOME is not set` / Spark won't start | Install Java 17 and run `export JAVA_HOME=$(/usr/libexec/java_home -v 17)` |
| `Cannot connect to the Docker daemon` | Start Docker Desktop, or deploy through the UI ([section 5, option B](05-deploy-and-run.md#step-51-deploy-1020-min-mostly-waiting)) |
| No *Create From Code Extension* option | Code Extension isn't enabled ([section 1](01-enable-and-toolchain.md)), or the user lacks CRUD on *Data Custom Code Procedure Definitions* |
| Local run processed only 1,000 rows | That's the default local row limit. Raise it with `config.reader_config.options["default_row_limit"]`, and **remove it before deploying** |
| `InvalidDatasetForMergeUpsertDelete` | `MERGE_UPSERT_DELETE` needs `_merge_record_type` set to UPSERT or DELETE on every row |
| Run red with no clear reason | Query `DataCustomCodeLogs__dll` for the execution. For multi-line stack traces, use `sf data query … --result-format csv` |
| Statuses don't match section 6 | Check `rule_version__c`: is the transform still pointing at the old package version? Edit the transform and reselect the extension |
| File re-upload fails | Updating a File Upload stream needs **exactly** the same columns, and the last run can't still be Pending / Extracting / In Progress |
| A UDF or `sparkContext` call works locally but fails deployed | Not supported in the Data 360 runtime. Rewrite it with `pyspark.sql.functions` |

## Where to look next

- **Run History:** Data Cloud Setup → Code Extension → ABT_Contact_DQ → **Run History** (status, rows read and written, runtime)
- **Logs:** `DataCustomCodeLogs__dll` (query 9 in [`verification_queries.sql`](../mock_seed/verification_queries.sql))
- **Docs:** [Data 360 Code Extension Guide](https://developer.salesforce.com/docs/data/data-cloud-code-ext/guide/use-custom-script.html) · [CLI reference](https://developer.salesforce.com/docs/data/data-cloud-code-ext-cli-reference/guide/data-code-extension-commands.html)

---

[← 6. Verify and iterate](06-verify-and-iterate.md) · [Guide index](../README.md) · **Next: [8. Golden rules →](08-golden-rules.md)**
