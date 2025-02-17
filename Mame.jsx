import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Bell, AlertTriangle, Battery, Wifi, Bluetooth, BluetoothOff, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Constants
const DEVICE_NAME = 'SetsubunDetector';
const SERVICE_UUID = '0000FFE0-0000-1000-8000-00805F9B34FB';
const CHARACTERISTIC_UUID = '0000FFE1-0000-1000-8000-00805F9B34FB';
const RECONNECT_DELAY = 5000;
const BATTERY_WARNING_THRESHOLD = 20;
const DISTANCE_WARNING_THRESHOLD = 3;
const DISTANCE_DANGER_THRESHOLD = 1;

const SetsubunDetectorBLE = () => {
  // State management
  const [device, setDevice] = useState(null);
  const [characteristic, setCharacteristic] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [sensorData, setSensorData] = useState({
    distance: 5,
    motion: false,
    battery: 100,
    lastUpdate: Date.now()
  });
  const [isActive, setIsActive] = useState(true);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // センサーデータの処理
  const handleSensorData = useCallback((event) => {
    const value = event.target.value;
    const decoder = new TextDecoder();
    const data = decoder.decode(value);
    
    try {
      const parsedData = JSON.parse(data);
      setSensorData(prev => ({
        ...prev,
        distance: parsedData.distance,
        motion: parsedData.motion,
        battery: parsedData.battery,
        lastUpdate: Date.now()
      }));
    } catch (e) {
      console.error('Data parsing error:', e);
      setError('センサーデータの解析に失敗しました');
    }
  }, []);

  // Bluetooth接続処理
  const connectBluetooth = async () => {
    if (isConnecting) return;
    
    setIsConnecting(true);
    setError(null);
    
    try {
      const newDevice = await navigator.bluetooth.requestDevice({
        filters: [{ name: DEVICE_NAME }],
        optionalServices: [SERVICE_UUID]
      });

      newDevice.addEventListener('gattserverdisconnected', handleDisconnection);
      setDevice(newDevice);

      const server = await newDevice.gatt.connect();
      const service = await server.getPrimaryService(SERVICE_UUID);
      const char = await service.getCharacteristic(CHARACTERISTIC_UUID);
      
      await char.startNotifications();
      char.addEventListener('characteristicvaluechanged', handleSensorData);
      
      setCharacteristic(char);
      setIsConnected(true);
      setReconnectAttempts(0);
    } catch (error) {
      console.error('Bluetooth connection failed:', error);
      setError(getBetterErrorMessage(error));
    } finally {
      setIsConnecting(false);
    }
  };

  // 切断処理
  const handleDisconnection = useCallback(async () => {
    setIsConnected(false);
    
    if (isActive && reconnectAttempts < 3) {
      setReconnectAttempts(prev => prev + 1);
      setTimeout(async () => {
        try {
          if (device?.gatt) {
            await device.gatt.connect();
            setIsConnected(true);
          }
        } catch (error) {
          console.error('Reconnection failed:', error);
          setError('再接続に失敗しました');
        }
      }, RECONNECT_DELAY);
    }
  }, [device, isActive, reconnectAttempts]);

  // データの有効性チェック
  useEffect(() => {
    const checkDataValidity = () => {
      const now = Date.now();
      if (isConnected && now - sensorData.lastUpdate > 10000) {
        setError('センサーデータの更新が停止しています');
      }
    };

    const interval = setInterval(checkDataValidity, 5000);
    return () => clearInterval(interval);
  }, [isConnected, sensorData.lastUpdate]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (characteristic) {
        characteristic.stopNotifications();
      }
      if (device) {
        device.removeEventListener('gattserverdisconnected', handleDisconnection);
      }
    };
  }, [characteristic, device, handleDisconnection]);

  // アラートレベルの判定
  const getAlertLevel = useCallback(() => {
    if (!isActive || !isConnected) return 'inactive';
    if (!sensorData.motion) return 'normal';
    if (sensorData.distance <= DISTANCE_DANGER_THRESHOLD) return 'danger';
    if (sensorData.distance <= DISTANCE_WARNING_THRESHOLD) return 'warning';
    return 'normal';
  }, [isActive, isConnected, sensorData.motion, sensorData.distance]);

  // アラート表示設定
  const alertStyles = {
    inactive: {
      bgColor: 'bg-gray-200',
      textColor: 'text-gray-600',
      message: isConnected ? 'システム停止中' : 'デバイス未接続',
      icon: null
    },
    normal: {
      bgColor: 'bg-green-100',
      textColor: 'text-green-600',
      message: '監視中...',
      icon: null
    },
    warning: {
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-600',
      message: '鬼が近づいています！',
      icon: <AlertTriangle className="w-6 h-6" />
    },
    danger: {
      bgColor: 'bg-red-100',
      textColor: 'text-red-600',
      message: '鬼が接近中！！',
      icon: <Bell className="w-6 h-6" />
    }
  };

  const currentAlert = alertStyles[getAlertLevel()];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <Card className="w-full max-w-md p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">鬼検知システム</h2>
          <div className="flex space-x-2">
            <Battery className={`w-6 h-6 ${
              sensorData.battery < BATTERY_WARNING_THRESHOLD ? 'text-red-500' : 'text-green-500'
            }`} />
            {isConnected ? 
              <Bluetooth className="w-6 h-6 text-blue-500" /> :
              <BluetoothOff className="w-6 h-6 text-gray-400" />
            }
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className={`p-4 rounded-lg ${currentAlert.bgColor}`}>
          <div className="flex items-center justify-between">
            <span className={`font-medium ${currentAlert.textColor}`}>
              {currentAlert.message}
            </span>
            {currentAlert.icon}
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">デバイス接続</label>
            <div className="mt-2">
              <button
                onClick={connectBluetooth}
                disabled={isConnected || isConnecting}
                className={`w-full px-4 py-2 rounded ${
                  isConnected ? 'bg-green-500 text-white' :
                  isConnecting ? 'bg-gray-400 text-white' :
                  'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {isConnected ? '接続済み' :
                 isConnecting ? '接続中...' :
                 'Bluetooth接続'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">センサー状態</label>
            <div className="mt-2 flex justify-between items-center">
              <button
                onClick={() => {
                  setIsActive(!isActive);
                  setError(null);
                }}
                disabled={!isConnected}
                className={`px-4 py-2 rounded ${
                  !isConnected ? 'bg-gray-300' :
                  isActive ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'
                }`}
              >
                {isActive ? '動作中' : '停止中'}
              </button>
              <span className="text-sm text-gray-500">
                バッテリー: {Math.round(sensorData.battery)}%
              </span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">センサー情報</label>
            <div className="mt-2 space-y-2">
              <div className="flex justify-between">
                <span>動体検知状態:</span>
                <span className={sensorData.motion ? 'text-red-500' : 'text-green-500'}>
                  {sensorData.motion ? '検知中' : '検知なし'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>検知距離:</span>
                <span>{sensorData.distance.toFixed(1)}m</span>
              </div>
              <div className="flex justify-between">
                <span>最終更新:</span>
                <span>{new Date(sensorData.lastUpdate).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

// エラーメッセージの改善
const getBetterErrorMessage = (error) => {
  if (error.name === 'NotFoundError') {
    return 'デバイスが見つかりませんでした。デバイスの電源が入っているか確認してください。';
  }
  if (error.name === 'SecurityError') {
    return 'Bluetooth接続の権限がありません。ブラウザの設定を確認してください。';
  }
  if (error.name === 'NetworkError') {
    return 'ネットワークエラーが発生しました。接続を確認してください。';
  }
  return `エラーが発生しました: ${error.message}`;
};

export default SetsubunDetectorBLE;
