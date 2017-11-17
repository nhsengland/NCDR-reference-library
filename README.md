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
sass --watch csv_schema/static/css/styles.scss:csv_schema/static/css/styles.css

#### TODO
change the csv loader into a form.
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
