# Service for analyse pdf science articles


Service was build on FastAPI and implement:

* Challenge A: responds with "hello world" when the "/" endpoint is hit
* Challenge B: accept a PDF file upload and return the number of pages in the document
* Challenge C: accept a [link](https://arxiv.org/pdf/2101.08809) to an Arxiv research paper and return the text content of each page as a JSON array

> Example response => { “text”: [“page 1 text”, “page 2 text”, ...] }

* Challenge D: a rule-based engine to classify content blocks within each page of the PDF using these predefined 
classes (see Cheat Sheet). Return the classifications as JSON.

> Example JSON schema => { “output”: [{ “title”: “Abstract”, ... }, {“title”: “Introduction” ... }, {...} ] }

* Challenge E: enhance the overall parsing quality of each page and also extract tables from the PDF as both images and
text, and return those in your JSON response.

> Note: To accomplish table extraction, you may either write your own
software, use closed/open source software, or use open/closed models

* Challenge F: replace your rules-engine with a DNN, LLM, or any combo models. You may train your own model. 
Return the classifications as your JSON response

* Challenge G: meet or exceed the performance on the provided dataset of papers and their corresponding JSON output.

> The dataset can be downloaded with the following command 'gsutil -m cp -r gs://cdn.bytez.com/technical-assessment-dataset'.


## Technology description

There are two main PDF processors were implemented:

* Simple PDF processor on PyMuPDF and rule-based approach (include table extraction)
* RAG + LLM PDF processor, based on llama3 model for QA sessions and bge-m3 as embedder for RAG


**Service include next main code blocks:**

`src/containers/container.py` with conteiners for dependency injectors, include:
* `Config` - to upload [config.yaml](configs/config.yaml) configuration from file
* `Simple Predictor` - singletone container to process pdf files data, wired with [pdf_utils.py](src/services/pdf_utils.py).
* `LLM Predictor` - singletone container to use RAG + LMM to analyze pdf file data, wired with [pdf_utils.py](src/services/pdf_utils.py). Preload model when container start.
* `PDF Processor` - singletone container to manipulate income data from API handlers (routs), wired with [pdf_process.py](src/services/pdf_process.py).

`src/routes/test_routs.py` with all API handlers, which serving GET and POST requests with asynchronous calculations.

`app.py` contain FastAPI application, which have 6 handles:
1. `/` - return 'hello world'.
2. `process_pdf` - get pdf file and return number of pages.
3. `process_arxiv_url` - get Arxiv URL to extract text from pages
3. `process_simple` - get Arxiv URL or pdf file to process with simple rule-based approach.
3. `process_tables` - get Arxiv URL or pdf file to extract table's text and image with classic approach from PyMuPDF.
3. `process_llm_rag` - get Arxiv URL or pdf file to process with LLM.

`src/container_task.py` contain example of calculating procedure.


**Used technologies:**

* FastAPI
* Dependencies injector containers
* CI/CD (test, deploy, destroy) - mainly for GitLab
* Ollama
* PyMuPDF
* Docker
* Pytest - unit & integration tests with coverage report
* Linters (flake8 + wemake)


**Location for manual test:**

* https://pdf_api.lydata.duckdns.org
* docs https://pdf_api.lydata.duckdns.org/docs


## Setup of environment

1. First, change python interpreter in `SYSTEM_PYTHON` variable in Makefile.
2. Install python venv, requirements and ollama with 
    ```bash
    make install
    ```
3. Pull ollama models with 
    ```bash
    make download_models
    ```


## Commands

* `make run_app` - run servie locally. You can define argument `APP_PORT`
* `make lint` - run linters (flake8, pylint)
* `make run_unit_tests` - run unit tests
* `make run_integration_tests` - run integration tests
* `make run_all_tests` - run all tests
* `make generate_coverage_report` - generate test coverage report
* `make build` - build Docker image, you can define arguments `DOCKER_TAG`, `DOCKER_IMAGE`
* `make docker_run` - run API service in Docker, you can define arguments `DOCKER_NAME`, 'APP_PORT'


## Disclaimers

* This is a small test project, which can be improved by:
  * modify rule-based pdf analyses with more accurate conditions
  * apply Computer Visions and OCR techniques to split pdf pages into blocks, which can be much more accurate and reliable, than exist pdf analyzers
  * apply cache techniques and DB to store pdf analyses results
  * apply Jinja2Template demo
* the project CI/CD was originally crated in GitLab local instance, some repo functionality may be unavailable
* images are return in `byte64` format, you can check them [here](https://base64.guru/converter/decode/image)


## TODO:

1. Delete or save uploaded pdf files to DB
2. Implement upload zip files 
3. Add Jinja2Template demo
4. Add NGINX configuration
5. Implement automatic deploy and destroy through CitHub CI/CD
6. Implement detection technique to analyse pdf elements, they coordinates and shapes
7. Implement OCR technique to analyze text data into pdf elements
