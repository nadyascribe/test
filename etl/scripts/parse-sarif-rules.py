import json
from pathlib import Path
from argparse import ArgumentParser

slsa_level = {
    "SourceVersionControlled": 2,
    "SourceHistoryVerified": 3,
    "SourceRetainedIndefinitely": 4,
    "BuildScripted": 1,
    "BuildService": 2,
    "BuildAsCode": 3,
    "BuildEphemeralEnvironment": 3,
    "BuildIsolated": 3,
    "ProvenanceAvailable": 1,
    "ProvenanceAuthenticated": 2,
    "ProvenanceServiceGenerated": 2,
    "ProvenanceNonFalsifiable": 3,
}


def load_sarif(filename, sariftype):
    d = json.loads(Path(filename).read_text())

    rules = []
    for r in d["runs"][0]["tool"]["driver"]["rules"]:
        rule = {
            "type": sariftype,
            "ruleName": r["name"],
            "ruleId": r["id"],
            "description": r["shortDescription"]["text"],
        }

        if sariftype == "SLSA":
            rule["slsaLevel"] = slsa_level[r["name"]]

        if "pass" in r["messageStrings"]:
            rule["messagePass"] = r["messageStrings"]["pass"]["text"]

        if "fail" in r["messageStrings"]:
            rule["messageFail"] = r["messageStrings"]["fail"]["text"]

        if "review" in r["messageStrings"]:
            rule["messageReview"] = r["messageStrings"]["review"]["text"]

        rules.append(rule)

    return rules


def gen_sql(rules):
    sql = []
    for rule in rules:
        keys = json.dumps(list(rule.keys()))[1:-1]
        values = repr(list(rule.values()))[1:-1]
        s = f'INSERT INTO "ComplianceRule" ({keys}) VALUES ({values});'
        sql.append(s)

    return sql


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("sariftype", choices=["slsa", "ssdf"])
    parser.add_argument("filename")
    args = parser.parse_args()
    sariftype = args.sariftype.upper()
    filename = args.filename

    rules = load_sarif(filename, sariftype)
    sql = gen_sql(rules)

    for l in sql:
        print(l)
