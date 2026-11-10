# palette-forge 우클릭 컨텍스트 메뉴 해제
$exts = ".jpg", ".jpeg", ".png", ".webp", ".bmp"
foreach ($ext in $exts) {
    foreach ($key in "PaletteForge.Quick", "PaletteForge.Claude") {
        $path = "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\$key"
        if (Test-Path $path) { Remove-Item -Path $path -Recurse -Force }
    }
}
Write-Host "해제 완료"
