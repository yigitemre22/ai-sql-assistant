create role ai_ingest
with login
password 'yigitemre1801';

grant connect on database ai_sql_assistant
to ai_ingest;

grant usage on schema public to ai_ingest;

grant select,insert,update on table public.customers
to ai_ingest;

grant usage,select on sequence public.customers_id_seq to ai_ingest;

GRANT UPDATE
ON SEQUENCE public.customers_id_seq
TO ai_ingest;


SELECT *
FROM public.customers
ORDER BY id;
SELECT COUNT(*) AS customer_count
FROM public.customers;

