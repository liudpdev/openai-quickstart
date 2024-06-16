import gradio as gr
from sales_chatai import get_sales_types, initialize_sales_bots, sales_chat


def echo(message, history, sales_type: str):
    return f"{sales_type}: {message}"


def launch_gradio():
    with gr.Blocks() as gr_server:
        gr.Markdown(
            """
            # 销售培训助手
            """
        )
        sales_types = get_sales_types()
        sales_selector = gr.Dropdown(
            get_sales_types(),
            value=sales_types[0][1],
            type="value",
            label="选择销售类型",
        )

        gr.ChatInterface(
            sales_chat,
            chatbot=gr.Chatbot(height=600, render=False),
            additional_inputs=[sales_selector],
        )

    gr_server.launch(share=False)


if __name__ == "__main__":
    # 初始化房产销售机器人
    initialize_sales_bots()
    # 启动 Gradio 服务
    launch_gradio()
