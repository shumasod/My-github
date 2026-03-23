/*
 * 節分人物検知システム (改善版)
 * 非接触型動態検知システム + 外部監視対応
 * 
 * 対応ハードウェア: Arduino Nano 33 IoT
 * センサー: PIR×2, MLX90614, HC-SR04, WS2812B LED×4
 * 
 * 改善点:
 * - 設定可能なパラメータ
 * - エラーハンドリング強化
 * - 構造化された出力
 * - ウォッチドッグタイマー対応
 * - メモリ使用量最適化
 */

#include <WiFiNINA.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// バージョン情報
#define FIRMWARE_VERSION "2.1.0"
#define BUILD_DATE __DATE__ " " __TIME__

// ピン定義
#define PIR1_PIN 2          // PIRセンサー1 (左側)
#define PIR2_PIN 3          // PIRセンサー2 (右側)
#define TRIG_PIN 4          // 超音波センサー トリガー
#define ECHO_PIN 5          // 超音波センサー エコー
#define LED_PIN 6           // WS2812B LED
#define SPEAKER_PIN 7       // 圧電スピーカー
#define POWER_LED_PIN 8     // 電源表示LED
#define RESET_PIN 9         // リセットボタン (オプション)

// システム定数 (設定可能)
#define LED_COUNT 4
#define DEFAULT_TEMP_THRESHOLD 5.0
#define DEFAULT_DISTANCE_THRESHOLD 10
#define DEFAULT_DETECTION_THRESHOLD 4
#define DEFAULT_SAMPLING_INTERVAL 200
#define DEFAULT_ALERT_DURATION 3000
#define CALIBRATION_TIME 30000
#define WATCHDOG_TIMEOUT 30000
#define MAX_SERIAL_BUFFER 256
#define JSON_BUFFER_SIZE 512

// エラーコード
enum ErrorCode {
  ERROR_NONE = 0,
  ERROR_SENSOR_INIT = 1,
  ERROR_CALIBRATION = 2,
  ERROR_SENSOR_READ = 3,
  ERROR_MEMORY = 4,
  ERROR_COMMUNICATION = 5
};

// システム設定構造体
struct SystemConfig {
  float tempThreshold = DEFAULT_TEMP_THRESHOLD;
  float distanceThreshold = DEFAULT_DISTANCE_THRESHOLD;
  int detectionThreshold = DEFAULT_DETECTION_THRESHOLD;
  unsigned long samplingInterval = DEFAULT_SAMPLING_INTERVAL;
  unsigned long alertDuration = DEFAULT_ALERT_DURATION;
  bool enableSound = true;
  bool enableLEDs = true;
  bool enableJsonOutput = false;
  bool debugMode = false;
};

// センサーオブジェクト
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// システム状態
enum SystemState {
  STANDBY,
  CALIBRATING,
  MONITORING,
  ALERT,
  ERROR_STATE
};

// グローバル変数
SystemConfig config;
SystemState currentState = STANDBY;
ErrorCode lastError = ERROR_NONE;
unsigned long lastSampleTime = 0;
unsigned long alertStartTime = 0;
unsigned long lastWatchdogTime = 0;
unsigned long systemStartTime = 0;
float previousDistance = 0;
float ambientTemp = 0;
bool sensorsInitialized = false;
char serialBuffer[MAX_SERIAL_BUFFER];
int serialBufferIndex = 0;

// 検知統計
struct DetectionStats {
  unsigned long totalDetections = 0;
  unsigned long falsePositives = 0;
  unsigned long lastDetectionTime = 0;
  unsigned long uptime = 0;
  int errorCount = 0;
  float averageDistance = 0;
  float averageObjectTemp = 0;
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
  bool isValid;
};

