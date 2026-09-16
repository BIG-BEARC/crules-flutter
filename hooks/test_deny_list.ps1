# deny-list.ps1 回归测试驱动（1.0.17 批F2——双驱夹具单源，与 test_deny_list.py 共读 cases.json）
# 跑法：pwsh -NoProfile -File hooks/test_deny_list.ps1（或 Windows：powershell -NoProfile -ExecutionPolicy Bypass -File 同路径）
# 结构（与 py 驱动的差异及理据）：
#   ① 判据面 = **点源 in-process**（$DENYLIST_LIB_ONLY 短路入口段，直调 Get-DenyListDecision）——
#      黑盒逐例 spawn powershell.exe 冷启 ≈0.4-1.0s × 138 例不可受；in-process <2s
#   ② 契约面 = **黑盒 spawn 探针 ×4**（stdin JSON → stdout JSON / exit code 全链路）：
#      deny JSON 形态、非法 JSON fail-open exit 0、ask JSON 形态、文案锁「不要尝试绕过」——
#      契约在入口段、判据在 Get-Decision，两层各测其责（py 侧纯黑盒无所谓慢系冷启 ~30ms 的平台差）
#   ③ 单调性变异（ps 集）：引号插 / 反引号续行插（D-a 无 \w 步故无反斜杠变异——cases.json
#      monotonicity.mutators 单源声明）
#   ④ os=win 例（$env:TEMP 依赖）在非 Windows（pwsh Linux/mac）跳过并计数——CI pwsh 步证据级声明。
# 探测纪律（v41 镜像）：黑盒输入一律 ConvertTo-Json 构造，禁手拼。
# 兼容：Windows PowerShell 5.1 底线（无 ??/三元；-File 直跑）。
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---- 夹具单源加载 ----
$docJson = Get-Content -Raw -Encoding UTF8 (Join-Path (Join-Path $here 'fixtures') 'deny-list-cases.json')
$doc = ConvertFrom-Json $docJson
$isWin = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
$cases = @($doc.cases | Where-Object {
    $langOk = ($_.lang -eq $null) -or ($_.lang -eq 'both') -or ($_.lang -eq 'ps')
    $osOk = -not ($_.os -eq 'win') -or $isWin
    $langOk -and $osOk
})
$skipOs = @($doc.cases | Where-Object { ($_.lang -eq $null -or $_.lang -eq 'both' -or $_.lang -eq 'ps') -and $_.os -eq 'win' -and -not $isWin }).Count

# ---- ① 判据面：点源 in-process ----
$global:DENYLIST_LIB_ONLY = $true
. (Join-Path $here 'deny-list.ps1')

$fails = @()
$nDeny = 0; $nAllow = 0; $nAsk = 0
foreach ($c in $cases) {
    $d = Get-DenyListDecision $c.cmd
    switch ($c.expect) {
        'deny'  { $nDeny++;  if ($d.kind -ne 'deny')  { $fails += ('应拦未拦: ' + $c.cmd) } }
        'allow' { $nAllow++; if ($d.kind -ne 'allow') { $fails += ('应放未放: ' + $c.cmd) } }
        'ask'   { $nAsk++;   if ($d.kind -ne 'ask')   { $fails += ('应 warn 未 ask: ' + $c.cmd) } }
    }
}

# ---- ③ 单调性（ps mutators：引号插 / 反引号续行插；抽样口径同 py 驱动 step） ----
$step = [int]$doc.monotonicity.step
$blockCases = @($cases | Where-Object { $_.expect -eq 'deny' })
$mutTotal = 0
$bt = [string][char]0x60
$nl = [string][char]10
for ($i = 0; $i -lt $blockCases.Count; $i += $step) {
    $cmd = [string]$blockCases[$i].cmd
    $n = $cmd.Length
    if ($n -lt 8) { continue }
    foreach ($pos in @([math]::Floor($n / 3), [math]::Floor($n * 2 / 3))) {
        $pos = [int]$pos
        if ($pos -ge $n) { continue }
        foreach ($m in @($cmd.Substring(0, $pos) + '"' + $cmd.Substring($pos),
                         $cmd.Substring(0, $pos) + $bt + $nl + $cmd.Substring($pos))) {
            $mutTotal++
            $d = Get-DenyListDecision $m
            if ($d.kind -ne 'deny') { $fails += ('单调性破坏（变异后非 deny）: ' + $m) }
        }
    }
}

# ---- ② 契约面：黑盒 spawn 探针 ×4 ----
$denyListPath = Join-Path $here 'deny-list.ps1'
function Invoke-Blackbox([string]$stdinStr) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = if ($PSVersionTable.PSVersion.Major -ge 6) { (Get-Process -Id $PID).Path } else { 'powershell.exe' }
    $psi.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $denyListPath + '"'
    $psi.RedirectStandardInput = $true; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
    # 编码显式（子进程 stdout 无 BOM UTF-8，父端默认按宿主码页读——5.1 GBK 下中文探针乱码误红）。
    # 注意：StandardInputEncoding 系 .NET Core 3.0+ API，5.1（.NET Framework）无此属性（review R2）——
    # 只设 Output 侧；输入侧探针全 ASCII（ConvertTo-Json 中文转 \uXXXX），不依赖 stdin 编码
    $psi.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $psi.UseShellExecute = $false
    $proc = [System.Diagnostics.Process]::Start($psi)
    $proc.StandardInput.Write($stdinStr)
    $proc.StandardInput.Close()
    $out = $proc.StandardOutput.ReadToEnd()
    $proc.WaitForExit()
    return @{out = $out; code = $proc.ExitCode}
}
# 探针 1：deny 端到端 JSON 契约（permissionDecision":"deny 且含尾文案）
$p1 = Invoke-Blackbox (@{tool_input = @{command = 'git push --force origin main'}} | ConvertTo-Json -Compress)
if ($p1.out -notmatch '"permissionDecision":"deny"') { $fails += ('黑盒探针1 deny JSON 缺失: ' + $p1.out) }
# 探针 2：非法 JSON fail-open exit 0 零输出
$p2 = Invoke-Blackbox '{not json'
if ($p2.code -ne 0 -or $p2.out.Trim().Length -gt 0) { $fails += ('黑盒探针2 fail-open 破坏: code=' + $p2.code + ' out=' + $p2.out) }
# 探针 3：ask 端到端
$p3 = Invoke-Blackbox (@{tool_input = @{command = 'chmod -R 755 assets'}} | ConvertTo-Json -Compress)
if ($p3.out -notmatch '"permissionDecision":"ask"') { $fails += ('黑盒探针3 ask JSON 缺失: ' + $p3.out) }
# 探针 4：文案锁（跨实现字节级一致断言点，py 驱动同款）
if ($p1.out -notmatch '不要尝试绕过') { $fails += '黑盒探针4 拦截文案缺「不要尝试绕过」' }

# ---- 汇总 ----
foreach ($f in $fails) { Write-Output ('FAIL ' + $f) }
$osNote = if ($isWin) { 'os=win 全跑' } else { ('os=win 跳过 ' + $skipOs) }
Write-Output ('deny-list 测试(ps 驱动): ' + $nDeny + ' 拦 + ' + $nAllow + ' 放 + ' + $nAsk + ' warn + 单调性 ' + $mutTotal + ' 变异 + 黑盒探针 4, 失败 ' + $fails.Count + ' (' + $osNote + ')')
if ($fails.Count -eq 0) { exit 0 } else { exit 1 }
