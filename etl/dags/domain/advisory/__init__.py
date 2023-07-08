from __future__ import annotations
from enum import Enum, unique


@unique
class AdvisoryType(str, Enum):
    NVD31 = "NVD3.1"
    NVD30 = "NVD3"
    NVD2 = "NVD2"
    OSV = "OSV"
    GHSA = "GHSA"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]


@unique
class Severity(int, Enum):
    CRITICAL = 10
    HIGH = 8
    MEDIUM = 5
    LOW = 2
    UNKNOWN = 1
    NEGLIGIBLE = -1
    NONE = 0

    @classmethod
    def from_str(cls, value: str) -> Severity:
        return cls[value.upper()]
