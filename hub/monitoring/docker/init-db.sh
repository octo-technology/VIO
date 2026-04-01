#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE SCHEMA iothub;
  CREATE TABLE iothub.telemetry (
      id uuid NOT NULL,
      device_id text NOT NULL,
      business_decision text NOT NULL,
      "timestamp" timestamp without time zone NOT NULL,
      item_id text,
      config text
  );
  ALTER TABLE ONLY iothub.telemetry
      ADD CONSTRAINT telemetry_pkey PRIMARY KEY (id);

  GRANT ALL PRIVILEGES ON DATABASE vio TO vio;
EOSQL
