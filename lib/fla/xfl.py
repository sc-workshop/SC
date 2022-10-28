import io
import os
import struct
import zipfile
from shutil import rmtree

from lib.fla import DOMDocument

# TODO: move to custom zip/fla reader
EOCD_FORMAT = "<4s4H2LH"
EOCD_SIZE = 22
CDIR_SIZE_CORRECTION = 54


def extract_files(file_path, folder):
    with zipfile.ZipFile(file_path, 'r') as file:
        file.extractall(folder)


class XFL:
    @staticmethod
    def load(project_path: str):
        if os.path.isfile(project_path):
            if os.path.splitext(project_path)[1] != ".fla":
                raise Exception(f"File is not \".fla\": {project_path}")

            fla_file = open(project_path, "rb")
            folder = os.path.splitext(project_path)[0]

            try:
                extract_files(fla_file, folder)
            except zipfile.BadZipfile:
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

                extract_files(fla_file, folder)

            return XFL.load(folder)
        elif os.path.isdir(project_path):
            document = DOMDocument()
            document.load(project_path)
            return document

        raise Exception(f"Project does not exist: {project_path}")

    @staticmethod
    def save(document: DOMDocument):
        filepath = document.document_path + ".fla"

        project_path = document.temp_path

        document.save()

        with zipfile.ZipFile(filepath, 'w', compression=zipfile.ZIP_DEFLATED) as file:
            for root, _, files in os.walk(document.temp_path):
                for filename in files:
                    file.write(os.path.join(root, filename),
                               os.path.relpath(os.path.join(root, filename), os.path.join(project_path, '')))

        rmtree(project_path)
