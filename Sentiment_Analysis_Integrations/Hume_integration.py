import requests
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

HUME_API_KEY = *****

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
    sentiment = 'sentiment'

"""def getJobID(feature,fileName):
  response = requests.post(
    "https://api.hume.ai/v0/batch/jobs",
    headers={
      "X-Hume-Api-Key": "GIiaZ2AZRUWjsBUBqGuG8rcHsPPCKx0RuwTDeTtPTRMrvpSk",
      "Content-Type": "application/json"
    },
    json={
      "urls": [
        "https://dpgr.am/spacewalk.wav"
      ],
      "transcription": {}
    },
  )
  return response.json()"""

@app.get("/v1/transcription")

def uploadAudioFile(flag,file=File(...)):

  #jobID=getJobID(flag,'sample-mp3.mp3')
  if flag == getattr(Flag.transcription,'value'):
      return generateTranscription()
  elif flag == getattr(Flag.sentiment,'value'):
      return generateSentimentReport()

def generateTranscription():

  finalTranscript = []
  response = requests.get(
    "https://api.hume.ai/v0/batch/jobs/a36368af-664a-4817-84af-f494623fa870/predictions",#.format(job_id=jobID),

  headers={
    "X-Hume-Api-Key": HUME_API_KEY
    },
  )
  for i in response.json()[0]['results']['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']:
    finalTranscript.append(i['text'])

  return finalTranscript

def generateSentimentReport():

  sentimentScores = []

  response = requests.get(
    "https://api.hume.ai/v0/batch/jobs/e364e3b9-abff-42f9-86d2-256efc3447aa/predictions",
    headers={
      "X-Hume-Api-Key": HUME_API_KEY
    },
  )

  for i in response.json()[0]['results']['predictions'][0]['models']['language']['grouped_predictions'][0]['predictions']:
     for j in i['sentiment']:
        sentimentScores.append(j['score'])

  sentiment_average = sum(sentimentScores)/len(sentimentScores) 
  if sentiment_average>0.6:
     sentiment='positive'
  elif sentiment_average>0.3:
     sentiment='neutral'
  else:
     sentiment='negative'

  return sentiment
