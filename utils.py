def status_was_set_to_waiting(comment):
    # проверяет менялся ли в комменатрии статус на "Ожидает ответа от пользователя"
    if "field_updates" in comment:
        updated_fields = comment["field_updates"]
        return any(map(lambda x: x["name"] == "Статус" and x["value"]["choice_id"] == 3, updated_fields))


def is_task_waiting_for_user_response(task):
    # проверяет стоит ли у задачи статус "Ожидает ответа от пользователя"
    return any(map(lambda x: x["name"] == "Статус" and x["value"]["choice_id"] == 3, task["fields"]))


def were_comments_from_user(task, status_changed_time, user_ids):
    #  проверяет были ли ответы от пользователей со стороны клиента
    comments = [comm for comm in task["comments"] if comm["create_date"] > status_changed_time]
    for comment in comments:
        if comment["author"]["id"] in user_ids:
            return True
    return False
