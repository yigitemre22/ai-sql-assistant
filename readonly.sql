create role ai_readonly
with LOGIN
PASSWORD 'yigitemre1801';

grant connect on database ai_sql_assistant to ai_readonly;
grant usage on schema public to ai_readonly;
grant select on table public.customers to ai_readonly;