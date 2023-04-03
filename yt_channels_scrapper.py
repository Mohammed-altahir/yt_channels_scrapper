import requests
import requests,json
from langdetect import detect

import pandas

KEY = "YOUR ACCESS TOKEN"

headers = {

    'Accept': 'application/json',
}

regionCodes_count = 0

# arabic region codes
regionCodes = ['bh','eg','dz','ae','iq','tr','gb','tk']

target = 250000
for rCode in regionCodes:
    if regionCodes_count >= target:
        break
    all_data = []
    response = requests.get('https://youtube.googleapis.com/youtube/v3/search?channelType=any&key='+KEY+'&part=snippet&regionCode='+rCode+'&maxResults=500', headers=headers)
    URL = response.url
    response = response.json()
    
    regionCodes_count += response["pageInfo"]["totalResults"]
    nextPageToken = response.get("nextPageToken")
    # print(response)
    while nextPageToken:
            r = requests.get(URL,headers=headers)
            json_data = r.json()
            
            response['items'].append(json_data['items'])
            nextPageToken = json_data.get("nextPageToken")

    all_data.append(response)
    with open("data2.json","w+")as js:
        js.writelines(json.dumps(all_data))

with open("data.json","r") as js:
    channels = json.loads(js.readlines())
# container to hold the channels information as list of lists
container = []
for channel in channels['items']:
    features = [channel["snippet"]["channelTitle"],channel["snippet"]["title"],channel["snippet"]["description"]]
    for feature in features: 
        if feature == "":
            features.remove(feature)

    is_arabic = [detect(feature) for feature in features]
    # only choosing channels with specific lanaguage
    # in this case arabic 
    if "ar" in is_arabic:
        # requesting channel stats
        stats_req = requests.get('https://www.googleapis.com/youtube/v3/channels?id='+channel["snippet"]["channelId"]+'&key='+KEY+'&part=statistics', headers=headers)
        stats_req = stats_req.json()
        container.append([channel["snippet"]["channelId"],channel["snippet"]["channelTitle"],channel["snippet"]["description"],stats_req['items'][0]["statistics"]["viewCount"],stats_req['items'][0]["statistics"]["subscriberCount"],stats_req['items'][0]["statistics"]["videoCount"],response["regionCode"]])

# first fillter
# removing duplicates from the data
res_list = []
for i in range(len(container)):
    if container[i] not in container[i + 1:]:
        res_list.append(container[i])
container = res_list

# creating pandas dataframe
columns = ['channel_id','channel_title','channel_description','channel_view_count','channel_subscriber_count','channel_video_count','channel_country']
df = pandas.DataFrame(data=container,columns=columns)
# removing duplicates from the dataframe if passed throw the first fillter
df.drop_duplicates(inplace=True)
# writting the dataframe content to an excel file
df.to_excel('data.xlsx')
