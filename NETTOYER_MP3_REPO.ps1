# NETTOYER_MP3_REPO.ps1 - Déplace MP3 du repo vers Drive et supprime doublons

Write-Host "=== NETTOYAGE MP3 ===" -ForegroundColor Cyan

# 1. Supprimer doublon Ruth sur Drive
$doublon = "G:\Mon Drive\BibleChantee\08_MP3_Ruth\Ruth 04 - Le Redempteur et la Promesse.mp3"
if (Test-Path $doublon) {
    Remove-Item $doublon -Force
    Write-Host "[OK] Doublon Ruth supprime" -ForegroundColor Green
}

# 2. Déplacer MP3 Psaumes du repo vers Drive
$source = "C:\ScriptBible\bible-chantee"
$destPsaumes = "G:\Mon Drive\BibleChantee\19_MP3_Psaumes"

# Créer dossier si nécessaire
if (-not (Test-Path $destPsaumes)) {
    New-Item -Path $destPsaumes -ItemType Directory -Force | Out-Null
}

# Compter avant
$mp3Count = (Get-ChildItem "$source\*.mp3").Count
Write-Host "MP3 dans repo: $mp3Count" -ForegroundColor Yellow

# Déplacer (seulement si pas déjà sur Drive)
$moved = 0
$skipped = 0
Get-ChildItem "$source\*.mp3" | ForEach-Object {
    $destFile = Join-Path $destPsaumes $_.Name
    if (-not (Test-Path $destFile)) {
        Move-Item $_.FullName $destFile
        $moved++
    } else {
        # Fichier existe déjà, supprimer du repo
        Remove-Item $_.FullName -Force
        $skipped++
    }
}

Write-Host "[OK] Deplaces: $moved, Doublons supprimes: $skipped" -ForegroundColor Green

# 3. Commit changements Git
Set-Location $source
git add -A
git commit -m "Remove MP3 files (using Suno CDN now)"
git push

Write-Host ""
Write-Host "=== TERMINE ===" -ForegroundColor Green
Write-Host "MP3 deplaces vers: $destPsaumes" -ForegroundColor Cyan
