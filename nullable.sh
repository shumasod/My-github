#!/bin/bash
# PHPファイル内の暗黙的nullable型を一行コマンドで修正するスクリプト

# 使用例:
# ./fix-nullable.sh /path/to/your/php/project

PROJECT_DIR=${1:-'.'}

echo "PHPファイル内の暗黙的nullable型パラメータを検索・修正します..."
echo "対象ディレクトリ: $PROJECT_DIR"

# 正規表現を使用して暗黙的nullable型を検出し、修正する
find "$PROJECT_DIR" -name "*.php" -type f | while read -r file; do
  # バックアップファイル作成
  cp "$file" "${file}.bak"
  
  # 型パラメータ修正（function xxx(Type $param = null) → function xxx(?Type $param = null)）
  perl -pe 's/(\bfunction\s+[\w_]+\s*\([^)]*?)(\b(?!(?:\?|string|int|float|bool|array|callable|iterable|object|self|parent|mixed)\b)[A-Za-z_\\]+(?:\[\])?)\s+(\$\w+\s*=\s*null)/$1?$2 $3/g' "${file}.bak" > "$file"
  
  # 変更があったか確認
  if cmp -s "$file" "${file}.bak"; then
    # 変更がなければバックアップ削除
    rm "${file}.bak"
  else
    echo "修正: $file"
  fi
done

echo "処理が完了しました。"
echo "修正例: function example(Type \$param = null) → function example(?Type \$param = null)"
