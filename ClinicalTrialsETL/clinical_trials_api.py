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
    return RESTClient(
        base_url=ClinicalTrialsEndpoints.BASE_URL,
        paginator=JSONResponseCursorPaginator(
            cursor_path="nextPageToken",
            cursor_param="pageToken"
        )
    )


def setup_data_pipeline():
    return dlt.pipeline(
        pipeline_name="clinical_trials",
        destination="duckdb",
        dataset_name="dbo",
    )

def fetch_clinical_trials(pipeline):
    @dlt.resource
    def clinical_trials(page_size=1000):
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
