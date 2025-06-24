/*
 * 節分人物検知システム
 * 非接触型動態検知システムの実装
 * 
 * 対応ハードウェア: Arduino Nano 33 IoT
 * センサー: PIR×2, MLX90614, HC-SR04, WS2812B LED×4
 */

#include <WiFiNINA.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_NeoPixel.h>

// ピン定義
#define PIR1_PIN 2          // PIRセンサー1 (左側)
#define PIR2_PIN 3          // PIRセンサー2 (右側)
#define TRIG_PIN 4          // 超音波センサー トリガー
#define ECHO_PIN 5          // 超音波センサー エコー
#define LED_PIN 6           // WS2812B LED
#define SPEAKER_PIN 7       // 圧電スピーカー
#define POWER_LED_PIN 8     // 電源表示LED

// システム定数
#define LED_COUNT 4
#define TEMP_THRESHOLD 5.0  // 温度閾値 (°C)
#define DISTANCE_THRESHOLD 10  // 距離変化閾値 (cm)
#define DETECTION_THRESHOLD 4  // 検知スコア閾値
#define SAMPLING_INTERVAL 200  // サンプリング間隔 (ms)
#define ALERT_DURATION 3000    // アラート継続時間 (ms)

// センサーオブジェクト
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// システム状態
enum SystemState {
  STANDBY,
  MONITORING,
  ALERT
};

// グローバル変数
SystemState currentState = STANDBY;
unsigned long lastSampleTime = 0;
unsigned long alertStartTime = 0;
float previousDistance = 0;
float ambientTemp = 0;
bool pirCalibrated = false;
unsigned long calibrationStartTime = 0;

// 検知統計
struct DetectionStats {
  unsigned long totalDetections = 0;
  unsigned long falsePositives = 0;
  unsigned long lastDetectionTime = 0;
  float averageReactionTime = 0;
};

DetectionStats stats;

// センサーデータ構造体
struct SensorData {
  bool pir1_triggered;
  bool pir2_triggered;
  float objectTemp;
  float ambientTemp;
  float distance;
  unsigned long timestamp;
};

void setup() {
  Serial.begin(115200);
  
  // ピン初期化
  pinMode(PIR1_PIN, INPUT);
  pinMode(PIR2_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(SPEAKER_PIN, OUTPUT);
  pinMode(POWER_LED_PIN, OUTPUT);
  
  // LED初期化
  strip.begin();
  strip.show();
  digitalWrite(POWER_LED_PIN, HIGH);
  
  // I2Cセンサー初期化
  Wire.begin();
  if (!mlx.begin()) {
    Serial.println("MLX90614センサーの初期化に失敗しました");
    errorBlink();
    while(1);
  }
  
  // 初期キャリブレーション
  Serial.println("システム初期化中...");
  calibrateSystem();
  
  Serial.println("節分人物検知システム開始");
  Serial.println("検知範囲: 3m以内");
  
  // 起動完了を示すLED点灯
  startupSequence();
}

void loop() {
  unsigned long currentTime = millis();
  
  // サンプリング間隔チェック
  if (currentTime - lastSampleTime >= SAMPLING_INTERVAL) {
    lastSampleTime = currentTime;
    
    // センサーデータ取得
    SensorData data = readSensors();
    
    // 検知処理
    processDetection(data);
    
    // 状態管理
    updateSystemState(currentTime);
    
    // LED更新
    updateLEDs();
    
    // デバッグ出力
    if (Serial.available()) {
      printDebugInfo(data);
    }
  }
  
  delay(10); // CPU負荷軽減
}

// システムキャリブレーション
void calibrateSystem() {
  Serial.println("PIRセンサーキャリブレーション中 (30秒)...");
  
  // 環境温度測定
  float tempSum = 0;
  for (int i = 0; i < 10; i++) {
    tempSum += mlx.readAmbientTempC();
    delay(100);
  }
  ambientTemp = tempSum / 10.0;
  
  Serial.print("環境温度: ");
  Serial.print(ambientTemp);
  Serial.println("°C");
  
  // PIRセンサー安定化待機
  calibrationStartTime = millis();
  while (millis() - calibrationStartTime < 30000) {
    // キャリブレーション中のLED表示
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, strip.Color(0, 0, 255)); // 青色
    }
    strip.show();
    delay(500);
    
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, strip.Color(0, 0, 0)); // 消灯
    }
    strip.show();
    delay(500);
  }
  
  pirCalibrated = true;
  Serial.println("キャリブレーション完了");
}

// センサーデータ読み取り
SensorData readSensors() {
  SensorData data;
  data.timestamp = millis();
  
  // PIRセンサー読み取り
  data.pir1_triggered = digitalRead(PIR1_PIN);
  data.pir2_triggered = digitalRead(PIR2_PIN);
  
  // 温度センサー読み取り
  data.objectTemp = mlx.readObjectTempC();
  data.ambientTemp = mlx.readAmbientTempC();
  
  // 超音波センサー読み取り
  data.distance = readUltrasonicDistance();
  
  return data;
}

// 超音波距離測定
float readUltrasonicDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30msタイムアウト
  if (duration == 0) return -1; // タイムアウト
  
  float distance = (duration * 0.034) / 2; // cm単位
  return distance;
}

