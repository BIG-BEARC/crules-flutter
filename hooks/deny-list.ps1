# crules-flutter 破坏性命令 deny-list —— PowerShell 原生实现（PreToolUse 硬闸，批F2/1.0.17，Windows 防线 F2）
# 双源声明：判据逻辑逐函数镜像 deny-list.py（文末对照表）。任何一侧改判据，必须同步另一侧
#   并跑双驱夹具全绿（hooks/fixtures/deny-list-cases.json 单源 → test_deny_list.py + test_deny_list.ps1）。
# 官方事实底座（code.claude.com/docs/en/hooks·tools-reference·setup，2026-09-16 查证）：
#   - Windows 无 Git Bash 时注册的是 PowerShell 工具（非 Bash）→ 原 matcher "Bash" 永不触发 = 零防线；
#     装 Git Bash 时两工具并存，模型可走 PowerShell 绕过 bash 域 → 两 matcher 双 handler
#   - exec form（command+args）不经 shell、${CLAUDE_PLUGIN_ROOT} 以纯字符串注入 args（空格/反斜杠安全）；
#     Windows exec form 只认真 exe（powershell.exe 内置 5.1）
#   - PreToolUse deny 在所有权限模式（含 bypass）生效；JSON 契约平台无关；if 过滤 best-effort——
#     硬判定在本脚本内对完整命令串做（不依赖 if 窄匹配）
# 与 deny-list.py 的有意差异（审读锚点）：
#   D-a 归一：删「\+NL」与「`+NL」续行、删引号、删其余反引号（PS 转义符，删后拼合=只增拦截面）；
#       **不做** \<word> 转义拼接删——\ 是 Windows 路径分隔符，删之破坏白名单方向（A2 归一只增不删）；
#       对应 fixture 2 例标 lang:bash（git pu\sh / g\it push --force）
#   D-b GIT_SIG 命令/子命令词与别名/env 名/路径 IgnoreCase（Windows 命令与文件系统大小写不敏感）；
#       **git 旗标字母与 argv 值保持区分**——-D/-d、-S/-s 语义差与 stash 子命令值 "clear" 的比较
#       由 git.exe 自身 argv 大小写敏感语义自持（`git stash CLEAR` git 亦拒——不判非漏，py parity；
#       review R5 头注订正：原「子命令 IgnoreCase」表述过宽，折叠的只是签名词面）；
#       fixture 锁：GIT RESET --hard 拦（签名词面）、git branch -D 拦而 -d 无 f 放（旗标区分）
#   D-c rm 别名域双标尺：CMDLET_SIG 族（Remove-Item|ri|rm|del|erase|rd|rmdir）→ Get-RmFlags
#       三源并集：bash 捆绑短字母仅限 ^[rf]+$ 形（-rf/-f/-r；**长名不做字母扫描**——review R1：
#       -Force 内含 r 会假置 Recurse、-WhatIf 内含 f 假置 Force，dry-run 被误拦）∪ PS 前缀缩写
#       （方向=全称.StartsWith(输入)，故 -R/-re 置 Recurse、-f/-fo 置 Force，5.1 歧义报错串也拦——
#       错命令无放行价值；py 侧 -R 系既存 FN，ps 侧前缀规则天然覆盖，双源差异声明于此）∪
#       cmd 形 /s /q /f（不区分大小写，入参先小写）；git 域 Get-GitFlags 逐字等价 py
#       （git.exe 自解析 argv，PS 缩写不参与；长名表小写后比对，--FORCE→force 与 py 现状差异系 D-b）
#   D-d pathspec 尾分隔符 TrimEnd('/','\')：PS 当前目录惯用 .\（git restore .\ 真实丢弃）
#   D-e 白名单自展开（Resolve-PsPath）：hook 收模型手写**字面串**（$env:TEMP\x 未经 shell 求值）——
#       $env:NAME\、%NAME%、~/ ~\ 展开；未知变量/残留 $ % → UNRESOLVED 即拒（deny 方向）；
#       折叠 ./.. 纯字符串（normpath 非 realpath，py L17 裁决镜像：解析 junction/符号链接反造误拦）；
#       比较 ToLowerInvariant；temp 根 = GetTempPath ∪ env TEMP/TMP ∪ 字面 /tmp /var/folders
#       （bash 习惯串跨界仍对，both allow 例锁）；UNC 不特判（TEMP 为 UNC 时前缀自然成立，否则拒）
#   D-f warn 扩集：左加 iwr/irm/Invoke-WebRequest/Invoke-RestMethod（5.1 里 curl/wget 皆 IWR 别名、
#       curl.exe 真二进制并存，词形非锚定全收）、右加 iex/Invoke-Expression + cmd/powershell；
#       新形态 ①' iex (iwr …) 括号形（无管道）与 iwr … | iex；icacls /T（chmod -R 等价）；
#       Start-Process -Verb RunAs（sudo 等价）；Set-Acl 不收（改 ACL 系 Windows 日常，FP 面广——边界）
# v1 已知不拦（诚实边界，deny 方向 FN）：
#   - powershell -EncodedCommand <base64>：整体旁路一切明文判据（bash「两步法」的 PS 强敌版）
#   - 字符串拼接/变量间接构造命令（git $op、"git pu"+"sh"）、splatting（Remove-Item @a）
#   - Remove-Item -Recurse 无 -Force：与 bash rm -r 同型**刻意放行**（parity，fixture 锁）
#   - Get-ChildItem | Remove-Item 枚举注入（右侧空操作数可拦、左侧枚举不盖——剩余面小）
#   - robocopy /MIR、format、diskpart、Set-MpPreference 等 Windows 原生破坏族不入名单——
#     黑名单不可穷尽（原则同 py 头注）
# 终极防线：本 hook 是安全网而非沙箱；终极防线是 Claude Code 原生权限确认与需求方人工执行。
# 输入契约 fail-open（镜像 py F10①）：stdin 非法 JSON / 读流失败 → exit 0 静默放行。
# 兼容底线 Windows PowerShell 5.1（不假设 pwsh7）：无 ??/三元/-AsHashtable；输出走 [Console]::Out.Write
#   （禁 Write-Host）；UTF-8 显式化（5.1 码页坑：stdin 按 UTF-8 解、stdout 无 BOM 写，否则宿主 JSON
#   解析被 BOM/码页破坏）。黑盒契约探针 ×4 在 test_deny_list.ps1 锁本段。
# 验证状态：mac 无 PowerShell——判据面经双驱 fixture（pwsh CI / Windows 实机）；
#   **Windows 实机为用户最终闸**（裁决单 §8 落账口径）。

