NCDR Reference
==============

A viewer for the schema of the National Commissioning Data Repository

## Set Up

### Quick Start

    1. `git clone`
    1. create and active a `virtualenv`
    1. `make setup`
    1. `pre-commit install`


This project uses a few tools which are either not installed via Pip or aren't Python tools.
The project leaves it up to you to decide how to install them.

    1. (Pre-Commit)[https://pre-commit.com]
    1. (Sass)[https://sass-lang.com]


## Running

To update CSS locally:

    sass --watch ncdr/static/css/styles.scss:ncdr/static/css/styles.css


## Deployment

    1. Update hosts.dev.
    2. Set your branch in deployment/group_vars/all
    3. `make deploy-prod` deploys prod, this means setting up back ups and restoring with the latest snapshot.

    It must be run after 19:00 every day when the snap shot is taken. Otherwise the deployment will fail.

    4. `make deploy-dev` deploys , this means no back ups and restoring from the first snap shot it can find from the last 4 days.
    5. The ckan instance has a hard coded link to the NCDR box in the nginx config. Change this to point to your newly deployed instance.
    6. Make sure that the NCDR instance is accessible, that the database is populated and that one can log in.

To view the encrypted variables:

    ansible-vault edit all --vault-password-file ~/.vault.txt



## S3
This project uses an S3 bucket for backups and uploaded CSVs (except when running locally).
An IAM User (with programmatic credentials) has been generated specifically for the v0.5 series.
A policy for the bucket, `ncdr-v0.5`, has been generated to only allow Users to access that bucket.


## TODO
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
