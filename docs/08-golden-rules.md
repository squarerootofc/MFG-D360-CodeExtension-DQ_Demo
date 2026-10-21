[← Guide index](../README.md)

# 8. Golden rules

Keep these on screen.

1. **Lowercase every column name in the script.** `email__c`, not `Email__c`. Object API names stay exactly as shown (`ABT_Contact_Raw__dll`).
2. **Read and write the same object type.** Go DLO → DLO, or DMO → DMO, and DMO writes go only to a *transform-type* DMO. Don't mix types in one script.
3. **Create the target DLO first,** with fields that match the DataFrame you write.
4. **Rules go in plain functions; the SDK goes in `main()`.** That's what makes the rules unit-testable with no org and no credits.
5. **Test before you spend.** Order: `pytest` → `scan` → `run` → `deploy`. Never deploy code that hasn't passed its tests.
6. **Bump `RULE_VERSION` on every rule change.** The hash then changes on every row, which proves the new rules reached them all.
7. **Never null the hash.** Replace blanks with `''` before hashing, so a missing field can't silently drop a row from change detection.
8. **Never print PII.** `DataCustomCodeLogs__dll` has no governance policies. Log counts and step names only.
9. **Size it on purpose.** Pass `--cpu-size CPU_L` unless you've measured a need for more. The default is 2XL, at 4× the CU rate.
10. **Built-ins only.** Use `pyspark.sql.functions`. No UDFs, RDDs, SparkContext patterns or listeners.
11. **A deployed extension runs only through a batch data transform.** Run it manually until it's verified, then schedule it, and only with a credit owner.
12. **Promote with a data kit.** Don't rebuild by hand in the next org ([use case 7](09-use-cases-to-configure.md#use-case-7--promote-to-the-next-org-with-a-data-kit)).

---

[← 7. Troubleshoot](07-troubleshoot.md) · [Guide index](../README.md) · **Next: [9. Use cases to configure →](09-use-cases-to-configure.md)**
