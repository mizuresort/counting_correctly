from dotenv import load_dotenv
import os
import requests
from prompt_config import system_prompt, GEMINI_MODEL

class GeminiAPI:
    """Gemini APIとのやりとりを管理するクライアント"""

    def __init__(self, api_key: str):
        """
        Gemini_apiの初期化
        
        Args:
            api_key: GEMINI apiキー
        """

        if not api_key:
            raise ValueError("GEMINI_API_KEYが設定されていません。" \
            ".envファイルを確認してください。")
        
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        self.history = [] #会話記録の保持

    
    def get_response(self, user_message: str, char_count: int, history: list = None) -> str:
        """
        ユーザメッセージに対するGEMINIの応答を取得する

        Args:
            user_message: ユーザーの入力メッセージ
            char_count: システムが計測した正確な文字数
            history: 会話履歴(Gradio)形式

        Returns:
            GEMINIからの応答テキスト
        """