# ai_loop.py
"""AI 推理和滑鼠控制的主要循環"""

from __future__ import annotations

import time
import threading
import queue
import traceback
import random
from typing import List, Tuple, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

import numpy as np
import mss
import win32api


from .inference import preprocess_image, postprocess_outputs, non_max_suppression, PIDController
from win_utils import send_mouse_move, is_key_pressed, get_ddxoft_statistics
from .smart_tracker import SmartTracker

if TYPE_CHECKING:
    from .config import Config
    import onnxruntime as ort


@dataclass
class LoopState:
    """AI 循環的狀態管理"""
    last_pid_update: float = 0.0
    last_ddxoft_stats_time: float = 0.0

    last_method_check_time: float = 0.0
    cached_mouse_move_method: str = 'mouse_event'
    
    # 間隔設定
    pid_check_interval: float = 1.0
    ddxoft_stats_interval: float = 30.0
    method_check_interval: float = 2.0

    # 貝塞爾/幽靈目標狀態
    bezier_curve_scalar: float = 0.0
    target_locked: bool = False
    # 智慧追蹤器狀態
    smart_tracker: SmartTracker | None = None
    tracker_last_time: float = 0.0
    tracker_last_target_box: tuple | None = None  # 用於偵測目標切換

def _update_crosshair_position(config: Config, half_width: int, half_height: int) -> None:
    """更新十字準心位置"""
    if config.fov_follow_mouse:
        try:
            x, y = win32api.GetCursorPos()
            config.crosshairX, config.crosshairY = x, y
        except (OSError, RuntimeError):
            config.crosshairX, config.crosshairY = half_width, half_height
    else:
        config.crosshairX, config.crosshairY = half_width, half_height


def _clear_queues(boxes_queue: queue.Queue, confidences_queue: queue.Queue) -> None:
    """清空檢測隊列"""
    try:
        while not boxes_queue.empty():
            boxes_queue.get_nowait()
        while not confidences_queue.empty():
            confidences_queue.get_nowait()
    except queue.Empty:
        pass
    boxes_queue.put([])
    confidences_queue.put([])


def _calculate_detection_region(
    config: Config, 
    crosshair_x: int, 
    crosshair_y: int
) -> Dict[str, int]:
    """計算檢測區域"""
    # 使用可調整的偵測範圍（正方形邊長），並遵守限制：
    # - 不得小於 fov_size
    # - 不得大於螢幕高度
    detection_size = int(getattr(config, 'detect_range_size', config.height))
    detection_size = max(int(config.fov_size), min(int(config.height), detection_size))
    half_detection_size = detection_size // 2

    region_left = max(0, crosshair_x - half_detection_size)
    region_top = max(0, crosshair_y - half_detection_size)
    region_width = max(0, min(detection_size, config.width - region_left))
    region_height = max(0, min(detection_size, config.height - region_top))

    return {
        "left": region_left,
        "top": region_top,
        "width": region_width,
        "height": region_height,
    }


def _filter_boxes_by_fov(
    boxes: List[List[float]], 
    confidences: List[float],
    crosshair_x: int, 
    crosshair_y: int, 
    fov_size: int
) -> Tuple[List[List[float]], List[float]]:
    """FOV 過濾：只保留與 FOV 框有交集的人物框"""
    if not boxes:
        return [], []
    
    fov_half = fov_size // 2
    fov_left = crosshair_x - fov_half
    fov_top = crosshair_y - fov_half
    fov_right = crosshair_x + fov_half
    fov_bottom = crosshair_y + fov_half
    
    filtered_boxes = []
    filtered_confidences = []
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        # 矩形交集檢測
        if (x1 < fov_right and x2 > fov_left and 
            y1 < fov_bottom and y2 > fov_top):
            filtered_boxes.append(box)
            if i < len(confidences):
                filtered_confidences.append(confidences[i])
    
    return filtered_boxes, filtered_confidences


def _find_closest_target(
    boxes: List[List[float]], 
    confidences: List[float],
    crosshair_x: int, 
    crosshair_y: int
) -> Tuple[List[List[float]], List[float]]:
    """單目標模式 - 只保留離準心最近的一個目標"""
    if not boxes:
        return [], []
    
    closest_box = None
    min_distance_sq = float('inf')
    closest_confidence = 0.5
    
    for i, box in enumerate(boxes):
        abs_x1, abs_y1, abs_x2, abs_y2 = box
        box_center_x = (abs_x1 + abs_x2) * 0.5
        box_center_y = (abs_y1 + abs_y2) * 0.5
        dx = box_center_x - crosshair_x
        dy = box_center_y - crosshair_y
        distance_sq = dx * dx + dy * dy
        
        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            closest_box = box
            closest_confidence = confidences[i] if i < len(confidences) else 0.5
    
    if closest_box:
        return [closest_box], [closest_confidence]
    return [], []





