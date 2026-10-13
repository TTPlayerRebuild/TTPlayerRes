[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Version,
    [string]$PreviousVersion,
    [Parameter(Mandatory)][string]$Repository,
    [Parameter(Mandatory)][string]$Commit,
    [string]$ArtifactDirectory = 'artifact',
    [string]$ServerUrl = 'https://github.com'
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'version.ps1')
$Version = (Get-ResBuildVersion $Version).Name
if ($PreviousVersion -and -not (Read-ResVersionTag $PreviousVersion)) { throw 'Invalid previous version.' }
if ($Repository -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' -or $Commit -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'Invalid repository or commit.'
}
$name = "ttpres-$Version.zip"
$hash = (Get-FileHash -LiteralPath (Join-Path $ArtifactDirectory $name) -Algorithm SHA256).Hash.ToLowerInvariant()
$sums = (Get-Content -LiteralPath (Join-Path $ArtifactDirectory 'SHA256SUMS.txt') -Raw -Encoding UTF8).Trim()
if ($sums -cne "$hash  $name") { throw 'Resource ZIP checksum mismatch.' }
$repoUrl = "$ServerUrl/$Repository"
$logUrl = if ($PreviousVersion) { "$repoUrl/compare/$PreviousVersion...$Version" } else { "$repoUrl/commits/$Version" }
@"
**更新记录**: $logUrl

关闭播放器后，将 ZIP 中的 ttpres.dll 放入播放器主目录。
兼容原版千千静听 5.7.9 与重建版；同一资源 DLL 用于 XP、Win7 和 Windows 10/11。
完整保留原版 192 项资源，新增独立资源区；无代码、无运行库依赖。
原版 VERSION 资源保留 5.7.9.0；构建版本 $Version 记录在扩展资源和包名中。
ZIP 仅包含 ttpres.dll 和 SHA256SUMS.txt。

[源码及兼容性说明]($repoUrl/tree/$Commit)
"@ | Set-Content -LiteralPath (Join-Path $ArtifactDirectory 'release-notes.md') -Encoding UTF8
