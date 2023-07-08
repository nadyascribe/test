from enum import Enum, unique


@unique
class RegistryImageState(str, Enum):
    UNPROCESSED = "unprocessed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    PROCESSED = "processed"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]
