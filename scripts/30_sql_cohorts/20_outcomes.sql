-- 20_outcomes.sql
-- Purpose: Cohort-level outcomes & aggregates for Skin MRI analysis.

-- 1) Top MRDx diagnoses within Skin MRI cohort (limit 15 for quick viz)
CREATE VIEW IF NOT EXISTS v_skin_mri_top_diag AS
SELECT
  MRDx AS DiagnosisCode,
  COUNT(*) AS Count
FROM v_skin_mri_dad
GROUP BY MRDx
ORDER BY Count DESC
LIMIT 15;

-- 2) Average LOS (from derived LOS_calc) by Skin MRI flag vs Non
CREATE VIEW IF NOT EXISTS v_los_by_skin_mri AS
SELECT
  SkinMRI_flag,
  ROUND(AVG(LOS_calc), 2)          AS AvgLOS,
  COUNT(*)                          AS N
FROM v_dad_clean
GROUP BY SkinMRI_flag;

-- If your SQLite doesn't support MEDIAN(), comment that line out. Python can compute median later.

-- 3) 30-day ER revisit for Skin MRI cohort
--    Join Skin MRI discharges (v_skin_mri_dad) to ER visits in NACRS within 0–30 days.
CREATE VIEW IF NOT EXISTS v_skin_mri_er_revisit AS
SELECT
  d.EncID,
  d.PatientID,
  d.DischargeDate_raw AS DischargeDate,
  n.VisitDateTime_raw AS ER_VisitDateTime,
  CAST(ROUND(julianday(n.VisitDateTime_raw) - julianday(d.DischargeDate_raw)) AS INTEGER) AS delta_days
FROM v_skin_mri_dad d
JOIN v_nacrs_clean n
  ON n.PatientID = d.PatientID
WHERE n.VisitType = 'ER'
  AND (julianday(n.VisitDateTime_raw) - julianday(d.DischargeDate_raw)) BETWEEN 0 AND 30;