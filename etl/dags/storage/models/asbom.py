from sqlalchemy import (
    PrimaryKeyConstraint,
    select,
    func,
    Column,
    BigInteger,
    Integer,
    cast,
    ARRAY,
    and_,
    Text,
    UniqueConstraint,
    NUMERIC,
)
from alembic_utils.pg_materialized_view import PGMaterializedView

from dags.storage import Base
from dags.storage.sqla_utils import compile_query, jsonb_array_to_string
from dags.storage.models.osint import (
    Component,
    Vulnerability,
    VulComponent,
    PackageToVersion,
    Attestation,
    Scorecard,
    AttestationComponent,
    VulAdvisory,
)


class ComponentVulnerabilities(Base):
    __tablename__ = "ComponentVulnerabilities"
    __table_args__ = (
        # sqlalchemy requires to have a primary key, but the pkey actually doesn't exist in the db
        PrimaryKeyConstraint("component_id"),
        # we must have unique constraint because it's a requirement of "refresh materialized view concurrently"
        UniqueConstraint("component_id"),
        {"schema": "osint", "info": {"skip_autogenerate": True}},
    )
    __materialized_view__ = (
        select(
            Component.id.label("component_id"),
            func.count(1).filter(Vulnerability.severity >= 4).label("severity_gte_4"),
        )
        .join(VulComponent, VulComponent.component == Component.id)
        .join(Vulnerability, Vulnerability.id == VulComponent.vulId)
        .group_by(Component.id)
    )
    component_id = Column(BigInteger)
    severity_gte_4 = Column(Integer)


class LatestPackageVersions(Base):
    __tablename__ = "LatestPackageVersions"
    __table_args__ = (
        # sqlalchemy requires to have a primary key, but the pkey actually doesn't exist in the db
        PrimaryKeyConstraint("name", "project_name", "system"),
        # we must have unique constraint because it's a requirement of "refresh materialized view concurrently"
        UniqueConstraint("name", "project_name", "system"),
        {"schema": "osint", "info": {"skip_autogenerate": True}},
    )
    _cte = (
        select(
            PackageToVersion.name,
            PackageToVersion.project_name,
            PackageToVersion.system,
            func.max(cast(func.regexp_split_to_array(PackageToVersion.version, "\."), ARRAY(Integer()))).label(
                "version_array"
            ),
        )
        .where(PackageToVersion.version.regexp_match("^\d{1,8}(\.\d{1,8})*$"))
        .group_by(
            PackageToVersion.name,
            PackageToVersion.project_name,
            PackageToVersion.system,
        )
        .cte()
    )

    _subq = (
        select(func.max(_cte.c.version_array).label("max"), _cte.c.name, _cte.c.system)
        .group_by(_cte.c.name, _cte.c.system)
        .subquery()
    )

    __materialized_view__ = select(
        _cte.c.name,
        _cte.c.project_name,
        _cte.c.system,
        _cte.c.version_array,
        func.array_to_string(_cte.c.version_array, ".").label("version"),
    ).join(
        _subq,
        onclause=and_(
            _subq.c.name == _cte.c.name, _subq.c.system == _cte.c.system, _subq.c.max == _cte.c.version_array
        ),
    )
    name = Column(Text)
    project_name = Column(Text)
    system = Column(Text)
    version_array = Column(ARRAY(Integer()))
    version = Column(Text)


