$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
$url = "http://127.0.0.1:8501"

try {
    $null = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2
} catch {
    Start-Process -FilePath "python" `
        -ArgumentList @("-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "8501", "--server.headless", "true") `
        -WorkingDirectory $project `
        -WindowStyle Hidden

    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 500
        try {
            $null = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2
            break
        } catch {
            if ($attempt -eq 19) { throw "本地服务启动超时" }
        }
    }
}

Start-Process $url
