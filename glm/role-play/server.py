"""
基于 CharacterGLM 角色扮演对话工具。
"""

import itertools

import streamlit as st
from dotenv import load_dotenv
from streamlit.delta_generator import DeltaGenerator
from zhipuai import ZhipuAI
from zhipuai.core import StreamResponse
from zhipuai.types.chat.chat_completion_chunk import ChatCompletionChunk

import store.store as store
from data_types import CharacterMeta, CharacterMetaLabel, TextMsg, TextMsgList

# 通过.env文件设置环境变量
# reference: https://github.com/theskumar/python-dotenv
load_dotenv()

client = ZhipuAI()  # 填写您自己的APIKey

st.set_page_config(page_title="角色扮演小工具", page_icon="🤖", layout="wide")

# 初始化
if "history" not in st.session_state:
    st.session_state["history"] = store.get_history()
if "meta" not in st.session_state:
    st.session_state["meta"] = store.get_meta()


def clear_session_history():
    st.session_state["history"] = []
    store.clear_history()


def clear_session_meta():
    st.session_state["meta"] = CharacterMeta(bot_name="", bot_info="", user_name="", user_info="")
    store.clear_meta()
    clear_session_history()


def get_session_meta() -> CharacterMeta:
    return st.session_state["meta"]


def verify_meta() -> bool:
    meta = get_session_meta()
    # 检查`角色名`和`角色人设`是否空，若为空，则弹出提醒
    if meta["bot_name"] == "" or meta["bot_info"] == "":
        st.error("角色名和角色人设不能为空")
        return False
    else:
        return True


# 2x2 layout
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            label=CharacterMetaLabel.bot_name.value,
            value=get_session_meta()["bot_name"],
            key=CharacterMetaLabel.bot_name.name,
            on_change=lambda: get_session_meta().update(
                bot_name=st.session_state[CharacterMetaLabel.bot_name.name]
            ),
            help="模型所扮演的角色的名字，不可以为空",
        )
        st.text_area(
            label=CharacterMetaLabel.bot_info.value,
            value=get_session_meta()["bot_info"],
            key=CharacterMetaLabel.bot_info.name,
            on_change=lambda: get_session_meta().update(
                bot_info=st.session_state[CharacterMetaLabel.bot_info.name]
            ),
            help="角色的详细人设信息，不可以为空",
        )

    with col2:
        st.text_input(
            label=CharacterMetaLabel.user_name.value,
            value=get_session_meta()["user_name"] or "用户",
            key=CharacterMetaLabel.user_name.name,
            on_change=lambda: get_session_meta().update(
                user_name=st.session_state[CharacterMetaLabel.user_name.name]
            ),
            help="用户的名字，默认为用户",
        )
        st.text_area(
            label=CharacterMetaLabel.user_info.value,
            value=get_session_meta()["user_info"],
            key=CharacterMetaLabel.user_info.name,
            on_change=lambda: get_session_meta().update(
                user_info=st.session_state[CharacterMetaLabel.user_info.name]
            ),
            help="用户的详细人设信息，可以为空",
        )

    button_labels = {
        "clear_meta": "清空人设",
        "clear_history": "清空对话历史"
    }

    n_button = len(button_labels)
    cols = st.columns(n_button)
    button_key_to_col = dict(zip(button_labels.keys(), cols))

    with button_key_to_col["clear_meta"]:
        clear_meta = st.button(button_labels["clear_meta"], key="clear_meta", help="清空人设同时会清空对话历史")
        if clear_meta:
            clear_session_meta()
            st.rerun()

    with button_key_to_col["clear_history"]:
        clear_history = st.button(button_labels["clear_history"], key="clear_history")
        if clear_history:
            clear_session_history()
            st.rerun()

# 展示对话历史
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(msg["content"])
    else:
        raise Exception("Invalid role")

with st.chat_message(name="user", avatar="user"):
    input_placeholder = st.empty()
with st.chat_message(name="assistant", avatar="assistant"):
    message_placeholder = st.empty()


def get_characterglm_stream_response(messages: TextMsgList, meta: CharacterMeta) -> StreamResponse[ChatCompletionChunk]:
    return client.chat.completions.create(
        model="charglm-3",
        meta=meta,
        messages=messages,
        stream=True
    )


def output_stream_response(response: StreamResponse[ChatCompletionChunk], placeholder: DeltaGenerator):
    content = ""
    for content in itertools.accumulate([chunk.choices[0].delta.content for chunk in response]):
        placeholder.markdown(content)
    return content


def start_chat():
    query = st.chat_input("开始对话吧")
    if not query:
        return
    else:
        if not verify_meta():
            return

        store.save_meta(get_session_meta())

        input_placeholder.markdown(query)
        st.session_state["history"].append(TextMsg(role="user", content=query))
        stream_response = get_characterglm_stream_response(
            messages=st.session_state["history"],
            meta=st.session_state["meta"]
        )

        bot_response = output_stream_response(stream_response, message_placeholder)
        if not bot_response:
            message_placeholder.markdown("生成出错")
            st.session_state["history"].pop()
        else:
            st.session_state["history"].append(TextMsg(role="assistant", content=bot_response))

            store.save_history(st.session_state["history"][-2:])


start_chat()
