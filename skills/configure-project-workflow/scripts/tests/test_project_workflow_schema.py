#!/usr/bin/env python3
"""Executable regression fixtures for the bundled workflow JSON Schema.

The repository validation environment intentionally has no third-party JSON
Schema dependency. This focused Draft 2020-12 subset evaluates every keyword
used by project-workflow.schema.json so its module conditionals remain tested
with the Python standard library.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "assets" / "project-workflow.schema.json"
SCRIPTS_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_PATH))

from validate_project_workflow_config import (  # noqa: E402
    DEFAULT_CATALOG,
    load_mapping,
    validate_semantics,
)


def type_matches(expected: str, value: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise AssertionError(f"Unsupported schema type in test evaluator: {expected}")


def validate(schema: Any, value: Any, path: str = "$") -> List[str]:
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: forbidden by false schema"]

    errors: List[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not type_matches(expected_type, value):
        return [f"{path}: expected {expected_type}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in enum")

    if "anyOf" in schema:
        if not any(not validate(branch, value, path) for branch in schema["anyOf"]):
            errors.append(f"{path}: no anyOf branch matched")

    if "not" in schema and not validate(schema["not"], value, path):
        errors.append(f"{path}: matched forbidden schema")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, value) is None:
            errors.append(f"{path}: string does not match {pattern!r}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has too few items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array items are not unique")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate(schema["items"], item, f"{path}[{index}]"))
        if "contains" in schema and not any(
            not validate(schema["contains"], item, f"{path}[*]") for item in value
        ):
            errors.append(f"{path}: no array item matched contains")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{path}: object has too few properties")
        properties: Dict[str, Any] = schema.get("properties", {})
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate(child_schema, value[key], f"{path}.{key}"))
        additional = schema.get("additionalProperties", True)
        for key in value.keys() - properties.keys():
            if additional is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(validate(additional, value[key], f"{path}.{key}"))

    for index, child_schema in enumerate(schema.get("allOf", [])):
        errors.extend(validate(child_schema, value, f"{path}.allOf[{index}]"))

    if "if" in schema:
        branch = "then" if not validate(schema["if"], value, path) else "else"
        if branch in schema:
            errors.extend(validate(schema[branch], value, path))

    return errors


def rendered_config() -> Dict[str, Any]:
    return {
        "schema_version": 3,
        "workflow_kit": {
            "source": "rubyhat/marshall-ai-agent",
            "revision": "v1.0.0",
            "installation_mode": "centralized",
            "selected_modules": [
                "load-project-context",
                "record-project-context",
                "maintain-project-context",
                "record-architecture-decision",
            ],
        },
        "project": {
            "name": "Example",
            "product_type": "service",
            "repositories": {"main": {}},
        },
        "language": {
            "interaction": "en",
            "project_docs": "en",
            "internal_memory": "en",
        },
        "interaction": {
            "clarifying_questions": {},
            "conflict_and_risk_gate": {},
        },
        "paths": {
            "root_instructions": "AGENTS.md",
            "project_docs": "docs_ai",
            "internal_memory": "local_memory_ai",
        },
        "protection": {
            "default_setup_boundary": "enforced",
            "additional_restrictions": [],
        },
        "memory": {
            "context_loading": {
                "preflight_large_or_mixed_artifacts": True,
                "section_targeting_required_when_available": True,
                "full_read_requires_identified_semantic_need": True,
            },
            "context_recording": {
                "canonical_current_state_only": True,
                "task_chronology_in_canonical_forbidden": True,
                "update_existing_owner_before_create": True,
            },
            "context_maintenance": {
                "manual_only": True,
                "audit_before_cleanup": True,
                "exact_manifest_approval_required": True,
                "section_level_compaction_for_mixed_canonical": True,
                "diagnostic_metrics_are_not_retention_rules": True,
            },
        },
        "architecture_decisions": {
            "enabled": True,
            "root": "docs_ai/adr",
            "index": "docs_ai/adr/README.md",
            "id_pattern": "ADR-[0-9]{4}",
            "filename_pattern": "<ID>-<slug>.md",
            "statuses": {
                "proposed": "proposed",
                "accepted": "accepted",
                "superseded": "superseded",
                "deprecated": "deprecated",
                "rejected": "rejected",
            },
            "decision_authority": ["maintainer"],
            "materiality_triggers": ["cross-component boundary"],
            "supersession": {
                "material_change_creates_new_adr": True,
                "preserve_old_rationale": True,
            },
            "applicability_review": {
                "before_forcing_task_conformance": True,
                "stop_on_unclear_or_review_required": True,
                "review_triggers": ["assumption changed"],
            },
            "bounded_exceptions": {
                "allowed": False,
                "owner_required": True,
                "expiry_or_review_trigger_required": True,
            },
            "retrospective_recording": {
                "allowed": True,
                "requires_verifiable_rationale": True,
                "bulk_creation_forbidden": True,
            },
        },
        "skills": {"active": {"configure-project-workflow": "installed"}},
        "commands": {
            "aliases_are_plain_text": True,
            "aliases_do_not_expand_authority": True,
            "sequence_guard": {
                "enabled": True,
                "stop_before_mutation_on_mismatch": True,
                "report_current_state_and_unmet_prerequisite": True,
                "recommend_exact_next_alias_or_action": True,
            },
            "aliases": {},
        },
    }


class ProjectWorkflowSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.catalog = load_mapping(DEFAULT_CATALOG)

    def assert_valid(self, config: Dict[str, Any]) -> None:
        errors = validate(self.schema, config)
        errors.extend(validate_semantics(config, self.catalog))
        self.assertEqual(errors, [])

    def assert_invalid(self, config: Dict[str, Any]) -> None:
        errors = validate(self.schema, config)
        errors.extend(validate_semantics(config, self.catalog))
        self.assertNotEqual(errors, [])

    def test_complete_rendered_config_is_valid(self) -> None:
        self.assert_valid(rendered_config())

    def test_selected_context_module_requires_its_policy(self) -> None:
        config = rendered_config()
        del config["memory"]["context_loading"]
        self.assert_invalid(config)

    def test_unselected_context_module_forbids_its_policy(self) -> None:
        config = rendered_config()
        config["workflow_kit"]["selected_modules"].remove("load-project-context")
        self.assert_invalid(config)

    def test_selected_adr_module_requires_its_policy(self) -> None:
        config = rendered_config()
        del config["architecture_decisions"]
        self.assert_invalid(config)

    def test_unselected_adr_module_forbids_its_policy(self) -> None:
        config = rendered_config()
        config["workflow_kit"]["selected_modules"].remove(
            "record-architecture-decision"
        )
        self.assert_invalid(config)

    def test_unselected_adr_module_without_policy_is_valid(self) -> None:
        config = rendered_config()
        config["workflow_kit"]["selected_modules"].remove(
            "record-architecture-decision"
        )
        del config["architecture_decisions"]
        self.assert_valid(config)

    def test_adr_lifecycle_labels_must_be_distinct(self) -> None:
        config = rendered_config()
        config["architecture_decisions"]["statuses"] = {
            "proposed": "same",
            "accepted": "same",
            "superseded": "same",
            "deprecated": "same",
            "rejected": "same",
        }
        self.assert_invalid(config)

    def test_custom_adr_lifecycle_label_must_be_distinct(self) -> None:
        config = rendered_config()
        config["architecture_decisions"]["statuses"]["draft"] = "accepted"
        self.assert_invalid(config)

    def test_adr_lifecycle_label_must_not_be_whitespace_only(self) -> None:
        config = rendered_config()
        config["architecture_decisions"]["statuses"]["accepted"] = "   "
        self.assert_invalid(config)

    def test_adr_identifier_pattern_must_compile(self) -> None:
        config = rendered_config()
        config["architecture_decisions"]["id_pattern"] = "["
        self.assert_invalid(config)

    def test_adr_authority_and_trigger_entries_must_not_be_blank(self) -> None:
        cases = (
            ("decision_authority",),
            ("materiality_triggers",),
            ("applicability_review", "review_triggers"),
        )
        for path in cases:
            with self.subTest(path=path):
                config = rendered_config()
                owner = config["architecture_decisions"]
                for key in path[:-1]:
                    owner = owner[key]
                owner[path[-1]] = ["   "]
                self.assert_invalid(config)

    def test_each_context_conditional_has_positive_and_negative_coverage(self) -> None:
        policy_by_module = {
            "load-project-context": "context_loading",
            "record-project-context": "context_recording",
            "maintain-project-context": "context_maintenance",
        }
        for module, policy in policy_by_module.items():
            with self.subTest(module=module, case="unselected_policy_absent"):
                config = rendered_config()
                if module == "record-project-context":
                    config["workflow_kit"]["selected_modules"].remove(
                        "maintain-project-context"
                    )
                    del config["memory"]["context_maintenance"]
                    config["workflow_kit"]["selected_modules"].remove(
                        "record-architecture-decision"
                    )
                    del config["architecture_decisions"]
                config["workflow_kit"]["selected_modules"].remove(module)
                del config["memory"][policy]
                self.assert_valid(config)
            with self.subTest(module=module, case="missing_selected_policy"):
                config = rendered_config()
                del config["memory"][policy]
                self.assert_invalid(config)
            with self.subTest(module=module, case="unexpected_unselected_policy"):
                config = rendered_config()
                config["workflow_kit"]["selected_modules"].remove(module)
                self.assert_invalid(config)


if __name__ == "__main__":
    unittest.main()
