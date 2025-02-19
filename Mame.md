# 節分鬼検知システム仕様書 v1.1
---
**更新履歴**  
v1.1 (2025-02-14): 電源管理、エラーハンドリング、デバッグ機能を追加  
v1.0 (2025-02-14): 初版作成

## 1. システム概要
### 目的
- 節分時に鬼（人）の接近を自動検知
- 視覚・聴覚的なアラート通知
- 手軽に設置・運用可能なシステム構築

### 制約条件
- 予算：1万円以内
- 環境：一般家庭内
- 重視点：手軽さ、簡単な操作性、省電力性

## 2. ハードウェア構成
### 必要機材と概算費用
| 部品名 | 型番 | 用途 | 概算費用 |
|--------|------|------|----------|
| Arduino Nano (互換品) | CH340チップ搭載 | メイン制御 | 800円 |
| PIRセンサー | HC-SR501 | 動体検知 | 300円 |
| 超音波センサー | HC-SR04 | 距離計測 | 300円 |
| RGB LED | WS2812B | 状態表示 | 200円 |
| 圧電ブザー | PSE3525 | 警告音 | 100円 |
| DC-DCコンバータ | MT3608 | 電圧安定化 | 300円 |
| 分圧抵抗 | 10kΩ×2 | 電池電圧測定 | 100円 |
| ブレッドボード | BB-801 | 回路作成 | 300円 |
| ジャンパーワイヤー | 20cm×30本 | 配線用 | 200円 |
| 電池ボックス | 単三×4本用 | 電源供給 | 200円 |
| その他部品 | コンデンサ等 | 各種調整用 | 200円 |
| **合計** | | | **3,000円** |

### センサー仕様
- PIRセンサー（HC-SR501）
  - 検知距離：最大7m
  - 検知角度：110度
  - 遅延調整：0.3〜30秒
  - 感度調整：3〜7m

- 超音波センサー（HC-SR04）
  - 計測距離：2cm〜400cm
  - 精度：±3mm
  - 測定角度：15度
  - 動作電圧：5V

## 3. 機能仕様
### 検知機能
- デュアルセンサーによる誤検知防止ロジック
  - PIRセンサー検知後に距離計測を実行
  - 3回連続で接近を確認した場合のみアラート
  - ノイズフィルタリング処理の実装

### アラート機能
- LED表示パターン
  - 緑色点灯：待機中（1秒間隔で点滅）
  - 黄色点灯：警戒モード（0.5秒間隔で点滅）
  - 赤色点灯：警報モード（0.2秒間隔で点滅）
  - 青色点灯：電池残量低下警告（2秒間隔で点滅）

- ブザーパターン
  - 警戒モード：500ms間隔でビープ音
  - 警報モード：100ms間隔で連続音
  - 電池警告：2000ms間隔で短いビープ音

### 電源管理
- 電源仕様
  - 入力：単三電池×4本（6V）
  - DC-DCコンバータによる5V安定化
  - 動作電圧範囲：4.5V〜7V
  - 省電力モード時消費電流：約5mA
  - 通常動作時消費電流：約30mA
  - 警報時消費電流：約50mA

- 電池管理
  - 電圧監視（1時間間隔）
  - 4.8V以下で警告開始
  - 4.5V以下で強制スリープモード

## 4. 実装コード

