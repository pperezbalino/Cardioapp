"""Provider boundary. Only a local simulation exists; no networking or secrets."""
from dataclasses import dataclass
from typing import Protocol

from clinical_case import FIELD_SPECS
from integrated_engine import checked, evaluate


@dataclass(frozen=True)
class ProviderRequest:
    mode: str
    confirmed_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    score_statuses: tuple[tuple[str, str], ...]
    # No alias, free text, identifiers or clinical values in the simulation contract.


@dataclass(frozen=True)
class ProviderResponse:
    provider_id: str
    simulated: bool
    missing_fields: tuple[str, ...]
    inference: tuple[str, ...] = ()
    model_calls: int = 0
    cost_usd: float = 0.0


class CopilotProvider(Protocol):
    def assess(self, request: ProviderRequest) -> ProviderResponse: ...


class SimulatedProvider:
    def assess(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse('local-simulation-v1', True, request.missing_fields)


def simulate(context, case):
    checked(context, case)
    confirmed = tuple(s.key for s in FIELD_SPECS if case.facts.get(s.key)
                      and case.facts[s.key].confirmed and case.facts[s.key].value is not None)
    missing = tuple(s.key for s in FIELD_SPECS if s.key not in confirmed)
    request = ProviderRequest(case.mode, confirmed, missing,
                              tuple((s.algorithm_id, s.status) for s in evaluate(context, case)))
    return SimulatedProvider().assess(request)