void setup() {
  Serial.begin(115200);
  
  // システム開始時間記録
  systemStartTime = millis();
  lastWatchdogTime = systemStartTime;
  
  // ピン初期化
  initializePins();
  
  // LED初期化
  if (config.enableLEDs) {
    strip.begin();
    strip.show();
  }
  digitalWrite(POWER_LED_PIN, HIGH);
  
  // センサー初期化
  if (initializeSensors()) {
    sensorsInitialized = true;
    Serial.println(F("=== 節分人物検知システム v" FIRMWARE_VERSION " ==="));
    Serial.println(F("Build: " BUILD_DATE));
    Serial.println(F("初期化完了"));
    
    // キャリブレーション実行
    currentState = CALIBRATING;
    if (calibrateSystem()) {
      currentState = MONITORING;
      Serial.println(F("システム稼働開始"));
    } else {
      setErrorState(ERROR_CALIBRATION);
    }
  } else {
    setErrorState(ERROR_SENSOR_INIT);
  }
  
  // 起動完了シーケンス
  if (currentState == MONITORING) {
    startupSequence();
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  // ウォッチドッグタイマー
  if (currentTime - lastWatchdogTime > WATCHDOG_TIMEOUT) {
    Serial.println(F("WARNING: Watchdog timeout"));
    lastWatchdogTime = currentTime;
  }
  
  // シリアルコマンド処理
  handleSerialCommands();
  
  // メイン処理
  if (sensorsInitialized && currentTime - lastSampleTime >= config.samplingInterval) {
    lastSampleTime = currentTime;
    
    // センサーデータ取得
    SensorData data = readSensors();
    
    if (data.isValid) {
      // 統計更新
      updateStatistics(data);
      
      // 検知処理
      if (currentState == MONITORING) {
        processDetection(data);
      }
      
      // 状態更新
      updateSystemState(currentTime);
      
      // LED更新
      if (config.enableLEDs) {
        updateLEDs();
      }
      
      // ウォッチドッグ更新
      lastWatchdogTime = currentTime;
    }
  }
  
  delay(10); // CPU負荷軽減
}

// ピン初期化
void initializePins() {
  pinMode(PIR1_PIN, INPUT);
  pinMode(PIR2_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(SPEAKER_PIN, OUTPUT);
  pinMode(POWER_LED_PIN, OUTPUT);
  if (RESET_PIN > 0) {
    pinMode(RESET_PIN, INPUT_PULLUP);
  }
}

// センサー初期化
bool initializeSensors() {
  Wire.begin();
  
  if (!mlx.begin()) {
    Serial.println(F("ERROR: MLX90614 initialization failed"));
    return false;
  }
  
  // センサー疎通確認
  float testTemp = mlx.readAmbientTempC();
  if (isnan(testTemp) || testTemp < -40 || testTemp > 85) {
    Serial.println(F("ERROR: MLX90614 sensor test failed"));
    return false;
  }
  
  Serial.println(F("センサー初期化完了"));
  return true;
}

// システムキャリブレーション
bool calibrateSystem() {
  Serial.println(F("キャリブレーション開始..."));
  
  // 環境温度測定
  float tempSum = 0;
  int validReadings = 0;
  
  for (int i = 0; i < 20; i++) {
    float temp = mlx.readAmbientTempC();
    if (!isnan(temp)) {
      tempSum += temp;
      validReadings++;
    }
    delay(100);
  }
  
  if (validReadings < 10) {
    Serial.println(F("ERROR: 環境温度測定失敗"));
    return false;
  }
  
  ambientTemp = tempSum / validReadings;
  Serial.print(F("環境温度: "));
  Serial.print(ambientTemp, 1);
  Serial.println(F("°C"));
  
  // PIRセンサー安定化
  Serial.println(F("PIRセンサー安定化中..."));
  unsigned long calibStart = millis();
  
  while (millis() - calibStart < CALIBRATION_TIME) {
    // キャリブレーション表示
    if (config.enableLEDs) {
      calibrationLEDs(millis() - calibStart, CALIBRATION_TIME);
    }
    
    // 中断チェック
    if (Serial.available()) {
      if (Serial.read() == 'q') {
        Serial.println(F("キャリブレーション中断"));
        return false;
      }
    }
    
    delay(500);
  }
  
  Serial.println(F("キャリブレーション完了"));
  return true;
}

// センサーデータ読み取り
SensorData readSensors() {
  SensorData data;
  data.timestamp = millis();
  data.isValid = true;
  
  // PIRセンサー
  data.pir1_triggered = digitalRead(PIR1_PIN);
  data.pir2_triggered = digitalRead(PIR2_PIN);
  
  // 温度センサー
  data.objectTemp = mlx.readObjectTempC();
  data.ambientTemp = mlx.readAmbientTempC();
  
  // 温度データ検証
  if (isnan(data.objectTemp) || isnan(data.ambientTemp)) {
    data.isValid = false;
    setErrorState(ERROR_SENSOR_READ);
  }
  
  // 超音波センサー
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
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  
  float distance = (duration * 0.034) / 2;
  
  // 有効範囲チェック
  if (distance < 2 || distance > 400) {
    return -1;
  }
  
  return distance;
}

// 検知処理
void processDetection(SensorData data) {
  int detectionScore = 0;
  String detectionDetails = "";
  
  // PIRセンサー評価
  if (data.pir1_triggered || data.pir2_triggered) {
    detectionScore += 3;
    detectionDetails += F("PIR:");
    
    if (data.pir1_triggered && data.pir2_triggered) {
      detectionDetails += F("BOTH ");
    } else if (data.pir1_triggered) {
      detectionDetails += F("LEFT ");
    } else {
      detectionDetails += F("RIGHT ");
    }
  }
  
  // 温度センサー評価
  float tempDiff = data.objectTemp - data.ambientTemp;
  if (tempDiff > config.tempThreshold) {
    detectionScore += 2;
    detectionDetails += F("TEMP:+");
    detectionDetails += String(tempDiff, 1);
    detectionDetails += F("°C ");
  }
  
  // 超音波センサー評価
  if (data.distance > 0 && previousDistance > 0) {
    float distanceChange = abs(data.distance - previousDistance);
    if (distanceChange > config.distanceThreshold) {
      detectionScore += 1;
      detectionDetails += F("MOVE:");
      detectionDetails += String(distanceChange, 1);
      detectionDetails += F("cm ");
    }
  }
  previousDistance = data.distance;
  
  // 検知判定
  if (detectionScore >= config.detectionThreshold) {
    triggerDetection(detectionScore, detectionDetails);
  }
}

// 検知トリガー
void triggerDetection(int score, String details) {
  if (currentState != ALERT) {
    Serial.println(F("=== 人物検知 ==="));
    Serial.print(F("スコア: "));
    Serial.print(score);
    Serial.print(F("/6, 詳細: "));
    Serial.println(details);
    
    currentState = ALERT;
    alertStartTime = millis();
    stats.totalDetections++;
    stats.lastDetectionTime = millis();
    
    // アラート実行
    if (config.enableSound) {
      playOniAlert();
    }
  }
}

// 統計更新
void updateStatistics(SensorData data) {
  stats.uptime = millis() - systemStartTime;
  
  // 移動平均更新 (簡易版)
  static int sampleCount = 0;
  sampleCount++;
  
  if (data.distance > 0) {
    stats.averageDistance = ((stats.averageDistance * (sampleCount - 1)) + data.distance) / sampleCount;
  }
  
  if (!isnan(data.objectTemp)) {
    stats.averageObjectTemp = ((stats.averageObjectTemp * (sampleCount - 1)) + data.objectTemp) / sampleCount;
  }
}

// システム状態更新
void updateSystemState(unsigned long currentTime) {
  switch (currentState) {
    case CALIBRATING:
      // キャリブレーション中は何もしない
      break;
      
    case MONITORING:
      // 通常監視中
      break;
      
    case ALERT:
      if (currentTime - alertStartTime >= config.alertDuration) {
        currentState = MONITORING;
        if (config.debugMode) {
          Serial.println(F("アラート終了"));
        }
      }
      break;
      
    case ERROR_STATE:
      // エラー状態 - 復旧試行
      if (currentTime % 10000 == 0) {
        if (initializeSensors()) {
          currentState = MONITORING;
          Serial.println(F("センサー復旧"));
        }
      }
      break;
  }
}

// LED更新
void updateLEDs() {
  switch (currentState) {
    case STANDBY:
    case CALIBRATING:
      calibrationLEDs(millis() % 2000, 2000);
      break;
      
    case MONITORING:
      // 緑色微光
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 20, 0));
      }
      break;
      
    case ALERT:
      // 赤色点滅
      int brightness = (millis() / 100) % 2 ? 255 : 0;
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(brightness, 0, 0));
      }
      break;
      
    case ERROR_STATE:
      // 黄色点滅
      int errorBright = (millis() / 200) % 2 ? 255 : 0;
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(errorBright, errorBright, 0));
      }
      break;
  }
  strip.show();
}

