## Clinical Trials Eligibility Search with OpenAI

This project loads a database with currently-recruiting clinical trials from [ClinicalTrials.gov](https://clinicaltrials.gov) and produces a delimited file of patient inclusion/exclusion criteria for use with [OpenAI's API](https://platform.openai.com/docs/api-reference/introduction) to help look for trials that patients may be eligible to participate in.

The app is wrapped into a [Docker](https://www.docker.com) container based on the official [Debian Dockerfile for Python 3.12.4](https://github.com/docker-library/python/blob/5ed2758efb58d9acaafa90515caa43edbcfe4c4e/3.12/bookworm/Dockerfile).

It starts by pulling down, via ClinicalTrials.gov's [API](https://github.com/duckdb/dbt-duckdb?tab=readme-ov-file), all clinical trials that are currently recruiting, as JSONs.

It then employs a [dlt](https://dlthub.com) pipeline to auto-generate a schema from the JSONs and write it out to a [DuckDB](http://duckdb.org) database.

Finally, [dbt](http://getdbt.com) is engaged to transform the inclusion/exclusion criteria into the same DuckDB database.

The resulting table is also exported to a csv, and made available locally (outside the Docker container).

### Installation

* Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) locally, and start it
* Make sure the Docker Desktop has set the Memory limit to at least 16 GB. Even just the subset of clinical trials that are currently recruiting approaches 70k entries!
![alt text](https://github.com/kuanjuliu/clinical_trials_ai/blob/main/Docker%20Desktop%20Memory%20Requirements.png)
* Clone the repo to your local machine
* From the repo's root directory, build, create, and run the Docker container — as well as execute the Python scripts — by typing:
````
docker compose up
````
* (Note that the data load and schema generation can take around 5 minutes to complete)
* Find out the name of the live container:
````
docker ps
````
* In this case, the container's name is `clinical_trials_ai-ct-1`:
````
CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS          PORTS     NAMES
81184729928f   clinical_trials_ai-ct   "python3 ClinicalTri…"   8 minutes ago   Up 48 seconds             clinical_trials_ai-ct-1
````
* Restart the container you found above if necessary:
````
docker restart clinical_trials_ai-ct-1
````
* You can now copy the `inclusion_exclusion_criteria.csv` file out to your (local) repo's root folder by typing:
````
docker cp clinical_trials_ai-ct-1:/opt/app/ClinicalTrialsETL/inclusion_exclusion_criteria.csv .
````
* Similarly, the raw clinical trials DLT -> DuckDB database can also be pulled out of the Docker container for reuse locally by typing:
````
docker cp clinical_trials_ai-ct-1:/opt/app/ClinicalTrialsETL/clinical_trials.duckdb .
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

#### Installation of OpenAI

* TBD

### Aspirations

* Gain a better understanding of which clinical trials are likely to be of interest to patients today, for example if we can ignore trials where the last status date was many years in the past
* Assign more accurate data types to each column (not just VARCHAR) to assist in training OpenAI
* Speed
  * The ClinicalTrials.gov database and its DBT transformation should be executed once for all clients and the resulting database mounted as an external source (say, on GCP) in whichever Docker container needs it. This would eliminate 99% of the time this project takes to execute, along with some of the runtime memory pressures.
  * Modularize the running of DBT, perhaps into its own container, so as to better tailor its performance needs independently
* Continuously train OpenAI on an increasingly granular set of patient characteristics to improve relevance of search results and speed of returning them. After all the set of clinical trials is finite and changes only very slowly
