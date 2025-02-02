graph TB
    subgraph "センサーユニット"
        A[人感センサー] -->|動き検知| C
        B[距離センサー] -->|距離データ| C
    end

    subgraph "制御ユニット"
        C[Arduino Nano] -->|判定処理| D[アラート制御]
    end

    subgraph "アラート"
        D -->|音声| E[圧電ブザー]
        D -->|光| F[LED]
    end

    style C fill:#bbf,stroke:#333,stroke-width:4px
    style D fill:#bfb,stroke:#333,stroke-width:4px
