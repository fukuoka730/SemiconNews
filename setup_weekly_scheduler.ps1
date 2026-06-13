# 毎週月曜 AM 8:00 に直近7日分の週刊ダイジェストをメール送信するタスクを登録するスクリプト。
# このスクリプトは管理者権限なしで実行できます（ログオン中のユーザーとして実行されるため、
# 実行時にPCが起動しログオンしている必要があります）。
#
# ログオフ中でもPC起動中なら実行したい場合は、管理者PowerShellで実行し、
# Register-ScheduledTask に次を追加してください:
#   -Principal (New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest)

$taskName   = "SemiNewsReport_Weekly"
$scriptPath = "C:\Users\tofukuok\Documents\Claude\Projects\SemiNewsReport\run_weekly.bat"
$logPath    = "C:\Users\tofukuok\Documents\Claude\Projects\SemiNewsReport\run_weekly.log"

# 既存タスクを削除 (再登録用)
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# トリガー: 毎週月曜 08:00
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "08:00"

# アクション: バッチ実行
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$scriptPath`""

# 設定: ネットワーク接続時のみ実行、見逃した場合は次回起動時に実行
$settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName $taskName `
    -Trigger   $trigger `
    -Action    $action `
    -Settings  $settings `
    -Description "半導体ニュース週報を毎週月曜に自動送信"

Write-Host "タスク登録完了: $taskName"
Write-Host "次回実行: 毎週月曜 08:00"
Write-Host "ログ: $logPath"
