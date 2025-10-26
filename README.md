<div align="center">
   
[![GitHub stars](https://img.shields.io/github/stars/iishong0w0/Axiom-AI?style=social)](https://github.com/iishong0w0/Axiom-AI/stargazers)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-PolyForm--Noncommercial%201.0.0-blueviolet.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/iishong0w0/Axiom-AI)
![Repo Size](https://img.shields.io/github/repo-size/iishong0w0/Axiom-AI)

<h1>Axiom AI</h1>
<p>Adaptive aim assistance powered by computer vision to support gamers who need it most.</p>

<p>
  <a href="https://github.com/iishong0w0/Axiom-AI/releases/latest"><strong>Download Latest Release</strong></a>
  ·
  <a href="https://discord.gg/h4dEh3b8Bt">Discord Community</a>
</p>

<img src="https://raw.githubusercontent.com/iisHong0w0/Axiom-AI/refs/heads/main/%E9%9D%A2%E6%9D%BF.png" alt="Control panel screenshot" width="720" />

<p><strong>If this project helps you, please give us a ⭐ Star!</strong></p>

</div>

---

**Languages**: [English](#english) | [中文](#中文)

---

# English

## Table of Contents
- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Tech Stack & Dependencies](#tech-stack--dependencies)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration Reference](#configuration-reference)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Community & Support](#community--support)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)
- [Acknowledgements](#acknowledgements)

## Overview

Axiom AI is a computer vision–driven overlay and mouse control suite designed to deliver real-time target detection and aim assistance for players who need accessibility support. By combining YOLO-based object detection with configurable control logic, the project helps users achieve smoother, more reliable input in demanding gaming scenarios.

**Designed for players who:**

- live with physical disabilities such as hand tremors, Parkinson's disease, or paralysis
- experience visual impairments including color blindness, low vision, or nystagmus
- face cognitive challenges such as ADHD, autism, anxiety disorders, or spatial perception issues
- manage chronic medical conditions or fatigue
- are limited by lower-end hardware, peripherals, or cloud gaming latency
- play in constrained environments with reduced space or ergonomics
- are beginners learning core aiming skills or returning to games after a break

> ⚠️ **Important:** Axiom AI is licensed under the PolyForm Noncommercial License 1.0.0. Commercial usage of any kind is strictly prohibited.

## Feature Highlights

### AI-Assisted Target Acquisition
- Ultralytics YOLOv8 detection pipeline with support for ONNX (`.onnx`) and PyTorch (`.pt`) models
- Real-time inference accelerated by ONNX Runtime (DirectML) or PyTorch CPU backends
- Configurable confidence thresholds, detection regions, and FOV radius
- Optional single-target mode to prioritise the nearest enemy

### Intelligent Aiming Controls
- Tunable PID controller for smooth, predictable mouse movement on both axes
- Separate X/Y gain, integral, and derivative settings for fine-grained adjustments
- Multiple aim modes (head, body, mixed) plus customisable aim and toggle hotkeys
- Hardware-level and Windows API mouse movement methods to match different games

### Visual Feedback & User Experience
- PyQt6 overlay with detection boxes, confidence readouts, and FOV indicator
- Real-time status panel showing FPS, latency, and detection statistics
- Configurable colour coding for different target areas and overlay elements

### Performance & Reliability
- CPU affinity, process/thread priority controls, and detection interval tuning
- Optimised ONNX runtime configuration for minimal inference latency
- Performance mode presets to balance responsiveness and resource usage

### Quality-of-Life Enhancements
- Auto-fire with adjustable delay, interval, and target preference
- Sound alerts for target acquisition, with frequency, duration, and cooldown settings
- Keep-detecting mode, model presets, multilingual interface (English / 中文), and more

## Tech Stack & Dependencies

- **Language:** Python 3.11+
- **GUI & Overlay:** PyQt6
- **Computer Vision:** Ultralytics YOLOv8, OpenCV, ONNX Runtime (DirectML), PyTorch (CPU)
- **Screen Capture:** MSS
- **Numerical Computing:** NumPy, TorchVision, Torchaudio
- **System Integration:** pywin32, psutil, custom `ddxoft.dll`
- **Packaging & Distribution:** PyInstaller (optional), Windows batch launcher

See [`requirements.txt`](requirements.txt) for the full list of pinned packages.

## System Requirements

### Minimum
- **OS:** Windows 10 64-bit
- **Python:** 3.11+
- **RAM:** 16 GB
- **GPU:** NVIDIA GTX 1060 / AMD RX 580 or equivalent
- **Storage:** 500 MB free space

### Recommended
- **OS:** Windows 11 64-bit
- **Python:** 3.11+
- **RAM:** 32 GB or higher
- **GPU:** NVIDIA RTX 3060 or better
- **Storage:** 1 GB free space

## Installation

### Quick Install (Recommended)

1. **Download the latest release** from the [Releases page](https://github.com/iishong0w0/Axiom-AI/releases/latest) and extract the ZIP archive.
2. **Install Python 3.11** using the bundled `python-3.11.0-amd64.exe`. Ensure that **Add python.exe to PATH** is selected during installation.
3. **Launch Axiom AI** by double-clicking `啟動Launcher.bat`. The launcher will install all dependencies automatically on first run.
4. Wait for the application window and overlay to appear. Subsequent launches will reuse the cached environment.

### Manual Setup (Developers)

```bash
# Clone the repository
git clone https://github.com/iishong0w0/Axiom-AI.git
cd Axiom-AI

# (Optional) create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd src
python main.py
```

### Verify Your Setup

After installation you should see:

- ✅ The main control panel window
- ✅ Overlay elements (FOV circle, detection boxes, confidence values)
- ✅ Status panel displaying FPS and detection statistics

If errors appear in the console, consult the [Troubleshooting](#troubleshooting) section below.

## Quick Start

1. **Launch the application** from the `src` directory: `python main.py`.
2. **Select an AI model** in the settings panel. Place `.onnx` or `.pt` files in `src/模型/` if you want to use custom models (default: `Roblox.onnx`).
3. **Adjust detection settings** such as FOV size, confidence threshold, aim part, and single-target mode to match your game.
4. **Configure hotkeys** for aiming, toggling, and auto-fire. The default toggle key is `Insert`.
5. **Start detecting** by pressing `Insert`. Hold one of the configured aim keys to engage the PID-driven mouse movement.
6. **Observe visual feedback** on the overlay to confirm detection boxes, confidence, and status information.

### Advanced Tips

- Tune `Kp`, `Ki`, and `Kd` for each axis to balance responsiveness and smoothness. Start with small changes (±0.02).
- Lower the detection interval (e.g., `0.01 → 0.005`) for faster reactions, or increase it to reduce CPU usage.
- Switch between `mouse_event` and `ddxoft` mouse methods to match your game's input requirements.
- Enable performance mode by raising process/thread priority if you experience latency.

## Configuration Reference

All runtime settings are stored in `src/config.json` and can also be adjusted through the GUI.

```jsonc
{
  "fov_size": 222,
  "min_confidence": 0.11,
  "aim_part": "head",
  "single_target_mode": true,
  "keep_detecting": true,
  "fov_follow_mouse": true,
  "pid_kp_x": 0.26,
  "pid_ki_x": 0.0,
  "pid_kd_x": 0.0,
  "pid_kp_y": 0.26,
  "pid_ki_y": 0.0,
  "pid_kd_y": 0.0,
  "AimKeys": [1, 6, 2],
  "aim_toggle_key": 45,
  "auto_fire_interval": 0.08,
  "auto_fire_target_part": "both",
  "detect_interval": 0.01,
  "cpu_optimization": true,
  "process_priority": "high",
  "thread_priority": "high",
  "mouse_move_method": "mouse_event",
  "mouse_click_method": "ddxoft",
  "enable_sound_alert": false,
  "show_status_panel": true
}
```

### Key Options

| Option | Description | Default |
| --- | --- | --- |
| `fov_size` | Field-of-view radius in pixels | `222` |
| `min_confidence` | Smallest confidence score for detections | `0.11` |
| `aim_part` | Target preference (`head`, `body`, `both`) | `head` |
| `AimKeys` | Mouse buttons that activate aiming | `[1, 6, 2]` |
| `auto_fire_interval` | Delay between auto-fire shots (seconds) | `0.08` |
| `detect_interval` | Sleep time between detection loops (seconds) | `0.01` |
| `mouse_move_method` | Mouse movement backend (`mouse_event`, `ddxoft`) | `mouse_event` |
| `show_status_panel` | Toggle the FPS / status overlay | `true` |

### Environment Variables

No environment variables are required. All configuration is handled via `config.json` or the in-app settings UI.

## Project Structure

```
Axiom-AI_Aimbot/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── config.json
│   ├── inference.py
│   ├── overlay.py
│   ├── settings_gui.py
│   ├── status_panel.py
│   ├── config_manager.py
│   ├── preset_manager.py
│   ├── language_manager.py
│   ├── language_data.py
│   ├── scaling_warning_dialog.py
│   ├── win_utils.py
│   ├── ddxoft.dll
│   └── 模型/
│       └── *.onnx, *.pt
├── requirements.txt
├── LICENSE
├── README.md
├── 啟動Launcher.bat
├── 常見問題FAQ.txt
├── 面板.png
├── python-3.11.0-amd64.exe
└── index.html
```

## Troubleshooting

#### Application does not start
- Confirm that Python 3.11+ is installed and added to PATH.
- Run from a terminal to capture errors: `cd src && python main.py`.
- Reinstall Python if the launcher still fails to create the environment.

#### ModuleNotFoundError
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`.
- Ensure the virtual environment (if used) is activated before running the app.

#### No detection or low FPS
- Verify that a model file exists under `src/模型/`.
- Reduce FOV size or raise the detection interval to balance performance.
- Close resource-intensive background applications and update GPU drivers.

#### Mouse does not move
- Check that your aim keys match the configured values.
- Try switching `mouse_move_method` between `mouse_event` and `ddxoft`.
- Run the application as Administrator if your game requires elevated privileges.
- Increase `pid_kp_x` / `pid_kp_y` for stronger corrective movement.

#### Overlay not visible
- Ensure `show_fov` and `show_boxes` remain enabled in the settings.
- Use Windowed or Borderless display modes and Alt+Tab to refresh the overlay.
- Disable competing overlays (Windows Game Bar, GPU overlays, etc.).

#### Access denied or permission errors
- Run the launcher or `main.py` with Administrator rights.
- Confirm that antivirus or anti-cheat software is not blocking `ddxoft.dll`.

#### High CPU usage
- Increase `detect_interval` (e.g., from `0.01` to `0.03`).
- Reduce FOV size or disable `keep_detecting`.
- Hide the status panel if you do not need live metrics.

## Contributing

Contributions are welcome! To propose changes:

```bash
# Fork and clone your copy
git clone https://github.com/YOUR_USERNAME/Axiom-AI.git
cd Axiom-AI

# Create a feature branch
git checkout -b feature/your-feature-name

# Install dependencies and make your changes
pip install -r requirements.txt

# Commit and push
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

**Guidelines**
- Follow the existing Python style (PEP 8) and project architecture.
- Update documentation or language strings when adding new features.
- Test on multiple Windows versions and hardware configurations when possible.
- Ensure changes remain compliant with the PolyForm Noncommercial License.

## License

This project is distributed under the **PolyForm Noncommercial License 1.0.0**. You may modify and share the software for personal, educational, or research purposes, but **any commercial use is forbidden**. Review the full terms in the [LICENSE](LICENSE) file or on the [PolyForm Project website](https://polyformproject.org/licenses/noncommercial/1.0.0/).

## Community & Support

- **Discord:** [Join the community](https://discord.gg/h4dEh3b8Bt)
- **GitHub Issues:** [Report bugs or request features](https://github.com/iishong0w0/Axiom-AI/issues)
- **Email:** [iis20160512@gmail.com](mailto:iis20160512@gmail.com)

## FAQ

**Is this a cheat or hack?**  
Axiom AI is built as an accessibility tool. Use it responsibly and respect each game's terms of service.

**Will I get banned for using it?**  
No guarantee can be made for online games. Use at your own risk.

**Can I use it in competitive play?**  
Competitive or tournament environments may forbid external assistance. Understand the rules before using it.

**Which games are supported?**  
Axiom AI is model-agnostic. Provide a suitable YOLO model for your target game (default model ships for Roblox).

**How do I train my own model?**  
Create a dataset and train a YOLOv8 model. The [Ultralytics documentation](https://docs.ultralytics.com) contains a full workflow.

**Why is detection slow?**  
Try reducing FOV size, raising the detection interval, closing background tasks, or using a lighter model.

## Disclaimer

This software is provided "as is" without warranty of any kind. The developers are not responsible for:

- Any consequences arising from the use of this software
- Account bans, penalties, or disciplinary actions
- Hardware or software damage
- Violations of third-party terms of service

You are solely responsible for ensuring that your usage complies with all applicable laws and agreements.

## Acknowledgements

- **Ultralytics YOLOv8** for the detection framework
- **ONNX Runtime** for efficient inference backends
- **PyQt6** for the overlay and UI foundation
- **Community contributors** for feedback, models, and testing support

---

# 中文

## 目錄
- [項目概述](#項目概述)
- [核心功能](#核心功能)
- [技術棧與依賴](#技術棧與依賴)
- [系統要求](#系統要求)
- [安裝指南](#安裝指南)
- [快速開始](#快速開始)
- [配置參考](#配置參考)
- [項目結構](#項目結構)
- [故障排除](#故障排除)
- [貢獻指南](#貢獻指南)
- [許可證](#許可證)
- [社群與支持](#社群與支持)
- [常見問題](#常見問題)
- [免責聲明](#免責聲明)
- [致謝](#致謝)

## 項目概述

Axiom AI 是一款基於計算機視覺的覆蓋層與鼠標控制系統，可提供實時的目標檢測與瞄準輔助，專為需要輔助功能的玩家設計。透過 YOLO 對象檢測與可調式控制邏輯的結合，協助使用者在高強度的遊戲情境中維持平穩而可靠的操作。

**適合以下族群使用：**

- 具有手部顫抖、帕金森氏症、癱瘓等身體障礙的玩家
- 經歷色盲、弱視、眼球震顫等視覺障礙的玩家
- 面對 ADHD、自閉症、焦慮、空間感知障礙等認知挑戰的玩家
- 長期處於慢性疲勞或其他醫療狀況的玩家
- 受限於低階硬體、週邊設備或雲端延遲的玩家
- 在狹小空間或不佳的人體工學環境下遊玩的玩家
- 想要學習瞄準技巧的新手或重返遊戲的玩家

> ⚠️ **重要提醒：** 本項目採用 PolyForm 非商業許可證 1.0.0，嚴禁任何形式的商業使用。

## 核心功能

### AI 輔助檢測
- Ultralytics YOLOv8 檢測流程，支援 ONNX（`.onnx`）與 PyTorch（`.pt`）模型
- 透過 ONNX Runtime（DirectML）或 PyTorch CPU 後端進行實時推理
- 可調式置信度門檻、檢測區域與視野（FOV）半徑
- 單目標模式可優先鎖定最近的敵人

### 智能瞄準控制
- 可調式 PID 控制器，提供平滑且可預期的滑鼠移動
- X/Y 軸獨立的比例、積分、微分參數，便於精細調整
- 多種瞄準模式（頭部、身體、混合）與自訂瞄準/切換熱鍵
- 同時支援 Windows API 與硬體層級的滑鼠輸入方法

### 視覺回饋與使用體驗
- PyQt6 覆蓋層顯示檢測框、置信度與 FOV 指示
- 即時狀態面板呈現 FPS、延遲與偵測統計
- 可自訂不同瞄準區域與介面元素的顏色

### 性能與穩定性
- CPU 親和性、行程/執行緒優先權與檢測間隔皆可調節
- 最佳化的 ONNX 運行時設定，降低推理延遲
- 性能模式可在反應速度與資源使用間取得平衡

### 便利性功能
- 自動射擊，可自訂延遲、間隔與目標偏好
- 目標偵測聲響提示，可調整頻率與持續時間
- 持續偵測模式、模型預設、多語系介面（English / 中文）等

## 技術棧與依賴

- **程式語言：** Python 3.11+
- **GUI 與覆蓋層：** PyQt6
- **計算機視覺：** Ultralytics YOLOv8、OpenCV、ONNX Runtime（DirectML）、PyTorch（CPU）
- **畫面擷取：** MSS
- **數值計算：** NumPy、TorchVision、Torchaudio
- **系統整合：** pywin32、psutil、自訂 `ddxoft.dll`
- **打包與分發：** PyInstaller（可選）、Windows 批次啟動器

完整依賴清單請參閱 [`requirements.txt`](requirements.txt)。

## 系統要求

### 最低配備
- **作業系統：** Windows 10 64 位元
- **Python：** 3.11+
- **記憶體：** 16 GB
- **顯示卡：** NVIDIA GTX 1060 / AMD RX 580 或同級
- **儲存空間：** 500 MB 可用空間

### 建議配備
- **作業系統：** Windows 11 64 位元
- **Python：** 3.11+
- **記憶體：** 32 GB 以上
- **顯示卡：** NVIDIA RTX 3060 或更高階
- **儲存空間：** 1 GB 可用空間

## 安裝指南

### 方式一：快速安裝（推薦）

1. 前往 [版本發布頁](https://github.com/iishong0w0/Axiom-AI/releases/latest) 下載最新 ZIP 並解壓縮。
2. 使用隨附的 `python-3.11.0-amd64.exe` 安裝 Python 3.11，記得勾選 **Add python.exe to PATH**。
3. 雙擊 `啟動Launcher.bat` 啟動 Axiom AI，首度執行會自動安裝所有依賴套件。
4. 等待主視窗與覆蓋層顯示，之後啟動將沿用既有環境。

### 方式二：手動安裝（開發者）

```bash
# 下載專案
git clone https://github.com/iishong0w0/Axiom-AI.git
cd Axiom-AI

# （可選）建立並啟用虛擬環境
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動應用程式
cd src
python main.py
```

### 成功驗證

完成安裝後應看到：

- ✅ 主控制面板視窗
- ✅ 覆蓋層顯示 FOV、檢測框與置信度
- ✅ 狀態面板呈現 FPS 與偵測資訊

若終端機出現錯誤訊息，請參考下方的[故障排除](#故障排除)章節。

## 快速開始

1. **啟動程式：** 在 `src` 目錄執行 `python main.py`。
2. **選擇模型：** 在設定面板挑選 `.onnx` 或 `.pt` 模型；自訂模型請放入 `src/模型/`（預設為 `Roblox.onnx`）。
3. **調整偵測參數：** 根據遊戲情境調整 FOV 大小、置信度、瞄準部位與單目標模式。
4. **設定熱鍵：** 自訂瞄準、切換與自動射擊按鍵，預設切換鍵為 `Insert`。
5. **啟動偵測：** 按下 `Insert` 啟用 AI 偵測，按住設定的瞄準鍵即可啟動 PID 驅動的滑鼠移動。
6. **確認視覺回饋：** 確認覆蓋層是否正確顯示檢測框、置信度與狀態資訊。

### 進階建議

- 微調 `Kp`、`Ki`、`Kd` 時請以 ±0.02 為單位逐步調整，兼顧反應與平滑度。
- 降低偵測間隔（如 `0.01 → 0.005`）可加快反應；提高值則能減少 CPU 負載。
- 視遊戲需求切換 `mouse_event` 與 `ddxoft` 滑鼠輸入模式。
- 若遇到延遲，可提高行程/執行緒優先權開啟性能模式。

## 配置參考

所有設定皆會儲存在 `src/config.json`，亦可於 GUI 即時調整。

```jsonc
{
  "fov_size": 222,                    // 視野半徑（像素）
  "min_confidence": 0.11,             // 最低置信度
  "aim_part": "head",                // 瞄準部位：head / body / both
  "single_target_mode": true,         // 是否鎖定最近目標
  "keep_detecting": true,             // 是否持續偵測
  "fov_follow_mouse": true,           // FOV 是否跟隨滑鼠
  "pid_kp_x": 0.26,
  "pid_ki_x": 0.0,
  "pid_kd_x": 0.0,
  "pid_kp_y": 0.26,
  "pid_ki_y": 0.0,
  "pid_kd_y": 0.0,
  "AimKeys": [1, 6, 2],               // 瞄準鍵（虛擬鍵碼）
  "aim_toggle_key": 45,               // 切換鍵（Insert）
  "auto_fire_interval": 0.08,         // 自動射擊間隔（秒）
  "auto_fire_target_part": "both",   // 自動射擊偏好
  "detect_interval": 0.01,            // 偵測迴圈延遲（秒）
  "cpu_optimization": true,
  "process_priority": "high",
  "thread_priority": "high",
  "mouse_move_method": "mouse_event",
  "mouse_click_method": "ddxoft",
  "enable_sound_alert": false,
  "show_status_panel": true
}
```

### 主要選項

| 選項 | 說明 | 預設值 |
| --- | --- | --- |
| `fov_size` | 視野半徑（像素） | `222` |
| `min_confidence` | 判定命中的最低置信度 | `0.11` |
| `aim_part` | 瞄準部位（`head` / `body` / `both`） | `head` |
| `AimKeys` | 觸發瞄準的滑鼠按鍵 | `[1, 6, 2]` |
| `auto_fire_interval` | 自動射擊間隔（秒） | `0.08` |
| `detect_interval` | 偵測迴圈延遲（秒） | `0.01` |
| `mouse_move_method` | 滑鼠移動方式（`mouse_event` / `ddxoft`） | `mouse_event` |
| `show_status_panel` | 是否顯示 FPS / 狀態面板 | `true` |

### 環境變量

本項目無需額外的環境變量，所有參數皆可透過 `config.json` 或介面設定完成。

## 項目結構

```
Axiom-AI_Aimbot/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── config.json
│   ├── inference.py
│   ├── overlay.py
│   ├── settings_gui.py
│   ├── status_panel.py
│   ├── config_manager.py
│   ├── preset_manager.py
│   ├── language_manager.py
│   ├── language_data.py
│   ├── scaling_warning_dialog.py
│   ├── win_utils.py
│   ├── ddxoft.dll
│   └── 模型/
│       └── *.onnx, *.pt
├── requirements.txt
├── LICENSE
├── README.md
├── 啟動Launcher.bat
├── 常見問題FAQ.txt
├── 面板.png
├── python-3.11.0-amd64.exe
└── index.html
```

## 故障排除

#### 程式無法啟動
- 確認已安裝並將 Python 3.11+ 加入 PATH。
- 以終端機執行 `cd src && python main.py` 以取得錯誤訊息。
- 重新安裝 Python，確保啟動器可建立環境。

#### 出現 ModuleNotFoundError
- 執行 `pip install -r requirements.txt --upgrade` 重新安裝依賴。
- 若使用虛擬環境，請先啟用後再啟動程式。

#### 沒有偵測或 FPS 過低
- 確認 `src/模型/` 內存在模型檔案。
- 減少 FOV 或提高偵測間隔來調整效能。
- 關閉耗資源程式並更新顯示卡驅動。

#### 滑鼠沒有移動
- 檢查瞄準鍵是否與設定一致。
- 在 `mouse_event` 與 `ddxoft` 之間切換以符合遊戲需求。
- 以系統管理員身分執行程式，避免權限受限。
- 提高 `pid_kp_x` / `pid_kp_y` 增強修正力度。

#### 覆蓋層未顯示
- 確認設定中 `show_fov` 與 `show_boxes` 為啟用狀態。
- 使用視窗或無邊框模式，並透過 Alt+Tab 重繪覆蓋層。
- 停用 Windows Game Bar 等其他覆蓋層。

#### 存取遭拒或權限錯誤
- 以系統管理員權限執行啟動器或 `main.py`。
- 確認防毒或反外掛軟體未封鎖 `ddxoft.dll`。

#### CPU 使用率過高
- 將 `detect_interval` 提高至 `0.03` 等較大數值。
- 減少 FOV 或停用 `keep_detecting`。
- 若無需即時監控，可關閉狀態面板。

## 貢獻指南

歡迎任何形式的貢獻！建議流程如下：

```bash
# Fork 並克隆你的儲存庫
git clone https://github.com/YOUR_USERNAME/Axiom-AI.git
cd Axiom-AI

# 建立功能分支
git checkout -b feature/your-feature-name

# 安裝依賴並進行修改
pip install -r requirements.txt

# 提交並推送
git add .
git commit -m "feat: 描述你的變更"
git push origin feature/your-feature-name
```

**開發建議**
- 遵循現有 Python 風格（PEP 8）與專案結構。
- 新功能請同步更新文件與多語系字串。
- 盡可能在不同 Windows 版本與硬體上測試。
- 所有改動必須符合 PolyForm 非商業許可證的要求。

## 許可證

本專案採用 **PolyForm 非商業許可證 1.0.0**。您可以在個人、教育或研究領域中修改與分享本軟體，但 **禁止任何商業用途**。詳情請參閱 [LICENSE](LICENSE) 或前往 [PolyForm 官方網站](https://polyformproject.org/licenses/noncommercial/1.0.0/)。

## 社群與支持

- **Discord：** [加入社群](https://discord.gg/h4dEh3b8Bt)
- **GitHub Issues：** [回報問題或提案新功能](https://github.com/iishong0w0/Axiom-AI/issues)
- **電子郵件：** [iis20160512@gmail.com](mailto:iis20160512@gmail.com)

## 常見問題

**這是不是外掛？**  
Axiom AI 定位為輔助工具，請在符合遊戲規範的前提下負責使用。

**會被封鎖帳號嗎？**  
無法保證所有線上遊戲的安全性，請自行評估風險。

**可以用在競技賽事上嗎？**  
競技或錦標賽通常禁止外部輔助工具，使用前務必了解相關規定。

**支援哪些遊戲？**  
Axiom AI 與模型無綁定，可搭配任何訓練完成的 YOLO 模型（預設模型支援 Roblox）。

**如何訓練自己的模型？**  
自行蒐集資料集並依照 [Ultralytics 說明文件](https://docs.ultralytics.com) 訓練 YOLOv8 模型即可。

**偵測速度很慢怎麼辦？**  
可減少 FOV、提高偵測間隔、關閉背景程式或改用更輕量的模型。

## 免責聲明

本軟體以「現狀」提供，不保證任何功能或安全性。開發者不對以下情況負責：

- 使用本軟體所導致的任何結果
- 線上遊戲中的帳號封鎖或處罰
- 硬體或軟體損壞
- 違反第三方服務條款

使用者需自行確保其使用行為符合相關法律與服務協議。

## 致謝

- **Ultralytics YOLOv8**：提供卓越的對象檢測框架
- **ONNX Runtime**：帶來高效率的推理後端
- **PyQt6**：構築覆蓋層與使用者介面
- **社群貢獻者**：提供模型、測試與寶貴回饋
