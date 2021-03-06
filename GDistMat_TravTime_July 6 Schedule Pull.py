
# coding: utf-8

# In[22]:


def GDistMat(reqtime, origins, destinations, RName, timestamp):
    #Google Maps Travel Time Output Tool
    #No User Inputs Required

    import os
    import googlemaps
    import datetime
    import calendar
    import numpy
    import pprint
    import time
    maps_key = "Placeholder"
    gmaps = googlemaps.Client(key=maps_key)

    deptime = reqtime
    
    
    try:
        #Best Guess
        BestGuess = gmaps.distance_matrix(
            (origins),
            (destinations),
            departure_time = deptime,
            mode = 'driving',
            traffic_model = 'best_guess',
            )
        

        #   Indexes json from google api to rows.
        data = BestGuess['rows']
        #Iterates through each "elements" dictionary in "data" 
        Travel_list = {}
        Travel_list['rtime'] = time.strftime("%H:%M:%S")
        for i in data:
            #for j in len(origins):
            #Populates a dictionary called "Travel_list " 
            Travel_list['node1'] = BestGuess['origin_addresses'][0]
            Travel_list['node2'] = BestGuess['destination_addresses'][0]
            Travel_list['time'] = i['elements'][0]['duration_in_traffic']['value']
            Travel_list['distance'] = i['elements'][0]['distance']['value']
        
            
    except:
        OptTime = "Er"
        BestTime = "Er"
        PesTime = "Er"
        #houston("error",RName)
    return Travel_list


# In[23]:



#def houston(status,RName):
    
#    import requests
#    
#    slack_token = "xoxb-300357605111-lSK0SxVQs1UfQKBZThBv3cfF"
#    
#    if status == "initialize":
#        text = "GoogleDistanceMatrixAPI-{} Running".format(RName)
#    if status == "success":
#        text = "GoogleDistanceMatrixAPI-{} Complete".format(RName)
#    if status == "fail":
#        text = "GoogleDistanceMatrixAPI-{} Failed".format(RName)
#    if status == "error":
#        text = "GoogleDistanceMatrixAPI-{} Error".format(RName)
    
#    channel = "#api_status"
#    #Paremeters
#    houstonparams = {"token": slack_token, "channel": channel, "as_user": "true", "text": text}

    #Slack message request line
#    r1 = requests.get("https://slack.com/api/chat.postMessage?", params=houstonparams)
#    r1.raise_for_status()


# In[24]:


#Connects to SQL Server with dbsettings credentials

# Not working as of right now.
def create_table():
    import sys
    import psycopg2
    import time
    import datetime
    import calendar
    conn = psycopg2.connect(host="localhost",database="TravelTime", user="postgres", password="postgres")
    year = datetime.datetime.today()
    year = year.year
    try:
        cur = conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS travel_times_" + str(year) + "(Int1 VARCHAR(70), Int2 VARCHAR(70), Node1 VARCHAR(70),Node2 VARCHAR(70), Month VARCHAR(50), Day VARCHAR(50), Date VARCHAR(50), Travel_Time REAL, Distance REAL, RTime TIME)"
        cur.execute(sql)
        # execute the Create statement

        # commit the changes to the database
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# In[25]:


def csv_read():
    
    #Connects to SQL Server with dbsettings credentials
    global Travel_list
    import sys
    import psycopg2
    import time
    import csv
    import pprint
    import datetime
    import schedule
    
    
    #--------------------------------------------------------------------------------
    
    #USER INPUT - Route Name
    #Reads CSV with list of origins and destinations
    file = "C:/Users/rxr/Documents//Travel Times/Durham Live/Durham Live - Travel Time List June 11 PM.csv"
    #outfile = "C:/Users/rxr/Documents/Durham Live PM - Travel Time Kingston EB 1out.csv"
    
    with open(file, "r") as csvfile:
        
        csvreader = csv.reader(csvfile)
        # If your csv has a header keep this as true, otherwise set to false
        is_header = True
        #Goes through each CSV row and pulls a set of origins and destinations
        origin_list = []
        destination_list = []
        description_list = []
        for row in csvreader:
            if is_header:
                is_header = False
                continue
            else:
            #define origin and destination coordinates
                origins = float(row[7].split(", ")[0]), float(row[7].split(", ")[1])
                destinations = float(row[8].split(", ")[0]), float(row[8].split(", ")[1])
                description = row[1]
                origin_list.append(origins)
                destination_list.append(destinations)
                description_list.append(description)


    return origin_list, destination_list, description_list


# In[26]:


def apicall(origin_list, destination_list, description_list):
    global Travel_list
    import psycopg2
    import time
    import csv
    import pprint
    import datetime
    import schedule
    
    Hour_stop = 9
    limit = 20000

    RName = 'TestRoute'
    conn = psycopg2.connect(host="localhost",database="TravelTime", user="postgres", password="postgres")
    timer = datetime.datetime.today()
    dateref = timer.date()
    
    day = dateref.strftime("%A")
    date = dateref.strftime("%d")
    month = dateref.strftime("%B")

    
    counter = 0
    rounds = 1
    timer = datetime.datetime.today()
    timer = timer.hour
    requests = 0
    while timer <= Hour_Stop and requests < limit:
        tic = time.clock()
        for i in range(0, len(origin_list)-1):
            origins = origin_list[i]
            destinations = destination_list[i]
            times = time.time() * 1000
            times = int(times)
            reqtime= "now"
            timestamp = time.strftime("%H:%M:%S")
            Travel_info = GDistMat(reqtime, origins, destinations, RName, timestamp)
            requests = requests + 1
            Travel_info['description'] = description_list[i]
            Travel_info['day'] = day
            Travel_info['date'] = date
            Travel_info['month'] = month
            year = datetime.datetime.today()
            year = year.year
            cur = conn.cursor()
                # execute the INSERT statement
            sql = "INSERT INTO travel_times_" + str(year) + "(Node1, Node2, Month, Day, Date, Travel_Time, Distance, RTime)                    VALUES(%(node1)s, %(node2)s,%(month)s, %(day)s, %(date)s, %(time)s, %(distance)s, %(rtime)s)"
            cur.execute(sql,Travel_info)
            # commit the changes to the database
            conn.commit()
        toc = time.clock()
        delay = toc-tic
        time.sleep(300 - delay)
        timer = datetime.datetime.today()
        timer = timer.hour


# In[21]:


create_table()
origin_list, destination_list, description_list = csv_read()
import schedule
import datetime
import time
hour_stop = 9
schedule.every().day.at("11:30").do(apicall(origin_list, destination_list, description_list))
timer = datetime.datetime.today()
timer = timer.hour
while timer <= hour_stop:
    schedule.run_pending()
    time.sleep(1)
    timer = datetime.datetime.today()
    timer = timer.hour
schedule.CancelJob
cur.close()
print("Done")

