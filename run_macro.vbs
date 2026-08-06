' Windows Native VBScript Notepad Macro Script
Dim WshShell, fso, file, logPath, userInput, statusStr

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

logPath = fso.GetAbsolutePathName("broadcast_log.txt")

' 1. 메모장 파일이 없으면 초기 세팅
If Not fso.FileExists(logPath) Then
    Set file = fso.CreateTextFile(logPath, True, True)
    file.WriteLine "=== [PD 생방송 연출 콘솔 - broadcast_log.txt] ==="
    file.WriteLine "방송 시작 일시: " & Now
    file.WriteLine "----------------------------------------------------------------------"
    file.WriteLine "시각" & vbTab & "판정결과" & vbTab & "원문 텍스트" & vbTab & "최종 처리 텍스트" & vbTab & "차단/마스킹 사유"
    file.WriteLine "----------------------------------------------------------------------"
    file.Close
End If

' 2. 실제 윈도우 메모장(Notepad.exe) 프로그램 실행
WshShell.Run "notepad.exe """ & logPath & """", 1, False
WScript.Sleep 1000

MsgBox "🎬 실제 윈도우 메모장(Notepad)이 켜졌습니다!" & vbCrLf & "확인을 누르면 시청자 글 입력창이 실행됩니다.", 64, "PD 생방송 연출 매크로"

' 3. 무한 매크로 입력 루프
Do
    userInput = InputBox("💬 시청자가 작성한 글을 입력하세요 (종료하려면 취소 클릭):" & vbCrLf & vbCrLf & "입력 시 화면의 실제 메모장에 직접 타자 기입됩니다.", "PD 시청자 참여글 AI 심의 매크로")
    
    If userInput = "" Then
        Exit Do
    End If

    ' 간단 심의
    Dim isSafe, reason, filterText, nowTime
    nowTime = FormatDateTime(Now, 4) & ":" & Right("0" & Second(Now), 2)
    isSafe = True
    reason = "-"
    filterText = userInput

    ' 욕설/비속어 검사
    If InStr(userInput, "시발") > 0 Or InStr(userInput, "씨발") > 0 Or InStr(userInput, "ㅅㅂ") > 0 Or InStr(userInput, "ㅂㅅ") > 0 Or InStr(userInput, "병신") > 0 Or InStr(userInput, "개새끼") > 0 Then
        isSafe = False
        reason = "악성 욕설/비속어 포함"
        filterText = "-"
    ElseIf InStr(userInput, "존나") > 0 Or InStr(userInput, "ㅈㄴ") > 0 Or InStr(userInput, "미친") > 0 Or InStr(userInput, "ㅁㅊ") > 0 Then
        filterText = Replace(userInput, "존나", "***")
        filterText = Replace(filterText, "ㅈㄴ", "***")
        filterText = Replace(filterText, "미친", "***")
        filterText = Replace(filterText, "ㅁㅊ", "***")
    End If

    If isSafe Then
        statusStr = "승인 (Approve)"
    Else
        statusStr = "차단 (Reject) "
    End If

    ' 4. 메모장 파일에 한 줄 덧붙이고, 실제 메모장 창 활성화 후 직접 타자 치듯 송출
    Set file = fso.OpenTextFile(logPath, 8, True, -1)
    file.WriteLine nowTime & vbTab & statusStr & vbTab & """" & userInput & """" & vbTab & """" & filterText & """" & vbTab & reason
    file.Close

    ' 메모장 창을 맨 앞으로 가져와서 갱신
    WshShell.AppActivate "broadcast_log.txt - 메모장"
    WshShell.AppActivate "broadcast_log.txt"
    WshShell.SendKeys "^{HOME}"
Loop

MsgBox "방송 매크로가 완료되었습니다.", 64, "PD 콘솔"
