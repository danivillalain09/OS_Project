import random
import mysql.connector
import traceback
import random
import time

cnx = mysql.connector.connect(user="root", password="7deJuniode2002",
                              host="localhost",
                              database="pruebas")
cursor = cnx.cursor()

try:

    #cursor.execute("CREATE TABLE prueba1 (Boats INT, Hakia_1 INT, Hakia2 INT)")

    """
    for i in range(10):
        boat = int(i+ random.randint(1, 10))
        cursor.execute(f"INSERT INTO `pruebas`.`prueba1` (`Boats`) VALUES ('{boat}')")
        cnx.commit()
    print("Everything inserted!")
    """

    column_name = "Hakia_1"
    start = 0
    cursor.execute(f"INSERT INTO prueba1 (Boats, {column_name}) VALUES (1,'{start}')")
    cnx.commit()

    """
    result = cursor.fetchall()
    result_list = []
    for x in result:
        x = x[0]
        result_list.append(x)
    maximum = max(result_list)
    print(maximum)
    """

except Exception:
    traceback.print_exc()

cnx.close()
