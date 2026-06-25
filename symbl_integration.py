from enum import Enum
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

#Test keys
SYMBL_APP_ID = *******
SYMBL_APP_SECRET = *****

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials =True,
    allow_methods=['*'],
    allow_headers=['*']
)

class Flag(Enum):
    transcription = 'transcription'
    topic = 'topic'
    sentiment = 'sentiment'
    intent = 'intent'
    entity = 'entity'
    summarization = 'summarization'
    feature = 'feature'

def ConvertToList(string):
    li = list(string.split(","))
    return li

def getAccessToken():

    url = "https://api.symbl.ai/oauth2/token:generate"

    payload = {
        "type": "application",
        "appId": SYMBL_APP_ID,
        "appSecret": SYMBL_APP_SECRET
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()['accessToken']

def getConversationID(filePath, ACCESS_TOKEN):
    
    url = "https://api.symbl.ai/v1/process/audio"

    payload = None
    numberOfBytes = 0

    try:
        audio_file = open(filePath, 'rb')  # use (r"path/to/file") when using windows path
        payload = audio_file.read()
        numberOfBytes = len(payload)

    except FileNotFoundError:
        print("Could not read the file provided.")

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN,
        'Content-Length': str(numberOfBytes),  # This should correctly indicate the length of the request body in bytes.
        'Content-Type': 'audio/mp3'
    }

    params = {
        'languageCode':'en-US',
        'detectPhrases':True,
        'enableSpeakerDiarization':False 
    }

    responses = {
        400: 'Bad Request! Please refer docs for correct input fields.',
        401: 'Unauthorized. Please generate a new access token.',
        404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',
        429: 'Maximum number of concurrent jobs reached. Please wait for some requests to complete.',
        500: 'Something went wrong! Please contact support@symbl.ai'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 201:
        return response.json()['conversationId']  # ID to be used with Conversation API.
    elif response.status_code in responses.keys():
        return responses[response.status_code] # Expected error occurred
    else:
        return "Unexpected error occurred"

@app.get("/v1/transcription")

def uploadAudioFile(flag, file=File(...)):

    ACCESS_TOKEN = getAccessToken()

    conversationID = getConversationID(file,ACCESS_TOKEN)

    if flag == getattr(Flag.transcription,'value'):
        return generateTranscription(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.topic,'value'):
        return generateTopicReport(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.sentiment,'value'):
        return generateSentimentReport(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.intent,'value'):
        return generateIntentReport(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.entity,'value'):
        return generateEntityReport(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.summarization,'value'):
        return generateSummary(conversationID,ACCESS_TOKEN)
    elif flag == getattr(Flag.feature,'value'):
        return generateFeatureOverview(conversationID,ACCESS_TOKEN)

def generateSentimentReport(conversationID,ACCESS_TOKEN):

    sentimentReport = []

    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/topics?sentiment=true"
    url= url.format(conversation_id = conversationID)

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    for i in ConvertToList(response.text):
        if i[:3]=='"su':
            sentimentReport.append(i)
    
    return sentimentReport

def generateTranscription(conversationID,ACCESS_TOKEN):
    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/transcript"
    url = url.format(conversation_id=conversationID)

    payload = { "contentType": "text/markdown" }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer "+ACCESS_TOKEN
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text.replace('"contentType":"text/markdown"','')

def generateSummary(conversationID,ACCESS_TOKEN):

    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/summary?refresh=true"
    url=url.format(conversation_id=conversationID)

    headers = {
        "accept": "application/json",
        "authorization": "Bearer "+ACCESS_TOKEN
    }

    response = requests.get(url, headers=headers)

    #return ConvertToList((response.text)[1])
    return response.json()['summary'][0]['text']

def generateEntityReport(conversationID,ACCESS_TOKEN):

    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/entities"
    url=url.format(conversation_id=conversationID)

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    #return ConvertToList((str(response.json()['entities']))[0])
    return {'entities':response.json()['entities'][0]['matches'][0]['detectedValue']}

def generateTopicReport(conversationID,ACCESS_TOKEN):

    allTopics = []

    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/topics?parentRefs=true&sentiment=true"
    url=url.format(conversation_id=conversationID)

    headers = {
        "accept": "application/json",
        'authorization': 'Bearer ' + ACCESS_TOKEN
    }

    params = {
        'sentiment': True,  
        'parentRefs': True, 
    }

    response = requests.request("GET", url, headers=headers, params=json.dumps(params))

    if response.json()['topics']!=[]:
        #return ConvertToList((str(response.json()['topics']))[0])
        topics = response.json()['topics']
        for i in topics:
            allTopics.append(i['text']) 
        
        return {'topics': allTopics}
    else:
        return "no topics were detected for this audio"

def generateIntentReport(conversationID,ACCESS_TOKEN):

    allIntents = []

    url = "https://api.symbl.ai/v1/conversations/{conversation_id}/trackers"
    url=url.format(conversation_id=conversationID)

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    if response.json() != []:
        for i in response.json():
            allIntents.append(i['name'].replace('Symbl.',''))

        return allIntents
    else:
        return "no intents were detected for this audio"

def generateFeatureOverview(conversationID,ACCESS_TOKEN):

    allTopics = []
    allIntents = []
    sentimentReport = []

    urlTopics = "https://api.symbl.ai/v1/conversations/{conversation_id}/topics?parentRefs=true&sentiment=true".format(conversation_id=conversationID)
    urlIntents = "https://api.symbl.ai/v1/conversations/{conversation_id}/trackers".format(conversation_id=conversationID)
    urlEntities = "https://api.symbl.ai/v1/conversations/{conversation_id}/entities".format(conversation_id=conversationID)
    urlSummary = "https://api.symbl.ai/v1/conversations/{conversation_id}/summary?refresh=true".format(conversation_id=conversationID)
    urlSentiments = "https://api.symbl.ai/v1/conversations/{conversation_id}/topics?sentiment=true".format(conversation_id=conversationID)

    access_token = ACCESS_TOKEN

    parameters={'sentiment':True}

    headers_topicsIntentsEntitiesSentiments = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    headers_summary = {
        "accept": "application/json",
        "authorization": "Bearer "+access_token
    }

    responseTopics = requests.request("GET", urlTopics, headers=headers_topicsIntentsEntitiesSentiments)
    responseIntents = requests.request("GET",urlIntents,headers=headers_topicsIntentsEntitiesSentiments)
    responseEntities = requests.request("GET",urlEntities,headers=headers_topicsIntentsEntitiesSentiments)
    responseSummary = requests.get(urlSummary, headers=headers_summary)
    responseSentiments = requests.get(urlSentiments, headers=headers_topicsIntentsEntitiesSentiments)

    for i in responseTopics.json()['topics']:
        allTopics.append(i['text']) 

    for i in ConvertToList(responseSentiments.text):
        if i[:3]=='"su':
            sentimentReport.append(i)
    
    if responseIntents.json() != []:
        for i in responseIntents.json():
            allIntents.append(i['name'].replace('Symbl.',''))
    else:
        allIntents.append("No intents were detected for this audio")

    return {'feature':{'topics': allTopics, 
                  'sentiment': sentimentReport, 
                  'intents': allIntents,
                  'entities': responseEntities.json()['entities'][0]['matches'][0]['detectedValue'],
                  'summary': responseSummary.json()['summary'][0]['text']}}
