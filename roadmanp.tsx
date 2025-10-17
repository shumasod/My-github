import React, { useState } from 'react';
import { CheckCircle, Circle, Code, Lightbulb, Users, BookOpen, Rocket, Award } from 'lucide-react';

export default function HobbyRoadmap() {
  const [completedItems, setCompletedItems] = useState({});

  const toggleItem = (id) => {
    setCompletedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const categories = [
    {
      icon: <Code className="w-6 h-6" />,
      title: "プログラミングスキル強化",
      color: "bg-blue-500",
      items: [
        { id: "go-advanced", text: "Goの高度なパターン学習（並行処理、チャネル最適化）", level: "中級" },
        { id: "rust", text: "Rustを学んで低レイヤーの理解を深める", level: "新規" },
        { id: "ddd", text: "ドメイン駆動設計（DDD）の実践", level: "中級" },
        { id: "microservices", text: "マイクロサービスアーキテクチャの構築", level: "上級" }
      ]
    },
    {
      icon: <Rocket className="w-6 h-6" />,
      title: "個人プロジェクト",
      color: "bg-purple-500",
      items: [
        { id: "oss", text: "OSSプロジェクトへのコントリビューション開始", level: "推奨" },
        { id: "cli-tool", text: "日常業務を楽にするCLIツール開発（Go）", level: "実用" },
        { id: "monitoring", text: "自作監視ツール／ダッシュボード構築", level: "実用" },
        { id: "k8s-operator", text: "Kubernetes Operatorの開発", level: "上級" }
      ]
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "コミュニティ活動",
      color: "bg-green-500",
      items: [
        { id: "lt", text: "技術カンファレンスでLT登壇（15分）", level: "挑戦" },
        { id: "blog-monthly", text: "月1回の技術ブログ執筆を習慣化", level: "継続" },
        { id: "study-group", text: "オンライン勉強会の主催", level: "挑戦" },
        { id: "mentoring", text: "技術メンタリング活動の開始", level: "上級" }
      ]
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "知識の体系化",
      color: "bg-orange-500",
      items: [
        { id: "cert", text: "AWS/GCP認定資格の取得", level: "資格" },
        { id: "reading", text: "月2冊の技術書精読", level: "継続" },
        { id: "zenn-book", text: "Zenn Bookで技術書執筆", level: "挑戦" },
        { id: "architecture", text: "システムアーキテクチャの事例研究", level: "継続" }
      ]
    },
    {
      icon: <Lightbulb className="w-6 h-6" />,
      title: "クリエイティブ挑戦",
      color: "bg-pink-500",
      items: [
        { id: "game", text: "趣味でシンプルなゲーム開発", level: "楽しむ" },
        { id: "iot", text: "IoT／ラズパイプロジェクト", level: "新規" },
        { id: "ai-ml", text: "機械学習の基礎を学ぶ", level: "新規" },
        { id: "webapp", text: "フルスタックWebアプリ開発", level: "実用" }
      ]
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: "長期目標",
      color: "bg-indigo-500",
      items: [
        { id: "conference-talk", text: "大規模カンファレンスで登壇", level: "目標" },
        { id: "tech-lead", text: "技術コミュニティのリーダー的存在に", level: "目標" },
        { id: "saas", text: "個人開発のSaaSサービスリリース", level: "目標" },
        { id: "book-author", text: "技術書の商業出版", level: "目標" }
      ]
    }
  ];

  const completionRate = Object.values(completedItems).filter(Boolean).length;
  const totalItems = categories.reduce((sum, cat) => sum + cat.items.length, 0);
  const percentage = Math.round((completionRate / totalItems) * 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* ヘッダー */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🚀 技術趣味発展ロードマップ
          </h1>
          <p className="text-gray-600 mb-4">
            インフラエンジニアとしてのスキルを活かし、楽しみながら成長していくための実践的なプラン
          </p>
          
          {/* 進捗バー */}
          <div className="mt-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">達成度</span>
              <span className="text-sm font-bold text-blue-600">{completionRate} / {totalItems} ({percentage}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* カテゴリーカード */}
        <div className="space-y-4">
          {categories.map((category, catIndex) => (
            <div key={catIndex} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className={`${category.color} p-3 rounded-lg text-white`}>
                  {category.icon}
                </div>
                <h2 className="text-2xl font-bold text-gray-800">{category.title}</h2>
              </div>
              
              <div className="space-y-3">
                {category.items.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-all ${
                      completedItems[item.id]
                        ? 'bg-green-50 border-2 border-green-300'
                        : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {completedItems[item.id] ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-400" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className={`font-medium ${
                        completedItems[item.id] ? 'text-green-800 line-through' : 'text-gray-800'
                      }`}>
                        {item.text}
                      </p>
                      <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${
                        item.level === '推奨' || item.level === '継続' ? 'bg-blue-100 text-blue-700' :
                        item.level === '挑戦' ? 'bg-orange-100 text-orange-700' :
                        item.level === '目標' ? 'bg-purple-100 text-purple-700' :
                        item.level === '新規' ? 'bg-pink-100 text-pink-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {item.level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* おすすめアクション */}
        <div className="mt-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl shadow-lg p-6 text-white">
          <h3 className="text-xl font-bold mb-3">💡 今週から始められること</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              Go Workshop Conferenceでの経験を技術ブログに書く
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              日常業務で使えるシンプルなCLIツールをGoで作ってみる
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              興味のあるOSSプロジェクトを3つリストアップ
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-white rounded-full"></span>
              次のカンファレンスでLT応募を検討
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
