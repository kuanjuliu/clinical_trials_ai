import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import JSONResponseCursorPaginator
import duckdb
import sys

class ClinicalTrialsEndpoints:
    """
    Class containing the endpoints for the ClinicalTrials.gov API.
    """
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    VERSION = "/version"
    METADATA = "/studies/metadata"
    SEARCH_AREAS = "/studies/search-areas"
    FIELD_VALUES = "/stats/field/values"
    FIELD_SIZES = "/stats/field/sizes"
    STUDIES = "/studies"


def setup_clinical_trials_client():
    """
    Set up and return a RESTClient for the ClinicalTrials.gov API.

    Returns:
        RESTClient: Configured client for making API requests.
    """
    return RESTClient(
        base_url=ClinicalTrialsEndpoints.BASE_URL,
        paginator=JSONResponseCursorPaginator(
            cursor_path="nextPageToken",
            cursor_param="pageToken"
        )
    )


def setup_data_pipeline():
    """
    Set up and return a DLT data pipeline for clinical trials data.

    Returns:
        dlt.Pipeline: Configured pipeline for processing clinical trials data.
    """
    return dlt.pipeline(
        pipeline_name="clinical_trials",
        destination="duckdb",
        dataset_name="dbo",
    )

def fetch_clinical_trials(pipeline):
    """
    Fetch clinical trials data and process it through the given pipeline.

    Args:
        pipeline (dlt.Pipeline): The pipeline to process the data.

    Returns:
        dlt.pipeline.RunResult: The result of running the pipeline.
    """
    @dlt.resource
    def clinical_trials(page_size=1000):
        """
        Generator function to fetch clinical trials data page by page.

        Args:
            page_size (int): Number of records per page. Defaults to 1000.

        Yields:
            dict: A page of clinical trials data.
        """
        client = setup_clinical_trials_client()
        record_count = 0
        total_size = 0

        for page in client.paginate(
            ClinicalTrialsEndpoints.STUDIES,
            params={
                "pageSize": page_size,
                "filter.overallStatus": "RECRUITING"
            }
        ):
            yield page
            record_count += page_size
            total_size += sys.getsizeof(page)
            print(f"Total Records Retrieved: {record_count}, {total_size / 1024**2:.2f} Total MiB.")

    return pipeline.run(clinical_trials(), write_disposition='replace')