// キャリブレーション用LED
void calibrationLEDs(unsigned long elapsed, unsigned long total) {
  int progress = map(elapsed, 0, total, 0, LED_COUNT);
  
  for (int i = 0; i < LED_COUNT; i++) {
    if (i <= progress) {
      strip.setPixelColor(i, strip.Color(0, 0, 255)); // 青
    } else {
      strip.setPixelColor(i, strip.Color(0, 0, 0)); // 消灯
    }
  }
  strip.show();
}

// エラー状態設定
void setErrorState(ErrorCode error) {
  currentState = ERROR_STATE;
  lastError = error;
  stats.errorCount++;
  
  Serial.print(F("ERROR CODE: "));
  Serial.println(error);
}

// シリアルコマンド処理
void handleSerialCommands() {
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n' || c == '\r') {
      if (serialBufferIndex > 0) {
        serialBuffer[serialBufferIndex] = '\0';
        processCommand(String(serialBuffer));
        serialBufferIndex = 0;
      } else {
        // 空の入力 - デバッグ情報出力
        printDebugInfo();
      }
    } else if (serialBufferIndex < MAX_SERIAL_BUFFER - 1) {
      serialBuffer[serialBufferIndex++] = c;
    }
  }
}

// コマンド処理
void processCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  
  if (cmd == "status") {
    printSystemStatus();
  } else if (cmd == "config") {
    printConfiguration();
  } else if (cmd == "reset") {
    Serial.println(F("システムリセット..."));
    delay(100);
    // ソフトウェアリセット
    asm volatile ("  jmp 0");
  } else if (cmd.startsWith("set ")) {
    processSetCommand(cmd.substring(4));
  } else if (cmd == "json") {
    config.enableJsonOutput = !config.enableJsonOutput;
    Serial.print(F("JSON出力: "));
    Serial.println(config.enableJsonOutput ? F("ON") : F("OFF"));
  } else if (cmd == "help") {
    printHelp();
  } else {
    Serial.println(F("不明なコマンド (help で使用法表示)"));
  }
}

