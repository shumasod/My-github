// 節分鬼検知システム v1.3 - Bluetooth対応版
// ライブラリのインクルード
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// バージョン
#define VERSION_MAJOR 1
#define VERSION_MINOR 3

// ピン定義
#define MOTION_PIN 2    // 人感センサー（割込対応ピン）
#define TRIG_PIN 3      // 距離センサー送信
#define ECHO_PIN 4      // 距離センサー受信
#define BUZZER_PIN 5    // ブザー
#define LED_R 9         // LED赤（PWM対応ピン）
#define LED_G 10        // LED緑（PWM対応ピン）
#define LED_B 11        // LED青（PWM対応ピン）
#define BATTERY_PIN A0  // 電池電圧測定
#define BLE_RX 6        // Bluetooth RXピン
#define BLE_TX 7        // Bluetooth TXピン

// 定数定義
#define DISTANCE_THRESHOLD_WARNING 300  // 警戒モード閾値(cm)
#define DISTANCE_THRESHOLD_ALERT 200    // 警報モード閾値(cm)
#define BATTERY_CHECK_INTERVAL 14400000 // 電池チェック間隔(ms) = 4時間
#define VALID_DISTANCE_MAX 400          // 有効な距離の最大値(cm)
#define VALID_DISTANCE_MIN 20           // 有効な距離の最小値(cm)
#define DETECTION_COUNT_THRESHOLD 2     // 警戒モード移行に必要な検知回数
#define MEASUREMENT_INTERVAL 500        // 距離測定間隔(ms)
#define BLE_UPDATE_INTERVAL 1000        // Bluetooth送信間隔(ms)

// システム状態
enum SystemState {
  STANDBY,      // 待機中
  WARNING,      // 警戒モード
  ALERT,        // 警報モード
  LOW_BATTERY   // 電池残量低下
};

// SoftwareSerialインスタンス
SoftwareSerial bleSerial(BLE_RX, BLE_TX);

// グローバル変数
volatile SystemState currentState = STANDBY;
unsigned long lastBatteryCheck = 0;
unsigned long lastMeasurement = 0;
unsigned long lastStateChange = 0;
unsigned long lastBleUpdate = 0;
volatile int motionDetected = 0;
int detectionCount = 0;
float batteryVoltage = 0.0;
float batteryPercentage = 100.0;
float currentDistance = 0.0;
bool deepSleepEnabled = true;
bool systemActive = true;

// 関数プロトタイプ宣言
void setupWatchdog();
void enterSleep();
float measureDistance();
void checkBatteryLevel();
void updateLedState();
void updateBuzzerState();
void handleMotionInterrupt();
void sendBluetoothData();
void processBluetoothCommands();

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

  // Bluetooth初期化
  bleSerial.begin(9600);
  bleSerial.println("AT+NAMESetsubunDetector");  // デバイス名設定
  delay(500);

  // ピンモード設定
  pinMode(MOTION_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  pinMode(BATTERY_PIN, INPUT);
  pinMode(BLE_RX, INPUT);
  pinMode(BLE_TX, OUTPUT);

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
  
  // Bluetoothコマンド処理
  processBluetoothCommands();
  
  // システムがアクティブな場合のみセンサー処理を実行
  if (systemActive) {
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
            currentDistance = distance; // 最新の距離を保存
            
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
          currentDistance = distance; // 最新の距離を保存
          
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
  }
  
  // Bluetoothデータ送信（1秒間隔）
  if (currentMillis - lastBleUpdate > BLE_UPDATE_INTERVAL) {
    lastBleUpdate = currentMillis;
    sendBluetoothData();
  }
  
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
  
  // バッテリーパーセンテージ計算（4.5V=100%, 3.6V=0%として線形変換）
  batteryPercentage = constrain(((batteryVoltage - 3.6) / 0.9) * 100.0, 0.0, 100.0);
  
  #ifdef DEBUG_MODE
    Serial.print(F("Battery: "));
    Serial.print(batteryVoltage);
    Serial.print(F("V ("));
    Serial.print(batteryPercentage);
    Serial.println(F("%)"));
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

// Bluetoothデータ送信関数
void sendBluetoothData() {
  // ArduinoJsonオブジェクト（サイズ最適化）
  StaticJsonDocument<128> doc;
  
  // データ設定
  doc["distance"] = currentDistance / 100.0; // cmからmへ変換
  doc["motion"] = (motionDetected > 0 || currentState == WARNING || currentState == ALERT);
  doc["battery"] = batteryPercentage;
  doc["state"] = (int)currentState;
  doc["active"] = systemActive;
  
  // JSONシリアライズとBluetooth送信
  String jsonString;
  serializeJson(doc, jsonString);
  bleSerial.println(jsonString);
}

// Bluetoothコマンド処理関数
void processBluetoothCommands() {
  if (bleSerial.available()) {
    String command = bleSerial.readStringUntil('\n');
    command.trim();
    
    #ifdef DEBUG_MODE
      Serial.print(F("Received command: "));
      Serial.println(command);
    #endif
    
    // コマンド解析
    if (command == "START") {
      systemActive = true;
      #ifdef DEBUG_MODE
        Serial.println(F("System activated"));
      #endif
    } 
    else if (command == "STOP") {
      systemActive = false;
      // システム停止時は全ての出力をオフ
      analogWrite(LED_R, 0);
      analogWrite(LED_G, 0);
      analogWrite(LED_B, 0);
      digitalWrite(BUZZER_PIN, LOW);
      #ifdef DEBUG_MODE
        Serial.println(F("System deactivated"));
      #endif
    }
    else if (command == "STATUS") {
      sendBluetoothData();
    }
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
