"""Read-only workbook structure audit using the standard-library OOXML parser."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json

ROOT = Path(__file__).resolve().parents[1]
namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
with ZipFile(ROOT / "Probability and Statistics Course Outline.xlsx") as archive:
    assert archive.testzip() is None
    shared = ["".join(item.itertext()) for item in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si", namespace)]
    worksheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    cells = {}
    for cell in worksheet.findall("m:sheetData/m:row/m:c", namespace):
        value = cell.find("m:v", namespace)
        if value is not None:
            cells[cell.attrib["r"]] = shared[int(value.text)] if cell.attrib.get("t") == "s" else value.text
    modules = {key: value for key, value in cells.items() if key.startswith("B") and key != "B2"}
    lessons = {key: value for key, value in cells.items() if key.startswith("C") and key != "C2"}
    tasks = {key: value for key, value in cells.items() if key[0] in "DEF" and key not in ["D2", "E2", "F2"]}
    assert len(modules) == 5 and len(lessons) == 25
    assert not tasks
    assert not worksheet.findall(".//m:f", namespace)
summary = {"date": "2026-10-17", "modules": modules, "lesson_count": len(lessons), "lessons": lessons,
           "populated_task_fields": len(tasks), "formulas": 0,
           "status": "Draft curriculum; no runtime or learner-outcome evaluation applies"}
(ROOT / "docs/outline-check.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("PASS: workbook ZIP/XML intact; five modules; 25 lesson entries; no formulas; task/type/description fields unpopulated")
