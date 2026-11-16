#!/usr/bin/env python3
import json
import sys
import urllib.parse
import urllib.request

CONFIG_FILE = "/var/ossec/integrations/telegram.conf"

config = {}
with open(CONFIG_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            config[key] = value

bot_token = config["BOT_TOKEN"]
chat_id = config["CHAT_ID"]

with open(sys.argv[1], "r") as alert_file:
    alert = json.load(alert_file)

rule = alert.get("rule", {})
agent = alert.get("agent", {})

message = (
    "WAZUH SOC LAB ALERT\n\n"
    f"Rule ID: {rule.get('id', 'N/A')}\n"
    f"Level: {rule.get('level', 'N/A')}\n"
    f"Description: {rule.get('description', 'N/A')}\n"
    f"Agent: {agent.get('name', 'N/A')}\n"
)

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

payload = urllib.parse.urlencode({
    "chat_id": chat_id,
    "text": message
}).encode()

urllib.request.urlopen(url, data=payload, timeout=10)