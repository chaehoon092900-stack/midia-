# -*- coding: utf-8 -*-
"""
PD 전용 생방송 연출 콘솔 - 실제 윈도우 메모장(Notepad.exe) 직접 연동 매크로
"""

import os
import sys
import re
import time
import subprocess
import datetime
import tkinter as tk
from tkinter import messagebox

# 1. 파일 경로 지정
LOG_FILE = os.path.abspath("broadcast_log.txt")

# 2. 심의 검수 패턴
HARD_BAD_WORDS = [
  re.compile(r'씨[발빨팔봘발바벌빠]|시[발빨팔벌]|ㅆ[ㅂㅃ]|ㅅㅂ|ㅂㅅ|병[신신씬]|개[새끼세끼새기]|엠창|느금|애미|지랄|좃|좆|창녀|꺼져|ㄲㅈ', re.I),
  re.compile(r'시\s*발|씨\s*발|존\s*나|ㅈ\s*ㄴ|ㅅ\s*ㅂ|ㅂ\s*ㅅ', re.I)
]

MASKABLE_WORDS = [
  (re.compile(r'존나'), '***'),
  (re.compile(r'ㅈㄴ'), '***'),
  (re.compile(r'미친'), '***'),
  (re.compile(r'ㅁㅊ'), '***'),
  (re.compile(r'개좋'), '***좋'),
  (re.compile(r'개꿀'), '***꿀')
]

PRIVACY_PATTERNS = [re.compile(r'01[016789][-\s]?\d{3,4}[-\s]?\d{4}'), re.compile(r'\d{6}[-\s]?[1-4]\d{6}')]

def evaluate_text(text):
  if not text or not text.strip():
    return False, "내용이 비어 있습니다.", None

  raw_text = text.strip()

  for pattern in PRIVACY_PATTERNS:
    if pattern.search(raw_text):
      return False, "개인정보(전화번호/주민번호) 노출", None

  for pattern in HARD_BAD_WORDS:
    if pattern.search(raw_text):
      return False, "악성 욕설/비속어 포함", None

  processed_text = raw_text
  for pattern, replace in MASKABLE_WORDS:
    processed_text = pattern.sub(replace, processed_text)

  return True, None, processed_text


