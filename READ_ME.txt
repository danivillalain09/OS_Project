
---- PORT SIMULATION ----
The simulation works around 4 main stages, outside port processes, entering port processes, inside port processes and exiting port processes.
Each of these stages have different processes within them that create all together a complete simulation of a port.
To start by, the outside process is only based on a queue system, the first to get there are the first to get in.
Then the entering port processes are based security standards, if not passed the boat is immediately expelled from the simulation or port.
Once inside the port, the boat has the option to pass by the gaz station and then get to the offloading area.
Cranes and transporter manage the offloading of the containers but everything is commanded by the tower.
Finally, after finishing the off loading, with the permission of the tower the boat can leave the port to its new destination.

---- SPECS ----
The python version required is 3.10.0 or higher

Before running the simulation it is necessary to change the SQL password in the file and "Simulation.py" (line 19)
and "sql_to_dataframes.py" (line 4). The values are set by default.

The simulation will only run if is already a database name "project" in your sql.
Therefore, you must run the project "Create_database.py" first.

If already done once, doing this will generate an error message.

---- HOW TO USE ----
In order to run the code please install the following libraries:

- threading
- time
- random
- concurrent.futures
- colorama
- mysql.connector
- traceback
- datetime
- faker
- copy

Once downloaded the libraries, please run the streamlit in the file "web_page.py" with the following command:

streamlit run web_page.py