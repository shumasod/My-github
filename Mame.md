<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
    <!-- 背景 -->
    <rect width="800" height="400" fill="#f8f9fa"/>
    
    <!-- センサーユニット -->
    <g transform="translate(50,50)">
        <rect x="0" y="0" width="200" height="120" rx="10" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
        <text x="100" y="30" text-anchor="middle" fill="#1565c0" font-size="16">センサーユニット</text>
        
        <!-- 人感センサー -->
        <rect x="20" y="50" width="70" height="50" rx="5" fill="#bbdefb" stroke="#1565c0" stroke-width="1"/>
        <text x="55" y="80" text-anchor="middle" font-size="12">人感センサー</text>
        
        <!-- 距離センサー -->
        <rect x="110" y="50" width="70" height="50" rx="5" fill="#bbdefb" stroke="#1565c0" stroke-width="1"/>
        <text x="145" y="80" text-anchor="middle" font-size="12">距離センサー</text>
    </g>

    <!-- Arduino制御ユニット -->
    <rect x="300" y="70" width="200" height="80" rx="10" fill="#fff3e0" stroke="#e65100" stroke-width="2"/>
    <text x="400" y="110" text-anchor="middle" fill="#e65100" font-size="16">Arduino Nano</text>
    
    <!-- アラートユニット -->
    <g transform="translate(550,50)">
        <rect x="0" y="0" width="200" height="120" rx="10" fill="#f3e5f5" stroke="#4a148c" stroke-width="2"/>
        <text x="100" y="30" text-anchor="middle" fill="#4a148c" font-size="16">アラートユニット</text>
        
        <!-- ブザー -->
        <rect x="20" y="50" width="70" height="50" rx="5" fill="#e1bee7" stroke="#4a148c" stroke-width="1"/>
        <text x="55" y="80" text-anchor="middle" font-size="12">ブザー</text>
        
        <!-- LED -->
        <rect x="110" y="50" width="70" height="50" rx="5" fill="#e1bee7" stroke="#4a148c" stroke-width="1"/>
        <text x="145" y="80" text-anchor="middle" font-size="12">LED</text>
    </g>

    <!-- 接続線 -->
    <!-- センサー → Arduino -->
    <path d="M 250,110 L 300,110" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- Arduino → アラート -->
    <path d="M 500,110 L 550,110" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- 矢印マーカー定義 -->
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
        </marker>
    </defs>

    <!-- システム説明 -->
    <g transform="translate(50,250)">
        <rect width="700" height="120" rx="10" fill="#ffffff" stroke="#999" stroke-width="1"/>
        <text x="20" y="30" font-size="14">システム仕様：</text>
        <text x="40" y="55" font-size="12">・電源：単三電池×3（約1ヶ月動作）</text>
        <text x="40" y="75" font-size="12">・検知範囲：最大3m</text>
        <text x="40" y="95" font-size="12">・アラート：音声警告 + LED表示（緑：待機、黄：警戒、赤：警報）</text>
    </g>
</svg>
