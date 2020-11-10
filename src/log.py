import logging
import logging.handlers
from importlib import reload
import os

import config

def setupLog(config : config.Config = None, initialLogger : bool =False):
  """ init function of the Log class """
  log : logging.Logger = None

  logfile = "/dev/stdout"
  loglevel = 10
  logformat = "[%(asctime)s]--[%(levelname)-8s]  %(message)s"
  logMaxBytes = 2e7
  logBackupCount = 10

  if not initialLogger:
    # reaload the logging module to configure it with the actual configuration
    logging.shutdown()
    reload(logging)

    # get the logfile, level and format from the config
    if config:
      logfile = config.logFile
      loglevel = config.logLevel
      logformat = config.logFormat
      logMaxBytes = config.logMaxBytes
      logBackupCount = config.logBackupCount

  # opening /dev/stdout with a (append) will cause errors on some platforms (TODO)
  if logfile == "/dev/stdout":
    mode = "w"
  else:
    mode = "a"

  # initialise the logger
  log = logging.getLogger("mainlog")
  log.setLevel(loglevel)

  # remove all installed handlers
  log.handlers = []
    
  # open a file handler
  try:
    # do not do log rotation when logging to stdout
    if logfile == "/dev/stdout":
      fh = logging.FileHandler(logfile, mode=mode)
    else:
      fh = logging.handlers.RotatingFileHandler(logfile, mode=mode, maxBytes=logMaxBytes, backupCount=logBackupCount)
  except Exception as e:
    logging.error("Error opening logfile '%s'!" % logfile)
    logging.exception(e)

    return None

  # configure the file handler
  fh.setLevel(loglevel)
  fmt = logging.Formatter(logformat)
  fh.setFormatter(fmt)

  # install the file handler and disable the default one
  log.addHandler(fh)
  log.propagate = False

  return log
