### Create Backend Environment
    conda env create -f environment.yml
    conda activate a2_system
    pip install -r requirements.txt

### Install ODBC 17 for SQL Server
    [ODBC 17](https://go.microsoft.com/fwlink/?linkid=2361646)

### Export Backend Environment
    conda activate a2_system
    conda env export --from-history > environment.yml
    pip freeze > requirements.txt

### Backend Unit Test
    pytest app/tests/unit --cov=app --cov-report=term-missing --cov-report=html -v -s

### Backend Integration Test
    pytest app/tests/integration -v -s



