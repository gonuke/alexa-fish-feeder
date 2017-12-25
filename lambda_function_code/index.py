"""
This will record and/or read back the last time the fish were fed
"""

from __future__ import print_function

import time
from datetime import datetime

def lambda_handler(event,context):
    """
    Determine which kind of request and route to the appropriate code.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    
    if event['session']['type'] == "LaunchRequest":
        return on_launch(event['request'],event['session'])
    elif event['session']['type'] == "IntentType":
        return on_intent(event['request'],event['session'])
    elif event['session']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'],event['session'])

# ----- Functions that unpack specific requests

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    return get_welcome_response()
    
def on_intent(intent_request, session):
    """
    parses which intent and calls the appropriate behavior
    """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "FishFeederWriteLogIntent":
        return handle_log_timestamp(intent_request,session)
    elif intent_name == "FishFeederReadLogIntent":
        return handle_read_log(intent_request,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")
    
def on_session_ended(session_ended_request,session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
# ----- Functions that implement the skill's behavior

def get_welcome_response():

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Fish Feeder Log.  You can tell me that you fed the fish, or ask when the fish were fed"
    reprompt_text = speech_output
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_log_timestamp(log_request,session):
    """
    Capture the current time stamp and save it for future recall."
    """

    timestamp = log_request['timestamp']

    save_timestamp(timestamp)

    session_attributes = {}
    card_title = "Logged"
    speech_output = "I have recorded that you just fed the fish."
    reprompt_text = speech_output
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_read_log(read_request,session):
    """
    Fetch the last time the fish were fed from the log and repeat it to the user.
    """

    dt_timestamp = fetch_log()

    session_attributes = {}
    card_title = "Reported"
    speech_output = "The last time you reported feeding the fish was " + convert_to_speech(timestamp)
    reprompt_text = speech_output
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = "You can tell me that you fed the fish, or ask when the fish were fed."
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

    
def handle_session_end_request():
    session_attributes = {}
    card_title = "Session Ended"
    speech_output = "Thank you for using the Fish Feeder skill! We hope you enjoyed the experience."
    reprompt_text = speech_output
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# ---- Data management

def save_timestamp(timestamp):
    """
    This method will use some form of persistent storage to save requests
    """
    pass

def fetch_log():
    """
    This method will read the persistent storage to find the last feeding.
    """
    simulated_timeshift = 7200
    return datetime.fromtimestamp(time.time() - simulated_timeshift)

def convert_to_speech(dt_timestamp):
    """
    Use intelligent processing to convert to speech
    """

    one_hour = 3600
    one_day = 24 * one_hour
    
    current_time = datetime.fromtimestamp(time.time())

    delta_time = int((current_time - dt_timestamp).total_seconds())

    if (delta_time < one_hour):
        return "less than 1 hour ago."
    elif (delta_time < one_day):
        hours = str(int(delta_time / one_hour))
        return "just over " + hours + " ago."
    else:
        return "more than 1 day ago."

    

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
