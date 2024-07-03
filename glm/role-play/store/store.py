import os
import os.path

from data_types import TextMsg, CharacterMeta

__curr_dir = os.path.dirname(os.path.abspath(__file__))

__history_path = os.path.join(__curr_dir, "data", "history.txt")
__meta_path = os.path.join(__curr_dir, "data", "meta.txt")
__encoding = "utf-8"


def path_exists(path: str) -> bool:
    return os.path.exists(path)


def get_history() -> list[TextMsg]:
    msg_list = []
    if path_exists(__history_path):
        with open(__history_path, 'r', encoding=__encoding) as file:
            for line in file:
                if not line:
                    continue
                role, content = line.strip().split(":", 1)
                msg_list.append(TextMsg(role=role, content=content))
    return msg_list


def save_history(history: list[TextMsg]) -> None:
    with open(__history_path, "a", encoding=__encoding) as file:
        content = "\n".join([f"{item["role"]}:{item["content"]}" for item in history])
        file.write(content)
        # for item in history:
        #     file.write(f"{item['role']}:{item['content']}\n")


def clear_history() -> None:
    with open(__history_path, 'w', encoding=__encoding):
        pass


def get_meta() -> CharacterMeta:
    meta: CharacterMeta = CharacterMeta(bot_name="", bot_info="", user_name="", user_info="")
    if path_exists(__meta_path):
        with open(__meta_path, 'r', encoding=__encoding) as file:
            line = file.readline().strip()
            if not line:
                return meta
            bot_name, bot_info, user_name, user_info = line.split("|")
            meta = CharacterMeta(user_name=user_name, user_info=user_info, bot_name=bot_name, bot_info=bot_info)
    return meta


def save_meta(meta: CharacterMeta):
    with open(__meta_path, 'w', encoding=__encoding) as file:
        file.write(f"{meta['bot_name']}|{meta['bot_info']}|{meta['user_name']}|{meta['user_info']}")


def clear_meta() -> None:
    with open(__meta_path, 'w', encoding=__encoding):
        pass

# save_meta(CharacterMeta(bot_name="b", bot_info="bi", user_name="u", user_info="ui"))
#
# print(get_meta())
#
# clear_meta()

# save_history([TextMsg(role="user", content="user 1")])
# save_history([TextMsg(role="assistant", content="assistant 1")])
# save_history([TextMsg(role="user", content="user 2")])

# his = get_history()
# print(his)
# print(type(his[0]))

# clear_history()

# print(get_meta())
