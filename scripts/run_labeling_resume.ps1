$ErrorActionPreference = "Stop"
$python = Join-Path (Get-Location).Path ".venv\Scripts\python.exe"
$outputDir = Join-Path (Get-Location).Path "results\teacher-label-attempt-02"
$monitorPath = Join-Path $outputDir "run-resume-monitor.log"
$availableRamLimitMiB = 768
$env:SHARD_COUNT = "2"
$env:LABEL_WORKERS = "1"
$env:RESUME_LABELING = "1"
$env:SHARD_OUTPUT_DIR = $outputDir

foreach ($shard in 0, 1) {
    $env:SHARD_INDEX = [string]$shard
    $env:RESUME_INPUTS = Join-Path (Get-Location).Path `
        "results\teacher-label-attempt-01-partial\teacher-shard-$shard.jsonl"
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $stdoutPath = Join-Path $outputDir "teacher-shard-$shard.resume-$stamp.stdout.log"
    $stderrPath = Join-Path $outputDir "teacher-shard-$shard.resume-$stamp.stderr.log"

    $worker = Start-Process -FilePath $python -ArgumentList "worker/label_worker.py" `
        -WorkingDirectory (Get-Location).Path -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    Add-Content -Path $monitorPath -Value "$(Get-Date -Format o) shard=$shard event=started pid=$($worker.Id) ram_limit_mib=$availableRamLimitMiB"
    $stoppedForMemory = $false

    while (-not $worker.HasExited) {
        Start-Sleep -Seconds 15
        $availableMiB = [int](Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue
        $shardPath = Join-Path $outputDir "teacher-shard-$shard.jsonl.resume.jsonl"
        if (-not (Test-Path $shardPath)) {
            $shardPath = Join-Path $outputDir "teacher-shard-$shard.jsonl"
        }
        $rowCount = 0
        if (Test-Path $shardPath) {
            $rowCount = (Get-Content $shardPath | Measure-Object -Line).Lines
        }
        Add-Content -Path $monitorPath -Value "$(Get-Date -Format o) shard=$shard rows=$rowCount available_ram_mib=$availableMiB"
        if ($availableMiB -lt $availableRamLimitMiB) {
            Add-Content -Path $monitorPath -Value "$(Get-Date -Format o) shard=$shard event=stopped_low_memory pid=$($worker.Id)"
            $stoppedForMemory = $true
            Stop-Process -Id $worker.Id -Force
            $worker.WaitForExit()
            break
        }
        $worker.Refresh()
    }

    if ($stoppedForMemory) {
        Add-Content -Path $monitorPath -Value "$(Get-Date -Format o) shard=$shard event=checkpoint_preserved; rerun this script after RAM recovers"
        exit 2
    }

    $worker.Refresh()
    if (-not $worker.HasExited) {
        $worker.WaitForExit()
    }
    $worker.Refresh()
    Add-Content -Path $monitorPath -Value "$(Get-Date -Format o) shard=$shard event=worker_exit exit_code=$($worker.ExitCode)"
    $completedRows = 0
    $finalShardPath = Join-Path $outputDir "teacher-shard-$shard.jsonl"
    if (Test-Path $finalShardPath) {
        $completedRows = (Get-Content $finalShardPath | Measure-Object -Line).Lines
    }
    if ($worker.ExitCode -ne 0 -and $completedRows -ne 1500) {
        exit $worker.ExitCode
    }
}
