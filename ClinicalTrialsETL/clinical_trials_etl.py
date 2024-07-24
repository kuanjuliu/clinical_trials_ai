# clinical_trials_etl.py

from clinical_trials_api import ClinicalTrialsEndpoints, setup_data_pipeline, fetch_clinical_trials
from data_transforms import run_dbt_models
from data_export import export_criteria

def main():
    """ Main function to run the ETL process from ClinicalTrials.gov

    • Sets up DLT pipeline and REST client to ClinicalTrials.gov
    • Fetches clinical trials data from ClinicalTrials.gov
    • Processes clinical trials data using DBT
    • Exports a certain subset of clinical trials data to CSV with a special '`' delimiter
    """

    # Set up the database
    pipeline = setup_data_pipeline()

    # Fetch and load clinical trials data
    load_info = fetch_clinical_trials(pipeline)

    # Process clinical trials data using DBT
    run_dbt_models(pipeline)

    # Export processed data
    export_criteria()


if __name__ == "__main__":
    main()

