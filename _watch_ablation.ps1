$ErrorActionPreference = "Continue"
$repo = "D:\桌面\HKU\IDAT7215 Computer programming for product development and applications\am-defect-tl"
Set-Location $repo
$slug = "kennethdeng/am-defect-ablation"
$deadline = (Get-Date).AddMinutes(80)
$status = ""

while ((Get-Date) -lt $deadline) {
    $status = (& kaggle kernels status $slug 2>&1 | Select-Object -Last 1)
    Write-Output ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $status)
    if ($status -match "COMPLETE|ERROR|CANCEL|FAILED") { break }
    Start-Sleep -Seconds 60
}

if ($status -match "COMPLETE") {
    Write-Output "[ablation] kernel complete, downloading output ..."
    & kaggle kernels output $slug -p kaggle_out_ablation 2>&1 | Select-Object -Last 3
    if (Test-Path "kaggle_out_ablation\results_ablation") {
        Copy-Item -Recurse -Force "kaggle_out_ablation\results_ablation" "results_ablation"
    }
    Write-Output "[ablation] downloaded run dirs:"
    Get-ChildItem "results_ablation\runs" -Directory -ErrorAction SilentlyContinue |
        ForEach-Object { "  " + $_.Name }
    Write-Output ""
    & python tools/summarize_ablation.py 2>&1
} else {
    Write-Output "[ablation] not complete: $status"
    Write-Output "[ablation] log tail:"
    & kaggle kernels output $slug -p kaggle_out_ablation 2>&1 | Select-Object -Last 5
}
