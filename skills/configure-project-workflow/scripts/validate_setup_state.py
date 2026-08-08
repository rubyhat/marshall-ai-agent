#!/usr/bin/env python3
"""Validate resumable project-workflow setup state and module dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


MODES = {"initialize", "resume", "reconfigure"}
PHASES = {
    "inspection",
    "safety",
    "module_selection",
    "interview",
    "manifest_preview",
    "approved",
    "applying",
    "validation",
    "blocked",
    "complete",
}
QUESTION_STATUSES = {
    "pending",
    "detected_needs_confirmation",
    "answered",
    "assumed",
    "deferred",
    "blocked",
    "not_applicable",
}
VALIDATION_STATUSES = {"not_run", "running", "passed", "failed", "blocked"}
MANIFEST_OPERATIONS = {
    "create",
    "update",
    "update_managed_section",
    "install",
    "disable",
    "preserve",
    "delete_setup_state",
}
SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "secrets",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "private_key",
    "credential",
    "credentials",
}
REQUIRED_KEYS = {
    "schema_version",
    "setup_id",
    "mode",
    "phase",
    "project_root",
    "workflow_kit",
    "protection",
    "facts",
    "decisions",
    "modules",
    "questions",
    "assumptions",
    "conflicts",
    "deferred_topics",
    "manifest",
    "validation",
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def find_sensitive_keys(value: Any, trail: Tuple[str, ...] = ()) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            current = trail + (str(key),)
            if normalized in SENSITIVE_KEYS:
                yield ".".join(current)
            yield from find_sensitive_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from find_sensitive_keys(child, trail + (str(index),))


def validate_relative_target(target: Any) -> bool:
    if not isinstance(target, str) or not target:
        return False
    path = Path(target)
    return not path.is_absolute() and ".." not in path.parts


def module_index(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    modules = catalog.get("modules")
    if not isinstance(modules, list):
        raise ValueError("Catalog must contain a modules array")
    result: Dict[str, Dict[str, Any]] = {}
    for module in modules:
        if not isinstance(module, dict) or not isinstance(module.get("name"), str):
            raise ValueError("Every catalog module must have a string name")
        name = module["name"]
        if name in result:
            raise ValueError(f"Duplicate module in catalog: {name}")

        config_section = module.get("config_section")
        if not isinstance(config_section, str) or not config_section:
            raise ValueError(f"Module {name} config_section must be a name")
        additional_config_sections = module.get("additional_config_sections", [])
        if not isinstance(additional_config_sections, list) or not all(
            isinstance(item, str) and item for item in additional_config_sections
        ):
            raise ValueError(
                f"Module {name} additional_config_sections must be an array of names"
            )
        if config_section in additional_config_sections or len(
            set(additional_config_sections)
        ) != len(additional_config_sections):
            raise ValueError(
                f"Module {name} configuration sections must be unique"
            )
        result[name] = module

    seen_aliases: Dict[str, str] = {}
    for name, module in result.items():
        dependencies = module.get("requires", [])
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) for item in dependencies
        ):
            raise ValueError(f"Module {name} requires must be an array of names")
        for dependency in dependencies:
            if dependency not in result:
                raise ValueError(f"Module {name} requires unknown module {dependency}")

        aliases = module.get("aliases", [])
        if not isinstance(aliases, list) or not all(
            isinstance(item, str) and item for item in aliases
        ):
            raise ValueError(f"Module {name} aliases must be an array of commands")

        conditional_aliases = module.get("conditional_aliases", [])
        if not isinstance(conditional_aliases, list):
            raise ValueError(f"Module {name} conditional_aliases must be an array")

        alias_entries = [(alias, []) for alias in aliases]
        for index, entry in enumerate(conditional_aliases):
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Module {name} conditional_aliases[{index}] must be an object"
                )
            command = entry.get("command")
            requirements = entry.get("requires")
            if not isinstance(command, str) or not command:
                raise ValueError(
                    f"Module {name} conditional_aliases[{index}] needs a command"
                )
            if not isinstance(requirements, list) or not requirements or not all(
                isinstance(item, str) for item in requirements
            ):
                raise ValueError(
                    f"Conditional alias {command} requires a non-empty module list"
                )
            alias_entries.append((command, requirements))

        for command, requirements in alias_entries:
            if command in seen_aliases:
                raise ValueError(
                    f"Duplicate alias {command}: {seen_aliases[command]} and {name}"
                )
            seen_aliases[command] = name
            for dependency in requirements:
                if dependency not in result:
                    raise ValueError(
                        f"Conditional alias {command} requires unknown module {dependency}"
                    )
    return result


def alias_index(
    modules: Dict[str, Dict[str, Any]]
) -> Dict[str, Tuple[str, List[str]]]:
    result: Dict[str, Tuple[str, List[str]]] = {}
    for name, module in modules.items():
        for command in module.get("aliases", []):
            result[command] = (name, [])
        for entry in module.get("conditional_aliases", []):
            result[entry["command"]] = (name, entry["requires"])
    return result


def validate(state: Dict[str, Any], catalog: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    missing = sorted(REQUIRED_KEYS - set(state))
    if missing:
        errors.append(f"Missing required keys: {', '.join(missing)}")

    if state.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if state.get("mode") not in MODES:
        errors.append(f"Unsupported mode: {state.get('mode')!r}")
    if state.get("phase") not in PHASES:
        errors.append(f"Unsupported phase: {state.get('phase')!r}")

    root_value = state.get("project_root")
    if not isinstance(root_value, str) or not Path(root_value).expanduser().is_absolute():
        errors.append("project_root must be an absolute path")

    for key in ("facts", "decisions", "questions", "assumptions", "conflicts", "deferred_topics", "manifest"):
        if key in state and not isinstance(state[key], list):
            errors.append(f"{key} must be an array")

    sensitive = sorted(set(find_sensitive_keys(state)))
    if sensitive:
        errors.append(f"Sensitive key names are forbidden in setup state: {', '.join(sensitive)}")

    questions = state.get("questions", [])
    seen_questions: Set[str] = set()
    if isinstance(questions, list):
        for index, question in enumerate(questions):
            if not isinstance(question, dict):
                errors.append(f"questions[{index}] must be an object")
                continue
            question_id = question.get("id")
            if not isinstance(question_id, str) or not question_id:
                errors.append(f"questions[{index}].id must be a non-empty string")
            elif question_id in seen_questions:
                errors.append(f"Duplicate question id: {question_id}")
            else:
                seen_questions.add(question_id)
            if question.get("status") not in QUESTION_STATUSES:
                errors.append(f"Question {question_id or index} has invalid status")

    try:
        available = module_index(catalog)
    except ValueError as error:
        errors.append(str(error))
        available = {}

    modules = state.get("modules", {})
    selected = modules.get("selected", []) if isinstance(modules, dict) else []
    enabled_aliases = (
        modules.get("enabled_aliases", []) if isinstance(modules, dict) else []
    )
    if isinstance(modules, dict) and "enabled_aliases" not in modules:
        errors.append("modules.enabled_aliases is required")
    if not isinstance(modules, dict) or not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        errors.append("modules.selected must be an array of skill names")
        selected = []
    if not isinstance(enabled_aliases, list) or not all(
        isinstance(item, str) for item in enabled_aliases
    ):
        errors.append("modules.enabled_aliases must be an array of commands")
        enabled_aliases = []
    if len(selected) != len(set(selected)):
        errors.append("modules.selected contains duplicates")
    if len(enabled_aliases) != len(set(enabled_aliases)):
        errors.append("modules.enabled_aliases contains duplicates")

    selected_set = set(selected)
    for name in sorted(selected_set):
        if name not in available:
            errors.append(f"Unknown selected module: {name}")
            continue
        for dependency in available[name].get("requires", []):
            if dependency not in selected_set:
                errors.append(f"Module {name} requires {dependency}")

    aliases = alias_index(available)
    for command in sorted(set(enabled_aliases)):
        if command not in aliases:
            errors.append(f"Unknown enabled alias: {command}")
            continue
        owner, requirements = aliases[command]
        if owner not in selected_set:
            errors.append(f"Alias {command} requires owning module {owner}")
        for dependency in requirements:
            if dependency not in selected_set:
                errors.append(f"Alias {command} requires module {dependency}")

    manifest = state.get("manifest", [])
    if isinstance(manifest, list):
        for index, item in enumerate(manifest):
            if not isinstance(item, dict):
                errors.append(f"manifest[{index}] must be an object")
                continue
            operation = item.get("operation")
            if operation not in MANIFEST_OPERATIONS:
                errors.append(f"manifest[{index}] has unsupported operation: {operation!r}")
            scope = item.get("scope", "project")
            target = item.get("target")
            if scope == "project" and not validate_relative_target(target):
                errors.append(f"manifest[{index}] project target must be a safe relative path")
            elif scope == "active_install":
                if not isinstance(target, str) or not target.startswith("~/.codex/skills/"):
                    errors.append(f"manifest[{index}] active_install target must be under ~/.codex/skills/")
            elif scope not in {"project", "active_install"}:
                errors.append(f"manifest[{index}] has unsupported scope: {scope!r}")

    validation = state.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    elif validation.get("status") not in VALIDATION_STATUSES:
        errors.append("validation.status is invalid")

    protection = state.get("protection")
    phase = state.get("phase")
    if phase not in {"inspection", "safety"}:
        if not isinstance(protection, dict) or protection.get("default_boundary_confirmed") is not True:
            warnings.append("Default protection boundary is not confirmed")

    if phase in {"manifest_preview", "approved", "applying", "validation", "complete"}:
        unresolved = [
            question.get("id", "<unknown>")
            for question in questions
            if isinstance(question, dict) and question.get("status") in {"pending", "deferred", "blocked", "detected_needs_confirmation"}
        ]
        if unresolved:
            warnings.append(f"Unresolved questions remain: {', '.join(unresolved)}")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    default_catalog = Path(__file__).resolve().parent.parent / "assets" / "workflow-modules.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True)
    parser.add_argument("--catalog", default=str(default_catalog))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = load_json(Path(args.state).expanduser())
        catalog = load_json(Path(args.catalog).expanduser())
        errors, warnings = validate(state, catalog)
    except ValueError as error:
        errors, warnings = [str(error)], []

    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print("Setup state: PASS" if result["valid"] else "Setup state: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