// 検知処理
void processDetection(SensorData data) {
  if (!pirCalibrated) return;
  
  int detectionScore = 0;
  String detectionDetails = "";
  
  // PIRセンサー評価 (重み: 3)
  if (data.pir1_triggered || data.pir2_triggered) {
    detectionScore += 3;
    detectionDetails += "PIR:ON ";
    
    // 方向推定
    if (data.pir1_triggered && !data.pir2_triggered) {
      detectionDetails += "(LEFT) ";
    } else if (!data.pir1_triggered && data.pir2_triggered) {
      detectionDetails += "(RIGHT) ";
    } else if (data.pir1_triggered && data.pir2_triggered) {
      detectionDetails += "(CENTER) ";
    }
  }
  
  // 温度センサー評価 (重み: 2)
  if (data.objectTemp > data.ambientTemp + TEMP_THRESHOLD) {
    detectionScore += 2;
    detectionDetails += "TEMP:HIGH ";
  }
  
  // 超音波センサー評価 (重み: 1)
  if (data.distance > 0 && previousDistance > 0) {
    float distanceChange = abs(data.distance - previousDistance);
    if (distanceChange > DISTANCE_THRESHOLD) {
      detectionScore += 1;
      detectionDetails += "MOVE:ON ";
    }
  }
  previousDistance = data.distance;
  
  // 検知判定
  if (detectionScore >= DETECTION_THRESHOLD) {
    triggerDetection(detectionScore, detectionDetails);
  }
}

// 検知トリガー
void triggerDetection(int score, String details) {
  if (currentState != ALERT) {
    Serial.println("=== 人物検知 ===");
    Serial.print("スコア: ");
    Serial.print(score);
    Serial.print("/6, 詳細: ");
    Serial.println(details);
    
    currentState = ALERT;
    alertStartTime = millis();
    stats.totalDetections++;
    stats.lastDetectionTime = millis();
    
    // 鬼来訪アラート
    playOniAlert();
  }
}

// システム状態更新
void updateSystemState(unsigned long currentTime) {
  switch (currentState) {
    case STANDBY:
      if (pirCalibrated) {
        currentState = MONITORING;
      }
      break;
      
    case MONITORING:
      // 通常の監視状態
      break;
      
    case ALERT:
      if (currentTime - alertStartTime >= ALERT_DURATION) {
        currentState = MONITORING;
        Serial.println("アラート終了 - 監視状態に復帰");
      }
      break;
  }
}

// LED表示更新
void updateLEDs() {
  switch (currentState) {
    case STANDBY:
      // 青色点滅 (キャリブレーション中)
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 100));
      }
      break;
      
    case MONITORING:
      // 緑色微光 (監視中)
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 20, 0));
      }
      break;
      
    case ALERT:
      // 赤色点滅 (検知中)
      int brightness = (millis() / 100) % 2 ? 255 : 0;
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(brightness, 0, 0));
      }
      break;
  }
  strip.show();
}

// 鬼来訪アラート音
void playOniAlert() {
  // 不気味なメロディー (鬼のテーマ)
  int melody[] = {
    262, 247, 220, 196, 175, 196, 220, 247, 262
  };
  int noteDurations[] = {
    200, 200, 200, 200, 400, 200, 200, 200, 400
  };
  
  for (int i = 0; i < 9; i++) {
    tone(SPEAKER_PIN, melody[i], noteDurations[i]);
    delay(noteDurations[i] * 1.3);
    noTone(SPEAKER_PIN);
  }
}

// 起動シーケンス
void startupSequence() {
  // 虹色回転
  for (int j = 0; j < 256; j++) {
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, wheel((i * 256 / LED_COUNT + j) & 255));
    }
    strip.show();
    delay(10);
  }
  
  // 全消灯
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
  
  // 起動完了音
  tone(SPEAKER_PIN, 440, 200);
  delay(250);
  tone(SPEAKER_PIN, 554, 200);
  delay(250);
  tone(SPEAKER_PIN, 659, 400);
  delay(500);
  noTone(SPEAKER_PIN);
}

// エラー表示
void errorBlink() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(POWER_LED_PIN, HIGH);
    delay(100);
    digitalWrite(POWER_LED_PIN, LOW);
    delay(100);
  }
}

// 虹色生成関数
uint32_t wheel(byte wheelPos) {
  wheelPos = 255 - wheelPos;
  if (wheelPos < 85) {
    return strip.Color(255 - wheelPos * 3, 0, wheelPos * 3);
  }
  if (wheelPos < 170) {
    wheelPos -= 85;
    return strip.Color(0, wheelPos * 3, 255 - wheelPos * 3);
  }
  wheelPos -= 170;
  return strip.Color(wheelPos * 3, 255 - wheelPos * 3, 0);
}

// デバッグ情報出力
void printDebugInfo(SensorData data) {
  Serial.println("=== センサー状態 ===");
  Serial.print("PIR1: "); Serial.print(data.pir1_triggered ? "ON" : "OFF");
  Serial.print(", PIR2: "); Serial.println(data.pir2_triggered ? "ON" : "OFF");
  Serial.print("物体温度: "); Serial.print(data.objectTemp);
  Serial.print("°C, 環境温度: "); Serial.print(data.ambientTemp); Serial.println("°C");
  Serial.print("距離: "); Serial.print(data.distance); Serial.println("cm");
  Serial.print("状態: ");
  switch (currentState) {
    case STANDBY: Serial.println("待機中"); break;
    case MONITORING: Serial.println("監視中"); break;
    case ALERT: Serial.println("アラート中"); break;
  }
  Serial.print("総検知回数: "); Serial.println(stats.totalDetections);
  Serial.println("==================");
  
  // 入力をクリア
  while (Serial.available()) {
    Serial.read();
  }
}
