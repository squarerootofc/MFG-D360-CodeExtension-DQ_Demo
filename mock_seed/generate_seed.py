"""
Mock seed generator: Acme Building Technologies (ABT) contact data.

ABT is a fictional manufacturer of fire, HVAC and security equipment for buildings.
This writes abt_contacts_raw.csv: 30,000 contact rows from three source systems, with
deliberately dirty email, phone and country values and built-in duplicate identities.

    python3 mock_seed/generate_seed.py          # stdlib only, deterministic, ~1 second

Shape (fixed seed, so every run produces the same file):
  - 18,000 people. 20 are hand-written spot-check rows (see SPOT_CHECKS), 17,980 are generated.
  - 12,000 of the generated people appear a second time from another source system, with
    the same email written differently (case, spaces, "Name <email>", stray punctuation).
  - 2,100 people have an invalid or missing email and are never duplicated, so matching on
    the cleaned email resolves 30,000 rows to exactly 18,000 people (40% consolidation).

Change the scale with GENERATED_PEOPLE, BAD_EMAILS and DUPLICATES. Keep
GENERATED_PEOPLE - BAD_EMAILS >= DUPLICATES.
"""

import csv
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "abt_contacts_raw.csv"
SEED = 20261019
GENERATED_PEOPLE = 17_980   # + 20 spot checks = 18,000 people
BAD_EMAILS = 2_094          # + 6 bad emails in the spot checks = 2,100 people
DUPLICATES = 12_000         # 18,000 people + 12,000 duplicates = 30,000 rows
HEADER = ["contact_id", "source_system", "account_name", "first_name", "last_name",
          "job_title", "product_line", "email", "phone", "country"]

SOURCES = {"CRM_NA": "NA", "CRM_EMEA": "EM", "DEALER_PORTAL": "DP"}

# account name, email domain, countries the account's contacts sit in
ACCOUNTS = {
    "CRM_NA": [
        ("Harborview Medical Center", "harborview-demo.com", ["US"]),
        ("Granite Plaza Office Tower", "granite-demo.com", ["US"]),
        ("Ironbridge Logistics Park", "ironbridge-demo.com", ["US"]),
        ("Riverside Unified School District", "riverside-demo.org", ["US"]),
        ("Maplegate Property Group", "maplegate-demo.ca", ["CA"]),
        ("Northshore Data Centers", "northshore-demo.com", ["US", "CA"]),
    ],
    "CRM_EMEA": [
        ("Thameside Retail Estates", "thameside-demo.co.uk", ["GB"]),
        ("Rheinwerk Industriebau", "rheinwerk-demo.de", ["DE"]),
        ("Lumiere Hospitality Group", "lumiere-demo.fr", ["FR"]),
        ("Kingsway Airports", "kingsway-demo.co.uk", ["GB"]),
    ],
    "DEALER_PORTAL": [
        ("Southcross Fire & Safety (dealer)", "southcross-demo.com.au", ["AU"]),
        ("Summit Mechanical Contractors (dealer)", "summitmech-demo.com", ["US"]),
        ("Brightline Security Integrators (dealer)", "brightline-demo.com", ["US", "CA"]),
        ("Pacific Controls Partners (dealer)", "pacificctl-demo.com.au", ["AU"]),
    ],
}

PRODUCT_LINES = {
    "FIRE_DETECTION": ["Fire Protection Engineer", "Life Safety Manager", "Fire Alarm Technician"],
    "FIRE_SUPPRESSION": ["Fire Protection Engineer", "Sprinkler Contractor", "Risk Manager"],
    "HVAC_EQUIPMENT": ["Facility Manager", "Mechanical Engineer", "Chief Engineer"],
    "HVAC_CONTROLS": ["Building Automation Specialist", "Energy Manager", "Facility Manager"],
    "SECURITY_ACCESS": ["Security Director", "Security Integrator", "IT Infrastructure Lead"],
    "SECURITY_VIDEO": ["Security Operations Manager", "Security Integrator", "Loss Prevention Lead"],
}

