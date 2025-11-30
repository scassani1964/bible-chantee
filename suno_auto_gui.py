#!/usr/bin/env python3
"""
suno_auto_gui.py - Automation script for generating Bible Chantee songs using Suno AI

This script automates the Suno web interface to generate worship songs
for Bible chapters in French.

Requirements:
    pip install pyautogui pyperclip pillow

Usage:
    python suno_auto_gui.py --book 06 --chapter 1
    python suno_auto_gui.py --book 06 --start 1 --end 24
    python suno_auto_gui.py --config config.json
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import pyautogui
    import pyperclip
except ImportError:
    print("Required packages not found. Install with:")
    print("  pip install pyautogui pyperclip pillow")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('suno_auto_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bible books data (French names)
BIBLE_BOOKS = {
    "01": {"name": "Genese", "chapters": 50},
    "02": {"name": "Exode", "chapters": 40},
    "03": {"name": "Levitique", "chapters": 27},
    "04": {"name": "Nombres", "chapters": 36},
    "05": {"name": "Deuteronome", "chapters": 34},
    "06": {"name": "Josue", "chapters": 24},
    "07": {"name": "Juges", "chapters": 21},
    "08": {"name": "Ruth", "chapters": 4},
    "09": {"name": "1 Samuel", "chapters": 31},
    "10": {"name": "2 Samuel", "chapters": 24},
    "11": {"name": "1 Rois", "chapters": 22},
    "12": {"name": "2 Rois", "chapters": 25},
    "13": {"name": "1 Chroniques", "chapters": 29},
    "14": {"name": "2 Chroniques", "chapters": 36},
    "15": {"name": "Esdras", "chapters": 10},
    "16": {"name": "Nehemie", "chapters": 13},
    "17": {"name": "Esther", "chapters": 10},
    "18": {"name": "Job", "chapters": 42},
    "19": {"name": "Psaumes", "chapters": 150},
    "20": {"name": "Proverbes", "chapters": 31},
    "21": {"name": "Ecclesiaste", "chapters": 12},
    "22": {"name": "Cantique", "chapters": 8},
    "23": {"name": "Esaie", "chapters": 66},
    "24": {"name": "Jeremie", "chapters": 52},
    "25": {"name": "Lamentations", "chapters": 5},
    "26": {"name": "Ezechiel", "chapters": 48},
    "27": {"name": "Daniel", "chapters": 12},
    "28": {"name": "Osee", "chapters": 14},
    "29": {"name": "Joel", "chapters": 3},
    "30": {"name": "Amos", "chapters": 9},
    "31": {"name": "Abdias", "chapters": 1},
    "32": {"name": "Jonas", "chapters": 4},
    "33": {"name": "Michee", "chapters": 7},
    "34": {"name": "Nahum", "chapters": 3},
    "35": {"name": "Habacuc", "chapters": 3},
    "36": {"name": "Sophonie", "chapters": 3},
    "37": {"name": "Aggee", "chapters": 2},
    "38": {"name": "Zacharie", "chapters": 14},
    "39": {"name": "Malachie", "chapters": 4},
    "40": {"name": "Matthieu", "chapters": 28},
    "41": {"name": "Marc", "chapters": 16},
    "42": {"name": "Luc", "chapters": 24},
    "43": {"name": "Jean", "chapters": 21},
    "44": {"name": "Actes", "chapters": 28},
    "45": {"name": "Romains", "chapters": 16},
    "46": {"name": "1 Corinthiens", "chapters": 16},
    "47": {"name": "2 Corinthiens", "chapters": 13},
    "48": {"name": "Galates", "chapters": 6},
    "49": {"name": "Ephesiens", "chapters": 6},
    "50": {"name": "Philippiens", "chapters": 4},
    "51": {"name": "Colossiens", "chapters": 4},
    "52": {"name": "1 Thessaloniciens", "chapters": 5},
    "53": {"name": "2 Thessaloniciens", "chapters": 3},
    "54": {"name": "1 Timothee", "chapters": 6},
    "55": {"name": "2 Timothee", "chapters": 4},
    "56": {"name": "Tite", "chapters": 3},
    "57": {"name": "Philemon", "chapters": 1},
    "58": {"name": "Hebreux", "chapters": 13},
    "59": {"name": "Jacques", "chapters": 5},
    "60": {"name": "1 Pierre", "chapters": 5},
    "61": {"name": "2 Pierre", "chapters": 3},
    "62": {"name": "1 Jean", "chapters": 5},
    "63": {"name": "2 Jean", "chapters": 1},
    "64": {"name": "3 Jean", "chapters": 1},
    "65": {"name": "Jude", "chapters": 1},
    "66": {"name": "Apocalypse", "chapters": 22},
}


@dataclass
class SunoConfig:
    """Configuration for Suno automation."""
    # Timing settings (in seconds)
    click_delay: float = 0.5
    typing_delay: float = 0.05
    wait_after_click: float = 1.0
    generation_timeout: int = 300  # 5 minutes max wait for generation
    poll_interval: float = 5.0  # Check every 5 seconds

    # Screen positions (to be calibrated)
    create_button: tuple = (0, 0)
    custom_mode_button: tuple = (0, 0)
    lyrics_input: tuple = (0, 0)
    style_input: tuple = (0, 0)
    title_input: tuple = (0, 0)
    generate_button: tuple = (0, 0)
    download_button: tuple = (0, 0)

    # Style settings
    music_style: str = "worship french, acoustic guitar, piano, soft drums, reverent, spiritual"

    # Lyrics directory
    lyrics_dir: str = "./lyrics"

    # Output directory
    output_dir: str = "./output"


class SunoAutomation:
    """Automates Suno AI web interface for Bible Chantee generation."""

    def __init__(self, config: SunoConfig):
        self.config = config
        self.is_calibrated = False

        # Ensure output directory exists
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # PyAutoGUI settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = config.click_delay

    def calibrate(self) -> bool:
        """
        Interactive calibration to capture screen positions.
        Returns True if calibration successful.
        """
        print("\n" + "="*60)
        print("SUNO AUTO GUI - CALIBRATION MODE")
        print("="*60)
        print("\nThis will capture the screen positions of Suno UI elements.")
        print("Make sure Suno is open in your browser before proceeding.")
        print("\nFor each element, position your mouse over it and press ENTER.")
        print("Press Ctrl+C at any time to cancel.\n")

        elements = [
            ("create_button", "the CREATE button"),
            ("custom_mode_button", "the CUSTOM MODE toggle/button"),
            ("lyrics_input", "the LYRICS text input area"),
            ("style_input", "the STYLE OF MUSIC input"),
            ("title_input", "the TITLE input"),
            ("generate_button", "the CREATE/GENERATE button"),
            ("download_button", "a song's DOWNLOAD button (any example)"),
        ]

        positions = {}

        try:
            for element_name, description in elements:
                input(f"Position mouse over {description}, then press ENTER...")
                pos = pyautogui.position()
                positions[element_name] = (pos.x, pos.y)
                print(f"  Captured: {element_name} = {pos}")

            # Save calibration
            self._save_calibration(positions)
            self._load_calibration(positions)
            self.is_calibrated = True

            print("\nCalibration complete! Positions saved to 'suno_calibration.json'")
            return True

        except KeyboardInterrupt:
            print("\nCalibration cancelled.")
            return False

    def _save_calibration(self, positions: dict):
        """Save calibration data to file."""
        with open("suno_calibration.json", "w") as f:
            json.dump(positions, f, indent=2)

    def _load_calibration(self, positions: dict):
        """Load calibration into config."""
        for key, value in positions.items():
            setattr(self.config, key, tuple(value))

    def load_calibration_file(self) -> bool:
        """Load calibration from file if exists."""
        try:
            with open("suno_calibration.json", "r") as f:
                positions = json.load(f)
            self._load_calibration(positions)
            self.is_calibrated = True
            logger.info("Loaded calibration from file")
            return True
        except FileNotFoundError:
            logger.warning("No calibration file found. Run with --calibrate first.")
            return False

    def get_lyrics_file(self, book_num: str, chapter: int) -> Optional[Path]:
        """Get the lyrics file path for a given book and chapter."""
        book_name = BIBLE_BOOKS.get(book_num, {}).get("name", "Unknown")
        chapter_str = str(chapter).zfill(2)

        # Try different naming conventions
        patterns = [
            f"{book_num}_{book_name}_{chapter_str}.txt",
            f"{book_num}_{book_name}_chapitre_{chapter}.txt",
            f"{book_name}_{chapter_str}.txt",
            f"{book_name}_chapitre_{chapter}.txt",
        ]

        lyrics_path = Path(self.config.lyrics_dir)

        for pattern in patterns:
            file_path = lyrics_path / pattern
            if file_path.exists():
                return file_path

        # Also check subdirectories
        for pattern in patterns:
            for subdir in lyrics_path.iterdir():
                if subdir.is_dir():
                    file_path = subdir / pattern
                    if file_path.exists():
                        return file_path

        return None

    def get_output_filename(self, book_num: str, chapter: int) -> str:
        """Generate the output filename for a generated song."""
        book_name = BIBLE_BOOKS.get(book_num, {}).get("name", "Unknown")
        chapter_str = str(chapter).zfill(2)
        return f"{book_num}_{book_name}_{chapter_str}.mp3"

    def click_element(self, element_name: str):
        """Click on a calibrated element."""
        pos = getattr(self.config, element_name)
        if pos == (0, 0):
            raise ValueError(f"Element '{element_name}' not calibrated")

        logger.debug(f"Clicking {element_name} at {pos}")
        pyautogui.click(pos[0], pos[1])
        time.sleep(self.config.wait_after_click)

    def type_text(self, text: str, clear_first: bool = True):
        """Type text with optional clearing of existing content."""
        if clear_first:
            # Select all and delete
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.1)

        # Use clipboard for faster and more reliable input
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)

    def generate_song(self, book_num: str, chapter: int) -> bool:
        """
        Generate a song for a specific Bible chapter.
        Returns True if successful.
        """
        if not self.is_calibrated:
            if not self.load_calibration_file():
                logger.error("Not calibrated. Run with --calibrate first.")
                return False

        book_info = BIBLE_BOOKS.get(book_num)
        if not book_info:
            logger.error(f"Invalid book number: {book_num}")
            return False

        book_name = book_info["name"]
        max_chapters = book_info["chapters"]

        if chapter < 1 or chapter > max_chapters:
            logger.error(f"{book_name} has only {max_chapters} chapters")
            return False

        # Get lyrics
        lyrics_file = self.get_lyrics_file(book_num, chapter)
        if not lyrics_file:
            logger.error(f"Lyrics file not found for {book_name} chapter {chapter}")
            logger.info(f"Expected in: {self.config.lyrics_dir}")
            return False

        with open(lyrics_file, 'r', encoding='utf-8') as f:
            lyrics = f.read().strip()

        if not lyrics:
            logger.error(f"Lyrics file is empty: {lyrics_file}")
            return False

        title = f"{book_name} Chapitre {chapter}"

        logger.info(f"Generating: {title}")
        logger.info(f"Lyrics file: {lyrics_file}")

        try:
            # Step 1: Click Create button
            logger.info("Step 1: Clicking Create button...")
            self.click_element("create_button")
            time.sleep(1)

            # Step 2: Enable Custom Mode
            logger.info("Step 2: Enabling Custom Mode...")
            self.click_element("custom_mode_button")
            time.sleep(0.5)

            # Step 3: Enter lyrics
            logger.info("Step 3: Entering lyrics...")
            self.click_element("lyrics_input")
            time.sleep(0.3)
            self.type_text(lyrics)
            time.sleep(0.5)

            # Step 4: Enter style
            logger.info("Step 4: Setting music style...")
            self.click_element("style_input")
            time.sleep(0.3)
            self.type_text(self.config.music_style)
            time.sleep(0.5)

            # Step 5: Enter title
            logger.info("Step 5: Setting title...")
            self.click_element("title_input")
            time.sleep(0.3)
            self.type_text(title)
            time.sleep(0.5)

            # Step 6: Click Generate
            logger.info("Step 6: Starting generation...")
            self.click_element("generate_button")

            logger.info("Generation started! Waiting for completion...")
            logger.info(f"(Timeout: {self.config.generation_timeout} seconds)")

            # Wait for generation (user can manually check/download)
            print("\n" + "-"*40)
            print("Song generation initiated!")
            print("Please manually verify and download when ready.")
            print("-"*40 + "\n")

            return True

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return False

    def batch_generate(self, book_num: str, start_chapter: int, end_chapter: int,
                       delay_between: int = 60):
        """Generate multiple chapters in sequence."""
        book_info = BIBLE_BOOKS.get(book_num)
        if not book_info:
            logger.error(f"Invalid book number: {book_num}")
            return

        book_name = book_info["name"]
        max_chapters = book_info["chapters"]

        end_chapter = min(end_chapter, max_chapters)

        logger.info(f"Batch generation: {book_name} chapters {start_chapter}-{end_chapter}")

        for chapter in range(start_chapter, end_chapter + 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing chapter {chapter}/{end_chapter}")
            logger.info(f"{'='*50}")

            success = self.generate_song(book_num, chapter)

            if success and chapter < end_chapter:
                logger.info(f"Waiting {delay_between} seconds before next chapter...")
                time.sleep(delay_between)

        logger.info("\nBatch generation complete!")


def create_sample_lyrics_structure():
    """Create sample lyrics directory structure."""
    lyrics_dir = Path("./lyrics")
    lyrics_dir.mkdir(exist_ok=True)

    sample_file = lyrics_dir / "06_Josue_01.txt"
    if not sample_file.exists():
        sample_content = """[Intro]
