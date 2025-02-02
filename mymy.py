from typing import Literal, Optional
import random
import time
from dataclasses import dataclass
from enum import Enum

# 定数の定義
PROCESS_DELAYS = {
    "grinding": 2,
    "seasoning": 1,
    "mixing": 3,
    "stuffing": 2,
    "cooking": 3
}

class CookingMethod(Enum):
    BOIL = "茹でる"
    GRILL = "焼く"
    STEAM = "蒸す"

@dataclass
class Meat:
    state: str
    is_seasoned: bool = False
    is_mixed: bool = False

class SausageProcessError(Exception):
    """ソーセージ製造プロセスでのエラーを表すカスタム例外"""
    pass

def grind_meat(delay: bool = True) -> Meat:
    """肉をミンチにする処理"""
    try:
        print("肉をミンチにしています...")
        if delay:
            time.sleep(PROCESS_DELAYS["grinding"])
        return Meat(state="ミンチ肉")
    except Exception as e:
        raise SausageProcessError(f"肉のミンチ処理に失敗: {str(e)}")

def add_spices(meat: Meat, delay: bool = True) -> Meat:
    """調味料を追加する処理"""
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
    """材料を混ぜ合わせる処理"""
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
    """ケーシングに詰める処理"""
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
    """ソーセージを調理する処理"""
    if raw_sausage != "生ソーセージ":
        raise SausageProcessError("無効なソーセージが渡されました")
    
    try:
        method = random.choice(list(CookingMethod))
        print(f"ソーセージを{method.value}調理しています...")
        if delay:
            time.sleep(PROCESS_DELAYS["cooking"])
        return "完成したソーセージ"
    except Exception as e:
        raise SausageProcessError(f"調理に失敗: {str(e)}")

def make_sausage(delay: bool = True) -> Optional[str]:
    """ソーセージを製造する主要プロセス"""
    try:
        meat = grind_meat(delay)
        seasoned_meat = add_spices(meat, delay)
        mixed_meat = mix_ingredients(seasoned_meat, delay)
        raw_sausage = stuff_casing(mixed_meat, delay)
        final_sausage = cook_sausage(raw_sausage, delay)
        print(f"{final_sausage}の製造が完了しました！")
        return final_sausage
    except SausageProcessError as e:
        print(f"エラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    make_sausage()
