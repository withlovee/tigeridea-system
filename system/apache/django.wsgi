import os
import sys

sys.path.append('/home/ubuntu/tigeridea-system/system')
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'system.settings'
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
