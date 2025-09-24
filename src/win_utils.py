# win_utils.py
import ctypes
import win32api
import win32con
import sys
import os
import time
import random
import threading
from language_manager import get_text

# Windows 虛擬按鍵碼對應英文名稱
VK_CODE_MAP = {
    0x01: "Mouse Left", 0x02: "Mouse Right", 0x04: "Mouse Middle", 0x05: "Mouse X1",
    0x06: "Mouse X2", 0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter",
    0x10: "Shift", 0x11: "Ctrl", 0x12: "Alt", 0x14: "CapsLock",
    0x1B: "Esc", 0x20: "Space", 0x25: "Left", 0x26: "Up", 0x27: "Right",
    0x28: "Down", 0x2C: "PrintScreen", 0x2D: "Insert", 0x2E: "Delete",
    0x30: "0", 0x31: "1", 0x32: "2", 0x33: "3", 0x34: "4", 0x35: "5",
    0x36: "6", 0x37: "7", 0x38: "8", 0x39: "9", 0x41: "A", 0x42: "B",
    0x43: "C", 0x44: "D", 0x45: "E", 0x46: "F", 0x47: "G", 0x48: "H",
    0x49: "I", 0x4A: "J", 0x4B: "K", 0x4C: "L", 0x4D: "M", 0x4E: "N",
    0x4F: "O", 0x50: "P", 0x51: "Q", 0x52: "R", 0x53: "S", 0x54: "T",
    0x55: "U", 0x56: "V", 0x57: "W", 0x58: "X", 0x59: "Y", 0x5A: "Z",
    0x5B: "Win", 0x60: "Num0", 0x61: "Num1", 0x62: "Num2", 0x63: "Num3",
    0x64: "Num4", 0x65: "Num5", 0x66: "Num6", 0x67: "Num7", 0x68: "Num8",
    0x69: "Num9", 0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4",
    0x74: "F5", 0x75: "F6", 0x76: "F7", 0x77: "F8", 0x78: "F9",
    0x79: "F10", 0x7A: "F11", 0x7B: "F12", 0x90: "NumLock", 0x91: "ScrollLock",
    0xA0: "Shift(L)", 0xA1: "Shift(R)", 0xA2: "Ctrl(L)", 0xA3: "Ctrl(R)",
    0xA4: "Alt(L)", 0xA5: "Alt(R)",
}

# 按鍵名稱多語言對應表
VK_TRANSLATIONS = {
    "zh_tw": {
        "Mouse Left": "滑鼠左鍵", "Mouse Right": "滑鼠右鍵", "Mouse Middle": "滑鼠中鍵", "Mouse X1": "滑鼠側鍵1",
        "Mouse X2": "滑鼠側鍵2", "Backspace": "Backspace", "Tab": "Tab", "Enter": "Enter",
        "Shift": "Shift", "Ctrl": "Ctrl", "Alt": "Alt", "CapsLock": "CapsLock",
        "Esc": "Esc", "Space": "Space", "Left": "←", "Up": "↑", "Right": "→",
        "Down": "↓", "PrintScreen": "PrintScreen", "Insert": "Insert", "Delete": "Delete",
        "Num0": "數字鍵0", "Num1": "數字鍵1", "Num2": "數字鍵2", "Num3": "數字鍵3", "Num4": "數字鍵4",
        "Num5": "數字鍵5", "Num6": "數字鍵6", "Num7": "數字鍵7", "Num8": "數字鍵8", "Num9": "數字鍵9",
        "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
        "Win": "Win", "Shift(L)": "Shift(左)", "Shift(R)": "Shift(右)", "Ctrl(L)": "Ctrl(左)", "Ctrl(R)": "Ctrl(右)", "Alt(L)": "Alt(左)", "Alt(R)": "Alt(右)"
    },
    "en": {}  # 英文直接顯示原名
}

def get_vk_name(key_code):
    name = VK_CODE_MAP.get(key_code, f'0x{key_code:02X}')
    lang = None
    try:
        from language_manager import language_manager
        lang = language_manager.get_current_language()
    except Exception:
        lang = "zh_tw"
    if lang != "en":
        return VK_TRANSLATIONS.get(lang, {}).get(name, name)
    return name

