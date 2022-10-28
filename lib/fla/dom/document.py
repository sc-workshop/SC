import os
import tempfile
from typing import List, Dict

from lxml.etree import *
from shutil import rmtree

from PIL import Image

from .folder_item import DOMFolderItem
from .bitmap_item import DOMBitmapItem
from .symbol_item import DOMSymbolItem
from .timeline import DOMTimeline

from ..dat.bitmap import Bitmap

from . import NAMESPACES

from lib.console import Console


class Folders(list):
    def __init__(self, library: str):
        self.library = library

    def add(self, folder_item):
        if isinstance(folder_item, DOMFolderItem):
            os.makedirs(os.path.join(self.library, folder_item.name), exist_ok=True)
            self.append(folder_item)

    def delete(self, index):
        rmtree(os.path.join(self.library, self[index].name))
        del self[index]


class Symbols(dict):
    def __init__(self, library: str):
        self.library = library

    def add(self, key, value):
        path = os.path.join(self.library, str(key) + ".xml")
        value.save(path)

        self[key] = path

    def get(self, key):
        symbol = DOMSymbolItem()
        symbol.load(self[key])
        return symbol


class DOMDocument:
    def __init__(self, filepath: str = None) -> None:
        # class fields
        if filepath is not None:
            self.document_name: str = os.path.basename(filepath)
            self.document_path: str = filepath
        self.temp_path: str = tempfile.mkdtemp()

        # attributes
        self.creator_info: str = "Generated with XFL Python module by Pavel Sokov (GitHub: https://github.com/Fred-31)"

        # elements
        self.folders = Folders(self.library_path)
        self.media: Dict[str, DOMBitmapItem] = {}
        self.symbols = Symbols(self.library_path)
        self.timelines: List[DOMTimeline] = []

        self._xfl_version: str = '2.971'
        self._width: int = 1280
        self._height: int = 720
        self._frame_rate: int = 30

        self._current_timeline: int = 1
        self._background_color: int = 0x666666

    @property
    def library_path(self):
        path = f"{self.temp_path}/LIBRARY"
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def binary_path(self):
        path = f"{self.temp_path}/bin"
        os.makedirs(path, exist_ok=True)
        return path

    def load(self, filepath: str):
        parsed = parse(os.path.join(filepath, "DOMDocument.xml"))
        xml = parsed.getroot()

        if "xflVersion" in xml.attrib:
            self._xfl_version = xml.attrib["xflVersion"]

        if "creatorInfo" in xml.attrib:
            self.creator_info = xml.attrib["creatorInfo"]

        if "width" in xml.attrib:
            self._width = int(xml.attrib["width"])

        if "height" in xml.attrib:
            self._height = int(xml.attrib["height"])

        if "frameRate" in xml.attrib:
            self._frame_rate = int(xml.attrib["frameRate"])

        if "currentTimeline" in xml.attrib:
            self._current_timeline = int(xml.attrib["currentTimeline"])

        if "backgroundColor" in xml.attrib:
            self._background_color = int(xml.attrib["backgroundColor"].replace("#", "0x"), 0)

        folders = xml.find("./xfl:folders", NAMESPACES)
        media = xml.find("./xfl:media", NAMESPACES)
        symbols = xml.find("./xfl:symbols", NAMESPACES)
        timelines = xml.find("./xfl:timelines", NAMESPACES)

        if folders is not None:
            for folder_element in folders:
                folder = DOMFolderItem()
                folder.load(folder_element)
                self.folders.append(folder)

        if media is not None:
            for media_element in media:
                bitmap = DOMBitmapItem()
                bitmap.load(media_element)

                if bitmap.bitmap_data_href is not None:
                    bitmap.image = Bitmap.load(os.path.join(self.binary_path, bitmap.bitmap_data_href))

                    # TODO: external source image loading
                    if bitmap.source_external_filepath is not None:
                        image_path = os.path.join(filepath, os.path.normpath(bitmap.source_external_filepath))
                        bitmap.image = Image.open(image_path)

                self.media[bitmap.name] = bitmap

        if symbols is not None:
            for symbol_element in symbols:
                symbol = DOMSymbolItem()
                symbol.load(os.path.join(self.library_path, symbol_element.attrib["href"]))
                self.symbols[symbol.name] = os.path.join(self.library_path, symbol_element.attrib["href"])

        if timelines is not None:
            for timeline_element in timelines:
                timeline = DOMTimeline()
                timeline.load(timeline_element)
                self.timelines.append(timeline)

    def save(self):
        os.makedirs(self.binary_path, exist_ok=True)
        os.makedirs(self.library_path, exist_ok=True)

        for folder in self.folders:
            if folder.name is not None and folder.name != "":
                os.makedirs(os.path.join(self.library_path, folder.name), exist_ok=True)
        xml = Element("DOMDocument", {"xmlns": NAMESPACES["xfl"]}, nsmap={'xsi': NAMESPACES["xsi"]})

        if self._xfl_version is not None:
            xml.attrib["xflVersion"] = self._xfl_version

        if self.creator_info is not None and self.creator_info != "":
            xml.attrib["creatorInfo"] = str(self.creator_info)

        if self._width is not None:
            xml.attrib["width"] = str(self._width)

        if self._height is not None:
            xml.attrib["height"] = str(self._height)

        if self._frame_rate is not None:
            xml.attrib["frameRate"] = str(self._frame_rate)

        if self._current_timeline is not None:
            xml.attrib["currentTimeline"] = str(self._current_timeline)

        if self._background_color is not None:
            xml.attrib["backgroundColor"] = "#" + str(hex(self._background_color).lstrip("0x").zfill(6))

        folders = SubElement(xml, "folders")
        media = SubElement(xml, "media")
        symbols = SubElement(xml, "symbols")
        timelines = SubElement(xml, "timelines")

        for folder in self.folders:
            if folder.name is not None and folder.name != "":
                folders.append(folder.save())

        for i, media_name in enumerate(self.media):
            medium = self.media[media_name]
            media.append(medium.save())

            # TODO: external source image saving
            if medium.source_external_filepath is not None:
                medium.image.save(
                    os.path.join(self.temp_path, os.path.normpath(medium.source_external_filepath)),
                    "PNG"
                )

            if medium.image is not None:

                Bitmap.save(os.path.join(self.get_binary_path(self.temp_path), medium.bitmap_data_href), medium.image)

            Console.progress_bar("Adobe binary images saving...", i, len(self.media))
        print()

        for symbol_name, symbol in self.symbols.items():
            include = Element("Include")
            include.attrib["href"] = str(symbol_name) + ".xml"

            symbols.append(include)

        for timeline in self.timelines:
            timelines.append(timeline.save())

        ElementTree(xml).write(os.path.join(self.temp_path, "DOMDocument.xml"))

        with open(os.path.join(self.temp_path, self.document_name + ".xfl"), 'w') as file:
            file.write("PROXY-CS5")

    @staticmethod
    def get_binary_path(directory) -> str:
        return os.path.join(directory, 'bin')
