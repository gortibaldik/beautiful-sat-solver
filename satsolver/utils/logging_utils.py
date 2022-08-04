import logzero

def set_debug_level(*, warning=False, debug=False):
    if warning:
        logzero.loglevel(logzero.WARNING)
    elif debug:
        logzero.loglevel(logzero.DEBUG)
    else:
        logzero.loglevel(logzero.INFO)