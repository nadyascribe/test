"""
Osint schema models.
"""
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    text,
    ForeignKey,
    Enum,
    Boolean,
    Computed,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

from dags.domain.attestations import (
    ContentType as ContentTypeEnum,
    EvidenceState as EvidenceStateEnum,
    SignatureStatus as SignatureStatusEnum,
)
from dags.domain.advisory import AdvisoryType as AdvisoryTypeEnum
from dags.domain.regscan import RegistryImageState
from dags.storage.models.base import Base


class EvidenceState(Base):
    __tablename__ = "EvidenceState"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="EvidenceState_pkey"),
        {"schema": "osint"},
    )

    enum = Column(
        Enum(*EvidenceStateEnum.values(), native_enum=False),
        nullable=False,
    )


class SignatureStatus(Base):
    __tablename__ = "SignatureStatus"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="SignatureStatus_pkey"),
        {"schema": "osint"},
    )

    enum = Column(
        Enum(*SignatureStatusEnum.values(), native_enum=False),
        nullable=False,
    )


class TargetType(Base):
    __tablename__ = "TargetType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="TargetType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Text)
    label = Column(Text)
    txt = Column(TSVECTOR, Computed("to_tsvector('simple', label)"))


class AdvisoryType(Base):
    __tablename__ = "AdvisoryType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="AdvisoryType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Enum(*AdvisoryTypeEnum.values(), native_enum=False, validate_strings=True))


class ComponentType(Base):
    __tablename__ = "ComponentType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="ComponentType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Text)
    label = Column(Text)
    txt = Column(TSVECTOR, Computed("to_tsvector('simple', label)"))


class ContentType(Base):
    __tablename__ = "ContentType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="ContentType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Enum(*ContentTypeEnum.values(), native_enum=False, validate_strings=True))
    label = Column(Text)
    txt = Column(TSVECTOR, Computed("to_tsvector('simple', label)"))


class ContextType(Base):
    __tablename__ = "ContextType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="ContextType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Text)
    label = Column(Text)
    txt = Column(TSVECTOR, Computed("to_tsvector('simple', label)"))


