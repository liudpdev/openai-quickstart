from typing import Tuple

from langchain_community.llms.chatglm import ChatGLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from utils import LOG

from langchain.chains.llm import LLMChain


class TranslationChain:
    def __init__(
        self,
        base_url: str | None = None,
        verbose: bool = True,
    ):
        # 翻译任务指令始终由 System 角色承担
        template = """You are a translation expert, proficient in various languages. \n
            Translates {source_language} to {target_language}."""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        llm = ChatGLM(
            endpoint_url=base_url,
            max_token=80000,
            top_p=0.9,
            model_kwargs={"sample_model_args": False},
            verbose=verbose,
        )
        self.chain = LLMChain(llm=llm, prompt=chat_prompt_template, verbose=verbose)

    def run(
        self, text: str, source_language: str, target_language: str
    ) -> Tuple[str, bool]:
        result = ""
        try:
            result = self.chain.run(
                {
                    "text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                }
            )
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True
