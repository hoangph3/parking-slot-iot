import json
from .base import ClassProperty


class RedisEnv:
    def __init__(
            self,
            password,
            host,
            port,
            database
    ):
        self.__password = password
        self.__host = host
        self.__port = port
        self.__database = database

    @property
    def password(self):
        return self.__password

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def database(self):
        return self.__database


class PostgreSqlEnv:
    def __init__(
            self,
            user,
            password,
            host,
            port,
            database
    ):
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__database = database

    @property
    def user(self):
        return self.__user

    @property
    def password(self):
        return self.__password

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def database(self):
        return self.__database


class SystemEnv:
    __instance: dict = None

    @staticmethod
    def get_instance():
        if not SystemEnv.__instance:
            return SystemEnv()

        return SystemEnv.__instance

    def __init__(self) -> None:
        if SystemEnv.__instance:
            raise Exception("This class cannot initialize")
        else:
            SystemEnv.__instance = self
            with open("./env/prod.json") as f:
                env_vars = json.load(f)

            self.__postgresql: PostgreSqlEnv = PostgreSqlEnv(
                user=env_vars["postgresql"]["user"],
                password=env_vars["postgresql"]["password"],
                host=env_vars["postgresql"]["host"],
                port=env_vars["postgresql"]["port"],
                database=env_vars["postgresql"]["database"],
            )

            self.__redis: RedisEnv = RedisEnv(
                password=env_vars["redis"]["password"],
                host=env_vars["redis"]["host"],
                port=env_vars["redis"]["port"],
                database=env_vars["redis"]["database"]
            )

            self.__time_interval: int = env_vars["system"]["time_interval"]
            self.__num_slots: int = env_vars["system"]["num_slots"]
            self.__api_port: int = env_vars["system"]["port"]
            self.__api_host: str = env_vars["system"]["host"]

    @ClassProperty
    def postgresql(cls):
        return cls.get_instance().__postgresql

    @ClassProperty
    def redis(cls):
        return cls.get_instance().__redis

    @ClassProperty
    def time_interval(cls):
        return cls.get_instance().__time_interval

    @ClassProperty
    def num_slots(cls):
        return cls.get_instance().__num_slots

    @ClassProperty
    def api_port(cls):
        return cls.get_instance().__api_port

    @ClassProperty
    def api_host(cls):
        return cls.get_instance().__api_host