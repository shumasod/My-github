import random
import time
from typing import List, Dict
from dataclasses import dataclass

# 時間の遅延を調整するための定数
PROCESSING_TIME = {
    'select_meat': 1,
    'grind': 2,
    'add_spices': 1,
    'mix': 3,
    'stuff': 2,
    'cook': 3,
    'quality_check': 1,
}

@dataclass
class SausageRecipe:
    """ソーセージのレシピを管理するクラス"""
    meat_types: List[str]
    spices: List[str]
    cooking_method: str
    deliciousness_score: int = 0

class DeliciousSausageMaker:
    """メッチャ旨いソーセージを作るクラス"""
    
    def __init__(self):
        self.meat_options = {
            "豚肉": {"flavor": 8, "texture": 7},
            "牛肉": {"flavor": 9, "texture": 8},
            "鶏肉": {"flavor": 6, "texture": 6},
            "羊肉": {"flavor": 10, "texture": 7},
            "鹿肉": {"flavor": 9, "texture": 9},
        }
        
        self.premium_spices = {
            "塩": {"flavor": 5, "essential": True},
            "黒コショウ": {"flavor": 6, "essential": True},
            "ナツメグ": {"flavor": 7, "essential": False},
            "パプリカ": {"flavor": 6, "essential": False},
            "ローズマリー": {"flavor": 8, "essential": False},
            "セージ": {"flavor": 8, "essential": False},
            "タイム": {"flavor": 7, "essential": False},
            "ガーリック": {"flavor": 9, "essential": False},
            "フェンネル": {"flavor": 8, "essential": False},
            "コリアンダー": {"flavor": 7, "essential": False},
            "赤唐辛子": {"flavor": 8, "essential": False},
            "燻製塩": {"flavor": 10, "essential": False},
        }
        
        self.cooking_methods = {
            "茹でる": {"difficulty": 3, "flavor_bonus": 5},
            "焼く": {"difficulty": 4, "flavor_bonus": 7},
            "蒸す": {"difficulty": 2, "flavor_bonus": 4},
            "燻製": {"difficulty": 8, "flavor_bonus": 12},
            "グリル": {"difficulty": 6, "flavor_bonus": 9},
            "オーブン焼き": {"difficulty": 5, "flavor_bonus": 8},
        }

    def select_premium_meat(self) -> List[str]:
        """プレミアムな肉を選択する"""
        print("🥩 最高級の肉を選んでいます...")
        time.sleep(PROCESSING_TIME['select_meat'])
        
        # ランダムに1-3種類の肉を選択（バランスを考慮）
        selected_meats = random.sample(list(self.meat_options.keys()), 
                                     random.randint(1, 3))
        
        print(f"選択された肉: {', '.join(selected_meats)}")
        return selected_meats

    def grind_meat(self, meat_types: List[str]) -> str:
        """肉をミンチにする処理（改良版）"""
        print("🔪 肉を最適な粒度でミンチにしています...")
        time.sleep(PROCESSING_TIME['grind'])
        
        # 肉の種類による風味計算
        total_flavor = sum(self.meat_options[meat]["flavor"] for meat in meat_types)
        total_texture = sum(self.meat_options[meat]["texture"] for meat in meat_types)
        
        print(f"ミンチ完了！風味レベル: {total_flavor}, 食感レベル: {total_texture}")
        return f"プレミアムミンチ肉（{'+'.join(meat_types)}）"

    def add_premium_spices(self, minced_meat: str) -> tuple[str, int]:
        """プレミアムスパイスを追加する処理"""
        print("🌿 秘伝のスパイスブレンドを準備しています...")
        time.sleep(PROCESSING_TIME['add_spices'])
        
        # 必須スパイスを追加
        selected_spices = [spice for spice, info in self.premium_spices.items() 
                          if info["essential"]]
        
        # オプショナルスパイスをランダムに3-5種類追加
        optional_spices = [spice for spice, info in self.premium_spices.items() 
                          if not info["essential"]]
        selected_spices.extend(random.sample(optional_spices, random.randint(3, 5)))
        
        # スパイスの風味スコア計算
        spice_score = sum(self.premium_spices[spice]["flavor"] for spice in selected_spices)
        
        print(f"追加されたスパイス: {', '.join(selected_spices)}")
        print(f"スパイス風味スコア: {spice_score}")
        
        return f"スパイス入り{minced_meat}", spice_score

    def mix_ingredients(self, seasoned_meat: str) -> str:
        """調味料を加えた肉をよく混ぜる処理（改良版）"""
        print("🥄 プロの技術で完璧に混ぜています...")
        time.sleep(PROCESSING_TIME['mix'])
        
        mixing_techniques = [
            "手で優しく混ぜる伝統技法",
            "スタンドミキサーで均一に混合",
            "職人の手技による完璧な混合"
        ]
        
        technique = random.choice(mixing_techniques)
        print(f"使用技法: {technique}")
        
        return f"完璧に混ぜられた{seasoned_meat}"

    def stuff_casing(self, mixed_meat: str) -> str:
        """肉をケーシングに詰める処理（改良版）"""
        print("🌭 天然ケーシングに丁寧に詰めています...")
        time.sleep(PROCESSING_TIME['stuff'])
        
        casing_types = ["天然豚腸", "天然羊腸", "コラーゲンケーシング"]
        selected_casing = random.choice(casing_types)
        
        print(f"使用ケーシング: {selected_casing}")
        return f"生ソーセージ（{selected_casing}使用）"

    def cook_sausage(self, raw_sausage: str) -> tuple[str, int]:
        """ソーセージを調理する処理（改良版）"""
        method = random.choice(list(self.cooking_methods.keys()))
        method_info = self.cooking_methods[method]
        
        print(f"🔥 {method}で調理しています...")
        print(f"調理難易度: {method_info['difficulty']}/10")
        
        # 調理の成功度をランダムに決定（難易度が高いほど失敗の可能性あり）
        success_rate = max(0.7, 1.0 - (method_info['difficulty'] / 20))
        cooking_success = random.random() < success_rate
        
        if cooking_success:
            print("✅ 調理成功！完璧な仕上がりです！")
            flavor_bonus = method_info['flavor_bonus']
        else:
            print("⚠️ 調理は成功しましたが、少し焦げました...")
            flavor_bonus = method_info['flavor_bonus'] // 2
        
        time.sleep(PROCESSING_TIME['cook'])
        return f"完成したソーセージ（{method}）", flavor_bonus

    def quality_check(self, sausage: str, total_score: int) -> str:
        """品質チェックを行う"""
        print("🔍 品質チェックを実施しています...")
        time.sleep(PROCESSING_TIME['quality_check'])
        
        if total_score >= 80:
            grade = "🌟 メッチャ旨い！（SSS級）"
        elif total_score >= 60:
            grade = "😋 とても美味しい（S級）"
        elif total_score >= 40:
            grade = "😊 美味しい（A級）"
        else:
            grade = "🤔 普通（B級）"
        
        print(f"最終スコア: {total_score}点")
        print(f"品質グレード: {grade}")
        
        return f"{sausage} - {grade}"

    def make_delicious_sausage(self) -> None:
        """メッチャ旨いソーセージを作る全体の処理"""
        try:
            print("🎉 メッチャ旨いソーセージ製造開始！")
            print("=" * 50)
            
            # 各工程の実行
            meat_types = self.select_premium_meat()
            minced_meat = self.grind_meat(meat_types)
            seasoned_meat, spice_score = self.add_premium_spices(minced_meat)
            mixed_meat = self.mix_ingredients(seasoned_meat)
            raw_sausage = self.stuff_casing(mixed_meat)
            final_sausage, cooking_bonus = self.cook_sausage(raw_sausage)
            
            # 最終スコア計算
            base_score = sum(self.meat_options[meat]["flavor"] for meat in meat_types)
            total_score = base_score + spice_score + cooking_bonus
            
            # 品質チェック
            graded_sausage = self.quality_check(final_sausage, total_score)
            
            print("=" * 50)
            print(f"🎊 {graded_sausage} の製造が完了しました！")
            
            # 成功時の特別メッセージ
            if total_score >= 80:
                print("👨‍🍳 シェフからのメッセージ: 「この出来栄えは芸術的です！」")
            
        except KeyboardInterrupt:
            print("\n🛑 製造が中断されました。")
            raise
        except Exception as e:
            print(f"❌ ソーセージ製造中にエラーが発生しました: {e}")

def main():
    """メイン関数"""
    print("Welcome to the Delicious Sausage Factory! 🏭")
    print("あなただけのメッチャ旨いソーセージを作りましょう！")
    
    sausage_maker = DeliciousSausageMaker()
    
    while True:
        try:
            sausage_maker.make_delicious_sausage()
            
            # 継続確認
            another = input("\n🔄 もう一度作りますか？ (y/n): ").strip().lower()
            if another not in ['y', 'yes', 'はい']:
                print("🙏 ご利用ありがとうございました！")
                break
                
        except KeyboardInterrupt:
            print("\n👋 さようなら！")
            break

if __name__ == "__main__":
    main()
