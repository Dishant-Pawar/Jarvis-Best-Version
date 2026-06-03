param(
    [string]$RadioKind = "WiFi",
    [string]$State = "On"
)

$ErrorActionPreference = "Stop"

try {
    if ($RadioKind -eq "WiFi") {
        # Use netsh to toggle Wi-Fi (works without admin for user-level control)
        # First try using Windows built-in radio management
        try {
            Add-Type -AssemblyName System.Runtime.WindowsRuntime

            $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
                $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
            })[0]

            function Await($WinRtTask, $ResultType) {
                $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
                $netTask = $asTask.Invoke($null, @($WinRtTask))
                $netTask.Wait(-1) | Out-Null
                return $netTask.Result
            }

            [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
            [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null

            $access = Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
            if ($access -eq "Allowed") {
                $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
                $wifiRadio = $radios | Where-Object { $_.Kind.ToString() -eq "WiFi" }
                if ($wifiRadio) {
                    if ($wifiRadio -is [array]) { $wifiRadio = $wifiRadio[0] }
                    $newState = if ($State -eq "On") { "On" } else { "Off" }
                    $result = Await ($wifiRadio.SetStateAsync($newState)) ([Windows.Devices.Radios.RadioAccessStatus])
                    Write-Output "WiFi Radio API Result: $result"
                    exit 0
                }
            }
        } catch {
            Write-Warning "Radio API failed, falling back to netsh: $_"
        }

        # Fallback: Use netsh wlan to enable/disable Wi-Fi interface
        $adapters = netsh wlan show interfaces 2>&1
        if ($LASTEXITCODE -eq 0 -or $adapters -match "Name") {
            if ($State -eq "On") {
                # Enable all WLAN adapters via netsh
                $result = netsh interface set interface "Wi-Fi" enabled 2>&1
                if ($LASTEXITCODE -ne 0) {
                    # Try alternate name
                    $result = netsh interface set interface "Wireless Network Connection" enabled 2>&1
                }
                Write-Output "WiFi netsh enable result: $result"
            } else {
                $result = netsh interface set interface "Wi-Fi" disabled 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $result = netsh interface set interface "Wireless Network Connection" disabled 2>&1
                }
                Write-Output "WiFi netsh disable result: $result"
            }
        } else {
            Write-Error "No WLAN service available or no Wi-Fi adapter found."
            exit 1
        }
    }
    elseif ($RadioKind -eq "Bluetooth") {
        # Try Radio API first
        try {
            Add-Type -AssemblyName System.Runtime.WindowsRuntime

            $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
                $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
            })[0]

            function Await($WinRtTask, $ResultType) {
                $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
                $netTask = $asTask.Invoke($null, @($WinRtTask))
                $netTask.Wait(-1) | Out-Null
                return $netTask.Result
            }

            [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
            [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null

            $access = Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
            if ($access -eq "Allowed") {
                $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
                $btRadio = $radios | Where-Object { $_.Kind.ToString() -eq "Bluetooth" }
                if ($btRadio) {
                    if ($btRadio -is [array]) { $btRadio = $btRadio[0] }
                    $newState = if ($State -eq "On") { "On" } else { "Off" }
                    $result = Await ($btRadio.SetStateAsync($newState)) ([Windows.Devices.Radios.RadioAccessStatus])
                    Write-Output "Bluetooth Radio API Result: $result"
                    exit 0
                }
            }
        } catch {
            Write-Warning "Radio API failed, falling back to service method: $_"
        }

        # Fallback: Toggle Bluetooth via bthserv service and adapter
        if ($State -eq "On") {
            # Start Bluetooth service
            $svc = Get-Service -Name "bthserv" -ErrorAction SilentlyContinue
            if ($svc) {
                Start-Service -Name "bthserv" -ErrorAction SilentlyContinue
                Write-Output "Bluetooth service started."
            }
            # Enable Bluetooth adapter via Get-PnpDevice
            $btDevices = Get-PnpDevice | Where-Object { $_.FriendlyName -match "Bluetooth" -and $_.Status -eq "Error" }
            foreach ($dev in $btDevices) {
                Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
            }
            Write-Output "Bluetooth enabled via PnP."
        } else {
            # Stop Bluetooth service
            $svc = Get-Service -Name "bthserv" -ErrorAction SilentlyContinue
            if ($svc -and $svc.Status -eq "Running") {
                Stop-Service -Name "bthserv" -Force -ErrorAction SilentlyContinue
                Write-Output "Bluetooth service stopped."
            }
            # Disable Bluetooth adapter via Get-PnpDevice
            $btDevices = Get-PnpDevice | Where-Object { $_.FriendlyName -match "Bluetooth" -and $_.Status -eq "OK" }
            foreach ($dev in $btDevices) {
                Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
            }
            Write-Output "Bluetooth disabled via PnP."
        }
    }
    else {
        Write-Error "Unknown RadioKind: $RadioKind. Use 'WiFi' or 'Bluetooth'."
        exit 1
    }
} catch {
    Write-Error "toggle_radio.ps1 error: $_"
    exit 1
}
