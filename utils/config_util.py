"""This module is for getting the parameters and credentials from the config json file."""

import os
import json

def get_config():
    """Function to get the configuration values
    (Discord Token, database URL) from the json file.
    """

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    with open(f'{directory}/config.json') as jsonfile:
        file_reader = json.load(jsonfile)
        return file_reader.get("token", None)

def get_prefix(cog_prefixes):
    """Function to get the bot prefix in Discord."""

    final_prefixes_list = []
    
    #Add default prefix
    final_prefixes_list.append(".")

    # #Add prefixes for all cogs (have to convert the args value to list again)
    cog_prefixes_list = list(cog_prefixes)
    for prefix in cog_prefixes_list:
        final_prefixes_list.append(prefix)
    return final_prefixes_list

def get_db_params():
    """Function to get the database configuration values
    from the json file.
    """

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    with open(f'{directory}/config.json') as jsonfile:
        file_reader = json.load(jsonfile)
        return file_reader.get("db_params", None)
