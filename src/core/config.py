# config.py
"""配置管理模組 - 使用類型提示實現類型安全的配置"""

from __future__ import annotations

import ctypes
import json
import os
from typing import List, Dict, Any


def _get_screen_size() -> tuple[int, int]:
    """獲取螢幕解析度"""
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


class Config:
    """主配置類 - Axiom 的所有配置項目
    
    包含所有可配置的參數，包括：
    - 螢幕和檢測區域設定
    - 模型和推理參數
    - PID 控制器參數
    - 瞄準和自動開火設定
    - 顯示和性能選項
    - 音效提示系統
    
    所有屬性都有類型提示，以確保類型安全。
    配置可透過 to_dict/from_dict 方法與 JSON 檔案互轉。
    """
    
    def __init__(self) -> None:
        # 自動獲取螢幕解析度
        self.width, self.height = _get_screen_size()
        
        self.center_x: int = self.width // 2
        self.center_y: int = self.height // 2
        
        # 全螢幕檢測
        self.capture_width: int = self.width
        self.capture_height: int = self.height
        self.capture_left: int = 0
        self.capture_top: int = 0
        self.crosshairX: int = self.width // 2
        self.crosshairY: int = self.height // 2
        self.region: Dict[str, int] = {
            "top": 0, "left": 0, 
            "width": self.width, "height": self.height
        }

        # 程式執行狀態
        self.Running: bool = True
        self.AimToggle: bool = True
        
        # ONNX 模型相關設定
        self.model_input_size: int = 640
        self.model_path: str = os.path.join('Model', 'roblox.onnx')
        self.current_provider: str = "DmlExecutionProvider"
        # 混合運算：在 DirectML 不支援的算子時自動回退到 CPU
        # ONNX Runtime providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
        self.dml_cpu_fallback: bool = True

        # 瞄準與顯示設定
        self.AimKeys: List[int] = [0x01, 0x06, 0x02]  # 左鍵 + X2鍵 + 右鍵
        self.fov_size: int = 222

        # AI 偵測範圍（正方形邊長）：與 fov_size 分離，但不得小於 fov_size，且不得大於螢幕高度
        # 預設取螢幕高度（等同舊版行為）
        self.detect_range_size: int = self.height
        self.show_confidence: bool = True
        self.min_confidence: float = 0.11
        self.aim_part: str = "head"
        
        # 單目標模式
        self.single_target_mode: bool = True  # 一次最多檢測一個離準心最近的敵人
        
        # 瞄準曲線平滑（貝塞爾）
        self.bezier_curve_enabled: bool = False
        self.bezier_curve_strength: float = 0.35  # 0~1，越大彎曲越明顯
        self.bezier_curve_steps: int = 4          # 分段越多越平滑（>=2）

        # 智慧追蹤預判設定（取代卡爾曼）
        self.tracker_enabled: bool = False           # 啟用智慧追蹤預判
        self.tracker_prediction_time: float = 0.025   # 預測時間（秒）
        self.tracker_smoothing_factor: float = 0.66   # 速度平滑係數 (0~1)
        self.tracker_stop_threshold: float = 10.0    # 低速歸零閾值（像素/秒）
        self.tracker_show_prediction: bool = True    # 顯示預判視覺化

        # 追蹤器預測資料（由 ai_loop 更新，overlay 讀取）
        self.tracker_predicted_x: float = 0.0        # 預測的 X 座標
        self.tracker_predicted_y: float = 0.0        # 預測的 Y 座標
        self.tracker_current_x: float = 0.0          # 當前觀測的 X 座標
        self.tracker_current_y: float = 0.0          # 當前觀測的 Y 座標
        self.tracker_has_prediction: bool = False    # 是否有有效預測

        # 免責聲明同意狀態
        self.disclaimer_agreed: bool = False

        # 首次啟動設置精靈
        self.first_run_complete: bool = False
        
        # 頭部和身體區域占比設定
        self.head_width_ratio: float = 0.38    # 頭部寬度占檢測框寬度的比例
        self.head_height_ratio: float = 0.26   # 頭部高度占檢測框高度的比例
        self.body_width_ratio: float = 0.87    # 身體寬度占檢測框寬度的比例
        
        # PID 控制器參數 (分離 X 和 Y 軸)
        self.pid_kp_x: float = 0.26      # 水平 P: 比例 - 主要影響反應速度
        self.pid_ki_x: float = 0.0       # 水平 I: 積分 - 修正靜態誤差
        self.pid_kd_x: float = 0.0       # 水平 D: 微分 - 抑制抖動與過衝
        self.pid_kp_y: float = 0.26      # 垂直 P: 比例
        self.pid_ki_y: float = 0.0       # 垂直 I: 積分
        self.pid_kd_y: float = 0.0       # 垂直 D: 微分

        # 滑鼠控制方式
        self.mouse_move_method: str = "mouse_event"  # 滑鼠移動方式（預設使用安全的 mouse_event）
        self.mouse_click_method: str = "mouse_event" # 滑鼠點擊方式
        self.arduino_com_port: str = ""              # Arduino Leonardo COM 埠

        # Xbox 360 虛擬手把設定
        self.xbox_sensitivity: float = 1.0          # 手把靈敏度 (0.1~5.0)
        self.xbox_deadzone: float = 0.05            # 手把死區 (0.0~0.5)
        self.xbox_auto_connect: bool = True          # 選擇 xbox 時自動連線

        # 檢測設定
        # 偵測節流：
        # - detect_interval: 進入瞄準/需要即時反應時的間隔
        # - idle_detect_interval: 未瞄準但 keep_detecting=True 時的間隔（降低占用）
        self.detect_interval: float = 0.02       # 秒，預設 20ms
        self.idle_detect_interval: float = 0.05  # 秒，預設 50ms
        self.aim_toggle_key: int = 45       # Insert 鍵
        self.auto_fire_key2: int = 0x04     # 滑鼠中鍵
        
        # 自動開槍
        self.auto_fire_key: int = 0x06           # 滑鼠X2鍵
        self.always_auto_fire: bool = False      # 不按自動開槍鍵也持續自動開槍
        self.auto_fire_delay: float = 0.0        # 無延遲
        self.auto_fire_interval: float = 0.08    # 射擊間隔
        self.auto_fire_target_part: str = "both" # 可選: "head", "body", "both"

        # 保持檢測功能
        self.keep_detecting: bool = True   # 啟用保持檢測
        self.always_aim: bool = False      # 不按瞄準鍵也執行自動瞄準
        self.fov_follow_mouse: bool = True # FOV 跟隨鼠標

        # 顯示開關
        self.show_fov: bool = True
        self.show_boxes: bool = True
        self.show_detect_range: bool = False
        self.show_status_panel: bool = True
        self.show_console: bool = True  # 顯示終端視窗

        # 主題設定
        self.dark_mode: bool = False  # 深色主題

        # Acrylic 毛玻璃效果專用設置
        self.enable_acrylic: bool = True
        self.acrylic_window_alpha: int = 187  # 0-255, 視窗底層不透明度 (約 73%)
        self.acrylic_element_alpha: int = 25   # 0-255, UI 元素不透明度 (約 10%)
        
        # 優化：性能相關設置
        self.performance_mode: bool = True  # 預設啟用性能模式
        self.max_queue_size: int = 1        # 減少隊列大小，降低延遲

        # 延遲/性能統計（預設關閉，避免輸出干擾）
        self.enable_latency_stats: bool = False
        self.latency_stats_interval: float = 1.0  # 秒
        self.latency_stats_alpha: float = 0.2     # EMA 平滑係數 (0~1)

        # 供統計使用的時間戳（由不同線程更新）
        self.last_detection_time: float = 0.0
        self.last_overlay_update_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """將可儲存的配置轉為字典"""
        return {
            'fov_size': self.fov_size,
            'detect_range_size': self.detect_range_size,
            'model_path': self.model_path,
            'model_input_size': self.model_input_size,
            'current_provider': self.current_provider,
            'dml_cpu_fallback': self.dml_cpu_fallback,
            'pid_kp_x': self.pid_kp_x,
            'pid_ki_x': self.pid_ki_x,
            'pid_kd_x': self.pid_kd_x,
            'pid_kp_y': self.pid_kp_y,
            'pid_ki_y': self.pid_ki_y,
            'pid_kd_y': self.pid_kd_y,
            'aim_part': self.aim_part,
            'AimKeys': self.AimKeys,
            'auto_fire_key': self.auto_fire_key,
            'always_auto_fire': self.always_auto_fire,
            'auto_fire_delay': self.auto_fire_delay,
            'auto_fire_interval': self.auto_fire_interval,
            'auto_fire_target_part': self.auto_fire_target_part,
            'min_confidence': self.min_confidence,
            'show_confidence': self.show_confidence,
            'detect_interval': self.detect_interval,
            'idle_detect_interval': self.idle_detect_interval,
            'keep_detecting': self.keep_detecting,
            'always_aim': self.always_aim,
            'fov_follow_mouse': self.fov_follow_mouse,
            'aim_toggle_key': self.aim_toggle_key,
            'auto_fire_key2': self.auto_fire_key2,
            'AimToggle': self.AimToggle,
            'show_fov': self.show_fov,
            'show_boxes': self.show_boxes,
            'show_detect_range': self.show_detect_range,
            'show_status_panel': self.show_status_panel,
            'single_target_mode': self.single_target_mode,
            'head_width_ratio': self.head_width_ratio,
            'head_height_ratio': self.head_height_ratio,
            'body_width_ratio': self.body_width_ratio,
            'performance_mode': self.performance_mode,
            'max_queue_size': self.max_queue_size,
            'enable_latency_stats': self.enable_latency_stats,
            'latency_stats_interval': self.latency_stats_interval,
            'latency_stats_alpha': self.latency_stats_alpha,

            'mouse_move_method': self.mouse_move_method,
            'mouse_click_method': self.mouse_click_method,
            'arduino_com_port': self.arduino_com_port,
            'xbox_sensitivity': self.xbox_sensitivity,
            'xbox_deadzone': self.xbox_deadzone,
            'xbox_auto_connect': self.xbox_auto_connect,
            'show_console': self.show_console,

            'bezier_curve_enabled': self.bezier_curve_enabled,
            'bezier_curve_strength': self.bezier_curve_strength,
            'bezier_curve_steps': self.bezier_curve_steps,
            'disclaimer_agreed': self.disclaimer_agreed,
            'first_run_complete': self.first_run_complete,

            'tracker_enabled': self.tracker_enabled,
            'tracker_prediction_time': self.tracker_prediction_time,
            'tracker_smoothing_factor': self.tracker_smoothing_factor,
            'tracker_stop_threshold': self.tracker_stop_threshold,
            'tracker_show_prediction': self.tracker_show_prediction,

            'dark_mode': self.dark_mode,

            'enable_acrylic': self.enable_acrylic,
            'acrylic_window_alpha': self.acrylic_window_alpha,
            'acrylic_element_alpha': self.acrylic_element_alpha,
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """從字典載入配置"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


def save_config(config_instance: Config, filepath: str = 'config.json') -> bool:
    """
    將配置儲存到 JSON 檔案
    
    Args:
        config_instance: Config 實例
        filepath: 儲存路徑
        
    Returns:
        是否成功儲存
    """
    try:
        # 先讀取現有的 config.json，保留不在 Config 類中的欄位（如 language）
        existing_data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                existing_data = {}
        
        # 將新的配置資料合併到現有資料上（新值覆蓋舊值，但保留額外欄位）
        data = config_instance.to_dict()
        existing_data.update(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print("設定已儲存")
        return True
    except OSError as e:
        print(f"設定儲存失敗 (IO錯誤): {e}")
        return False
    except (TypeError, ValueError) as e:
        print(f"設定儲存失敗 (序列化錯誤): {e}")
        return False


def load_config(config_instance: Config, filepath: str = 'config.json') -> bool:
    """
    從 JSON 檔案載入配置
    
    Args:
        config_instance: Config 實例
        filepath: 載入路徑
        
    Returns:
        是否成功載入
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config_instance.from_dict(data)
        
        # 向後兼容：確保檢測間隔在合理範圍內 (1-100ms)
        _validate_detect_interval(config_instance)

        # 向後兼容：確保閒置檢測間隔在合理範圍內 (5-500ms)
        _validate_idle_detect_interval(config_instance)
        
        # 向後兼容：修正滑鼠移動方式
        _validate_mouse_method(config_instance)

        # 向後兼容：確保偵測範圍在合理範圍內
        _validate_detect_range_size(config_instance)
        
        print("設定檔已載入")
        return True
        
    except FileNotFoundError:
        print("未找到設定檔，使用預設值")
        return False
    except json.JSONDecodeError as e:
        print(f"設定載入失敗 (JSON 格式錯誤): {e}")
        return False
    except OSError as e:
        print(f"設定載入失敗 (IO錯誤): {e}")
        return False


def _validate_detect_interval(config: Config) -> None:
    """驗證並修正檢測間隔"""
    detect_interval_ms = config.detect_interval * 1000
    if detect_interval_ms < 1:
        config.detect_interval = 0.001  # 1ms
        print("[配置修正] 檢測間隔過小，已調整為 1ms")
    elif detect_interval_ms > 100:
        config.detect_interval = 0.1  # 100ms
        print("[配置修正] 檢測間隔過大，已調整為 100ms")


def _validate_idle_detect_interval(config: Config) -> None:
    """驗證並修正閒置檢測間隔"""
    idle_ms = getattr(config, 'idle_detect_interval', 0.05) * 1000
    if idle_ms < 5:
        config.idle_detect_interval = 0.005
        print("[配置修正] 閒置檢測間隔過小，已調整為 5ms")
    elif idle_ms > 500:
        config.idle_detect_interval = 0.5
        print("[配置修正] 閒置檢測間隔過大，已調整為 500ms")


def _validate_mouse_method(config: Config) -> None:
    """驗證並修正滑鼠移動方式"""
    # 移除不支援的 hardware 方式
    if config.mouse_move_method == 'hardware':
        config.mouse_move_method = 'mouse_event'
    
    # ddxoft 模式下，點擊方式自動使用 mouse_event
    if config.mouse_move_method == 'ddxoft':
        if config.mouse_click_method != 'mouse_event':
            config.mouse_click_method = 'mouse_event'


def _validate_detect_range_size(config: Config) -> None:
    """驗證並修正 AI 偵測範圍（正方形邊長）

    規則：
    - 最小不得小於 fov_size
    - 最大不得大於螢幕高度
    """
    try:
        raw = int(getattr(config, 'detect_range_size', config.height))
    except (TypeError, ValueError):
        raw = int(config.height)

    min_size = int(getattr(config, 'fov_size', 0) or 0)
    max_size = int(getattr(config, 'height', raw) or raw)
    if max_size <= 0:
        max_size = raw if raw > 0 else 1

    clamped = max(min_size, min(max_size, raw))
    config.detect_range_size = clamped