class Vulnerability(Base):
    __tablename__ = "Vulnerability"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Vulnerability_pkey"),
        Index("Vulnerability_cvssScore_key", "cvssScore"),
        Index("Vulnerability_epssProbability_key", "epssProbability"),
        Index("Vulnerability_publishedOn_key", "publishedOn"),
        Index("Vulnerability_severity_key", "severity"),
        Index("Vulnerability_txt_key", "txt"),
        {"schema": "osint"},
    )

    id = Column(Text)
    publishedOn = Column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))
    severity = Column(Integer, nullable=False)
    cvssScore = Column(Float)
    epssProbability = Column(Float)
    txt = Column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple', id
        || ' ' || replace(id, '-', ' ') || ' ' || coalesce("cvssScore"::TEXT, '')
        || coalesce(ROUND("epssProbability" * 100)::text, ''))""",
            persisted=True,
        ),
    )


class PipelineRun(Base):
    __tablename__ = "PipelineRun"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="PipelineRun_pkey"),
        Index("PipelineRun_product_idx", "productKey"),
        Index("PipelineRun_version_idx", "version"),
        Index("PipelineRun_timestamp_idx", "timestamp"),
        Index("PipelineRun_team_idx", "team"),
        Index("PipelineRun_deleted_idx", "deleted"),
        Index("PipelineRun_pipelineName_idx", "pipelineName"),
        Index("PipelineRun_pipelineRun_idx", "pipelineRun"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    productKey = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    team = Column(BigInteger, nullable=False)
    deleted = Column(Boolean, server_default=text("false"))
    pipelineRun = Column(Text, nullable=False)
    pipelineName = Column(Text, nullable=False)
    context = Column(JSONB, nullable=True)


class Attestation(Base):
    __tablename__ = "Attestation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Attestation_pkey"),
        Index("Attestation_contentType_key", "contentType"),
        Index("Attestation_contextType_key", "contextType"),
        Index("Attestation_context_key", "context", postgresql_using="gin"),
        Index("Attestation_license_key", "license"),
        Index("Attestation_teamId_key", "teamId"),
        Index("Attestation_pipelineRun_key", "pipelineRun"),
        Index("Attestation_timestamp_key", "timestamp"),
        Index("Attestation_txt_key", "txt", postgresql_using="gin"),
        Index("Attestation_userId_key", "userId"),
        Index("Attestation_state_key", "state"),
        Index("Attestation_targetName_key", "targetName"),
        Index("Attestation_targetType_key", "targetType"),
        Index("Attestation_deleted_key", "deleted"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    contentType: ContentTypeEnum = Column(
        ForeignKey(ContentType.enum, name="Attestation_contentType_fkey"),
        nullable=False,
    )
    contextType: str = Column(
        ForeignKey(ContextType.enum, name="Attestation_contextType_fkey"),
        nullable=False,
    )
    context = Column(JSONB, nullable=False)
    key = Column(Text)
    timestamp = Column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))
    userId = Column(BigInteger)
    teamId = Column(BigInteger)
    state = Column(
        ForeignKey(EvidenceState.enum, name="Attestation_state_fkey"),
        server_default=EvidenceStateEnum.CREATED,
        nullable=False,
    )
    targetType = Column(ForeignKey(TargetType.enum, name="Attestation_targetType_fkey"), nullable=False)
    targetName = Column(Text, nullable=False)
    alerted = Column(Boolean, server_default=text("false"))
    deleted = Column(Boolean, server_default=text("false"))
    sigStatus = Column(ForeignKey(SignatureStatus.enum, name="Attestation_sigStatus_fkey"))
    license = Column(Text)
    job_ids = Column(Text, nullable=False, server_default="{}")
    txt = Column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple', "contentType" || ' ' || "contextType" || ' ' || context::text || ' ' || coalesce(key, '') || ' ' || coalesce(license, ''))""",
            persisted=True,
        ),
    )
    pipelineRun = Column(ForeignKey(PipelineRun.id, name="Attestation_pipelineRun_fkey"), nullable=False)
    project = Column(Text, Computed("context->>'project'", persisted=True), nullable=True)
    logical_app = Column(Text, nullable=True)
    logical_app_version = Column(Text, nullable=True)
    tool = Column(Text, nullable=True)


