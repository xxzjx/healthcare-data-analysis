#!/usr/bin/env python3
"""
Load synthetic CSVs into a SQLite database and add useful indexes.

- Input CSVs (expected in data/raw/):
  - patients.csv
  - dad.csv
  - nacrs.csv

- Output DB:
  - data/db/health_admin_demo.sqlite

Usage:
  python scripts/20_load_to_db/load_to_db.py
"""

import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DBDIR = ROOT / "data" / "db"
DBDIR.mkdir(parents=True, exist_ok=True)
DBPATH = DBDIR / "health_admin_demo.sqlite"

def load_csv_to_sqlite(csv_path: Path, table_name: str, conn: sqlite3.Connection) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")
    df = pd.read_csv(csv_path)
    # Replace existing table to keep idempotent
    df.to_sql(table_name, conn, if_exists="replace", index=False)

def create_indexes(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    # Pragmas
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA synchronous=NORMAL;")
    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_patients_id ON patients(PatientID);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_enc ON DAD(EncID);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_patient ON DAD(PatientID);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_admit ON DAD(AdmitDate);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_discharge ON DAD(DischargeDate);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_proc1 ON DAD(Proc1);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_dad_proc2 ON DAD(Proc2);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nacrs_visit ON NACRS(VisitID);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nacrs_patient ON NACRS(PatientID);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nacrs_time ON NACRS(VisitDateTime);")
    conn.commit()

def main():
    if DBPATH.exists():
        DBPATH.unlink()  # fresh load each run
    conn = sqlite3.connect(DBPATH)
    try:
        load_csv_to_sqlite(RAW / "patients.csv", "patients", conn)
        load_csv_to_sqlite(RAW / "dad.csv", "DAD", conn)
        load_csv_to_sqlite(RAW / "nacrs.csv", "NACRS", conn)
        create_indexes(conn)
    finally:
        conn.close()
    print("Loaded CSVs into:", DBPATH)

if __name__ == "__main__":
    main()
