"""Unit tests for the ABT contact DQ rules. Plain pyspark, no org, no SDK.

    JAVA_HOME=$(/usr/libexec/java_home -v 17) python -m pytest code_extension/tests -q
"""

import csv
import sys
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code_extension" / "payload"))
from entrypoint import transform  # noqa: E402

SEED_CSV = REPO / "data" / "abt_contacts_raw.csv"

# Spot-check rows -> (email_status, phone_status, country_status)
EXPECTED = {
    "NA-100001": ("VALID", "VALID", "REMEDIATED"),
    "NA-100002": ("VALID", "REMEDIATED", "REMEDIATED"),    # case and spaces only: still VALID
    "NA-100003": ("REMEDIATED", "REMEDIATED", "VALID"),    # "us" is ISO2 once upper-cased
    "NA-100004": ("INVALID", "INVALID", "VALID"),
    "NA-100005": ("INVALID", "INVALID", "INVALID"),
    "NA-100006": ("MISSING", "INVALID", "MISSING"),
    "NA-100007": ("REMEDIATED", "VALID", "VALID"),
    "NA-100008": ("INVALID", "VALID", "VALID"),
    "EM-200001": ("VALID", "VALID", "REMEDIATED"),
    "EM-200002": ("VALID", "INVALID", "REMEDIATED"),
    "EM-200003": ("VALID", "VALID", "REMEDIATED"),
    "EM-200004": ("INVALID", "INVALID", "REMEDIATED"),
    "EM-200005": ("REMEDIATED", "VALID", "REMEDIATED"),
    "EM-200006": ("REMEDIATED", "REMEDIATED", "VALID"),
    "DP-300001": ("VALID", "REMEDIATED", "VALID"),
    "DP-300002": ("VALID", "VALID", "REMEDIATED"),
    "DP-300003": ("INVALID", "VALID", "REMEDIATED"),
    "DP-300004": ("VALID", "INVALID", "REMEDIATED"),
    "DP-300005": ("VALID", "MISSING", "REMEDIATED"),
    "DP-300006": ("VALID", "VALID", "INVALID"),
}


@pytest.fixture(scope="module")
def result():
    spark = SparkSession.builder.master("local[1]").appName("abt-dq-test").getOrCreate()
    with open(SEED_CSV, newline="") as f:
        # Mimic the DLO: header "email" becomes field email__c; blanks arrive as null
        rows = [{f"{k}__c": (v if v != "" else None) for k, v in r.items()} for r in csv.DictReader(f)]
    out = {r["contact_id__c"]: r for r in transform(spark.createDataFrame(rows)).collect()}
    yield out
    spark.stop()


@pytest.mark.parametrize("cid", sorted(EXPECTED))
def test_spot_check_statuses(result, cid):
    r = result[cid]
    assert (r["email_status__c"], r["phone_status__c"], r["country_status__c"]) == EXPECTED[cid]


def test_remediated_values(result):
    assert result["NA-100002"]["email_clean__c"] == "dana.lopez@granite-demo.com"
    assert result["NA-100003"]["email_clean__c"] == "raj.patel@ironbridge-demo.com"
    assert result["NA-100003"]["phone_clean__c"] == "800-555-1234"
    assert result["DP-300001"]["phone_clean__c"] == "02 9374 4000"
    assert result["EM-200001"]["country_iso2__c"] == "DE"
    assert result["NA-100005"]["email_clean__c"] is None


def test_one_row_per_contact_and_hash_never_null(result):
    assert len(result) == 30_000
    assert len({r["dq_key__c"] for r in result.values()}) == 30_000
    assert all(r["dq_hash__c"] for r in result.values())
    assert result["NA-100001"]["dq_key__c"] == "CRM_NA:NA-100001"


def test_clean_email_resolves_30k_rows_to_18k_people(result):
    rows = list(result.values())
    clean = {r["email_clean__c"] for r in rows if r["email_clean__c"]}
    unmatched = sum(1 for r in rows if not r["email_clean__c"])
    assert len(clean) + unmatched == 18_000


def test_placeholder_email_is_never_a_match_key(result):
    shared = [r for r in result.values()
              if r["email_raw__c"] and r["email_raw__c"].strip().lower() == "noemail@example.com"]
    assert len(shared) > 1
    assert all(r["email_clean__c"] is None for r in shared)