class NotepadMacroApp:
  def __init__(self, root):
    self.root = root
    self.root.title("🎬 PD 전용 생방송 연출 & 메모장 매크로 콘솔")
    self.root.geometry("620x680")
    self.root.configure(bg="#f8fafc")

    self.init_log_file()
    self.open_windows_notepad()
    self.create_widgets()

  def init_log_file(self):
    """실제 메모장 파일 초기 세팅"""
    if not os.path.exists(LOG_FILE):
      with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== [PD 생방송 연출 콘솔 - broadcast_log.txt] ===\n")
        f.write(f"방송 시작 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("----------------------------------------------------------------------\n")
        f.write("시각\t\t판정결과\t원문 텍스트\t\t최종 처리 텍스트\t차단/마스킹 사유\n")
        f.write("----------------------------------------------------------------------\n")

  def open_windows_notepad(self):
    """실제 윈도우 메모장(Notepad.exe) 프로그램을 직접 실행하여 화면에 띄움"""
    try:
      os.startfile(LOG_FILE) # 윈도우 기본 메모장 연동 열기
    except Exception:
      try:
        subprocess.Popen(["notepad.exe", LOG_FILE])
      except Exception as e:
        pass

  def append_to_notepad(self, time_str, status_str, raw_text, filter_text, reason_str):
    """실제 메모장 파일에 텍스트를 적고 메모장 화면을 즉시 재로드"""
    line = f"{time_str}\t{status_str}\t\"{raw_text}\"\t\"{filter_text}\"\t{reason_str}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
      f.write(line)

    self.open_windows_notepad()

  def create_widgets(self):
    header_frame = tk.Frame(self.root, bg="#2563eb", padx=15, pady=15)
    header_frame.pack(fill="x")

    title_label = tk.Label(header_frame, text="🎬 PD 생방송 연출 & 메모장 직접 기입 매크로", font=("Malgun Gothic", 14, "bold"), fg="white", bg="#2563eb")
    title_label.pack(anchor="w")

    sub_label = tk.Label(header_frame, text="시청자 글을 입력하면 실제 메모장에 즉시 타자 기록됩니다.", font=("Malgun Gothic", 9), fg="#dbeafe", bg="#2563eb")
    sub_label.pack(anchor="w", pady=(3, 0))

    input_frame = tk.LabelFrame(self.root, text=" 💬 시청자 참여글 입력 ", font=("Malgun Gothic", 10, "bold"), bg="#f8fafc", fg="#0f172a", padx=15, pady=15)
    input_frame.pack(fill="x", padx=15, pady=15)

    self.text_entry = tk.Entry(input_frame, font=("Malgun Gothic", 11), bg="white", relief="solid", bd=1)
    self.text_entry.pack(fill="x", ipady=8, pady=(0, 10))
    self.text_entry.bind("<Return>", lambda event: self.process_input())
    self.text_entry.focus()

    submit_btn = tk.Button(input_frame, text="📝 실제 윈도우 메모장에 직접 적기 (Enter)", font=("Malgun Gothic", 10, "bold"), bg="#059669", fg="white", relief="flat", cursor="hand2", command=self.process_input, ipady=6)
    submit_btn.pack(fill="x")

    preset_frame = tk.Frame(input_frame, bg="#f8fafc")
    preset_frame.pack(fill="x", pady=(10, 0))

    preset_title = tk.Label(preset_frame, text="⚡ 테스트용 샘플 (클릭 시 메모장에 즉시 타이핑):", font=("Malgun Gothic", 8), fg="#64748b", bg="#f8fafc")
    preset_title.pack(anchor="w", pady=(0, 5))

    presets = [
      ("✅ 정상 댓글", "오늘 라이브 방송 응원합니다 화이팅!"),
      ("⚠️ 마스킹 댓글", "와 오늘 무대 연출 진짜 존나 미쳤다 ㅋㅋㅋ 대박!"),
      ("❌ 초성 욕설", "진행자 진행 ㅈㄴ 못하네 ㅆㅂ 진짜 노답"),
      ("❌ 개인정보", "제 전화번호 010-1234-5678 로 이벤트를 보내주세요!")
    ]

    btn_box = tk.Frame(preset_frame, bg="#f8fafc")
    btn_box.pack(fill="x")

    for label, text_val in presets:
      btn = tk.Button(btn_box, text=label, font=("Malgun Gothic", 8), bg="#e2e8f0", fg="#334155", relief="flat", cursor="hand2", command=lambda t=text_val: self.run_preset(t))
      btn.pack(side="left", padx=2)

    self.status_label = tk.Label(self.root, text="💡 시청자 글을 입력하고 엔터를 누르면 실제 메모장에 직접 써집니다.", font=("Malgun Gothic", 10, "bold"), bg="#f1f5f9", fg="#334155", pady=10, relief="solid", bd=1)
    self.status_label.pack(fill="x", padx=15, pady=(0, 15))

    bottom_frame = tk.Frame(self.root, bg="#f8fafc")
    bottom_frame.pack(fill="x", padx=15)

    reopen_btn = tk.Button(bottom_frame, text="📄 실제 메모장(Notepad) 다시 열기", font=("Malgun Gothic", 9, "bold"), bg="#4f46e5", fg="white", relief="flat", cursor="hand2", command=self.open_windows_notepad, ipady=6)
    reopen_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

    sheets_btn = tk.Button(bottom_frame, text="📊 방송 종료: 구글 시트 이동", font=("Malgun Gothic", 9, "bold"), bg="#059669", fg="white", relief="flat", cursor="hand2", command=self.open_sheets, ipady=6)
    sheets_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

  def run_preset(self, text_val):
    self.text_entry.delete(0, tk.END)
    self.text_entry.insert(0, text_val)
    self.process_input()

  def process_input(self):
    raw_text = self.text_entry.get().strip()
    if not raw_text:
      return

    is_safe, reason, filtered_text = evaluate_text(raw_text)
    time_str = datetime.datetime.now().strftime("%H:%M:%S")

    status_str = "승인 (Approve)" if is_safe else "차단 (Reject) "
    filter_val = filtered_text if filtered_text else "-"
    reason_val = reason if reason else "-"

    self.append_to_notepad(time_str, status_str, raw_text, filter_val, reason_val)

    if is_safe:
      self.status_label.config(text=f"🟢 [승인] 메모장에 직접 적히고 MC 프롬프터 자막이 등록되었습니다!\n내용: {filter_val}", bg="#d1fae5", fg="#065f46")
    else:
      self.status_label.config(text=f"🔴 [차단] 사유: {reason_val}\n원문: {raw_text}", bg="#fee2e2", fg="#991b1b")

    self.text_entry.delete(0, tk.END)

  def open_sheets(self):
    import webbrowser
    webbrowser.open("https://docs.google.com/spreadsheets/d/12i5rUGrLTCYolnxHj04JYOrffCaiO5PR1hLX2gGZ-1g/edit")

if __name__ == "__main__":
  root = tk.Tk()
  app = NotepadMacroApp(root)
  root.mainloop()
