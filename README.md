NCDR Reference
==============

A viewer for the schema of the National Commissioning Data Repository

set up

git clone/mkvirtualenv/pip install -r requirements.txt
./manage.py loaddata data/fixtures/site_description.json

load in all existing csvs (stored in data/csvs)
./manage.py initial_load

for future, loading in csvs
./manage.py csv_loader {{ path to the csv }}

#### TODO
change the csv loader into a form.
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
