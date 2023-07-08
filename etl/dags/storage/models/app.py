"""
App schema models.
May be not synchronized with the actual schema.

Migrations must be applied only by scribehub.
"""
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Computed,
    DateTime,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AdvisoryJustificationEnum(Base):
    __tablename__ = "AdvisoryJustificationEnum"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="AdvisoryJustificationEnum_pkey"),
        {"schema": "app"},
    )

    id = Column(BigInteger)
    name = Column(Text, nullable=False)
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, COALESCE(name, ''::text))", persisted=True),
    )


class AdvisoryStatusEnum(Base):
    __tablename__ = "AdvisoryStatusEnum"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="AdvisoryStatusEnum_pkey"),
        {"schema": "app"},
    )

    id = Column(BigInteger)
    name = Column(Text, nullable=False)
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, COALESCE(name, ''::text))", persisted=True),
    )


class CustomVulnerabilityAdvisory(Base):
    __tablename__ = "CustomVulnerabilityAdvisory"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="CustomVulnerabilityAdvisory_pkey"),
        Index("CustomVulnerabilityAdvisory_fts_idx", "fts"),
        {"schema": "app"},
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
    pipelineRunId = Column(BigInteger, nullable=False)
    vulnerabilityId = Column(Text, nullable=False)
    componentId = Column(BigInteger, nullable=False)
    advisoryText = Column(Text)
    advisoryStatus = Column(Integer)
    advisoryJustification = Column(Integer)
    advisoryLastModified = Column(DateTime(True))
    advisoryResponse = Column(JSONB)
    severity = Column(Integer)
    fts = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple'::regconfig, COALESCE(\"advisoryText\", ''::text))",
            persisted=True,
        ),
    )


class DemoProduct(Base):
    __tablename__ = "DemoProduct"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="DemoProduct_pkey"),
        UniqueConstraint("productId", "type", name="unique_demoproduct_productid_type"),
        {"schema": "app"},
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
    productId = Column(BigInteger, nullable=False)
    type = Column(Text, nullable=False)


t_PipelineRunAttestationStats = Table(
    "PipelineRunAttestationStats",
    metadata,
    Column("id", BigInteger),
    Column("componentCount", BigInteger),
    Column("layerCount", BigInteger),
    Column("signatureStatus", Text),
    Column("operatingSystem", Text),
    Column("licenseCount", BigInteger),
    Column("fts", TSVECTOR),
    schema="app",
)


t_PipelineRunComplianceStats = Table(
    "PipelineRunComplianceStats",
    metadata,
    Column("id", BigInteger),
    Column("slsaCompliant", BigInteger),
    Column("slsaNotCompliant", BigInteger),
    Column("slsaLevel1Compliant", BigInteger),
    Column("slsaLevel1NotCompliant", BigInteger),
    Column("slsaLevel2Compliant", BigInteger),
    Column("slsaLevel2NotCompliant", BigInteger),
    Column("slsaLevel3Compliant", BigInteger),
    Column("slsaLevel3NotCompliant", BigInteger),
    Column("slsaLevel4Compliant", BigInteger),
    Column("slsaLevel4NotCompliant", BigInteger),
    Column("ssdfCompliant", BigInteger),
    Column("ssdfNotCompliant", BigInteger),
    schema="app",
)


t_PipelineRunLicense = Table(
    "PipelineRunLicense",
    metadata,
    Column("pipelineRun", BigInteger),
    Column("name", Text),
    Column("count", BigInteger),
    Column("fts", TSVECTOR),
    schema="app",
)


class PipelineRunPublish(Base):
    __tablename__ = "PipelineRunPublish"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="PipelineRunStats_pkey"),
        Index("PipelineRunPublish_fts_idx", "fts"),
        {"schema": "app"},
    )

    id = Column(BigInteger)
    published = Column(Boolean, nullable=False)
    publishedOn = Column(DateTime(True))
    fts = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple'::regconfig,\nCASE\n    WHEN (published = true) THEN 'published'::text\n    ELSE ''::text\nEND)",
            persisted=True,
        ),
    )


t_PipelineRunVulnerabilityStats = Table(
    "PipelineRunVulnerabilityStats",
    metadata,
    Column("id", BigInteger),
    Column("criticalVulnerabilitiesCount", BigInteger),
    Column("highVulnerabilitiesCount", BigInteger),
    Column("mediumVulnerabilitiesCount", BigInteger),
    Column("lowVulnerabilitiesCount", BigInteger),
    schema="app",
)


