import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# 定数の定義
PROCESS_DELAYS = {
    "grinding": 2,
    "seasoning": 1,
    "mixing": 3,
    "stuffing": 2,
    "cooking": 3
}


class CookingMethod(Enum):
    """調理方法を定義するEnum"""
    BOIL = "茹でる"
    GRILL = "焼く"
    STEAM = "蒸す"


@dataclass
class Meat:
    """肉の状態を管理するデータクラス"""
    state: str
    is_seasoned: bool = False
    is_mixed: bool = False


class SausageProcessError(Exception):
    """ソーセージ製造プロセスでのエラーを表すカスタム例外"""
    pass


def grind_meat(delay: bool = True) -> Meat:
    """肉をミンチにする処理
    
    Args:
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: ミンチ状態の肉オブジェクト
        
    Raises:
        SausageProcessError: 肉のミンチ処理に失敗した場合
    """
    try:
        print("肉をミンチにしています...")
        if delay:
            time.sleep(PROCESS_DELAYS["grinding"])
        return Meat(state="ミンチ肉")
    except Exception as e:
        raise SausageProcessError(f"肉のミンチ処理に失敗: {str(e)}")


def add_spices(meat: Meat, delay: bool = True) -> Meat:
    """調味料を追加する処理
    
    Args:
        meat: 肉オブジェクト
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: 調味料が追加された肉オブジェクト
        
    Raises:
        SausageProcessError: 無効な材料または調味料追加に失敗した場合
    """
    if not isinstance(meat, Meat) or meat.state != "ミンチ肉":
        raise SausageProcessError("無効な材料が渡されました")
    
    spices = ["塩", "コショウ", "ナツメグ", "パプリカ"]
    try:
        print(f"{', '.join(spices)}を追加しています...")
        if delay:
            time.sleep(PROCESS_DELAYS["seasoning"])
        meat.is_seasoned = True
        return meat
    except Exception as e:
        raise SausageProcessError(f"調味料の追加に失敗: {str(e)}")


def mix_ingredients(meat: Meat, delay: bool = True) -> Meat:
    """材料を混ぜ合わせる処理
    
    Args:
        meat: 調味料が追加された肉オブジェクト
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: 混ぜ合わされた肉オブジェクト
        
    Raises:
        SausageProcessError: 調味料が未追加または混合に失敗した場合
    """
    if not meat.is_seasoned:
        raise SausageProcessError("調味料が追加されていません")
    
    try:
        print(f"{meat.state}をよく混ぜています...")
        if delay:
            time.sleep(PROCESS_DELAYS["mixing"])
        meat.is_mixed = True
        return meat
    except Exception as e:
        raise SausageProcessError(f"材料の混合に失敗: {str(e)}")


def stuff_casing(meat: Meat, delay: bool = True) -> str:
    """ケーシングに詰める処理
    
    Args:
        meat: 混ぜ合わされた肉オブジェクト
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        str: 生ソーセージの状態
        
    Raises:
        SausageProcessError: 材料が未混合またはケーシング詰めに失敗した場合
    """
    if not meat.is_mixed:
        raise SausageProcessError("材料が適切に混ぜられていません")
    
    try:
        print("ケーシングに肉を詰めています...")
        if delay:
            time.sleep(PROCESS_DELAYS["stuffing"])
        return "生ソーセージ"
    except Exception as e:
        raise SausageProcessError(f"ケーシング詰めに失敗: {str(e)}")


def cook_sausage(raw_sausage: str, delay: bool = True) -> str:
    """ソーセージを調理する処理
    
    Args:
        raw_sausage: 生ソーセージ
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        str: 完成したソーセージ
        
    Raises:
        SausageProcessError: 無効なソーセージまたは調理に失敗した場合
    """
    if raw_sausage != "生ソーセージ":
        raise SausageProcessError("無効なソーセージが渡されました")
    
    try:
        method = random.choice(list(CookingMethod))
        print(f"ソーセージを{method.value}で調理しています...")
        if delay:
            time.sleep(PROCESS_DELAYS["cooking"])
        return "完成したソーセージ"
    except Exception as e:
        raise SausageProcessError(f"調理に失敗: {str(e)}")


def make_sausage(delay: bool = True) -> Optional[str]:
    """ソーセージを製造する主要プロセス
    
    Args:
        delay: 各工程での処理時間遅延を有効にするかどうか
        
    Returns:
        Optional[str]: 完成したソーセージ、失敗時はNone
    """
    try:
        meat = grind_meat(delay=delay)
        seasoned_meat = add_spices(meat, delay=delay)
        mixed_meat = mix_ingredients(seasoned_meat, delay=delay)
        raw_sausage = stuff_casing(mixed_meat, delay=delay)
        final_sausage = cook_sausage(raw_sausage, delay=delay)
        print(f"{final_sausage}の製造が完了しました！")
        return final_sausage
    except SausageProcessError as e:
        print(f"エラーが発生しました: {str(e)}")
        return None
    except KeyboardInterrupt:
        print("\n製造が中断されました。")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}")
        return None


if __name__ == "__main__":
    make_sausage()
