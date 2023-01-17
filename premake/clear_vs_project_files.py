import os

import glob
import pathlib


def main():
    EXT_FILTERS = [
        ".sln",
        ".vcxproj",
        ".filters",  # must be ".vcxproj.filters" but os module says no.
        ".user"  # must be ".vcxproj.user" but os module says no.
    ]
    
    def visit_dir(dirname):
        dir = os.listdir(dirname)
        for item in dir:
            absolute = os.path.join(dirname, item)

            if os.path.isdir(absolute):
                print(f"{absolute} is directory")
                visit_dir(absolute)
            
            if os.path.isfile(absolute):
                ext = os.path.splitext(item)[1]

                if ext in EXT_FILTERS:
                    print(f"{absolute} must be removed")
                    os.remove(absolute)
                else:
                    print(f"{absolute} is file")

    visit_dir("../")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
