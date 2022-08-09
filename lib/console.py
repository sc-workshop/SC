import sys

import colorama

import platform

if platform.system() == "Windows":
    colorama.init()


class Console:
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
        sys.stdout.write(f"\r[{((current + 1) * end + start) // total + start}%] {message}")
    
    @staticmethod
    def percent(current, total):
        return (current + 1) * 100 // total


if __name__ == "__main__":
    Console.info("Simple message!")
    Console.warning("Oops!")
    Console.error("Ban mfkr.")

    n = 999999
    for x in range(n):
        Console.progress_bar("Loading...", x, n)
    print()
    
    Console.info("You gay!")