def _calculate_aim_target(
    box: List[float], 
    aim_part: str, 
    head_height_ratio: float
) -> Tuple[float, float]:
    """計算瞄準點座標"""
    abs_x1, abs_y1, abs_x2, abs_y2 = box
    box_w, box_h = abs_x2 - abs_x1, abs_y2 - abs_y1
    box_center_x = abs_x1 + box_w * 0.5
    
    if aim_part == "head":
        target_x = box_center_x
        target_y = abs_y1 + box_h * head_height_ratio * 0.5
    else:  # "body"
        target_x = box_center_x
        head_h = box_h * head_height_ratio
        target_y = (abs_y1 + head_h + abs_y2) * 0.5
    
    return target_x, target_y


def _process_aiming(
    config: Config,
    boxes: List[List[float]],
    crosshair_x: int,
    crosshair_y: int,
    pid_x: PIDController,
    pid_y: PIDController,
    mouse_method: str,
    state: LoopState,
    current_time: float
) -> None:
    """處理瞄準邏輯 (包含卡爾曼濾波預判和幽靈目標/貝塞爾曲線偏移)"""
    aim_part = config.aim_part
    head_height_ratio = config.head_height_ratio
    
    valid_targets = []
    for box in boxes:
        target_x, target_y = _calculate_aim_target(box, aim_part, head_height_ratio)
        moveX = target_x - crosshair_x
        moveY = target_y - crosshair_y
        distance_sq = moveX * moveX + moveY * moveY
        valid_targets.append((distance_sq, target_x, target_y, box))

    if valid_targets:
        valid_targets.sort(key=lambda x: x[0])
        _, target_x, target_y, box = valid_targets[0]
        
        # === 智慧追蹤器預判 ===
        tracker_enabled = getattr(config, 'tracker_enabled', False)
        if tracker_enabled:
            # 初始化追蹤器
            if state.smart_tracker is None:
                state.smart_tracker = SmartTracker(
                    smoothing_factor=getattr(config, 'tracker_smoothing_factor', 0.5),
                    stop_threshold=getattr(config, 'tracker_stop_threshold', 20.0)
                )
                state.tracker_last_time = current_time
            else:
                # 更新追蹤器參數（如果用戶調整了）
                state.smart_tracker.alpha = getattr(config, 'tracker_smoothing_factor', 0.5)
                state.smart_tracker.stop_threshold = getattr(config, 'tracker_stop_threshold', 20.0)
            
            # 偵測目標切換（當目標框大幅變化時重置追蹤器）
            current_box_tuple = tuple(box)
            if state.tracker_last_target_box is not None:
                last_box = state.tracker_last_target_box
                # 計算框中心距離變化
                last_cx = (last_box[0] + last_box[2]) * 0.5
                last_cy = (last_box[1] + last_box[3]) * 0.5
                curr_cx = (box[0] + box[2]) * 0.5
                curr_cy = (box[1] + box[3]) * 0.5
                box_distance_sq = (curr_cx - last_cx) ** 2 + (curr_cy - last_cy) ** 2
                # 如果目標跳躍超過 200 像素，認為是新目標
                if box_distance_sq > 40000:  # 200^2
                    state.smart_tracker.reset()
            state.tracker_last_target_box = current_box_tuple
            
            # 計算時間間隔
            dt = current_time - state.tracker_last_time
            if dt <= 0:
                dt = 0.01  # 防止 dt 為 0
            state.tracker_last_time = current_time
            
            # 更新追蹤器（輸入當前觀測位置）
            state.smart_tracker.update(target_x, target_y, dt)
            
            # 取得預測位置
            prediction_time = getattr(config, 'tracker_prediction_time', 0.05)
            pred_x, pred_y = state.smart_tracker.get_predicted_position(prediction_time)
            
            # 更新視覺化資料（供 overlay 使用）
            config.tracker_current_x = target_x
            config.tracker_current_y = target_y
            config.tracker_predicted_x = pred_x
            config.tracker_predicted_y = pred_y
            config.tracker_has_prediction = True
            
            # 使用預測位置取代原始目標位置
            target_x, target_y = pred_x, pred_y
        else:
            # 追蹤器未啟用，重置狀態
            config.tracker_has_prediction = False
            if state.smart_tracker is not None:
                state.smart_tracker.reset()
                state.smart_tracker = None
        
        # 計算誤差
        errorX = target_x - crosshair_x
        errorY = target_y - crosshair_y

        # 幽靈目標 / 貝塞爾曲線偏移邏輯
        if getattr(config, 'bezier_curve_enabled', False):
            # 如果剛鎖定目標，隨機生成一個偏移方向
            if not state.target_locked:
                state.target_locked = True
                # 生成 -1.0 到 1.0 之間的隨機純量
                state.bezier_curve_scalar = random.uniform(-1.0, 1.0)
            
            strength = float(getattr(config, 'bezier_curve_strength', 0.35))
            # 計算垂直向量 (-y, x)
            perp_x = -errorY
            perp_y = errorX
            
            # 施加偏移: 垂直向量 * 強度 * 隨機純量
            # 隨著 errorX/Y (距離) 變小，偏移量也會自然變小，實現收斂
            offset_x = perp_x * strength * state.bezier_curve_scalar
            offset_y = perp_y * strength * state.bezier_curve_scalar
            
            # 將偏移加到誤差上，PID 會試圖修正這個「假」誤差，從而走出弧線
            errorX += offset_x
            errorY += offset_y
        else:
            state.target_locked = False

        dx, dy = pid_x.update(errorX), pid_y.update(errorY)
        move_x, move_y = int(round(dx)), int(round(dy))
        
        if move_x != 0 or move_y != 0:
            send_mouse_move(move_x, move_y, method=mouse_method)
    else:
        state.target_locked = False
        pid_x.reset()
        pid_y.reset()


