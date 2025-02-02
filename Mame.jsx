import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Bell, AlertTriangle, Battery, Wifi, Bluetooth, BluetoothOff } from 'lucide-react';

// Bluetooth service and characteristic UUIDs
const DEVICE_NAME = 'SetsubunDetector';
const SERVICE_UUID = '0000FFE0-0000-1000-8000-00805F9B34FB';
const CHARACTERISTIC_UUID = '0000FFE1-0000-1000-8000-00805F9B34FB';

const SetsubunDetectorBLE = () => {
  const [device, setDevice] = useState(null);
  const [characteristic, setCharacteristic] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [sensorData, setSensorData] = useState({
    distance: 5,
    motion: false,
    battery: 100
  });
  const [isActive, setIsActive] = useState(true);

  // Bluetooth接続処理
  const connectBluetooth = async () => {
    try {
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ name: DEVICE_NAME }],
        optionalServices: [SERVICE_UUID]
      });

      device.addEventListener('gattserverdisconnected', onDisconnected);
      setDevice(device);

      const server = await device.gatt.connect();
      const service = await server.getPrimaryService(SERVICE_UUID);
      const characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);
      setCharacteristic(characteristic);
      setIsConnected(true);

      // データ受信の開始
      startNotifications(characteristic);
    } catch (error) {
      console.error('Bluetooth connection failed:', error);
      alert('Bluetooth接続に失敗しました。');
    }
  };

  // 切断処理
  const onDisconnected = () => {
    setIsConnected(false);
    setDevice(null);
    setCharacteristic(null);
  };

  // データ受信の設定
  const startNotifications = async (characteristic) => {
    await characteristic.startNotifications();
    characteristic.addEventListener('characteristicvaluechanged', handleSensorData);
  };

  // センサーデータの処理
  const handleSensorData = (event) => {
    const value = event.target.value;
    const decoder = new TextDecoder();
    const data = decoder.decode(value);
    
    try {
      const parsedData = JSON.parse(data);
      setSensorData({
        distance: parsedData.distance,
        motion: parsedData.motion,
        battery: parsedData.battery
      });
    } catch (e) {
      console.error('Data parsing error:', e);
    }
  };

  // アラートレベルの判定
  const getAlertLevel = () => {
    if (!isActive || !isConnected) return 'inactive';
    if (!sensorData.motion) return 'normal';
    if (sensorData.distance <= 1) return 'danger';
    if (sensorData.distance <= 3) return 'warning';
    return 'normal';
  };

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
            <Battery className={`w-6 h-6 ${sensorData.battery < 20 ? 'text-red-500' : 'text-green-500'}`} />
            {isConnected ? 
              <Bluetooth className="w-6 h-6 text-blue-500" /> :
              <BluetoothOff className="w-6 h-6 text-gray-400" />
            }
          </div>
        </div>

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
                disabled={isConnected}
                className={`w-full px-4 py-2 rounded ${
                  isConnected ? 'bg-green-500 text-white' : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {isConnected ? '接続済み' : 'Bluetooth接続'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">センサー状態</label>
            <div className="mt-2 flex justify-between items-center">
              <button
                onClick={() => setIsActive(!isActive)}
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
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default SetsubunDetectorBLE;
