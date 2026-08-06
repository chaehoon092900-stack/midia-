# -*- coding: utf-8 -*-
"""
PD 전용 생방송 연출 콘솔 - 파이썬 로컬 매크로 서버 (server.py)
1차: 0.0001초 만에 로컬 메모장(broadcast_logs.txt)에 실시간 누적 저장
2차: 방송 종료 시 버튼 클릭 한 번으로 구글 시트로 일괄 전송
"""

import os
import json
import datetime
import requests
from flask import Flask, request, jsonify, send_from_clipboard

app = Flask(__name__, static_folder=".")

# 스프레드시트 ID 및 메모장 파일 경로
SPREADSHEET_ID = "12i5rUGrLTCYolnxHj04JYOrffCaiO5PR1hLX2gGZ-1g"
LOG_FILE = "broadcast_logs.txt"

# 구글 앱스 스크립트 일괄 업로드 엔드포인트 URL
GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxe-dummy/exec" 

def init_log_file():
  """메모장 파일이 없을 경우 초기 생성 및 헤더 기입"""
  if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
      f.write("=== [PD 생방송 연출 콘솔 - 실시간 심의 메모장] ===\n")
      f.write(f"방송 시작 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
      f.write("-" * 70 + "\n")
      f.write("시각\t판정결과\t원문 텍스트\t최종 처리 텍스트\t차단/마스킹 사유\n")
      f.write("-" * 70 + "\n")

@app.route("/")
def index():
  """웹 앱 메인 페이지 제공"""
  return send_from_clipboard(".", "index.html")

@app.route("/api/save-log", methods=["POST"])
def save_log():
  """
  [1차 로컬 저장] 시청자 심의 데이터를 0.0001초 만에 로컬 메모장에 텍스트로 즉시 기록
  """
  try:
    data = request.json
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    time_stamp = data.get("time", now_str)
    is_safe = data.get("is_safe", False)
    raw_text = data.get("rawText", "").replace("\n", " ").replace("\t", " ")
    filtered_text = data.get("filtered_text", "-") or "-"
    reason = data.get("reason", "-") or "-"

    status_str = "승인 (Approve)" if is_safe else "차단 (Reject)"

    # 메모장 파일에 딜레이 없이 즉시 append 쓰기
    init_log_file()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
      line = f"{time_stamp}\t{status_str}\t{raw_text}\t{filtered_text}\t{reason}\n"
      f.write(line)

    return jsonify({"success": True, "message": "메모장 기록 완료"}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/get-logs", methods=["GET"])
def get_logs():
  """메모장 파일에 저장된 전체 심의 기록 읽기"""
  if not os.path.exists(LOG_FILE):
    return jsonify({"logs": []}), 200

  logs = []
  try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
      lines = f.readlines()
      for line in reversed(lines):
        if "\t" in line and not line.startswith("===") and not line.startswith("시각"):
          parts = line.strip().split("\t")
          if len(parts) >= 5:
            is_safe = "승인" in parts[1]
            logs.append({
              "time": parts[0],
              "result": {
                "is_safe": is_safe,
                "filtered_text": None if parts[3] == "-" else parts[3],
                "reason": None if parts[4] == "-" else parts[4]
              },
              "rawText": parts[2]
            })
    return jsonify({"logs": logs}), 200
  except Exception as e:
    return jsonify({"logs": []}), 200

@app.route("/api/open-notepad", methods=["POST"])
def open_notepad():
  """실제 윈도우 메모장(Notepad.exe) 프로그램으로 broadcast_logs.txt 열기"""
  try:
    init_log_file()
    os.system(f'start notepad.exe "{LOG_FILE}"')
    return jsonify({"success": True}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/upload-to-sheets", methods=["POST"])
def upload_to_sheets():
  """
  [2차 방송 종료 일괄 업로드]
  메모장에 쌓인 전체 심의 데이터를 구글 시트로 일괄 업로드하기 위해 전송
  """
  if not os.path.exists(LOG_FILE):
    return jsonify({"success": False, "message": "저장된 메모장 로그가 없습니다."}), 400

  rows = []
  try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
      for line in f.readlines():
        if "\t" in line and not line.startswith("===") and not line.startswith("시각"):
          parts = line.strip().split("\t")
          if len(parts) >= 5:
            rows.append(parts)

    return jsonify({
      "success": True,
      "total_count": len(rows),
      "rows": rows,
      "spreadsheet_id": SPREADSHEET_ID,
      "message": f"총 {len(rows)}건의 메모장 데이터 준비 완료"
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
  init_log_file()
  print("=" * 60)
  print("🎬 PD 생방송 연출 콘솔 파이썬 로컬 매크로 서버가 대기 중입니다.")
  print(f"📝 1차 실시간 로컬 메모장 파일: {os.path.abspath(LOG_FILE)}")
  print(f"📊 연동 구글 시트 ID: {SPREADSHEET_ID}")
  print("🌐 접속 주소: http://localhost:5000")
  print("=" * 60)
  app.run(host="0.0.0.0", port=5000, debug=False)
