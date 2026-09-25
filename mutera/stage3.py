"""Stage 3 ecosystem layer: species, predators, disease and climate events."""
from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, List

from .stage2 import Stage2Config, Stage2Simulation


@dataclass(frozen=True)
class Stage3Config(Stage2Config):
    species_count: int = 2
    predator_pressure: float = 0.08
    disease_pressure: float = 0.03
    climate_event_chance: float = 0.05
    climate_damage: float = 0.10

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.species_count < 1:
            raise ValueError("species_count must be positive")
        for value, name in (
            (self.predator_pressure, "predator_pressure"),
            (self.disease_pressure, "disease_pressure"),
            (self.climate_event_chance, "climate_event_chance"),
            (self.climate_damage, "climate_damage"),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass
class Species:
    id: str
    members: List[str] = field(default_factory=list)
    trophic_level: int = 1


@dataclass
class EcosystemStats:
    turn: int
    population: int
    species: int
    predators: int
    disease_cases: int
    climate_event: bool
    diversity: float


@dataclass
class Stage3Simulation(Stage2Simulation):
    config: Stage3Config = field(default_factory=Stage3Config)
    species: Dict[str, Species] = field(default_factory=dict)
    predator_ids: set[str] = field(default_factory=set)
    disease_ids: set[str] = field(default_factory=set)
    ecosystem_history: List[EcosystemStats] = field(default_factory=list)

    def seed(self, count=None):
        organisms = super().seed(count)
        self.species = {}
        self.predator_ids = set()
        self.disease_ids = set()
        for index, organism in enumerate(organisms):
            species_id = f"species-{index % self.config.species_count}"
            self.species.setdefault(species_id, Species(species_id))
            self.species[species_id].members.append(organism.id)
        return organisms

    def _assign_newborns(self, previous_ids: set[str]) -> None:
        for organism in self.organisms:
            if organism.id in previous_ids:
                continue
            species_id = f"species-{int(organism.id.split('-')[-1]) % self.config.species_count}"
            self.species.setdefault(species_id, Species(species_id)).members.append(organism.id)

    def _apply_ecosystem_pressure(self) -> tuple[int, bool]:
        living = [o for o in self.organisms if o.alive]
        disease_cases = 0
        climate_event = self.rng.random() < self.config.climate_event_chance
        self.disease_ids.clear()
        for organism in living:
            if self.rng.random() < self.config.disease_pressure:
                self.disease_ids.add(organism.id)
                organism.health = max(0.0, organism.health - 10.0)
                disease_cases += 1
            if climate_event:
                organism.health = max(0.0, organism.health * (1 - self.config.climate_damage))
            if self.rng.random() < self.config.predator_pressure:
                organism.energy = max(0.0, organism.energy - 12.0)
        return disease_cases, climate_event

    def step(self) -> EcosystemStats:
        previous_ids = {o.id for o in self.organisms}
        super().step()
        self._assign_newborns(previous_ids)
        disease_cases, climate_event = self._apply_ecosystem_pressure()
        living = [o for o in self.organisms if o.alive]
        for organism in living:
            if organism.health <= 0 or organism.energy <= 0:
                organism.alive = False
        living = [o for o in self.organisms if o.alive]
        # Rebuild species membership so dead organisms no longer count.
        for species in self.species.values():
            species.members = [oid for oid in species.members if any(o.id == oid and o.alive for o in self.organisms)]
        predators = len(self.predator_ids)
        result = EcosystemStats(
            turn=self.turn,
            population=len(living),
            species=sum(bool(s.members) for s in self.species.values()),
            predators=predators,
            disease_cases=disease_cases,
            climate_event=climate_event,
            diversity=self.diversity(),
        )
        self.ecosystem_history.append(result)
        return result

    def ecosystem_snapshot(self) -> Dict[str, object]:
        return {
            "turn": self.turn,
            "population": sum(o.alive for o in self.organisms),
            "species": {
                sid: {"members": list(species.members), "trophic_level": species.trophic_level}
                for sid, species in self.species.items() if species.members
            },
            "disease_cases": len(self.disease_ids),
            "history": [entry.__dict__.copy() for entry in self.ecosystem_history],
        }
