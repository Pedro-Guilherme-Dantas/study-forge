CREATE EXTENSION IF NOT EXISTS vector;
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'studyforge_runtime') THEN
    CREATE ROLE studyforge_runtime LOGIN PASSWORD 'studyforge-runtime-local'
      NOSUPERUSER NOCREATEDB NOCREATEROLE;
  END IF;
END $$;
GRANT CONNECT ON DATABASE studyforge TO studyforge_runtime;
GRANT USAGE ON SCHEMA public TO studyforge_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO studyforge_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE studyforge IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO studyforge_runtime;
