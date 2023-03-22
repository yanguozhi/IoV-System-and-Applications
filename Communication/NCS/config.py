import os
import configparser


def read_config(section, key=None):
    root_path = os.path.abspath(os.path.dirname(__file__))
    config = configparser.ConfigParser()
    config.read(root_path + "\\config.conf")
    value = config.get(section, key)
    return value