class Component(Base):
    __tablename__ = "Component"
    __table_args__ = (
        Index("Component_attestation_key", "mainAttestation"),
        Index("Component_purl_teamId_key", "purl", "teamId", unique=True),
        Index("Component_cpes_key", "cpes"),
        Index("Component_group_key", "group"),
        Index("Component_license_key", "licenses"),
        Index("Component_name_key", "name"),
        Index("Component_txt_key", "txt"),
        Index("Component_type_key", "type"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )

    purl = Column(Text, nullable=False)
    type: str = Column(Text, nullable=False)
    cpes = Column(ARRAY(Text()), nullable=False)
    group = Column(
        ForeignKey(ComponentType.enum, name="Component_group_fkey", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    teamId = Column(BigInteger, nullable=False, server_default="0")
    mainAttestation: int = Column(ForeignKey(Attestation.id, name="Component_attestation_key", ondelete="CASCADE"))
    info = Column(JSONB)
    extraIdx = Column(ARRAY(BigInteger()))
    licenses = Column(JSONB)
    txt = Column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple',
                    purl || ' ' || name || ' ' || coalesce(info, '{}')::text || ' ' || array_dims(licenses)
            )
        )""",
            persisted=True,
        ),
    )
    version = Column(Text, Computed("(info ->> 'version'::text)", persisted=True), nullable=True)


class AttestationComponent(Base):
    __tablename__ = "AttestationComponent"
    __table_args__ = (
        ForeignKeyConstraint(
            ["attestation"],
            [Attestation.id],
            name="AttestationComponent_attestation_fkey",
        ),
        ForeignKeyConstraint(
            ["component"],
            [Component.id],
            name="AttestationComponent_component_fkey",
        ),
        PrimaryKeyConstraint("attestation", "component", name="AttestationComponent_pkey"),
        Index("AttestationComponent_component_key", "component"),
        {"schema": "osint"},
    )

    attestation = Column(BigInteger, nullable=False)
    component = Column(Text, nullable=False)
    info = Column(JSONB)


class VulComponent(Base):
    __tablename__ = "VulComponent"
    __table_args__ = (
        PrimaryKeyConstraint("component", "vulId", "created", name="VulComponent_pkey"),
        Index("VulComponent_created_deleted", "created", "deleted"),
        Index("VulComponent_deleted", "deleted"),
        {"schema": "osint"},
    )

    component: str = Column(ForeignKey(Component.id, name="VulComponent_component_fkey"), nullable=False)
    vulId: str = Column(ForeignKey(Vulnerability.id, name="VulComponent_vulId_fkey"), nullable=False)
    created: DateTime = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    deleted: DateTime = Column(DateTime(True), nullable=True)
    fixedInVersion = Column(Text)
    txt = Column(
        TSVECTOR,
        Computed("""to_tsvector('simple', "fixedInVersion"::text)""", persisted=True),
    )


class VulAdvisory(Base):
    __tablename__ = "vul_advisory"
    __table_args__ = (
        Index(
            "VulAdvisory_vulId_source_lastModified",
            "vul_id",
            "source",
            "lastModified",
            unique=True,
        ),
        Index("VulAdvisory_source_key", "source"),
        Index("VulAdvisory_lastModified_key", "lastModified"),
        Index("VulAdvisory_vulId_key", "vul_id"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )

    vulId: str = Column(
        "vul_id",
        ForeignKey(Vulnerability.id, name="VulAdvisory_vulId_fkey"),
        nullable=False,
    )
    source: AdvisoryTypeEnum = Column(ForeignKey(AdvisoryType.enum, name="VulAdvisory_source_fkey"), nullable=False)
    lastModified = Column(DateTime(True), nullable=True, server_default=text("CURRENT_TIMESTAMP"))
    publishedOn = Column(DateTime(True))
    hyperLinks = Column(ARRAY(Text()))
    vector = Column(Text)
    baseScore = Column(Float)
    advisoryText = Column(Text)
    cpes = Column(ARRAY(Text()), nullable=False)
    info = Column(JSONB)
    txt = Column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple', "source" || ' ' || coalesce("advisoryText", ''))""",
            persisted=True,
        ),
    )


class ComplianceType(Base):
    __tablename__ = "ComplianceType"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="ComplianceType_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Text)


