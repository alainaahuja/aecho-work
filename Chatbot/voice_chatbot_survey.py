from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import base64
import json
import queue
import requests
import websocket

#Test Key & config id used - needs to be changed
HUME_API_KEY = 'GIiaZ2AZRUWjsBUBqGuG8rcHsPPCKx0RuwTDeTtPTRMrvpSk'
EVI_CONFIG_ID = 'f289ba70-7487-4167-aa71-aa078d891ad3'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:MgFFpsyuFOBuBbmo@34.68.125.220/aechodeva1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
CORS(app)

message_queue = queue.Queue()

ws_url = "wss://api.hume.ai/v0/evi/chat?config_id="+EVI_CONFIG_ID+"&api_key="+HUME_API_KEY

class AnalysisData(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    prosody = db.Column(db.String, nullable = False)

with app.app_context():
    db.create_all()

@app.route('/chat', methods=['POST'])
def chat():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    audio_data = file.read()

    print(defineConfiguration('explicit', 3, 1))

    establish_connection(ws_url, audio_data)

    response = getAnalysis()
    return jsonify(response)

def defineConfiguration (MODE, numOfQuestions, survey_duration):
    url = "https://api.hume.ai/v0/evi/configurations/"+EVI_CONFIG_ID


    MODE_txt = ''
    if MODE == 'explicit':
        MODE_txt = '<explicitMode>Do not create any questions independently. All survey questions should be the following questions:'+str(survey_questions)+'. All questions should be asked of the user verbatim.</explicitMode>'

    headers = {
        "X-Hume-Api-Key": HUME_API_KEY,
        "Content-Type": "application/json"
    }
    config_data = {
        "prompt": "<role>You are a mental health chatbot for Aecho, here to conduct a survey regarding the mental wellbeing of the user. You will be asking "+str(numOfQuestions)+" questions beginning with "+seed_question+". Stop after "+str(survey_duration)+" minutes or when the user says the phrase 'end survey'.</role>"+MODE_txt
    }

    response=requests.put(url, headers=headers,json=config_data)
    
    return response

def encodeAudio(file):
    return base64.b64encode(file).decode('utf-8')

def establish_connection(ws_url, audio_data):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_open=lambda ws: ws.send(json.dumps(generateMessage(audio_data))),
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_ping=on_ping)
    ws.run_forever()

def generateMessage(file):
    return {"type": "audio_input", "data": encodeAudio(file)}

def getAnalysis():
    messages = []
    while not message_queue.empty():
        messages.append(message_queue.get())
    return messages

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_error(ws, error):
    print(f"Error: {error}")

def on_message(ws, message):
    receivedMessage = f"{message}"
    #print("Received message:", receivedMessage)
    message_queue.put(json.loads(receivedMessage))

def on_open(ws):
    print("WebSocket connection opened")

def on_ping(ws, message):
    ws.send(message, websocket.ABNF.OPCODE_PONG)

@app.route('/submit',methods=['POST'])
def submit_analysis():
    data = request.json
    prosody = data.get('prosody')

    if not prosody:
        return jsonify({'error': 'prosody data not found'}), 400
    
    new_prosody=AnalysisData(prosody=prosody)
    db.session.add(new_prosody)
    db.session.commit()

    return jsonify({'message':'Prosody data successfuly saved'})


if __name__ == '__main__':
    app.run(port=5000)