# ===== 滑鼠移動方式 =====

# 方式1: 原始 SendInput (容易被檢測)
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong), ("u", _INPUT_UNION)]

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

def send_mouse_move_sendinput(dx, dy):
    """方式1: SendInput API (原始方式，容易被檢測)"""
    print(f"[滑鼠移動] 使用 SendInput 方式，移動: ({dx}, {dy})")
    extra = ctypes.c_ulong(0)
    ii_ = INPUT._INPUT_UNION()
    ii_.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
    command = INPUT(INPUT_MOUSE, ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

# 方式2: 硬件層級模擬
def send_mouse_move_hardware(dx, dy):
    """方式2: 硬件層級滑鼠移動模擬"""
    print(f"[滑鼠移動] 使用硬件層級方式，移動: ({dx}, {dy})")
    try:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)
    except Exception as e:
        print(f"硬件層級移動失敗: {e}")

# 方式3: mouse_event (異步)
def send_mouse_move_mouse_event(dx, dy):
    """方式3: mouse_event 移動（異步執行）"""
    print(f"[滑鼠移動] 使用 mouse_event 方式，移動: ({dx}, {dy})")
    def mouse_event_move():
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)
        except Exception:
            pass
    
    # 異步執行
    threading.Thread(target=mouse_event_move, daemon=True).start()

