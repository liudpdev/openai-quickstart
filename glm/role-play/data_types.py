"""
相关数据类型的定义
"""
import os
from enum import Enum
from typing import TYPE_CHECKING, List, Literal, TypedDict

from dotenv import load_dotenv

if TYPE_CHECKING:
    pass


class BaseMsg(TypedDict):
    pass


class TextMsg(BaseMsg):
    """文本消息"""
    role: Literal["user", "assistant"]
    """消息来源"""
    content: str
    """消息内容"""


TextMsgList = List[TextMsg]


class CharacterMeta(TypedDict):
    """角色扮演设定，它是CharacterGLM API所需的参数"""

    """用户人设"""
    bot_name: str
    """bot扮演的角色的名字"""
    bot_info: str
    """角色人设"""
    user_name: str
    """用户的名字"""
    user_info: str


class CharacterMetaLabel(str, Enum):
    bot_name = "角色名"
    bot_info = "角色人设"
    user_name = "用户名"
    user_info = "用户人设"


load_dotenv()


def demo():
    print(os.getenv("ZHIPUAI_API_KEY"))
    # print("name: " + CharacterMetaLabel.user_info.name)
    # print("value: " + CharacterMetaLabel.user_info.value)


demo()
