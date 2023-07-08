-- CREATE SCHEMA if not exists app;

INSERT INTO app."Team" ("name", "clientId") VALUES
  ('xxx', 'xxx'), 
  ('xxx', 'xxx'), 
  ('xxx', 'xxx'), 
  ('xxx', 'xxx'), 
  ('xxx', 'xxx'), 
  ('Ilan Schifter''s Team', 'jejUL01B6hRqQP930A5zeaLAyA2BWwWe'),
  ('Reuven local', 'Y7kdWVbxMpgTwSPte7TCgrbOwtwGa95M');

----------------------------------------------------------------
-- cyclonedx-json Attestations
----------------------------------------------------------------
insert into osint."PipelineRun" ("productKey",
                                 "pipelineName",
                                 "pipelineRun",
                                 "version",
                                 "team")
values ('test', 'pip name', 'pip run', '0.0.1', 1);

INSERT INTO osint."Attestation" ("contentType", "targetType", "targetName", "contextType", context, key, timestamp,
                                 "userId", "teamId", "pipelineRun", state, "sigStatus", alerted, license, deleted,
                                 job_ids)
VALUES ('cyclonedx-json', 'image', 'hasura/graphql-engine', 'local', '{
  "name": "hasura/graphql-engine",
  "user": "john",
  "imageID": "sha256:d74824329d7a473163990b3555c109d6fdf7a6140e04eaee20f2d1cca159eaee",
  "hostname": "john",
  "sbomname": "index.docker.io/hasura/graphql-engine:latest",
  "sbompurl": "pkg:docker/index.docker.io/hasura/graphql-engine:index.docker.io/hasura/graphql-engine:latest@sha256:d74824329d7a473163990b3555c109d6fdf7a6140e04eaee20f2d1cca159eaee",
  "file_size": 12554482,
  "sbomgroup": "image",
  "sbomhashs": [
    "sha256-b363eb6d8ffc21b73674399b5bdfa2e7ad52174bcd2c784a0c1829b250b8b6ff",
    "sha256-d74824329d7a473163990b3555c109d6fdf7a6140e04eaee20f2d1cca159eaee"
  ],
  "timestamp": "2023-05-23T11:24:06+03:00",
  "input_name": "hasura/graphql-engine",
  "sbomversion": "sha256:d74824329d7a473163990b3555c109d6fdf7a6140e04eaee20f2d1cca159eaee",
  "target_type": "image",
  "content_type": "cyclonedx-json",
  "context_type": "local",
  "input_scheme": "docker"
}',
        's3://scribe-dev-filetransfers/3131/Q5z6uiqHWeGSLdZzIFVHMcnlF09kM1x8/23f756b575422a37f61206ec3a72b065_.sshfgblbqapm.json',
        '2023-05-23 08:24:45.139850 +00:00', null, 11, 1, 'uploaded', 'in-progress', false, null, false, '{}');
INSERT INTO osint."Attestation" ("contentType", "targetType", "targetName", "contextType", context, key, timestamp,
                                 "userId", "teamId", "pipelineRun", state, "sigStatus", alerted, license, deleted,
                                 job_ids)
VALUES ('cyclonedx-json', 'image', 'postgres', 'local', '{
  "name": "postgres",
  "user": "john",
  "imageID": "sha256:680aba37fd0f0766e7568a00daf18cfd4916c2689def0f17962a3e1508c22856",
  "hostname": "john",
  "sbomname": "index.docker.io/library/postgres:latest",
  "sbompurl": "pkg:docker/index.docker.io/library/postgres:index.docker.io/library/postgres:latest@sha256:680aba37fd0f0766e7568a00daf18cfd4916c2689def0f17962a3e1508c22856",
  "file_size": 12882814,
  "sbomgroup": "image",
  "sbomhashs": [
    "sha256-901df890146ec46a5cab7a33f4ac84e81bac2fe92b2c9a14fd649502c4adf954",
    "sha256-680aba37fd0f0766e7568a00daf18cfd4916c2689def0f17962a3e1508c22856"
  ],
  "timestamp": "2023-05-23T11:25:15+03:00",
  "input_name": "postgres",
  "sbomversion": "sha256:680aba37fd0f0766e7568a00daf18cfd4916c2689def0f17962a3e1508c22856",
  "target_type": "image",
  "content_type": "cyclonedx-json",
  "context_type": "local",
  "input_scheme": "docker"
}',
        's3://scribe-dev-filetransfers/3131/Q5z6uiqHWeGSLdZzIFVHMcnlF09kM1x8/cd78265f99777e645865f19138af7316_.bcdueuwklerg.json',
        '2023-05-23 08:25:21.285952 +00:00', null, 11, 1, 'uploaded', 'in-progress', false, null, false, '{}');