$script:DENYLIST_BT = [char]0x60   # 反引号（PS 转义符）按码位构造，规避文件字面转义歧义
$script:DENYLIST_NL = [char]10

# ========== 判定体（Get-DenyListDecision 返回 @{kind=deny|ask|allow; reason}；
# ========== stdin 与出口 JSON 只在入口段——驱动点源 in-process 测判据、黑盒 spawn 测契约） ==========

$DENYLIST_GIT_SIG = [regex]::new('\bgit\b[^;|]*?\b(push|reset|clean|branch|checkout|restore|switch|stash)\b', 'IgnoreCase')
$DENYLIST_CMDLET_SIG = [regex]::new('(^|[\s(`$!&;|])(Remove-Item|ri|rm|del|erase|rd|rmdir)\b', 'IgnoreCase')
$DENYLIST_REDIR = [regex]::new('^(\d*|\*)[<>]')
$DENYLIST_PFE = [regex]::new('^(?<name>\w+)(?<rest>[\\/].*)?$')
$DENYLIST_PCT = [regex]::new('^%(?<name>[^%]+)%(?<rest>.*)$')

function Get-DenyListDecision([string]$rawCmd) {
    if ([string]::IsNullOrEmpty($rawCmd)) { return @{kind = 'allow'; reason = ''} }
    if ($rawCmd.Trim().Length -eq 0) { return @{kind = 'allow'; reason = ''} }
    $cmd = Normalize-DenyList($rawCmd)
    foreach ($part in [regex]::Split($cmd, ';|&&|\|\||\||\r?\n')) {
        $seg = $part.Trim()
        if ($seg.Length -eq 0) { continue }
        $m = $DENYLIST_GIT_SIG.Match($seg)
        if ($m.Success) {
            $sub = $m.Groups[1].Value.ToLowerInvariant()
            $after = $seg.Substring($m.Index + $m.Length)
            if ($sub -eq 'push') {
                $fl = Get-GitFlags $seg
                if ($fl.short.Contains('f') -or $fl.long.Contains('force')) {
                    return @{kind = 'deny'; reason = '破坏性命令（git push --force）：请人工确认后自行执行；确需强推建议人工用 --force-with-lease'} }
                if ($fl.long.Contains('delete') -or [regex]::IsMatch($seg, '\s:[^\s]')) {
                    return @{kind = 'deny'; reason = '破坏性命令（git push 删除远端分支）：请人工确认后自行执行'} }
                if ([regex]::IsMatch($seg, '(^|\s)\+\S+')) {
                    return @{kind = 'deny'; reason = '破坏性命令（git push +refspec 强制覆盖远端）：请人工确认后自行执行'} }
            } elseif ($sub -eq 'reset') {
                if ($seg.Contains('--hard')) {
                    return @{kind = 'deny'; reason = '破坏性命令（git reset --hard）：请人工确认后自行执行'} }
            } elseif ($sub -eq 'clean') {
                $fl = Get-GitFlags $seg
                if (($fl.short.Contains('f') -or $fl.long.Contains('force')) -and -not ($fl.short.Contains('n') -or $fl.long.Contains('dry-run'))) {
                    return @{kind = 'deny'; reason = '破坏性命令（git clean -f）：请人工确认后自行执行'} }
            } elseif ($sub -eq 'branch') {
                $fl = Get-GitFlags $seg
                if ($fl.short.Contains('D') -or (($fl.short.Contains('d') -or $fl.long.Contains('delete')) -and ($fl.short.Contains('f') -or $fl.long.Contains('force')))) {
                    return @{kind = 'deny'; reason = '破坏性命令（git branch -D 强删分支）：请人工确认后自行执行'} }
            } elseif ($sub -eq 'stash') {
                $rest = @($after -split '\s+' | Where-Object { $_.Length -gt 0 })
                if ($rest.Count -gt 0 -and $rest[0] -ceq 'clear') {
                    return @{kind = 'deny'; reason = '破坏性命令（git stash clear 清空全部 stash）：请人工确认后自行执行'} }
            } else {   # checkout / restore / switch
                if ((Test-ForceSwitch $after) -or (Test-CheckoutDiscards $after)) {
                    return @{kind = 'deny'; reason = '破坏性命令（git checkout/restore/switch 丢弃工作区改动）：请人工确认后自行执行'} }
            }
        }
        if (Test-RmDestructive $seg) {
            return @{kind = 'deny'; reason = '破坏性命令（rm 递归+强制，非临时目录或无操作数）：请人工确认后自行执行'}
        }
    }
    foreach ($w in $DENYLIST_WARN_SIGS) {
        if ($w[0].IsMatch($cmd)) {
            return @{kind = 'ask'; reason = ('crules-flutter warn 层：' + $w[1] + '——危险面大，确认无误后放行')}
        }
    }
    return @{kind = 'allow'; reason = ''}
}

