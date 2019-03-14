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


To import new CSVs via the web form, run the Queue worker:

    python rq_worker


## Deployment

    1. update hosts.dev (and use keys natch)
    1. set your branch in deployment/group_vars/all
    1. create .vault.txt and put the vault password in there
    1. `make deploy`

To view the encrypted variables:

    ansible-vault edit all --vault-password-file ~/.vault.txt



## S3
This project uses an S3 bucket for backups and uploaded CSVs (except when running locally).
An IAM User (with programmatic credentials) has been generated specifically for the v0.5 series.
A policy for the bucket, `ncdr-v0.5`, has been generated to only allow Users to access that bucket.


## TODO
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
