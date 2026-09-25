#!/usr/bin/env python3
"""Validate a stage's JSON output against its contract (a JSON-Schema subset).

    python3 tools/validate_contract.py pipeline/stage1-issues.json contracts/stage1-issues.schema.json

Supports: type, required, properties, items, enum, pattern, minItems, maxLength.
Standard library only, so it runs anywhere the pipeline runs (including CI).
Exit 0 = valid, 1 = invalid. "An unspecified format silently breaks" (Lesson 3.9.1) -
a validated one breaks loudly, at the stage boundary, where a retry is cheap.
"""
import json
import re
import sys

TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool}


def validate(value, schema, path="$"):
    errs = []
    t = schema.get("type")
    if t and not isinstance(value, TYPES[t]):
        return [f"{path}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: {value!r} does not match {schema['pattern']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: length {len(value)} > {schema['maxLength']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errs.append(f"{path}: {len(value)} items < minItems {schema['minItems']}")
        for i, item in enumerate(value):
            errs += validate(item, schema.get("items", {}), f"{path}[{i}]")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required key '{k}'")
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errs += validate(value[k], sub, f"{path}.{k}")
    return errs


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    data_path, schema_path = argv
    try:
        data = json.load(open(data_path))
    except (OSError, ValueError) as exc:
        print(f"INVALID {data_path}: not readable JSON ({exc})")
        return 1
    errs = validate(data, json.load(open(schema_path)))
    if errs:
        print(f"INVALID {data_path} ({len(errs)} problem(s))")
        for e in errs[:20]:
            print("  -", e)
        return 1
    print(f"VALID   {data_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
