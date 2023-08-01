import time
import json
import redis
import psycopg2
from keeper.connections import *
from keeper.environments import SystemEnv
from utility import utils
from utility import database
from loguru import logger


def get_hist_state():
    # Perform get the historical state of slot from database -> return: dict
    hist_state = {}
    try:
        # Get data from the database
        data = utils.get_data_from_psql()
        # Get state of slots
        for item in data:
            slot_id, _, start_time, end_time, status = item
            if slot_id not in hist_state:
                hist_state[slot_id] = {"start_time": start_time, "end_time": end_time, "status": status}
                continue
            hist_state[slot_id] = {"start_time": start_time, "end_time": end_time, "status": status}
        return hist_state

    except Exception as e:
        logger.info("[observer] Did not get the historical state of slot from DB caused by {}".format(e))
        return


def get_curr_state():
    # Perform get the current state of slot from redis -> return: dict
    curr_state = {}
    try:
        curr_state = utils.get_data_from_redis()
        return curr_state

    except Exception as e:
        logger.info("[observer] Did not get the historical state of slot from DB caused by {}".format(e))
        return


def check_slot_status(hist_state, curr_state):
    update_state = []
    if (hist_state is None) or (curr_state is None):
        return

    # Convert the curr_state which read from redis to a new data with type: int
    curr_state = {int(k): int(v) for k, v in curr_state.items()}

    for slot_id in curr_state:
        curr_slot_state = curr_state.get(slot_id)
        hist_slot_state = hist_state.get(slot_id).get("status")

        if curr_slot_state != hist_slot_state:
            start_time = hist_state.get(slot_id).get("start_time")
            end_time = hist_state.get(slot_id).get("end_time")

            # The state of slot changed from empty to busy corresponding to 0 -> 1
            if (hist_slot_state == 0) and (curr_slot_state == 1):
                start_time = int(time.time())
            # The state of slot changed from busy to empty corresponding to 1 -> 0
            if (hist_slot_state == 1) and (curr_slot_state == 0):
                end_time = int(time.time())

            # Get only the slots which changed status
            update_state.append({
                "slot_id": slot_id,
                "location": str(slot_id),  # Need add the information as tuple represents for (x, y) coordinates
                "start_time": start_time,
                "end_time": end_time,
                "status": curr_slot_state
            })

    # Convert to a list of 5-tuple items
    update_state = [(item.get("slot_id"), item.get("location"),
                     item.get("start_time"), item.get("end_time"),
                     item.get("status")) for item in update_state]

    return update_state


def update_info(update_state):
    """
    :param
    data =  [
        {"slot_id": <int>, "start_time": <timestamp>, "end_time": <timestamp>},
        ...
        {"slot_id": <int>, "start_time": <timestamp>, "end_time": <timestamp>},
    ]
    :return: response: message - {dict}
    """
    # Update the information of slot which changed when compare between the historical state and current state
    # The tart_time and end_time represent for "0 -> 1" and "1 -> 0
    if not update_state:
        logger.info("[observer] The update_data is invalid!")
        return
    try:
        resp = utils.update_data_to_psql(update_state)
        return resp

    except Exception as e:
        logger.info("[observer] Did not update the state of slot into PostgreSQL caused by {}".format(e))
        return


def execute():
    window_time = SystemEnv.time_interval
    num_slots = SystemEnv.num_slots
    # Initialize the default slots
    logger.info("[observer] Initialize the {} default slots".format(num_slots))
    database.init_default_slot()

    while True:
        logger.info("Starting at the time: ", int(time.time()))
        hist_state = get_hist_state()
        curr_state = get_curr_state()
        update_state = check_slot_status(hist_state=hist_state, curr_state=curr_state)
        if update_state:
            logger.info("The changed slots which have the slot_id are: {}".format(
                [item[0] for item in update_state])
            )
            resp = update_info(update_state)
            if resp is not None:
                logger.info("[observer] Result of the update information: {}".format(resp.get("message")))
        time.sleep(window_time)