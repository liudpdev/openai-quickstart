import os
from enum import Enum

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from langchain.chains.retrieval_qa.base import BaseRetrievalQA, RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter


class SalesType(str, Enum):
    RealEstateSales = "real_estate_sales"
    HomeImprovementSales = "home_improvement_sales"
    OnlineEducationSales = "online_education_sales"


__sales_types = {
    SalesType.RealEstateSales.value: "房地产销售",
    SalesType.HomeImprovementSales.value: "家装销售",
    SalesType.OnlineEducationSales.value: "在线教育销售",
}

__embeddings = OpenAIEmbeddings()


def get_sales_types() -> list[tuple[str, str]]:
    return [(v, k) for k, v in __sales_types.items()]


def get_current_dir():
    current_file_path = os.path.abspath(__file__)
    return os.path.dirname(current_file_path)


def create_docs(sales_type: SalesType) -> list[Document]:
    file_path = get_current_dir() + "/data/raw/" + sales_type.value + "_data.txt"
    with open(file_path) as f:
        sales_raw_data = f.read()

    text_splitter = CharacterTextSplitter(
        separator=r"\d+\.\n",
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=True,
    )

    return text_splitter.create_documents([sales_raw_data])


def get_store_dir(dir_name: str):
    return get_current_dir() + "/data/local_store/" + dir_name


def save_local_vector_store(sales_type: SalesType):
    docs = create_docs(sales_type)

    db = FAISS.from_documents(docs, __embeddings)
    save_dir = get_store_dir(sales_type.value)
    db.save_local(save_dir)


def store_dir_exists(dir_name: str) -> bool:
    dir_path = get_store_dir(dir_name)

    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        return False


__sales_bots: dict[str, BaseRetrievalQA] = {
    SalesType.RealEstateSales.value: None,
    SalesType.HomeImprovementSales.value: None,
    SalesType.OnlineEducationSales.value: None,
}


def initialize_sales_bots():
    for st in [
        SalesType.RealEstateSales,
        SalesType.HomeImprovementSales,
        SalesType.OnlineEducationSales,
    ]:
        __sales_bots[st.value] = create_sales_bot(st)


def create_sales_bot(sales_type: SalesType) -> BaseRetrievalQA:
    dir_name = sales_type.value
    if not store_dir_exists(dir_name):
        save_local_vector_store(sales_type)

    store_dir = get_store_dir(dir_name)
    db = FAISS.load_local(store_dir, __embeddings, allow_dangerous_deserialization=True)

    llm = ChatOpenAI(
        model_name=os.getenv("OPENAI_MODEL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )

    bot = RetrievalQA.from_chain_type(
        llm,
        retriever=db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.7},
        ),
    )
    # 返回向量数据库的检索结果
    bot.return_source_documents = True
    return bot


def sales_chat(message, history, sales_type: str):
    print(f"[message]{message}")
    print(f"[history]{history}")
    # TODO: 从命令行参数中获取
    enable_chat = True

    bot = __sales_bots[sales_type]
    ans = bot({"query": message})
    resp = f"【{__sales_types[sales_type]}】： "
    # 如果检索出结果，或者开了大模型聊天模式
    # 返回 RetrievalQA combine_documents_chain 整合的结果
    if ans["source_documents"] or enable_chat:
        print(f"[result]{ans['result']}")
        print(f"[source_documents]{ans['source_documents']}")
        resp += ans["result"]
    # 否则输出套路话术
    else:
        resp += "这个问题我要问问领导"

    return resp
