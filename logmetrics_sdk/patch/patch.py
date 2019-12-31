
import logging
import importlib

log = logging.getLogger(__name__)


SUPPORTED_MODULES = (
    'requests'
)

_PATCHED_MODULES = set()


def patch_backend():
    patch(SUPPORTED_MODULES, raise_errors=False)


def patch(modules_to_patch, raise_errors=True):
    if isinstance(modules_to_patch, str):
        modules_to_patch = [modules_to_patch]
    modules = set()
    for module_to_patch in modules_to_patch:
            modules.add(module_to_patch)
    for m in modules:
        _patch_module(m, raise_errors)


def _patch_module(module_to_patch, raise_errors=True):
    try:
        _patch(module_to_patch)
    except KeyError:
        if raise_errors:
            raise
        log.debug('failed to patch module %s', module_to_patch)


def _patch(module_to_patch):

    path = 'logmetrics_sdk.patch.%s' % module_to_patch

    if module_to_patch in _PATCHED_MODULES:
        log.debug('%s already patched', module_to_patch)
        return

    imported_module = importlib.import_module(path)
    imported_module.patch()

    _PATCHED_MODULES.add(module_to_patch)
    log.info('successfully patched module %s', module_to_patch)
