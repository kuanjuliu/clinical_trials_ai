# import logging
#
# logging.basicConfig(filename="ClinicalTrialsETL.log", filemode="w", format="%(name)s → %(levelname)s: %(message)s")
#
# logging.warning("warning")

import time

start_time = time.time()
prev_time = start_time

# ------------------------------------------------------------------------------
# ClinicalTrials.gov API subdirectories
#
# https://clinicaltrials.gov/data-api/about-api/api-migration#other-all-public-xml
# ------------------------------------------------------------------------------

url = "https://clinicaltrials.gov/api/v2/version"               # Data version
url = "https://clinicaltrials.gov/api/v2/studies/metadata"      # API Definitions
url = "https://clinicaltrials.gov/api/v2/studies/search-areas"
url = "https://clinicaltrials.gov/api/v2/stats/field/values"
url = "https://clinicaltrials.gov/api/v2/stats/field/sizes"
url = "https://clinicaltrials.gov/api/v2/studies"               # Query API endpoints (full studies)
url = "https://clinicaltrials.gov/api/v2/studies"               # Query API endpoints (selected study fields)

# ------------------------------------------------------------------------------
# Download from ClinicalTrials.gov using dlt's REST API Helpers
# ------------------------------------------------------------------------------

import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import JSONResponseCursorPaginator
clinical_trials_client = RESTClient(
    base_url="https://clinicaltrials.gov/api/v2",
    paginator=JSONResponseCursorPaginator(
        cursor_path="nextPageToken",
        cursor_param="pageToken"
    )
)

import sys

@dlt.resource
def clinical_trials():
    i = 1
    s = 0
    page_size = 1000    # ClinicalTrials.gov API v2 default is 0 (=10), max is 1000
    for page in clinical_trials_client.paginate(
        "/studies",
        params={
            "pageSize": page_size,
            "filter.overallStatus": "RECRUITING"
        }
    ):
        yield page
        s += page_size * sys.getsizeof(page)
        print ("Total Records Retrieved:", i * page_size,",", "{:.2f}".format(s / 1024**2), "Total MiB.")
        i += 1


# Create dlt pipeline
import duckdb

# db = duckdb.connect("clinical_trials.duckdb", read_only=False)     # Needed only for in-memory DuckDB database
# db.execute("SET memory_limit='8GB';")  # Resourcing for DuckDB needs to be understood vs where Docker's own memory limits are set
pipeline = dlt.pipeline(
    # import_schema_path="schemas/import",
    # export_schema_path="schemas/export",
    pipeline_name="clinical_trials",
    destination="duckdb",                       # External database file
    # destination=dlt.destinations.duckdb(db),  # In-memory database
    dataset_name="dbo",
)

load_info = pipeline.run(clinical_trials, write_disposition='replace')
# print (load_info)

# Log time
current_time = time.time(); print ("Step Time:", "{:.2f}".format(current_time - prev_time), "secs. Total Time Elapsed:", "{:.2f}".format(prev_time - start_time), "secs."); prev_time = current_time


# ------------------------------------------------------------------------------
# Check DuckDB schema
# ------------------------------------------------------------------------------
# db.sql("DESCRIBE;").show(max_width = 1000, max_rows = 1000)
# db.sql("DESCRIBE dbo.clinical_trials;").show(max_width = 1000, max_rows = 1000)
# db.sql("SELECT _dlt_id, protocol_section__eligibility_module__eligibility_criteria FROM dbo.clinical_trials limit 1").show(max_width = 1000, max_rows = 1000)
# db.sql("SELECT * FROM dbo.clinical_trials limit 1").show(max_width = 10000)

# ------------------------------------------------------------------------------
# Parse out inclusion and exclusion criteria with DBT
# ------------------------------------------------------------------------------

print("Set up DBT model through DLT")
dbt = dlt.dbt.package(pipeline,
                    "dbt_clinical_trials",
)

# Execute DBT models
print ("Execute DBT model")
models = dbt.run_all()

# Save outcomes to db for monitoring
# pipeline.run([models], table_name="loading_status", write_disposition="replace")

# for m in models:
#     print(
#         f"Model {m.model_name} materialized" +
#         f"in {m.time}" +
#         f"with status {m.status}" +
#         f"and message {m.message}")

# Log time
current_time = time.time(); print ("Step Time:", "{:.2f}".format(current_time - prev_time), "secs. Total Time Elapsed:", "{:.2f}".format(prev_time - start_time), "secs."); prev_time = current_time

# # Load the duckdb and query it
print ("Reconnecting to clinical_trials.duckdb ....")
db = duckdb.connect(database='clinical_trials.duckdb', read_only=False)
# print ("Setting DuckDB memory limits lower ....")
# db.execute("SET memory_limit='8GB';")  # Resourcing for DuckDB needs to be understood vs where Docker's own memory limits are set
print ("Exporting inclusion_exclusion_criteria ....")
db.sql("COPY (SELECT * FROM dbo.inclusion_exclusion_criteria) to 'inclusion_exclusion_criteria.csv' (HEADER, DELIMITER '`');")
print ("Closing DuckDB connection")
db.close()
# db_file.sql("SELECT * FROM temp.information_schema.tables").show(max_width = 1000, max_rows = 1000)
# db_file.sql("SELECT * FROM dbo.inclusion_exclusion_criteria LIMIT 10").show(max_width = 300, max_rows = 1000)
