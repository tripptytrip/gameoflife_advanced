# db_explorer.py

import sqlite3

def get_schema(db_path="species.db"):
    """
    Inspects a SQLite database and returns its schema.
    """
    schema = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            column_names = [info[1] for info in columns_info]
            schema[table_name] = column_names
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
    return schema

def query_rows(db_path, table, filters=None, sort_by=None, sort_dir='ASC', limit=10, offset=0):
    """
    Queries rows from a specific table with filtering, sorting, and pagination.
    """
    schema = get_schema(db_path)
    if not schema or table not in schema:
        raise ValueError(f"Table '{table}' not found in database.")
    columns = schema[table]
    where_clauses, params = [], []
    if filters:
        for col, condition in filters.items():
            if col == "search" and "contains" in condition:
                search_term = condition["contains"]
                search_cols = ['lifeform_birth_rules', 'lifeform_survival_rules', 'shape']
                search_clauses = [f'"{sc}" LIKE ?' for sc in search_cols if sc in columns]
                if search_clauses:
                    where_clauses.append(f"({' OR '.join(search_clauses)})")
                    for _ in search_clauses: params.append(f'%{search_term}%')
                continue
            if col == "rules" and "birth" in condition and "survival" in condition:
                where_clauses.append('"lifeform_birth_rules" = ? AND "lifeform_survival_rules" = ?')
                params.extend([condition["birth"], condition["survival"]])
                continue
            if col not in columns: continue
            if "contains" in condition:
                where_clauses.append(f'"{col}" LIKE ?'); params.append(f'%{condition["contains"]}%')
            elif "min" in condition or "max" in condition:
                if "min" in condition: where_clauses.append(f'"{col}" >= ?'); params.append(condition["min"])
                if "max" in condition: where_clauses.append(f'"{col}" <= ?'); params.append(condition["max"])
            elif "eq" in condition:
                where_clauses.append(f'"{col}" = ?'); params.append(condition["eq"])
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\" {where_sql}", params)
        total_count = cursor.fetchone()[0]
        query_sql = f"SELECT * FROM \"{table}\" {where_sql}"
        if sort_by in columns:
            safe_sort_dir = 'DESC' if sort_dir.upper() == 'DESC' else 'ASC'
            query_sql += f' ORDER BY "{sort_by}" {safe_sort_dir}'
        query_sql += " LIMIT ? OFFSET ?"
        cursor.execute(query_sql, params + [limit, offset])
        rows = [dict(row) for row in cursor.fetchall()]
        return rows, total_count, columns
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return [], 0, []
    finally:
        if conn: conn.close()

def get_row_by_id(db_path, table, row_id):
    """
    Fetches a single row from a table by its 'id' column.
    """
    schema = get_schema(db_path)
    if not schema or table not in schema: raise ValueError(f"Table '{table}' not found.")
    if 'id' not in schema[table]: raise ValueError(f"Table '{table}' has no 'id' column.")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table}" WHERE id = ?', (row_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database query error: {e}"); return None
    finally:
        if conn: conn.close()

def get_unique_rules(db_path, table):
    """
    Fetches distinct combinations of birth and survival rules from a table.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT DISTINCT lifeform_birth_rules, lifeform_survival_rules FROM "{table}" ORDER BY lifeform_birth_rules, lifeform_survival_rules')
        rules = cursor.fetchall()
        return [f"B{b}/S{s}" for b, s in rules]
    except sqlite3.Error as e:
        print(f"Database query error: {e}"); return []
    finally:
        if conn: conn.close()

if __name__ == '__main__':
    pass
