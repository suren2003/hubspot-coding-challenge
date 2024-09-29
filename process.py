import requests
import json 
from datetime import datetime, timedelta
import pytz

# Set timezone to UTC
timezone = pytz.utc

# Fetch data from API
url = 'https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey='
apikey = ""
url = url + apikey
res = requests.get(url)
if res.status_code != 200:
    print("Failed to fetch data:", res.status_code)
    exit()

response = json.loads(res.text)

customerCalls = {}  # Structure: {customerId: {date: [callInfo]}}

# Helper function to add a call to the correct customer and date
def add_call_to_customer(customerId, callDate, call):
    if customerId not in customerCalls:
        customerCalls[customerId] = {}
    if callDate not in customerCalls[customerId]:
        customerCalls[customerId][callDate] = []

    customerCalls[customerId][callDate].append(call)

# Process all call records
for entry in response['callRecords']:
    customerId = entry['customerId']
    startDate = datetime.fromtimestamp(entry['startTimestamp'] / 1000, tz=timezone)
    endDate = datetime.fromtimestamp(entry['endTimestamp'] / 1000, tz=timezone)

    # If the call starts and ends on the same day
    if startDate.date() == endDate.date():
        add_call_to_customer(customerId, startDate.date(), entry)
    else:
        # Handle the first day
        firstDayEnd = datetime(startDate.year, startDate.month, startDate.day, 23, 59, 59, 999999, tzinfo=timezone)
        add_call_to_customer(customerId, startDate.date(), {
            'customerId': customerId,
            'callId': entry['callId'],
            'startTimestamp': entry['startTimestamp'],
            'endTimestamp': int(firstDayEnd.timestamp() * 1000)
        })

        # Handle intermediate full days
        currentDate = startDate + timedelta(days=1)
        while currentDate.date() < endDate.date():
            startOfDay = datetime.combine(currentDate, datetime.min.time(), tzinfo=timezone)
            endOfDay = datetime.combine(currentDate, datetime.max.time(), tzinfo=timezone)
            add_call_to_customer(customerId, currentDate.date(), {
                'customerId': customerId,
                'callId': entry['callId'],
                'startTimestamp': int(startOfDay.timestamp() * 1000),
                'endTimestamp': int(endOfDay.timestamp() * 1000)
            })
            currentDate += timedelta(days=1)

        # Handle the last day
        if endDate.time() > datetime.min.time():  
            lastDayStart = datetime(endDate.year, endDate.month, endDate.day, 0, 0, 0, tzinfo=timezone)
            add_call_to_customer(customerId, endDate.date(), {
                'customerId': customerId,
                'callId': entry['callId'],
                'startTimestamp': int(lastDayStart.timestamp() * 1000),
                'endTimestamp': entry['endTimestamp']
            })

# Convert the customerCalls dictionary to a serializable format
serializable_customerCalls = {
    customerId: {
        str(callDate): calls for callDate, calls in dates.items()
    } for customerId, dates in customerCalls.items()
}

results = {'results': []}   # {results: [{customerId, date, maxConcurrentCalls, timestamp, callIds: []}, {  }]}

# Line sweep approach to calculate max concurrent calls
for customerId in customerCalls.keys():
    for date, calls in customerCalls[customerId].items():
        events = []
        for call in calls:
            startTime = call['startTimestamp'] 
            endTime = call['endTimestamp'] 

            events.append((startTime, "start", call["callId"]))
            events.append((endTime, "end", call["callId"]))

        events.sort(key=lambda x: (x[0], x[1] == "start"))  # Sort by time, then by event type

        concurrentCalls = 0 
        currentCallId = []       # Active call IDs
        maxConcurrentCalls = 0
        maxConcurrentTime = None
        maxCurrrentCallId = []
       
        for eventTime, eventType, callId in events:
            if eventType == 'start':
                concurrentCalls += 1
                currentCallId.append(callId)
            else:
                concurrentCalls -= 1
                currentCallId.remove(callId)
            
            if concurrentCalls > maxConcurrentCalls:
                maxConcurrentCalls = concurrentCalls
                maxConcurrentTime = eventTime
                maxCurrrentCallId = currentCallId[:]

        results['results'].append({
            "customerId": customerId,
            "date": str(date.strftime("%Y-%m-%d")),
            "maxConcurrentCalls": maxConcurrentCalls,
            "timestamp": maxConcurrentTime,
            "callIds": maxCurrrentCallId
        })

# Posting data
url = 'https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey='
apikey = ""
url = url + apikey
json_data = json.dumps(results, indent=2)

print(json_data)
headers = {
    'Content-Type': 'application/json'  # Specify that you're sending JSON
}

# Send the POST request
response = requests.post(url, data=json_data, headers=headers)

# Check the response
if response.status_code == 200:
    print("Success:", response.json())  # Assuming the response is in JSON format
else:
    print("Failed:", response.status_code, response.text)
