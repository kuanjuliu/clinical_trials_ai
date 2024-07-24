import duckdb

def export_criteria(db_name = 'clinical_trials.duckdb', delimiter='`'):
    print("Reconnecting to " + db_name + " ....")
    db = duckdb.connect(database=db_name, read_only=False)
    print("Exporting inclusion_exclusion_criteria ....")
    db.sql("COPY (SELECT * FROM dbo.inclusion_exclusion_criteria) to 'inclusion_exclusion_criteria.csv' (HEADER, DELIMITER '" + delimiter + "');")
    print("Closing DuckDB connection")
    db.close()
