import dlt

def run_dbt_models(pipeline):
    """
    Run DBT models using the provided pipeline.

    This function sets up and executes DBT models through DLT (Data Loading Tool).
    It prints the progress and can optionally print detailed execution information
    for each model.

    Args:
        pipeline: The DLT pipeline object to use for running DBT models.

    Returns:
        None
    """
    print("Set up DBT model through DLT")
    dbt = dlt.dbt.package(pipeline, "dbt_clinical_trials")

    print("Execute DBT model")
    models = dbt.run_all()

    # Uncomment the following lines if you want to print model execution details
    # for m in models:
    #     print(
    #         f"Model {m.model_name} materialized " +
    #         f"in {m.time} " +
    #         f"with status {m.status} " +
    #         f"and message {m.message}"
    #     )
