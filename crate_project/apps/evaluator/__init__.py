from evaluator.evaluators import suite


def autodiscover():
    """
    Auto-discover INSTALLED_APPS evaluators.py modules and fail silently when
    not present. This forces an import on them to register any evaluators they
    may want.
    """

    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try:
            import_module("%s.evaluators" % app)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, "evaluators"):
                raise
