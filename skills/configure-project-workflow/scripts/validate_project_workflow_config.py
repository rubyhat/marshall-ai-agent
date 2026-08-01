#!/usr/bin/env python3
"""Validate cross-field semantics in a generated project workflow config."""

from __future__ import annotations

import argparse
import json
import re
import sre_parse
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
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
ADR_ID_SAFE_CODEPOINTS = frozenset(
    ord(character)
    for character in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
)


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


def validate_nonblank_string_list(
    errors: List[str], path: str, value: Any
) -> None:
    if not isinstance(value, list):
        return
    normalized: List[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{path}[{index}] must be a non-empty value")
        else:
            normalized.append(item.strip())
    duplicates = sorted(
        {item for item in normalized if normalized.count(item) > 1}
    )
    if duplicates:
        errors.append(
            f"{path} entries must be distinct: "
            + ", ".join(repr(item) for item in duplicates)
        )


def safe_relative_project_path(raw: str) -> bool:
    posix_path = PurePosixPath(raw)
    windows_path = PureWindowsPath(raw)
    return not (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or ".." in posix_path.parts
        or ".." in windows_path.parts
    )


def regex_matches_only_safe_adr_id_characters(pattern: str) -> bool:
    """Prove safety and produce one concrete witness for the ADR ID regex."""

    def safe_witness(subpattern: Any) -> Optional[str]:
        pieces: List[str] = []
        for operation, argument in subpattern:
            name = str(operation)
            if name == "LITERAL":
                if argument not in ADR_ID_SAFE_CODEPOINTS:
                    return None
                pieces.append(chr(argument))
            elif name == "IN":
                candidates: List[str] = []
                for item_operation, item_argument in argument:
                    item_name = str(item_operation)
                    if item_name == "LITERAL":
                        if item_argument not in ADR_ID_SAFE_CODEPOINTS:
                            return None
                        candidates.append(chr(item_argument))
                    elif item_name == "RANGE":
                        start, end = item_argument
                        if any(
                            codepoint not in ADR_ID_SAFE_CODEPOINTS
                            for codepoint in range(start, end + 1)
                        ):
                            return None
                        candidates.append(chr(start))
                    else:
                        return None
                if not candidates:
                    return None
                pieces.append(candidates[0])
            elif name in {"MAX_REPEAT", "MIN_REPEAT", "POSSESSIVE_REPEAT"}:
                minimum = argument[0]
                child = safe_witness(argument[-1])
                if child is None or minimum > 256:
                    return None
                pieces.append(child * minimum)
            elif name in {"SUBPATTERN", "ATOMIC_GROUP"}:
                if name == "SUBPATTERN":
                    _, added_flags, removed_flags, child = argument
                    if added_flags or removed_flags:
                        return None
                else:
                    child = argument
                child_witness = safe_witness(child)
                if child_witness is None:
                    return None
                pieces.append(child_witness)
            elif name == "BRANCH":
                branch_witnesses = [
                    safe_witness(branch) for branch in argument[1]
                ]
                if any(witness is None for witness in branch_witnesses):
                    return None
                pieces.append(branch_witnesses[0] or "")
            elif name == "AT":
                continue
            else:
                # Assertions, backreferences, wildcards, categories, negated
                # classes, and conditionals are intentionally unsupported:
                # their satisfiability or output alphabet is not provable by
                # this bounded validator.
                return None
        return "".join(pieces)

    try:
        compiled = re.compile(pattern)
        parsed = sre_parse.parse(pattern)
    except re.error:
        return False
    if compiled.flags != re.UNICODE:
        return False
    witness = safe_witness(parsed)
    return bool(
        witness
        and compiled.fullmatch("") is None
        and compiled.fullmatch(witness) is not None
    )


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
    unknown_memory_policies = sorted(memory_mapping.keys() - POLICY_OWNERS.keys())
    for policy in unknown_memory_policies:
        errors.append(f"memory policy has no workflow module owner: {policy}")
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
        for path_name in ("root", "index"):
            path_value = adr.get(path_name)
            if isinstance(path_value, str) and not safe_relative_project_path(
                path_value
            ):
                errors.append(
                    f"architecture_decisions.{path_name} must stay inside "
                    "the project root"
                )
        adr_root = adr.get("root")
        adr_index = adr.get("index")
        if isinstance(adr_root, str) and isinstance(adr_index, str):
            if (
                PurePosixPath(adr_root) == PurePosixPath(adr_index)
                or PureWindowsPath(adr_root) == PureWindowsPath(adr_index)
            ):
                errors.append(
                    "architecture_decisions.index must be distinct from "
                    "architecture_decisions.root"
                )
        id_pattern = adr.get("id_pattern")
        if isinstance(id_pattern, str) and id_pattern:
            try:
                re.compile(id_pattern)
            except re.error as error:
                errors.append(
                    f"architecture_decisions.id_pattern is invalid: {error}"
                )
            else:
                if not regex_matches_only_safe_adr_id_characters(id_pattern):
                    errors.append(
                        "architecture_decisions.id_pattern must match one or more "
                        "portable filename-safe characters: A-Z, a-z, 0-9, - or _"
                    )
        filename_pattern = adr.get("filename_pattern")
        if isinstance(filename_pattern, str) and "<ID>" not in filename_pattern:
            errors.append(
                "architecture_decisions.filename_pattern must contain <ID>"
            )
        if isinstance(filename_pattern, str):
            if not safe_relative_project_path(filename_pattern):
                errors.append(
                    "architecture_decisions.filename_pattern must stay inside "
                    "architecture_decisions.root"
                )
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
                if not isinstance(label, str) or not label.strip():
                    errors.append(
                        f"architecture_decisions.statuses.{state} must be a non-empty label"
                    )
                else:
                    labels.append(label.strip())
            duplicates = sorted({label for label in labels if labels.count(label) > 1})
            if duplicates:
                errors.append(
                    "architecture decision lifecycle labels must be distinct: "
                    + ", ".join(repr(label) for label in duplicates)
                )
        validate_nonblank_string_list(
            errors,
            "architecture_decisions.decision_authority",
            adr.get("decision_authority"),
        )
        validate_nonblank_string_list(
            errors,
            "architecture_decisions.materiality_triggers",
            adr.get("materiality_triggers"),
        )
        applicability_review = adr.get("applicability_review")
        if isinstance(applicability_review, dict):
            validate_nonblank_string_list(
                errors,
                "architecture_decisions.applicability_review.review_triggers",
                applicability_review.get("review_triggers"),
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