# —— 归一（py L54-61 等价，D-a）：①\+NL、`+NL 双删 ③引号删 ④残余反引号删 ——
function Normalize-DenyList([string]$c) {
    $bt = $script:DENYLIST_BT
    $nl = [regex]::Escape([string]$script:DENYLIST_NL)
    $c = [regex]::Replace($c, ('\\\r?' + $nl), '')      # bash 续行（跨界串无害拼合）
    $c = [regex]::Replace($c, ($bt + '\r?' + $nl), '')  # PS 续行
    $c = [regex]::Replace($c, "['`"]", '')              # 引号删除（单双同 py 语义）
    $c = [regex]::Replace($c, [regex]::Escape($bt), '') # 残余反引号（转义拼接拼合，只增拦截面）
    # （勿写 .Replace($bt,'')：PS 重载绑到 Replace(char,char)，空串转 char 抛——pwsh 实测炸点）
    return $c
}

# 出口文案（py blocked L66 / warned L77 同文复制；「不要尝试绕过」系跨实现文案锁断言点）
$DENYLIST_TAIL = '；请需求方人工执行，不要尝试绕过（如需展示命令，直接在回复中写文本）'

# —— py strip_quotes L83-87 等价（归一后基本 no-op，纵深保留） ——
function Get-StripQuotes([string]$tok) {
    if ($tok.Length -ge 2 -and (($tok[0] -eq '"' -and $tok[$tok.Length - 1] -eq '"') -or ($tok[0] -eq "'" -and $tok[$tok.Length - 1] -eq "'"))) {
        return $tok.Substring(1, $tok.Length - 2)
    }
    return $tok
}

