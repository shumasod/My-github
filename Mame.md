# 節分鬼検知システム仕様書

## 1. システム概要

### 目的
- 節分時に鬼（人）の接近を自動検知
- 視覚・聴覚的なアラート通知
- 手軽に設置・運用可能なシステム構築

### 制約条件
- 予算：1万円以内
- 環境：一般家庭内
- 重視点：手軽さ、簡単な操作性

## 2. ハードウェア構成

### 必要機材と概算費用
| 部品名 | 用途 | 概算費用 |
|--------|------|----------|
| Arduino Nano (互換品) | メイン制御 | 800円 |
| PIR人感センサー | 動体検知 | 300円 |
| 超音波距離センサー | 距離計測 | 300円 |
| RGB LED | 状態表示 | 200円 |
| 圧電ブザー | 警告音 | 100円 |
| ブレッドボード | 回路作成 | 300円 |
| ジャンパーワイヤー | 配線用 | 200円 |
| 電池ボックス | 電源供給 | 200円 |
| その他部品 | 抵抗等 | 100円 |
| **合計** | | **2,500円** |

## 3. 機能仕様

### 検知機能
- 人感センサーによる動体検知（最大5m）
- 距離センサーによる接近測定（〜3m）
- デュアルセンサーによる誤検知防止

### アラート機能
- LED表示
  - 緑：待機中
  - 黄：警戒モード（接近検知）
  - 赤：警報モード（近接検知）
- ブザー音
  - 警戒モード：短い警告音
  - 警報モード：連続警告音

### 電源管理
- 電池駆動（単三電池×3）
- 想定稼働時間：約1ヶ月
- 電池残量低下警告機能

## 4. 実装コード

```cpp
// 基本設定
const int MOTION_PIN = 2;    // 人感センサー
const int TRIG_PIN = 3;      // 距離センサー送信
const int ECHO_PIN = 4;      // 距離センサー受信
const int BUZZER_PIN = 5;    // ブザー
const int LED_R = 6;         // LED赤
const int LED_G = 7;         // LED緑
const int LED_B = 8;         // LED青

void setup() {
  // ピンモード設定
  pinMode(MOTION_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
}

void loop() {
  // メインループ処理
  if (digitalRead(MOTION_PIN) == HIGH) {
    float distance = measureDistance();
    updateAlert(distance);
  } else {
    normalMode();
  }
  delay(100);
}

float measureDistance() {
  // 距離測定処理
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}
```

## 5. 設置・運用手順

### 組立手順
1. ブレッドボードにArduinoを配置
2. センサー類の接続
3. LED・ブザーの接続
4. 電池ボックスの接続
5. プログラムの書き込み
6. 動作確認

### 設置方法
1. 玄関や部屋の入り口付近を選定
2. 人の動きを検知しやすい高さに配置（推奨：床上1-1.5m）
3. 両面テープまたは粘着フックで固定
4. センサーの向きを調整

### メンテナンス
- 月1回の電池確認・交換
- センサー部分の定期清掃
- 誤検知時の感度調整

## 6. 注意事項・制限事項

### 環境条件
- 室内専用（防水機能なし）
- 動作温度：0-40℃
- 直射日光を避けて設置

### 制限事項
- 検知可能距離：最大3m
- 電池寿命：約1ヶ月
- センサー検知角度：約120度

これらの仕様で、手軽で実用的な節分鬼検知システムが実現可能です。必要に応じて機能の追加や調整が可能です。