class AggregatedSbom(Base):
    __tablename__ = "AggregatedSbom"
    __table_args__ = (
        # sqlalchemy requires to have a primary key, but the pkey actually doesn't exist in the db
        PrimaryKeyConstraint("attestation_id", "component_id", name="pkey"),
        # we must have unique constraint because it's a requirement of "refresh materialized view concurrently"
        UniqueConstraint("attestation_id", "component_id", name="pkey"),
        {"schema": "osint", "info": {"skip_autogenerate": True}},
    )
    __materialized_view__ = (
        select(
            Attestation.logical_app,
            Attestation.logical_app_version,
            Attestation.context["input_tag"].astext,
            Attestation.targetName,
            Attestation.targetType,
            Attestation.tool,
            Attestation.id.label("attestation_id"),
            Component.id.label("component_id"),
            jsonb_array_to_string(Attestation.context["labels"], "labels"),
            Component.name,
            Component.version,
            Component.group,
            select(Scorecard.score)
            .where(Scorecard.project_name == LatestPackageVersions.project_name)
            .scalar_subquery()
            .label("scorecard"),
            func.coalesce(
                select(ComponentVulnerabilities.severity_gte_4)
                .where(ComponentVulnerabilities.component_id == Component.id)
                .subquery(),
                0,
            ).label("high_severity_cves"),
            jsonb_array_to_string(Component.licenses, "licenses"),
            (LatestPackageVersions.version <= Component.version).label("version_is_up_to_date"),
        )
        .select_from(
            Attestation.__table__.join(AttestationComponent, Attestation.id == AttestationComponent.attestation)
            .join(Component, Component.id == AttestationComponent.component)
            .join(
                LatestPackageVersions,
                func.lower(Component.name) == func.lower(LatestPackageVersions.name),
                isouter=True,
            )
        )
        .where(Component.group.not_in(["file", "deb", "layer", "syft"]))
    )

    attestation_id = Column(BigInteger)
    component_id = Column(BigInteger)


class CveImpact(Base):
    __tablename__ = "CveImpact"
    __table_args__ = (
        # sqlalchemy requires to have a primary key, but the pkey actually doesn't exist in the db
        PrimaryKeyConstraint("attestation_id", "component_id", "vulnerability_id"),
        # we must have unique constraint because it's a requirement of "refresh materialized view concurrently"
        UniqueConstraint("attestation_id", "component_id", "vulnerability_id"),
        {"schema": "osint", "info": {"skip_autogenerate": True}},
    )
    __materialized_view__ = (
        select(
            Vulnerability.id.label("vulnerability_id"),
            Vulnerability.severity.label("severity"),
            Attestation.id.label("attestation_id"),
            Attestation.logical_app,
            Attestation.logical_app_version,
            Attestation.context["input_tag"].astext,
            Attestation.targetName,
            Component.id.label("component_id"),
            Component.name,
            Component.version,
            jsonb_array_to_string(Attestation.context["labels"], "labels"),
            LatestPackageVersions.version.label("latest_package_version"),
            Vulnerability.cvssScore,
            func.round(cast(Vulnerability.epssProbability * 100, NUMERIC), 6).label("epssProbability"),
            Vulnerability.publishedOn,
            VulAdvisory.hyperLinks,
            VulAdvisory.source,
        )
        .select_from(
            Attestation.__table__.join(AttestationComponent, Attestation.id == AttestationComponent.attestation)
            .join(Component, Component.id == AttestationComponent.component)
            .join(VulComponent, Component.id == VulComponent.component)
            .join(Vulnerability, Vulnerability.id == VulComponent.vulId)
            .join(VulAdvisory, VulAdvisory.vulId == Vulnerability.id)
            .join(
                LatestPackageVersions,
                func.lower(Component.name) == func.lower(LatestPackageVersions.name),
                isouter=True,
            )
        )
        .where(Component.group.not_in(["file", "deb", "layer", "syft"]))
    )

    vulnerability_id = Column(BigInteger)
    component_id = Column(BigInteger)
    attestation_id = Column(BigInteger)


MAT_VIEWS = []

for ent in list(vars().values()):
    if hasattr(ent, "__materialized_view__"):
        schema = next((arg.get("schema") for arg in ent.__table_args__ if isinstance(arg, dict)), "public")
        MAT_VIEWS.append(
            PGMaterializedView(
                schema=schema,
                signature=ent.__tablename__,
                definition=compile_query(ent.__materialized_view__),
                with_data=False,
            )
        )
