from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from enroll import signals #register signals

def import_class(path):
    module, attr = path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        class_ = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s"' % (module, attr))
    return class_
