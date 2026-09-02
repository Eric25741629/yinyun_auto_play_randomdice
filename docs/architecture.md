# System Architecture

```mermaid
flowchart TD
    U[User starts newmain.py] --> M[load_models.AI_model]
    M --> M1[MobileNetV3<br/>64-class dice classifier]
    M --> M2[YOLO wave model]
    M --> M3[EasyOCR Traditional Chinese]

    U --> C[Two emulator controllers]
    C --> A[Attacker thread<br/>dicer_att]
    C --> S[Support thread<br/>dicer_sup]

    A --> P1[prepareGame]
    S --> P2[prepareGame]
    P1 --> V1[gameview + str_tool]
    P2 --> V2[gameview + str_tool]
    V1 --> Q[(Queue<br/>room number / sync signal)]
    V2 --> Q

    A --> G1[control_game.play]
    S --> G2[control_game.play]
    G1 --> I1[img_tools / Fast_Screenshot]
    G2 --> I2[img_tools / Fast_Screenshot]
    I1 --> F[Screen image]
    I2 --> F

    F --> R[Region crop & preprocessing]
    R --> D[Dice detection<br/>pic_tranform.py]
    R --> O[OCR text detection<br/>tools.py]
    R --> W[Wave recognition<br/>YOLO + OCR fallback]

    D --> B[3 x 5 board state]
    B --> K[calculate.py<br/>matching & connection calculation]
    K --> ACT[click / swipe / level-up actions]
    O --> ST[Screen state machine<br/>view.py]
    W --> ST
    ST --> ACT
    ACT --> E[ADB / uiautomator2]
    E --> C
```

## Data flow

```text
Android Emulator
      │
      ▼
Screenshot capture (ADB / Windows window capture)
      │
      ▼
ROI crop + image preprocessing
      │
      ├── MobileNetV3 → dice type / level
      ├── EasyOCR     → UI text / room number / buttons
      └── YOLO        → wave number
      │
      ▼
Structured game state + 3×5 board matrix
      │
      ▼
State machine + matching / connection calculation
      │
      ▼
ADB / uiautomator2 click, swipe, launch, input
```
