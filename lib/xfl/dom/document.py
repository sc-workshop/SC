import os

from xml.etree.ElementTree import *
import xml.dom.minidom as md

from .folder_item import DOMFolderItem
from .bitmap_item import DOMBitmapItem
from .symbol_item import DOMSymbolItem
from .timeline import DOMTimeline

from ..dat.bitmap import Bitmap

from . import NAMESPACES


class DOMDocument:
    def __init__(self) -> None:
        # class fields
        self.filepath: str = None

        # attributes
        self.xfl_version: float = 2.971
        self.creator_info: str = "Generated with XFL Python module by Pavel Sokov (luberalles aka fred31)"

        self.width: int = 1280
        self.height: int = 720
        self.frame_rate: int = 30

        self.current_timeline: int = 1
        self.background_color: int = 0x000000

        # elements
        self.folders: list = []
        self.media: dict = {}
        self.symbols: dict = {}
        self.timelines: list = []
    
    @property
    def librarypath(self):
        path = f"{self.filepath}/LIBRARY"
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    @property
    def binarypath(self):
        path = f"{self.filepath}/bin"
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    def load(self, filepath: str):
        self.filepath = filepath

        parsed = parse(os.path.join(self.filepath, "DOMDocument.xml"))
        xml = parsed.getroot()

        if "xflVersion" in xml.attrib:
            self.xfl_version = float(xml.attrib["xflVersion"])
        
        if "creatorInfo" in xml.attrib:
            self.creator_info = xml.attrib["creatorInfo"]
        
        if "width" in xml.attrib:
            self.width = int(xml.attrib["width"])
        
        if "height" in xml.attrib:
            self.height = int(xml.attrib["height"])
        
        if "frameRate" in xml.attrib:
            self.frame_rate = int(xml.attrib["frameRate"])
        
        if "currentTimeline" in xml.attrib:
            self.current_timeline = int(xml.attrib["currentTimeline"])
        
        if "backgroundColor" in xml.attrib:
            self.background_color = int(xml.attrib["backgroundColor"].replace("#", "0x"), 0)
        
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

                """if bitmap.bitmap_data_href is not None and bitmap.bitmap_data_href != "":
                    bitmap.image = Bitmap.load(os.path.join(self.binarypath, bitmap.bitmap_data_href))

                    # TODO: external source image loading
                    # if bitmap.source_external_filepath is not None and bitmap.source_external_filepath != "":
                    #     bitmap.image = Image.open(os.path.join(self.filepath, os.path.normpath(bitmap.source_external_filepath)))"""

                self.media[bitmap.name] = bitmap
        
        if symbols is not None:
            for symbol_element in symbols:
                symbol = DOMSymbolItem()
                symbol.load(os.path.join(self.librarypath, symbol_element.attrib["href"]))
                self.symbols[symbol.name] = symbol
        
        if timelines is not None:
            for timeline_element in timelines:
                timeline = DOMTimeline()
                timeline.load(timeline_element)
                self.timelines.append(timeline)

    def save(self, filepath: str):
        self.filepath = filepath

        if not os.path.exists(filepath):
            os.mkdir(filepath)

        if not os.path.exists(self.binarypath):
            os.mkdir(self.binarypath)

        if not os.path.exists(self.librarypath):
            os.mkdir(self.librarypath)
        
        for folder in self.folders:
            if folder.name is not None and folder.name != "":
                if not os.path.exists(os.path.join(self.librarypath, folder.name)):
                    os.mkdir(os.path.join(self.librarypath, folder.name))

        xml = Element("DOMDocument")

        xml.attrib["xmlns:xsi"] = NAMESPACES["xsi"]
        xml.attrib["xmlns"] = NAMESPACES["xfl"]
        
        if self.xfl_version is not None:
            xml.attrib["xflVersion"] = str(self.xfl_version)
        
        if self.creator_info is not None and self.creator_info != "":
            xml.attrib["creatorInfo"] = str(self.creator_info)
        
        if self.width is not None:
            xml.attrib["width"] = str(self.width)
        
        if self.height is not None:
            xml.attrib["height"] = str(self.height)
        
        if self.frame_rate is not None:
            xml.attrib["frameRate"] = str(self.frame_rate)
        
        if self.current_timeline is not None:
            xml.attrib["currentTimeline"] = str(self.current_timeline)
        
        if self.background_color is not None:
            xml.attrib["backgroundColor"] = "#" + str(hex(self.background_color).lstrip("0x").zfill(6))
        
        folders = SubElement(xml, "folders")
        media = SubElement(xml, "media")
        symbols = SubElement(xml, "symbols")
        timelines = SubElement(xml, "timelines")

        for folder in self.folders:
            if folder.name is not None and folder.name != "":
                folders.append(folder.save())
        
        for media_name in self.media:
            medium = self.media[media_name]
            media.append(medium.save())

            # TODO: external source image saving
            # if medium.source_external_filepath is not None and medium.source_external_filepath != "":
            #     medium.image.save(os.path.join(self.filepath, os.path.normpath(medium.source_external_filepath)))

            if medium.image is not None:
                Bitmap.save(os.path.join(self.binarypath, medium.bitmap_data_href), medium.image)
        
        for symbol_name in self.symbols:
            symbol = self.symbols[symbol_name]

            href = str(symbol_name) + ".xml"

            symbol.save(os.path.join(self.librarypath, href))
            
            include = Element("Include")
            include.attrib["href"] = href

            if symbol.symbol_type is not None and symbol.symbol_type == "graphic":
                include.attrib["itemIcon"] = "1"
            
            include.attrib["loadImmediate"] = "true"

            symbols.append(include)

        for timeline in self.timelines:
            timelines.append(timeline.save())
        
        with open(os.path.join(self.filepath, "DOMDocument.xml"), 'w') as file:
            file.write(md.parseString(tostring(xml)).toprettyxml())
        
        with open(os.path.join(self.filepath, os.path.basename(self.filepath) + ".xfl"), 'w') as file:
            file.write("PROXY-CS5")
