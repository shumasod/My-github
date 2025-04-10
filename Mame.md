# 節分鬼検知システム仕様書 v1.2
---
**更新履歴**  
v1.2 (2025-04-10): ハードウェア構成の最適化、センサー仕様の調整、コード実装の改善  
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
| Arduino Nano (互換品) | CH340チップ搭載 | メイン制御 | 700円 |
| PIRセンサー | HC-SR501 | 動体検知 | 250円 |
| 超音波センサー | HC-SR04 | 距離計測 | 250円 |
| フルカラーLED | 5mm共通カソード | 状態表示 | 100円 |
| 圧電ブザー | 自己発振型 | 警告音 | 100円 |
| 昇圧型レギュレータ | LM2937-5.0 | 電圧安定化 | 200円 |
| 抵抗セット | 1kΩ、10kΩ各2個 | 電圧調整用 | 100円 |
| ミニブレッドボード | 170点用 | 回路作成 | 250円 |
| ジャンパーワイヤー | オス-オス15本 | 配線用 | 150円 |
| 電池ボックス | 単三×3本用 | 電源供給 | 150円 |
| コンデンサ | 100μF, 100nF各1個 | ノイズ対策 | 100円 |
| スイッチ | スライドスイッチ | 電源ON/OFF | 100円 |
| プラスチックケース | 100×70×30mm | 収納用 | 300円 |
| **合計** | | | **2,750円** |

### センサー仕様
- PIRセンサー（HC-SR501）
  - 検知距離：最大5m（実用域3m）
  - 検知角度：110度
  - 遅延調整：2〜10秒に設定（誤検知防止）
  - 感度調整：中感度（約3〜5m）に設定

- 超音波センサー（HC-SR04）
  - 実用計測距離：20cm〜200cm
  - 測定間隔：最低500ms（連続測定による誤動作防止）
  - 計測回数：3回の平均値を採用

## 3. 機能仕様
### 検知機能
- 二段階検知ロジック
  - 第一段階：PIRセンサーによる動体検知
  - 第二段階：超音波センサーによる距離確認
  - 確認ロジック：2回以上の連続検知で警戒モード、距離200cm以内で警報モード

### アラート機能
- LED表示パターン
  - 緑色点灯：待機中（3秒間隔で点滅）
  - 黄色点灯：警戒モード（1秒間隔で点滅）
  - 赤色点灯：警報モード（0.5秒間隔で点滅）
  - 青色点灯：電池残量低下警告（5秒間隔で点滅）

- ブザーパターン
  - 警戒モード：1000ms間隔でビープ音（省電力化）
  - 警報モード：500ms間隔で連続音
  - 電池警告：5000ms間隔で短いビープ音

### 電源管理
- 電源仕様
  - 入力：単三電池×3本（4.5V）
  - レギュレータによる安定化
  - 最低動作電圧：3.6V
  - 省電力モード時消費電流：約2mA
  - 通常動作時消費電流：約15mA
  - 警報時消費電流：約30mA

- 電池管理
  - 電圧監視（起動時および4時間間隔）
  - 3.8V以下で警告開始
  - 3.6V以下で緊急モード（LEDのみ動作）

## 4. 実装コード

