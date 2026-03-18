from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "mock_research"


class MockResearchFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        shutil.copytree(REPO_ROOT / "scripts", self.workspace / "scripts")
        shutil.copytree(FIXTURE_ROOT / "state", self.workspace / "state")
        shutil.copytree(FIXTURE_ROOT / "memory", self.workspace / "memory")
        shutil.copytree(FIXTURE_ROOT / "docs", self.workspace / "docs")
        shutil.copytree(FIXTURE_ROOT / "templates", self.workspace / "templates")
        (self.workspace / "runs").mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_script(self, script_name: str, *args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(self.workspace / "scripts" / script_name), *args],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        if expect_success and completed.returncode != 0:
            self.fail(
                f"{script_name} failed unexpectedly.\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        if not expect_success and completed.returncode == 0:
            self.fail(f"{script_name} succeeded unexpectedly.\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
        return completed

    def write_plan_reviews(self, text: str) -> None:
        (self.workspace / "state" / "plan_reviews.yaml").write_text(text, encoding="utf-8")

    def append_done_task_without_verdict(self) -> None:
        path = self.workspace / "state" / "tasks.yaml"
        path.write_text(
            path.read_text(encoding="utf-8")
            + (
                "  - id: TASK-BAD-001\n"
                "    title: Broken task completion\n"
                "    plan_id: PLAN-MOCK-001\n"
                "    stage: execution\n"
                "    kind: implementation\n"
                "    status: done\n"
                "    owner: claude\n"
                "    reviewer: codex\n"
                "    updated_at: 2026-03-18\n"
                "    why: This is a deliberate failure injection for review gate testing.\n"
                "    success: The gate should reject this task because no verdict exists.\n"
                "    next_action: Do not allow completion.\n"
                "    blockers: []\n"
                "    validation:\n"
                "      - python -m py_compile src/mock_impl.py\n"
                "    links:\n"
                "      - docs/mock-plan.md\n"
            ),
            encoding="utf-8",
        )

    def test_mock_research_flow(self) -> None:
        self.run_script("validate_state.py")
        self.run_script("check_task_quality.py")
        self.run_script("review_gate.py")

        gate = self.run_script("plan_gate.py", "PLAN-MOCK-001")
        self.assertIn("Review outcome: draft", gate.stdout)

        require_gate = self.run_script("plan_gate.py", "PLAN-MOCK-001", "--require-approved", expect_success=False)
        self.assertIn("not approved yet", require_gate.stdout)

        create_before_approval = self.run_script("create_execution_tasks.py", "PLAN-MOCK-001", expect_success=False)
        self.assertIn("is not approved", create_before_approval.stdout)

        self.write_plan_reviews(
            "plan_reviews:\n"
            "  - id: PREVIEW-MOCK-001\n"
            "    plan_id: PLAN-MOCK-001\n"
            "    reviewer: codex\n"
            "    role: direction\n"
            "    decision: approve\n"
            "    rationale: The mock plan has clear scope and measurable success.\n"
            "    evidence:\n"
            "      - docs/mock-plan.md\n"
            "    updated_at: 2026-03-18\n"
            "  - id: PREVIEW-MOCK-002\n"
            "    plan_id: PLAN-MOCK-001\n"
            "    reviewer: human\n"
            "    role: safety\n"
            "    decision: approve\n"
            "    rationale: The execution task is bounded and validation is explicit.\n"
            "    evidence:\n"
            "      - docs/mock-plan.md\n"
            "    updated_at: 2026-03-18\n"
        )

        self.run_script("validate_state.py")
        self.run_script("check_task_quality.py")
        approved = self.run_script("plan_gate.py", "PLAN-MOCK-001", "--require-approved")
        self.assertIn("Approvals: 2/2", approved.stdout)

        created = self.run_script("create_execution_tasks.py", "PLAN-MOCK-001")
        self.assertIn("TASK-MOCK-001", created.stdout)

        self.run_script("validate_state.py")
        self.run_script("check_task_quality.py")
        self.run_script("review_gate.py")

        run_result = self.run_script("run_task.py", "TASK-MOCK-001")
        self.assertIn("Created run scaffold", run_result.stdout)
        runs = list((self.workspace / "runs").glob("*-task-mock-001"))
        self.assertEqual(len(runs), 1)

        self.append_done_task_without_verdict()
        gate_failure = self.run_script("review_gate.py", expect_success=False)
        self.assertIn("TASK-BAD-001", gate_failure.stdout)


if __name__ == "__main__":
    unittest.main()
