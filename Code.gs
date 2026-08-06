/**
 * Google Apps Script (GAS) - 구글 시트 100% 최신화 및 일괄 업로드 Code.gs
 */

var SPREADSHEET_ID = "12i5rUGrLTCYolnxHj04JYOrffCaiO5PR1hLX2gGZ-1g";

function getTargetSheet() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (ss && ss.getId() === SPREADSHEET_ID) return ss.getActiveSheet();
  } catch(e) {}
  return SpreadsheetApp.openById(SPREADSHEET_ID).getActiveSheet();
}

function doGet() {
  resetAndInitSheet();
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('PD 전용 생방송 연출 콘솔')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function onOpen() {
  try {
    resetAndInitSheet();
    SpreadsheetApp.getUi()
      .createMenu('🎬 PD 콘솔')
      .addItem('시트 전체 깨끗이 초기화', 'resetAndInitSheet')
      .addToUi();
  } catch(e) {}
}

// 구글 시트 B1 날짜 시각 갱신 및 초기화
function resetAndInitSheet() {
  try {
    var sheet = getTargetSheet();
    sheet.clear();

    var nowStr = Utilities.formatDate(new Date(), "GMT+9", "yyyy-MM-dd HH:mm:ss");

    sheet.getRange("A1").setValue("방송 시작 일시").setFontWeight("bold").setBackground("#f1f5f9");
    sheet.getRange("A2").setValue("프로그램명").setFontWeight("bold").setBackground("#f1f5f9");
    sheet.getRange("A3").setValue("동시 시청자수").setFontWeight("bold").setBackground("#f1f5f9");

    sheet.getRange("B1").setValue(nowStr);
    sheet.getRange("B2").setValue("생방송 라이브 시청자 톡");
    sheet.getRange("B3").setValue("15,420명");

    sheet.getRange("D1").setValue("총 검수");
    sheet.getRange("E1").setValue("송출 승인");
    sheet.getRange("F1").setValue("사고 차단");
    sheet.getRange("D1:F1").setFontWeight("bold").setBackground("#e2e8f0").setHorizontalAlignment("center");

    sheet.getRange("D2").setValue(0).setHorizontalAlignment("center");
    sheet.getRange("E2").setValue(0).setHorizontalAlignment("center");
    sheet.getRange("F2").setValue(0).setHorizontalAlignment("center");

    var headers = [["심의 시각", "판정 결과", "시청자 원문 텍스트", "최종 방송 처리 텍스트", "차단 / 마스킹 사유"]];
    sheet.getRange("A5:E5").setValues(headers)
      .setFontWeight("bold")
      .setBackground("#2563eb")
      .setFontColor("#ffffff")
      .setHorizontalAlignment("center");

    sheet.setColumnWidth(1, 160);
    sheet.setColumnWidth(2, 130);
    sheet.setColumnWidth(3, 300);
    sheet.setColumnWidth(4, 300);
    sheet.setColumnWidth(5, 250);

  } catch(e) {
    Logger.log("시트 초기화 에러: " + e.toString());
  }
}
