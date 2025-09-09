-- Purpose: Define the Skin MRI inpatient cohort using CCI pattern "3.SC.20%"

CREATE VIEW IF NOT EXISTS v_skin_mri_dad AS
SELECT *
FROM v_dad_clean
WHERE SkinMRI_flag = 1;