create schema if not exists app;

create table if not exists app."User"
(
    id           bigint generated always as identity,
    name         text,
    email        text not null,
    "lastAccess" timestamp with time zone,
    settings     jsonb,
    fts          tsvector generated always as (to_tsvector('simple'::regconfig,
                                                           ((COALESCE(name, '') || ' ') ||
                                                            COALESCE(email, '')))) stored
);

create index if not exists "User_email_idx"
    on app."User" (email);

create index if not exists "User_fts_idx"
    on app."User" using gin (fts);

alter table app."User"
    add primary key (id);

alter table app."User"
    add constraint unique_user_email
        unique (email);

create table if not exists app."Team"
(
    id                            bigint generated always as identity,
    name                          text not null,
    "clientId"                    text,
    "gitHubAppInstallationId"     bigint,
    "gitHubAppInstallationActive" boolean,
    fts                           tsvector generated always as (to_tsvector('simple'::regconfig, COALESCE(name, ''))) stored
);

create index if not exists "Team_clientId_idx"
    on app."Team" ("clientId");

create index if not exists "Team_gitHubAppInstallationId_idx"
    on app."Team" ("gitHubAppInstallationId");

create index if not exists "Team_fts_idx"
    on app."Team" using gin (fts);

alter table app."Team"
    add primary key (id);

create table if not exists app."TeamInvite"
(
    "userId"  bigint not null,
    "teamId"  bigint not null,
    timestamp timestamp with time zone default CURRENT_TIMESTAMP,
    "isAdmin" boolean                  default false,
    fts       tsvector generated always as (to_tsvector('simple'::regconfig,
                                                        CASE
                                                            WHEN ("isAdmin" = true) THEN 'admin'
                                                            ELSE 'member'
                                                            END)) stored
);

create index if not exists "TeamInvite_teamId_idx"
    on app."TeamInvite" ("teamId");

create index if not exists "TeamInvite_team_idx"
    on app."TeamInvite" ("userId");

create index if not exists "TeamInvite_fts_idx"
    on app."TeamInvite" using gin (fts);

alter table app."TeamInvite"
    add primary key ("teamId", "userId");

alter table app."TeamInvite"
    add foreign key ("userId") references app."User";

alter table app."TeamInvite"
    add foreign key ("teamId") references app."Team";

create table if not exists app."Plan"
(
    id                   integer generated always as identity,
    name                 text    not null,
    type                 integer not null,
    seats                integer not null,
    "retentionMonths"    integer not null,
    "buildsPerMonth"     integer not null,
    "blueSnapStoreId"    bigint,
    "blueSnapSkuMonthly" bigint,
    "blueSnapSkuAnnual"  bigint
);

alter table app."Plan"
    add primary key (id);

create table if not exists app."TeamPlan"
(
    "teamId"                    bigint                   not null,
    "planId"                    bigint                   not null,
    "activeFrom"                timestamp with time zone not null,
    "expiresOn"                 timestamp with time zone,
    "lastPaymentOn"             timestamp with time zone,
    "blueSnapShopperId"         bigint,
    "blueSnapSubscriptionId"    bigint,
    "blueSnapOriginalInvoiceId" bigint,
    "blueSnapLastInvoiceId"     bigint
);

create index if not exists "TeamPlan_teamId_idx"
    on app."TeamPlan" ("teamId");

create index if not exists "TeamPlan_planId_idx"
    on app."TeamPlan" ("planId");

alter table app."TeamPlan"
    add primary key ("teamId", "planId");

alter table app."TeamPlan"
    add constraint unique_teamplan_bluesnapsubscriptionid
        unique ("blueSnapSubscriptionId");

alter table app."TeamPlan"
    add constraint unique_teamplan_bluesnaporiginalinvoiceid
        unique ("blueSnapOriginalInvoiceId");

alter table app."TeamPlan"
    add constraint unique_teamplan_bluesnaplastinvoiceid
        unique ("blueSnapLastInvoiceId");

alter table app."TeamPlan"
    add foreign key ("teamId") references app."Team";

alter table app."TeamPlan"
    add foreign key ("planId") references app."Plan";

create table if not exists app."Product"
(
    id               bigint generated always as identity,
    name             text   not null,
    "teamId"         bigint not null,
    key              text   not null,
    "userDefinedKey" text,
    fts              tsvector generated always as (to_tsvector('simple'::regconfig, COALESCE(name, ''))) stored
);

create index if not exists "Product_name_lower_idx"
    on app."Product" (lower(name));

create index if not exists "Product_team_idx"
    on app."Product" ("teamId");

create index if not exists "Product_key_idx"
    on app."Product" (key);

create index if not exists "Product_fts_idx"
    on app."Product" using gin (fts);

alter table app."Product"
    add primary key (id);

alter table app."Product"
    add constraint unique_product_key
        unique (key);

alter table app."Product"
    add foreign key ("teamId") references app."Team";

create table if not exists app."DemoProduct"
(
    id          bigint generated always as identity,
    "productId" bigint not null,
    type        text   not null
);

