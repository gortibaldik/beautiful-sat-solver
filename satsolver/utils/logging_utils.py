import logzero

def set_debug_level(args):
    if args.warning:
        logzero.loglevel(logzero.WARNING)
    elif args.debug:
        logzero.loglevel(logzero.DEBUG)
    else:
        logzero.loglevel(logzero.INFO)