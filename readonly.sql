-- Create a read-only database role
CREATE ROLE ai_readonly
WITH LOGIN
PASSWORD 'CHANGE_ME';

-- Allow the role to connect to the application database
GRANT CONNECT ON DATABASE ai_sql_assistant
TO ai_readonly;

-- Allow the role to use the public schema
GRANT USAGE ON SCHEMA public
TO ai_readonly;

-- Allow read-only access to the customers table
GRANT SELECT ON TABLE public.customers
TO ai_readonly;