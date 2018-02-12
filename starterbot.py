import os
import time
import re
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None

RTM_READ_DELAY = 1
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
REDDIT_REGEX = "(| )((\/r\/)|(r\/))(\w+)"

def parse_bot_commands(slack_events):

	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == starterbot_id:
				return message, event["channel"]
			if parse_reddit_links(event["text"]) is not None:
				message = parse_reddit_links(event["text"])
				post_reddit_link(message, event["channel"])
	return None, None

def parse_reddit_links(message_text):

	matches = re.search(REDDIT_REGEX, message_text)
	return matches.group(5) if matches else None

def post_reddit_link(subreddit, channel):

	response  = "http://reddit.com/r/{}".format(subreddit)

	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response
	)

def parse_direct_mention(message_text):

	matches = re.search(MENTION_REGEX, message_text)
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):

	default_response = "Does not compute. Try *{}*.".format(EXAMPLE_COMMAND)
	response = None
	#implement more commands here
	if command.startswith(EXAMPLE_COMMAND):
		response = "Sure! Write more code then I'll do it!"

	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
	)

if __name__ == "__main__":

	if slack_client.rtm_connect(with_team_state=False):
		print("StartBot connected and running")
		#Read user id by calling web api method 'auth.test'
		starterbot_id = slack_client.api_call("auth.test")["user_id"]
		while True:
			command, channel = parse_bot_commands(slack_client.rtm_read())
			if command:
				handle_command(command,channel)
			time.sleep(RTM_READ_DELAY)
	else:
		print("Connection failed. Traceback printed above")
