import sqlite3
import os

class DatabaseManager:
    """
    A simple SQLite database manager for purchase order header details.

    This class encapsulates common operations against an SQLite database file
    located at `db_path`. It allows you to:

      • Retrieve the full database schema (tables, indexes, views, triggers)
        as a concatenated SQL string via `get_schema()`.
      • Execute arbitrary SQL queries via `execute_query()` and get the
        results back as a structured dictionary.

    Attributes:
        db_path (str): Path to the SQLite database file.

    Methods:
        get_schema() -> str
            Connects to the database and fetches all CREATE statements for
            tables, indexes, views, and triggers. Returns them joined into
            a single string. Raises an Exception if no schema objects are found
            or if any error occurs during retrieval.

        execute_query(query: str) -> dict
            Executes the given SQL query. On success, returns:
                {
                    "columns": [<column_name>, ...],
                    "rows": [(<val1>, <val2>, ...), ...]
                }
            If the query returns no rows (when at least one was expected),
            or if any other error occurs, returns:
                { "error": "<error message>" }.
    """
    
    def __init__(self):
        self.db_path = "dataset/synthetic_po.sqlite"

    def get_schema(self) -> str:
        """Retrieve the database schema as a string."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT sql FROM sqlite_master "
                    "WHERE type IN ('table','index','view','trigger') "
                    "AND sql IS NOT NULL;"
                )
                schema_rows = cursor.fetchall()

                if not schema_rows:
                    raise Exception("No Result Return.")
                
                return "\n".join(row[0] for row in schema_rows)

        except Exception as e:
            raise Exception(f"Error fetching schema: {e}")
        
    def execute_query(self, query: str) -> dict:
        """Execute SQL query and return results as a structured dictionary."""
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                if not rows:
                    raise Exception("No rows returned, but at least one row was expected.")

                return {"columns": columns, "rows": rows}
        
        except Exception as e:
            return {"error": str(e)}