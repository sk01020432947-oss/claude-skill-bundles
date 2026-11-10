# palette-forge 우클릭 컨텍스트 메뉴 등록 (HKCU — 관리자 불필요)
# 이미지 파일(.jpg .jpeg .png .webp .bmp) 우클릭 → 팔레트 추출 (빠름 / 정밀·Claude)
$launcher = "$env:USERPROFILE\.claude\skills\palette-forge\launcher"
$exts = ".jpg", ".jpeg", ".png", ".webp", ".bmp"

foreach ($ext in $exts) {
    $base = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell"

    $quick = "$base\PaletteForge.Quick"
    New-Item -Path "$quick\command" -Force | Out-Null
    Set-ItemProperty -Path $quick -Name "MUIVerb" -Value "팔레트 추출 (빠름)"
    Set-ItemProperty -Path $quick -Name "Icon" -Value "shell32.dll,-322"
    Set-ItemProperty -Path "$quick\command" -Name "(Default)" -Value "`"$launcher\palette-quick.cmd`" `"%1`""

    $ai = "$base\PaletteForge.Claude"
    New-Item -Path "$ai\command" -Force | Out-Null
    Set-ItemProperty -Path $ai -Name "MUIVerb" -Value "팔레트 추출 (정밀·Claude)"
    Set-ItemProperty -Path $ai -Name "Icon" -Value "shell32.dll,-25"
    Set-ItemProperty -Path "$ai\command" -Name "(Default)" -Value "`"$launcher\palette-claude.cmd`" `"%1`""
}
Write-Host "등록 완료: 이미지 우클릭 → '팔레트 추출 (빠름/정밀)' ($($exts -join ', '))"
Write-Host "해제: unregister-context-menu.ps1 실행"
