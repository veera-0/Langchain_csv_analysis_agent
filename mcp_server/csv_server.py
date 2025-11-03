# main.py
import os, json
import pandas as pd

# --- 0) Loading CSV ---
DF_PATH = "titanic.csv"
df = pd.read_csv(DF_PATH)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("main")

@mcp.tool()
def tool_schema(dummy: str) -> str:
    """Returns column names and data types as JSON."""
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return json.dumps(schema)

@mcp.tool()
def tool_nulls(dummy: str) -> str:
    """Returns columns with the number of missing values as JSON (only columns with >0 missing values)."""
    nulls = df.isna().sum()
    result = {col: int(n) for col, n in nulls.items() if n > 0}
    return json.dumps(result)

@mcp.tool()
def tool_describe(input_str: str) -> str:
    """
    Returns describe() statistics.
    Optional: input_str can contain a comma-separated list of columns, e.g. "age, fare".
    """
    cols = None
    if input_str and input_str.strip():
        cols = [c.strip() for c in input_str.split(",") if c.strip() in df.columns]
    stats = df[cols].describe() if cols else df.describe()
    return stats.to_csv(index=True) 

# --- Additional Useful Tools ---
@mcp.tool()
def tool_head(n: str) -> str:
    """Returns the first n rows of the dataframe as CSV (default 5)."""
    try:
        n_rows = int(n)
    except (ValueError, TypeError):
        n_rows = 5
    return df.head(n_rows).to_csv(index=False)

@mcp.tool()
def tool_value_counts(col: str) -> str:
    """Returns value counts for a given column as JSON."""
    if col not in df.columns:
        return json.dumps({"error": "Column not found"})
    counts = df[col].value_counts(dropna=False).to_dict()
    counts = {str(k): int(v) for k, v in counts.items()}
    return json.dumps(counts)

@mcp.tool()
def tool_unique_values(col: str) -> str:
    """Returns unique values for a given column as JSON list."""
    if col not in df.columns:
        return json.dumps({"error": "Column not found"})
    uniques = df[col].dropna().unique().tolist()
    return json.dumps(uniques)

@mcp.tool()
def tool_fillna_count(args: str) -> str:
    """Returns the number of missing values that would be filled for a given column and value as JSON."""
    try:
        col, value = [a.strip() for a in args.split(",", 1)]
    except Exception:
        return json.dumps({"error": "Provide arguments as 'col,value'"})
    if col not in df.columns:
        return json.dumps({"error": "Column not found"})
    missing = df[col].isna().sum()
    return json.dumps({"column": col, "missing_count": int(missing), "fill_value": value})

if __name__ == "__main__":
    mcp.run(transport="stdio")