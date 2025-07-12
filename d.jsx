import React, { useState, useEffect, useRef } from ‘react’;
import { Play, Pause, Square, RotateCcw, Clock, CheckCircle, AlertCircle, Download, Upload, Server, Database, Shield } from ‘lucide-react’;

export default function DeployTimer() {
const [isRunning, setIsRunning] = useState(false);
const [totalTime, setTotalTime] = useState(0);
const [currentPhase, setCurrentPhase] = useState(0);
const [phaseStartTime, setPhaseStartTime] = useState(null);
const [deployHistory, setDeployHistory] = useState([]);
const [projectName, setProjectName] = useState(’’);

const [phases, setPhases] = useState([
{ name: ‘コードレビュー’, icon: CheckCircle, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘ビルド’, icon: Upload, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘テスト実行’, icon: Shield, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘ステージング環境’, icon: Server, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘データベースマイグレーション’, icon: Database, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘プロダクション環境’, icon: Server, completed: false, duration: 0, status: ‘pending’ },
{ name: ‘動作確認’, icon: CheckCircle, completed: false, duration: 0, status: ‘pending’ }
]);

const intervalRef = useRef(null);
const deployStartTime = useRef(null);

useEffect(() => {
if (isRunning) {
intervalRef.current = setInterval(() => {
const now = Date.now();
if (deployStartTime.current) {
setTotalTime(Math.floor((now - deployStartTime.current) / 1000));
}
if (phaseStartTime) {
const phaseDuration = Math.floor((now - phaseStartTime) / 1000);
setPhases(prev => prev.map((phase, index) =>
index === currentPhase ? { …phase, duration: phaseDuration } : phase
));
}
}, 1000);
} else {
clearInterval(intervalRef.current);
}

```
return () => clearInterval(intervalRef.current);
```

}, [isRunning, phaseStartTime, currentPhase]);

const formatTime = (seconds) => {
const mins = Math.floor(seconds / 60);
const secs = seconds % 60;
return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatDetailedTime = (seconds) => {
const hours = Math.floor(seconds / 3600);
const mins = Math.floor((seconds % 3600) / 60);
const secs = seconds % 60;

```
if (hours > 0) {
  return `${hours}h ${mins}m ${secs}s`;
} else if (mins > 0) {
  return `${mins}m ${secs}s`;
} else {
  return `${secs}s`;
}
```

};

const startDeploy = () => {
if (!isRunning) {
setIsRunning(true);
deployStartTime.current = Date.now();
setPhaseStartTime(Date.now());
setPhases(prev => prev.map((phase, index) =>
index === 0 ? { …phase, status: ‘running’ } : { …phase, status: ‘pending’ }
));
} else {
setIsRunning(false);
}
};

const completeCurrentPhase = () => {
if (currentPhase < phases.length - 1) {
const now = Date.now();
const phaseDuration = Math.floor((now - phaseStartTime) / 1000);

```
  setPhases(prev => prev.map((phase, index) => {
    if (index === currentPhase) {
      return { ...phase, completed: true, duration: phaseDuration, status: 'completed' };
    } else if (index === currentPhase + 1) {
      return { ...phase, status: 'running' };
    }
    return phase;
  }));
  
  setCurrentPhase(prev => prev + 1);
  setPhaseStartTime(now);
  
  // 成功音を再生
  playSuccessSound();
} else {
  // 最後のフェーズ完了
  finishDeploy();
}
```

};

const markPhaseAsFailed = () => {
setPhases(prev => prev.map((phase, index) =>
index === currentPhase ? { …phase, status: ‘failed’ } : phase
));
setIsRunning(false);
playErrorSound();
};

const finishDeploy = () => {
const now = Date.now();
const phaseDuration = Math.floor((now - phaseStartTime) / 1000);
const finalTotalTime = Math.floor((now - deployStartTime.current) / 1000);

```
setPhases(prev => prev.map((phase, index) => 
  index === currentPhase 
    ? { ...phase, completed: true, duration: phaseDuration, status: 'completed' }
    : phase
));

setIsRunning(false);

// デプロイ履歴に追加
const deployRecord = {
  id: Date.now(),
  projectName: projectName || 'Unnamed Project',
  date: new Date().toLocaleString('ja-JP'),
  totalTime: finalTotalTime,
  phases: [...phases.map((phase, index) => 
    index === currentPhase 
      ? { ...phase, duration: phaseDuration, completed: true, status: 'completed' }
      : phase
  )],
  status: 'success'
};

setDeployHistory(prev => [deployRecord, ...prev].slice(0, 10)); // 最新10件を保持
playCompletionSound();
```

};

const resetTimer = () => {
setIsRunning(false);
setTotalTime(0);
setCurrentPhase(0);
setPhaseStartTime(null);
deployStartTime.current = null;
setPhases(prev => prev.map(phase => ({
…phase,
completed: false,
duration: 0,
status: ‘pending’
})));
};

const playSuccessSound = () => {
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const oscillator = audioContext.createOscillator();
const gainNode = audioContext.createGain();

```
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);

oscillator.frequency.setValueAtTime(523, audioContext.currentTime); // C5
oscillator.frequency.setValueAtTime(659, audioContext.currentTime + 0.1); // E5
oscillator.frequency.setValueAtTime(784, audioContext.currentTime + 0.2); // G5

oscillator.type = 'sine';
gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

oscillator.start();
oscillator.stop(audioContext.currentTime + 0.3);
```

};

const playErrorSound = () => {
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const oscillator = audioContext.createOscillator();
const gainNode = audioContext.createGain();

```
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);

oscillator.frequency.value = 200;
oscillator.type = 'sawtooth';
gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

oscillator.start();
oscillator.stop(audioContext.currentTime + 0.5);
```

};

const playCompletionSound = () => {
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

```
// ファンファーレ風の音
const notes = [523, 659, 784, 1047]; // C5, E5, G5, C6
notes.forEach((freq, index) => {
  setTimeout(() => {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = freq;
    oscillator.type = 'sine';
    gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.4);
  }, index * 150);
});
```

};

const exportResults = () => {
const results = {
projectName: projectName || ‘Unnamed Project’,
deployDate: new Date().toISOString(),
totalTime: totalTime,
phases: phases,
history: deployHistory
};

```
const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `deploy-results-${new Date().toISOString().split('T')[0]}.json`;
a.click();
URL.revokeObjectURL(url);
```

};

const getStatusColor = (status) => {
switch (status) {
case ‘completed’: return ‘text-green-600 bg-green-100’;
case ‘running’: return ‘text-blue-600 bg-blue-100’;
case ‘failed’: return ‘text-red-600 bg-red-100’;
default: return ‘text-gray-600 bg-gray-100’;
}
};

const getStatusIcon = (status) => {
switch (status) {
case ‘completed’: return ‘✓’;
case ‘running’: return ‘⟳’;
case ‘failed’: return ‘✗’;
default: return ‘○’;
}
};

return (
<div className="max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
<div className="bg-white rounded-lg shadow-lg p-6">
<div className="text-center mb-6">
<h1 className="text-3xl font-bold text-gray-800 mb-4">デプロイ時間計測タイマー</h1>
<div className="flex justify-center gap-4 mb-4">
<input
type=“text”
placeholder=“プロジェクト名を入力”
value={projectName}
onChange={(e) => setProjectName(e.target.value)}
className=“px-4 py-2 border border-gray-300 rounded-lg text-center”
/>
</div>
</div>

```
    {/* 総時間表示 */}
    <div className="text-center mb-8">
      <div className="text-6xl font-mono font-bold text-blue-600 mb-2">
        {formatTime(totalTime)}
      </div>
      <div className="text-lg text-gray-600">総デプロイ時間</div>
      {isRunning && (
        <div className="mt-2">
          <div className="inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
          <span className="text-sm text-red-600 font-medium">デプロイ中...</span>
        </div>
      )}
    </div>

    {/* フェーズ一覧 */}
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4">デプロイフェーズ</h2>
      <div className="space-y-3">
        {phases.map((phase, index) => {
          const Icon = phase.icon;
          return (
            <div
              key={index}
              className={`flex items-center justify-between p-4 rounded-lg border-2 transition-all ${
                index === currentPhase && isRunning
                  ? 'border-blue-500 bg-blue-50'
                  : phase.completed
                  ? 'border-green-500 bg-green-50'
                  : phase.status === 'failed'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-5 h-5 ${
                  phase.completed ? 'text-green-600' :
                  index === currentPhase && isRunning ? 'text-blue-600' :
                  phase.status === 'failed' ? 'text-red-600' : 'text-gray-500'
                }`} />
                <span className="font-medium text-gray-800">{phase.name}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(phase.status)}`}>
                  {getStatusIcon(phase.status)}
                </span>
              </div>
              <div className="text-right">
                <div className={`font-mono font-bold ${
                  index === currentPhase && isRunning ? 'text-blue-600' :
                  phase.completed ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {formatTime(phase.duration)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>

    {/* コントロールボタン */}
    <div className="flex justify-center gap-4 mb-8">
      <button
        onClick={startDeploy}
        className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors ${
          isRunning
            ? 'bg-red-500 text-white hover:bg-red-600'
            : 'bg-green-500 text-white hover:bg-green-600'
        }`}
      >
        {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        {isRunning ? '一時停止' : 'デプロイ開始'}
      </button>
      
      {isRunning && (
        <>
          <button
            onClick={completeCurrentPhase}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 flex items-center gap-2 transition-colors"
          >
            <CheckCircle className="w-5 h-5" />
            フェーズ完了
          </button>
          
          <button
            onClick={markPhaseAsFailed}
            className="px-6 py-3 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 flex items-center gap-2 transition-colors"
          >
            <AlertCircle className="w-5 h-5" />
            失敗
          </button>
        </>
      )}
      
      <button
        onClick={resetTimer}
        className="px-6 py-3 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600 flex items-center gap-2 transition-colors"
      >
        <RotateCcw className="w-5 h-5" />
        リセット
      </button>
      
      <button
        onClick={exportResults}
        className="px-6 py-3 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 flex items-center gap-2 transition-colors"
      >
        <Download className="w-5 h-5" />
        結果出力
      </button>
    </div>

    {/* デプロイ履歴 */}
    {deployHistory.length > 0 && (
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">最近のデプロイ履歴</h2>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {deployHistory.map((deploy) => (
            <div key={deploy.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-800">{deploy.projectName}</div>
                <div className="text-sm text-gray-600">{deploy.date}</div>
              </div>
              <div className="text-right">
                <div className="font-mono font-bold text-blue-600">
                  {formatDetailedTime(deploy.totalTime)}
                </div>
                <div className={`text-xs px-2 py-1 rounded-full ${
                  deploy.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {deploy.status === 'success' ? '成功' : '失敗'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )}

    <div className="mt-6 text-center text-sm text-gray-600">
      <p>各フェーズの完了後は「フェーズ完了」ボタンを押して次の段階に進んでください</p>
      <p>問題が発生した場合は「失敗」ボタンでマークできます</p>
    </div>
  </div>
</div>
```

);
}