// Set コマンド処理
void processSetCommand(String params) {
  int spaceIndex = params.indexOf(' ');
  if (spaceIndex == -1) return;
  
  String param = params.substring(0, spaceIndex);
  String value = params.substring(spaceIndex + 1);
  
  if (param == "temp") {
    config.tempThreshold = value.toFloat();
    Serial.print(F("温度閾値: "));
    Serial.println(config.tempThreshold);
  } else if (param == "distance") {
    config.distanceThreshold = value.toFloat();
    Serial.print(F("距離閾値: "));
    Serial.println(config.distanceThreshold);
  } else if (param == "score") {
    config.detectionThreshold = value.toInt();
    Serial.print(F("検知閾値: "));
    Serial.println(config.detectionThreshold);
  }
}

// ヘルプ表示
void printHelp() {
  Serial.println(F("=== コマンド一覧 ==="));
  Serial.println(F("status     - システム状態表示"));
  Serial.println(F("config     - 設定表示"));
  Serial.println(F("json       - JSON出力切替"));
  Serial.println(F("reset      - システムリセット"));
  Serial.println(F("set temp X - 温度閾値設定"));
  Serial.println(F("set distance X - 距離閾値設定"));
  Serial.println(F("set score X - 検知スコア閾値設定"));
  Serial.println(F("Enter      - デバッグ情報表示"));
}

// システム状態表示
void printSystemStatus() {
  if (config.enableJsonOutput) {
    printJsonStatus();
  } else {
    Serial.println(F("=== システム状態 ==="));
    Serial.print(F("バージョン: ")); Serial.println(F(FIRMWARE_VERSION));
    Serial.print(F("稼働時間: ")); Serial.print(stats.uptime / 1000); Serial.println(F("秒"));
    Serial.print(F("状態: ")); Serial.println(getStateString());
    Serial.print(F("総検知回数: ")); Serial.println(stats.totalDetections);
    Serial.print(F("エラー回数: ")); Serial.println(stats.errorCount);
    Serial.print(F("最終エラー: ")); Serial.println(lastError);
    Serial.print(F("平均距離: ")); Serial.print(stats.averageDistance); Serial.println(F("cm"));
    Serial.print(F("平均物体温度: ")); Serial.print(stats.averageObjectTemp); Serial.println(F("°C"));
  }
}

