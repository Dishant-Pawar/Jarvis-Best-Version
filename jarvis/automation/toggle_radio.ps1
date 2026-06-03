param(
    [string]$RadioKind = "WiFi",
    [string]$State = "On"
)

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
    if ($access -ne "Allowed") {
        Write-Error "Access not allowed: $access"
        exit 1
    }

    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
    
    $targetRadio = $radios | Where-Object { $_.Kind.ToString() -eq $RadioKind -or $_.Name -like "*$RadioKind*" }
    if (-not $targetRadio) {
        Write-Error "Radio of kind $RadioKind not found."
        exit 1
    }

    if ($targetRadio -is [array]) {
        $targetRadio = $targetRadio[0]
    }

    $newState = if ($State -eq "On") { "On" } else { "Off" }
    $result = Await ($targetRadio.SetStateAsync($newState)) ([Windows.Devices.Radios.RadioAccessStatus])
    Write-Output "Result: $result"
} catch {
    Write-Error $_
    exit 1
}
