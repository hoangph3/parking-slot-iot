from keeper.connections import DBConnector
from keeper.environments import SystemEnv


def init_default_slot():
    num_slots = SystemEnv.num_slots
    insert_sql = """
            INSERT INTO slot_info (slot_id, location, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (slot_id, location) DO UPDATE SET
            (start_time, end_time, status) = (EXCLUDED.start_time, EXCLUDED.end_time, EXCLUDED.status)
            """
    try:
        # Create a new cursor
        cur = DBConnector.psql_connection.cursor()

        # If the slot_info table is exists, don't initialize the default slots
        # get_table_sql = """
        #         SELECT table_name FROM information_schema.tables WHERE table_schema='public'
        #         """
        # cur.execute(get_table_sql)
        # table_rows = cur.fetchall()
        # is_exist = False
        # for row in table_rows:
        #     if "slot_info" in row:
        #         is_exist = True
        #         break
        # if not is_exist:
        #     # Execute the INSERT statement
        #     for slot_id in range(num_slots):
        #         slot_data = create_slot_info(slot_id=slot_id, location=slot_id)
        #         cur.execute(insert_sql, slot_data)

        for slot_id in range(num_slots):
            slot_id += 1
            slot_data = create_slot_info(slot_id=slot_id, location=slot_id)
            cur.execute(insert_sql, slot_data)
        # Commit the changes to the database
        DBConnector.psql_connection.commit()
        # Close communication with the database
        cur.close()

    except Exception as e:
        print("[database] Did not initialize the default slots caused by {}".format(e))


def create_slot_info(slot_id, location, start_time=0, end_time=0, status=0):
    """
    :param slot_id: slot identification
    :param location: (x, y) coordinate
    :param start_time: 0 - timestamp which changed when the status of slot from 0 to 1
    :param end_time: 0 - timestamp which changed when the status of slot from 1 to 0
    :param status: 0 - empty and 1 - busy
    :return: slot_info: the default information of slot is initialized
    """
    # slot_info = {
    #     "slot_id": slot_id,
    #     "location": location,
    #     "start_time": start_time,
    #     "end_time": end_time,
    #     "status": status
    # }

    slot_info = (slot_id, location, start_time, end_time, status)
    return slot_info
