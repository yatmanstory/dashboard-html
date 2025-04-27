import pyautogui
import time
import os
import requests
from pathlib import Path
import logging
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_and_retry(func, max_retries=3, wait_time=1):
    """함수를 재시도하는 데코레이터"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"시도 {attempt + 1} 실패: {str(e)}")
                time.sleep(wait_time)
    return wrapper

@wait_and_retry
def automate_quedata_copy_paste():
    """Quedata 자동화 함수"""
    try:
        logger.info("Quedata 자동화 시작...")
        
        # AWS 대시보드로 전환할 시간을 위해 대기
        time.sleep(2)
        
        # Ctrl+A로 전체 선택
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        
        # Ctrl+C로 복사
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
        # CSV 파일 창으로 전환
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)  # 창 전환을 위한 충분한 시간
        
        # Ctrl+Shift+V로 붙여넣기
        pyautogui.hotkey('ctrl', 'shift', 'v')
        time.sleep(0.5)
        
        # Ctrl+S로 저장
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)
        
        logger.info("Quedata 자동화가 성공적으로 완료되었습니다!")
        return True
    except Exception as e:
        logger.error(f"자동화 중 오류 발생: {str(e)}")
        raise

def upload_csv_to_server(csv_path: Optional[str] = None) -> bool:
    """CSV 파일을 서버로 업로드하는 함수"""
    if csv_path is None:
        csv_path = "Quedata.csv"
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
        return False

    # 서버 비밀번호 설정
    password = "12345678"
    url = "https://dashboard-server-8neo.onrender.com/upload_csv"
    
    try:
        with open(csv_path, "rb") as f:
            files = {"file": f}
            data = {"password": password}
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                logger.info("✅ CSV 파일 서버로 업로드 성공")
                return True
            else:
                logger.error(f"❌ 업로드 실패: {response.text}")
                return False
    except Exception as e:
        logger.error(f"❌ 업로드 에러: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # 시작 전 5초 대기하여 올바른 창으로 전환할 시간 제공
        logger.info("5초 후 Quedata 자동화를 시작합니다...")
        time.sleep(5)
        
        if automate_quedata_copy_paste():
            upload_csv_to_server()
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {str(e)}") 