# 方式4: ddxoft (最隱蔽) - 面向對象接口
class DDXoftMouse:
    """DDXoft 滑鼠控制類"""
    
    def __init__(self):
        self.dll = None
        self.available = False
        self.success_count = 0      # 成功次數
        self.failure_count = 0      # 失敗次數
        self.last_status = None     # 最後一次操作狀態
        self._init_dll()
    
    def _init_dll(self):
        """初始化 ddxoft DLL"""
        if self.available:
            return True
            
        try:
            # 嘗試載入 ddxoft DLL（常見位置）
            dll_paths = [
                "ddxoft.dll",  # 當前目錄
                "./ddxoft.dll",  # 相對路徑
                "src/ddxoft.dll",  # src 目錄
                "lib/ddxoft.dll",  # lib 目錄
            ]
            
            for dll_path in dll_paths:
                try:
                    self.dll = ctypes.CDLL(dll_path)
                    break
                except OSError:
                    continue
            
            if self.dll is None:
                print("[ddxoft] 警告: ddxoft.dll 未找到，請將 ddxoft.dll 放置在程序目錄中")
                return False
                
            # 設定函數原型
            self.dll.DD_btn.argtypes = [ctypes.c_int]
            self.dll.DD_btn.restype = ctypes.c_int
            self.dll.DD_str.argtypes = [ctypes.c_char_p]
            self.dll.DD_str.restype = ctypes.c_int
            self.dll.DD_movR.argtypes = [ctypes.c_int, ctypes.c_int]
            self.dll.DD_movR.restype = ctypes.c_int
            
            # 執行初始化序列
            # 步驟1: 調用 DD_btn(0) 進行初始化
            btn_result = self.dll.DD_btn(0)
            
            # 步驟2: 調用 DD_str 設定免費版標識
            str_result = self.dll.DD_str(b"dd2")
            
            # 檢查初始化結果
            if btn_result == 1 and str_result == 1:
                print("[ddxoft] ✓ ddxoft 初始化成功")
                self.available = True
                return True
            else:
                print(f"[ddxoft] ✗ 初始化失敗，請確保程序以管理員權限運行")
                return False
            
        except Exception as e:
            print(f"[ddxoft] 載入失敗: {e}")
            return False
    
    def move_relative(self, dx, dy):
        """相對移動滑鼠"""
        if not self.available:
            print("[ddxoft] DLL 未初始化或不可用")
            self.failure_count += 1
            self.last_status = "DLL_NOT_AVAILABLE"
            return False
        
        try:
            # 確保參數為整數且在合理範圍內
            dx = max(-32767, min(32767, int(dx)))
            dy = max(-32767, min(32767, int(dy)))
            
            # 使用 DD_movR 進行相對移動
            result = self.dll.DD_movR(dx, dy)
            
            if result == 1:
                self.success_count += 1
                self.last_status = "SUCCESS"
                return True
            else:
                self.failure_count += 1
                self.last_status = f"FAILED_CODE_{result}"
                
                # 詳細的錯誤分析
                error_messages = {
                    -1: "一般錯誤，可能是權限不足或初始化失敗",
                    -2: "找不到指定的窗口",
                    -3: "窗口最小化",
                    -4: "窗口不可見",
                    -5: "參數錯誤",
                    0: "操作失敗"
                }
                error_msg = error_messages.get(result, f"未知錯誤碼: {result}")
                print(f"[ddxoft] 移動失敗，返回值: {result} ({error_msg})")
                
                # 提供解決建議
                if result == -1:
                    print("[ddxoft] 建議：1) 確保以管理員權限運行 2) 檢查防毒軟體是否阻擋")
                elif result == -5:
                    print(f"[ddxoft] 參數檢查：dx={dx}, dy={dy}")
                    
                return False
                
        except Exception as e:
            self.failure_count += 1
            self.last_status = f"EXCEPTION_{type(e).__name__}"
            print(f"[ddxoft] 移動錯誤: {e}")
            return False
    
    def click_left(self):
        """左鍵點擊"""
        if not self.available:
            print("[ddxoft] DLL 未初始化或不可用，無法點擊")
            self.failure_count += 1
            self.last_status = "DLL_NOT_AVAILABLE"
            return False
        
        try:
            # 使用 DD_btn 進行滑鼠點擊
            # 1 = 左鍵按下, 2 = 左鍵釋放
            down_result = self.dll.DD_btn(1)
            # 添加微小延遲確保按下和釋放被正確識別
            import time
            time.sleep(0.001)  # 1ms延遲
            up_result = self.dll.DD_btn(2)
            
            if down_result == 1 and up_result == 1:
                self.success_count += 1
                self.last_status = "CLICK_SUCCESS"
                print(f"[ddxoft] ✓ 點擊成功")
                return True
            else:
                self.failure_count += 1
                self.last_status = f"CLICK_FAILED_DOWN_{down_result}_UP_{up_result}"
                print(f"[ddxoft] ✗ 點擊失敗，按下返回值: {down_result}, 釋放返回值: {up_result}")
                return False
                
        except Exception as e:
            self.failure_count += 1
            self.last_status = f"CLICK_EXCEPTION_{type(e).__name__}"
            print(f"[ddxoft] ✗ 點擊錯誤: {e}")
            return False
    
    def is_available(self):
        """檢查 ddxoft 是否可用"""
        return self.available
    
    def get_statistics(self):
        """獲取使用統計"""
        total = self.success_count + self.failure_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        return {
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'total_count': total,
            'success_rate': success_rate,
            'last_status': self.last_status
        }
    
    def reset_statistics(self):
        """重置統計數據"""
        self.success_count = 0
        self.failure_count = 0
        self.last_status = None
    
    def print_statistics(self):
        """打印統計信息"""
        stats = self.get_statistics()
        print(f"[ddxoft] 統計信息:")
        print(f"  成功次數: {stats['success_count']}")
        print(f"  失敗次數: {stats['failure_count']}")
        print(f"  總計次數: {stats['total_count']}")
        print(f"  成功率: {stats['success_rate']:.1f}%")
        print(f"  最後狀態: {stats['last_status']}")
    
    def test_functionality(self):
        """測試 ddxoft 功能並診斷問題"""
        print("[ddxoft] 開始診斷測試...")
        
        if not self.available:
            print("[ddxoft] ✗ DLL 未初始化")
            return False
        
        
        # 測試小幅度移動
        test_moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        success_count = 0
        
        for dx, dy in test_moves:
            if self.move_relative(dx, dy):
                success_count += 1
            time.sleep(0.1)  # 短暫延遲
        
        print(f"[ddxoft] 測試結果: {success_count}/{len(test_moves)} 次移動成功")
        
        if success_count > 0:
            print("[ddxoft] ✓ 基本功能正常")
            return True
        else:
            print("[ddxoft] ✗ 所有移動測試失敗")
            print("[ddxoft] 請檢查：")
            print("  1. 是否以管理員權限運行")
            print("  2. 是否被防毒軟體阻擋")
            print("  3. ddxoft.dll 版本是否正確")
            return False

