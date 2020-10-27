import logging
import os
from typing import Optional

import myNotebook as nb

try:
    import tkinter as tk
    from tkinter import ttk
except:
    import Tkinter as tk
    import ttk

from config import appname, config

# This could also be returned from plugin_start3()
plugin_name = os.path.basename(os.path.dirname(__file__))

# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
logger = logging.getLogger(f'{appname}.{plugin_name}')

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(
        f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

edma_Active: Optional[tk.IntVar] = None


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[
    tk.Frame]:
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    global edma_Active
    edma_Active = tk.IntVar(value=config.getint(
        "EDMA-Active"))  # Retrieve saved value from config
    frame = nb.Frame(parent)
    nb.Label(frame, text="Active").grid()
    nb.Checkbutton(frame, text="Active", variable=edma_Active).grid()

    return frame


def prefs_changed() -> None:
    """
    Save settings.
    """
    config.set('MyPluginSetting',
               edma_Active.get())  # Store new value in config


def plugin_start3(plugin_dir: str) -> str:
    logger.info(f"Loaded {plugin_name} from directory {plugin_dir}")
    return "ED-MA"


def plugin_stop() -> None:
    """
    EDMC is closing
    """
    logger.info("closing time")
    return
