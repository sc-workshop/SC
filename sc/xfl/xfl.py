class XFL:
    def __init__(self) -> None:
        self.project_dir: str = None

        self.dom = None

        self.folders = None
        self.media = None
        self.symbols = None
        self.timelines = None
    
    @property
    def library_dir(self):
        return self.project_dir + "/LIBRARY/"
    
    @property
    def shapes_dir(self):
        return self.library_dir + "Shapes/"
    
    @property
    def binary_dir(self):
        return self.project_dir + "/bin/"
    
    @property
    def resources_dir(self):
        return self.library_dir + "Resources/"
