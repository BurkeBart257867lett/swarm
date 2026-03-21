$resp = Invoke-WebRequest -Uri "https://redacted-website-production.up.railway.app/" -UseBasicParsing
$html = $resp.Content
$checks = @(
    @{ name="Skill section title"; pattern="REDACTED TERMINAL" },
    @{ name="Install step"; pattern="Install Claude Code" },
    @{ name="SKILL.md curl command"; pattern="SKILL.md" },
    @{ name="Command reference"; pattern="/summon" },
    @{ name="GROQ note"; pattern="GROQ_API_KEY" },
    @{ name="Nav link"; pattern='href="#skill"' }
)
foreach ($c in $checks) {
    if ($html -match [regex]::Escape($c.pattern)) {
        Write-Host "PASS: $($c.name)"
    } else {
        Write-Host "FAIL: $($c.name)"
    }
}
