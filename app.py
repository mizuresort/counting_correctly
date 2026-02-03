import gradio as gr
from gemini_api import GeminiAPI
from utils import count_characters
import os 
from dotenv import load_dotenv

#環境変数を読み込み
load_dotenv()

#GEMINIクライアントの初期化
gemini_api = GeminiAPI(api_key=os.getenv("GEMINI_API_KEY"))


def chat_interface(message, history):
    """
    チャットインターフェースのメイン処理

    Args:
        message: ユーザーの入力メッセージ
        history: 会話履歴
    Returns:
        GEMINIからの応答
    """

    #正確な文字数カウント
    char_count = count_characters(message)

    #Geminiに送信して応答を取得する
    response = gemini_api.get_response(message, char_count, history)

    return response

#Gradio UI
with gr.Blocks(title="正確な文字数カウンターAI") as demo:
    gr.Markdown(
        """
       # 正確な文字数カウンターAI
        
        文字数を正確にカウントし、ChatGPTやGeminiのように会話できるアシスタントです。
        
        **できること：**
        - 送信した文章の正確な文字数カウント
        - 文字数調整（圧縮・拡張）
        - 通常のAI会話 
        """
    )

    chatbot = gr.Chatbot(
        height = 500, 
        label = "チャット",
        #bubble_full_width=False,
    )

    with gr.Row():
        msg = gr.Textbox(
            label="メッセージを入力",
            placeholder="文章を入力してください。",
            lines=3, 
            scale=4,
        )
    
    with gr.Row():
        submit = gr.Button("送信", variant="primary", scale=1)
        clear = gr.Button("会話をクリア", scale=1)
    
    gr.Markdown(
        """
        ### 使い方の例：
        - 「この文章の文字数を教えて」
        - 「これを100文字以内にして」
        - 「もっと詳しく書いて」
        - 通常の会話も可能です
        """
    )

    # イベントハンドラー
    submit.click(
        chat_interface,
        inputs=[msg, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        outputs=msg
    )
    
    msg.submit(
        chat_interface,
        inputs=[msg, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        outputs=msg
    )
    
    clear.click(lambda: None, outputs=chatbot)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
    )