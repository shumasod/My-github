graph TB
    subgraph "入力デバイス"
        A[USBカメラ] -->|画像データ| D
        B[PIRモーションセンサー] -->|動き検知| D
        C[超音波距離センサー] -->|距離データ| D
    end

    subgraph "メイン処理システム"
        D[Raspberry Pi] --> E[OpenCV画像処理]
        E --> F{検知判定エンジン}
        F -->|閾値判定| G[アラート管理]
    end

    subgraph "アラート出力"
        G -->|音声再生| H[スピーカー]
        G -->|LED制御| I[警告LED]
        G -->|画面表示| J[ディスプレイ]
        G -->|Push通知| K[スマートフォン]
    end

    style D fill:#bbf,stroke:#333,stroke-width:4px
    style E fill:#fbf,stroke:#333,stroke-width:4px
    style F fill:#ff9,stroke:#333,stroke-width:4px
    style G fill:#bfb,stroke:#333,stroke-width:4px
