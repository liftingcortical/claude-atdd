#!/usr/bin/env python3
"""Parse all .feature files and generate an Excel workbook for manual tester review."""

import os
import re
import glob
from datetime import date
import xlsxwriter


SPECS_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_DIR = os.path.join(SPECS_DIR, "features")
OUTPUT_FILE = os.path.join(SPECS_DIR, f"bdd-scenarios-{date.today()}.xlsx")


def parse_feature_file(filepath):
    """Extract feature name, scenarios with tags, steps, and rules from a .feature file."""
    with open(filepath) as f:
        lines = f.readlines()

    feature_area = os.path.basename(os.path.dirname(filepath))
    feature_name = ""
    scenarios = []
    current_tags = []
    current_scenario = None
    current_scenario_id = ""
    current_rule = ""
    tag_rationale = []
    in_rationale = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Feature:"):
            feature_name = stripped.replace("Feature:", "").strip()
        elif stripped.startswith("Rule:"):
            current_rule = stripped.replace("Rule:", "").strip()
        elif stripped.startswith("@"):
            current_tags = stripped.split()
            # Extract scenario ID tag (@F-NNN-S-NN)
            scenario_id_match = [t for t in current_tags if re.match(r"^@F-\d+-S-\d+$", t)]
            current_scenario_id = scenario_id_match[0].lstrip("@") if scenario_id_match else ""
        elif stripped.startswith("Scenario:") or stripped.startswith("Scenario Outline:"):
            if current_scenario:
                current_scenario["tag_rationale"] = " ".join(tag_rationale).strip()
                scenarios.append(current_scenario)
            title = re.sub(r"^Scenario( Outline)?:\s*", "", stripped)
            current_scenario = {
                "scenario_id": current_scenario_id,
                "feature_area": feature_area,
                "feature_name": feature_name,
                "rule": current_rule,
                "title": title,
                "tags": current_tags,
                "steps": [],
                "tag_rationale": "",
            }
            current_tags = []
            tag_rationale = []
            in_rationale = False
        elif stripped.startswith("# TAG RATIONALE:"):
            in_rationale = True
            tag_rationale.append(stripped.replace("# TAG RATIONALE:", "").strip())
        elif in_rationale and stripped.startswith("#"):
            tag_rationale.append(stripped.lstrip("#").strip())
        elif in_rationale and not stripped.startswith("#"):
            in_rationale = False
        elif current_scenario and re.match(r"^(Given|When|Then|And|But)\s", stripped):
            current_scenario["steps"].append(stripped)

    if current_scenario:
        current_scenario["tag_rationale"] = " ".join(tag_rationale).strip()
        scenarios.append(current_scenario)

    return scenarios


def extract_tag(tags, prefix_list):
    """Find the first tag matching any of the prefixes."""
    for tag in tags:
        clean = tag.lstrip("@")
        if clean in prefix_list:
            return clean
    return ""


def extract_personas(tags):
    """Extract all persona names from @persona:<name> tags, joined by comma."""
    personas = []
    for tag in tags:
        clean = tag.lstrip("@")
        if clean.startswith("persona:"):
            personas.append(clean.removeprefix("persona:"))
    return ", ".join(personas)


