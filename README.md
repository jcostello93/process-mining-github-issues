# Process Mining GitHub Issues

This project used PM4PY to apply Process Mining techniques to analyze GitHub Issues from GitHub repositories. It consists of an ELT pipeline to extract GitHub Issues data and land an XES event log
in S3, and a Streamlit application to create and event process mining artifacts.

The project was developed as part of a master's thesis in software engineering and aims to explore how techniques from the field of process mining can provide insights into the workflows of software projects hosted on GitHub.

## Installation

Set up the repository and dependencies:

``` bash
git clone https://github.com/jcostello93/process-mining-github-issues.git
cd process-mining-github-issues
pip install -r requirements.txt
```

Required env variables:
``` bash
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
S3_BUCKET
GH_PAT
```

Run the ELT pipeline:

``` bash
python src/data_pipeline/full_elt.py --owner <owner> --repo <repo>
```

Run the Streamlit app:

``` bash
streamlit run src/app/app.py
```