# —— py parse_flags L89-97 等价（D-c git 域；长名表小写系 D-b，短旗标字母保持大小写） ——
function Get-GitFlags([string]$seg) {
    $short = ''
    $longs = New-Object System.Collections.Generic.HashSet[string]
    foreach ($t in ($seg -split '\s+')) {
        if ($t.Length -lt 2 -or $t[0] -ne '-') { continue }
        if ($t.Length -ge 3 -and $t[1] -eq '-') {
            $v = $t.Substring(2)
            $i = $v.IndexOf('=')
            if ($i -ge 0) { $v = $v.Substring(0, $i) }
            [void]$longs.Add($v.ToLowerInvariant())
        } elseif ($t[1] -ne '-') {
            $short += $t.Substring(1)
        }
    }
    return @{short = $short; long = $longs}
}

# —— py checkout_discards L99-125 等价（批E 目标面判据；D-d TrimEnd 扩 \；:/ 与裸 : 照 py） ——
function Test-CheckoutDiscards([string]$after) {
    $toks = @($after -split '\s+' | Where-Object { $_.Length -gt 0 })
    $fl = Get-GitFlags $after
    if ($fl.short.Contains('b') -or $fl.short.Contains('c') -or $fl.long.Contains('branch') -or $fl.long.Contains('create')) {
        return $false }   # 建分支，非丢弃
    if (($fl.short.Contains('S') -or $fl.long.Contains('staged')) -and -not ($fl.short.Contains('W') -or $fl.long.Contains('worktree'))) {
        return $false }   # 仅暂存区（批E）
    foreach ($tok in $toks) {
        if ($tok -eq '--' -or $tok.StartsWith('-')) { continue }
        $t = Get-StripQuotes $tok
        $core = $t.TrimEnd('/', '\')
        if ($core -eq '') { $core = $t }   # py L122 `or t` 语义镜像（bare / 不早退——py 现状放）
        if ($core -eq '.' -or $core -eq '*' -or $core -eq ':') { return $true }
        if ($t.StartsWith(':/')) { return $true }
    }
    return $false
}

# —— py force_switch L127-132 等价（豁免集 b/c/s 与 branch/create/source 保持 py 语义） ——
function Test-ForceSwitch([string]$after) {
    $fl = Get-GitFlags $after
    $force = $fl.short.Contains('f') -or $fl.long.Contains('force')
    $exempt = ($fl.short.IndexOfAny([char[]]@('b', 'c', 's')) -ge 0) -or $fl.long.Contains('branch') -or $fl.long.Contains('create') -or $fl.long.Contains('source')
    return ($force -and -not $exempt)
}

# —— py rm 段 L169-180 等价 + D-c 别名域 + D-e 白名单 ——
function Test-RmDestructive([string]$seg) {
    $m = $DENYLIST_CMDLET_SIG.Match($seg)
    if (-not $m.Success) { return $false }
    $tokens = @($seg.Substring($m.Index) -split '\s+' | Where-Object { $_.Length -gt 0 })
    $fl = Get-RmFlags $tokens
    if (-not ($fl.Recurse -and $fl.Force)) { return $false }
    $paths = @()
    if ($tokens.Count -gt 1) {
        for ($i = 1; $i -lt $tokens.Count; $i++) {
            $t = $tokens[$i]
            if ($t.StartsWith('-')) { continue }
            if ($DENYLIST_REDIR.IsMatch($t)) { continue }
            if ($t -eq '$null') { continue }
            $paths += (Resolve-PsPath $t)
        }
    }
    if ($paths.Count -eq 0) { return $true }              # 空操作数即拦（v47 向量1）
    foreach ($p in $paths) {
        if ($p -eq 'UNRESOLVED') { return $true }          # 不可解析即拒（deny 方向）
        if (-not (Test-PsTempUnder $p)) { return $true }
    }
    return $false
}

# —— D-c rm 别名域三源旗标（bash 字母保大小写照 py；/x 与 PS 前缀小写化——cmd/PS 参数不区分） ——
function Get-RmFlags($tokens) {
    $r = $false; $f = $false
    foreach ($t in $tokens) {
        if ($t.Length -lt 2) { continue }
        if ($t[0] -eq '/') {
            $v = $t.Substring(1).ToLowerInvariant()
            if ($v -eq 's') { $r = $true }
            if ($v -eq 'q' -or $v -eq 'f') { $f = $true }
            continue
        }
        if ($t[0] -ne '-') { continue }
        $body = $t.Substring(1).TrimStart('-')
        if ($body.Length -eq 0) { continue }
        # 字母扫描仅限**捆绑短旗标形**（全体字符 ∈ {r,f}，如 -rf/-fr/-f/-r）——review R1：
        # 对长名扫描会误置（-Force 内含 r → 假 Recurse；-WhatIf 内含 f → 假 Force，dry-run 被拦）
        if ($body -cmatch '^[rf]+$') {
            foreach ($ch in $body.ToCharArray()) {
                if ($ch -ceq 'r') { $r = $true }
                if ($ch -ceq 'f') { $f = $true }
            }
        }
        $lb = $body.ToLowerInvariant()
        # PS 参数前缀缩写：用户写的是全称的**前缀**（-Re / -Rec / -fo…）——方向是 全称.StartsWith(输入)，
        # 非 输入.StartsWith(全称)。deny-by-default 取严：匹配任一全称前缀即置位（-fo/-f 命中 force、
        # -r/-R/-re 命中 recurse——即便 5.1 因 -Filter 歧义报错也拦，错命令无放行价值）
        if ('recurse'.StartsWith($lb) -or 'recursive'.StartsWith($lb)) { $r = $true }
        if ('force'.StartsWith($lb)) { $f = $true }
    }
    return @{Recurse = $r; Force = $f}
}

# —— D-e 字面串自展开 + 折叠 + 小写化 ——
function Resolve-PsPath([string]$tok) {
    $t = (Get-StripQuotes $tok).Replace('/', '\')
    if ($t -eq '~' -or $t.StartsWith('~\')) {
        $h = Get-UnsafeEnv 'HOME'
        if ([string]::IsNullOrEmpty($h)) { $h = Get-UnsafeEnv 'USERPROFILE' }
        if ([string]::IsNullOrEmpty($h)) { return 'UNRESOLVED' }
        $t = $h + $t.Substring(1)
    }
    if ($t.StartsWith('$env:\')) {
        $mm = $DENYLIST_PFE.Match($t.Substring(6))
        if (-not $mm.Success) { return 'UNRESOLVED' }
        $v = Get-UnsafeEnv $mm.Groups['name'].Value
        if ([string]::IsNullOrEmpty($v)) { return 'UNRESOLVED' }
        $t = $v + $mm.Groups['rest'].Value
    }
    $mm = $DENYLIST_PCT.Match($t)
    if ($mm.Success) {
        $v = Get-UnsafeEnv $mm.Groups['name'].Value
        if ([string]::IsNullOrEmpty($v)) { return 'UNRESOLVED' }
        $t = $v + $mm.Groups['rest'].Value
    }
    if ($t.Contains('$') -or $t.Contains('%')) { return 'UNRESOLVED' }
    return Collapse-DenyListPath $t
}

function Get-UnsafeEnv([string]$name) {
    try { return [Environment]::GetEnvironmentVariable($name) } catch { return $null }
}

# —— normpath 等价（纯字符串 ./.. 折叠，保绝对性/UNC/盘符；ToLowerInvariant 供不敏感比较） ——
function Collapse-DenyListPath([string]$p) {
    if ($p.Length -eq 0) { return '' }
    $p = $p.Replace('/', '\')   # 分隔符统一（白名单根 /tmp /var/folders 与 token 侧同源可比）
    $isUnc = $p.StartsWith('\\')
    $drive = ''
    if (-not $isUnc -and $p.Length -ge 2 -and [char]::IsLetter($p[0]) -and $p[1] -eq ':') {
        $drive = $p.Substring(0, 2).ToLowerInvariant() + '\'
        $p = $p.Substring(2)
    }
    $isAbs = $isUnc -or $drive.Length -gt 0 -or $p.StartsWith('\')
    $parts = @($p.Split('\') | Where-Object { $_.Length -gt 0 -and $_ -ne '.' })
    $st = New-Object System.Collections.Generic.List[string]
    foreach ($x in $parts) {
        $lx = $x.ToLowerInvariant()
        if ($lx -eq '..') { if ($st.Count -gt 0) { $st.RemoveAt($st.Count - 1) } }
        else { $st.Add($lx) }
    }
    $joined = $st -join '\'
    if ($isUnc) { return '\\' + $joined }
    if ($drive.Length -gt 0) { return $drive + $joined }
    if ($isAbs) { return '\' + $joined }
    return $joined
}

function Get-TempRoots {
    if ($script:DENYLIST_ROOTS) { return $script:DENYLIST_ROOTS }
    $roots = @()
    try { $roots += [IO.Path]::GetTempPath() } catch { }
    $roots += (Get-UnsafeEnv 'TEMP')
    $roots += (Get-UnsafeEnv 'TMP')
    $roots += '/tmp'
    $roots += '/var/folders'
    $script:DENYLIST_ROOTS = @($roots | Where-Object { -not [string]::IsNullOrEmpty($_) } |
        ForEach-Object { Collapse-DenyListPath $_ } | Where-Object { $_.Length -gt 0 })
    return $script:DENYLIST_ROOTS
}

function Test-PsTempUnder([string]$p) {
    # 根不 TrimEnd——/tmp 折叠为 \tmp（isAbs 保留），剥尾分隔符会把单段根剥成空致全拦；
    # 前缀比较时补分隔符（根若本身以 \ 结尾如 C:\T\，不重复加）
    foreach ($r in (Get-TempRoots)) {
        if ($p -eq $r) { return $true }
        $rr = if ($r.EndsWith('\')) { $r } else { $r + '\' }
        if ($p.StartsWith($rr)) { return $true }
    }
    return $false
}

# —— warn 层（py L182-193 结构照搬：全 deny 未中才到，deny 优先天然成立；D-f 扩集） ——
$DENYLIST_WARN_SIGS = @(
    ,@([regex]::new('\b(curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^;|]*\|\s*(?:sudo\s+)?(?:(?:ba|z|da)?sh|python3?|ruby|perl|cmd|powershell|iex|invoke-expression)\b', 'IgnoreCase'), '网络内容直接进解释器（curl/wget/iwr | sh/iex 等）')
    ,@([regex]::new('\b(iex|invoke-expression)\b[^;|]*\b(iwr|irm|invoke-webrequest|invoke-restmethod|curl|wget)\b', 'IgnoreCase'), '下载内容直接求值（iex (iwr …) 括号形）')
    ,@([regex]::new('\bchmod\b[^;|]*\s-R', 'IgnoreCase'), '递归改权限（chmod -R）')
    ,@([regex]::new('\bicacls\b[^;|]*\s/T\b', 'IgnoreCase'), '递归改权限（icacls /T）')
    ,@([regex]::new('(?:^\s*|[;&|\n]\s*)sudo\b', 'IgnoreCase'), '提权执行（sudo）')
    ,@([regex]::new('\bstart-process\b[^;|]*-verb\s+runas\b', 'IgnoreCase'), '提权执行（Start-Process -Verb RunAs）')
    ,@([regex]::new('\bgit\b[^;|]*\bfilter-(?:branch|repo)\b', 'IgnoreCase'), '重写历史（git filter-branch / filter-repo）')
)

# ========== 双源对照表（维护义务：改判据两源同改 + 双驱夹具全绿） ==========
# py L54-61 归一      ↔ Normalize-DenyList（D-a：无 \<word> 步；反引号并入删除）
# py L63-78 blocked/warned ↔ $DENYLIST_TAIL + 入口段 JSON（手工模板 + \ " 转义）
# py L80 GIT_SIG      ↔ $DENYLIST_GIT_SIG（IgnoreCase，D-b）
# py L81 RM_SIG        ↔ $DENYLIST_CMDLET_SIG（别名域扩集，D-c）
# py L83-87 strip_quotes ↔ Get-StripQuotes   py L89-97 parse_flags ↔ Get-GitFlags
# py L99-125 checkout_discards ↔ Test-CheckoutDiscards（D-d）
# py L127-132 force_switch     ↔ Test-ForceSwitch
# py L134-180 主循环/rm/白名单 ↔ Get-DenyListDecision / Test-RmDestructive / Get-RmFlags /
#                                Resolve-PsPath / Collapse-DenyListPath / Get-TempRoots（D-e）
# py L182-193 WARN_SIGS        ↔ $DENYLIST_WARN_SIGS（D-f）
# 有意差异全集：D-a / D-b（命令名折叠、git 旗标保区分）/ D-c / D-d / D-e / D-f——审读只查这六处。

# ========== 入口段（驱动置 $global:DENYLIST_LIB_ONLY=$true 点源时短路） ==========
if ($global:DENYLIST_LIB_ONLY) { return }
# 编码走 OpenStandardInput/Output + 显式 UTF8 流（review R4：[Console]::InputEncoding setter 依赖
# 附加控制台——无控制台宿主 spawn 下抛异常会 fail-open 整闸静默放行，且成功时改用户共享控制台码页；
# 流式构造无控制台依赖）
$raw = ''
try {
    $inStream = [Console]::OpenStandardInput()
    $reader = New-Object System.IO.StreamReader($inStream, (New-Object System.Text.UTF8Encoding($false)))
    $raw = $reader.ReadToEnd()
} catch { exit 0 }
$cmdIn = $null
try {
    $obj = ConvertFrom-Json $raw
    if ($null -ne $obj.tool_input) { $cmdIn = [string]$obj.tool_input.command }
} catch { exit 0 }
$d = Get-DenyListDecision $cmdIn
if ($d.kind -eq 'deny' -or $d.kind -eq 'ask') {
    $reason = $d.reason
    if ($d.kind -eq 'deny') { $reason += $DENYLIST_TAIL }
    $reason = $reason.Replace('\', '\\').Replace('"', '\"')
    $json = '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"' + $d.kind +
            '","permissionDecisionReason":"' + $reason + '"}}'
    try {
        $outStream = [Console]::OpenStandardOutput()
        $writer = New-Object System.IO.StreamWriter($outStream, (New-Object System.Text.UTF8Encoding($false)))
        $writer.Write($json); $writer.Flush()
    } catch { }
}
exit 0