alter table app."DemoProduct"
    add primary key (id);

alter table app."DemoProduct"
    add constraint unique_demoproduct_productid_type
        unique ("productId", type);

create table if not exists app."Subscription"
(
    "userId"           bigint not null,
    "productId"        bigint not null,
    timestamp          timestamp with time zone default CURRENT_TIMESTAMP,
    "isHidden"         boolean                  default false,
    "isAutoSubscribed" boolean                  default false
);

create index if not exists "Subscription_userId_idx"
    on app."Subscription" ("userId");

create index if not exists "Subscription_productId_idx"
    on app."Subscription" ("productId");

alter table app."Subscription"
    add primary key ("productId", "userId");

alter table app."Subscription"
    add foreign key ("userId") references app."User";

alter table app."Subscription"
    add foreign key ("productId") references app."Product";

create table if not exists app."PipelineRunPublish"
(
    id                           bigint                not null,
    published                    boolean               not null,
    "publishedOn"                timestamp with time zone,
    fts                          tsvector generated always as (to_tsvector('simple'::regconfig,
                                                                           CASE
                                                                               WHEN (published = true) THEN 'published'
                                                                               ELSE ''
                                                                               END)) stored,
    "vulnerabilitiesPublished"   boolean default false not null,
    "vulnerabilitiesPublishedOn" timestamp with time zone
);

create index if not exists "PipelineRunPublish_fts_idx"
    on app."PipelineRunPublish" using gin (fts);

create index if not exists "PipelineRunPublish_vulnerabilitiesPublished"
    on app."PipelineRunPublish" ("vulnerabilitiesPublished");

create index if not exists "PipelineRunPublish_vulnerabilitiesPublishedOn"
    on app."PipelineRunPublish" ("vulnerabilitiesPublishedOn");

create index if not exists "PipelineRunPublish_published"
    on app."PipelineRunPublish" (published);

alter table app."PipelineRunPublish"
    add constraint "PipelineRunStats_pkey"
        primary key (id);

create table if not exists app.shedlock
(
    name       varchar(64)  not null,
    lock_until timestamp    not null,
    locked_at  timestamp    not null,
    locked_by  varchar(255) not null
);

alter table app.shedlock
    add primary key (name);

create table if not exists app."CustomVulnerabilityAdvisory"
(
    id                      bigint generated always as identity,
    "pipelineRunId"         bigint not null,
    "vulnerabilityId"       text   not null,
    "componentId"           bigint not null,
    "advisoryText"          text,
    "advisoryStatus"        integer,
    "advisoryJustification" integer,
    "advisoryLastModified"  timestamp with time zone,
    "advisoryResponse"      jsonb,
    severity                integer,
    fts                     tsvector generated always as (to_tsvector('simple'::regconfig,
                                                                      COALESCE("advisoryText", ''))) stored
);

create index if not exists "CustomVulnerabilityAdvisory_fts_idx"
    on app."CustomVulnerabilityAdvisory" using gin (fts);

alter table app."CustomVulnerabilityAdvisory"
    add primary key (id);

create table if not exists app."VulnerabilitySeverityEnum"
(
    id   bigint not null,
    name text   not null,
    fts  tsvector generated always as (to_tsvector('simple'::regconfig, COALESCE(name, ''))) stored
);

alter table app."VulnerabilitySeverityEnum"
    add primary key (id);

create table if not exists app."AdvisoryStatusEnum"
(
    id   bigint not null,
    name text   not null,
    fts  tsvector generated always as (to_tsvector('simple'::regconfig, COALESCE(name, ''))) stored
);

alter table app."AdvisoryStatusEnum"
    add primary key (id);

create table if not exists app."AdvisoryJustificationEnum"
(
    id   bigint not null,
    name text   not null,
    fts  tsvector generated always as (to_tsvector('simple'::regconfig, COALESCE(name, ''))) stored
);

alter table app."AdvisoryJustificationEnum"
    add primary key (id);

create table if not exists app."Label"
(
    id       bigint generated always as identity,
    name     varchar(20),
    "teamId" bigint  not null,
    type     integer not null,
    fts      tsvector generated always as (to_tsvector('simple'::regconfig, (name))) stored
);

create index if not exists "Label_fts_idx"
    on app."Label" using gin (fts);

alter table app."Label"
    add primary key (id);

alter table app."Label"
    add unique ("teamId", name);

alter table app."Label"
    add foreign key ("teamId") references app."Team";

create table if not exists app."LabelAssignment"
(
    id          bigint generated always as identity,
    "productId" bigint not null,
    "labelId"   bigint not null
);

alter table app."LabelAssignment"
    add primary key (id);

alter table app."LabelAssignment"
    add foreign key ("productId") references app."Product";

alter table app."LabelAssignment"
    add foreign key ("labelId") references app."Label";

create table if not exists app."ComplianceIntegrity"
(
    "complianceStatus" text not null,
    integrity          text
);

alter table app."ComplianceIntegrity"
    add primary key ("complianceStatus");
