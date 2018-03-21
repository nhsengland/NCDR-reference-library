NCDR Reference
==============

A viewer for the schema of the National Commissioning Data Repository

set up

git clone/mkvirtualenv/pip install -r requirements.txt
./manage.py loaddata data/fixtures/site_description.json

load in all existing csvs (stored in data/csvs)
./manage.py initial_load

for future, loading in csvs
./manage.py row_loader {{ path to row csv }}
./manage.py table_loader {{ path to the table csv }}

When running the server locally, we are using sass. So installl sass and run
<!-- sass --watch csv_schema/static/css/styles.scss:csv_schema/static/css/styles.css -->

#### deployment
update hosts.dev (and use keys natch)
set your branch in deployment/group_vars/all
cd deployment
ansible-playbook setup-server.yml -i hosts.dev --vault-password-file ~/.vault.txt

to view the encrypted variables
ansible-vault edit all --vault-password-file ~/.vault.txt


#### loading in new files.
We currently accept 3 csv files.

1. Columns
A file that contains all the information about NCDR references. These are columns
that exist in multiple tables and carry the same information.

2. Database and Tables
These contain information about the details and tables. For example descriptions
and display names.

3. Mappings
These contain information about the Mappings and Groupings of different columns.



#### TODO
change the csv loader into a form.
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
