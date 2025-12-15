# rules.py
#
# Lattice-agnostic rule helpers.

from __future__ import annotations

from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class Rule:
    birth: Set[int]
    survive: Set[int]

    def to_bs_string(self, N: int) -> str:
        """
        Format the rule as B*/S*, only including counts up to N.
        """
        b = "".join(str(v) for v in sorted(x for x in self.birth if x <= N))
        s = "".join(str(v) for v in sorted(x for x in self.survive if x <= N))
        return f"B{b}/S{s}"

    @staticmethod
    def random(N: int, p_birth: float, p_survive: float, rng) -> "Rule":
        """
        Sample a random rule with independent inclusion probabilities.
        """
        birth = {i for i in range(N + 1) if rng.random() < p_birth}
        survive = {i for i in range(N + 1) if rng.random() < p_survive}
        return Rule(birth=birth, survive=survive)

    def mutate(self, N: int, rate: float, rng) -> "Rule":
        """
        Flip bits with probability 'rate' for each neighbor count up to N.
        """
        birth = set(self.birth)
        survive = set(self.survive)

        for i in range(N + 1):
            if rng.random() < rate:
                if i in birth:
                    birth.remove(i)
                else:
                    birth.add(i)
            if rng.random() < rate:
                if i in survive:
                    survive.remove(i)
                else:
                    survive.add(i)

        return Rule(birth=birth, survive=survive)
