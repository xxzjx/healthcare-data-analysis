# Step 1: generate synthetic data
gen-data:
	python scripts/10_generate_data/generate_synthetic_data.py

# Step 2: load data into sqlite database
sql:
	python scripts/20_load_to_db/load_to_db.py
	python scripts/30_sql_cohorts/apply_sql.py

# step 3: run analysis
analysis:
	python scripts/40_analysis/analyze_skin_mri.py