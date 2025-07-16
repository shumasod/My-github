import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

# 🍴 調理プロセスの時間定数（美味しさを引き出すための最適時間）
GOURMET_PROCESS_DELAYS = {
    "grinding": 2,      # 🥩 肉の繊維を丁寧にほぐす時間
    "seasoning": 1,     # 🌿 スパイスの香りを肉に浸透させる時間
    "mixing": 3,        # 🥄 全体を均一に混ぜ合わせる時間
    "stuffing": 2,      # 🌭 ケーシングに愛情込めて詰める時間
    "cooking": 3        # 🔥 完璧な焼き色を付ける時間
}

# 🎨 美味しそうな調理音
COOKING_SOUNDS = {
    "sizzle": "ジュージュー♪",
    "bubble": "ぐつぐつ♪",
    "steam": "シューッ♪",
    "crackle": "パチパチ♪"
}

# 🌺 豊かな香りの表現
AROMAS = [
    "肉汁のジューシーな香り",
    "スパイスの芳醇な香り",
    "焼けた表面の香ばしい香り",
    "ハーブの爽やかな香り",
    "燻製の深い香り"
]


class GourmetCookingMethod(Enum):
    """🍳 美食家も認める調理方法"""
    GENTLE_BOIL = ("優しく茹でる", "🍲", "じっくりと旨味を閉じ込める伝統製法")
    PERFECT_GRILL = ("完璧にグリル", "🔥", "表面はカリッと、中はジューシーに")
    STEAM_DELICATE = ("繊細に蒸す", "💨", "素材の持つ自然な味わいを最大限に引き出す")
    SMOKE_ARTISAN = ("職人の燻製", "🌪️", "深みのある燻香で贅沢な仕上がり")
    
    def __init__(self, description: str, emoji: str, technique: str):
        self.description = description
        self.emoji = emoji
        self.technique = technique


@dataclass
class PremiumMeat:
    """🥩 最高級の肉の状態管理"""
    state: str
    quality_grade: str = "A5"  # 🌟 最高品質グレード
    temperature: float = 18.0  # 🌡️ 最適な肉温度
    marbling_score: int = 12   # 🎯 霜降りスコア（最高12点）
    is_seasoned: bool = False
    is_mixed: bool = False
    aroma_level: int = 0       # 👃 香りの強さ（0-10）
    texture_score: int = 0     # 🤤 食感スコア（0-10）
    
    def describe_quality(self) -> str:
        """肉の品質を美味しそうに説明"""
        descriptions = []
        if self.quality_grade == "A5":
            descriptions.append("🌟 最高級A5ランクの極上肉")
        if self.marbling_score >= 10:
            descriptions.append("💎 美しい霜降りが織り成す芸術的な肉質")
        if self.aroma_level >= 8:
            descriptions.append("🌹 豊かな香りが食欲をそそる")
        return " | ".join(descriptions)


class GourmetSausageError(Exception):
    """🚨 美食ソーセージ製造でのエラー"""
    pass


def select_premium_ingredients() -> List[str]:
    """🛒 最高級食材の選定"""
    premium_spices = [
        "🧂 フランス産ゲランドの塩",
        "🌶️ マレーシア産黒胡椒",
        "🌰 グルノーブル産ナツメグ",
        "🌹 ハンガリー産パプリカ",
        "🌿 地中海産ローズマリー",
        "🧄 イタリア産ガーリック"
    ]
    
    selected = random.sample(premium_spices, random.randint(4, 6))
    print("🎯 本日の厳選スパイス:")
    for spice in selected:
        print(f"   ✨ {spice}")
    return selected


def grind_premium_meat(delay: bool = True) -> PremiumMeat:
    """🥩 最高級肉の繊細なミンチ加工
    
    Args:
        delay: 丁寧な加工時間を再現するかどうか
        
    Returns:
        PremiumMeat: 完璧にミンチされた最高級肉
        
    Raises:
        GourmetSausageError: ミンチ加工に問題が発生した場合
    """
    try:
        print("🔪 ✨ 熟練シェフによる肉のミンチ加工を開始...")
        print("   🎯 肉の繊維を丁寧に断ち切り、最適な粒度に調整中...")
        
        if delay:
            for i in range(GOURMET_PROCESS_DELAYS["grinding"]):
                print(f"   ⏰ 加工中... {COOKING_SOUNDS['crackle']} ({i+1}/{GOURMET_PROCESS_DELAYS['grinding']})")
                time.sleep(1)
        
        meat = PremiumMeat(
            state="🥩 極上ミンチ肉",
            texture_score=9,
            aroma_level=6
        )
        
        print(f"   ✅ 完成！{meat.describe_quality()}")
        print(f"   🎨 美しいピンク色の肉が、{random.choice(AROMAS)}を放っています")
        
        return meat
        
    except Exception as e:
        raise GourmetSausageError(f"🚨 極上ミンチ加工に失敗: {str(e)}")


