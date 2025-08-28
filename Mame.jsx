import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, Bluetooth, Power, Battery, Wifi, WifiOff } from 'lucide-react';

// システム状態の定義
const SystemState = {
  STANDBY: 0,
  WARNING: 1,
  ALERT: 2,
  LOW_BATTERY: 3
};

const StateNames = {
  [SystemState.STANDBY]: '待機中',
  [SystemState.WARNING]: '警戒モード',
  [SystemState.ALERT]: '警報モード',
  [SystemState.LOW_BATTERY]: '電池残量低下'
};

const SetsubunDetectorApp = () => {
  // 状態管理
  const [isConnected, setIsConnected] = useState(false);
  const [systemActive, setSystemActive] = useState(true);
  const [currentState, setCurrentState] = useState(SystemState.STANDBY);
  const [distance, setDistance] = useState(0);
  const [batteryPercentage, setBatteryPercentage] = useState(100);
  const [motionDetected, setMotionDetected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  
  // Bluetooth関連
  const [device, setDevice] = useState(null);
  const [characteristic, setCharacteristic] = useState(null);
  
  // UI状態
  const [logs, setLogs] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('未接続');
  
  // リファレンス
  const logsRef = useRef(logs);
  logsRef.current = logs;

  // ログ追加関数
  const addLog = (message, type = 'info') => {
    const newLog = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('ja-JP'),
      message,
      type
    };
    setLogs(prev => [newLog, ...prev.slice(0, 49)]); // 最新50件のみ保持
  };

  // Bluetooth接続関数
  const connectBluetooth = async () => {
    try {
      setConnectionStatus('接続中...');
      addLog('Bluetoothデバイスを検索中...', 'info');
      
      const bluetoothDevice = await navigator.bluetooth.requestDevice({
        filters: [
          { namePrefix: 'SetsubunDetector' },
          { services: ['12345678-1234-1234-1234-123456789abc'] }
        ],
        optionalServices: ['12345678-1234-1234-1234-123456789abc']
      });

      addLog(`デバイス発見: ${bluetoothDevice.name}`, 'success');
      
      const server = await bluetoothDevice.gatt.connect();
      const service = await server.getPrimaryService('12345678-1234-1234-1234-123456789abc');
      const char = await service.getCharacteristic('87654321-4321-4321-4321-cba987654321');
      
      setDevice(bluetoothDevice);
      setCharacteristic(char);
      setIsConnected(true);
      setConnectionStatus('接続済み');
      
      addLog('Bluetooth接続完了', 'success');

      // 通知設定
      await char.startNotifications();
      char.addEventListener('characteristicvaluechanged', handleBluetoothData);

      // 切断イベントリスナー
      bluetoothDevice.addEventListener('gattserverdisconnected', handleDisconnect);
      
    } catch (error) {
      console.error('Bluetooth接続エラー:', error);
      addLog(`接続エラー: ${error.message}`, 'error');
      setConnectionStatus('接続失敗');
    }
  };

  // Bluetooth切断処理
  const handleDisconnect = () => {
    setIsConnected(false);
    setDevice(null);
    setCharacteristic(null);
    setConnectionStatus('切断されました');
    addLog('Bluetoothデバイスが切断されました', 'warning');
  };

  // Bluetoothデータ受信処理
  const handleBluetoothData = (event) => {
    try {
      const decoder = new TextDecoder();
      const jsonString = decoder.decode(event.target.value);
      const data = JSON.parse(jsonString);
      
      // データ更新
      setDistance(data.distance * 100); // mからcmに変換
      setMotionDetected(data.motion);
      setBatteryPercentage(data.battery);
      setCurrentState(data.state);
      setSystemActive(data.active);
      setLastUpdate(new Date());
      
      addLog(`データ受信: 距離=${(data.distance * 100).toFixed(1)}cm, バッテリー=${data.battery.toFixed(1)}%`, 'info');
      
    } catch (error) {
      console.error('データ解析エラー:', error);
      addLog(`データ解析エラー: ${error.message}`, 'error');
    }
  };

  // コマンド送信関数
  const sendCommand = async (command) => {
    if (!characteristic) {
      addLog('デバイスが接続されていません', 'error');
      return;
    }

    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(command + '\n');
      await characteristic.writeValue(data);
      addLog(`コマンド送信: ${command}`, 'info');
    } catch (error) {
      console.error('コマンド送信エラー:', error);
      addLog(`コマンド送信エラー: ${error.message}`, 'error');
    }
  };

  // システム制御関数
  const handleSystemToggle = () => {
    const command = systemActive ? 'STOP' : 'START';
    sendCommand(command);
  };

  // ステータス更新要求
  const requestStatus = () => {
    sendCommand('STATUS');
  };

  // LEDカラー取得
  const getLedColor = () => {
    switch (currentState) {
      case SystemState.STANDBY: return 'bg-green-500';
      case SystemState.WARNING: return 'bg-yellow-500';
      case SystemState.ALERT: return 'bg-red-500';
      case SystemState.LOW_BATTERY: return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  // バッテリーアイコンの色
  const getBatteryColor = () => {
    if (batteryPercentage > 50) return 'text-green-500';
    if (batteryPercentage > 20) return 'text-yellow-500';
    return 'text-red-500';
  };

  // 距離に基づく警告レベル
  const getDistanceWarning = () => {
    if (distance > 300 || distance === 0) return null;
    if (distance < 200) return { level: 'danger', message: '緊急警報！' };
    if (distance < 300) return { level: 'warning', message: '警戒中' };
    return null;
  };

  const distanceWarning = getDistanceWarning();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-6">
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-yellow-400 to-red-500 bg-clip-text text-transparent">
            🎌 節分鬼検知システム v1.3 🎌
          </h1>
          <p className="text-lg text-gray-300">Bluetooth対応版 - Web制御インターフェース</p>
        </div>

        {/* 接続ステータス */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 border-2 border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
              <span className="font-semibold">接続状態: {connectionStatus}</span>
              {isConnected ? <Wifi className="w-5 h-5 text-green-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
            </div>
            <button
              onClick={isConnected ? () => device?.gatt?.disconnect() : connectBluetooth}
              className={`px-4 py-2 rounded-lg font-medium ${
                isConnected 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
              } transition-colors duration-200`}
            >
              <Bluetooth className="w-4 h-4 inline mr-2" />
              {isConnected ? '切断' : '接続'}
            </button>
          </div>
        </div>

        {/* メイン制御パネル */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          
          {/* システム状態 */}
          <div className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-center">システム状態</h3>
            <div className="flex flex-col items-center space-y-4">
              <div className={`w-16 h-16 rounded-full ${getLedColor()} animate-pulse shadow-lg`}></div>
              <div className="text-center">
                <p className="text-lg font-semibold">{StateNames[currentState]}</p>
                <p className="text-sm text-gray-400">
                  最終更新: {lastUpdate.toLocaleTimeString('ja-JP')}
                </p>
              </div>
            </div>
          </div>

          {/* 距離センサー */}
          <div className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-center">距離センサー</h3>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">
                {distance > 0 ? `${distance.toFixed(1)}cm` : '---'}
              </div>
              {distanceWarning && (
                <div className={`mt-3 p-2 rounded-lg ${
                  distanceWarning.level === 'danger' 
                    ? 'bg-red-600 text-white' 
                    : 'bg-yellow-600 text-white'
                }`}>
                  <AlertCircle className="w-4 h-4 inline mr-2" />
                  {distanceWarning.message}
                </div>
              )}
              {motionDetected && (
                <div className="mt-2 text-yellow-400">
                  🚶 動きを検知中
                </div>
              )}
            </div>
          </div>

          {/* バッテリー状態 */}
          <div className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-center">バッテリー</h3>
            <div className="text-center">
              <Battery className={`w-12 h-12 mx-auto mb-3 ${getBatteryColor()}`} />
              <div className="text-3xl font-bold mb-2">
                {batteryPercentage.toFixed(1)}%
              </div>
              <div className="w-full bg-gray-600 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${getBatteryColor().replace('text-', 'bg-')}`}
                  style={{ width: `${Math.max(batteryPercentage, 0)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* 制御ボタン */}
        <div className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700 mb-6">
          <h3 className="text-xl font-bold mb-4 text-center">システム制御</h3>
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={handleSystemToggle}
              disabled={!isConnected}
              className={`px-6 py-3 rounded-lg font-medium transition-colors duration-200 ${
                systemActive
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'
              } disabled:bg-gray-600 disabled:cursor-not-allowed`}
            >
              <Power className="w-5 h-5 inline mr-2" />
              {systemActive ? 'システム停止' : 'システム開始'}
            </button>
            
            <button
              onClick={requestStatus}
              disabled={!isConnected}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors duration-200 disabled:bg-gray-600 disabled:cursor-not-allowed"
            >
              ステータス更新
            </button>
          </div>
        </div>

        {/* ログ表示 */}
        <div className="bg-gray-800 rounded-lg p-6 border-2 border-gray-700">
          <h3 className="text-xl font-bold mb-4">システムログ</h3>
          <div className="bg-black rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <p className="text-gray-500">ログがありません</p>
            ) : (
              logs.map((log) => (
                <div key={log.id} className={`mb-1 ${
                  log.type === 'error' ? 'text-red-400' :
                  log.type === 'success' ? 'text-green-400' :
                  log.type === 'warning' ? 'text-yellow-400' :
                  'text-gray-300'
                }`}>
                  <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
                </div>
              ))
            )}
          </div>
        </div>

        {/* フッター */}
        <div className="text-center mt-8 text-gray-400">
          <p>節分鬼検知システム - Web Bluetooth API対応</p>
          <p className="text-sm">豆まきの効果を科学的に測定します 🫘👹</p>
        </div>
      </div>
    </div>
  );
};

export default SetsubunDetectorApp;
