import duckdb

def export_criteria(db_name='clinical_trials.duckdb', delimiter='`'):
    """
    Export certain inclusion and exclusion criteria from a DLT-pipelined DuckDB database extracted from
    ClinicalTrials.gov to a CSV file.

    This function connects to a specified DuckDB database, exports the contents of the
    'inclusion_exclusion_criteria' table to a CSV file, and then closes the database connection.

    By default, the '`' delimiter is used to avoid overlap with other characters in the database.

    Args:
        db_name (str): The name of the DuckDB database file. Defaults to 'clinical_trials.duckdb'.
        delimiter (str): The delimiter to use in the CSV file. Defaults to '`'.

    Returns:
        None
    """
    print("Reconnecting to " + db_name + " ....")
    db = duckdb.connect(database=db_name, read_only=False)
    print("Exporting inclusion_exclusion_criteria ....")
    db.sql("COPY (SELECT * FROM dbo.inclusion_exclusion_criteria) to 'inclusion_exclusion_criteria.csv' (HEADER, DELIMITER '" + delimiter + "');")
    print("Closing DuckDB connection")
    db.close()
