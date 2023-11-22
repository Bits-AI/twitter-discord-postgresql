"""This module is for creating Postgres database connection pool with asyncpg."""

import asyncpg
import ssl
from utils import config_util

async def create_pool():
    """Function to create Postgres connection pool."""

    #Create the SSL parameters for Heroku
    # param = ssl.create_default_context(cafile="")
    # param.check_hostname = False
    # param.verify_mode = ssl.CERT_NONE

    pool = await asyncpg.create_pool(
        config_util.get_db_params(),
        command_timeout=10,
        min_size=1,
        max_size=20,
        max_inactive_connection_lifetime=10.0,
        # ssl=param
        )

    conn = await pool.acquire()
    return conn, pool
    