class Plan(Base):
    __tablename__ = "Plan"
    __table_args__ = (PrimaryKeyConstraint("id", name="Plan_pkey"), {"schema": "app"})

    id = Column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
    )
    name = Column(Text, nullable=False)
    type = Column(Integer, nullable=False)
    seats = Column(Integer, nullable=False)
    retentionMonths = Column(Integer, nullable=False)
    buildsPerMonth = Column(Integer, nullable=False)
    blueSnapStoreId = Column(BigInteger)
    blueSnapSkuMonthly = Column(BigInteger)
    blueSnapSkuAnnual = Column(BigInteger)


class ProductStats(Base):
    __tablename__ = "ProductStats"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="ProductStats_pkey"),
        {"schema": "app"},
    )

    id = Column(BigInteger)
    lastPipelineRun = Column(BigInteger)
    lastPublishedPipelineRun = Column(BigInteger)
    pipelineRunCount = Column(Integer)
    publishedPipelineRunCount = Column(Integer)
    subscriptionCount = Column(Integer)


class Team(Base):
    __tablename__ = "Team"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Team_pkey"),
        Index("Team_clientId_idx", "clientId"),
        Index("Team_fts_idx", "fts"),
        Index("Team_gitHubAppInstallationId_idx", "gitHubAppInstallationId"),
        {"schema": "app"},
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
    name = Column(Text, nullable=False)
    clientId = Column(Text)
    gitHubAppInstallationId = Column(BigInteger)
    gitHubAppInstallationActive = Column(Boolean)
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, COALESCE(name, ''::text))", persisted=True),
    )


class User(Base):
    __tablename__ = "User"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="User_pkey"),
        UniqueConstraint("email", name="unique_user_email"),
        Index("User_email_idx", "email"),
        Index("User_fts_idx", "fts"),
        {"schema": "app"},
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
    email = Column(Text, nullable=False)
    name = Column(Text)
    lastAccess = Column(DateTime(True))
    settings = Column(JSONB)
    fts = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple'::regconfig, ((COALESCE(name, ''::text) || ' '::text) || COALESCE(email, ''::text)))",
            persisted=True,
        ),
    )


class VulnerabilitySeverityEnum(Base):
    __tablename__ = "VulnerabilitySeverityEnum"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="VulnerabilitySeverityEnum_pkey"),
        {"schema": "app"},
    )

    id = Column(BigInteger)
    name = Column(Text, nullable=False)
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, COALESCE(name, ''::text))", persisted=True),
    )


class FlywaySchemaHistory(Base):
    __tablename__ = "flyway_schema_history"
    __table_args__ = (
        PrimaryKeyConstraint("installed_rank", name="flyway_schema_history_pk"),
        Index("flyway_schema_history_s_idx", "success"),
        {"schema": "app"},
    )

    installed_rank = Column(Integer)
    description = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)
    script = Column(String(1000), nullable=False)
    installed_by = Column(String(100), nullable=False)
    installed_on = Column(DateTime, nullable=False, server_default=text("now()"))
    execution_time = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    version = Column(String(50))
    checksum = Column(Integer)


class Shedlock(Base):
    __tablename__ = "shedlock"
    __table_args__ = (
        PrimaryKeyConstraint("name", name="shedlock_pkey"),
        {"schema": "app"},
    )

    name = Column(String(64))
    lock_until = Column(DateTime, nullable=False)
    locked_at = Column(DateTime, nullable=False)
    locked_by = Column(String(255), nullable=False)


class Label(Base):
    __tablename__ = "Label"
    __table_args__ = (
        ForeignKeyConstraint(["teamId"], ["app.Team.id"], name="Label_teamId_fkey"),
        PrimaryKeyConstraint("id", name="Label_pkey"),
        UniqueConstraint("teamId", "name", name="Label_teamId_name_key"),
        Index("Label_fts_idx", "fts"),
        {"schema": "app"},
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
    type = Column(Integer, nullable=False)
    name = Column(String(20))
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, (name)::text)", persisted=True),
    )


