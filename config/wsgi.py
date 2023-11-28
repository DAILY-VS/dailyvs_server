import os
# 추가
import site
from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
# 추가
site.addsitedir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

application = Sentry(get_wsgi_application())