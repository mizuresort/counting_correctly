def count_characters(text: str) -> int:
    """
    テキストの正確な文字数をカウント

    Args:
        text: カウント対象のテキスト
    Returns:
        文字数(空白、改行、句読点も含むすべての文字)
    """

    if text is None:
        return 0
    
    #len()
    return len(text)

def format_character_inf0(text: str, char_count: int) -> str:
    """
    文字数情報を整形して返す（デバッグ用)

    Args:
        text:対象テキスト
        char_count:文字数
    Returns:
        整形された文字数情報
    """

    return f"文字数: {char_count}文字\nテキスト：{text[:50]}{'...' if len(text) > 50 else ''}"

def validate_text_input(text: str) -> tuple[bool, str]:
    """
    入力テキストが妥当かチェック

    Args:
        text:チェック対象のテキスト
    Returns:
        (妥当性、エラーメッセージ)
    """

    if text is None or text.strip() == "":
        return False, "テキストが入力されてません"
    
    if len(text) > 100000: #入力が10万超えたら辛いので
        return False, "テキストが長すぎます。10万字が上限です"
    
    return True, ""