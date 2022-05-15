import toml, json
import os


MYSQL_CONFIG_PATH = os.path.join(os.getcwd(), r'resources/mysql-config.toml')
MYSQL_CONFIG = toml.load(MYSQL_CONFIG_PATH)['database']