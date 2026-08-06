# Windows Native PowerShell Notepad Macro Script
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

$logPath = [System.IO.Path]::GetFullPath("broadcast_log.txt")

# 1. 메모장 파일 초기 세팅
if (-not (Test-Path $logPath)) {
    $header = "=== [PD 생방송 연출 콘솔 - broadcast_log.txt] ===" + "`n" +
              "방송 시작 일시: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "`n" +
              "----------------------------------------------------------------------`n" +
              "시각`t판정결과`t원문 텍스트`t최종 처리 텍스트`t차단/마스킹 사유`n" +
              "----------------------------------------------------------------------`n"
    [System.IO.File]::WriteAllText($logPath, $header, [System.Text.Encoding]::UTF8)
}

# 2. 실제 윈도우 메모장(Notepad.exe) 실행
Start-Process "notepad.exe" $logPath
Start-Sleep -Seconds 1

[System.Windows.Forms.MessageBox]::Show("🎬 실제 윈도우 메모장(Notepad)이 실행되었습니다!`n`n확인을 누르면 시청자 글 입력창이 켜집니다.", "PD 생방송 연출 매크로", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)

# 3. 매크로 입력 무한 루프
while ($true) {
    $userInput = [Microsoft.VisualBasic.Interaction]::InputBox("💬 시청자가 작성한 글을 입력하세요:`n(종료하려면 취소 버튼 클릭)", "PD 시청자 참여글 AI 심의 매크로", "")
    
    if ([string]::IsNullOrWhiteSpace($userInput)) {
        break
    }

    $nowTime = Get-Date -Format "HH:mm:ss"
    $isSafe = $true
    $reason = "-"
    $filterText = $userInput

    # 심의 검수
    if ($userInput -match "시발|씨발|ㅅㅂ|ㅂㅅ|병신|개새끼|지랄|꺼져") {
        $isSafe = $false
        $reason = "악성 욕설/비속어 포함"
        $filterText = "-"
    } elseif ($userInput -match "01[016789][-\s]?\d{3,4}[-\s]?\d{4}") {
        $isSafe = $false
        $reason = "개인정보(전화번호) 노출"
        $filterText = "-"
    } else {
        $filterText = $filterText -replace "존나", "***" -replace "ㅈㄴ", "***" -replace "미친", "***" -replace "ㅁㅊ", "***"
    }

    $statusStr = if ($isSafe) { "승인 (Approve)" } else { "차단 (Reject) " }

    # 메모장 파일에 한 줄 덧붙이기
    $logLine = "$nowTime`t$statusStr`t`"$userInput`"`t`"$filterText`"`t$reason`n"
    [System.IO.File]::AppendAllText($logPath, $logLine, [System.Text.Encoding]::UTF8)

    # 실제 메모장 재로드 구동
    Start-Process "notepad.exe" $logPath
}

[System.Windows.Forms.MessageBox]::Show("방송 매크로 기록이 종료되었습니다.", "PD 콘솔", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
