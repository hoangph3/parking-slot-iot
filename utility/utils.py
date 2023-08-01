import json
from keeper.connections import DBConnector


def get_data_from_redis():
    data = {}
    try:
        keys = DBConnector.redis_connection.keys()
        vals = DBConnector.redis_connection.mget(keys)
        for k, v in zip(keys, vals):
            # Decode
            k = k.decode()
            v = v.decode()
            data[k] = v
        return data

    except Exception as e:
        print("[utils] Did not get the data from redis caused by {}0".format(e))
        return


def send_0_to_redis():
    # data = {
    #     0: 1,
    #     1: 1,
    #     2: 1,
    #     3: 1,
    #     4: 1
    # }

    data = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }
    try:
        resp = DBConnector.redis_connection.mset(data)
        if resp:
            print("[utils] Completed sent the data to redis!")
    except Exception as e:
        print("[utils] Did not send the data from redis caused by {}0".format(e))


def send_data_to_redis(data):
    if data is None:
        data = {
            0: 1,
            1: 1,
            2: 1,
            3: 1,
            4: 1
        }

    try:
        resp = DBConnector.redis_connection.mset(data)
        if resp:
            print("[utils] Completed sent the data to redis!")
    except Exception as e:
        print("[utils] Did not send the data from redis caused by {}0".format(e))


def get_data_from_psql():
    data = {}
    try:
        query = """
        SELECT slot_id, location, start_time, end_time, status FROM slot_info
        """
        # Create a new cursor
        cur = DBConnector.psql_connection.cursor()
        # Execute the CREATE statement
        cur.execute(query)
        # Get data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        return data

    except Exception as e:
        print("[utils] Did not get the data from PostgreSQL caused by {}".format(e))
    return


def update_data_to_psql(update_data):
    """
    :param update_data: is data has the type is a list of 5-tuple item:
                                                        (slot_id, location, start_time, end_time, status)
    :return:
    """
    update_sql = """
            INSERT INTO slot_info (slot_id, location, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (slot_id, location) DO UPDATE SET
            (start_time, end_time, status) = (EXCLUDED.start_time, EXCLUDED.end_time, EXCLUDED.status)
            """
    try:
        # Create a new cursor
        cur = DBConnector.psql_connection.cursor()
        # Execute the INSERT statement
        count = 0
        for slot_data in update_data:
            cur.execute(update_sql, slot_data)
            count += 1
        # Commit the changes to the database
        DBConnector.psql_connection.commit()
        # Close communication with the database
        cur.close()
        return {"message": "The number of updated slots are {}".format(count)}

    except Exception as e:
        print("[utils] Did not update the current information of slot into PostgreSQL caused by {}".format(e))
        return


def insert_data_to_psql():
    return

# if __name__ == "__main__":
#     send_data_to_redis()
