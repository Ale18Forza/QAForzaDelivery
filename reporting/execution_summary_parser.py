from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def parse_junit_summary(junit_xml: Path) -> dict:
    if not junit_xml.exists():
        return {
            "total": 0,
            "passed": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0.0,
            "test_cases": [],
        }

    tree = ET.parse(junit_xml)
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")

    total = failures = errors = skipped = 0
    duration = 0.0
    cases = []

    for suite in suites:
        total += int(suite.attrib.get("tests", "0"))
        failures += int(suite.attrib.get("failures", "0"))
        errors += int(suite.attrib.get("errors", "0"))
        skipped += int(suite.attrib.get("skipped", "0"))
        duration += float(suite.attrib.get("time", "0"))
        for case in suite.findall("testcase"):
            status = "PASSED"
            message = ""
            if case.find("failure") is not None:
                status = "FAILED"
                message = case.find("failure").attrib.get("message", "")
            elif case.find("error") is not None:
                status = "ERROR"
                message = case.find("error").attrib.get("message", "")
            elif case.find("skipped") is not None:
                status = "SKIPPED"
                message = case.find("skipped").attrib.get("message", "")
            cases.append(
                {
                    "name": case.attrib.get("name", ""),
                    "classname": case.attrib.get("classname", ""),
                    "time": float(case.attrib.get("time", "0")),
                    "status": status,
                    "message": message,
                }
            )

    return {
        "total": total,
        "passed": max(total - failures - errors - skipped, 0),
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "duration": round(duration, 2),
        "test_cases": cases,
    }
