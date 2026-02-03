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
            raise ValueError(
                "GEMINI_API_KEYが設定されていません。" ".envファイルを確認してください。"
            )

        self.api_key = api_key
        self.api_url = (
            "https://generativelanguage.googleapis.com/v1/models/"
            f"{GEMINI_MODEL}:generateContent?key={api_key}"
        )
        self.history = []  # 会話記録の保持

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
            # システムプロンプトに文字数を挿入
            system_prompt_with_count = system_prompt.replace("{char_count}", str(char_count))

            # 会話履歴を構築
            contents = []

            def _normalize_text(value) -> str:
                if value is None:
                    return ""
                if isinstance(value, str):
                    return value
                # Gradioのmessages形式でcontentがlist/dictになるケースに対応
                if isinstance(value, list):
                    parts = []
                    for item in value:
                        if isinstance(item, str):
                            parts.append(item)
                        elif isinstance(item, dict) and "text" in item:
                            parts.append(str(item.get("text") or ""))
                        else:
                            parts.append(str(item))
                    return "".join(parts)
                if isinstance(value, dict):
                    if "text" in value:
                        return str(value.get("text") or "")
                    return str(value)
                return str(value)

            # 過去の会話履歴があれば追加
            if history and len(history) > 0:
                for user_msg, bot_msg in history:
                    user_text = _normalize_text(user_msg)
                    if user_text:
                        contents.append({
                            "role": "user",
                            "parts": [{"text": user_text}],
                        })
                    bot_text = _normalize_text(bot_msg)
                    if bot_text:
                        contents.append({
                            "role": "model",
                            "parts": [{"text": bot_text}],
                        })

            # 現在のメッセージを追加（システムプロンプト込み）
            full_message = (
                f"{system_prompt_with_count}\n\n---ユーザーの入力---\n"
                f"{_normalize_text(user_message)}"
            )
            contents.append(
                {
                    "role": "user",
                    "parts": [{"text": full_message}],
                }
            )

            # リクエストボディの構築
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                },
            }

            # Gemini APIにPOSTリクエスト
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            # レスポンスの確認
            if response.status_code != 200:
                error_detail = response.json() if response.text else "不明なエラー"
                raise Exception(f"API Error (Status {response.status_code}): {error_detail}")

            # レスポンスからテキストを抽出
            response_data = response.json()

            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"]

            raise Exception("APIレスポンスに有効なテキストが含まれていません")

        except requests.exceptions.Timeout:
            return (
                "申し訳ございません。リクエストがタイムアウトしました。\n\n"
                f"ただし、入力された文章の文字数は **{char_count}文字** です。"
            )

        except requests.exceptions.RequestException as e:
            error_message = f"通信エラーが発生しました: {str(e)}"
            print(error_message)
            return (
                f"申し訳ございません。{error_message}\n\n"
                f"ただし、入力された文章の文字数は **{char_count}文字** です。"
            )

        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            print(error_message)
            return (
                f"申し訳ございません。{error_message}\n\n"
                f"ただし、入力された文章の文字数は **{char_count}文字** です。"
            )