// JSON形式状態出力
void printJsonStatus() {
  StaticJsonDocument<JSON_BUFFER_SIZE> doc;
  
  doc["version"] = FIRMWARE_VERSION;
  doc["uptime"] = stats.uptime / 1000;
  doc["state"] = getStateString();
  doc["total_detections"] = stats.totalDetections;
  doc["error_count"] = stats.errorCount;
  doc["last_error"] = lastError;
  doc["avg_distance"] = stats.averageDistance;
  doc["avg_object_temp"] = stats.averageObjectTemp;
  doc["timestamp"] = millis();
  
  serializeJson(doc, Serial);
  Serial.println();
}

// 設定表示
void printConfiguration() {
  Serial.println(F("=== システム設定 ==="));
  Serial.print(F("温度閾値: ")); Serial.print(config.tempThreshold); Serial.println(F("°C"));
  Serial.print(F("距離閾値: ")); Serial.print(config.distanceThreshold); Serial.println(F("cm"));
  Serial.print(F("検知スコア閾値: ")); Serial.println(config.detectionThreshold);
  Serial.print(F("サンプリング間隔: ")); Serial.print(config.samplingInterval); Serial.println(F("ms"));
  Serial.print(F("アラート時間: ")); Serial.print(config.alertDuration); Serial.println(F("ms"));
  Serial.print(F("音声: ")); Serial.println(config.enableSound ? F("ON") : F("OFF"));
  Serial.print(F("LED: ")); Serial.println(config.enableLEDs ? F("ON") : F("OFF"));
  Serial.print(F("JSON出力: ")); Serial.println(config.enableJsonOutput ? F("ON") : F("OFF"));
}

// デバッグ情報出力
void printDebugInfo() {
  SensorData data = readSensors();
  
  if (config.enableJsonOutput) {
    printJsonSensorData(data);
  } else {
    Serial.println(F("=== センサー状態 ==="));
    Serial.print(F("PIR1: ")); Serial.print(data.pir1_triggered ? F("ON") : F("OFF"));
    Serial.print(F(", PIR2: ")); Serial.println(data.pir2_triggered ? F("ON") : F("OFF"));
    Serial.print(F("物体温度: ")); Serial.print(data.objectTemp, 1);
    Serial.print(F("°C, 環境温度: ")); Serial.print(data.ambientTemp, 1); Serial.println(F("°C"));
    Serial.print(F("距離: ")); Serial.print(data.distance, 1); Serial.println(F("cm"));
    Serial.print(F("状態: ")); Serial.println(getStateString());
    Serial.print(F("総検知回数: ")); Serial.println(stats.totalDetections);
    Serial.println(F("=================="));
  }
}

// JSON形式センサーデータ出力
void printJsonSensorData(SensorData data) {
  StaticJsonDocument<JSON_BUFFER_SIZE> doc;
  
  doc["timestamp"] = data.timestamp;
  doc["pir1"] = data.pir1_triggered;
  doc["pir2"] = data.pir2_triggered;
  doc["object_temp"] = data.objectTemp;
  doc["ambient_temp"] = data.ambientTemp;
  doc["distance"] = data.distance;
  doc["state"] = getStateString();
  doc["detection_count"] = stats.totalDetections;
  doc["valid"] = data.isValid;
  
  serializeJson(doc, Serial);
  Serial.println();
}

// 状態文字列取得
String getStateString() {
  switch (currentState) {
    case STANDBY: return F("待機中");
    case CALIBRATING: return F("校正中");
    case MONITORING: return F("監視中");
    case ALERT: return F("警戒中");
    case ERROR_STATE: return F("エラー");
    default: return F("不明");
  }
}

// 各種アラート・シーケンス関数
void playOniAlert() {
  int melody[] = {262, 247, 220, 196, 175, 196, 220, 247, 262};
  int durations[] = {200, 200, 200, 200, 400, 200, 200, 200, 400};
  
  for (int i = 0; i < 9; i++) {
    tone(SPEAKER_PIN, melody[i], durations[i]);
    delay(durations[i] * 1.3);
    noTone(SPEAKER_PIN);
  }
}

void startupSequence() {
  for (int j = 0; j < 128; j++) {
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, wheel((i * 256 / LED_COUNT + j) & 255));
    }
    strip.show();
    delay(20);
  }
  
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
  
  // 起動音
  tone(SPEAKER_PIN, 440, 200);
  delay(250);
  tone(SPEAKER_PIN, 554, 200);
  delay(250);
  tone(SPEAKER_PIN, 659, 400);
  delay(500);
  noTone(SPEAKER_PIN);
}

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
