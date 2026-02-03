import gradio as gr
from gemini_api import GeminiAPI
from utils import count_characters
import os 
from dotenv import load_dotenv

#環境変数を読み込み
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
gemini_api = None
gemini_init_error = None
try:
    if api_key:
        gemini_api = GeminiAPI(api_key=api_key)
    else:
        gemini_init_error = "GEMINI_API_KEYが設定されていません。環境変数または .env を確認してください。"
except Exception as e:
    gemini_init_error = str(e)


def chat_interface(message, history):
    """
    チャットインターフェースのメイン処理

    Args:
        message: ユーザーの入力メッセージ
        history: 会話履歴（Gradio 6.0形式：辞書のリスト）
    Returns:
        更新された会話履歴
    """
    if not message.strip():
        return history
    
    #正確な文字数カウント
    char_count = count_characters(message)

    # Gradioのmessages形式（dictのlist）をGemini用の従来形式に変換
    legacy_history = []
    if history:
        for msg in history:
            if msg.get("role") == "user":
                legacy_history.append([msg.get("content"), None])
            elif msg.get("role") == "assistant" and legacy_history:
                legacy_history[-1][1] = msg.get("content")
    
    # Geminiに送信して応答を取得する
    if gemini_api is None:
        response = (
            f"現在AI応答は利用できません（{gemini_init_error}）。\n\n"
            f"ただし、入力された文章の文字数は **{char_count}文字** です。"
        )
    else:
        response = gemini_api.get_response(message, char_count, legacy_history)

    # 新しい履歴に追加
    if history is None:
        history = []

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
    return history

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
    if gemini_init_error:
        gr.Markdown(
            f"**注意:** {gemini_init_error}\n\n"
            "文字数カウント機能のみ利用できます。"
        )

    chatbot = gr.Chatbot(
        height=500,
        label="チャット",
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
    
    clear.click(lambda: [], outputs=chatbot)  # ← Noneから[]に変更

if __name__ == "__main__":
    port = int(os.getenv("PORT") or os.getenv("GRADIO_SERVER_PORT", "7860"))
    share_enabled = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share_enabled,  # Spacesでは不要。必要時のみ有効化
        theme=gr.themes.Soft()
    )
