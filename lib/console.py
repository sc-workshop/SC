import sys

import colorama

import platform

from shutil import get_terminal_size


if platform.system() == "Windows":
    colorama.init()


class Console:
    @staticmethod
    def title(message):
        print(colorama.Fore.GREEN + message.center(get_terminal_size().columns) + colorama.Style.RESET_ALL)

    @staticmethod
    def info(message: str):
        print(colorama.Fore.GREEN + f"[INFO] {message}" + colorama.Style.RESET_ALL)

    @staticmethod
    def warning(message: str):
        print(colorama.Fore.MAGENTA + f"[WARNING] {message}" + colorama.Style.RESET_ALL)

    @staticmethod
    def error(message: str):
        print(colorama.Fore.RED + f"[ERROR] {message}" + colorama.Style.RESET_ALL)

    @staticmethod
    def progress_bar(message, current, total, start=0, end=100):
        sys.stdout.write(
            colorama.Fore.GREEN + f"\r[{((current + 1) * end + start) // total + start}%] {message}" + colorama.Style.RESET_ALL)
