from django.db.backends.mysql.base import DatabaseWrapper as OriginalDatabaseWrapper

class DatabaseWrapper(OriginalDatabaseWrapper):
    def check_database_version_supported(self):
        """ Ignore la vérification de la version MariaDB """
        pass
