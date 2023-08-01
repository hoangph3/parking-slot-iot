import time
import redis
import psycopg2
from keeper.environments import SystemEnv
from keeper.base import ClassProperty


class DBConnector:
    __instance = None

    @staticmethod
    def get_instance():
        if not DBConnector.__instance:
            return DBConnector()

        return DBConnector.__instance

    def __init__(self) -> None:
        if DBConnector.__instance:
            raise Exception("This class cannot initialize")
        else:
            DBConnector.__instance = self
            self.__postgre_connection = None
            self.__redis_connection = None

            self.connect_psql()
            self.connect_redis()
            DBConnector.init_db()

    def connect_psql(self):
        # Initialize a connection to the postgresql server -> return: conn object
        while not self.__postgre_connection:
            try:
                self.__postgre_connection = psycopg2.connect(
                    user=SystemEnv.postgresql.user,
                    password=SystemEnv.postgresql.password,
                    host=SystemEnv.postgresql.host,
                    port=SystemEnv.postgresql.port,
                    database=SystemEnv.postgresql.database
                )
                break

            except psycopg2.OperationalError as e:
                print("Fail to connect cause {}, retry after 10s".format(e))
                time.sleep(10)

    def connect_redis(self, retry=False):
        while not self.__redis_connection:
            try:
                if not self.__redis_connection:
                    self.__redis_connection = redis.Redis(
                        host=SystemEnv.redis.host,
                        port=SystemEnv.redis.port,
                        db=SystemEnv.redis.database
                    )

                self.__redis_connection.ping()
                break
            except Exception as e:
                print("Connect to Redis fail cause {}".format(e))
                self.__redis_connection = None
                if not retry:
                    break
                print("Retry after 10s")
                time.sleep(10)

    @staticmethod
    def init_db():
        query = """CREATE TABLE IF NOT EXISTS slot_info ( 
                                    slot_id INT, 
                                    location TEXT, 
                                    start_time INT, 
                                    end_time INT, 
                                    status INT, 
                                PRIMARY KEY (slot_id, location) 
                                )"""

        # Create a new cursor
        cur = DBConnector.psql_connection.cursor()
        # Execute the CREATE statement
        cur.execute(query)
        # Commit the changes to the database
        DBConnector.psql_connection.commit()
        # Close communication with the database
        cur.close()


    @ClassProperty
    def psql_connection(cls):
        cls.get_instance().connect_psql()
        return cls.get_instance().__postgre_connection

    @ClassProperty
    def redis_connection(cls):
        cls.get_instance().connect_redis(retry=True)
        return cls.get_instance().__redis_connection
