#!/usr/bin/env python3
"""
Generate synthetic DAD (inpatient) and NACRS (ambulatory/ER) data.
Outputs CSVs to data/raw/: patients.csv, dad.csv, nacrs.csv
"""
import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Config ---
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DICTS = ROOT / "data" / "dicts"
RAW.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env") if (ROOT / ".env").exists() else load_dotenv(ROOT / ".env.example")

RNG_SEED = int(os.getenv("RNG_SEED", "42"))
N_PATIENTS = int(os.getenv("N_PATIENTS", "6000"))
N_DAD = int(os.getenv("N_DAD_ROWS", "12000"))
N_NACRS = int(os.getenv("N_NACRS_ROWS", "24000"))
START_DATE = os.getenv("START_DATE", "2022-01-01")
END_DATE = os.getenv("END_DATE", "2025-06-30")

rng = np.random.default_rng(RNG_SEED)

# --- Vocabs ---
icd10_codes = json.loads((DICTS / "icd10_codes.json").read_text())
cci_mri = json.loads((DICTS / "cci_mri.json").read_text())
cci_other = json.loads((DICTS / "cci_other.json").read_text())
hospitals = [f"HOSP{i:03d}" for i in range(1, 11)]
sexes = ["F","M"]
provinces = ["AB","BC","SK","MB"]
visit_types = ["ER","DaySurgery","Clinic"]
provider_types = ["Physician","NursePractitioner","Resident"]

def random_dates(start, end, size):
    start_u = np.datetime64(start).astype("datetime64[s]").astype(int)
    end_u = np.datetime64(end).astype("datetime64[s]").astype(int)
    return pd.to_datetime(rng.integers(start_u, end_u+1, size=size), unit="s")

# --- Patients ---
patient_ids = np.arange(1, N_PATIENTS+1)
birth_years = rng.integers(1935, 2011, size=N_PATIENTS)
birth_dates = [datetime(int(y), int(rng.integers(1, 13)), int(rng.integers(1, 28))) for y in birth_years]
patients = pd.DataFrame({
    "PatientID": patient_ids,
    "Province": rng.choice(provinces, size=N_PATIENTS, replace=True),
    "BirthDate": birth_dates,
    "Sex": rng.choice(sexes, size=N_PATIENTS, replace=True),
})

# --- DAD (inpatient) ---
admit_dates = random_dates(START_DATE, "2024-12-15", size=N_DAD)
los = rng.poisson(lam=4, size=N_DAD)
los = np.clip(los, 0, 30)
discharge_dates = pd.to_datetime(admit_dates) + pd.to_timedelta(los, unit="D")

dad = pd.DataFrame({
    "EncID": np.arange(1, N_DAD+1),
    "PatientID": rng.integers(1, N_PATIENTS+1, size=N_DAD),
    "HospitalID": rng.choice(hospitals, size=N_DAD, replace=True),
    "AdmitDate": admit_dates,
    "DischargeDate": discharge_dates,
    "LengthOfStay": los,
    "AdmissionCategory": rng.choice(["Elective","Urgent","Newborn","Other"], size=N_DAD, replace=True, p=[0.25,0.55,0.02,0.18]),
    "DischargeDisposition": rng.choice(["Home","Transfer","Died","Other"], size=N_DAD, replace=True, p=[0.78,0.15,0.02,0.05]),
    "MRDx": rng.choice(icd10_codes, size=N_DAD, replace=True),
    "Diagnosis1": rng.choice(icd10_codes, size=N_DAD, replace=True),
    "Diagnosis2": rng.choice(icd10_codes, size=N_DAD, replace=True),
    "Diagnosis3": rng.choice(icd10_codes, size=N_DAD, replace=True),
})

p_mri = 0.18
proc1_is_mri = rng.random(N_DAD) < p_mri
proc2_is_mri = rng.random(N_DAD) < (p_mri * 0.5)
dad["Proc1"] = np.where(proc1_is_mri, rng.choice(cci_mri, size=N_DAD, replace=True),
                        rng.choice(cci_other, size=N_DAD, replace=True))
dad["Proc2"] = np.where(proc2_is_mri, rng.choice(cci_mri, size=N_DAD, replace=True),
                        rng.choice(cci_other, size=N_DAD, replace=True))

proc1_offsets = rng.integers(0, np.maximum(los,1))
proc2_offsets = rng.integers(0, np.maximum(los,1))
dad["Proc1Date"] = pd.to_datetime(dad["AdmitDate"]) + pd.to_timedelta(proc1_offsets, unit="D")
dad["Proc2Date"] = pd.to_datetime(dad["AdmitDate"]) + pd.to_timedelta(proc2_offsets, unit="D")

# Flags
dad["AnyMRI"] = dad[["Proc1","Proc2"]].apply(lambda r: (".20." in str(r["Proc1"])) or (".20." in str(r["Proc2"])), axis=1)
dad["SkinMRI"] = dad[["Proc1","Proc2"]].apply(lambda r: ("3.SC.20" in str(r["Proc1"])) or ("3.SC.20" in str(r["Proc2"])), axis=1)

# Attach demographics
dad = dad.merge(patients[["PatientID","Province","BirthDate","Sex"]], on="PatientID", how="left")

# --- NACRS (ambulatory) ---
nacrs = pd.DataFrame({
    "VisitID": np.arange(1, N_NACRS+1),
    "PatientID": rng.integers(1, N_PATIENTS+1, size=N_NACRS),
    "VisitDateTime": random_dates(START_DATE, END_DATE, size=N_NACRS),
    "VisitType": rng.choice(["ER","DaySurgery","Clinic"], size=N_NACRS, replace=True, p=[0.65,0.05,0.30]),
    "Diagnosis": rng.choice(icd10_codes, size=N_NACRS, replace=True),
    "ProviderType": rng.choice(["Physician","NursePractitioner","Resident"], size=N_NACRS, replace=True),
})

proc_is_mri = rng.random(N_NACRS) < 0.07
nacrs["Procedure"] = np.where(proc_is_mri, rng.choice(cci_mri, size=N_NACRS, replace=True),
                              rng.choice(cci_other, size=N_NACRS, replace=True))

# --- Save CSVs ---
patients.to_csv(RAW / "patients.csv", index=False)
dad.to_csv(RAW / "dad.csv", index=False)
nacrs.to_csv(RAW / "nacrs.csv", index=False)

print("Generated:")
print(RAW / "patients.csv")
print(RAW / "dad.csv")
print(RAW / "nacrs.csv")
