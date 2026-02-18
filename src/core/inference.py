# inference.py
"""AI 推理模組 - 圖像預處理、後處理和 PID 控制器"""

from __future__ import annotations

from typing import List, Tuple, Any

import cv2
import numpy as np
import numpy.typing as npt


class PIDController:
    """PID 控制器 - 用於平滑瞄準移動
    
    實現比例-積分-微分 (PID) 控制算法，用於計算滑鼠移動量。
    支援 X/Y 軸獨立設定，并包含動態調整 P 參數的功能。
    
    Attributes:
        Kp: 比例係數，控制反應速度
        Ki: 積分係數，修正靜態誤差
        Kd: 微分係數，抑制抖動與過衝
    """
    
    def __init__(self, Kp: float, Ki: float, Kd: float) -> None:
        self.Kp = Kp  # 比例 Proportional
        self.Ki = Ki  # 積分 Integral
        self.Kd = Kd  # 微分 Derivative
        self.reset()

    def reset(self) -> None:
        """重置控制器狀態"""
        self.integral: float = 0.0
        self.previous_error: float = 0.0

    def update(self, error: float) -> float:
        """
        根據當前誤差計算控制輸出
        
        Args:
            error: 當前誤差 (例如, target_x - current_x)
            
        Returns:
            控制量 (例如, 滑鼠應移動的量)
        """
        # 積分項
        self.integral += error
        
        # 微分項
        derivative = error - self.previous_error
        
        # 調整P參數的響應曲線
        adjusted_kp = self._calculate_adjusted_kp(self.Kp)
        
        # 計算輸出
        output = (adjusted_kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        
        # 更新上一次的誤差
        self.previous_error = error
        
        return output
    
    def _calculate_adjusted_kp(self, kp: float) -> float:
        """計算動態調整後的 P 參數
        
        實現非線性的 P 參數響應曲線：
        - 0% ~ 50%: 線性增長，保持原始比例
        - 50% ~ 100%: 加速增長，最終放大到 200%
        
        此設計讓低靈敏度時更平滑，高靈敏度時更積極。
        
        Args:
            kp: 原始 P 參數值 (0.0 ~ 1.0)
            
        Returns:
            調整後的 P 參數值 (0.0 ~ 2.0)
        """
        if kp <= 0.5:
            return kp
        else:
            # 當kp=0.5時，輸出=0.5；當kp=1.0時，輸出=2.0
            return 0.5 + (kp - 0.5) * 3.0


def preprocess_image(image: npt.NDArray[np.uint8], model_input_size: int) -> npt.NDArray[np.float32]:
    """
    預處理圖像以適配 ONNX 模型
    
    Args:
        image: 輸入圖像 (BGR 格式)
        model_input_size: 模型輸入尺寸
        
    Returns:
        預處理後的張量 [1, 3, H, W]
    """
    # 優化 1: 使用 cvtColor 處理 BGRA -> BGR
    # 這比 numpy slicing (image[:, :, :3]) 更快，且直接產生連續記憶體
    if image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # 優化 2: 顯式調整大小並使用 INTER_NEAREST (最近鄰插值)
    # 當從小圖 (如 222) 放大到大圖 (如 640) 時，預設的線性插值非常耗時
    # INTER_NEAREST 速度極快，能大幅降低 pre-process 時間
    if image.shape[0] != model_input_size or image.shape[1] != model_input_size:
        image = cv2.resize(image, (model_input_size, model_input_size), interpolation=cv2.INTER_NEAREST)

    # blob: [1, 3, H, W] float32
    # 因為已經 resize 過，這裡的 resize 動作會被跳過或開銷極小
    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1.0 / 255.0,
        size=(model_input_size, model_input_size),
        swapRB=True,
        crop=False,
    )

    # 確保連續記憶體布局（避免某些後端額外拷貝）
    return np.ascontiguousarray(blob, dtype=np.float32)


def postprocess_outputs(
    outputs: List[Any], 
    original_width: int, 
    original_height: int, 
    model_input_size: int, 
    min_confidence: float, 
    offset_x: int = 0, 
    offset_y: int = 0
) -> Tuple[List[List[float]], List[float]]:
    """
    後處理 ONNX 模型輸出
    
    Args:
        outputs: 模型輸出
        original_width: 原始圖像寬度
        original_height: 原始圖像高度
        model_input_size: 模型輸入尺寸
        min_confidence: 最小置信度閾值
        offset_x: X 軸偏移
        offset_y: Y 軸偏移
        
    Returns:
        (boxes, confidences) 元組
    """
    predictions = outputs[0][0].T
    
    # 向量化過濾：先篩選高置信度的檢測
    conf_mask = predictions[:, 4] >= min_confidence
    filtered_predictions = predictions[conf_mask]
    
    if len(filtered_predictions) == 0:
        return [], []
    
    # 向量化計算邊界框
    scale_x = original_width / model_input_size
    scale_y = original_height / model_input_size
    
    cx, cy, w, h = (filtered_predictions[:, 0], filtered_predictions[:, 1], 
                    filtered_predictions[:, 2], filtered_predictions[:, 3])
    
    x1 = (cx - w / 2) * scale_x + offset_x
    y1 = (cy - h / 2) * scale_y + offset_y
    x2 = (cx + w / 2) * scale_x + offset_x
    y2 = (cy + h / 2) * scale_y + offset_y

    boxes = np.stack([x1, y1, x2, y2], axis=1).tolist()
    confidences = filtered_predictions[:, 4].tolist()

    return boxes, confidences


def non_max_suppression(
    boxes: List[List[float]], 
    confidences: List[float], 
    iou_threshold: float = 0.4
) -> Tuple[List[List[float]], List[float]]:
    """
    非極大值抑制
    
    Args:
        boxes: 邊界框列表
        confidences: 置信度列表
        iou_threshold: IoU 閾值
        
    Returns:
        (filtered_boxes, filtered_confidences) 元組
    """
    if len(boxes) == 0:
        return [], []
    
    boxes_arr = np.array(boxes)
    confidences_arr = np.array(confidences)
    areas = (boxes_arr[:, 2] - boxes_arr[:, 0]) * (boxes_arr[:, 3] - boxes_arr[:, 1])
    order = confidences_arr.argsort()[::-1]
    
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)
        if len(order) == 1:
            break
        
        xx1 = np.maximum(boxes_arr[i, 0], boxes_arr[order[1:], 0])
        yy1 = np.maximum(boxes_arr[i, 1], boxes_arr[order[1:], 1])
        xx2 = np.minimum(boxes_arr[i, 2], boxes_arr[order[1:], 2])
        yy2 = np.minimum(boxes_arr[i, 3], boxes_arr[order[1:], 3])
        
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        intersection = w * h
        union = areas[i] + areas[order[1:]] - intersection
        iou = intersection / union
        
        order = order[1:][iou <= iou_threshold]
        
    return boxes_arr[keep].tolist(), confidences_arr[keep].tolist()
