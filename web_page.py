import streamlit as st
from simulation import run_simulation
import time
from get_df import get_dataframes as get_df
import plotly.express as px
import pandas as pd

st.set_page_config(layout="wide", page_title="Simulation", page_icon="🧪",  initial_sidebar_state="expanded")
st.write("""# 📊 Port Simulation 📊""")
st.markdown("""
<style>
.big-font {
    font-size:12px !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<p class="big-font">This simulation was made by the following students: Edwin Marmolejos, Tomas Ploquin, Sebastian Vasquez, Francisco Jimenez and Daniel Villalaín.</p>', unsafe_allow_html=True)
st.write("____________________________________________________________________________________________________________")

st.image("images/los-puertos-en-2030.jpeg" , use_column_width=True)
st.write("The following page will run a simulation of a port with the parameters you choose. The simulation processes is as follows:")
st.write("The simulation works arround 4 main stages, outside port processes, entering port processes, inside port processes and exiting port processes. "
         "Each of theses stages have different processes within them that create all together a complete simulation of a port. "
         "To start by, the outside process is only based on a queue system, the first to get there are the first to get in. Then the entering port processes are based security standards, if not passed the boat is immediately expelled from the simulation or port. "
         "Once inside the port, the boat has the option to pass by the gaz station and then get to the offloading area. "
         "Cranes and transporter manage the offloading of the containers but everything is commanded by the tower. Finally after finishing the off loading, with the permission of the tower the boat can leave the port to its new destination .")
st.write("____________________________________________________________________________________________________________")

st.write("Please, input the parameters for the simulation: ")
st.sidebar.title("Number parameters")

# Parameters
st.sidebar.subheader("Number of boats")
n_boats = st.number_input("Number of boats: ", min_value=1, max_value=50, value=1, key="n_simulations")
st.sidebar.subheader("Number of docks")
n_docks = st.number_input("Number of docks: ", min_value=1, max_value=10, value=1, key="n_docks")
st.sidebar.subheader("Number of cranes")
n_cranes = st.number_input("Number of cranes: ", min_value=1, max_value=7, value=1, key="n_cranes")
st.sidebar.subheader("Number of transporters")
n_transporters = st.number_input("Number of transporters: ", min_value=1, value=1,max_value=7, key="n_transporters")
st.write("____________________________________________________________________________________________________________")
st.sidebar.title("Functions of the simulation")
st.write("There are two functions that you can disable in order to see the results of the simulation.")
st.write("1. The first one is the delay in arriving. "
         "This function will delay the arrival of the boats.")
st.write("2. The second one is the boat priority. "
         "This function will only let the boats enter if they were the first to get in the queue.")


delay_remove = st.checkbox("Delay in arriving ", value=False, key="delay")
priority_remove = st.checkbox("Boat priority ", value=False, key="priority")

form = st.form(key='my_form1')
submit_button4 = form.form_submit_button(label='Submit')

st.write("____________________________________________________________________________________________________________")

if submit_button4:
    start = time.time()
    st.write("The simulation is running. Please, check the results in the terminal.")
    run_simulation(n_boats, n_docks, n_cranes, n_transporters, delay_remove, priority_remove)
    st.sidebar.title("Insights")
    st.write(" ")
    st.header("The simulation was completed!! :) ")
    st.write(f"The simulation took {int(time.time() - start)} seconds to run.")
    st.write("____________________________________________________________________________________________________________")
    st.write("The first table is about the characteristics of each of the boats that arrived to the port."
             "There is plenty information about the boats. Among others we can see which docks stays in the port, the place of origin and the merchandise that the boat has in its containers, ")
    df_boats = get_df("Boats")
    st.dataframe(df_boats.head())
    st.write()
    st.write("The second table is about the time that the boat takes to complete each of the processes."
             "We can see when the boat arrives and leaves the port, the time that it takes to get to the offloading area and the time that it takes to get to the exit of the port.")
    df_boats_arrivals = get_df("Boats_arrivals")
    st.dataframe(df_boats_arrivals.head())
    st.write()
    st.write("The third table is about the employees hired in the port. The workers are dvided into two jobs: "
             "the first one is working on the transportation of containers and the second one is the working on the unloading of the containers.")
    df_employees = get_df("Employees")
    st.dataframe(df_employees.head())
    st.write()
    st.write(
        "____________________________________________________________________________________________________________")
    st.write("The following graphs and metrics will allow you to see the performance of the port. Some of the metrics might be useful in order to decide later "
             "on the parameters of the port. For example, if the port is not able to handle the amount of boats that arrive, it might be a good idea to increase the number of docks.")
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Boats**')
    st.write("In order to asses the efficiency of the port we can see the following insights: ")
    con_moved = df_boats["Containers"].sum()
    st.write(f"The total number of containers moved in the port is: {con_moved}.")
    mv_moved = df_boats["Value_in_market"].sum()
    st.write(f"The value of those containers where {mv_moved}€.")
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Salary**')
    total_salary = df_employees["Salary"].mean()
    avg_work_time = df_employees["Workday_time"].mean()
    st.write(f"The average salary of the employees is: {total_salary}€.")
    st.write(f"Moreover, the average work schedule of the employees is: {avg_work_time}.")
    st.write(f"Therefore, with a simple calculation, the average cost on salaries per min: {round(total_salary / avg_work_time, 2)}.")
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Worst Performance Employee**')
    st.write("Now, we can analyse the performance of the employees in the port.")
    df_employee_min = df_employees.sort_values(by='Working_time', ascending=True)
    df_employee_min = df_employee_min.reset_index(drop=True)
    name = df_employee_min.loc[0][0]
    picture = df_employee_min.loc[0][2]
    work_time = df_employee_min.loc[0][-3]
    total_time = df_employee_min.loc[0][-4]
    percentage_time = int((work_time / total_time) * 100)
    st.write(f"The employee that has worked the least is: {name}.")
    st.write(f"The {name} worked {work_time} mins out of a total {total_time} mins. ({percentage_time}%)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name", str(name))
    col2.metric("Work Time", str(work_time) + " mins")
    col3.metric("Percentage of total time", str(percentage_time) + "%")
    st.image(picture, width=200)
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Best Performance Employee**')
    st.write("On the other hand, we can see the employee that has worked the most: ")
    df_employee_max = df_employees.sort_values(by='Working_time', ascending=False)
    df_employee_max = df_employee_max.reset_index(drop=True)

    name = df_employee_max.loc[0][0]
    picture = df_employee_max.loc[0][2]
    work_time = df_employee_max.loc[0][-3]
    total_time = df_employee_max.loc[0][-4]
    percentage_time = int((work_time / total_time) * 100)
    st.write(f"The employee that has worked the most is: {name}.")
    st.write(f"The {name} worked {work_time} mins out of a total {total_time} mins. ({percentage_time}%)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name", str(name))
    col2.metric("Work Time", str(work_time) + " mins")
    col3.metric("Percentage", str(percentage_time) + "%")
    st.image(picture, width=200)
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Crane VS Transporter**')
    st.write("Another interesting insight is made by comparing the crane workers and the transporter workers. ")

    crane_df = df_employees[df_employees['Job'] == "Crane"]
    trans_df = df_employees[df_employees['Job'] == "Transporter"]
    st.write("For crane workers: ")
    st.write(f"The average age is {round(crane_df['Age'].mean())}.")
    st.write(f"The average salary is: {round(crane_df['Salary'].mean())}€.")
    st.write(f"The average schedule time is: {crane_df['Workday_time'].mean()}.")
    st.write(f"The average working time is: {crane_df['Working_time'].mean()}.")
    st.write(f"The average number of breaks is: {round(crane_df['Breaks'].mean())}.")
    st.write(f"And the average time spent in breaks is {round(crane_df['Time_in_break'].mean())}.")
    st.write("")
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Crane VS Transporter**')
    st.write("On the other hand, for transporter workers: ")
    st.write(f"The average age is {round(trans_df['Age'].mean())}.")
    st.write(f"The average salary is: {round(trans_df['Salary'].mean())}€.")
    st.write(f"The average schedule time is: {trans_df['Workday_time'].mean()}.")
    st.write(f"The average working time is: {trans_df['Working_time'].mean()}.")
    st.write(f"The average number of breaks is: {round(trans_df['Breaks'].mean())}.")
    st.write(f"And the average time spent in breaks is {round(trans_df['Time_in_break'].mean())}.")

    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Revenue**')
    revenue = df_boats_arrivals["Amount_charged"].sum()
    revenue_boat = round(revenue / len(df_boats_arrivals))
    revenue_cont = round(revenue / con_moved)
    avg_rev_worker = round(con_moved / len(df_employees))
    st.write(f"The total revenue of the port is: {revenue}€.")
    st.write(f"The average revenue per boat is: {revenue_boat}€.")
    st.write(f"The average revenue per container is: {revenue_cont}€.")
    st.write(f"The average revenue per worker is: {avg_rev_worker}€.")
    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Boats Arrivals**')
    st.write("Now, we can analyse the boats arrivals in the port. This is one of the most important metric we want to analyse."
             "With this time, we can better adjust how much we charge for the boats and how many containers we can move per day."
             "Moreover, we can see how efficient the port is working. In order to pass the queue, there needs to be space in the port and,"
             "for that, we need to move as fast as possible.")
    time_in_queue = round(df_boats_arrivals["Time_in_queue"].mean(), 2)
    st.write(f"The average time in queue is: {time_in_queue} mins.")


    st.write("____________________________________________________________________________________________________________")
    st.subheader('**Graphics**')
    st.write("Now, we move on to analayse the values that the each of the boats have in the market. ")
    st.markdown('**Value of Boats**')
    st.write("This is the distribution of the values of the boats that arrived to the port. The major insight of this chart is"
             "how much money the port has gained with each of the merchandise. For some people relying on just one merchandise "
             "might seem very risky. For others, it might be a good idea. What do you think?")
    st.sidebar.subheader("Value per merchandise insight")

    df1 = df_boats.groupby('Merchandise')['Value_in_market'].sum()
    df2 = pd.DataFrame(df1)

    fig = px.bar(df2, x=df2.index, y="Value_in_market", title="Value of boats per merchandise")
    fig.update_xaxes(title_text='Merchandise')
    fig.update_yaxes(title_text='Number of Boats')
    st.plotly_chart(fig)
    st.write("____________________________________________________________________________________________________________")
    st.markdown('**Docks Used**')
    st.write("In the graph below the number of docks used in the port is shown. This helps us understand the capapcity of the port."
             "As well, it makes a great insight of how much this resources is being used. If almost all docks are being used the same, it means that "
             "the docks are used fairly. However, if some docks are being used more than others, it means that the port is not being used to its full potential.")
    st.sidebar.subheader("Dock Usage")
    df1 = df_boats.groupby('Dock')["Boat"].count()
    df1 = pd.DataFrame(df1)
    df1["Dock"] = df1.index
    fig = px.bar(df1, x='Dock', y='Boat', color='Dock')
    st.plotly_chart(fig)
    st.write(
        "____________________________________________________________________________________________________________")
    st.markdown('**Revenue per Dock**')
    st.write("In the graph below the revenue per dock is shown. This helps us understand how we are making money with the port.")
    st.sidebar.subheader("Revenue per Dock")
    dock_amount_c = df_boats_arrivals.groupby('Dock')['Amount_charged'].sum()
    dock_amount_c = pd.DataFrame(dock_amount_c)
    dock_amount_c["Dock"] = dock_amount_c.index
    fig = px.bar(dock_amount_c, x='Dock', y='Amount_charged', color='Dock')
    st.plotly_chart(fig)
    st.write(
        "____________________________________________________________________________________________________________")
    st.markdown('**Average Revenue per Dock**')
    st.write("To keep the factor of the number of boats out, it is important to look at the next graph. "
             "This graph helps us understand on average, how much money we are making per dock.")
    st.sidebar.subheader("Average Revenue per Dock")
    dock_amount_c = df_boats_arrivals.groupby('Dock')['Amount_charged'].mean()
    dock_amount_c = pd.DataFrame(dock_amount_c)
    dock_amount_c["Dock"] = dock_amount_c.index
    fig = px.bar(dock_amount_c, x='Dock', y='Amount_charged', color='Dock')
    st.plotly_chart(fig)

    st.write("____________________________________________________________________________________________________________")
    st.markdown('**Boat Times**')
    st.write("Normally, boats that arrive later to the port, they would need to wait more in the queue to enter the port. "
             "In the graph below we can see the correlation between the time in queue and the time of arrival.")
    st.sidebar.subheader("Time in queue insight")
    st.write("The following graph might be affected by the priority function... "
             "(Changing the priority function might affect the results).")
    x_values = df_boats_arrivals["Arrival_time"]
    y_values = df_boats_arrivals["Time_in_queue"]
    fig = px.scatter(df_boats_arrivals, x=x_values, y=y_values, title="Time in queue vs Arrival time")
    st.plotly_chart(fig)

    st.sidebar.subheader("Time waiting confirmation insight")
    st.write("Another key factor is the time that the boats wait for the confirmation to enter a dock. "
             "If this time is high, it means that our control station is not working efficiently. ")
    x_values = df_boats_arrivals["Arrival_time"]
    y_values = df_boats_arrivals["Time_waiting_confirmation"]
    fig = px.scatter(df_boats_arrivals, x=x_values, y=y_values, title="Time in queue vs Arrival time")
    st.plotly_chart(fig)

    st.sidebar.subheader("Time in dock insight")
    st.write("The time that the boats spend in the dock is also important. "
             "If this time is high, it means that the workers take long to unload"
             " and transport the containers of a boat. ")
    x_values = df_boats_arrivals["Arrival_time"]
    y_values = df_boats_arrivals["Time_in_dock"]
    fig = px.scatter(df_boats_arrivals, x=x_values, y=y_values, title="Time in queue vs Arrival time")
    st.plotly_chart(fig)