```cpp
// ライブラリのインクルード
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

// バージョン
#define VERSION_MAJOR 1
#define VERSION_MINOR 2

// ピン定義
#define MOTION_PIN 2    // 人感センサー（割込対応ピン）
#define TRIG_PIN 3      // 距離センサー送信
#define ECHO_PIN 4      // 距離センサー受信
#define BUZZER_PIN 5    // ブザー
#define LED_R 9         // LED赤（PWM対応ピン）
#define LED_G 10        // LED緑（PWM対応ピン）
#define LED_B 11        // LED青（PWM対応ピン）
#define BATTERY_PIN A0  // 電池電圧測定

// 定数定義
#define DISTANCE_THRESHOLD_WARNING 300  // 警戒モード閾値(cm)
#define DISTANCE_THRESHOLD_ALERT 200    // 警報モード閾値(cm)
#define BATTERY_CHECK_INTERVAL 14400000 // 電池チェック間隔(ms) = 4時間
#define VALID_DISTANCE_MAX 400          // 有効な距離の最大値(cm)
#define VALID_DISTANCE_MIN 20           // 有効な距離の最小値(cm)
#define DETECTION_COUNT_THRESHOLD 2     // 警戒モード移行に必要な検知回数
#define MEASUREMENT_INTERVAL 500        // 距離測定間隔(ms)

// システム状態
enum SystemState {
  STANDBY,      // 待機中
  WARNING,      // 警戒モード
  ALERT,        // 警報モード
  LOW_BATTERY   // 電池残量低下
};

// グローバル変数
volatile SystemState currentState = STANDBY;
unsigned long lastBatteryCheck = 0;
unsigned long lastMeasurement = 0;
unsigned long lastStateChange = 0;
volatile int motionDetected = 0;
int detectionCount = 0;
float batteryVoltage = 0.0;
bool deepSleepEnabled = true;

// 関数プロトタイプ宣言
void setupWatchdog();
void enterSleep();
float measureDistance();
void checkBatteryLevel();
void updateLedState();
void updateBuzzerState();
void handleMotionInterrupt();

void setup() {
  // シリアル初期化（デバッグ用）
  #ifdef DEBUG_MODE
    Serial.begin(9600);
    Serial.print(F("Setsubun Oni Detection System v"));
    Serial.print(VERSION_MAJOR);
    Serial.print(F("."));
    Serial.println(VERSION_MINOR);
    deepSleepEnabled = false; // デバッグモードではディープスリープ無効
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

  // 初期状態
  digitalWrite(TRIG_PIN, LOW);
  analogWrite(LED_R, 0);
  analogWrite(LED_G, 0);
  analogWrite(LED_B, 0);
  
  // 人感センサー割込設定
  attachInterrupt(digitalPinToInterrupt(MOTION_PIN), handleMotionInterrupt, RISING);
  
  // ウォッチドッグタイマー設定
  setupWatchdog();
  
  // 初回電池チェック
  checkBatteryLevel();
  
  // 起動完了シグナル
  for (int i = 0; i < 3; i++) {
    analogWrite(LED_G, 255);
    delay(100);
    analogWrite(LED_G, 0);
    delay(100);
  }
}

void loop() {
  // 現在時刻取得
  unsigned long currentMillis = millis();
  
  // 電池電圧チェック（4時間間隔）
  if (currentMillis - lastBatteryCheck > BATTERY_CHECK_INTERVAL) {
    checkBatteryLevel();
    lastBatteryCheck = currentMillis;
  }

  // システム状態に応じた処理
  switch (currentState) {
    case STANDBY:
      // 待機モード処理
      if (motionDetected) {
        motionDetected = 0;
        
        // 十分な間隔を空けて距離測定
        if (currentMillis - lastMeasurement > MEASUREMENT_INTERVAL) {
          lastMeasurement = currentMillis;
          
          // 距離測定と判定
          float distance = measureDistance();
          
          #ifdef DEBUG_MODE
            Serial.print(F("Distance: "));
            Serial.print(distance);
            Serial.println(F("cm"));
          #endif
          
          // 有効な測定値の場合
          if (distance > VALID_DISTANCE_MIN && distance < VALID_DISTANCE_MAX) {
            if (distance < DISTANCE_THRESHOLD_WARNING) {
              detectionCount++;
              
              if (detectionCount >= DETECTION_COUNT_THRESHOLD) {
                // 警戒モードへ移行
                currentState = WARNING;
                lastStateChange = currentMillis;
                detectionCount = 0;
                
                #ifdef DEBUG_MODE
                  Serial.println(F("State: WARNING"));
                #endif
              }
            }
          }
        }
      } else {
        // 検知がなければカウントをリセット
        if (detectionCount > 0 && currentMillis - lastMeasurement > 5000) {
          detectionCount = 0;
        }
        
        // 省電力モードへ移行（十分な時間動きがない場合）
        if (deepSleepEnabled && currentMillis - lastMeasurement > 30000) {
          #ifdef DEBUG_MODE
            Serial.println(F("Entering sleep mode..."));
            delay(100); // シリアル出力完了を待つ
          #endif
          
          enterSleep();
        }
      }
      break;
    
    case WARNING:
      // 警戒モード処理
      // 定期的に距離測定
      if (currentMillis - lastMeasurement > MEASUREMENT_INTERVAL) {
        lastMeasurement = currentMillis;
        float distance = measureDistance();
        
        // 警報条件の判定
        if (distance > VALID_DISTANCE_MIN && distance < DISTANCE_THRESHOLD_ALERT) {
          currentState = ALERT;
          lastStateChange = currentMillis;
          
          #ifdef DEBUG_MODE
            Serial.println(F("State: ALERT"));
          #endif
        }
        
        // 一定時間検知がなければ待機モードに戻る
        if (currentMillis - lastStateChange > 10000) {
          currentState = STANDBY;
          detectionCount = 0;
          
          #ifdef DEBUG_MODE
            Serial.println(F("State: STANDBY"));
          #endif
        }
      }
      break;
    
    case ALERT:
      // 警報モード処理
      // 一定時間経過後に警戒モードに戻る
      if (currentMillis - lastStateChange > 30000) {
        currentState = WARNING;
        lastStateChange = currentMillis;
        
        #ifdef DEBUG_MODE
          Serial.println(F("State: WARNING"));
        #endif
      }
      break;
    
    case LOW_BATTERY:
      // 電池残量低下処理
      // 最小限の機能のみ維持
      break;
  }
  
  // LED・ブザー状態更新
  updateLedState();
  updateBuzzerState();
  
  // 省電力化のためのディレイ
  delay(20);
}

// 距離測定関数
float measureDistance() {
  // 超音波送信
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // 超音波受信（タイムアウト付き）
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  
  // 計測不能の場合は-1を返す
  if (duration == 0) {
    return -1;
  }
  
  // 3回計測して平均値を返す（ノイズ低減）
  float total = 0;
  int validCount = 0;
  
  for (int i = 0; i < 3; i++) {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    duration = pulseIn(ECHO_PIN, HIGH, 30000);
    
    if (duration > 0) {
      total += duration * 0.034 / 2;
      validCount++;
    }
    
    delay(10);
  }
  
  // 有効な測定がなければ-1を返す
  if (validCount == 0) {
    return -1;
  }
  
  // 平均値を返す
  return total / validCount;
}

// 電池電圧チェック関数
void checkBatteryLevel() {
  // アナログ参照電圧を内部基準（1.1V）に設定
  analogReference(INTERNAL);
  delay(10); // 参照電圧切替の安定化待ち
  
  // 複数回測定して平均値を取得
  int rawValue = 0;
  for (int i = 0; i < 8; i++) {
    rawValue += analogRead(BATTERY_PIN);
    delay(5);
  }
  rawValue /= 8;
  
  // 電圧計算（電圧分圧回路で実値の1/3を測定する想定）
  batteryVoltage = (rawValue * 1.1 * 3.0) / 1023.0;
  
  #ifdef DEBUG_MODE
    Serial.print(F("Battery: "));
    Serial.print(batteryVoltage);
    Serial.println(F("V"));
  #endif
  
  // 電池残量判定
  if (batteryVoltage < 3.6) {
    currentState = LOW_BATTERY;
  } else if (batteryVoltage >= 4.0 && currentState == LOW_BATTERY) {
    // 電池交換後など、電圧回復時
    currentState = STANDBY;
  }
  
  // 参照電圧を元に戻す
  analogReference(DEFAULT);
  delay(10);
}

// LED状態更新関数
void updateLedState() {
  static unsigned long lastLedUpdate = 0;
  unsigned long currentMillis = millis();
  static bool ledState = false;
  
  // 状態に応じたLEDパターン
  switch (currentState) {
    case STANDBY:
      // 緑色LED点滅（3秒間隔）
      if (currentMillis - lastLedUpdate > 3000) {
        lastLedUpdate = currentMillis;
        ledState = !ledState;
        analogWrite(LED_R, 0);
        analogWrite(LED_G, ledState ? 50 : 0); // 省電力化のため輝度を下げる
        analogWrite(LED_B, 0);
      }
      break;
    
    case WARNING:
      // 黄色LED点滅（1秒間隔）
      if (currentMillis - lastLedUpdate > 1000) {
        lastLedUpdate = currentMillis;
        ledState = !ledState;
        analogWrite(LED_R, ledState ? 100 : 0);
        analogWrite(LED_G, ledState ? 50 : 0);
        analogWrite(LED_B, 0);
      }
      break;
    
    case ALERT:
      // 赤色LED点滅（0.5秒間隔）
      if (currentMillis - lastLedUpdate > 500) {
        lastLedUpdate = currentMillis;
        ledState = !ledState;
        analogWrite(LED_R, ledState ? 255 : 0);
        analogWrite(LED_G, 0);
        analogWrite(LED_B, 0);
      }
      break;
    
    case LOW_BATTERY:
      // 青色LED点滅（5秒間隔）
      if (currentMillis - lastLedUpdate > 5000) {
        lastLedUpdate = currentMillis;
        ledState = !ledState;
        analogWrite(LED_R, 0);
        analogWrite(LED_G, 0);
        analogWrite(LED_B, ledState ? 50 : 0);
      }
      break;
  }
}

// ブザー状態更新関数
void updateBuzzerState() {
  static unsigned long lastBuzzerUpdate = 0;
  unsigned long currentMillis = millis();
  static bool buzzerState = false;
  
  // 状態に応じたブザーパターン
  switch (currentState) {
    case STANDBY:
      // 待機中はブザー無効
      digitalWrite(BUZZER_PIN, LOW);
      break;
    
    case WARNING:
      // 警戒モード（1000ms間隔）
      if (currentMillis - lastBuzzerUpdate > 1000) {
        lastBuzzerUpdate = currentMillis;
        buzzerState = !buzzerState;
        if (buzzerState) {
          // 短いビープ音（100ms）
          digitalWrite(BUZZER_PIN, HIGH);
          delay(100);
          digitalWrite(BUZZER_PIN, LOW);
        }
      }
      break;
    
    case ALERT:
      // 警報モード（500ms間隔）
      if (currentMillis - lastBuzzerUpdate > 500) {
        lastBuzzerUpdate = currentMillis;
        buzzerState = !buzzerState;
        digitalWrite(BUZZER_PIN, buzzerState);
      }
      break;
    
    case LOW_BATTERY:
      // 電池警告（5000ms間隔）
      if (currentMillis - lastBuzzerUpdate > 5000) {
        lastBuzzerUpdate = currentMillis;
        // 短いビープ音（50ms）
        digitalWrite(BUZZER_PIN, HIGH);
        delay(50);
        digitalWrite(BUZZER_PIN, LOW);
      }
      break;
  }
}

// 人感センサー割込ハンドラ
void handleMotionInterrupt() {
  motionDetected = 1;
  
  // スリープ中に割込発生した場合の処理
  // （スリープ解除自体は割込で自動的に行われる）
}

// ウォッチドッグタイマー設定
void setupWatchdog() {
  // ウォッチドッグタイマーの設定
  cli();  // 割込無効化
  wdt_reset();  // タイマーリセット
  
  // ウォッチドッグ変更許可ビット設定
  WDTCSR |= (1 << WDCE) | (1 << WDE);
  
  // ウォッチドッグタイマー設定（8秒）
  WDTCSR = (1 << WDIE) | (1 << WDP3) | (1 << WDP0);
  
  sei();  // 割込有効化
}

// ディープスリープモード移行関数
void enterSleep() {
  // すべての出力を無効化
  analogWrite(LED_R, 0);
  analogWrite(LED_G, 0);
  analogWrite(LED_B, 0);
  digitalWrite(BUZZER_PIN, LOW);
  
  // スリープモード準備
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  
  // 不要な機能を無効化
  power_adc_disable();
  power_timer0_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_twi_disable();
  
  // スリープ実行
  sleep_mode();
  
  // ここからスリープ解除後の処理
  sleep_disable();
  
  // 機能を再有効化
  power_all_enable();
  
  // ADCを再有効化
  ADCSRA |= (1 << ADEN);
}

// ウォッチドッグタイマー割込ハンドラ
ISR(WDT_vect) {
  // ウォッチドッグタイマー割込時の処理
  // 何もしない（ウォッチドッグによるシステムリセット防止）
}
```

