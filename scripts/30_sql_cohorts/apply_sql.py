#!/usr/bin/env python3
"""
Apply SQL files in scripts/30_sql_cohorts/ to the SQLite DB.
Creates views for analysis and exports them to outputs/tables/ as CSVs.
"""

import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DBPATH = ROOT / "data/db/health_admin_demo.sqlite"
SQLDIR = ROOT / "scripts/30_sql_cohorts"
OUTDIR = ROOT / "outputs/tables"
OUTDIR.mkdir(parents=True, exist_ok=True)

def run_sql_files():
    conn = sqlite3.connect(DBPATH)
    try:
        for sql_file in sorted(SQLDIR.glob("*.sql")):
            print(f"Applying {sql_file.name} ...")
            sql = sql_file.read_text()
            conn.executescript(sql)
        conn.commit()

        # Export the key views as CSVs for Python/Tableau
        views = [
            "v_skin_mri_top_diag",
            "v_los_by_skin_mri",
            "v_skin_mri_er_revisit",
        ]
        for v in views:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {v}", conn)
                df.to_csv(OUTDIR / f"{v}.csv", index=False)
                print(f"Exported {v} to outputs/tables/{v}.csv")
            except Exception as e:
                print(f"Warning: could not export {v}: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_sql_files()
