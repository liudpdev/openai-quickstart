# 导入相关模块，包括运算符、输出解析器、聊天模板、ChatOpenAI 和 运行器
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

chat_ai = ChatOpenAI(model=model_name, base_url=base_url, verbose=True)

# 创建一个计划器，生成一个关于给定输入的论证
planner = (
    ChatPromptTemplate.from_template("{input}")
    | chat_ai
    | StrOutputParser()
    | {"topic": RunnablePassthrough()}
)

java_code = (
    ChatPromptTemplate.from_template("生成{topic}可运行且高效版本的 java 代码")
    | chat_ai
    | StrOutputParser()
)
python_code = (
    ChatPromptTemplate.from_template("生成{topic}可运行且高效版本的 python 代码")
    | chat_ai
    | StrOutputParser()
)
go_code = (
    ChatPromptTemplate.from_template("生成{topic}可运行且高效版本的 go 代码")
    | chat_ai
    | StrOutputParser()
)

# 创建最终响应者，综合原始回应和正反论点生成最终的回应
final_responder = (
    ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "java 代码:\n{java_code}\n\npython 代码:\n{python_code}\n\ngo 代码:\n{go_code}\n\n",
            ),
            (
                "system",
                "将代码分别以良好的格式输出",
            ),
        ]
    )
    | chat_ai
    | StrOutputParser()
)

# 构建完整的处理链，从生成论点到列出正反论点，再到生成最终回应
chain = (
    planner
    | {"java_code": java_code, "python_code": python_code, "go_code": go_code}
    | final_responder
)

# res = chain.invoke({"input": "房地产低迷"})
# print(res)

for s in chain.stream({"input": "快速排序算法"}):
    print(s, end="", flush=True)
