-- 00_clean_views.sql (fixed to match current synthetic schema)

DROP VIEW IF EXISTS v_dad_clean;
CREATE VIEW v_dad_clean AS
SELECT
  d.EncID,
  d.PatientID,
  d.HospitalID,
  d.AdmitDate            AS AdmitDate_raw,
  d.DischargeDate        AS DischargeDate_raw,
  MAX(0, CAST(ROUND(julianday(d.DischargeDate) - julianday(d.AdmitDate)) AS INTEGER)) AS LOS_calc,
  d.LengthOfStay         AS LOS_reported,
  d.AdmissionCategory,
  d.DischargeDisposition,
  d.MRDx,
  d.Diagnosis1, d.Diagnosis2, d.Diagnosis3,
  d.Proc1, d.Proc2,
  d.Proc1Date, d.Proc2Date,
  d.BirthDate, d.Sex,
  CASE WHEN d.Proc1 LIKE '%.20.%' OR d.Proc2 LIKE '%.20.%' THEN 1 ELSE 0 END AS AnyMRI_flag,
  CASE WHEN d.Proc1 LIKE '3.SC.20%' OR d.Proc2 LIKE '3.SC.20%' THEN 1 ELSE 0 END AS SkinMRI_flag
FROM DAD d;

DROP VIEW IF EXISTS v_nacrs_clean;
CREATE VIEW v_nacrs_clean AS
SELECT
  n.VisitID,
  n.PatientID,
  n.VisitDateTime        AS VisitDateTime_raw,
  n.VisitType,
  n.Diagnosis            AS NACRS_Diagnosis,
  n.ProviderType,
  n.Procedure            AS NACRS_Procedure
FROM NACRS n;