def build_workbook(all_scenarios):
    """Build the Excel workbook with xlsxwriter."""
    wb = xlsxwriter.Workbook(OUTPUT_FILE)

    # --- Formats ---
    header_fmt = wb.add_format({
        "bold": True, "font_color": "#FFFFFF", "bg_color": "#2F5496",
        "align": "center", "valign": "vcenter", "font_size": 11,
        "border": 1,
    })
    wrap_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    smoke_fmt = wb.add_format({"text_wrap": True, "valign": "top", "bg_color": "#FFF2CC"})
    critical_fmt = wb.add_format({"text_wrap": True, "valign": "top", "bold": True, "font_color": "#C00000"})
    critical_smoke_fmt = wb.add_format({"text_wrap": True, "valign": "top", "bold": True, "font_color": "#C00000", "bg_color": "#FFF2CC"})
    high_fmt = wb.add_format({"text_wrap": True, "valign": "top", "font_color": "#BF6000"})
    high_smoke_fmt = wb.add_format({"text_wrap": True, "valign": "top", "font_color": "#BF6000", "bg_color": "#FFF2CC"})
    low_fmt = wb.add_format({"text_wrap": True, "valign": "top", "font_color": "#808080"})
    low_smoke_fmt = wb.add_format({"text_wrap": True, "valign": "top", "font_color": "#808080", "bg_color": "#FFF2CC"})
    bold_fmt = wb.add_format({"bold": True})
    title_fmt = wb.add_format({"bold": True, "font_size": 14})
    section_fmt = wb.add_format({"bold": True, "font_size": 11})
    summary_header_fmt = wb.add_format({
        "bold": True, "font_color": "#FFFFFF", "bg_color": "#2F5496",
        "align": "center", "border": 1,
    })
    summary_critical_fmt = wb.add_format({"bold": True, "font_color": "#C00000"})
    summary_high_fmt = wb.add_format({"font_color": "#BF6000"})
    summary_low_fmt = wb.add_format({"font_color": "#808080"})

    # --- Sheet 1: All Scenarios ---
    ws = wb.add_worksheet("All Scenarios")

    headers = [
        "ID", "Persona", "Feature Area", "Feature", "Rule", "Scenario",
        "Timing", "Depth", "Criticality",
        "Steps", "Tag Rationale",
        "Tester Status", "Tester Comments",
    ]
    col_widths = [14, 20, 18, 28, 22, 45, 12, 14, 12, 55, 40, 16, 30]

    for col, (header, width) in enumerate(zip(headers, col_widths)):
        ws.write(0, col, header, header_fmt)
        ws.set_column(col, col, width)

    ws.autofilter(0, 0, len(all_scenarios), len(headers) - 1)
    ws.freeze_panes(1, 0)

    # Data validation for Tester Status (column index 11)
    status_col = headers.index("Tester Status")
    statuses = ["APPROVED", "NEEDS EDIT", "MISSING CASE", "DUPLICATE", "QUESTION"]
    ws.data_validation(1, status_col, len(all_scenarios), status_col, {
        "validate": "list",
        "source": statuses,
        "input_title": "Tester Status",
        "input_message": "Select a review status",
        "error_title": "Invalid Status",
        "error_message": "Pick from: " + ", ".join(statuses),
    })

    for row_idx, s in enumerate(all_scenarios, 1):
        persona = extract_personas(s["tags"])
        timing = extract_tag(s["tags"], ["smoke", "regression", "nightly"])
        depth = extract_tag(s["tags"], ["e2e", "integration", "component"])
        criticality = extract_tag(s["tags"], ["critical", "high", "low"])
        steps_text = "\n".join(s["steps"])
        is_smoke = timing == "smoke"

        row_fmt = smoke_fmt if is_smoke else wrap_fmt

        ws.write(row_idx, 0, s["scenario_id"], row_fmt)
        ws.write(row_idx, 1, persona, row_fmt)
        ws.write(row_idx, 2, s["feature_area"], row_fmt)
        ws.write(row_idx, 3, s["feature_name"], row_fmt)
        ws.write(row_idx, 4, s["rule"], row_fmt)
        ws.write(row_idx, 5, s["title"], row_fmt)
        ws.write(row_idx, 6, timing, row_fmt)
        ws.write(row_idx, 7, depth, row_fmt)

        # Criticality cell with color
        if criticality == "critical":
            crit_fmt = critical_smoke_fmt if is_smoke else critical_fmt
        elif criticality == "high":
            crit_fmt = high_smoke_fmt if is_smoke else high_fmt
        elif criticality == "low":
            crit_fmt = low_smoke_fmt if is_smoke else low_fmt
        else:
            crit_fmt = row_fmt
        ws.write(row_idx, 8, criticality, crit_fmt)

        ws.write(row_idx, 9, steps_text, row_fmt)
        ws.write(row_idx, 10, s["tag_rationale"], row_fmt)
        ws.write(row_idx, 11, "", row_fmt)
        ws.write(row_idx, 12, "", row_fmt)

    # --- Sheet 2: Summary ---
    ws2 = wb.add_worksheet("Summary")
    summary_headers = ["Feature Area", "Total", "Smoke", "Regression", "Critical", "High", "Low"]
    for col, header in enumerate(summary_headers):
        ws2.write(0, col, header, summary_header_fmt)
        ws2.set_column(col, col, 16)

    area_stats = {}
    for s in all_scenarios:
        area = s["feature_area"]
        if area not in area_stats:
            area_stats[area] = {"total": 0, "smoke": 0, "regression": 0, "critical": 0, "high": 0, "low": 0}
        area_stats[area]["total"] += 1
        timing = extract_tag(s["tags"], ["smoke", "regression", "nightly"])
        criticality = extract_tag(s["tags"], ["critical", "high", "low"])
        if timing in area_stats[area]:
            area_stats[area][timing] += 1
        if criticality in area_stats[area]:
            area_stats[area][criticality] += 1

    row2 = 1
    for area in sorted(area_stats.keys()):
        stats = area_stats[area]
        ws2.write(row2, 0, area)
        ws2.write(row2, 1, stats["total"])
        ws2.write(row2, 2, stats["smoke"])
        ws2.write(row2, 3, stats["regression"])
        ws2.write(row2, 4, stats["critical"], summary_critical_fmt)
        ws2.write(row2, 5, stats["high"], summary_high_fmt)
        ws2.write(row2, 6, stats["low"], summary_low_fmt)
        row2 += 1

    totals = {k: sum(a[k] for a in area_stats.values()) for k in ["total", "smoke", "regression", "critical", "high", "low"]}
    ws2.write(row2, 0, "TOTAL", bold_fmt)
    for col, key in enumerate(["total", "smoke", "regression", "critical", "high", "low"], 1):
        ws2.write(row2, col, totals[key], bold_fmt)

    # --- Sheet 3: Instructions ---
    ws3 = wb.add_worksheet("Instructions")
    ws3.set_column(0, 0, 80)

    instructions = [
        ("BDD Scenario Review — Instructions for Testers", title_fmt),
        ("", None),
        ("PURPOSE:", section_fmt),
        ("Review each scenario for completeness, accuracy, and missing edge cases.", None),
        ("These scenarios describe WHAT the system should do, not HOW it does it.", None),
        ("", None),
        ("HOW TO REVIEW:", section_fmt),
        ('1. Go to the "All Scenarios" sheet', None),
        ("2. For each scenario, read the Steps column", None),
        ('3. Set the "Tester Status" column (dropdown) to one of:', None),
        ("   - APPROVED — Scenario is correct and complete", None),
        ("   - NEEDS EDIT — Scenario needs modification (explain in Comments)", None),
        ("   - MISSING CASE — A related scenario is missing (describe in Comments)", None),
        ("   - DUPLICATE — This overlaps with another scenario (reference it in Comments)", None),
        ("   - QUESTION — Need clarification before approving", None),
        ("", None),
        ("COLUMN GUIDE:", section_fmt),
        ("- ID: Unique scenario identifier (F-NNN-S-NN)", None),
        ("- Persona: The user role performing the action (from @persona: tags)", None),
        ("- Feature Area: The feature domain (authentication, parent-portal, etc.)", None),
        ("- Feature: The feature name from the .feature file", None),
        ("- Rule: The business rule grouping within the feature", None),
        ("- Scenario: The scenario title (describes a business outcome)", None),
        ("- Timing: smoke (every deploy) / regression (nightly) / nightly (scheduled)", None),
        ("- Depth: e2e (full stack) / integration (API contract) / component (isolated)", None),
        ("- Criticality: critical (blocks deploy) / high (blocks release) / low (tracked)", None),
        ("- Steps: The Given/When/Then steps describing the behavior", None),
        ("- Tag Rationale: Why these tags were chosen", None),
        ("", None),
        ("YELLOW ROWS = @smoke scenarios (run on every deploy, highest priority)", None),
        ("RED TEXT in Criticality = @critical (deploy blocker if failing)", None),
        ("", None),
        ("TIP: Use the Persona column filter to review all scenarios for a specific user role.", None),
        ("", None),
        ("QUESTIONS? Add them in the Comments column.", None),
    ]

    for row_idx, (text, fmt) in enumerate(instructions):
        if fmt:
            ws3.write(row_idx, 0, text, fmt)
        else:
            ws3.write(row_idx, 0, text)

    wb.close()
    return OUTPUT_FILE, len(all_scenarios)


def main():
    feature_files = sorted(glob.glob(os.path.join(FEATURES_DIR, "**", "*.feature"), recursive=True))
    all_scenarios = []
    for fpath in feature_files:
        all_scenarios.extend(parse_feature_file(fpath))

    output, count = build_workbook(all_scenarios)
    print(f"Generated: {output}")
    print(f"Scenarios: {count}")
    print(f"Feature files parsed: {len(feature_files)}")


if __name__ == "__main__":
    main()
