### Create Backend Environment
conda env create -f environment.yml
conda activate a2_system
pip install -r requirements.txt

### Export Backend Environment
conda activate a2_system
conda env export --from-history > environment.yml
pip freeze > requirements.txt