FIRST = ["Maria", "James", "Aisha", "Daniel", "Sofia", "Kenji", "Olivia", "Mateo", "Hannah",
         "Lucas", "Amara", "Ethan", "Chloe", "Ravi", "Ingrid", "Diego", "Fatima", "Noel",
         "Elena", "Marcus", "Yuki", "Grace", "Tariq", "Nora", "Felix", "Leah", "Owen", "Zara"]
LAST = ["Chen", "Okafor", "Novak", "Brennan", "Ruiz", "Lindqvist", "Patel", "Dubois", "Moreau",
        "Fischer", "Walsh", "Tanaka", "Haddad", "Silva", "Kowalski", "Reyes", "Murphy", "Nguyen",
        "Becker", "Ahmed", "Larsen", "Costa", "Byrne", "Schultz", "Ortiz", "Grant"]

# Ways the same country arrives in the wild. All are in the code extension's COUNTRY_MAP.
COUNTRY_ALIASES = {
    "US": ["United States", "USA", "usa", "U.S.A.", "United States of America"],
    "CA": ["Canada", "CANADA", "ca"],
    "GB": ["United Kingdom", "UK", "Great Britain", "England", "gb"],
    "DE": ["Germany", "Deutschland", "de"],
    "FR": ["France", "FRANCE", "fr"],
    "AU": ["Australia", "AUS", "au"],
}

# Hand-written rows with known outcomes. tests/test_entrypoint.py checks every one.
# (id, source, account, first, last, title, product_line, email, phone, country)
SPOT_CHECKS = [
    ("NA-100001", "CRM_NA", "Harborview Medical Center", "Dana", "Whitfield", "Facility Manager",
     "HVAC_EQUIPMENT", "dana.whitfield@harborview-demo.com", "+1 (312) 555-0100", "USA"),
    ("NA-100002", "CRM_NA", "Granite Plaza Office Tower", "Dana", "Lopez", "Chief Engineer",
     "HVAC_CONTROLS", " Dana.Lopez@Granite-Demo.com ", "312-555-0199 ext 22", "United States"),
    ("NA-100003", "CRM_NA", "Ironbridge Logistics Park", "Raj", "Patel", "Life Safety Manager",
     "FIRE_DETECTION", "Raj Patel <raj.patel@ironbridge-demo.com>", "800-555-1234#9", "us"),
    ("NA-100004", "CRM_NA", "Ironbridge Logistics Park", "Tom", "Brown", "Security Director",
     "SECURITY_ACCESS", "tom.brown@ironbridge-demo", "555..1234", "US"),
    ("NA-100005", "CRM_NA", "Riverside Unified School District", "Mia", "Wong", "Risk Manager",
     "FIRE_SUPPRESSION", "noemail@example.com", "000-000-0000", "N/A"),
    ("NA-100006", "CRM_NA", "Riverside Unified School District", "Leo", "Garcia", "Facility Manager",
     "HVAC_EQUIPMENT", "", "123-456-7890", ""),
    ("NA-100007", "CRM_NA", "Harborview Medical Center", "Priya", "Nair", "Energy Manager",
     "HVAC_CONTROLS", "priya.nair@harborview-demo.com;", "312.555.0123", "us "),
    ("NA-100008", "CRM_NA", "Maplegate Property Group", "Grace", "Kim", "Security Operations Manager",
     "SECURITY_VIDEO", "grace.kim@mailinator.com", "+1 416 555 0188", "CA"),
    ("EM-200001", "CRM_EMEA", "Rheinwerk Industriebau", "Ella", "Schmidt", "Fire Protection Engineer",
     "FIRE_DETECTION", "ella.schmidt@rheinwerk-demo.de", "+49 30 1234567", "Deutschland"),
    ("EM-200002", "CRM_EMEA", "Rheinwerk Industriebau", "Max", "Mueller", "Mechanical Engineer",
     "HVAC_EQUIPMENT", "max.mueller@rheinwerk-demo.de", "030/1234567", "Germany"),
    ("EM-200003", "CRM_EMEA", "Thameside Retail Estates", "Zoe", "Clark", "Loss Prevention Lead",
     "SECURITY_VIDEO", "zoe.clark@thameside-demo.co.uk", "+44 20 7946 0958", "UK"),
    ("EM-200004", "CRM_EMEA", "Kingsway Airports", "Sam", "Green", "Security Director",
     "SECURITY_ACCESS", "sam@yy.com", "9999999", "United Kingdom"),
    ("EM-200005", "CRM_EMEA", "Lumiere Hospitality Group", "Claire", "Martin", "Facility Manager",
     "FIRE_SUPPRESSION", "<claire.martin@lumiere-demo.fr>", "+33 1 42 68 53 00", "France"),
    ("EM-200006", "CRM_EMEA", "Thameside Retail Estates", "Liam", "OConnor", "Building Automation Specialist",
     "HVAC_CONTROLS", "'liam.oconnor@thameside-demo.co.uk'", "+44 161 496 0000 ext. 4", "GB"),
    ("DP-300001", "DEALER_PORTAL", "Southcross Fire & Safety (dealer)", "Ben", "King", "Fire Alarm Technician",
     "FIRE_DETECTION", "ben.king@southcross-demo.com.au", "02 9374 4000 x 15", "AU"),
    ("DP-300002", "DEALER_PORTAL", "Summit Mechanical Contractors (dealer)", "Ava", "Scott", "Mechanical Engineer",
     "HVAC_EQUIPMENT", "ava.scott@summitmech-demo.com", "(415) 555-0142", "U.S.A."),
    ("DP-300003", "DEALER_PORTAL", "Summit Mechanical Contractors (dealer)", "Noah", "Young", "Chief Engineer",
     "HVAC_EQUIPMENT", "noah.young@@summitmech-demo.com", "415 555 0143", "USA"),
    ("DP-300004", "DEALER_PORTAL", "Brightline Security Integrators (dealer)", "Lily", "Adams", "Security Integrator",
     "SECURITY_ACCESS", "lily.adams@brightline-demo.com", "call site office", "USA"),
    ("DP-300005", "DEALER_PORTAL", "Brightline Security Integrators (dealer)", "Jack", "Baker", "Security Integrator",
     "SECURITY_VIDEO", "jack.baker@brightline-demo.com", "", "Canada"),
    ("DP-300006", "DEALER_PORTAL", "Brightline Security Integrators (dealer)", "Omar", "Haddad", "IT Infrastructure Lead",
     "SECURITY_ACCESS", "omar.haddad@brightline-demo.com", "+1 416 555 0175", "Atlantis"),
]


