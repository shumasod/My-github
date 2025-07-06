#!/usr/bin/env python3
"""
ソーセージ製造システム - Cron実行対応版
"""

import argparse
import logging
import random
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


# 定数の定義
PROCESS_DELAYS = {
    "grinding": 2,
    "seasoning": 1,
    "mixing": 3,
    "stuffing": 2,
    "cooking": 3
}

# 終了コード
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INTERRUPTED = 2


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


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """ログ設定を初期化する
    
    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ログファイルのパス（指定しない場合は標準出力）
        
    Returns:
        logging.Logger: 設定されたロガー
    """
    logger = logging.getLogger("sausage_maker")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 既存のハンドラーをクリア
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # フォーマッターを設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ハンドラーを設定
    if log_file:
        # ファイルハンドラー
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def grind_meat(logger: logging.Logger, delay: bool = False) -> Meat:
    """肉をミンチにする処理
    
    Args:
        logger: ロガーインスタンス
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: ミンチ状態の肉オブジェクト
        
    Raises:
        SausageProcessError: 肉のミンチ処理に失敗した場合
    """
    try:
        logger.info("肉をミンチにしています...")
        if delay:
            time.sleep(PROCESS_DELAYS["grinding"])
        logger.debug("肉のミンチ処理が完了しました")
        return Meat(state="ミンチ肉")
    except Exception as e:
        error_msg = f"肉のミンチ処理に失敗: {str(e)}"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)


def add_spices(meat: Meat, logger: logging.Logger, delay: bool = False) -> Meat:
    """調味料を追加する処理
    
    Args:
        meat: 肉オブジェクト
        logger: ロガーインスタンス
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: 調味料が追加された肉オブジェクト
        
    Raises:
        SausageProcessError: 無効な材料または調味料追加に失敗した場合
    """
    if not isinstance(meat, Meat) or meat.state != "ミンチ肉":
        error_msg = "無効な材料が渡されました"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)
    
    spices = ["塩", "コショウ", "ナツメグ", "パプリカ"]
    try:
        logger.info(f"調味料を追加しています: {', '.join(spices)}")
        if delay:
            time.sleep(PROCESS_DELAYS["seasoning"])
        meat.is_seasoned = True
        logger.debug("調味料の追加が完了しました")
        return meat
    except Exception as e:
        error_msg = f"調味料の追加に失敗: {str(e)}"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)


def mix_ingredients(meat: Meat, logger: logging.Logger, delay: bool = False) -> Meat:
    """材料を混ぜ合わせる処理
    
    Args:
        meat: 調味料が追加された肉オブジェクト
        logger: ロガーインスタンス
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        Meat: 混ぜ合わされた肉オブジェクト
        
    Raises:
        SausageProcessError: 調味料が未追加または混合に失敗した場合
    """
    if not meat.is_seasoned:
        error_msg = "調味料が追加されていません"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)
    
    try:
        logger.info(f"{meat.state}をよく混ぜています...")
        if delay:
            time.sleep(PROCESS_DELAYS["mixing"])
        meat.is_mixed = True
        logger.debug("材料の混合が完了しました")
        return meat
    except Exception as e:
        error_msg = f"材料の混合に失敗: {str(e)}"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)


def stuff_casing(meat: Meat, logger: logging.Logger, delay: bool = False) -> str:
    """ケーシングに詰める処理
    
    Args:
        meat: 混ぜ合わされた肉オブジェクト
        logger: ロガーインスタンス
        delay: 処理時間の遅延を有効にするかどうか
        
    Returns:
        str: 生ソーセージの状態
        
    Raises:
        SausageProcessError: 材料が未混合またはケーシング詰めに失敗した場合
    """
    if not meat.is_mixed:
        error_msg = "材料が適切に混ぜられていません"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)
    
    try:
        logger.info("ケーシングに肉を詰めています...")
        if delay:
            time.sleep(PROCESS_DELAYS["stuffing"])
        logger.debug("ケーシング詰めが完了しました")
        return "生ソーセージ"
    except Exception as e:
        error_msg = f"ケーシング詰めに失敗: {str(e)}"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)