# 創建全局 ddxoft_mouse 實例
ddxoft_mouse = DDXoftMouse()

# ddxoft 統計顯示控制變量
_ddxoft_move_count = 0
_ddxoft_last_stats_display = 0

def send_mouse_move_ddxoft(dx, dy):
    """方式4: ddxoft 移動（最隱蔽）"""
    global _ddxoft_move_count, _ddxoft_last_stats_display
    
    _ddxoft_move_count += 1
    
    # 首次使用時確認
    if _ddxoft_move_count == 1:
        print(f"[ddxoft] ✓ 開始使用 ddxoft 滑鼠移動方式")
    
    if ddxoft_mouse.move_relative(dx, dy):
        # 成功使用 ddxoft
        # 每 50 次移動顯示一次統計（避免刷屏）
        if _ddxoft_move_count % 50 == 0:
            stats = ddxoft_mouse.get_statistics()
            print(f"[ddxoft] ✓ 已成功執行 {stats['success_count']} 次移動 (成功率: {stats['success_rate']:.1f}%)")
        return
    
    # 如果 ddxoft 失敗，回退到 mouse_event 方式
    print(f"[ddxoft] ✗ 第 {_ddxoft_move_count} 次移動失敗，回退到 mouse_event 方式")
    send_mouse_move_mouse_event(dx, dy)



# 主要滑鼠移動函數 - 簡化版本
def send_mouse_move(dx, dy, method="mouse_event"):
    """
    主要滑鼠移動函數
    method 選項:
    - "sendinput": SendInput (原始方式，容易被檢測)
    - "hardware": 硬件層級 (較隱蔽)
    - "mouse_event": mouse_event (很隱蔽)
    - "ddxoft": ddxoft (最隱蔽，需要 ddxoft.dll)
    """
    if abs(dx) < 1 and abs(dy) < 1:
        return  # 移動量太小，跳過
    
    if method == "sendinput":
        send_mouse_move_sendinput(dx, dy)
    elif method == "hardware":
        send_mouse_move_hardware(dx, dy)
    elif method == "mouse_event":
        send_mouse_move_mouse_event(dx, dy)
    elif method == "ddxoft":
        send_mouse_move_ddxoft(dx, dy)
    else:
        # 默認使用 mouse_event 方式
        send_mouse_move_mouse_event(dx, dy)

# ===== 滑鼠點擊函數 =====

def send_mouse_click_sendinput():
    """方式1: SendInput 左鍵點擊"""
    import win32api
    import win32con
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def send_mouse_click_hardware():
    """方式2: 硬件層級左鍵點擊"""
    # 這裡可以使用更底層的硬件API，暫時使用和sendinput相同的實現
    send_mouse_click_sendinput()

def send_mouse_click_mouse_event():
    """方式3: mouse_event 左鍵點擊"""
    import win32api
    import win32con
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def send_mouse_click_ddxoft():
    """方式4: ddxoft 左鍵點擊"""
    global ddxoft_mouse
    try:
        if ddxoft_mouse.click_left():
            return True
        else:
            # 如果 ddxoft 失敗，立即回退到 mouse_event 方式
            print("[自動開火] ddxoft 點擊失敗，立即回退到 mouse_event")
            send_mouse_click_mouse_event()
            return True  # 回退成功，返回 True
    except Exception as e:
        print(f"[自動開火] ddxoft 點擊異常: {e}，回退到 mouse_event")
        send_mouse_click_mouse_event()
        return True