```cpp
// ライブラリのインクルード
#include <avr/sleep.h>
#include <avr/power.h>

// 定数定義
const int VERSION = 11;  // v1.1を表す
const int MOTION_PIN = 2;    // 人感センサー
const int TRIG_PIN = 3;      // 距離センサー送信
const int ECHO_PIN = 4;      // 距離センサー受信
const int BUZZER_PIN = 5;    // ブザー
const int LED_R = 6;         // LED赤
const int LED_G = 7;         // LED緑
const int LED_B = 8;         // LED青
const int BATTERY_PIN = A0;  // 電池電圧測定

// システム状態
enum SystemState {
  STANDBY,
  WARNING,
  ALERT,
  LOW_BATTERY
};

// グローバル変数
SystemState currentState = STANDBY;
unsigned long lastBatteryCheck = 0;
int consecutiveDetections = 0;

void setup() {
  // デバッグモード初期化
  #ifdef DEBUG_MODE
    Serial.begin(9600);
    Serial.println("System Start: v" + String(VERSION));
  #endif

  // ピンモード設定
  pinMode(MOTION_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  pinMode(BATTERY_PIN, INPUT);

  // 省電力設定
  setupPowerSaving();
}

void loop() {
  // 電池電圧チェック（1時間間隔）
  if (millis() - lastBatteryCheck > 3600000) {
    checkBatteryLevel();
    lastBatteryCheck = millis();
  }

  // メインループ処理
  if (currentState != LOW_BATTERY) {
    if (digitalRead(MOTION_PIN) == HIGH) {
      float distance = measureDistance();
      if (distance > 0 && distance < 300) {  // 有効な測定値の場合
        handleDetection(distance);
      }
    } else {
      consecutiveDetections = 0;
      normalMode();
    }
  } else {
    lowBatteryMode();
  }

  // 省電力処理
  if (currentState == STANDBY) {
    enterSleepMode();
  }

  delay(50);  // 最小限の遅延
}

float measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // タイムアウト付き距離測定
  unsigned long timeout = millis();
  while (digitalRead(ECHO_PIN) == LOW) {
    if (millis() - timeout > 500) {
      #ifdef DEBUG_MODE
        Serial.println("Distance measurement timeout");
      #endif
      return -1;
    }
  }
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30msタイムアウト
  if (duration == 0) {
    return -1;
  }
  return duration * 0.034 / 2;
}

void handleDetection(float distance) {
  #ifdef DEBUG_MODE
    Serial.println("Distance: " + String(distance) + "cm");
  #endif

  if (distance < 150) {
    consecutiveDetections++;
    if (consecutiveDetections >= 3) {
      alertMode();
    } else {
      warningMode();
    }
  }
}

void checkBatteryLevel() {
  float voltage = (analogRead(BATTERY_PIN) * 5.0 * 2) / 1024.0;  // 分圧を考慮
  #ifdef DEBUG_MODE
    Serial.println("Battery: " + String(voltage) + "V");
  #endif

  if (voltage < 4.5) {
    currentState = LOW_BATTERY;
  }
}

void setupPowerSaving() {
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  power_adc_disable();
  power_spi_disable();
}

// 以下、各モード処理の実装
```

## 5. 設置・運用手順
### 組立手順
1. ブレッドボードにArduinoを配置
2. DC-DCコンバータの接続と電圧調整
3. センサー類の接続とピン配置確認
4. LED・ブザーの接続
5. 電池ボックスの接続
6. 電圧測定回路の構築
7. プログラムの書き込みと動作確認

### キャリブレーション手順
1. 電源投入後、LEDが緑点滅するまで待機
2. PIRセンサーの感度調整（左に回すと鈍感に）
3. テスト歩行による検知範囲確認
4. 必要に応じてセンサー角度を調整

### トラブルシューティング
- LED点灯なし
  - 電池電圧確認
  - DC-DCコンバータ出力確認
  - 配線確認

- 誤検知が多い
  - PIRセンサー感度を下げる
  - センサー前面の清掃
  - 設置場所の見直し

- 反応しない
  - 電池交換
  - センサー角度調整
  - プログラム再書き込み

## 6. 注意事項・制限事項
### 環境条件
- 動作環境
  - 温度：0-40℃
  - 湿度：20-80%（結露なきこと）
  - 照度：蛍光灯下で問題なし
  - 室内専用（防水機能なし）

### 保守・点検
- 定期点検項目
  - 週1回：動作確認
  - 月1回：電池電圧確認
  - 3ヶ月：センサー清掃
  - 6ヶ月：接続部確認

### 制限事項
- 検知制限
  - 最大検知距離：3m（確実な検知）
  - センサー検知角度：約110度
  - 連続警報時間：最大10分
  - 電池寿命：約2ヶ月（標準使用時）

