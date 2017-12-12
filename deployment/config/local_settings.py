ALLOWED_HOSTS = [
    'localhost',
    "{{ hostvars['webserver'] }}"
]
