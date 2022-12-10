import pandas as pd
import mysql.connector

database = mysql.connector.connect(user="root", password="7deJuniode2002", host="127.0.0.1", database="project")
cursor = database.cursor()


def get_dataframes(table_name):
    global database, cursor

    tables = table_name
    cursor.execute(f"DESCRIBE {tables};")
    values = cursor.fetchall()
    column_names = [i[0] for i in values]
    query = f"SELECT * FROM {tables}"
    cursor.execute(query)
    result = cursor.fetchall()
    df_boats = pd.DataFrame(result, columns=column_names)

    return df_boats