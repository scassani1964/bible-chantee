# AJOUTER_TITRES.ps1 - Modifie l'affichage des titres
# Format: "Ch.01 - Titre du chapitre" au lieu de "Livre - Chapitre 1"

$indexPath = "C:\ScriptBible\bible-chantee\index.html"
$content = Get-Content $indexPath -Raw -Encoding UTF8

# Ancien code
$oldCode = "document.getElementById('player-title').textContent = book.name + ' - Chapitre ' + chapter;"

# Nouveau code - extrait le titre depuis les paroles
$newCode = @"
// Extraire titre depuis paroles (format: "Livre X - Titre")
            let displayTitle = book.name + ' - Ch.' + String(chapter).padStart(2, '0');
            if (chapterLyrics[currentBook] && chapterLyrics[currentBook][chapter]) {
                const firstLine = chapterLyrics[currentBook][chapter].split('\n')[0];
                const titleMatch = firstLine.match(/[–-]\s*(.+)$/);
                if (titleMatch) {
                    displayTitle = book.name + ' Ch.' + String(chapter).padStart(2, '0') + ' - ' + titleMatch[1].trim();
                }
            }
            document.getElementById('player-title').textContent = displayTitle;
"@

$content = $content.Replace($oldCode, $newCode)

# Sauvegarder
$content | Out-File -FilePath $indexPath -Encoding UTF8 -NoNewline
Write-Host "[OK] Titres modifies dans index.html" -ForegroundColor Green

# Git
Set-Location "C:\ScriptBible\bible-chantee"
git add index.html
git commit -m "Add chapter titles from lyrics"
git push

Write-Host "[OK] Deploye sur GitHub" -ForegroundColor Green
Write-Host "Teste: https://scassani1964.github.io/bible-chantee/" -ForegroundColor Cyan
