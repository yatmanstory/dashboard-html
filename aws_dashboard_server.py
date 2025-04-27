from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import uvicorn
import shutil

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# 업로드 인증 비밀번호
UPLOAD_PASSWORD = "Dkzldkzl!2"  # 여기에만 너만 아는 비밀번호 세팅하기!

# --- CSV 업로드 API ---
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), password: str = Form(...)):
    if password != UPLOAD_PASSWORD:
        return {"message": "❌ 인증 실패: 비밀번호가 틀렸습니다."}
    
    try:
        with open("Quedata.csv", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "✅ CSV 파일 업로드 성공!"}
    except Exception as e:
        return {"message": f"업로드 실패: {e}"}

# 상담사 매핑 테이블 로드
def load_agent_mapping(file_path="agents.json"):
    with open(file_path, encoding="utf-8") as f:
        agents = json.load(f)
    return {agent["ConID"]: agent["Name"] for agent in agents}

agent_mapping = load_agent_mapping()

# --- CSV 줄 단위 파싱 함수 ---
def parse_csv_line_by_line(file_path="Quedata.csv"):
    records = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # 헤더 찾기
    header_line_idx = None
    for idx, line in enumerate(lines):
        if idx >= 65 and "에이전트 로그인" in line:
            header_line_idx = idx
            break

    if header_line_idx is None:
        raise ValueError("❌ 헤더를 찾을 수 없습니다.")

    headers = [h.strip() for h in lines[header_line_idx].strip().split(",")]
    data_lines = lines[header_line_idx + 1:]

    current_agent = None
    voice = None
    chat_total = None
    live_chats = []

    for line in data_lines:
        parts = [p.strip() for p in line.strip().split(",")]

        if len(parts) < 5:
            continue

        if parts[0].startswith("con"):
            if current_agent:
                records.append(build_agent_record(current_agent, voice, chat_total, live_chats))
            current_agent = parts
            voice = None
            chat_total = None
            live_chats = []
        elif parts[1] == "음성":
            voice = parts
        elif parts[1] == "채팅 합계":
            chat_total = parts
        elif parts[1] == "채팅":
            live_chats.append(parts)

    if current_agent:
        records.append(build_agent_record(current_agent, voice, chat_total, live_chats))

    final_df = pd.DataFrame(records)
    return final_df

def build_agent_record(main, voice, chat_total, live_chats):
    try:
        con_id = main[0]
        agent_name = agent_mapping.get(con_id, "Unknown")

        # --- 점유율 찾기 (라우팅 프로필 이후, %포함된 값) ---
        routing_profile = main[5]
        routing_profile_idx = 5
        percent_value = "-"
        for i in range(routing_profile_idx + 1, len(main)):
            if "%" in main[i]:
                percent_value = main[i]
                break

        return {
            "이름": agent_name,
            "연결": sum(int(lc[11]) for lc in live_chats if len(lc) > 11 and lc[11].isdigit()),
            "상태": main[2],
            "다음상태": main[3] if len(main) > 3 else "-",
            "시간": main[4],
            "라우팅 프로필": routing_profile,
            "점유율": percent_value,
            "CaAHT": voice[9] if voice and len(voice) > 9 else "-",
            "ChAHT": chat_total[9] if chat_total and len(chat_total) > 9 else "-",
            "처리호": (int(voice[11]) if voice and len(voice) > 11 and voice[11].isdigit() else 0) +
                     (int(chat_total[12]) if chat_total and len(chat_total) > 12 and chat_total[12].isdigit() else 0)
        }
    except Exception as e:
        print(f"❌ 에이전트 블록 파싱 실패: {e}")
        return {}


# --- FastAPI API 엔드포인트 ---
@app.get("/data")
def get_data():
    df = parse_csv_line_by_line("Quedata.csv")
    return df.to_dict(orient="records")

# --- FastAPI 서버 실행 부분 ---
if __name__ == "__main__":
    uvicorn.run("aws_dashboard_server:app", host="0.0.0.0", port=8000, reload=True)
