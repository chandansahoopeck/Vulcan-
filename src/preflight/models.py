class PreflightError(RuntimeError):
    """
    Raised when mandatory preflight checks fail.
    Used by scheduler / main to block business logic.
    """
    pass



from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CheckResult:
    name: str                 # Check name (e.g. SERVICENOW, CYBERARK)
    mandatory: bool           # True if required to proceed
    enabled: bool             # False = SKIP
    status: str               # OK | FAIL | SKIP
    latency_ms: int           # End-to-end latency
    details: Dict[str, Any]   # Any diagnostic info


from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class PreflightReport:
    overall: str                  # OK | FAIL
    timestamp_ms: int
    results: List[CheckResult]

    def to_dict(self) -> dict:
        return {
            "overall": self.overall,
            "timestamp_ms": self.timestamp_ms,
            "results": [asdict(r) for r in self.results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


