from enum import Enum, unique


@unique
class ContentType(str, Enum):
    CYCLONEDX = "cyclonedx-json"
    CYCLONEDX_ATTEST = "attest-cyclonedx-json"
    CYCLONEDX_STATEMENT = "statement-cyclonedx-json"
    SLSA_ATTEST = "attest-slsa"
    SLSA_STATEMENT = "statement-slsa"
    SSDF = "ssdf"
    SCORECARD = "scorecard"
    POLICY_RUN = "policy-run"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]


@unique
class ContextType(str, Enum):
    OTHER = "other"
    LOCAL = "local"
    JENKINS = "jenkins"
    GITHUB = "github"
    CIRCLECI = "circleci"
    AZURE = "azure"
    GITLAB = "gitlab"
    TRAVIS = "travis"
    BITBUCKET = "bitbucket"
    SCORECARD = "scorecard"
    GITHUBAPP = "githubapp"
    SCRIBE = "scribe"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]


@unique
class EvidenceState(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    FAILED = "failed"
    REMOVED = "removed"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]


@unique
class SignatureStatus(str, Enum):
    IN_PROGRESS = "in-progress"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    UNSIGNED = "unsigned"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]
