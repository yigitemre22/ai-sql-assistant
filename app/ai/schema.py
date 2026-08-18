# Database schema information for the AI
# This helps the LLM understand our database structure


# Tables and columns that the AI is allowed to use
DATABASE_SCHEMA = """
Database: PostgreSQL

Table: customers

Columns:
- id: integer
- name: character varying
- email: character varying
- city: character varying
- total_spent: numeric
"""