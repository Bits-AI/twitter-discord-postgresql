"""This module is for handling the utility functions for Twitter cog module."""

import os
import json
from datetime import datetime, timedelta
from utils.logging import logger

def get_twitter_credentials():
    """Function to retrieve the required OAuth 
    and access token for Twitter API.
    """

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    with open(f"{directory}/config.json") as jsonfile:
        file_reader = json.load(jsonfile)

        return (
            file_reader.get("TwitterOAuth1", ""),
            file_reader.get("TwitterOAuth2", ""),
            file_reader.get("TwitterToken1", ""),
            file_reader.get("TwitterToken2", "")
        )

def get_twitter_target():
    """Function to retrieve the twitter target url."""

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    with open(f"{directory}/config.json") as jsonfile:
        file_reader = json.load(jsonfile)

        return (
            file_reader.get("twitter_url", "")
        )

def get_twitter_id():
    """Function to retrieve the twitter user id."""

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    with open(f"{directory}/config.json") as jsonfile:
        file_reader = json.load(jsonfile)

        return (
            file_reader.get("twitter_id", "")
        )

async def _tweet_handler(conn, twitter_id, api, url):
    """Main function for Twitter monitoring."""

    try:
        #Get the tweet ID for the last post saved in db
        last_post_id, twitter_name = await _get_db_data(conn, twitter_id)

        if last_post_id == "Failed":
            return "Failed"

        #Get the latest tweet ID from Twitter API
        new_post_id = await _get_tweet_data(twitter_id, api, last_post_id, twitter_name)

        #If there is no new tweet, only update the timestamp in db
        if new_post_id is None:
            db_res = await _update_db_data(
                conn, twitter_id, api
            )

            if db_res == "Failed":
                return "Failed"
            
            return None

        #If there is new tweet, update the data in db and return the tweet url
        db_res = await _update_db_data(
            conn, twitter_id, api, new_post_id
        )

        if db_res == "Failed":
            return "Failed"

        new_url = await _get_post_url(url, new_post_id)

        return new_url

    except Exception as error:
        logger.error(f"Error: {type(error).__name__}: {error}")
        return "Failed"

async def _get_db_data(conn, twitter_id):
    """Get the user data from database,
    returns last_post_id and twitter name.
    """

    try:
        result = await conn.fetch(
            """
            SELECT last_post_id, name
            FROM twitter
            WHERE id = $1
            """,
            twitter_id
        )

        if result:
            for i in result:
                last_post_id = '' if i[0] is None else i[0].strip()
                twitter_name = '' if i[1] is None else i[1].strip()
            
            return last_post_id, twitter_name

    except Exception as error:
        logger.error(f"Error: {type(error).__name__}: {error}")
        return "Failed"

async def _get_tweet_data(twitter_id, api, last_post_id, twitter_name):
    """Pull the tweet data from Twitter API,
    compare the latest tweet ID with the ID stored in db.
    """

    try:
        #Set new post id variable default to value None
        new_post_id = None

        #Initialize the twitter timeline by following tweepy specs
        timeline = api.user_timeline(user_id=twitter_id, exclude_replies=True, include_rts=False, count="1")

        for tweet in timeline:
            #Compare the current tweet id with the last tweet id (Experimental with new Tweepy)
            if tweet.id_str != last_post_id:
                new_post_id = tweet.id_str

        return new_post_id

    except Exception as error:
        logger.error(f"Error: {type(error).__name__}: {error}")
        return None

async def _update_db_data(conn, twitter_id, api, new_post_id=None):
    """Function to update the twitter database table."""

    try:
        #If no new tweet is found, update the timestamp only
        if new_post_id is None:
            await conn.execute(
                """
                UPDATE twitter
                SET last_api_call = $1
                WHERE id = $2
                """,
                datetime.utcnow() + timedelta(hours=8),
                twitter_id
            )
        
        #If new tweet is found, update the data
        else:
            await conn.execute(
                """
                UPDATE twitter
                SET last_post_id = $1,
                last_api_call = $2
                WHERE id = $3
                """,
                new_post_id, datetime.utcnow() + timedelta(hours=8),
                twitter_id
            )

        return "OK"

    except Exception as error:
        logger.error(f"Error: {type(error).__name__}: {error}")
        return "Failed"

async def _get_post_url(url, new_post_id):
    """Craft and return a string with the twitter URL
    for Discord to automatically generates embed.
    """

    new_url = f"{url}{new_post_id}"
    return new_url
    