## 5. 設置・運用手順
### 組立手順
1. ブレッドボードにArduinoを配置
2. 電源回路の構築
   - 電池ボックスの「+」端子 → スイッチ → 昇圧型レギュレータ入力
   - 昇圧型レギュレータ出力 → Arduino VIN
   - 電池ボックスの「-」端子 → Arduino GND
3. 電圧監視回路の構築
   - 10kΩ抵抗を2つ使った分圧回路（電池電圧の1/3をA0ピンに入力）
4. センサー類の接続
   - PIRセンサー：VCC→5V, GND→GND, OUT→D2
   - 超音波センサー：VCC→5V, GND→GND, TRIG→D3, ECHO→D4
5. LED・ブザーの接続
   - フルカラーLED：R→D9（抵抗経由）, G→D10（抵抗経由）, B→D11（抵抗経由）, GND→GND
   - ブザー：+→D5, -→GND
6. プログラムの書き込み
7. ケースへの収納
   - センサー部分が外部に向くように位置調整
   - ケースに通気孔を確保

### 調整手順
1. PIRセンサーの調整
   - 遅延時間：最小（約2秒）に設定
   - 感度：中程度に設定（3m程度の検知距離）
2. 実動作テスト
   - 歩行テスト：各モードへの移行を確認
   - 電池電圧テスト：低電圧時の動作確認

