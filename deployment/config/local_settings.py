ALLOWED_HOSTS = [
    'localhost',
{% for key in hostvars.keys() %}
    '{{ key}}',
{% endfor %}
]

SITE_PREFIX = "/ncdr"
