import requests as req
import json
import sys
import re
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def writeToDynamodb(key, url, viewCount):
    print('starting')
    table = dynamodb.Table("pitchfork_reviews")
    # print(table.creation_date_time)
    table.update_item(
        Key = {
            'artistNameAlbumName': key
        },
        UpdateExpression = 'SET ytUrl = :url, viewCount = :viewCount',
        ExpressionAttributeValues = {
            ':url': url,
            'viewCount': viewCount
        }
    )
    
    res = table.get_item(
        Key = {
            'artistNameAlbumName': key
        }
    )
    item = res['Item']
    print(item)

def getViews(key, playlist):
    ytInfo = {}
    url = "https://www.youtube.com" + playlist
    print(url)
    res = req.get(url)
    if (res.ok):
        viewCount = res.text[res.text.find("views")-12:res.text.find(" views")]
        n = re.search("\d", viewCount)
        if n:
            viewCount = viewCount[n.start():]
            # ytInfo['ytUrl'] = url
            # ytInfo['ytViewCount'] = viewCount.replace(",", "")
            print(viewCount)
            writeToDynamodb(key, url, viewCount.replace(',', ''))
            
        else:
            # ytInfo['ytUrl'] = url
            # ytInfo['ytViewCount'] = 0
            writeToDynamodb(key, url, 0)
            print("Couldn't find view count")

def makeUrl(title):
    url = "https://www.youtube.com/results?search_query="
    playlistTag = "&sp=EgIQA1AU"
    newTitle = "+".join(title.split())
    return url + newTitle + playlistTag

def search(title):
    print(makeUrl(title))
    # res = req.get(makeUrl(title))
    res = req.get('https://www.youtube.com/results?search_query=dog')
    if (res.ok):
        playlist = res.text[res.text.find("/playlist?list="):res.text.find("View full playlist") + 50]
        playlist = playlist[:playlist.find('"')]
        # print (playlist)
        # getViews(title, playlist)
    
    else:
        print("failed to find playlist")
        print(res)
        
def readReviews():
    table = dynamodb.Table("pitchfork_reviews")
    res = table.scan(ProjectionExpression="artistNameAlbumName")
    data = res['Items']
    
    # print(json.dumps(data, indent=4, separators=(',', ': ')))
    
    for obj in data:
        for key, value in obj.items():
            # print(value)
            search(value)
    
    # while res.get('LastEvaluatedKey'):
    #     res = table.scan(ExclusiveStartKey=res['LastEvaluatedKey'])
    #     data.extend(res["Items"])
        
    # print(data)
        
readReviews()
    
# title = "sun ra and his arkestra the magic city"
# search(title)