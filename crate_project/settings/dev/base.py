from ..base import *

DEBUG = True
TEMPLATE_DEBUG = True

SERVE_MEDIA = DEBUG

SITE_ID = 1

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

MIDDLEWARE_CLASSES += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += [
    "debug_toolbar",
    "devserver",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEVSERVER_ARGS = [
    "--dozer",
]

DEVSERVER_IGNORED_PREFIXES = [
    "/site_media/",
]

DEVSERVER_MODULES = [
    # "devserver.modules.sql.SQLRealTimeModule",
    "devserver.modules.sql.SQLSummaryModule",
    "devserver.modules.profile.ProfileSummaryModule",

    # Modules not enabled by default
    "devserver.modules.ajax.AjaxDumpModule",
    "devserver.modules.cache.CacheSummaryModule",
    "devserver.modules.profile.LineProfilerModule",
]

# Configure Celery
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"
BROKER_PASSWORD = None
BROKER_POOL_LIMIT = 10

CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_PASSWORD = None

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "crate-dev",
    },
}

SIMPLE_API_URL = "https://simple.crate.io/"

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    'haystack.panels.HaystackDebugPanel',
)

AWS_STATS_LOG_REGEX = "^cloudfront/dev/packages/"
