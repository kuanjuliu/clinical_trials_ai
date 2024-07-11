## Clinical Trials Eligibility Search with OpenAI

This project loads a database with currently-recruiting clinical trials from [ClinicalTrials.gov](https://clinicaltrials.gov) and produces a delimited file of patient inclusion/exclusion criteria for use with [OpenAI's API](https://platform.openai.com/docs/api-reference/introduction) to help look for trials that patients may be eligible to participate in.

The app is wrapped into a [Docker](https://www.docker.com) container based on the official [Debian Dockerfile for Python 3.12.4](https://github.com/docker-library/python/blob/5ed2758efb58d9acaafa90515caa43edbcfe4c4e/3.12/bookworm/Dockerfile).

It starts by pulling down, via ClinicalTrials.gov's [API](https://github.com/duckdb/dbt-duckdb?tab=readme-ov-file), all clinical trials that are currently recruiting, as JSONs.

It then employs a [dlt](https://dlthub.com) pipeline to auto-generate a schema from the JSONs and write it out to a [DuckDB](http://duckdb.org) database.

Finally, [dbt](http://getdbt.com) is engaged to transform the inclusion/exclusion criteria into the same DuckDB database.

The resulting table is also exported to a csv, and made available locally (outside the Docker container).

### Installation

* Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) locally
* Make sure the Docker Desktop has set the Memory limit to at least 16 GB. Even just the subset of clinical trials that are currently recruiting approaches 70k entries!
![alt text](https://github.com/kuanjuliu/clinical_trials_ai/blob/main/Docker%20Desktop%20Memory%20Requirements.png)
* Clone the repo to your local machine
* From the repo's root directory, build, create, and run the Docker container — as well as execute the Python scripts — by typing:
````
docker compose up
````
* (Note that the data load and schema generation can take around 5 minutes to complete)
* Copy out to your local `app/` folder the `inclusion_exclusion_criteria.csv` file by typing:
````
docker cp ct:/opt/app/ClinicalTrialsETL/inclusion_exclusion_criteria.csv .
````
* If desired, the entire clinical trials DuckDB database can also be pulled out of the Docker container for reuse by typing:
````
docker cp ct:/opt/app/ClinicalTrialsETL/clinical_trials.duckdb .
````

### Training OpenAI to Search for Eligible Clinical Trials

* The goal is to use [OpenAI's API](https://platform.openai.com/docs/api-reference/introduction) to find clinical trials that a given patient is eligibile to participate in
* For this exercise, we limit the scope of the search to:
  * Age
  * Gender
  * Existing Medical Conditions
* Input-Output pairs will be generated to train OpenAI in the meaning of the inclusion/exclusion criteria, namely:
  * Age, gender, and existing medical conditions, if not mentioned explicitly in the eligibility criteria, can be ignored as search parameters
  * Age, gender, and existing medical conditions, if mentioned explicitly in the eligibiilty criteria, must be filtered on/out depending on whether they are in the inclusion/exclusion criteria
* The trained model will be used against the local database to quickly return clinical trials that fit patients in those three characteristics

#### Installation

* TBD
