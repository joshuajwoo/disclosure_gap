CREATE ROLE disclosure_gap_migrator LOGIN PASSWORD 'local_migration_only';
CREATE ROLE disclosure_gap_app LOGIN PASSWORD 'local_runtime_only';

GRANT CONNECT ON DATABASE disclosure_gap TO disclosure_gap_migrator, disclosure_gap_app;
GRANT USAGE, CREATE ON SCHEMA public TO disclosure_gap_migrator;
GRANT USAGE ON SCHEMA public TO disclosure_gap_app;

ALTER DEFAULT PRIVILEGES FOR ROLE disclosure_gap_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO disclosure_gap_app;
ALTER DEFAULT PRIVILEGES FOR ROLE disclosure_gap_migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO disclosure_gap_app;

REVOKE CREATE ON SCHEMA public FROM disclosure_gap_app;
