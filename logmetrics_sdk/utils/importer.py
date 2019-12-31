import importlib


class LazyImport:
    """
    Lazy import a module. The module is only imported when an attribute is accessed.
    """
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None

    def __getattr__(self, name):
        if self.module is None:
            self.module = importlib.import_module(self.module_name)
        return getattr(self.module, name)
