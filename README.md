# Health Admin Demo (Synthetic DAD & NACRS)

## 1. Install packages
```bash
pip install -r scripts/00_setup_env/requirements.txt
```

## 2. Install sqlite3
Install Homebrew first, then
```bash
brew install sqlite3
```

## 3. Run pipeline
```bash
make gen-data    # generate synthetic CSVs
make sql         # load to SQLite, build views, export tables
make analysis    # run Python analysis (tables + matplotlib)
```

## 5. Run interactive Analysis notebook
Run the notebook in `scripts/40_analysis/skin_mri_analysis_plotly.ipynb`