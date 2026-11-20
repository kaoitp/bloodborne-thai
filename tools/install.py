"""Installer for the enggb game files."""

from pathlib import Path
import shutil
import sys

import build


FILES = (
    *(build.archive_path(Path(), name) for name in build.ARCHIVES),
    Path("menu") / build.LANGUAGE / "font.gfx",
)


def copy_files(source, destination):
    for relative in FILES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)


def update(game, action):
    game = game.resolve(strict=True)
    if game.name.lower() == "dvdroot_ps4":
        game = game.parent
    target = game / "dvdroot_ps4"
    backup = game / "bloodborne-thai-backup"
    work = game / "bloodborne-thai-work"
    if any(not (target / relative).is_file() for relative in FILES):
        raise ValueError("Game files missing. Select CUSA03173 or its dvdroot_ps4 folder.")

    work.mkdir()
    keep_work = False
    try:
        previous = work / "previous"
        staged = work / "staged"
        updating = action == "install" and backup.exists()
        if updating or action == "restore":
            if any(not (backup / relative).is_file() for relative in FILES):
                raise ValueError("Original backup files are missing or incomplete.")
        copy_files(target, previous)
        if action == "install":
            for relative in FILES:
                (staged / relative).parent.mkdir(parents=True, exist_ok=True)
            build.GAME = staged
            build.ORIGINAL = backup if updating else previous
            build.build()
            if not updating:
                copy_files(previous, work / "backup")
                (work / "backup").rename(backup)
        else:
            copy_files(backup, staged)

        replaced = []
        try:
            for relative in FILES:
                (staged / relative).replace(target / relative)
                replaced.append(relative)
            if action == "restore":
                backup.rename(work / "backup")
        except OSError:
            keep_work = True
            for relative in reversed(replaced):
                (previous / relative).replace(target / relative)
            keep_work = False
            raise
    finally:
        if not keep_work:
            shutil.rmtree(work)
    return updating


def main():
    if getattr(sys, "frozen", False):
        build.PROJECT = Path(sys._MEIPASS)
    if len(sys.argv) == 3 and sys.argv[1] in {"install", "restore"}:
        action, folder = sys.argv[1:]
    elif len(sys.argv) in {1, 2}:
        choice = input("[1] Install / Update Thai  [2] Restore original  [Enter] Exit: ").strip()
        if choice not in {"1", "2"}:
            return
        action = {"1": "install", "2": "restore"}[choice]
        folder = sys.argv[1] if len(sys.argv) == 2 else input("Drop or paste your game folder here: ")
    else:
        raise ValueError(f"Usage: {Path(sys.argv[0]).name} [install|restore GAME_FOLDER]")
    folder = folder.strip().strip('"')
    if not folder:
        raise ValueError("Select a game folder.")
    updating = update(Path(folder), action)
    if action == "restore":
        print("Original files restored.")
    else:
        result = "updated" if updating else "installed"
        print(f"Thai {result}. Select English (UK) in the game.")


if __name__ == "__main__":
    try:
        main()
    except (Exception, SystemExit) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
