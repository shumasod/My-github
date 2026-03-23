<?php
/**
 * PHP 暗黙的nullable型修正ツール
 * 
 * このスクリプトは暗黙的なnullable型の引数を検出し、明示的な型宣言に変換します。
 * PHP 8.1以降の非推奨警告に対応するためのツールです。
 * 
 * 使用方法:
 * php nullable-fixer.php [ディレクトリパス]
 */

// コマンドライン引数の処理
$directory = $argv[1] ?? __DIR__;
if (!is_dir($directory)) {
    die("エラー: 指定されたディレクトリが存在しません: $directory\n");
}

// PHPファイルを再帰的に検索
$files = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator($directory)
);

$phpFiles = [];
foreach ($files as $file) {
    if ($file->isFile() && $file->getExtension() === 'php') {
        $phpFiles[] = $file->getPathname();
    }
}

echo "PHPファイルが" . count($phpFiles) . "個見つかりました\n";

// 問題のある関数を検出して修正
$fixedFiles = 0;
$totalFunctions = 0;
$fixedFunctions = 0;

foreach ($phpFiles as $phpFile) {
    $content = file_get_contents($phpFile);
    $modified = false;
    
    // トークン解析を行う
    $tokens = token_get_all($content);
    $newContent = '';
    $inFunction = false;
    $functionStart = 0;
    $openParenthesis = 0;
    $closeParenthesis = 0;
    $typedParams = [];
    $nullDefaults = [];
    
    // 関数定義を検出
    for ($i = 0; $i < count($tokens); $i++) {
        $token = $tokens[$i];
        
        // トークンが配列の場合（トークン種別と値がある）
        if (is_array($token)) {
            $tokenType = $token[0];
            $tokenValue = $token[1];
            
            // 関数定義の開始を検出
            if ($tokenType === T_FUNCTION) {
                $inFunction = true;
                $functionStart = $i;
                $openParenthesis = 0;
                $closeParenthesis = 0;
                $typedParams = [];
                $nullDefaults = [];
            }
            
            // 型宣言を検出
            if ($inFunction && $openParenthesis > 0 && $closeParenthesis === 0) {
                if ($tokenType === T_STRING || $tokenType === T_ARRAY || 
                    $tokenType === T_CALLABLE || $tokenType === T_NAMESPACE || 
                    $tokenType === T_NS_SEPARATOR) {
                    
                    // パラメータの型を記録
                    $paramName = '';
                    $paramType = $tokenValue;
                    
                    // 次のトークンがパラメータ名を含むか確認
                    for ($j = $i + 1; $j < count($tokens); $j++) {
                        if (is_array($tokens[$j]) && $tokens[$j][0] === T_VARIABLE) {
                            $paramName = $tokens[$j][1];
                            break;
                        }
                    }
                    
                    if ($paramName !== '') {
                        $typedParams[$paramName] = $paramType;
                    }
                }
            }
            
            // デフォルト値nullを検出
            if ($inFunction && $openParenthesis > 0 && $closeParenthesis === 0 && 
                $tokenType === T_VARIABLE) {
                $paramName = $tokenValue;
                
                // 次のトークンが =, NULL かどうか調べる
                $foundEquals = false;
                $foundNull = false;
                
                for ($j = $i + 1; $j < count($tokens) && !($tokens[$j] === ',' || $tokens[$j] === ')'); $j++) {
                    if ($tokens[$j] === '=') {
                        $foundEquals = true;
                    } elseif (is_array($tokens[$j]) && ($tokens[$j][0] === T_STRING && strtolower($tokens[$j][1]) === 'null')) {
                        $foundNull = true;
                    }
                }
                
                if ($foundEquals && $foundNull && isset($typedParams[$paramName])) {
                    $nullDefaults[$paramName] = $typedParams[$paramName];
                }
            }
        } else {
            // 文字列トークン
            if ($inFunction) {
                if ($token === '(') {
                    $openParenthesis++;
                } elseif ($token === ')') {
                    $closeParenthesis++;
                    
                    // 関数定義の終了
                    if ($openParenthesis === $closeParenthesis) {
                        $inFunction = false;
                        
                        // 暗黙的なnullable型を検出
                        if (!empty($nullDefaults)) {
                            $totalFunctions++;
                            
                            // 関数定義を修正
                            $functionContent = '';
                            for ($j = $functionStart; $j <= $i; $j++) {
                                if (is_array($tokens[$j])) {
                                    $tokenValue = $tokens[$j][1];
                                    $tokenType = $tokens[$j][0];
                                    
                                    // 型宣言を修正
                                    if ($tokenType === T_STRING || $tokenType === T_ARRAY || 
                                        $tokenType === T_CALLABLE || $tokenType === T_NS_SEPARATOR) {
                                        
                                        // 次のトークンがパラメータ名を含むか確認
                                        $nextVarIdx = -1;
                                        for ($k = $j + 1; $k < count($tokens); $k++) {
                                            if (is_array($tokens[$k]) && $tokens[$k][0] === T_VARIABLE) {
                                                $nextVarIdx = $k;
                                                break;
                                            }
                                        }
                                        
                                        if ($nextVarIdx !== -1) {
                                            $paramName = $tokens[$nextVarIdx][1];
                                            
                                            // このパラメータがnullデフォルト値を持っているか確認
                                            if (isset($nullDefaults[$paramName])) {
                                                // 型の前に?を追加
                                                $tokenValue = '?' . $tokenValue;
                                                $fixedFunctions++;
                                                $modified = true;
                                            }
                                        }
                                    }
                                    
                                    $functionContent .= $tokenValue;
                                } else {
                                    $functionContent .= $token;
                                }
                            }
                            
                            $newContent .= $functionContent;
                            continue;
                        }
                    }
                }
            }
        }
        
        // トークンを新しいコンテンツに追加
        if (is_array($token)) {
            $newContent .= $token[1];
        } else {
            $newContent .= $token;
        }
    }
    
    // ファイルを修正
    if ($modified) {
        file_put_contents($phpFile, $newContent);
        echo "修正: $phpFile\n";
        $fixedFiles++;
    }
}

echo "処理完了:\n";
echo "- $fixedFiles 個のファイルを修正しました\n";
echo "- $totalFunctions 個の関数を検査しました\n";
echo "- $fixedFunctions 個の暗黙的nullable型を修正しました\n";

// サンプル使用方法の表示
echo "\n使用例：\n";
echo "```php\n";
echo "// 変更前\n";
echo "public function regist(array \$inputs, array \$cost_info, RpsettleResultDto \$result_payment = null)\n";
echo "\n";
echo "// 変更後\n";
echo "public function regist(array \$inputs, array \$cost_info, ?RpsettleResultDto \$result_payment = null)\n";
echo "```\n";
