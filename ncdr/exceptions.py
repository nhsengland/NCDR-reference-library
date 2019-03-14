class VersionAlreadyExists(Exception):
    """
    Exception to denote a Version Already Exists based on its files_hash
    """

    def __init__(self, existing_pk, *args, **kwargs):
        self.existing_pk = existing_pk
