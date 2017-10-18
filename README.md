NCDR Reference
==============

A viewer for the schema of the National Commissioning Data Repository

set up

git clone/mkvirtualenv/pip install -r requirements.txt
./manage.py loaddata data/fixtures/site_description.json

When we've decided what the finished version of the description should be ./manage.py dumpdata csv_schema.SiteDescription > data/fixtures/site_description.json

loading in csvs
./manage.py csv_loader {{ path to the csv }}

#### TODO
change the csv loader into a form.
add in a search function, but lets find out which columns to query
make the table look more like https://data.england.nhs.uk/dataset?
