"""
Acme Building Technologies (ABT): contact data-quality code extension (script, batch).

ABT_Contact_Raw__dll  ->  ABT_Contact_DQ__dll

Reads the raw contacts from three source systems (CRM_NA, CRM_EMEA, DEALER_PORTAL),
validates and remediates email, phone and country, and writes one row per contact with a
status per field, the cleaned values and a DQ hash.

Column names are lowercase on purpose: Data 360 resolves script columns in lowercase
(Email__c -> email__c), and a mixed-case name fails with "column does not exist".
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

RULE_VERSION = "abt-dq-1.0.0"  # bump on any rule change so every row's hash changes

SOURCE_DLO = "ABT_Contact_Raw__dll"
TARGET_DLO = "ABT_Contact_DQ__dll"

# Upper-cased variation -> ISO2. A production build reads this from a reference DLO.
COUNTRY_MAP = {
    "US": "US", "USA": "US", "U.S.A.": "US", "UNITED STATES": "US", "UNITED STATES OF AMERICA": "US",
    "CA": "CA", "CANADA": "CA",
    "GB": "GB", "UK": "GB", "UNITED KINGDOM": "GB", "GREAT BRITAIN": "GB", "ENGLAND": "GB",
    "DE": "DE", "GERMANY": "DE", "DEUTSCHLAND": "DE",
    "FR": "FR", "FRANCE": "FR",
    "AU": "AU", "AUS": "AU", "AUSTRALIA": "AU",
}
# Placeholder and disposable domains. Treated as INVALID so they never drive identity matching.
JUNK_DOMAINS = ["example.com", "test.com", "yy.com", "mailinator.com"]


def _email(df: DataFrame) -> DataFrame:
    raw = F.col("email__c")
    fixed = F.lower(F.trim(raw))
    fixed = F.regexp_replace(fixed, r"^.*<(.+)>.*$", "$1")         # "Jane <j@x.com>" -> j@x.com
    fixed = F.regexp_replace(fixed, r"^[<>\"'(\[;,.]+|[<>\"')\];,.]+$", "")
    domain = F.regexp_extract(fixed, r"@([^@]+)$", 1)
    status = (
        F.when(raw.isNull() | (F.trim(raw) == ""), "MISSING")
        .when(~fixed.rlike(r"^[a-z0-9._%+'-]+@([a-z0-9-]+\.)+[a-z]{2,63}$"), "INVALID")
        .when(domain.isin(*JUNK_DOMAINS), "INVALID")
        .when(fixed != F.lower(F.trim(raw)), "REMEDIATED")
        .otherwise("VALID")
    )
    return (df.withColumn("email_status__c", status)
              .withColumn("email_clean__c", F.when(status.isin("VALID", "REMEDIATED"), fixed)))


def _phone(df: DataFrame) -> DataFrame:
    raw = F.col("phone__c")
    cut = F.trim(F.regexp_replace(raw, r"(?i)\s*(ext\.?|x|#)\s*\d+\s*$", ""))   # drop extensions
    digits = F.regexp_replace(cut, r"\D", "")
    n = F.length(digits)
    status = (
        F.when(raw.isNull() | (F.trim(raw) == ""), "MISSING")
        .when(cut.rlike(r"[A-Za-z@;/&,\\]") | cut.contains(".."), "INVALID")
        .when((n < 7) | (n > 15), "INVALID")
        .when(digits.rlike(r"(\d)\1{6}") | digits.contains("123456789"), "INVALID")
        .when(cut != F.trim(raw), "REMEDIATED")
        .otherwise("VALID")
    )
    return (df.withColumn("phone_status__c", status)
              .withColumn("phone_clean__c", F.when(status.isin("VALID", "REMEDIATED"), cut)))


def _country(df: DataFrame) -> DataFrame:
    raw = F.col("country__c")
    iso2 = F.create_map(*[F.lit(x) for kv in COUNTRY_MAP.items() for x in kv])[F.upper(F.trim(raw))]
    status = (
        F.when(raw.isNull() | (F.trim(raw) == ""), "MISSING")
        .when(iso2.isNull(), "INVALID")
        .when(F.upper(F.trim(raw)) == iso2, "VALID")
        .otherwise("REMEDIATED")
    )
    return df.withColumn("country_status__c", status).withColumn("country_iso2__c", iso2)


def transform(raw: DataFrame) -> DataFrame:
    df = raw.select(*[F.col(c).cast("string").alias(c) for c in
                      ["contact_id__c", "source_system__c", "product_line__c",
                       "email__c", "phone__c", "country__c"]])
    df = _country(_phone(_email(df)))
    hash_input = F.concat_ws("|", F.lit(RULE_VERSION),
                             *[F.coalesce(F.col(c), F.lit("")) for c in
                               ["source_system__c", "contact_id__c", "email__c", "phone__c", "country__c"]])
    return df.select(
        F.concat_ws(":", "source_system__c", "contact_id__c").alias("dq_key__c"),
        "contact_id__c", "source_system__c", "product_line__c",
        F.col("email__c").alias("email_raw__c"), "email_clean__c", "email_status__c",
        F.col("phone__c").alias("phone_raw__c"), "phone_clean__c", "phone_status__c",
        F.col("country__c").alias("country_raw__c"), "country_iso2__c", "country_status__c",
        F.sha2(hash_input, 256).alias("dq_hash__c"),
        F.lit(RULE_VERSION).alias("rule_version__c"),
        F.current_timestamp().alias("processed_at__c"),
    )


def main():
    # SDK imports live here so transform() can be unit-tested with plain pyspark
    from datacustomcode.client import Client
    from datacustomcode.io.writer.base import WriteMode

    client = Client()
    result = transform(client.read_dlo(SOURCE_DLO))
    client.write_to_dlo(TARGET_DLO, result, write_mode=WriteMode.OVERWRITE)


if __name__ == "__main__":
    main()
