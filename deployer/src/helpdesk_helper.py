import os
import re
import json
from . import helpers
from ratelimit import rate_limited
import html


def get_helpscout_api_key():
    hs_api_key = os.environ.get('HELP_SCOUT_API_KEY')

    if not hs_api_key:
        raise ValueError("None HELP_SCOUT_API_KEY from environment variables")

    return hs_api_key


def is_helpdesk_url(u):
    return 'secure.helpscout.net/conversation' in u


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
    hs_api_key = get_helpscout_api_key()

    response_json = json.loads(helpers.make_request(conversation_endpoint,
                                                    username=hs_api_key,
                                                    password="X"))
    conversation = response_json.get('item')

    if not conversation:
        raise ValueError("Wrong json returned from help scout, must have an item attribute")

    return conversation


def get_start_url_from_conversation(conversation):
    if not conversation or not conversation.get('threads')[-1]:
        raise ValueError("Wrong input conversation, must be not evaluate at None and have at least one thread")

    # The message to extract is the first from the thread and it was sent by a customer
    first_thread = conversation.get('threads')[-1]
    was_sent_by_customer = first_thread.get('createdByCustomer')
    url_from_conversation = first_thread.get('body')

    if not len(url_from_conversation):
        raise ValueError("First thread from the conversation thread is empty")

    if not was_sent_by_customer:
        raise ValueError("First thread from the conversation thread wasn't sent by customer")

    print ("URL fetched is \033[1;36m" + url_from_conversation + "\033[0m sent by \033[1;33m" + first_thread.get(
        "customer").get("email") + "\033[0m")

    return url_from_conversation


def get_emails_from_conversation(conversation):
    emails = []

    if not conversation or not conversation.get('threads')[-1]:
        raise ValueError("Wrong input conversation, must be not evaluate at None and have at least one thread")

    # Extract customer
    customer = conversation.get('customer')
    customers_mail = customer.get('email')
    first_thread = conversation.get('threads')[-1]
    was_sent_by_customer = first_thread.get('createdByCustomer')

    if not was_sent_by_customer:
        raise ValueError("First thread from the conversation thread wasn't sent by customer")

    emails.append(customers_mail)

    cc = conversation.get('cc')
    if cc:
        emails = emails + cc

    bcc = conversation.get('bcc')
    if bcc:
        emails = emails + bcc

    if len(emails) > 1:
        print ("Conversation sent by \033[1;33m" + customers_mail + "\033[0m" + (" with " + " ".join(emails[1:])))

    return emails


def add_note(cuid, body):
    conversation_endpoint = "https://api.helpscout.net/v1/conversations/" + cuid + ".json"

    hs_api_key = get_helpscout_api_key()

    # Inserting HTML code into HTML mail, snippet need to be HTML escaped
    body = html.escape(body)

    response = helpers.make_request(conversation_endpoint,
                                    json_request=True,
                                    data={"createdBy": {"id": "75881", "type": "user"},
                                          "type": "note",
                                          "body": body
                                          },
                                    username=hs_api_key,
                                    password="X",
                                    type='POST')

    return response


def get_conversation_url_from_cuid(cuid):
    if not cuid:
        raise ValueError("Wrong input conversation ID")

    return "https://secure.helpscout.net/conversation/" + cuid


def is_docusaurus_conversation(conversation):
    return "docusaurus" in conversation.get("tags")


def is_gitbook_conversation(conversation):
    return "gitbook" in conversation.get("tags")


def is_pkgdown_conversation(conversation):
    return "pkgdown" in conversation.get("tags")


def is_vuepress_conversation(conversation):
    return "vuepress" in conversation.get("tags")

def is_larecipe_conversation(conversation):
    return "larecipe" in conversation.get("tags")


@rate_limited(200, 60)
def search(query, page=1, pageSize=50, sortField="modifiedAt", sortOrder="asc"):
    search_endpoint = "https://api.helpscout.net/v1/search/conversations.json"
    hs_api_key = get_helpscout_api_key()

    response_json = json.loads(helpers.make_request(search_endpoint,
                                                    username=hs_api_key,
                                                    password="X",
                                                    data={
                                                        "query": query,
                                                        "page": page,
                                                        "pageSize": pageSize,
                                                        "sortField": sortField,
                                                        "sortOrder": sortOrder
                                                    },
                                                    json_request=True)
                               )

    return response_json


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
