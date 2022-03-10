from datetime import datetime, timezone, date
from utils import is_task_waiting_for_user_response, status_was_set_to_waiting, were_comments_from_user
from pyrus import get_forms, get_form_registry, get_task, send_comment


class ClientResponseCheckingBot:
    def __init__(self, task, token, settings):
        self.task = task
        self.token = token
        self.settings = settings

        self.forms = get_forms(self.token)
        self.tasks_to_check = self.get_tasks_to_check()
        self.pyrus_user_ids = self.settings["pyrus_user_ids"]
        self.wip_status_id = 2

    def get_tasks_to_check(self):
        form_tasks = []
        for form in self.forms:
            tasks = get_form_registry(form["id"], self.token)
            if tasks:
                for task in tasks:
                    if is_task_waiting_for_user_response(task):
                        form_tasks.append(get_task(task["id"], self.token))
        return form_tasks

    def get_client_ids(self, task):
        client_ids = []
        for step in task["approvals"]:
            for approval in step:
                approval_id = approval["person"]["id"]
                if approval_id not in self.pyrus_user_ids:
                    client_ids.append(approval_id)
        return client_ids

    def send_remind_comment(self, task_id):
        text = "Для решения вашей задачи 3 рабочих дня назад был задан уточняющий вопрос. Пожалуйста, ответьте! " \
               "Если через 3 рабочих дня от вас не будет ответа, мы завершим задачу автоматически."
        comment = {"text": text}
        send_comment(task_id, self.token, comment)

    def close_task(self, task_id):
        text = "Поскольку в течение 6 рабочих дней от вас не поступило ответа на уточняющий вопрос, мы полагаем, " \
               "что задача потеряла актуальность и автоматически ее завершаем. Если задача еще актуальна для вас, " \
               "то ее можно открыть снова и продолжить работу по ней."
        comment = {"text": text, "action": "finished"}
        send_comment(task_id, self.token, comment)

    def set_wip_status(self, task):
        # ставит статус "В работе" (Work In Progress)
        status_field = [field for field in task["fields"] if field["name"] == "Статус"][0]
        if status_field:
            field_id = status_field["id"]
            field_updates = [
                {
                    "id": field_id,
                    "value": {"choice_ids": [self.wip_status_id]}
                }
            ]
            comment = {"field_updates": field_updates}
            send_comment(task["id"], self.token, comment)

    def check_tasks(self):
        # сервис обходит задачи со статусом "Ожидает ответа от пользователя" и проверяет отвечал ли
        # кто-то со стороны клиента. если ответа не поступило в течении 3 дней, отправляется напоминание
        # если ответа не поступило в течении 6 дней, задача закрывается
        # если ответ был, ставит статус "В работе"
        for task in self.tasks_to_check:
            changed_to_waiting_status_comments = [comm for comm in task["comments"] if status_was_set_to_waiting(comm)]
            last_status_changed_comment = changed_to_waiting_status_comments[-1]
            last_status_changed_date = last_status_changed_comment["create_date"][:-1]

            current_date = datetime.now()
            last_status_changed = datetime.fromisoformat(last_status_changed_date)
            delta = current_date - last_status_changed

            client_ids = self.get_client_ids(task)
            if not were_comments_from_user(task, last_status_changed_date, client_ids):
                if delta.days == 3:
                    return self.send_remind_comment(task["id"])
                if delta.days == 6:
                    return self.close_task(task["id"])
            return self.set_wip_status(task)

    def main(self):
        self.check_tasks()
