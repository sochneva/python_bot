from bot import ClientResponseCheckingBot
import json


def lambda_handler(event, context):
    if isinstance(event, str):
        event = json.loads(event)

    if "body" in event:
        try:
            data = json.loads(event["body"])
        except json.JSONDecodeError:
            data = event["body"]

        task = data["task"]
        token = data["access_token"]
        settings = None
        if "bot_settings" in data:
            try:
                settings = json.loads(data["bot_settings"])
            except (json.JSONDecodeError, TypeError):
                print("Невалидный JSON")

        bot = ClientResponseCheckingBot(task, token, settings)
        bot.main()

    return {"statusCode": 200}

