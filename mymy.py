#!/usr/bin/env python3
"""
ソーセージ製造システム - Cron実行対応版
""
       


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



