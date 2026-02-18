# auto_fire.py
"""自動開火功能模組 - 處理自動射擊邏輯"""

from __future__ import annotations

import queue
import time
import traceback
import logging
from typing import TYPE_CHECKING

from win_utils import is_key_pressed, send_mouse_click

if TYPE_CHECKING:
    from .config import Config


def auto_fire_loop(config: Config, boxes_queue: queue.Queue) -> None:
    """自動開火功能的獨立循環
    
    監聽自動開火按鍵，當準心位於檢測到的目標範圍內時自動觸發射擊。
    支援頭部、身體和全部區域三種射擊模式。
    
    Args:
        config: 配置實例，包含自動開火相關設定
        boxes_queue: 檢測框隊列，從 AI 推理循環獲取目標位置
    
    Note:
        此函數應在獨立的 daemon 線程中運行
    """
    last_key_state = False
    delay_start_time = None
    last_fire_time = 0
    cached_boxes = []
    last_box_update = 0
    logger = logging.getLogger(__name__)
    
    BOX_UPDATE_INTERVAL = 1 / 60  # 60Hz更新頻率
    
    # 緩存按鍵配置
    auto_fire_key = config.auto_fire_key
    auto_fire_key2 = getattr(config, 'auto_fire_key2', None)
    last_key_update = 0
    key_update_interval = 0.5  # 每0.5秒檢查一次按鍵配置變化
    
    while config.Running:
        try:
            current_time = time.time()
            
            # 定期更新按鍵配置
            if current_time - last_key_update > key_update_interval:
                auto_fire_key = config.auto_fire_key
                auto_fire_key2 = getattr(config, 'auto_fire_key2', None)
                last_key_update = current_time
            
            # 檢查按鍵狀態
            key_state = bool(getattr(config, 'always_auto_fire', False)) or is_key_pressed(auto_fire_key)
            if auto_fire_key2:
                key_state = key_state or is_key_pressed(auto_fire_key2)

            # 處理按鍵狀態變化
            if key_state and not last_key_state:
                delay_start_time = current_time
            
            if key_state:
                # 檢查開鏡延遲
                if delay_start_time and (current_time - delay_start_time >= config.auto_fire_delay):
                    # 檢查射擊冷卻時間
                    if current_time - last_fire_time >= config.auto_fire_interval:
                        
                        # 更新檢測框緩存
                        if current_time - last_box_update >= BOX_UPDATE_INTERVAL:
                            try:
                                # 從隊列中獲取最新的檢測結果（使用 get_nowait 替代直接訪問）
                                if not boxes_queue.empty():
                                    cached_boxes = boxes_queue.get_nowait()
                                    last_box_update = current_time
                            except queue.Empty:
                                # 沒有新的資料，使用舊緩存
                                pass
                            except Exception as e:
                                logger.warning("AutoFire 讀取檢測隊列失敗: %s", e)
                        
                        # 判斷是否應該開火
                        if cached_boxes:
                            crosshair_x, crosshair_y = config.crosshairX, config.crosshairY
                            target_part = config.auto_fire_target_part
                            head_height_ratio = config.head_height_ratio
                            head_width_ratio = config.head_width_ratio
                            body_width_ratio = config.body_width_ratio
                            
                            # 射擊判斷
                            should_fire = False
                            for box in cached_boxes:
                                x1, y1, x2, y2 = box
                                box_w, box_h = x2 - x1, y2 - y1
                                box_center_x = x1 + box_w * 0.5
                                
                                # 邊界檢查
                                if target_part == "head":
                                    head_h = box_h * head_height_ratio
                                    head_w = box_w * head_width_ratio
                                    head_x1 = box_center_x - head_w * 0.5
                                    head_x2 = box_center_x + head_w * 0.5
                                    head_y2 = y1 + head_h
                                    should_fire = (head_x1 <= crosshair_x <= head_x2 and y1 <= crosshair_y <= head_y2)
                                elif target_part == "body":
                                    body_w = box_w * body_width_ratio
                                    body_x1 = box_center_x - body_w * 0.5
                                    body_x2 = box_center_x + body_w * 0.5
                                    body_y1 = y1 + box_h * head_height_ratio
                                    should_fire = (body_x1 <= crosshair_x <= body_x2 and body_y1 <= crosshair_y <= y2)
                                elif target_part == "both":
                                    # 檢查頭部和身體區域
                                    head_h = box_h * head_height_ratio
                                    head_w = box_w * head_width_ratio
                                    head_x1 = box_center_x - head_w * 0.5
                                    head_x2 = box_center_x + head_w * 0.5
                                    
                                    is_in_head = (head_x1 <= crosshair_x <= head_x2 and y1 <= crosshair_y <= y1 + head_h)
                                    
                                    if not is_in_head:
                                        body_w = box_w * body_width_ratio
                                        body_x1 = box_center_x - body_w * 0.5
                                        body_x2 = box_center_x + body_w * 0.5
                                        body_y1 = y1 + head_h
                                        is_in_body = (body_x1 <= crosshair_x <= body_x2 and body_y1 <= crosshair_y <= y2)
                                        should_fire = is_in_body
                                    else:
                                        should_fire = True

                                if should_fire:
                                    # 執行射擊
                                    mouse_click_method = getattr(config, 'mouse_click_method', 'mouse_event')
                                    send_mouse_click(mouse_click_method)
                                    last_fire_time = current_time
                                    break
            else:
                delay_start_time = None
                if cached_boxes:
                    cached_boxes = []

            last_key_state = key_state
            
            time.sleep(1 / 60)
            
        except Exception as e:
            logger.error("AutoFire 發生錯誤: %s", e)
            traceback.print_exc()
            time.sleep(1.0)

