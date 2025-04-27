import pyautogui
import time
import os
import requests

def automate_quedata_copy_paste():
    # AWS 대시보드로 전환할 시간을 위해 2초 대기
    time.sleep(2)
    
    # Ctrl+A로 전체 선택
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    
    # Ctrl+C로 복사
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    
    # CSV 파일 창으로 전환 (다음 창으로 가정)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.5)
    
    # Ctrl+Shift+V로 붙여넣기
    pyautogui.hotkey('ctrl', 'shift', 'v')
    time.sleep(0.5)
    
    # Ctrl+S로 저장
    pyautogui.hotkey('ctrl', 's')
    time.sleep(0.5)
    
    print("Quedata 자동화가 성공적으로 완료되었습니다!")

def upload_csv_to_server(csv_path="Quedata.csv"):
    url = "https://your-render-app.onrender.com/upload_csv"  # Render URL
    password = "Dkzldkzl!2"  # 서버와 같은 비밀번호!

    files = {"file": open(csv_path, "rb")}
    data = {"password": password}
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("✅ CSV 파일 서버로 업로드 성공")
        else:
            print(f"❌ 업로드 실패: {response.text}")
    except Exception as e:
        print(f"❌ 업로드 에러: {e}")

if __name__ == "__main__":
    # 시작 전 5초 대기하여 올바른 창으로 전환할 시간 제공
    print("5초 후 Quedata 자동화를 시작합니다...")
    time.sleep(5)
    automate_quedata_copy_paste()
    # 자동화 완료 후 CSV 파일 업로드
    upload_csv_to_server() 