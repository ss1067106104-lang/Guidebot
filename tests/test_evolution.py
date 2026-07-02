from __future__ import annotations

from guidebot.evolution import EvolutionEngine, EvolutionGate, ProposalStatus, SkillProposal


class TextEvaluator:
    async def score(self, skill: str, trajectories: object) -> float:
        return 1.0 if "ask before moving" in skill else 0.5


async def test_only_measured_improvement_passes_gate() -> None:
    current = "# Skill\nBe helpful.\n"
    proposal = SkillProposal(
        current + "- ask before moving\n",
        "reduce surprising motion",
        ("add consent rule",),
    )

    passed = await EvolutionGate().validate(current, proposal, TextEvaluator(), [])

    assert passed
    assert proposal.status is ProposalStatus.VALIDATED


async def test_safety_bypass_is_never_evolvable() -> None:
    current = "# Skill\nBe helpful.\n"
    proposal = SkillProposal(current + "- disable safety policy\n", "move faster", ("bad edit",))

    passed = await EvolutionGate().validate(current, proposal, TextEvaluator(), [])

    assert not passed
    assert proposal.status is ProposalStatus.REJECTED


class ConsentOptimizer:
    async def propose(self, skill: str, trajectories: object) -> SkillProposal:
        return SkillProposal(skill + "- ask before moving\n", "safer interaction", ("add rule",))


async def test_engine_requires_validation_then_explicit_approval(tmp_path) -> None:
    skill_path = tmp_path / "skill.md"
    skill_path.write_text("# Skill\nBe helpful.\n", encoding="utf-8")
    engine = EvolutionEngine(skill_path, ConsentOptimizer(), TextEvaluator())

    proposal = await engine.evolve([], [])

    assert proposal.status is ProposalStatus.VALIDATED
    assert "ask before moving" not in skill_path.read_text(encoding="utf-8")
    engine.approve(proposal.id)
    assert proposal.status is ProposalStatus.APPROVED
    assert "ask before moving" in skill_path.read_text(encoding="utf-8")
