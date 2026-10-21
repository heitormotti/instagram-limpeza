# Cria 5 tarefas agendadas no Windows (09:30, 12:30, 15:30, 18:30, 21:30) que rodam um lote cada.
# Uso: powershell -ExecutionPolicy Bypass -File agendar.ps1
$py = (Get-Command python).Source
$script = Join-Path $PSScriptRoot "limpeza.py"
foreach ($h in "09:30","12:30","15:30","18:30","21:30") {
    $nome = "LimpezaIG-" + $h.Replace(":","")
    $acao = New-ScheduledTaskAction -Execute "$env:WINDIR\System32\conhost.exe" -Argument "--headless `"$py`" `"$script`" lote" -WorkingDirectory $PSScriptRoot
    $gat = New-ScheduledTaskTrigger -Daily -At $h -RandomDelay (New-TimeSpan -Minutes 40)
    $cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries
    Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gat -Settings $cfg -Force | Out-Null
    Write-Host "criada: $nome"
}
