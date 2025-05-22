import random
import time
from typing import List

# 時間の遅延を調整するための定数
PROCESSING_TIME = {
    'grind': 2,
    'add_spices': 1,
    'mix': 3,
    'stuff': 2,
    'cook': 3,
}


def grind_meat() -> str:
    """肉をミンチにする処理"""
    print("肉をミンチにしています...")
    time.sleep(PROCESSING_TIME['grind'])
    return "ミンチ肉"


def add_spices(minced_meat: str) -> str:
    """ミンチ肉に調味料を追加する処理"""
    spices: List[str] = ["塩", "コショウ", "ナツメグ", "パプリカ"]
    print(f"{', '.join(spices)}を追加しています...")
    time.sleep(PROCESSING_TIME['add_spices'])
    return f"調味料入り{minced_meat}"


def mix_ingredients(seasoned_meat: str) -> str:
    """調味料を加えた肉をよく混ぜる処理"""
    print(f"{seasoned_meat}をよく混ぜています...")
    time.sleep(PROCESSING_TIME['mix'])
    return f"混ぜられた{seasoned_meat}"


def stuff_casing(mixed_meat: str) -> str:
    """肉をケーシングに詰める処理"""
    print("ケーシングに肉を詰めています...")
    time.sleep(PROCESSING_TIME['stuff'])
    return "生ソーセージ"


def cook_sausage(raw_sausage: str) -> str:
    """ソーセージを調理する処理"""
    cooking_methods: List[str] = ["茹でる", "焼く", "蒸す"]
    method: str = random.choice(cooking_methods)
    print(f"ソーセージを{method}で調理しています...")
    time.sleep(PROCESSING_TIME['cook'])
    return "完成したソーセージ"


def make_sausage() -> None:
    """ソーセージを作る全体の処理"""
    try:
        meat = grind_meat()
        seasoned_meat = add_spices(meat)
        mixed_meat = mix_ingredients(seasoned_meat)
        raw_sausage = stuff_casing(mixed_meat)
        final_sausage = cook_sausage(raw_sausage)
        print(f"{final_sausage}の製造が完了しました！")
    except KeyboardInterrupt:
        print("\n製造が中断されました。")
        raise
    except Exception as e:
        print(f"ソーセージ製造中にエラーが発生しました: {e}")


if __name__ == "__main__":
    make_sausage()
