import numpy as np
from typing import Tuple, Optional

class SmartTracker:
    """
    智慧追蹤器
    特點：
    1. 對抖動進行平滑 (Smoothing)
    2. 對急停/變向進行瞬間反應 (Zero-Lag Reset)
    3. 拋棄物理慣性假設
    """
    
    def __init__(self, smoothing_factor: float = 0.5, stop_threshold: float = 20.0, position_deadzone: float = 4.0):
        """
        Args:
            smoothing_factor (0.0~1.0): 
                越大越滑順但延遲越高，越小反應越快但越抖。
                建議 0.3 ~ 0.6 之間調整。
            stop_threshold: 
                速度低於此值(像素/秒)強制歸零，防止微小漂移。
            position_deadzone:
                位置死區(像素)。當準心與目標距離小於此值時停止修正，
                避免在目標附近產生震盪。建議 3~5 像素。
        """
        self.alpha = smoothing_factor
        self.stop_threshold = stop_threshold
        self.position_deadzone = position_deadzone
        
        # 狀態
        self.last_x = None
        self.last_y = None
        self.vx = 0.0
        self.vy = 0.0
        self.initialized = False
        
    def update(self, measured_x: float, measured_y: float, dt: float) -> Tuple[float, float, float, float]:
        """更新位置並計算速度"""
        if not self.initialized or dt <= 0:
            self.last_x = measured_x
            self.last_y = measured_y
            self.vx = 0.0
            self.vy = 0.0
            self.initialized = True
            return measured_x, measured_y, 0.0, 0.0

        # 1. 計算原始瞬時速度 (Raw Velocity)
        raw_vx = (measured_x - self.last_x) / dt
        raw_vy = (measured_y - self.last_y) / dt
        
        # 2. 智慧濾波邏輯
        # 檢查變向：如果新速度和舊速度方向相反 (點積 < 0)，說明目標正在 ADAD 或急停
        # 這時候我們不要平滑，直接採納新速度（犧牲平滑換取反應速度）
        dot_product = raw_vx * self.vx + raw_vy * self.vy
        
        if dot_product < 0:
            # 偵測到變向/急停：重置速度，不進行平滑
            self.vx = raw_vx
            self.vy = raw_vy
        else:
            # 同向移動：使用指數移動平均 (EMA) 來消除 YOLO 的抖動
            self.vx = self.vx * self.alpha + raw_vx * (1 - self.alpha)
            self.vy = self.vy * self.alpha + raw_vy * (1 - self.alpha)
            
        # 3. 強制靜止 (Deadzone)
        # 如果速度很小，直接歸零，解決準心在靜止目標上微動的問題
        if abs(self.vx) < self.stop_threshold: self.vx = 0
        if abs(self.vy) < self.stop_threshold: self.vy = 0

        # 更新位置記錄
        self.last_x = measured_x
        self.last_y = measured_y
        
        return measured_x, measured_y, self.vx, self.vy

    def is_in_deadzone(self, target_x: float, target_y: float, crosshair_x: float, crosshair_y: float) -> bool:
        """
        檢查準心是否已在目標的死區內
        
        Args:
            target_x, target_y: 目標位置
            crosshair_x, crosshair_y: 準心位置（通常是畫面中心）
            
        Returns:
            True 如果在死區內，不需要修正
        """
        if self.position_deadzone <= 0:
            return False
            
        dx = target_x - crosshair_x
        dy = target_y - crosshair_y
        distance = np.sqrt(dx * dx + dy * dy)
        
        return distance < self.position_deadzone
    
    def get_corrected_move(self, target_x: float, target_y: float, 
                           crosshair_x: float, crosshair_y: float) -> Tuple[float, float]:
        """
        計算修正後的移動量，考慮位置死區
        
        Args:
            target_x, target_y: 目標位置
            crosshair_x, crosshair_y: 準心位置
            
        Returns:
            (move_x, move_y): 修正後的移動量。如果在死區內則返回 (0, 0)
        """
        dx = target_x - crosshair_x
        dy = target_y - crosshair_y
        
        # 位置死區檢查：距離太近就不動
        distance = np.sqrt(dx * dx + dy * dy)
        if distance < self.position_deadzone:
            return 0.0, 0.0
            
        return dx, dy

    def get_predicted_position(self, prediction_time: float) -> Tuple[float, float]:
        """預測未來位置"""
        if not self.initialized:
            return 0.0, 0.0
            
        # 簡單線性預測：位置 + 速度 * 時間
        pred_x = self.last_x + self.vx * prediction_time
        pred_y = self.last_y + self.vy * prediction_time
        
        return pred_x, pred_y
        
    def reset(self):
        self.last_x = None
        self.last_y = None
        self.vx = 0.0
        self.vy = 0.0
        self.initialized = False
