#!/usr/bin/env python3
"""Validate cross-field semantics in a generated project workflow config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = SKILL_ROOT / "assets" / "workflow-modules.json"
POLICY_OWNERS = {
    "context_loading": "load-project-context",
    "context_recording": "record-project-context",
    "context_maintenance": "maintain-project-context",
}
ADR_MODULE = "record-architecture-decision"
REQUIRED_ADR_STATES = ("accepted", "superseded", "deprecated", "rejected")


def load_mapping(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as error:
            raise RuntimeError(
                "YAML parsing requires an already available safe parser; "
                "do not install one automatically"
            ) from error
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("configuration root must be a mapping")
    return value


def module_index(catalog: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    modules = catalog.get("modules")
    if not isinstance(modules, list):
        raise ValueError("workflow module catalog must contain a modules list")
    index: Dict[str, Mapping[str, Any]] = {}
    for module in modules:
        if not isinstance(module, dict) or not isinstance(module.get("name"), str):
            raise ValueError("workflow module catalog contains an invalid module")
        name = module["name"]
        if name in index:
            raise ValueError(f"workflow module catalog duplicates {name}")
        index[name] = module
    return index


def validate_semantics(
    config: Mapping[str, Any], catalog: Mapping[str, Any]
) -> List[str]:
    errors: List[str] = []
    workflow_kit = config.get("workflow_kit")
    selected_raw = (
        workflow_kit.get("selected_modules")
        if isinstance(workflow_kit, dict)
        else None
    )
    if not isinstance(selected_raw, list) or not all(
        isinstance(item, str) for item in selected_raw
    ):
        return ["workflow_kit.selected_modules must be a list of module names"]

    selected = set(selected_raw)
    index = module_index(catalog)
    for module in sorted(selected):
        if module not in index:
            errors.append(f"selected module is unknown: {module}")
            continue
        dependencies = index[module].get("requires", [])
        if not isinstance(dependencies, list):
            errors.append(f"module {module} has invalid requires metadata")
            continue
        for dependency in dependencies:
            if dependency not in selected:
                errors.append(f"module {module} requires {dependency}")

    memory = config.get("memory")
    memory_mapping = memory if isinstance(memory, dict) else {}
    for policy, owner in POLICY_OWNERS.items():
        present = policy in memory_mapping
        if owner in selected and not present:
            errors.append(f"memory.{policy} is required by {owner}")
        if owner not in selected and present:
            errors.append(f"memory.{policy} is forbidden without {owner}")

    adr = config.get("architecture_decisions")
    if ADR_MODULE in selected and not isinstance(adr, dict):
        errors.append(f"architecture_decisions is required by {ADR_MODULE}")
    if ADR_MODULE not in selected and adr is not None:
        errors.append(f"architecture_decisions is forbidden without {ADR_MODULE}")

    if isinstance(adr, dict):
        statuses = adr.get("statuses")
        if not isinstance(statuses, dict):
            errors.append("architecture_decisions.statuses must be a mapping")
        else:
            labels: List[str] = []
            for state in REQUIRED_ADR_STATES:
                if state not in statuses:
                    errors.append(
                        f"architecture_decisions.statuses.{state} must be a non-empty label"
                    )
            for state, label in statuses.items():
                if state == "proposed" and label is None:
                    continue
                if not isinstance(label, str) or not label:
                    errors.append(
                        f"architecture_decisions.statuses.{state} must be a non-empty label"
                    )
                else:
                    labels.append(label)
            duplicates = sorted({label for label in labels if labels.count(label) > 1})
            if duplicates:
                errors.append(
                    "architecture decision lifecycle labels must be distinct: "
                    + ", ".join(repr(label) for label in duplicates)
                )

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate project workflow cross-field semantics."
    )
    parser.add_argument("--config", required=True, help="Generated YAML or JSON config")
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG),
        help="Workflow module catalog JSON",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_mapping(Path(args.config))
        catalog = load_mapping(Path(args.catalog))
        errors = validate_semantics(config, catalog)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Project workflow validation could not run: {error}", file=sys.stderr)
        return 2
    if errors:
        print("Project workflow semantic validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Project workflow semantic validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
