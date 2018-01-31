ALLOWED_HOSTS = [
    'localhost',
{% for key in hostvars.keys() %}
    '{{ key}}',
{% endfor %}
]

# DEBUG = False
# SITE_PREFIX = "/ncdr"
