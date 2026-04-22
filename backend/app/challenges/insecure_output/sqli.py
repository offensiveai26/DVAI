"""
Challenge: SQL Injection via AI
The AI generates SQL from natural language and executes it.
"""

import re
import sqlite3
from app.flags import get_flag
from app.llm import chat, _check_ollama

FLAG = get_flag("io-sqli")


def setup_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
        INSERT INTO users VALUES (1, 'Alice', 'alice@example.com');
        INSERT INTO users VALUES (2, 'Bob', 'bob@example.com');
        INSERT INTO users VALUES (3, 'Charlie', 'charlie@example.com');
        CREATE TABLE secrets (id INTEGER PRIMARY KEY, flag TEXT);
        INSERT INTO secrets VALUES (1, '""" + FLAG + """');
    """)
    return conn


SYSTEM_PROMPTS = {
    1: "Convert the user's question into a SQL query for a database with tables: users(id, name, email). Return ONLY the SQL query, nothing else.",
    2: "Convert the user's question into a SQL query for a database with table: users(id, name, email). Return ONLY the SQL query. Only query the users table.",
    3: (
        "Convert the user's question into a SQL query. The database has table: users(id, name, email). "
        "RULES: Only generate SELECT queries on the users table. No UNION, no subqueries, no other tables. "
        "Return ONLY the SQL query."
    ),
}


def _sim(user_input: str, difficulty: int) -> str:
    """SQL injection simulation — requires actual SQL syntax knowledge."""
    u = user_input.lower().strip()
    words = u.split()

    # Need a proper sentence/query, not just a keyword
    if len(words) < 6:
        return "I can help you query the database. Describe what data you need in detail."

    # Detect actual SQL injection patterns
    has_union_select = bool(re.search(r'union\s+(all\s+)?select\b', u))
    has_secrets_ref = bool(re.search(r'\b(secrets?|flag|hidden|password)\b', u))
    has_schema_discovery = bool(re.search(r'(sqlite_master|information_schema|pg_catalog|show\s+tables|\.schema|table_name)', u))
    has_subquery = bool(re.search(r'\(\s*select\b', u))
    has_stacked = bool(re.search(r';\s*select\b', u))
    has_comment = bool(re.search(r'(--|#|/\*)', u))
    has_or_true = bool(re.search(r"(or|and)\s+['\"]?\s*(1\s*=\s*1|true|''='')", u))

    if difficulty == 1:
        # Need actual UNION SELECT syntax with table reference
        if has_union_select and has_secrets_ref:
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if has_union_select:
            return "SELECT * FROM users UNION SELECT 1, 2, 3"
        if has_schema_discovery:
            return "SELECT sql FROM sqlite_master WHERE type='table'"
        if has_or_true:
            return "SELECT * FROM users WHERE 1=1"
        # Just keywords without SQL syntax
        if re.search(r'\b(secret|flag|union)\b', u) and not has_union_select:
            return "SELECT * FROM users WHERE name LIKE '%" + u.split()[-1] + "%'"
        if re.search(r'\b(all|everyone|list|show)\b', u):
            return "SELECT * FROM users"
        return "SELECT * FROM users LIMIT 10"

    elif difficulty == 2:
        # Direct UNION + secrets is blocked — need indirect discovery
        if has_union_select and has_secrets_ref:
            return "SELECT * FROM users"  # Filtered — too obvious
        if has_schema_discovery:
            # Schema discovery reveals table structure — this is the intended path
            return "SELECT * FROM users UNION SELECT 1, sql, '' FROM sqlite_master"
        if has_union_select and has_comment:
            # UNION with comment bypass
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if has_subquery and has_secrets_ref:
            return "SELECT * FROM users WHERE name IN (SELECT flag FROM secrets)"
        # Social engineering the natural language
        if re.search(r'(join|combine|merge|relate|cross.?reference)\s+.{3,}(table|data|info|record|all)', u) and len(u.split()) >= 8:
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if re.search(r'\b(all|everyone|list)\b', u):
            return "SELECT * FROM users"
        return "SELECT * FROM users WHERE name LIKE '%'"

    else:
        # Direct UNION+secrets, schema discovery keywords all blocked
        if (has_union_select and has_secrets_ref) or re.search(r'\b(secrets?|flag)\b', u):
            return "SELECT * FROM users"
        if re.search(r'\b(sqlite_master|information_schema|show\s+tables)\b', u):
            return "SELECT * FROM users"
        # Need clever indirection
        if has_stacked and re.search(r'(select\s+.{2,}\s+from\s+\w+)', u):
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if re.search(r'(backup|export|dump|migrate)\s+.{3,}(all|full|complete|entire|every)\s+.{3,}(table|data|database)', u) and len(u.split()) >= 10:
            return "SELECT * FROM users UNION SELECT id, flag, '' FROM secrets"
        if re.search(r'(count|statistic|analytic|aggregate)\s+.{3,}(across|all|every|each)\s+.{3,}(table|schema|database)', u) and len(u.split()) >= 10:
            return "SELECT * FROM users UNION SELECT 1, flag, '' FROM secrets"
        if has_subquery:
            return "SELECT * FROM users WHERE id IN (SELECT 1)"
        return "SELECT * FROM users"


async def handle(user_input: str, difficulty: int = 1) -> dict:
    if await _check_ollama():
        system_prompt = SYSTEM_PROMPTS.get(difficulty, SYSTEM_PROMPTS[1])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        sql = await chat(messages)
    else:
        sql = _sim(user_input, difficulty)

    sql = sql.strip().strip("`").replace("sql\n", "").strip()

    conn = setup_db()
    try:
        results = conn.execute(sql).fetchall()
        flag_found = any(FLAG in str(row) for row in results)
        return {
            "generated_sql": sql,
            "results": [list(row) for row in results],
            "flag_found": flag_found,
        }
    except Exception as e:
        return {"generated_sql": sql, "error": str(e), "flag_found": False}
    finally:
        conn.close()
