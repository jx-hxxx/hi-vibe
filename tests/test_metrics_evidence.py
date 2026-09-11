"""정량 성과가 재현 가능한 근거로 남고, write-gate가 다시 비대해지지 않게 한다."""
import os
import unittest


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


class MetricsEvidenceContractTest(unittest.TestCase):
    def test_docs_keeper_has_conditional_evidence_mode(self):
        skill = read("skills/docs-keeper/SKILL.md")
        self.assertIn("## Mode: evidence", skill)
        self.assertIn("evidence/METRICS.md", skill)
        self.assertIn("근거가 없으면", skill)

    def test_metrics_template_keeps_reproduction_fields(self):
        template = read("skills/docs-keeper/templates/METRICS.md.tpl")
        for field in (
            "변경 전", "변경 후", "개선율", "측정 명령", "측정 환경",
            "표본", "관련 커밋", "원본 결과",
        ):
            self.assertIn(field, template)

    def test_write_gate_loads_metrics_rules_only_for_numeric_claims(self):
        skill = read("skills/write-gate/SKILL.md")
        self.assertIn("references/metrics-evidence.md", skill)
        self.assertIn("정량", skill)
        self.assertIn("조건", skill)


class WriteGateContextBudgetTest(unittest.TestCase):
    def test_main_skill_stays_lean(self):
        skill = read("skills/write-gate/SKILL.md")
        self.assertLessEqual(
            len(skill.splitlines()), 180,
            "write-gate 본문은 모든 모드가 함께 읽는다 — 세부 절차를 references/로 옮겨라",
        )

    def test_review_contract_moved_to_reference(self):
        skill = read("skills/write-gate/SKILL.md")
        reference = read("skills/write-gate/references/review-checklist.md")
        self.assertIn("references/review-checklist.md", skill)
        for contract in ("실행 검증", "문서 동기화", "fresh-eyes", "review_scope.py"):
            self.assertIn(contract, reference)


if __name__ == "__main__":
    unittest.main()
