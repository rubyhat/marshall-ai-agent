import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SHAPE_SKILL = REPOSITORY_ROOT / "skills" / "shape-project-work" / "SKILL.md"
MANAGE_SKILL = REPOSITORY_ROOT / "skills" / "manage-project-work" / "SKILL.md"
IDENTITY_REFERENCE = (
    REPOSITORY_ROOT
    / "skills"
    / "manage-project-work"
    / "references"
    / "task-identity-and-hierarchy.md"
)
CREATE_REFERENCE = (
    REPOSITORY_ROOT
    / "skills"
    / "manage-project-work"
    / "references"
    / "create-or-reconcile-project-task.md"
)
INTERVIEW = (
    REPOSITORY_ROOT
    / "skills"
    / "configure-project-workflow"
    / "references"
    / "configuration-interview.md"
)
PUBLIC_ALIASES_CANDIDATES = (
    REPOSITORY_ROOT / "docs" / "workflow-aliases.md",
    REPOSITORY_ROOT / "workflows" / "agent_commands.md",
)


def resolve_public_aliases() -> Path:
    for candidate in PUBLIC_ALIASES_CANDIDATES:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in PUBLIC_ALIASES_CANDIDATES)
    raise FileNotFoundError(f"Public alias contract not found; searched: {searched}")


ALIASES = resolve_public_aliases()


class RoadmapManifestContractTest(unittest.TestCase):
    def test_roadmap_requires_shaped_outcome_and_one_semantic_preview(self):
        text = SHAPE_SKILL.read_text(encoding="utf-8")
        self.assertIn("already shaped outcome", text)
        self.assertIn("one exact semantic mutation preview", text)
        self.assertIn("stable semantic manifest key", text)
        self.assertIn("stable roadmap-operation key", text)
        self.assertIn("complete concise Issue body", text)
        self.assertIn("predict provider numbers or final Task IDs", text)
        self.assertIn("Do not create or update a local roadmap", text)
        self.assertIn("do not invoke durable local recording", text)
        self.assertNotIn("optional durable-artifact", text)

    def test_task_management_uses_issue_first_provider_identity(self):
        skill = MANAGE_SKILL.read_text(encoding="utf-8")
        identity = IDENTITY_REFERENCE.read_text(encoding="utf-8")
        creation = CREATE_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("create the Issue first", skill)
        self.assertIn("Provider-number-derived identity", identity)
        self.assertIn("Do not search for the “next free” custom number", identity)
        self.assertIn("project-task-key", creation)
        self.assertIn("correlation-marker format", creation)
        self.assertIn("parent-to-child precedence edge", creation)
        self.assertIn("combined graph contains a cycle", creation)
        self.assertIn("semantic key to", skill)

    def test_setup_defaults_to_provider_number_without_forcing_migration(self):
        text = INTERVIEW.read_text(encoding="utf-8")
        self.assertIn("immutable human-visible Issue number", text)
        self.assertIn("coherent existing custom allocator", text)

    def test_public_alias_contract_has_no_local_coordination_output(self):
        text = ALIASES.read_text(encoding="utf-8")
        self.assertIn("exact semantic mutation preview", text)
        self.assertIn("не создаёт локальные roadmap, memory, coordination", text)
        self.assertIn("первым с детерминированным semantic marker", text)


if __name__ == "__main__":
    unittest.main()
