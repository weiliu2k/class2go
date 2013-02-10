from c2g.readonly import get_database_considering_override

class CeleryDBRouter(object):
    """
        A router to control all database operations on models in the
        djcelery application.
    """
    def db_for_read(self, model, **hints):
        """
            Attempts to read djcelery models go to celery.
        """
        if model._meta.app_label == 'djcelery':
            return 'celery'
        return None
    
    def db_for_write(self, model, **hints):
        """
            Attempts to write djcelery models go to celery.
            """
        if model._meta.app_label == 'djcelery':
            return 'celery'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
            Allow relations if a model in the djcelery app is involved as both parties.
            """
        if obj1._meta.app_label == 'djcelery' and \
           obj2._meta.app_label == 'djcelery':
            return True
        return None
    
    def allow_syncdb(self, db, model):
        """
            Make sure the djcelery app only appears in the 'celery'
            database and no where else.  Plus allow south to sync
            celery db for necessary migrations
            """
        if db == 'celery':
            return model._meta.app_label in ('djcelery', 'south',)
        elif model._meta.app_label == 'djcelery':
            return False
        return None


class ReadonlyDBRouter(object):
    """
    Router to enable a request to go against our readonly database.  Two features:
    1. prevent syncdb from being run on the readonly DB
    2. Use override value set by the use_readonly_db decorator to override db
    """
    def db_for_read(self, model, **hints):
        return get_database_considering_override()

    def allow_syncdb(self, db, model):
        override = get_database_considering_override()
        if db == 'readonly' or override == 'readonly':
            return False
        else:
            return None
