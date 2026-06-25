from deepgram import Deepgram
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

#DEEPGRAM_API_KEY = *****
DEEPGRAM_API_KEY = *****

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Flag(Enum):
    transcription='transcription'
    topic = 'topic'
    sentiment = 'sentiment'
    intent='intent'
    entity = 'entity'
    summarization = 'summarization'
    feature='feature'

#Retrieves flagged feature(s) from passed file 
@app.get("/v1/transcription")

def retrieveFeatureReport(flag, file=File(...)):
    
    deepgram = Deepgram(DEEPGRAM_API_KEY)

    source = {'url':file}

    #Check flag values to call and return reports 
    if flag == getattr(Flag.transcription,'value'):
        return generateTranscription(source,deepgram)
    elif flag == getattr(Flag.topic,'value'):
        return generateTopicReport(source,deepgram)
    elif flag == getattr(Flag.sentiment,'value'):
        return generateSentimentReport(source,deepgram)
    elif flag == getattr(Flag.intent,'value'):
        return generateIntentReport(source,deepgram)
    elif flag == getattr(Flag.entity,'value'):
        return generateEntityReport(source,deepgram)
    elif flag == getattr(Flag.summarization,'value'):
        return generateSummary(source,deepgram)
    elif flag == getattr(Flag.feature,'value'):
        return generateFeatureOverview(source, deepgram)


def generateTranscription(sourceFile,deepgramObj):
    options={'punctuate':True}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    transcription = response['results']['channels'][0]['alternatives'][0]['transcript']
    finalReport = {'body': {'transcription':transcription}}
    return finalReport

def generateTopicReport(sourceFile,deepgramObj):
    options = {'detect_topics': True,}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    topics = [j for i in response['results']['channels'][0]['alternatives'][0]['topics'] for j in i['topics'] ]
    finalReport = {'body': {'topics': topics}}
    return finalReport

def generateSentimentReport(sourceFile,deepgramObj):
    options = {'sentiment':True}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    sentiments = response['results']['sentiments']['average']
    finalReport = {'body':{'sentiment': sentiments}}
    return finalReport

def generateIntentReport(sourceFile, deepgramObj):
    options = {'intents':True}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    intents = [j for i in response['results']['intents']['segments'] for j in i['intents']]
    finalReport = {'body':{'intents': intents}}    
    return finalReport

def generateEntityReport(sourceFile,deepgramObj):
    options = {'detect_entities':True}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    entities = response['results']['channels'][0]['alternatives'][0]['entities']
    finalReport = {'body':{'entities': entities}}
    return finalReport

def generateSummary(sourceFile, deepgramObj):
    options = {'punctuate': True ,'summarize':'v2'}
    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)
    summary = response['results']['summary']['short']
    finalReport = {'body':{'summary': summary}}
    return finalReport

def generateFeatureOverview(sourceFile, deepgramObj):
    options = {'detect_topics':True, 'sentiment':True, 'intents':True,'detect_entities':True, 'summarize':'v2','punctuate':True}

    response = deepgramObj.transcription.sync_prerecorded(sourceFile, options)

    topics = [j for i in response['results']['channels'][0]['alternatives'][0]['topics'] for j in i['topics'] ]
    sentiments = response['results']['sentiments']['average']
    intents = [j for i in response['results']['intents']['segments'] for j in i['intents']]
    entities = response['results']['channels'][0]['alternatives'][0]['entities']
    summary = response['results']['summary']['short']

    finalReport = {'body':{'topics': topics, 
                  'sentiment': sentiments, 
                  'intents': intents,
                  'entities': entities,
                  'summary': summary}}
    
    return finalReport