def phone_for(rng, iso2):
    line = f"{rng.randint(100, 199):04d}"
    if iso2 in ("US", "CA"):
        area = rng.choice(["312", "415", "617", "212", "416", "604"])
        return rng.choice([f"({area}) 555-{line}", f"{area}-555-{line}", f"+1 {area} 555 {line}",
                           f"{area}.555.{line}"])
    if iso2 == "GB":
        return rng.choice([f"+44 20 7946 {line}", f"020 7946 {line}"])
    if iso2 == "DE":
        return rng.choice([f"+49 30 901820{line[-2:]}", f"030 901820{line[-2:]}"])
    if iso2 == "FR":
        return f"+33 1 42 68 {line[-2:]} {rng.randint(10, 99)}"
    return rng.choice([f"+61 2 9374 {line}", f"(02) 9374 {line}"])  # AU


def dirty_phone(rng, phone):
    r = rng.random()
    if r < 0.08:
        return phone + rng.choice([" ext 12", " x204", "#3", " ext. 7"])   # REMEDIATED
    if r < 0.11:
        return rng.choice(["see notes", "TBD", "front desk"])               # INVALID: text
    if r < 0.13:
        return "0000000"                                                     # INVALID: repeated
    if r < 0.16:
        return ""                                                            # MISSING
    return phone


def dirty_country(rng, iso2):
    r = rng.random()
    if r < 0.65:
        return iso2
    if r < 0.94:
        return rng.choice(COUNTRY_ALIASES[iso2])                             # REMEDIATED
    if r < 0.97:
        return rng.choice(["Unknown", "N/A", "--"])                          # INVALID
    return ""                                                                # MISSING