Josue, serviteur de l'Eternel
Leve-toi et traverse le Jourdain

[Verse 1]
Moise mon serviteur est mort
Maintenant leve-toi, passe ce Jourdain
Toi et tout ce peuple ensemble
Vers le pays que je vous donne

[Chorus]
Fortifie-toi, prends courage
L'Eternel ton Dieu sera avec toi
Partout ou tu iras
Il ne te delaissera pas

[Verse 2]
Tout lieu que foulera ton pied
Je vous le donne comme promis
De ce desert au grand Liban
Jusqu'au fleuve, l'Euphrate

[Chorus]
Fortifie-toi, prends courage
L'Eternel ton Dieu sera avec toi
Partout ou tu iras
Il ne te delaissera pas

[Outro]
Sois fort et courageux
Car l'Eternel est avec toi
"""
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print(f"Created sample lyrics file: {sample_file}")

    # Create README
    readme_file = lyrics_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# Lyrics Directory

Place your Bible chapter lyrics files here.

## Naming Convention
Files should be named: `{book_num}_{BookName}_{chapter_num}.txt`

Examples:
- `06_Josue_01.txt`
- `06_Josue_02.txt`
- `07_Juges_01.txt`

## Lyrics Format
Use Suno-compatible tags:
- `[Intro]`
- `[Verse 1]`, `[Verse 2]`, etc.
- `[Chorus]`
- `[Bridge]`
- `[Outro]`
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Created: {readme_file}")


def list_books():
    """Print a list of all Bible books with their numbers."""
    print("\nBible Books Reference:")
    print("=" * 50)
    print("\nOld Testament:")
    for num in range(1, 40):
        num_str = str(num).zfill(2)
        info = BIBLE_BOOKS.get(num_str, {})
        print(f"  {num_str}: {info.get('name', '?'):20} ({info.get('chapters', '?')} chapters)")

    print("\nNew Testament:")
    for num in range(40, 67):
        num_str = str(num).zfill(2)
        info = BIBLE_BOOKS.get(num_str, {})
        print(f"  {num_str}: {info.get('name', '?'):20} ({info.get('chapters', '?')} chapters)")


def main():
    parser = argparse.ArgumentParser(
        description="Automate Suno AI for Bible Chantee song generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --calibrate              # Calibrate screen positions
  %(prog)s --list                   # List all Bible books
  %(prog)s --book 06 --chapter 1    # Generate Josue chapter 1
  %(prog)s --book 06 --start 1 --end 24  # Generate Josue chapters 1-24
  %(prog)s --init                   # Create sample lyrics structure
        """
    )

    parser.add_argument('--calibrate', action='store_true',
                        help='Run calibration to capture screen positions')
    parser.add_argument('--list', action='store_true',
                        help='List all Bible books with numbers')
    parser.add_argument('--init', action='store_true',
                        help='Create sample lyrics directory structure')
    parser.add_argument('--book', type=str,
                        help='Book number (e.g., 06 for Josue)')
    parser.add_argument('--chapter', type=int,
                        help='Chapter number to generate')
    parser.add_argument('--start', type=int,
                        help='Start chapter for batch generation')
    parser.add_argument('--end', type=int,
                        help='End chapter for batch generation')
    parser.add_argument('--delay', type=int, default=60,
                        help='Delay between generations in batch mode (default: 60s)')
    parser.add_argument('--style', type=str,
                        help='Custom music style description')
    parser.add_argument('--lyrics-dir', type=str, default='./lyrics',
                        help='Directory containing lyrics files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle special commands
    if args.list:
        list_books()
        return

    if args.init:
        create_sample_lyrics_structure()
        return

    # Create config
    config = SunoConfig()
    if args.lyrics_dir:
        config.lyrics_dir = args.lyrics_dir
    if args.style:
        config.music_style = args.style

    # Create automation instance
    suno = SunoAutomation(config)

    # Handle calibration
    if args.calibrate:
        suno.calibrate()
        return

    # Validate book argument for generation
    if not args.book:
        parser.print_help()
        print("\nError: --book is required for generation (or use --calibrate, --list, --init)")
        return

    # Pad book number
    book_num = args.book.zfill(2)

    if book_num not in BIBLE_BOOKS:
        print(f"Error: Invalid book number '{args.book}'. Use --list to see valid options.")
        return

    # Single chapter or batch generation
    if args.start and args.end:
        suno.batch_generate(book_num, args.start, args.end, args.delay)
    elif args.chapter:
        suno.generate_song(book_num, args.chapter)
    else:
        print("Error: Specify --chapter or --start/--end for generation")
        parser.print_help()


if __name__ == "__main__":
    main()
