import os

from shutil import rmtree

from zipfile import ZipFile
from zipfile import BadZipfile

from .dom.document import DOMDocument

import io
import struct
# TODO move to custom zip/fla reader


class XFL:
    @staticmethod
    def load(projectpath: str):
        if os.path.isfile(projectpath):
            if os.path.splitext(projectpath)[1] != ".fla":
                raise Exception(f"File is not \".fla\": {projectpath}")

            fla_file = open(projectpath, "rb")
            folder = os.path.splitext(projectpath)[0]

            try:
                with ZipFile(fla_file, 'r') as file:
                    file.extractall(folder)

            except BadZipfile:
                EOCD_FORMAT = "<4s4H2LH"
                EOCD_SIZE = 22
                CDIR_SIZE_CORRECTION = 54

                real_seek = fla_file.seek
                real_read = fla_file.read

                def fake_seek(self, offset, whence=io.SEEK_SET):
                    if offset == -EOCD_SIZE and whence == io.SEEK_END:
                        # Perform the seek and get the zip's total size
                        zip_size = EOCD_SIZE + real_seek(offset, whence)
                        eocd_data = self.read()
                        eocd = list(struct.unpack(EOCD_FORMAT, eocd_data))
                        cdir_size = eocd[5]
                        cdir_offset = eocd[6]

                        # Assuming the central dir offset is right, is the size wrong?
                        actual_cdir_size = zip_size - cdir_offset - EOCD_SIZE
                        delta = cdir_size - actual_cdir_size
                        if delta == CDIR_SIZE_CORRECTION:
                            eocd[5] -= CDIR_SIZE_CORRECTION
                            eocd_data = struct.pack(EOCD_FORMAT, *eocd)
                        elif delta != 0:
                            raise Exception(
                                f"Central directory size is off by an unexpected amount: {delta}"
                            )

                        self.seek = real_seek

                        # Fake the next read() to return `eocd_data`
                        def fake_read(self, size=-1):
                            if size != -1:
                                # We expect read() to be called with no arguments
                                raise Exception(f"Expected size of -1, not {size}")
                            self.read = real_read
                            return eocd_data

                        self.read = fake_read.__get__(self)
                    else:
                        return real_seek(offset, whence)

                # __get__ turns a function into a method: https://stackoverflow.com/a/46757134
                fla_file.seek = fake_seek.__get__(fla_file)

                with ZipFile(fla_file, 'r') as file:
                    file.extractall(folder)

            return XFL.load(folder)

        elif os.path.isdir(projectpath):
            document = DOMDocument()
            document.load(projectpath)
            return document

        raise Exception(f"Project does not exist: {projectpath}")

    @staticmethod
    def save(filepath: str, document: DOMDocument):
        if os.path.splitext(filepath)[1] != ".fla":
            raise Exception(f"File must be \".fla\": {filepath}")

        projectpath = os.path.splitext(filepath)[0]

        if not os.path.exists(projectpath):
            os.mkdir(projectpath)

        document.save(projectpath)

        with ZipFile(filepath, 'w') as file:
            for root, _, files in os.walk(projectpath):
                for filename in files:
                    file.write(os.path.join(root, filename),
                               os.path.relpath(os.path.join(root, filename), os.path.join(projectpath, '')))

        rmtree(projectpath)
