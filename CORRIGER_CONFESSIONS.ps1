# CORRIGER_CONFESSIONS.ps1 - Remplace Archive.org par Suno CDN

$filePath = "C:\ScriptBible\bible-chantee\confessions.html"
$content = Get-Content $filePath -Raw -Encoding UTF8

# Ancien système : BASE + filename
$oldCode = @'
var BASE="https://archive.org/download/confessions-bible-chantee/";
var C=[
{n:1,i:"&#x1F60A;",f:"01_Joie"
'@

# Nouveau système : URLs directes Suno CDN
$newCode = @'
var URLS={
"01_Joie":"https://cdn1.suno.ai/69557118-0717-488a-8b75-b5171da4be10.mp3",
"02_Gueri":"https://cdn1.suno.ai/d09a0a0a-41f2-49c0-8e49-620c60031727.mp3",
"03_Sante":"https://cdn1.suno.ai/88cd18c4-4be4-44e9-bdeb-da0363f369d3.mp3",
"04_Vainqueur":"https://cdn1.suno.ai/723cecb4-b117-460d-814c-b3590f5fb16a.mp3",
"05_Prospere":"https://cdn1.suno.ai/bb8450bf-2d64-4793-93b3-9f3350e2dd9c.mp3",
"06_Reconnaissant":"https://cdn1.suno.ai/7e4e12f4-891e-43cb-ab02-893c60dae098.mp3",
"07_Heureux":"https://cdn1.suno.ai/c2c15ac9-563b-4b3f-a68b-7fa99503425e.mp3",
"08_Beni":"https://cdn1.suno.ai/4a4f7809-519d-444a-80ef-6bf853c7fb14.mp3",
"09_Amen":"https://cdn1.suno.ai/8b14d0ee-1611-4222-8f9c-108db657fa96.mp3",
"10_Shalom":"https://cdn1.suno.ai/1fefd605-4d8d-4af2-93af-67645e0bf825.mp3"
};
var C=[
{n:1,i:"&#x1F60A;",f:"01_Joie"
'@

$content = $content.Replace($oldCode, $newCode)

# Corriger aussi la ligne audio.src
$content = $content.Replace("document.getElementById('au').src=BASE+c.f+'.mp3';", "document.getElementById('au').src=URLS[c.f];")

# Sauvegarder
$content | Out-File -FilePath $filePath -Encoding UTF8 -NoNewline
Write-Host "[OK] confessions.html corrige (URLs Suno)" -ForegroundColor Green

# Git
Set-Location "C:\ScriptBible\bible-chantee"
git add confessions.html
git commit -m "Fix confessions audio: use Suno CDN"
git push

Write-Host "[OK] Deploye" -ForegroundColor Green
Write-Host "Teste: https://scassani1964.github.io/bible-chantee/confessions.html" -ForegroundColor Cyan