def wrap_email(email):
    return f"'{email}'" if len(email) % 2 else f"{email};"


def main():
    rng = random.Random(SEED)
    people = []   # dicts without contact_id; spot checks are added separately

    for i in range(GENERATED_PEOPLE):
        source = rng.choices(list(SOURCES), weights=[50, 30, 20])[0]
        account, domain, countries = rng.choice(ACCOUNTS[source])
        iso2 = rng.choice(countries)
        line = rng.choice(list(PRODUCT_LINES))
        first, last = rng.choice(FIRST), rng.choice(LAST)
        people.append({
            "source_system": source, "account_name": account, "first_name": first, "last_name": last,
            "job_title": rng.choice(PRODUCT_LINES[line]), "product_line": line, "iso2": iso2,
            "email": f"{first}.{last}{100 + i}@{domain}".lower(),   # number keeps it unique per person
        })

    # Some generated people get an email that can't be fixed; they are never duplicated.
    # Split: ~30% shared placeholder, ~20% shared test address, ~25% malformed, rest blank.
    bad = rng.sample(range(GENERATED_PEOPLE), BAD_EMAILS)
    for n, i in enumerate(bad):
        p = people[i]
        local, domain = p["email"].split("@")
        share = n / BAD_EMAILS
        if share < 0.30:
            p["email"] = rng.choice(["noemail@example.com", "NoEmail@example.com", " noemail@example.com"])
        elif share < 0.50:
            p["email"] = rng.choice(["none@test.com", "na@test.com"])
        elif share < 0.75:
            p["email"] = rng.choice([f"{local}.{domain}", f"{local}@@{domain}",
                                     f"{local}@{domain.split('.')[0]}", f"{p['first_name']} {local}@{domain}"])
        else:
            p["email"] = ""
        p["bad_email"] = True

    candidates = [i for i in range(GENERATED_PEOPLE) if not people[i].get("bad_email")]
    dup_of = rng.sample(candidates, DUPLICATES)
    duplicated = set(dup_of)
    # 40% identical, 20% case/spaces, 20% "Name <email>", 20% stray quotes or ";"
    q = DUPLICATES // 5
    kinds = ["exact"] * (DUPLICATES - 3 * q) + ["case"] * q + ["angle"] * q + ["wrap"] * q
    rng.shuffle(kinds)

    rows = []
    for i, p in enumerate(people):
        email = p["email"]
        if i not in duplicated and not p.get("bad_email") and rng.random() < 0.10:
            email = rng.choice([email.upper(), f"{p['first_name']} {p['last_name']} <{email}>", f"{email}."])
        rows.append({**p, "email": email, "phone": dirty_phone(rng, phone_for(rng, p["iso2"])),
                     "country": dirty_country(rng, p["iso2"])})

    for i, kind in zip(dup_of, kinds):
        p = people[i]
        other = rng.choice([s for s in SOURCES if s != p["source_system"]])
        email = p["email"]
        if kind == "case":
            email = f" {email.title()} " if rng.random() < 0.5 else email.upper()
        elif kind == "angle":
            email = f"{p['first_name']} {p['last_name']} <{email}>"
        elif kind == "wrap":
            email = wrap_email(email)
        rows.append({**p, "source_system": other, "email": email,
                     "phone": dirty_phone(rng, phone_for(rng, p["iso2"])),
                     "country": dirty_country(rng, p["iso2"])})

    rng.shuffle(rows)
    counters = {"CRM_NA": 100100, "CRM_EMEA": 200100, "DEALER_PORTAL": 300100}
    out = [dict(zip(HEADER, s)) for s in SPOT_CHECKS]
    for r in rows:
        counters[r["source_system"]] += 1
        r["contact_id"] = f"{SOURCES[r['source_system']]}-{counters[r['source_system']]}"
        out.append({k: r[k] for k in HEADER})

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows to {OUT.name}")


if __name__ == "__main__":
    main()