def add_aromatic_spices(meat: PremiumMeat, delay: bool = True) -> PremiumMeat:
    """🌿 香り豊かなスパイスブレンド
    
    Args:
        meat: 最高級肉オブジェクト
        delay: スパイスの馴染み時間を再現するかどうか
        
    Returns:
        PremiumMeat: 香り豊かに調味された肉
        
    Raises:
        GourmetSausageError: 無効な材料または調味に失敗した場合
    """
    if not isinstance(meat, PremiumMeat) or "ミンチ肉" not in meat.state:
        raise GourmetSausageError("🚨 最高級ミンチ肉以外は使用できません")
    
    try:
        print("🌿 ✨ 秘伝のスパイスブレンド調合中...")
        selected_spices = select_premium_ingredients()
        
        print("   🎭 各スパイスの香りが調和し、魔法のようなブレンドを創造...")
        
        if delay:
            print(f"   ⏰ スパイスが肉に浸透中... {COOKING_SOUNDS['steam']}")
            time.sleep(GOURMET_PROCESS_DELAYS["seasoning"])
        
        meat.is_seasoned = True
        meat.aroma_level = min(10, meat.aroma_level + 4)
        
        print("   ✅ 完璧な調味完了！")
        print(f"   🌺 {random.choice(AROMAS)}が空気中に舞い踊っています")
        
        return meat
        
    except Exception as e:
        raise GourmetSausageError(f"🚨 スパイスブレンドに失敗: {str(e)}")


def mix_with_love(meat: PremiumMeat, delay: bool = True) -> PremiumMeat:
    """❤️ 愛情を込めた手作業での混合
    
    Args:
        meat: 調味された最高級肉
        delay: 愛情込めた混合時間を再現するかどうか
        
    Returns:
        PremiumMeat: 完璧に混合された肉
        
    Raises:
        GourmetSausageError: 調味が不十分または混合に失敗した場合
    """
    if not meat.is_seasoned:
        raise GourmetSausageError("🚨 スパイスによる調味が完了していません")
    
    try:
        print("🥄 ❤️ 職人の手による愛情溢れる混合作業...")
        print("   🎪 肉とスパイスが織り成す美しいマリアージュを創造中...")
        
        if delay:
            mixing_stages = [
                "🌀 優しく全体を馴染ませています...",
                "🎯 均一な食感を目指して丁寧に混合中...",
                "✨ 最終的な味の調和を完成させています..."
            ]
            
            for stage in mixing_stages:
                print(f"   {stage}")
                time.sleep(GOURMET_PROCESS_DELAYS["mixing"] / len(mixing_stages))
        
        meat.is_mixed = True
        meat.texture_score = min(10, meat.texture_score + 1)
        
        print("   ✅ 完璧な混合完了！")
        print("   🎨 滑らかで均一な美しいミンチが完成しました")
        
        return meat
        
    except Exception as e:
        raise GourmetSausageError(f"🚨 愛情込めた混合に失敗: {str(e)}")


def stuff_natural_casing(meat: PremiumMeat, delay: bool = True) -> str:
    """🌭 天然ケーシングへの丁寧な詰め込み
    
    Args:
        meat: 完璧に混合された肉
        delay: 職人技による詰め込み時間を再現するかどうか
        
    Returns:
        str: 美しく成形された生ソーセージ
        
    Raises:
        GourmetSausageError: 混合が不十分またはケーシング詰めに失敗した場合
    """
    if not meat.is_mixed:
        raise GourmetSausageError("🚨 混合作業が完了していません")
    
    try:
        print("🌭 ✨ 天然ケーシングへの芸術的な詰め込み作業...")
        
        casing_types = [
            "🐷 最高級天然豚腸（薄くて弾力性抜群）",
            "🐑 希少な天然羊腸（繊細で上品な食感）",
            "🌿 コラーゲン天然ケーシング（プルプル食感）"
        ]
        
        selected_casing = random.choice(casing_types)
        print(f"   🎯 本日選択: {selected_casing}")
        
        if delay:
            print("   🎪 職人の技で一つ一つ丁寧に詰め込み中...")
            print(f"   ⏰ 完璧な太さと形状を追求... {COOKING_SOUNDS['bubble']}")
            time.sleep(GOURMET_PROCESS_DELAYS["stuffing"])
        
        print("   ✅ 美しいソーセージの形状完成！")
        print("   🌟 まさに芸術品のような美しい仕上がりです")
        
        return f"🌭 極上生ソーセージ（{selected_casing}使用）"
        
    except Exception as e:
        raise GourmetSausageError(f"🚨 天然ケーシング詰めに失敗: {str(e)}")