class ComplianceRule(Base):
    __tablename__ = "ComplianceRule"
    __table_args__ = (
        ForeignKeyConstraint(["type"], [ComplianceType.enum], name="ComplianceRule_type_fkey"),
        PrimaryKeyConstraint("id", name="ComplianceRule_pkey"),
        Index("ComplianceRule_type_idx", "type"),
        Index("ComplianceRule_txt_key", "txt", postgresql_using="gin"),
        Index("ComplianceRule_type_ruleId", "type", "ruleId", unique=True),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    type = Column(Text, nullable=False)
    ruleName = Column(Text, nullable=False)
    ruleId = Column(Text)
    description = Column(Text)
    messagePass = Column(Text)
    messageFail = Column(Text)
    messageReview = Column(Text)
    messageOpen = Column(Text)
    messageInformational = Column(Text)
    messageNotApplicable = Column(Text)
    slsaLevel = Column(Integer)
    txt = Column(
        Text,
        Computed(
            """to_tsvector('simple',
                                "ruleName" || ' ' || description || ' ' || "type"
                                )""",
            persisted=True,
        ),
    )


class ComplianceStatus(Base):
    __tablename__ = "ComplianceStatus"
    __table_args__ = (
        PrimaryKeyConstraint("enum", name="ComplianceStatus_pkey"),
        {"schema": "osint"},
    )

    enum = Column(Text)
    label = Column(Text)
    txt = Column(TSVECTOR, Computed("to_tsvector('simple', label)", persisted=True))


class ComplianceRun(Base):
    __tablename__ = "ComplianceRun"
    __table_args__ = (
        ForeignKeyConstraint(["pipelineRun"], [PipelineRun.id], name="ComplianceRun_pipelineRun_fkey"),
        ForeignKeyConstraint(["rule"], [ComplianceRule.id], name="ComplianceRun_rule_fkey"),
        ForeignKeyConstraint(["status"], [ComplianceStatus.enum], name="ComplianceRun_status_fkey"),
        PrimaryKeyConstraint("id", name="ComplianceRun_pkey"),
        Index("ComplianceRun_message_idx", "message"),
        Index("ComplianceRun_pipeline_idx", "pipelineRun"),
        Index("ComplianceRun_status_idx", "status"),
        Index("ComplianceRun_txt_key", "txt", postgresql_using="gin"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    pipelineRun = Column(BigInteger, nullable=False)
    status = Column(Text, nullable=False)
    rule = Column(BigInteger, nullable=False)
    message = Column(Text, server_default=text("''::text"))
    info = Column(JSONB)
    attestations = Column(ARRAY(BigInteger()))
    txt = Column(
        TSVECTOR,
        Computed(
            """to_tsvector('simple', status || ' ' || message)""",
            persisted=True,
        ),
    )


class PackageToVersion(Base):
    __tablename__ = "PackageToVersion"
    __table_args__ = ({"schema": "osint"},)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    system = Column(Text)
    name = Column(Text, nullable=False)
    version = Column(Text)
    project_type = Column(Text)
    project_name = Column(Text)
    snapshotAt = Column(DateTime, nullable=False)


class Scorecard(Base):
    __tablename__ = "Scorecard"
    __table_args__ = ({"schema": "osint"},)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    repo_name = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    project_name = Column(Text, Computed("""substr(repo_name, (strpos(repo_name, '/'::text) + 1))""", persisted=True))
    extra = Column(JSONB)


class RegistryScanConfig(Base):
    __tablename__ = "RegistryScanConfig"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="RegistryScanConfig_pkey"),
        Index("RegistryScanConfig_teamId_idx", "teamId"),
        Index("RegistryScanConfig_provider_idx", "provider"),
        Index("RegistryScanConfig_registry_url_idx", "registry_url"),
        CheckConstraint(
            """
                ("token" IS NULL AND "username" IS NOT NULL AND "password" IS NOT NULL) OR 
                ("token" IS NOT NULL AND "username" IS NULL AND "password" IS NULL)
            """
        ),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    teamId = Column(BigInteger, nullable=False)
    provider = Column(Text, nullable=False)
    registry_url = Column(Text, nullable=False)
    username = Column(Text)
    password = Column(Text)
    token = Column(Text)
    repos_filter = Column(JSONB, nullable=False, server_default=text("'{}'"))


class RegistryImage(Base):
    __tablename__ = "RegistryImage"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="RegistryImage_pkey"),
        Index("RegistryImage_image_id_idx", "image_id"),
        Index("RegistryImage_digest_idx", "digest"),
        Index("RegistryImage_repository_idx", "repository"),
        Index("RegistryImage_tag_idx", "tag"),
        Index("RegistryImage_layers_idx", "layers", postgresql_using="gin"),
        Index("RegistryImage_config_idx", "config", postgresql_using="gin"),
        Index("RegistryImage_registry_scan_config_idx", "registry_scan_config"),
        Index("RegistryImage_state_idx", "state"),
        Index("RegistryImage_is_base_image_idx", "is_base_image"),
        UniqueConstraint("digest", "tag", "repository", "registry_scan_config"),
        {"schema": "osint"},
    )

    id = Column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
    )
    image_id = Column(Text, nullable=False)
    digest = Column(Text, nullable=False)
    repository = Column(Text, nullable=False)
    tag = Column(Text, nullable=False)
    layers = Column(ARRAY(Text()), nullable=False)
    config = Column(JSONB, nullable=False)
    registry_scan_config = Column(
        ForeignKey(RegistryScanConfig.id, name="RegistryImage_registry_scan_config_idx"),
        nullable=False,
    )
    state = Column(
        Enum(*RegistryImageState.values(), native_enum=False, validate_strings=True),
        nullable=False,
        server_default=text(RegistryImageState.UNPROCESSED),
    )
    is_base_image = Column(Boolean)
