from System.sc.swf import SupercellSWF

from System.sc_import import sc_to_xfl


if __name__ == "__main__":
    sc = SupercellSWF()
    sc.load("assets/characters.sc")

    sc_to_xfl(sc)