INSERT INTO osint."Attestation" ("contentType", "targetType", "targetName", "contextType", context, key, timestamp,
                                 "userId", "teamId", "pipelineRun", state, "sigStatus", alerted, license, deleted,
                                 job_ids)
VALUES ('cyclonedx-json', 'image', 'scribe-node-demo_test', 'local', '{
  "name": "scribe-node-demo_test",
  "user": "john",
  "imageID": "sha256:9399a238f48601fc88443a82c3b966ce931ef81c1054bd796219b769d2ed3602",
  "hostname": "john",
  "imageTag": [
    "latest"
  ],
  "sbomname": "index.docker.io/library/scribe-node-demo_test:latest",
  "sbompurl": "pkg:docker/index.docker.io/library/scribe-node-demo_test:index.docker.io/library/scribe-node-demo_test:latest@sha256:9399a238f48601fc88443a82c3b966ce931ef81c1054bd796219b769d2ed3602",
  "file_size": 4382064,
  "input_tag": "latest",
  "sbomgroup": "image",
  "sbomhashs": [
    "sha256-9399a238f48601fc88443a82c3b966ce931ef81c1054bd796219b769d2ed3602"
  ],
  "timestamp": "2023-05-23T11:25:58+03:00",
  "input_name": "scribe-node-demo_test",
  "sbomversion": "sha256:9399a238f48601fc88443a82c3b966ce931ef81c1054bd796219b769d2ed3602",
  "target_type": "image",
  "content_type": "cyclonedx-json",
  "context_type": "local",
  "input_scheme": "docker"
}',
        's3://scribe-dev-filetransfers/3131/Q5z6uiqHWeGSLdZzIFVHMcnlF09kM1x8/6a1074d72cdb6b8c81dad8580aa28f54_.wdndmfavgget.json',
        '2023-05-23 08:26:00.994511 +00:00', null, 11, 1, 'uploaded', 'in-progress', false, null, false, '{}');
INSERT INTO osint."Attestation" ("contentType", "targetType", "targetName", "contextType", context, key, timestamp,
                                 "userId", "teamId", "pipelineRun", state, "sigStatus", alerted, license, deleted,
                                 job_ids)
VALUES ('cyclonedx-json', 'image', 'apache/airflow', 'local', '{
  "name": "apache/airflow",
  "user": "john",
  "imageID": "sha256:1fdedb32a90fef523c58e3e0e4a012fa0358f522b9aaae10c624fc6ac558a7e2",
  "hostname": "john",
  "sbomname": "index.docker.io/apache/airflow:latest",
  "sbompurl": "pkg:docker/index.docker.io/apache/airflow:index.docker.io/apache/airflow:latest@sha256:1fdedb32a90fef523c58e3e0e4a012fa0358f522b9aaae10c624fc6ac558a7e2",
  "file_size": 61320130,
  "sbomgroup": "image",
  "sbomhashs": [
    "sha256-ea866b905de7eb2d8e89923763999c2e889144a2a2adde1886fd19d79a1a1191",
    "sha256-1fdedb32a90fef523c58e3e0e4a012fa0358f522b9aaae10c624fc6ac558a7e2"
  ],
  "timestamp": "2023-05-23T11:27:49+03:00",
  "input_name": "apache/airflow",
  "sbomversion": "sha256:1fdedb32a90fef523c58e3e0e4a012fa0358f522b9aaae10c624fc6ac558a7e2",
  "target_type": "image",
  "content_type": "cyclonedx-json",
  "context_type": "local",
  "input_scheme": "docker"
}',
        's3://scribe-dev-filetransfers/3131/Q5z6uiqHWeGSLdZzIFVHMcnlF09kM1x8/1afe00708d59ee4082010427b820ee10_.xsbmyxnlnhfd.json',
        '2023-05-23 08:28:17.719299 +00:00', null, 11, 1, 'uploaded', 'in-progress', false, null, false, '{}');

update osint."Attestation"
set state = 'uploaded';
