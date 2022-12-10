import mysql.connector

password = str(input("What is the password for your SQL? "))

cnx = mysql.connector.connect(user="root",
                              password=password,
                              host="127.0.0.1")

cnx.cursor().execute("CREATE DATABASE project")