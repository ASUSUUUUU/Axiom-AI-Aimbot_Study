# admin.py - 管理員權限模組
"""Windows 管理員權限管理"""

from __future__ import annotations

import ctypes
import os
import sys


def is_admin() -> bool:
    """檢查當前程序是否以管理員權限運行"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
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
        print("[權限管理] 程序已以管理員權限運行")
        return True
    else:
        print("[權限管理] 程序未以管理員權限運行")
        return request_admin_privileges()

