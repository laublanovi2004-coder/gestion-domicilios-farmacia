# Empty file
import pymysql

# Engañar a Django para que piense que es mysqlclient
pymysql.install_as_MySQLdb()
pymysql.version_info = (1, 4, 6, "final", 0)