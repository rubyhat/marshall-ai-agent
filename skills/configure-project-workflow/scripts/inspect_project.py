#!/usr/bin/env python3
"""Read-only bounded inventory for project workflow setup."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".nuxt",
    ".parcel-cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "log",
    "logs",
    "node_modules",
    "out",
    "public/assets",
    "target",
    "tmp",
    "vendor",
    "venv",
}

SENSITIVE_NAME_PATTERNS = (
    re.compile(r"^\.env(?:\.|$)", re.IGNORECASE),
    re.compile(r"(?:^|[._-])(secret|secrets|credential|credentials)(?:[._-]|$)", re.IGNORECASE),
    re.compile(r"(?:^|[._-])(private[_-]?key|api[_-]?key|access[_-]?token)(?:[._-]|$)", re.IGNORECASE),
    re.compile(r"^(id_rsa|id_ed25519|id_ecdsa)(?:\.|$)", re.IGNORECASE),
    re.compile(r"\.(?:key|p12|pfx|pem|kdbx)$", re.IGNORECASE),
)

MANIFEST_NAMES = {
    "package.json",
    "pnpm-workspace.yaml",
    "yarn.lock",
    "pnpm-lock.yaml",
    "package-lock.json",
    "Gemfile",
    "Gemfile.lock",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "go.mod",
    "Cargo.toml",
    "composer.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "mix.exs",
    "Package.swift",
}

SAFE_CONTENT_MANIFESTS = {"package.json", "Gemfile", "pyproject.toml", "go.mod", "Cargo.toml"}
MAX_SAFE_MANIFEST_BYTES = 512_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_sensitive_name(name: str) -> bool:
    return any(pattern.search(name) for pattern in SENSITIVE_NAME_PATTERNS)


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def relative(root: Path, path: Path) -> str:
    return "." if path == root else path.relative_to(root).as_posix()


def run_git(repo: Path, args: List[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_metadata(repo: Path) -> Dict[str, Any]:
    branch = run_git(repo, ["branch", "--show-current"])
    top = run_git(repo, ["rev-parse", "--show-toplevel"])
    names = run_git(repo, ["remote"])
    return {
        "root": str(repo),
        "reported_top_level": top,
        "branch": branch,
        "remote_names": sorted(names.splitlines()) if names else [],
        "remote_urls_read": False,
    }


def categorize(path: Path, root: Path) -> Optional[str]:
    rel = path.relative_to(root)
    name = path.name
    lower_parts = [part.lower() for part in rel.parts]

    if name == "AGENTS.md":
        return "instructions"
    if name in MANIFEST_NAMES:
        return "manifests"
    if name == "CODEOWNERS" or ".github" in lower_parts and "issue_template" in lower_parts:
        return "repository_policy"
    if (
        ".github" in lower_parts
        and "workflows" in lower_parts
        or name in {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml"}
    ):
        return "ci"
    if name.startswith("README") or name in {"ARCHITECTURE.md", "CONTRIBUTING.md", "SECURITY.md"}:
        return "documentation"
    if any(part in {"docs", "docs_ai", "local_memory_ai"} for part in lower_parts):
        if path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}:
            return "documentation"
    if ".codex" in lower_parts or name in {"project-workflow.yaml", "project-workflow.yml"}:
        return "workflow"
    return None


def read_safe_manifest(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_SAFE_MANIFEST_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def detect_technology(manifest_paths: Iterable[Path]) -> Dict[str, Any]:
    languages: Set[str] = set()
    frameworks: Set[str] = set()
    package_managers: Set[str] = set()
    workspaces: Set[str] = set()

    for path in manifest_paths:
        name = path.name
        if name == "package.json":
            languages.add("javascript_or_typescript")
            package_managers.add("node")
            text = read_safe_manifest(path)
            if text:
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = {}
                dependencies = {}
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    value = data.get(key, {})
                    if isinstance(value, dict):
                        dependencies.update(value)
                signals = {
                    "next": "nextjs",
                    "react": "react",
                    "vue": "vue",
                    "nuxt": "nuxt",
                    "@angular/core": "angular",
                    "svelte": "svelte",
                    "@nestjs/core": "nestjs",
                }
                for dependency, framework in signals.items():
                    if dependency in dependencies:
                        frameworks.add(framework)
                if data.get("workspaces"):
                    workspaces.add(str(path.parent))
                manager = data.get("packageManager")
                if isinstance(manager, str):
                    package_managers.add(manager.split("@", 1)[0])
        elif name in {"pnpm-workspace.yaml", "pnpm-lock.yaml"}:
            languages.add("javascript_or_typescript")
            package_managers.add("pnpm")
        elif name == "yarn.lock":
            languages.add("javascript_or_typescript")
            package_managers.add("yarn")
        elif name == "package-lock.json":
            languages.add("javascript_or_typescript")
            package_managers.add("npm")
        elif name == "Gemfile":
            languages.add("ruby")
            package_managers.add("bundler")
            text = read_safe_manifest(path) or ""
            if re.search(r"gem\\s+['\"]rails['\"]", text):
                frameworks.add("rails")
        elif name in {"pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock"}:
            languages.add("python")
            text = read_safe_manifest(path) if name == "pyproject.toml" else ""
            for signal in ("django", "fastapi", "flask"):
                if text and signal in text.lower():
                    frameworks.add(signal)
        elif name == "go.mod":
            languages.add("go")
            package_managers.add("go_modules")
        elif name == "Cargo.toml":
            languages.add("rust")
            package_managers.add("cargo")
        elif name == "composer.json":
            languages.add("php")
            package_managers.add("composer")
        elif name in {"pom.xml", "build.gradle", "build.gradle.kts"}:
            languages.add("jvm")
        elif name == "mix.exs":
            languages.add("elixir")
            package_managers.add("mix")
        elif name == "Package.swift":
            languages.add("swift")
            package_managers.add("swift_package_manager")

    return {
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "package_managers": sorted(package_managers),
        "workspace_roots": sorted(workspaces),
    }


def detect_topology_candidates(
    root: Path,
    manifest_paths: Iterable[Path],
    git_roots: Iterable[Path],
    categories: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
    """Group safe structural evidence without declaring service ownership."""

    candidates: Dict[str, Dict[str, Set[str]]] = {}

    def add(candidate_path: Path, evidence_kind: str, evidence_path: Path) -> None:
        key = relative(root, candidate_path)
        entry = candidates.setdefault(
            key,
            {"evidence_kinds": set(), "evidence_paths": set()},
        )
        entry["evidence_kinds"].add(evidence_kind)
        entry["evidence_paths"].add(relative(root, evidence_path))

    for git_root in git_roots:
        add(git_root, "git_root", git_root / ".git")

    for manifest in manifest_paths:
        add(manifest.parent, "manifest_root", manifest)

    for instruction in categories.get("instructions", []):
        path = root / instruction
        add(path.parent, "instruction_root", path)

    for document in categories.get("documentation", []):
        path = root / document
        if path.name == "ARCHITECTURE.md":
            add(path.parent, "architecture_root", path)

    return [
        {
            "path": path,
            "evidence_kinds": sorted(evidence["evidence_kinds"]),
            "evidence_paths": sorted(evidence["evidence_paths"]),
        }
        for path, evidence in sorted(candidates.items())
    ]


def inspect(root: Path, max_depth: int, max_files: int) -> Dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    categories: Dict[str, List[str]] = {
        "instructions": [],
        "manifests": [],
        "repository_policy": [],
        "ci": [],
        "documentation": [],
        "workflow": [],
    }
    manifest_paths: List[Path] = []
    git_roots: Set[Path] = set()
    skipped = {
        "sensitive_entries": 0,
        "excluded_directories": 0,
        "symlinks": 0,
        "external_git_links": 0,
    }
    scanned_files = 0
    limit_reached = False

    for current_raw, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(current_raw)
        depth = len(current.relative_to(root).parts)
        if depth > max_depth:
            dirnames[:] = []
            continue

        git_marker = current / ".git"
        if git_marker.is_dir():
            git_roots.add(current)
        elif git_marker.is_file():
            skipped["external_git_links"] += 1

        kept_dirs: List[str] = []
        for dirname in sorted(dirnames):
            candidate = current / dirname
            rel_name = candidate.relative_to(root).as_posix()
            if candidate.is_symlink():
                skipped["symlinks"] += 1
                continue
            if is_sensitive_name(dirname):
                skipped["sensitive_entries"] += 1
                continue
            if dirname in EXCLUDED_DIRS or rel_name in EXCLUDED_DIRS:
                skipped["excluded_directories"] += 1
                continue
            if not inside(root, candidate):
                skipped["symlinks"] += 1
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs if depth < max_depth else []

        for filename in sorted(filenames):
            if scanned_files >= max_files:
                limit_reached = True
                dirnames[:] = []
                break
            scanned_files += 1
            if is_sensitive_name(filename):
                skipped["sensitive_entries"] += 1
                continue
            path = current / filename
            if path.is_symlink() or not inside(root, path):
                skipped["symlinks"] += 1
                continue
            category = categorize(path, root)
            if category:
                categories[category].append(relative(root, path))
            if filename in MANIFEST_NAMES:
                manifest_paths.append(path)

        if limit_reached:
            break

    git_entries = [git_metadata(path) for path in sorted(git_roots)]
    topology_candidates = detect_topology_candidates(
        root, manifest_paths, git_roots, categories
    )

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "read_only": True,
        "root": str(root),
        "limits": {"max_depth": max_depth, "max_files": max_files, "limit_reached": limit_reached},
        "git": git_entries,
        "technology": detect_technology(manifest_paths),
        "topology_candidates": topology_candidates,
        "files": {key: sorted(set(value)) for key, value in categories.items()},
        "layout": {
            "has_codex_directory": (root / ".codex").is_dir(),
            "has_docs_ai": (root / "docs_ai").is_dir(),
            "has_local_memory_ai": (root / "local_memory_ai").is_dir(),
            "has_root_agents": (root / "AGENTS.md").is_file(),
            "has_setup_tracker": (root / ".codex/project-workflow.setup.json").is_file(),
        },
        "skipped": skipped,
        "notice": "Inventory contains safe metadata and bounded manifest signals only; no project code was executed.",
    }


def render_text(result: Dict[str, Any]) -> str:
    lines = [
        f"Root: {result['root']}",
        "Read-only: yes",
        f"Git roots: {len(result['git'])}",
        f"Topology candidates: {len(result['topology_candidates'])}",
        f"Languages: {', '.join(result['technology']['languages']) or 'unknown'}",
        f"Frameworks: {', '.join(result['technology']['frameworks']) or 'unknown'}",
    ]
    for key, values in result["files"].items():
        lines.append(f"{key}: {len(values)}")
    lines.append(f"Sensitive entries skipped: {result['skipped']['sensitive_entries']}")
    lines.append(f"Scan limit reached: {'yes' if result['limits']['limit_reached'] else 'no'}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Exact project root to inspect.")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum directory depth. Default: 5.")
    parser.add_argument("--max-files", type=int, default=20_000, help="Maximum files considered. Default: 20000.")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_depth < 0 or args.max_files < 1:
        print("max-depth must be >= 0 and max-files must be >= 1", file=sys.stderr)
        return 2
    try:
        result = inspect(Path(args.root), args.max_depth, args.max_files)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
