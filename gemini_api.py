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

        try:
            #システムプロンプトに文字数を挿入
            system_prompt_with_count = system_prompt.replace("{char_count}", str(char_count))

            #会話履歴を作る
            contents = []

            #過去の会話履歴があれば追加する
            if history and len(history) > 0:
                for user_msg, bot_msg in history:
                    if user_msg:
                        contents_append({
                            "role": "user",
                            "parts" : [{"text": user_msg}]
                        })
                    if bot_msg:
                        contents.append({
                            "role": "model",
                            "parts": [{"text": bot_msg}]
                        })

            #現在のメッセージを追加する
            full_message = f"{system_prompt_with_count}\n\n---ユーザーの入力---\n{user_message}"
            contents.append({
                "role": "user",
                "parts": [{"text": full_message}]
            })

            #リクエストボディの構築
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                }
            } 

            #Gemini API にPOSTリクエスト
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )          

            #レスポンスの確認
            if response.status_code != 200:
                error_detail = response.json() if response.text else "不明なエラー"
                raise Exception(f"API Error (Status {response.status_code}): {error_detail}")
            
            #レスポンスからテキストを抽出
            response_data = response.json()

            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]
            
            raise Exception("APIレスポンスに有効なテキストが含まれていません")
        
        except requests.exceptions.Timeout:
            return f"申し訳ございません。リクエストがタイムアウトしました。\n\nただし、入力された文章は{char_count}文字です。"

        except requests.exceptions.RequestException as e:
            error_message = f"通信エラーが発生しました：{str(e)}"
            print(error_message)
            return f"申し訳ございません。{error_message}\n\nただし入力された文章は{char_count}文字です。"

        except Exception as e:
            error_message = f"エラーが発生しました：{str(e)}"
            print(error_message)
            return f"申し訳ございません。{error_message}\n\nただし、入力された文章は{char_count}文字です。" 