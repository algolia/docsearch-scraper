import os
import re
import json
from . import helpers

def get_helpscout_APIKey():
    hs_api_key = os.environ.get('HELP_SCOUT_API_KEY')

    if not hs_api_key:
        raise ValueError("None HELP_SCOUT_API_KEY from environment variables")

    return hs_api_key


def is_helpdesk_url(u):
    return 'secure.helpscout.net/conversation'in u

def get_conversation_ID_from_url(hs_url):
    capture_conversation_uid = re.compile('.+/conversation/(\d+)/.*')
    cuid = capture_conversation_uid.match(hs_url).group(1)

    if not len(cuid) > 0:
        raise ValueError("Wrong help scout url " + hs_url + ", must have a conversation sub part with ID")

    if not RepresentsInt(cuid):
        raise ValueError("Conversation ID : " + cuid + " must be an integer")

    return cuid

def get_conversation(cuid):

    conversation_endpoint = "https://api.helpscout.net/v1/conversations/" + cuid + ".json"
    hs_api_key=get_helpscout_APIKey()

    response_json = json.loads(helpers.make_request(conversation_endpoint, username=hs_api_key, password="X"))
    conversation = response_json.get('item')

    if not conversation:
        raise ValueError("Wrong json returned from help scout, must have an item attribute")

    return conversation

def get_start_url_from_conversation(conversation):

    # The message to extract is the first from the thread and it was sent by a customer
    first_thread = conversation.get('threads')[-1]
    was_sent_by_customer = first_thread.get('createdByCustomer')
    url_from_conversation = first_thread.get('body')

    if not len(url_from_conversation):
        raise ValueError("First thread from the conversation thread is empty")

    if not was_sent_by_customer:
        raise ValueError("First thread from the conversation thread wasn't sent by customer")

    print "URL fetched is \033[1;36m" + url_from_conversation + "\033[0m sent by \033[1;33m" + first_thread.get("customer").get("email") + "\033[0m"

    return url_from_conversation


def add_note(cuid, body):

    conversation_endpoint = "https://api.helpscout.net/v1/conversations/" + cuid + ".json"
    hs_api_key=get_helpscout_APIKey()
    body=body.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
    print body

    response=helpers.make_request(conversation_endpoint,
                        json_request=True,
                         data={ "createdBy":
                                    { "id": "218687", "type": "user" },
                                "type": "note",
                                "body": body },
                         username=hs_api_key,
                         password="X",
                         type='POST')

    return response


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