def send_mouse_click(method="mouse_event"):
    """
    統一的滑鼠點擊函數，支援多種方式
    method 選項:
    - "sendinput": SendInput (原始方式，容易被檢測)
    - "hardware": 硬件層級 (較隱蔽)
    - "mouse_event": mouse_event (很隱蔽)
    - "ddxoft": ddxoft (最隱蔽，需要 ddxoft.dll)
    """
    print(f"[點擊] 執行滑鼠點擊 - 方式: {method}")
    
    try:
        if method == "sendinput":
            send_mouse_click_sendinput()
        elif method == "hardware":
            send_mouse_click_hardware()
        elif method == "mouse_event":
            send_mouse_click_mouse_event()
        elif method == "ddxoft":
            return send_mouse_click_ddxoft()
        else:
            print(f"[點擊] 未知的滑鼠點擊方式: {method}，使用預設方式")
            send_mouse_click_mouse_event()
        return True
    except Exception as e:
        print(f"[點擊] 滑鼠點擊失敗: {e}")
        # 萬無一失的回退到 mouse_event
        try:
            send_mouse_click_mouse_event()
            return True
        except Exception as e2:
            print(f"[點擊] 回退點擊也失敗: {e2}")
            return False

def is_key_pressed(key_code):
    return win32api.GetAsyncKeyState(key_code) & 0x8000 != 0

# ===== 管理員權限管理 =====

def is_admin():
    """檢查當前程序是否以管理員權限運行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_privileges():
    """請求管理員權限並重新啟動程序"""
    if is_admin():
        return True
    
    try:
        print("[權限管理] 正在以管理員權限重新啟動程序...")
        
        # 獲取當前腳本的完整路徑
        script_path = os.path.abspath(sys.argv[0])
        
        # 使用 ShellExecute 以管理員權限啟動
        result = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{script_path}"', 
            None, 
            1  # SW_SHOW
        )
        
        # 如果成功啟動，退出當前程序
        if result > 32:  # ShellExecute 成功返回值 > 32
            print("[權限管理] 管理員權限程序已啟動，結束當前程序")
            sys.exit(0)
        else:
            print(f"[權限管理] 無法啟動管理員權限程序，錯誤代碼: {result}")
            print("[權限管理] 繼續以普通權限運行（某些功能可能受限）")
            return False
            
    except Exception as e:
        print(f"[權限管理] 請求管理員權限時發生錯誤: {e}")
        print("[權限管理] 繼續以普通權限運行（某些功能可能受限）")
        return False

def check_and_request_admin():
    """檢查並在需要時請求管理員權限"""
    # 檢查是否有跳過管理員權限的命令行參數
    if "--no-admin" in sys.argv:
        return False
    
    if is_admin():
        print("[權限管理] ✓ 程序已以管理員權限運行")
        return True
    else:
        print("[權限管理] ⚠ 程序未以管理員權限運行")
        return request_admin_privileges()

def test_ddxoft_functions():
    """測試 ddxoft 功能的公共接口"""
    return ddxoft_mouse.test_functionality()

def get_ddxoft_statistics():
    """獲取 ddxoft 統計信息的公共接口"""
    return ddxoft_mouse.get_statistics()

def print_ddxoft_statistics():
    """打印 ddxoft 統計信息的公共接口"""
    return ddxoft_mouse.print_statistics()

def reset_ddxoft_statistics():
    """重置 ddxoft 統計信息的公共接口"""
    global _ddxoft_move_count
    _ddxoft_move_count = 0
    return ddxoft_mouse.reset_statistics()

def test_mouse_click_methods():
    """測試所有滑鼠點擊方式"""
    print("[測試] 開始測試所有滑鼠點擊方式...")
    
    methods = ["mouse_event", "sendinput", "hardware", "ddxoft"]
    
    for method in methods:
        print(f"[測試] 測試 {method} 點擊方式...")
        try:
            success = send_mouse_click(method)
            if success:
                print(f"[測試] ✓ {method} 點擊成功")
            else:
                print(f"[測試] ✗ {method} 點擊失敗")
        except Exception as e:
            print(f"[測試] ✗ {method} 點擊異常: {e}")
        
        import time
        time.sleep(0.5)  # 延遲0.5秒避免連點
    
    print("[測試] 滑鼠點擊測試完成")