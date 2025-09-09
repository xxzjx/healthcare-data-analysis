#!/usr/bin/env python3
"""
Step 4: Python analysis that reads from the SQLite DB views (or the exported CSVs),
computes simple descriptive stats, and produces a few figures.

Outputs:
- outputs/tables/summary_skin_mri_overview.csv
- outputs/figures/fig_top_diag.png
- outputs/figures/fig_los_by_flag.png
- outputs/figures/fig_revisit_hist.png
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DBPATH = ROOT / "data" / "db" / "health_admin_demo.sqlite"
OUT_T = ROOT / "outputs" / "tables"
OUT_F = ROOT / "outputs" / "figures"
OUT_T.mkdir(parents=True, exist_ok=True)
OUT_F.mkdir(parents=True, exist_ok=True)

def fetch_view(conn, view_name: str) -> pd.DataFrame:
    return pd.read_sql_query(f"SELECT * FROM {view_name};", conn)

def main():
    if not DBPATH.exists():
        raise FileNotFoundError("DB not found. Run `make sql` first.")
    conn = sqlite3.connect(DBPATH)

    # Fetch core views
    top_diag = fetch_view(conn, "v_skin_mri_top_diag")
    los_by_flag = fetch_view(conn, "v_los_by_skin_mri")
    revisit = fetch_view(conn, "v_skin_mri_er_revisit")

    # 1) Overview table
    # Total skin-MRI encounters
    n_skin = pd.read_sql_query("SELECT COUNT(*) AS n FROM v_skin_mri_dad;", conn).iloc[0,0]
    # Total DAD encounters
    n_dad = pd.read_sql_query("SELECT COUNT(*) AS n FROM v_dad_clean;", conn).iloc[0,0]
    # Skin-MRI share
    share = round(100.0 * n_skin / n_dad, 2) if n_dad else 0.0
    # 30-day ER revisit rate for Skin cohort
    # Count unique EncID appearing in revisit
    n_skin_revisit = revisit["EncID"].nunique() if not revisit.empty else 0
    revisit_rate = round(100.0 * n_skin_revisit / n_skin, 2) if n_skin else 0.0

    overview = pd.DataFrame({
        "Metric": ["Total DAD Encounters", "Skin MRI Encounters", "Skin MRI Share (%)", "30d ER Revisit in Skin MRI (%)"],
        "Value": [n_dad, n_skin, share, revisit_rate]
    })
    overview.to_csv(OUT_T / "summary_skin_mri_overview.csv", index=False)

    # 2) Figures
    # a) Top diagnoses (barh)
    if not top_diag.empty:
        plt.figure()
        td = top_diag.sort_values("Count", ascending=True)
        plt.barh(td["DiagnosisCode"], td["Count"])
        plt.title("Top MRDx among Skin MRI Encounters")
        plt.xlabel("Count")
        plt.ylabel("ICD-10-CA Code")
        plt.tight_layout()
        plt.savefig(OUT_F / "fig_top_diag.png", dpi=150)
        plt.close()

    # b) LOS by SkinMRI flag
    # Fetch LOS distributions directly from v_dad_clean for better detail
    dad = pd.read_sql_query("SELECT SkinMRI_flag, LOS_calc FROM v_dad_clean;", conn)
    plt.figure()
    data = [
        dad.loc[dad["SkinMRI_flag"]==0, "LOS_calc"].dropna(),
        dad.loc[dad["SkinMRI_flag"]==1, "LOS_calc"].dropna()
    ]
    plt.boxplot(data, labels=["Non-Skin MRI","Skin MRI"], showfliers=False)
    plt.title("Length of Stay by Skin MRI Flag")
    plt.ylabel("Days")
    plt.tight_layout()
    plt.savefig(OUT_F / "fig_los_by_flag.png", dpi=150)
    plt.close()

    # c) Histogram of delta_days for ER revisits (Skin cohort)
    if not revisit.empty:
        plt.figure()
        vals = revisit["delta_days"].dropna().astype(int)
        plt.hist(vals, bins=np.arange(0, 31, 2), edgecolor="black")
        plt.title("Distribution of ER revisit timing (Skin MRI cohort)")
        plt.xlabel("Days from discharge")
        plt.ylabel("Count of revisits")
        plt.tight_layout()
        plt.savefig(OUT_F / "fig_revisit_hist.png", dpi=150)
        plt.close()

    # Also export the SQL views as CSVs (in case runner skipped it)
    top_diag.to_csv(OUT_T / "v_skin_mri_top_diag.csv", index=False)
    los_by_flag.to_csv(OUT_T / "v_los_by_skin_mri.csv", index=False)
    revisit.to_csv(OUT_T / "v_skin_mri_er_revisit.csv", index=False)

    conn.close()
    print("Analysis complete. Outputs saved to outputs/tables and outputs/figures.")

if __name__ == "__main__":
    main()