def cook_sausage(raw_sausage: str, logger: logging.Logger, delay: bool = False, 
                cooking_method: Optional[str] = None) -> str:
    """ソーセージを調理する処理
    
    Args:
        raw_sausage: 生ソーセージ
        logger: ロガーインスタンス
        delay: 処理時間の遅延を有効にするかどうか
        cooking_method: 指定する調理方法（None の場合はランダム選択）
        
    Returns:
        str: 完成したソーセージ
        
    Raises:
        SausageProcessError: 無効なソーセージまたは調理に失敗した場合
    """
    if raw_sausage != "生ソーセージ":
        error_msg = "無効なソーセージが渡されました"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)
    
    try:
        if cooking_method:
            # 指定された調理方法を使用
            method_enum = None
            for method in CookingMethod:
                if method.value == cooking_method:
                    method_enum = method
                    break
            if not method_enum:
                error_msg = f"無効な調理方法: {cooking_method}"
                logger.error(error_msg)
                raise SausageProcessError(error_msg)
            method = method_enum
        else:
            # ランダムに選択
            method = random.choice(list(CookingMethod))
        
        logger.info(f"ソーセージを{method.value}で調理しています...")
        if delay:
            time.sleep(PROCESS_DELAYS["cooking"])
        logger.debug(f"調理が完了しました（調理方法: {method.value}）")
        return "完成したソーセージ"
    except Exception as e:
        error_msg = f"調理に失敗: {str(e)}"
        logger.error(error_msg)
        raise SausageProcessError(error_msg)


def make_sausage(logger: logging.Logger, delay: bool = False, 
                cooking_method: Optional[str] = None, random_seed: Optional[int] = None) -> Optional[str]:
    """ソーセージを製造する主要プロセス
    
    Args:
        logger: ロガーインスタンス
        delay: 各工程での処理時間遅延を有効にするかどうか
        cooking_method: 指定する調理方法
        random_seed: ランダムシード値
        
    Returns:
        Optional[str]: 完成したソーセージ、失敗時はNone
    """
    try:
        # ランダムシードを設定
        if random_seed is not None:
            random.seed(random_seed)
            logger.debug(f"ランダムシードを設定しました: {random_seed}")
        
        logger.info("ソーセージ製造を開始します")
        
        meat = grind_meat(logger, delay=delay)
        seasoned_meat = add_spices(meat, logger, delay=delay)
        mixed_meat = mix_ingredients(seasoned_meat, logger, delay=delay)
        raw_sausage = stuff_casing(mixed_meat, logger, delay=delay)
        final_sausage = cook_sausage(raw_sausage, logger, delay=delay, 
                                   cooking_method=cooking_method)
        
        logger.info(f"{final_sausage}の製造が完了しました！")
        return final_sausage
        
    except SausageProcessError as e:
        logger.error(f"製造エラー: {str(e)}")
        return None
    except KeyboardInterrupt:
        logger.warning("製造が中断されました")
        return None
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        return None


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="ソーセージ製造システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                          # 基本実行
  %(prog)s --delay                  # 遅延ありで実行
  %(prog)s --log-level DEBUG        # デバッグログ有効
  %(prog)s --log-file sausage.log   # ファイルにログ出力
  %(prog)s --cooking-method 焼く     # 調理方法を指定
  %(prog)s --random-seed 42         # ランダムシード指定
        """
    )
    
    parser.add_argument(
        "--delay", 
        action="store_true",
        help="各工程で遅延を有効にする（デフォルト: 無効）"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="ログレベルを指定（デフォルト: INFO）"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="ログファイルのパス（指定しない場合は標準出力）"
    )
    
    parser.add_argument(
        "--cooking-method",
        choices=["茹でる", "焼く", "蒸す"],
        help="調理方法を指定（指定しない場合はランダム選択）"
    )
    
    parser.add_argument(
        "--random-seed",
        type=int,
        help="ランダムシード値（再現可能な結果を得るため）"
    )
    
    args = parser.parse_args()
    
    # ログ設定
    logger = setup_logging(args.log_level, args.log_file)
    
    try:
        # ソーセージ製造実行
        result = make_sausage(
            logger=logger,
            delay=args.delay,
            cooking_method=args.cooking_method,
            random_seed=args.random_seed
        )
        
        if result:
            logger.info("製造処理が正常に完了しました")
            sys.exit(EXIT_SUCCESS)
        else:
            logger.error("製造処理が失敗しました")
            sys.exit(EXIT_ERROR)
            
    except KeyboardInterrupt:
        logger.warning("処理が中断されました")
        sys.exit(EXIT_INTERRUPTED)
    except Exception as e:
        logger.critical(f"致命的なエラーが発生しました: {str(e)}")
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
