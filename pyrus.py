import requests
import json


def get_form(form_id, token):
    url = f"https://api.pyrus.com/v4/forms/{form_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        form = response.json()
        return form
    else:
        print(response.text)


def get_forms(token):
    url = f"https://api.pyrus.com/v4/forms"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        forms = response.json()
        return forms["forms"]
    else:
        print(response.text)


def get_form_registry(form_id, token):
    url = f"https://api.pyrus.com/v4/forms/{form_id}/register"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        registry = response.json()
        return registry["tasks"]
    else:
        print(response.text)


def get_task(task_id, token):
    url = f"https://api.pyrus.com/v4/tasks/{task_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        task = response.json()
        return task["task"]
    else:
        print(response.text)


def send_comment(task_id, token, comment):
    url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(comment)
    )
    return response


def error_report(task_id, token, error_message):
    comment = {"text": error_message, "approval_choice": "rejected"}
    print(error_message)
    send_comment(task_id, token, comment=json.dumps(comment))
