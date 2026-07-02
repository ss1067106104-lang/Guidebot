"""Validation-gated skill evolution inspired by SkillOpt."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol, Sequence
from uuid import uuid4

from .models import Trajectory


class ProposalStatus(str, Enum):
    PROPOSED = "proposed"
    REJECTED = "rejected"
    VALIDATED = "validated"
    APPROVED = "approved"


@dataclass(slots=True)
class SkillProposal:
    candidate_text: str
    rationale: str
    edits: tuple[str, ...]
    id: str = field(default_factory=lambda: uuid4().hex)
    status: ProposalStatus = ProposalStatus.PROPOSED
    baseline_score: float | None = None
    candidate_score: float | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SkillOptimizer(Protocol):
    async def propose(self, skill: str, trajectories: Sequence[Trajectory]) -> SkillProposal: ...


class SkillEvaluator(Protocol):
    async def score(self, skill: str, trajectories: Sequence[Trajectory]) -> float: ...


class EvolutionGate:
    """Accepts bounded, measurable improvements; activation remains explicit."""

    FORBIDDEN = ("bypass safety", "disable safety", "ignore safety policy", "扩大设备权限")

    def __init__(self, max_edits: int = 4, max_growth_chars: int = 1200) -> None:
        self.max_edits = max_edits
        self.max_growth_chars = max_growth_chars

    async def validate(
        self,
        current_skill: str,
        proposal: SkillProposal,
        evaluator: SkillEvaluator,
        held_out: Sequence[Trajectory],
    ) -> bool:
        lowered = proposal.candidate_text.lower()
        bounded = (
            len(proposal.edits) <= self.max_edits
            and len(proposal.candidate_text) - len(current_skill) <= self.max_growth_chars
            and not any(term in lowered for term in self.FORBIDDEN)
        )
        if not bounded:
            proposal.status = ProposalStatus.REJECTED
            return False

        proposal.baseline_score = await evaluator.score(current_skill, held_out)
        proposal.candidate_score = await evaluator.score(proposal.candidate_text, held_out)
        improved = proposal.candidate_score > proposal.baseline_score
        proposal.status = ProposalStatus.VALIDATED if improved else ProposalStatus.REJECTED
        return improved

    @staticmethod
    def approve(proposal: SkillProposal, skill_path: Path) -> None:
        if proposal.status is not ProposalStatus.VALIDATED:
            raise ValueError("only validated proposals can be approved")
        skill_path.write_text(proposal.candidate_text, encoding="utf-8")
        proposal.status = ProposalStatus.APPROVED


class EvolutionEngine:
    """Coordinates propose → validate → explicit approval and keeps audit history."""

    def __init__(
        self,
        skill_path: Path,
        optimizer: SkillOptimizer,
        evaluator: SkillEvaluator,
        gate: EvolutionGate | None = None,
    ) -> None:
        self.skill_path = skill_path
        self.optimizer = optimizer
        self.evaluator = evaluator
        self.gate = gate or EvolutionGate()
        self.proposals: list[SkillProposal] = []

    async def evolve(
        self,
        training: Sequence[Trajectory],
        held_out: Sequence[Trajectory],
    ) -> SkillProposal:
        current = self.skill_path.read_text(encoding="utf-8")
        proposal = await self.optimizer.propose(current, training)
        await self.gate.validate(current, proposal, self.evaluator, held_out)
        self.proposals.append(proposal)
        return proposal

    def approve(self, proposal_id: str) -> SkillProposal:
        proposal = next((item for item in self.proposals if item.id == proposal_id), None)
        if proposal is None:
            raise KeyError(f"unknown proposal: {proposal_id}")
        self.gate.approve(proposal, self.skill_path)
        return proposal
