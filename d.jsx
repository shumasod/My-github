import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, Square, RotateCcw, Clock, CheckCircle, AlertCircle, Download, Upload, Server, Database, Shield } from 'lucide-react';

export default function DeployTimer() {
  const [isRunning, setIsRunning] = useState(false);
  const [totalTime, setTotalTime] = useState(0);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [phaseStartTime, setPhaseStartTime] = useState(null);
  const [deployHistory, setDeployHistory] = useState([]);
  const [projectName, setProjectName] = useState('');

  const [phases, setPhases] = useState([
    { name: 'コードレビュー', icon: CheckCircle, completed: false, duration: 0, status: 'pending' },
    { name: 'ビルド', icon: Upload, completed: false, duration: 0, status: 'pending' },
    { name: 'テスト実行', icon: Shield, completed: false, duration: 0, status: 'pending' },
    { name: 'ステージング環境', icon: Server, completed: false, duration: 0, status: 'pending' },
    { name: 'データベースマイグレーション', icon: Database, completed: false, duration: 0, status: 'pending' },
    { name: 'プロダクション環境', icon: Server, completed: false, duration: 0, status: 'pending' },
    { name: '動作確認', icon: CheckCircle, completed: false, duration: 0, status: 'pending' }
  ]);

  const intervalRef = useRef(null);
  const deployStartTime = useRef(null);

  // useCallbackでタイマーを更新する関数を定義して依存を安定化
  const updateTimer = useCallback(() => {
    const now = Date.now();
    if (deployStartTime.current) {
      setTotalTime(Math.floor((now - deployStartTime.current) / 1000));
    }
    if (phaseStartTime) {
      const phaseDuration = Math.floor((now - phaseStartTime) / 1000);
      setPhases(prev => prev.map((phase, index) =>
        index === currentPhase ? { ...phase, duration: phaseDuration } : phase
      ));
    }
  }, [phaseStartTime, currentPhase]);

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(updateTimer, 1000);
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isRunning, updateTimer]);

  const formatTime = useCallback((seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  const formatDetailedTime = useCallback((seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${mins}m ${secs}s`;
    } else if (mins > 0) {
      return `${mins}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  }, []);

  const startDeploy = useCallback(() => {
    if (!isRunning) {
      setIsRunning(true);
      deployStartTime.current = Date.now();
      setPhaseStartTime(Date.now());
      setPhases(prev => prev.map((phase, index) =>
        index === 0 ? { ...phase, status: 'running' } : { ...phase, status: 'pending' }
      ));
    } else {
      setIsRunning(false);
    }
  }, [isRunning]);

  const completeCurrentPhase = useCallback(() => {
    if (currentPhase < phases.length - 1) {
      const now = Date.now();
      const phaseDuration = Math.floor((now - phaseStartTime) / 1000);

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
  }, [currentPhase, phases.length, phaseStartTime]);

  const markPhaseAsFailed = useCallback(() => {
    setPhases(prev => prev.map((phase, index) =>
      index === currentPhase ? { ...phase, status: 'failed' } : phase
    ));
    setIsRunning(false);
    playErrorSound();
  }, [currentPhase]);

  const finishDeploy = useCallback(() => {
    const now = Date.now();
    const phaseDuration = Math.floor((now - phaseStartTime) / 1000);
    const finalTotalTime = Math.floor((now - deployStartTime.current) / 1000);

    setPhases(prev => prev.map((phase, index) =>
      index === currentPhase
        ? { ...phase, completed: true, duration: phaseDuration, status: 'completed' }
        : phase
    ));

    setIsRunning(false);

    // デプロイ履歴に追加（現在のphasesをスナップショット）
    const snapshotPhases = phases.map((phase, index) =>
      index === currentPhase
        ? { ...phase, duration: phaseDuration, completed: true, status: 'completed' }
        : phase
    );

    const deployRecord = {
      id: Date.now(),
      projectName: projectName || 'Unnamed Project',
      date: new Date().toLocaleString('ja-JP'),
      totalTime: finalTotalTime,
      phases: snapshotPhases,
      status: 'success'
    };

    setDeployHistory(prev => [deployRecord, ...prev].slice(0, 10)); // 最新10件を保持
    playCompletionSound();
  }, [currentPhase, phaseStartTime, phases, projectName]);

  const resetTimer = useCallback(() => {
    setIsRunning(false);
    setTotalTime(0);
    setCurrentPhase(0);
    setPhaseStartTime(null);
    deployStartTime.current = null;
    setPhases(prev => prev.map(phase => ({
      ...phase,
      completed: false,
      duration: 0,
      status: 'pending'
    })));
    setDeployHistory([]); // 履歴もリセット（オプション）
  }, []);

  const playSuccessSound = useCallback(() => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

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
  }, []);

  const playErrorSound = useCallback(() => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 200;
    oscillator.type = 'sawtooth';
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.5);
  }, []);

  const playCompletion
