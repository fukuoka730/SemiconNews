# 毎月1日 AM 6:00 に前月分のレポートを自動生成するタスクを登録するスクリプト
# PowerShell を管理者権限で実行してください

$taskName   = "SemiNewsReport_Monthly"
$scriptPath = "C:\Users\tofukuok\OfflineDocument\Claude\Projects\SemiNewsReport\run_monthly.bat"
$logPath    = "C:\Users\tofukuok\OfflineDocument\Claude\Projects\SemiNewsReport\run.log"

# 既存タスクを削除 (再登録用)
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# トリガー: 毎月1日 06:00
$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At "06:00"

# アクション: バッチ実行
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$scriptPath`""

# 設定: ネットワーク接続時のみ実行、ログオン不要
$settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Trigger   $trigger `
    -Action    $action `
    -Settings  $settings `
    -Principal $principal `
    -Description "半導体市場ニュースレポートを毎月1日に自動生成"

Write-Host "タスク登録完了: $taskName"
Write-Host "次回実行: 毎月1日 06:00"
Write-Host "ログ: $logPath"