def cook_to_perfection(raw_sausage: str, delay: bool = True) -> str:
    """🔥 完璧な調理技術による仕上げ
    
    Args:
        raw_sausage: 美しく成形された生ソーセージ
        delay: 完璧な調理時間を再現するかどうか
        
    Returns:
        str: 完璧に調理された極上ソーセージ
        
    Raises:
        GourmetSausageError: 無効なソーセージまたは調理に失敗した場合
    """
    if "生ソーセージ" not in raw_sausage:
        raise GourmetSausageError("🚨 適切に成形された生ソーセージが必要です")
    
    try:
        method = random.choice(list(GourmetCookingMethod))
        print(f"🔥 ✨ {method.emoji} {method.description}による極上調理開始...")
        print(f"   🎯 調理技法: {method.technique}")
        
        cooking_stages = [
            f"🌡️ 最適温度でゆっくりと加熱中... {COOKING_SOUNDS['sizzle']}",
            f"🎨 美しい焼き色を付けています... {COOKING_SOUNDS['crackle']}",
            f"✨ 最終仕上げで完璧な状態に調整中... {COOKING_SOUNDS['steam']}"
        ]
        
        if delay:
            for stage in cooking_stages:
                print(f"   {stage}")
                time.sleep(GOURMET_PROCESS_DELAYS["cooking"] / len(cooking_stages))
        
        # 🎊 完成時の美味しそうな描写
        completion_descriptions = [
            "🌟 黄金色に輝く完璧な表面",
            "🎯 中はジューシーで外はカリッと",
            "🌺 食欲をそそる香ばしい香り",
            "💎 職人技が光る美しい仕上がり"
        ]
        
        print("   ✅ 完璧な調理完了！")
        print(f"   🎊 {random.choice(completion_descriptions)}が完成しました！")
        
        return f"🏆 極上完成ソーセージ（{method.description}）"
        
    except Exception as e:
        raise GourmetSausageError(f"🚨 完璧な調理に失敗: {str(e)}")


def create_gourmet_sausage(delay: bool = True) -> Optional[str]:
    """🍴 美食家も唸る極上ソーセージ製造プロセス
    
    Args:
        delay: 各工程での職人技の時間を再現するかどうか
        
    Returns:
        Optional[str]: 完成した極上ソーセージ、失敗時はNone
    """
    try:
        print("🎉" + "="*60 + "🎉")
        print("🍴          極上ソーセージ製造工房へようこそ!          🍴")
        print("🎉" + "="*60 + "🎉")
        print()
        
        # 🥩 Step 1: 最高級肉の準備
        print("【Step 1】🥩 最高級肉の選定とミンチ加工")
        premium_meat = grind_premium_meat(delay=delay)
        print()
        
        # 🌿 Step 2: スパイスブレンド
        print("【Step 2】🌿 秘伝のスパイスブレンド")
        seasoned_meat = add_aromatic_spices(premium_meat, delay=delay)
        print()
        
        # ❤️ Step 3: 愛情込めた混合
        print("【Step 3】❤️ 職人の手による愛情混合")
        mixed_meat = mix_with_love(seasoned_meat, delay=delay)
        print()
        
        # 🌭 Step 4: 天然ケーシング詰め
        print("【Step 4】🌭 天然ケーシングへの芸術的詰め込み")
        raw_sausage = stuff_natural_casing(mixed_meat, delay=delay)
        print()
        
        # 🔥 Step 5: 完璧な調理
        print("【Step 5】🔥 完璧な調理技術による仕上げ")
        final_masterpiece = cook_to_perfection(raw_sausage, delay=delay)
        print()
        
        # 🎊 完成の喜び
        print("🎊" + "="*60 + "🎊")
        print(f"🏆 {final_masterpiece} 製造完了！")
        print("🌟 まさに芸術品レベルの極上ソーセージが完成しました！")
        print("🤤 一口食べれば、その美味しさに感動すること間違いなし！")
        print("🎊" + "="*60 + "🎊")
        
        return final_masterpiece
        
    except GourmetSausageError as e:
        print(f"⚠️ 製造工程でエラーが発生: {str(e)}")
        return None
    except KeyboardInterrupt:
        print("\n🛑 製造が中断されました。また美味しいソーセージを作りましょう！")
        return None
    except Exception as e:
        print(f"🚨 予期せぬエラー: {str(e)}")
        return None


if __name__ == "__main__":
    print("🍽️ 美食家のための極上ソーセージ工房 🍽️")
    print("💫 今日も最高の一品をお作りします！")
    print()
    
    result = create_gourmet_sausage()
    
    if result:
        print("\n🥂 本日も素晴らしい一品をお作りいただき、ありがとうございました！")
        print("🍴 ぜひ熱々のうちにお召し上がりください！")
    else:
        print("\n😔 今回は残念でしたが、また挑戦してくださいね！")