def _update_queues(
    overlay_boxes_queue: queue.Queue,
    overlay_confidences_queue: queue.Queue,
    boxes: List[List[float]],
    confidences: List[float],
    auto_fire_queue: queue.Queue | None = None,
) -> None:
    """更新檢測結果隊列，並向自動開火單獨佇列廣播"""
    try:
        if overlay_boxes_queue.full():
            overlay_boxes_queue.get_nowait()
        if overlay_confidences_queue.full():
            overlay_confidences_queue.get_nowait()
    except queue.Empty:
        pass

    overlay_boxes_queue.put(boxes)
    overlay_confidences_queue.put(confidences)

    if auto_fire_queue is not None:
        try:
            if auto_fire_queue.full():
                auto_fire_queue.get_nowait()
        except queue.Empty:
            pass
        # 將檢測框單獨複製給自動開火，避免被其他消費者取走
        auto_fire_queue.put(list(boxes))


def ai_logic_loop(
    config: Config,
    model: ort.InferenceSession,
    model_type: str,
    overlay_boxes_queue: queue.Queue,
    overlay_confidences_queue: queue.Queue,
    auto_fire_boxes_queue: queue.Queue | None = None,
) -> None:
    """
    AI 推理和滑鼠控制的主要循環
    
    Args:
        config: 配置實例
        model: ONNX 模型會話
        model_type: 模型類型（目前僅支持 'onnx'）
        boxes_queue: 檢測框隊列
        confidences_queue: 置信度隊列
    """
    screen_capture = mss.mss()
    input_name = model.get_inputs()[0].name
        
    pid_x = PIDController(config.pid_kp_x, config.pid_ki_x, config.pid_kd_x)
    pid_y = PIDController(config.pid_kp_y, config.pid_ki_y, config.pid_kd_y)
    
    # 狀態管理
    state = LoopState(cached_mouse_move_method=config.mouse_move_method)
    
    # 預計算常用值
    half_width = config.width // 2
    half_height = config.height // 2

    # 延遲/性能統計（EMA）
    ema_total = 0.0
    ema_capture = 0.0
    ema_pre = 0.0
    ema_inf = 0.0
    ema_post = 0.0
    last_stats_print = time.perf_counter()

    while config.Running:
        try:
            loop_start = time.perf_counter()
            current_time = time.time()
            
            # 定期更新 PID 參數
            if current_time - state.last_pid_update > state.pid_check_interval:
                pid_x.Kp, pid_x.Ki, pid_x.Kd = config.pid_kp_x, config.pid_ki_x, config.pid_kd_x
                pid_y.Kp, pid_y.Ki, pid_y.Kd = config.pid_kp_y, config.pid_ki_y, config.pid_kd_y
                state.last_pid_update = current_time
            
            # 檢查滑鼠移動方式變更
            if current_time - state.last_method_check_time > state.method_check_interval:
                new_method = config.mouse_move_method
                if new_method != state.cached_mouse_move_method:
                    state.cached_mouse_move_method = new_method
                state.last_method_check_time = current_time
            
            # 更新十字準心位置
            _update_crosshair_position(config, half_width, half_height)

            # 檢查是否正在瞄準
            is_aiming = bool(getattr(config, 'always_aim', False)) or any(is_key_pressed(k) for k in config.AimKeys)
            
            if not config.AimToggle or (not config.keep_detecting and not is_aiming):
                _clear_queues(overlay_boxes_queue, overlay_confidences_queue)
                # 清除追蹤預測視覺化
                config.tracker_has_prediction = False
                time.sleep(0.05)
                continue
                
            crosshair_x, crosshair_y = config.crosshairX, config.crosshairY
            region = _calculate_detection_region(config, crosshair_x, crosshair_y)
            
            if region['width'] <= 0 or region['height'] <= 0:
                continue

            # 擷取螢幕
            try:
                # 優化: 使用 frombuffer 避免額外拷貝，並直接 reshape
                sct_img = screen_capture.grab(region)
                game_frame = np.frombuffer(sct_img.bgra, dtype=np.uint8).reshape((sct_img.height, sct_img.width, 4))
            except mss.exception.ScreenShotError:
                continue
            if game_frame.size == 0: 
                continue
            
            # AI 模型推理
            t0 = time.perf_counter()
            input_tensor = preprocess_image(game_frame, config.model_input_size)
            t1 = time.perf_counter()
            try:
                t2 = time.perf_counter()
                outputs = model.run(None, {input_name: input_tensor})
                t3 = time.perf_counter()
                boxes, confidences = postprocess_outputs(
                    outputs, region['width'], region['height'], 
                    config.model_input_size, config.min_confidence, 
                    region['left'], region['top']
                )
                boxes, confidences = non_max_suppression(boxes, confidences)
                t4 = time.perf_counter()
            except (RuntimeError, ValueError) as e:
                print(f"ONNX 推理錯誤: {e}")
                continue

            # FOV 過濾
            boxes, confidences = _filter_boxes_by_fov(
                boxes, confidences, crosshair_x, crosshair_y, config.fov_size
            )

            # 單目標模式
            if config.single_target_mode:
                boxes, confidences = _find_closest_target(
                    boxes, confidences, crosshair_x, crosshair_y
                )



            # 瞄準處理
            if is_aiming and boxes:
                _process_aiming(
                    config, boxes, crosshair_x, crosshair_y,
                    pid_x, pid_y, state.cached_mouse_move_method,
                    state, current_time
                )
            else:
                state.target_locked = False
                # 清除追蹤預測視覺化
                config.tracker_has_prediction = False
                pid_x.reset()
                pid_y.reset()

            # 更新隊列
            _update_queues(
                overlay_boxes_queue,
                overlay_confidences_queue,
                boxes,
                confidences,
                auto_fire_queue=auto_fire_boxes_queue,
            )

            # 延遲/占用優化：用「總處理時間」扣掉 sleep，避免額外延遲疊加
            desired_interval = config.detect_interval if is_aiming else getattr(config, 'idle_detect_interval', config.detect_interval)
            elapsed = time.perf_counter() - loop_start
            remaining = desired_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

            # 延遲統計（預設關閉）
            if getattr(config, 'enable_latency_stats', False):
                alpha = float(getattr(config, 'latency_stats_alpha', 0.2))
                total_ms = (time.perf_counter() - loop_start) * 1000.0
                cap_ms = (t0 - loop_start) * 1000.0
                pre_ms = (t1 - t0) * 1000.0
                inf_ms = (t3 - t2) * 1000.0 if 't3' in locals() else 0.0
                post_ms = (t4 - t3) * 1000.0 if 't4' in locals() else 0.0

                ema_total = ema_total * (1 - alpha) + total_ms * alpha
                ema_capture = ema_capture * (1 - alpha) + cap_ms * alpha
                ema_pre = ema_pre * (1 - alpha) + pre_ms * alpha
                ema_inf = ema_inf * (1 - alpha) + inf_ms * alpha
                ema_post = ema_post * (1 - alpha) + post_ms * alpha

                now = time.perf_counter()
                if now - last_stats_print >= float(getattr(config, 'latency_stats_interval', 1.0)):
                    print(
                        f"[Latency EMA] total={ema_total:.1f}ms "
                        f"cap={ema_capture:.1f}ms pre={ema_pre:.1f}ms "
                        f"inf={ema_inf:.1f}ms post={ema_post:.1f}ms "
                        f"interval={desired_interval*1000:.0f}ms"
                    )
                    last_stats_print = now
                    
        except Exception as e:
            print(f"[AI Loop Error] {e}")
            traceback.print_exc()
            time.sleep(1.0)
