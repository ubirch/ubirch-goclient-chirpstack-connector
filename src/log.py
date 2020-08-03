import logging
from importlib import reload

import config


def setupLog(config : config.Config = None, default_logfile : str ="/dev/stdout", initialLogger : bool =False):
  """ init function of the Log class """
  log : logging.Logger = None

  logfile = default_logfile
  loglevel = 10
  logformat = "[%(asctime)s]--[%(levelname)-8s]  %(message)s"

  # opening /dev/stdout with a will cause errors on some platforms
  if default_logfile == "/dev/stdout":
    mode = "w"
  else:
    mode = "a"

  if not initialLogger:
    # reaload the logging module to configure it with the actual configuration
    logging.shutdown()
    reload(logging)

    # get the logfile, level and format from the config
    if config:
      logfile = config.logFile
      loglevel = config.logLevel
      logformat = config.logFormat

  # initialise the logger
  log = logging.getLogger("mainlog")
  log.setLevel(loglevel)
    
  # open a file handler
  try:
    fh = logging.FileHandler(logfile, mode=mode)
  except Exception as e:
    logging.error("Error opening logfile '%s'!" % logfile)
    logging.exception(e)

    return None

  # configure the file handler
  fh.setLevel(loglevel)
  fmt = logging.Formatter(logformat)
  fh.setFormatter(fmt)

  # install the file handler
  log.addHandler(fh)

  return log
