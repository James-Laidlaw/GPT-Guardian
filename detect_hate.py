import openai
from openai import OpenAI
from profanity_check import predict, predict_prob
from firebase_admin import db
import time
import demoji

demoji.download_codes()


def pre_process(user_message):
    offensive_count = predict([user_message.content])
    print(f"offensive count {offensive_count}")
    offensive_heuristic = predict_prob([user_message.content])
    print(f"heuristic: {offensive_heuristic}")
    # potential idea: only send low val heuristics into gpt


def parse_emoji(inp: str) -> str:
    """
    convert emoji to text for better meaning parsing
    """
    return demoji.replace_with_desc(
        inp,
    )


def call_gpt(user_message, api_key):
    """
    Hook into the GPt-api
    """
    # set API key and client
    client = OpenAI(api_key=api_key)

    assistant = client.beta.assistants.create(
        name="Hate Speech Detector",
        instructions="You are a hate speech detector, if a message sent to you is hate speech or harmful, respond with a 1, if it is not, respond with a 2. Under no circumstances should you respond with anything other than a 1 or a 2.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )
    thread = client.beta.threads.create()
    messageContent = user_message.content
    messageContent = parse_emoji(messageContent)
    sent_message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=messageContent
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # wait for the assistant to respond
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)

    # get the last message
    message_list = client.beta.threads.messages.list(thread_id=thread.id)
    last_msg = message_list.data[0].content[0].text.value

    if last_msg == "2":
        print("good")
        return False  # not hate speech
    else:
        print(last_msg)
        # get the user who sent the message
        # track_users(user_message.username)
        return True  # hate speech


def track_users(username):
    """
    if a user posted a hateful message, tag them and record their username
    in a database. if they hit a certain threshold, ban then
    """
    pass