### トラブルシューティング
- 頻繁な誤動作
  - PIRセンサーの感度を下げる
  - エアコンや窓からの風を避ける設置場所に変更
  - コードの `DETECTION_COUNT_THRESHOLD` を増やす（2→3など）

- 反応が鈍い
  - PIRセンサーの感度を上げる
  - 超音波センサーの向きを調整
  - `DISTANCE_THRESHOLD_ALERT` の値を大きくする

- 電池の消耗が早い
  - LED輝度を下げる（コード内の値を調整）
  - 警報音の間隔を広げる
  - スリープモードが正常に動作しているか確認

## 6. 注意事項・制限事項
### 環境条件
- 動作環境
  - 温度：5-35℃（低温環境ではセンサー感度が低下）
  - 湿度：30-70%（結露なきこと）
  - 室内専用（防水機能なし）
  - 直射日光を避ける（PIRセンサーの誤動作防止）

### 保守・点検
- 定期点検項目
  - 使用前：動作確認、電池電圧
  - 使用後：電源OFF確認
  - 長期保管時：電池取り外し

### 制限事項
- 検知制限
  - 実用検知距離：3m以内
  - 人以外の熱源（暖房機、ペットなど）にも反応する可能性
  - 設置高さ：床から1.2〜1.5m程度が最適
  - 電池寿命：単三アルカリ電池使用時約3ヶ月（スタンバイ状態主体）

## 7. 発展・カスタマイズ案
- 機能拡張案
  - 電子オルゴルによる豆まき音声再生機能
  - スマートフォン連携（Bluetooth通信機能追加）
  - カメラモジュール追加による画像認識機能
  - 複数台連携による広範囲監視

- 省電力化案
  - 更に低消費電力なセンサーへの変更
  - 太陽電池によるバッテリー充電機能
  - 使用状況に応じた省電力モード自動調整
