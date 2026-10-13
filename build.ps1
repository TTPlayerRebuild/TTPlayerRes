[CmdletBinding()]
param(
    [string]$BuildDirectory = (Join-Path $PSScriptRoot 'build'),
    [string]$Generator = 'Visual Studio 18 2026',
    [string]$PackageVersion,
    [switch]$Package
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'cmake/version.ps1')
$PackageVersion = (Get-ResBuildVersion $PackageVersion).Name
& cmake -S $PSScriptRoot -B $BuildDirectory -G $Generator -A Win32 "-DTTPRES_BUILD_VERSION=$PackageVersion"
if ($LASTEXITCODE -ne 0) { throw 'Resource configuration failed.' }
& cmake --build $BuildDirectory --config Release --target ttpres --parallel 4 -- /nr:false
if ($LASTEXITCODE -ne 0) { throw 'Resource build or contract audit failed.' }
if ($Package) {
    & python (Join-Path $PSScriptRoot 'tools/package.py') --directory (Join-Path $BuildDirectory 'Release') --version $PackageVersion
    if ($LASTEXITCODE -ne 0) { throw 'Resource packaging failed.' }
}
