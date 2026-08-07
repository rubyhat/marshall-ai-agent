#!/usr/bin/env python3
"""Validate repository-level invariants for the reusable skill library."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
README_PATH = ROOT / "README.md"
WORKFLOW_MODULES_PATH = (
    SKILLS_ROOT
    / "configure-project-workflow"
    / "assets"
    / "workflow-modules.json"
)

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
QUOTED_YAML_VALUE_RE = re.compile(
    r'^\s{2}(display_name|short_description|default_prompt):\s*"([^"]*)"\s*$'
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"}
FULL_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ACTION_REFERENCE_RE = re.compile(r"^\s*uses:\s+([^@\s]+)@([^\s#]+)")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.test_files = 0

    def error(self, path: Path, message: str) -> None:
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            display_path = path
        self.errors.append(f"{display_path}: {message}")


def parse_frontmatter(validation: Validation, skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0] != "---":
        validation.error(skill_md, "SKILL.md must start with YAML frontmatter")
        return {}

    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        validation.error(skill_md, "YAML frontmatter is not closed")
        return {}

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        if not line.strip():
            continue
        if ":" not in line:
            validation.error(
                skill_md, f"invalid frontmatter entry on line {line_number}"
            )
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in fields:
            validation.error(skill_md, f"duplicate frontmatter field {key!r}")
        fields[key] = value

    allowed_fields = {"name", "description"}
    unexpected = sorted(set(fields) - allowed_fields)
    if unexpected:
        validation.error(
            skill_md,
            "frontmatter contains unsupported fields: " + ", ".join(unexpected),
        )

    for required in sorted(allowed_fields):
        if not fields.get(required):
            validation.error(skill_md, f"missing frontmatter field {required!r}")

    if len(lines) > 500:
        validation.error(skill_md, "SKILL.md exceeds the 500-line context budget")

    return fields


def parse_openai_yaml(
    validation: Validation, openai_yaml: Path, skill_name: str
) -> None:
    if not openai_yaml.is_file():
        validation.error(openai_yaml, "missing agents/openai.yaml")
        return

    values: dict[str, str] = {}
    lines = openai_yaml.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "interface:":
        validation.error(openai_yaml, "file must start with the interface mapping")

    for line in lines[1:]:
        match = QUOTED_YAML_VALUE_RE.match(line)
        if match:
            values[match.group(1)] = match.group(2)

    for required in ("display_name", "short_description", "default_prompt"):
        if not values.get(required):
            validation.error(openai_yaml, f"missing quoted {required!r}")

    short_description = values.get("short_description", "")
    if short_description and not 25 <= len(short_description) <= 64:
        validation.error(
            openai_yaml,
            "short_description must contain between 25 and 64 characters",
        )

    default_prompt = values.get("default_prompt", "")
    if default_prompt and f"${skill_name}" not in default_prompt:
        validation.error(
            openai_yaml,
            f"default_prompt must explicitly mention ${skill_name}",
        )


def validate_markdown_links(validation: Validation, markdown_path: Path) -> None:
    text = markdown_path.read_text(encoding="utf-8")
    for raw_destination in MARKDOWN_LINK_RE.findall(text):
        destination = raw_destination.strip().strip("<>")
        if not destination or destination.startswith("#"):
            continue
        if re.match(r"^[a-z][a-z0-9+.-]*:", destination, re.IGNORECASE):
            continue

        destination = destination.split("#", 1)[0]
        destination = unquote(destination)
        if not destination:
            continue
        if destination.startswith("/"):
            validation.error(
                markdown_path,
                f"repository documentation must not use absolute link {destination!r}",
            )
            continue

        target = (markdown_path.parent / destination).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            validation.error(
                markdown_path, f"relative link escapes the repository: {destination!r}"
            )
            continue
        if not target.exists():
            validation.error(
                markdown_path, f"relative link target does not exist: {destination!r}"
            )


def validate_json(validation: Validation, path: Path) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        validation.error(path, f"invalid JSON: {error}")


def validate_python(validation: Validation, path: Path) -> None:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        validation.error(path, f"invalid Python syntax: {error}")


def validate_portability(validation: Validation, path: Path) -> None:
    if path.suffix not in TEXT_SUFFIXES:
        return

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    if "fastyshop" in text.lower():
        validation.error(path, "reusable skill contains FastyShop-specific hardcode")
    if re.search(r"/Users/[^/\s]+", text):
        validation.error(path, "reusable skill contains an absolute macOS user path")
    if re.search(r"/home/[^/\s]+", text):
        validation.error(path, "reusable skill contains an absolute Linux user path")
    if re.search(r"[A-Za-z]:\\Users\\[^\\\s]+", text):
        validation.error(path, "reusable skill contains an absolute Windows user path")


def run_script_tests(validation: Validation, skill_dir: Path) -> None:
    for test_file in sorted(skill_dir.glob("scripts/tests/test_*.py")):
        validation.test_files += 1
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            details = (result.stdout + result.stderr).strip()
            validation.error(test_file, f"script tests failed:\n{details}")


def validate_skill(validation: Validation, skill_dir: Path, run_tests: bool) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        validation.error(skill_md, "missing SKILL.md")
        return skill_dir.name

    fields = parse_frontmatter(validation, skill_md)
    skill_name = fields.get("name", skill_dir.name)

    if not SKILL_NAME_RE.fullmatch(skill_name):
        validation.error(skill_md, f"invalid skill name {skill_name!r}")
    if len(skill_name) > 64:
        validation.error(skill_md, "skill name exceeds 64 characters")
    if skill_name != skill_dir.name:
        validation.error(
            skill_md,
            f"frontmatter name {skill_name!r} must match directory {skill_dir.name!r}",
        )

    parse_openai_yaml(validation, skill_dir / "agents" / "openai.yaml", skill_name)

    for unexpected_name in ("README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"):
        unexpected = skill_dir / unexpected_name
        if unexpected.exists():
            validation.error(
                unexpected,
                "auxiliary documentation does not belong inside a skill folder",
            )

    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        validate_portability(validation, path)
        if path.suffix == ".md":
            validate_markdown_links(validation, path)
        elif path.suffix == ".json":
            validate_json(validation, path)
        elif path.suffix == ".py":
            validate_python(validation, path)

    if run_tests:
        run_script_tests(validation, skill_dir)

    return skill_name


def validate_readme_catalog(validation: Validation, skill_names: list[str]) -> None:
    if not README_PATH.is_file():
        validation.error(README_PATH, "missing root README.md")
        return

    text = README_PATH.read_text(encoding="utf-8")
    validate_markdown_links(validation, README_PATH)

    for skill_name in skill_names:
        if f"`{skill_name}`" not in text:
            validation.error(
                README_PATH, f"skill {skill_name!r} is missing from the catalog"
            )


def validate_workflow_module_catalog(
    validation: Validation, skill_names: list[str]
) -> None:
    try:
        catalog = json.loads(WORKFLOW_MODULES_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        validation.error(WORKFLOW_MODULES_PATH, f"invalid module catalog: {error}")
        return

    modules = catalog.get("modules")
    if not isinstance(modules, list):
        validation.error(WORKFLOW_MODULES_PATH, "modules must be an array")
        return

    module_names = [
        module.get("name")
        for module in modules
        if isinstance(module, dict) and isinstance(module.get("name"), str)
    ]
    if len(module_names) != len(modules):
        validation.error(
            WORKFLOW_MODULES_PATH, "every module must have a string name"
        )

    duplicate_modules = sorted(
        name for name in set(module_names) if module_names.count(name) > 1
    )
    if duplicate_modules:
        validation.error(
            WORKFLOW_MODULES_PATH,
            "duplicate modules: " + ", ".join(duplicate_modules),
        )

    skill_set = set(skill_names)
    module_set = set(module_names)
    missing_modules = sorted(skill_set - module_set)
    unknown_modules = sorted(module_set - skill_set)
    if missing_modules:
        validation.error(
            WORKFLOW_MODULES_PATH,
            "skills missing from module catalog: " + ", ".join(missing_modules),
        )
    if unknown_modules:
        validation.error(
            WORKFLOW_MODULES_PATH,
            "catalog modules without matching skills: " + ", ".join(unknown_modules),
        )

    module_index = {
        module["name"]: module
        for module in modules
        if isinstance(module, dict) and isinstance(module.get("name"), str)
    }
    valid_dependencies: dict[str, list[str]] = {}
    for name, module in module_index.items():
        dependencies = module.get("requires", [])
        if not isinstance(dependencies, list) or not all(
            isinstance(dependency, str) for dependency in dependencies
        ):
            validation.error(
                WORKFLOW_MODULES_PATH,
                f"module {name} requires must be an array of skill names",
            )
            valid_dependencies[name] = []
            continue
        valid_dependencies[name] = dependencies
        for dependency in dependencies:
            if dependency not in module_index:
                validation.error(
                    WORKFLOW_MODULES_PATH,
                    f"module {name} requires unknown module {dependency}",
                )

    profiles = catalog.get("profiles")
    if not isinstance(profiles, dict):
        validation.error(WORKFLOW_MODULES_PATH, "profiles must be an object")
        return
    for profile_name, selected in profiles.items():
        if not isinstance(selected, list) or not all(
            isinstance(name, str) for name in selected
        ):
            validation.error(
                WORKFLOW_MODULES_PATH,
                f"profile {profile_name} must be an array of module names",
            )
            continue
        if len(selected) != len(set(selected)):
            validation.error(
                WORKFLOW_MODULES_PATH,
                f"profile {profile_name} contains duplicate modules",
            )
        selected_set = set(selected)
        for name in selected:
            if name not in module_index:
                validation.error(
                    WORKFLOW_MODULES_PATH,
                    f"profile {profile_name} references unknown module {name}",
                )
                continue
            for dependency in valid_dependencies[name]:
                if dependency not in selected_set:
                    validation.error(
                        WORKFLOW_MODULES_PATH,
                        f"profile {profile_name} selects {name} without {dependency}",
                    )


def validate_root_files(validation: Validation) -> None:
    release_config_path = ROOT / "release-please-config.json"
    for path in (
        ROOT / ".release-please-manifest.json",
        release_config_path,
    ):
        if not path.is_file():
            validation.error(path, "required release configuration is missing")
        else:
            validate_json(validation, path)

    if release_config_path.is_file():
        try:
            release_config = json.loads(
                release_config_path.read_text(encoding="utf-8")
            )
            if release_config.get("initial-version") != "0.1.0":
                validation.error(
                    release_config_path,
                    "initial-version must preserve the v0.1.0 bootstrap policy",
                )
        except (AttributeError, json.JSONDecodeError):
            pass

    version_path = ROOT / "version.txt"
    if not version_path.is_file():
        validation.error(version_path, "missing version.txt")
        version = ""
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(
            r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
            version,
        ):
            validation.error(version_path, f"invalid SemVer core version {version!r}")

    changelog_path = ROOT / "CHANGELOG.md"
    if changelog_path.is_file() and version == "0.0.0":
        changelog = changelog_path.read_text(encoding="utf-8")
        if re.search(r"^#{1,6}\s+", changelog, re.MULTILINE):
            validation.error(
                changelog_path,
                "bootstrap changelog must not define a heading before Release Please",
            )

    manifest_path = ROOT / ".release-please-manifest.json"
    if manifest_path.is_file() and version_path.is_file():
        try:
            manifest_version = json.loads(
                manifest_path.read_text(encoding="utf-8")
            ).get(".")
            version = version_path.read_text(encoding="utf-8").strip()
            if manifest_version != version:
                validation.error(
                    manifest_path,
                    "root manifest version must match version.txt",
                )
        except (AttributeError, json.JSONDecodeError):
            pass

    root_markdown = [
        ROOT / "AGENTS.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "README.md",
        *sorted((ROOT / "docs").glob("**/*.md")),
    ]
    for markdown_path in root_markdown:
        if not markdown_path.is_file():
            validation.error(markdown_path, "required repository documentation is missing")
        else:
            validate_markdown_links(validation, markdown_path)

    workflows_root = ROOT / ".github" / "workflows"
    expected_workflows = {
        workflows_root / "release-please.yml",
        workflows_root / "validate.yml",
    }
    for workflow_path in sorted(expected_workflows):
        if not workflow_path.is_file():
            validation.error(workflow_path, "required GitHub Actions workflow is missing")

    for workflow_path in sorted(workflows_root.glob("*.yml")):
        for line_number, line in enumerate(
            workflow_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = ACTION_REFERENCE_RE.match(line)
            if match and not FULL_GIT_SHA_RE.fullmatch(match.group(2)):
                validation.error(
                    workflow_path,
                    f"external Action on line {line_number} is not pinned to a full SHA",
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate reusable skill repository structure and tests."
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="validate structure without executing bundled script tests",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = Validation()

    if not SKILLS_ROOT.is_dir():
        validation.error(SKILLS_ROOT, "missing skills directory")
        skill_dirs: list[Path] = []
    else:
        skill_dirs = sorted(
            path for path in SKILLS_ROOT.iterdir() if path.is_dir()
        )

    skill_names = [
        validate_skill(validation, skill_dir, run_tests=not args.skip_tests)
        for skill_dir in skill_dirs
    ]

    duplicates = sorted(
        name for name in set(skill_names) if skill_names.count(name) > 1
    )
    if duplicates:
        validation.error(
            SKILLS_ROOT, "duplicate skill names: " + ", ".join(duplicates)
        )

    validate_readme_catalog(validation, skill_names)
    validate_workflow_module_catalog(validation, skill_names)
    validate_root_files(validation)

    if validation.errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    test_summary = (
        "tests skipped"
        if args.skip_tests
        else f"{validation.test_files} script test files"
    )
    print(
        f"Repository validation passed: {len(skill_dirs)} skills, {test_summary}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