class Product(Base):
    __tablename__ = "Product"
    __table_args__ = (
        ForeignKeyConstraint(["teamId"], ["app.Team.id"], name="Product_teamId_fkey"),
        PrimaryKeyConstraint("id", name="Product_pkey"),
        UniqueConstraint("key", name="unique_product_key"),
        Index("Product_fts_idx", "fts"),
        Index("Product_key_idx", "key"),
        Index("Product_team_idx", "teamId"),
        {"schema": "app"},
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
    name = Column(Text, nullable=False)
    teamId = Column(BigInteger, nullable=False)
    key = Column(Text, nullable=False)
    userDefinedKey = Column(Text)
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple'::regconfig, COALESCE(name, ''::text))", persisted=True),
    )


class TeamInvite(Base):
    __tablename__ = "TeamInvite"
    __table_args__ = (
        ForeignKeyConstraint(["teamId"], ["app.Team.id"], name="TeamInvite_teamId_fkey"),
        ForeignKeyConstraint(["userId"], ["app.User.id"], name="TeamInvite_userId_fkey"),
        PrimaryKeyConstraint("teamId", "userId", name="TeamInvite_pkey"),
        Index("TeamInvite_fts_idx", "fts"),
        Index("TeamInvite_teamId_idx", "teamId"),
        Index("TeamInvite_team_idx", "userId"),
        {"schema": "app"},
    )

    userId = Column(BigInteger, nullable=False)
    teamId = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))
    isAdmin = Column(Boolean, server_default=text("false"))
    fts = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple'::regconfig,\nCASE\n    WHEN (\"isAdmin\" = true) THEN 'admin'::text\n    ELSE 'member'::text\nEND)",
            persisted=True,
        ),
    )


class TeamPlan(Base):
    __tablename__ = "TeamPlan"
    __table_args__ = (
        ForeignKeyConstraint(["planId"], ["app.Plan.id"], name="TeamPlan_planId_fkey"),
        ForeignKeyConstraint(["teamId"], ["app.Team.id"], name="TeamPlan_teamId_fkey"),
        PrimaryKeyConstraint("teamId", "planId", name="TeamPlan_pkey"),
        UniqueConstraint("blueSnapLastInvoiceId", name="unique_teamplan_bluesnaplastinvoiceid"),
        UniqueConstraint(
            "blueSnapOriginalInvoiceId",
            name="unique_teamplan_bluesnaporiginalinvoiceid",
        ),
        UniqueConstraint("blueSnapSubscriptionId", name="unique_teamplan_bluesnapsubscriptionid"),
        Index("TeamPlan_planId_idx", "planId"),
        Index("TeamPlan_teamId_idx", "teamId"),
        {"schema": "app"},
    )

    teamId = Column(BigInteger, nullable=False)
    planId = Column(BigInteger, nullable=False)
    activeFrom = Column(DateTime(True), nullable=False)
    expiresOn = Column(DateTime(True))
    lastPaymentOn = Column(DateTime(True))
    blueSnapShopperId = Column(BigInteger)
    blueSnapSubscriptionId = Column(BigInteger)
    blueSnapOriginalInvoiceId = Column(BigInteger)
    blueSnapLastInvoiceId = Column(BigInteger)


class LabelAssignment(Base):
    __tablename__ = "LabelAssignment"
    __table_args__ = (
        ForeignKeyConstraint(["labelId"], ["app.Label.id"], name="LabelAssignment_labelId_fkey"),
        ForeignKeyConstraint(["productId"], ["app.Product.id"], name="LabelAssignment_productId_fkey"),
        PrimaryKeyConstraint("id", name="LabelAssignment_pkey"),
        {"schema": "app"},
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
    productId = Column(BigInteger, nullable=False)
    labelId = Column(BigInteger, nullable=False)


class Subscription(Base):
    __tablename__ = "Subscription"
    __table_args__ = (
        ForeignKeyConstraint(["productId"], ["app.Product.id"], name="Subscription_productId_fkey"),
        ForeignKeyConstraint(["userId"], ["app.User.id"], name="Subscription_userId_fkey"),
        PrimaryKeyConstraint("productId", "userId", name="Subscription_pkey"),
        Index("Subscription_productId_idx", "productId"),
        Index("Subscription_userId_idx", "userId"),
        {"schema": "app"},
    )

    userId = Column(BigInteger, nullable=False)
    productId = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))
    isHidden = Column(Boolean, server_default=text("false"))
    isAutoSubscribed = Column(Boolean, server_default=text("false"))
