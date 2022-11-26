<h1 align="center">
  <img src="resources/Sc_logo_v1_256x.png">
</h1>

<p align="center">
  Supercell SWF (Flash) file format decompiler and compiler. Supercell's games using .sc files for almost all 2D graphics (UI, VFX, particles, characters facial animations, etc.).
 Please follow the Supercell fan content policy - http://supercell.com/fan-content-policy!
</p>

## <h1 align="center"> About  </h1>

This tool is designed to import and export 2D assets (`*.sc`, `*_dl.sc`, `*_tex.sc` files) from Supercell games using Adobe Animate 2019. At the moment, the tool is very slow when working with large files (so we do not advise you to import large files like ui.sc if you have a weak PC, 8Gb RAM and fast CPU is recommended ). Maybe we rewrite it with C++ or C# in future...

There are also a lot of bugs and errors in the tool, if you find them, please let us know in <a href="https://github.com/scwmake/SC/issues">Issues</a> or our <a href="https://discord.gg/spFcna3xFJ">Discord server</a>!

## Installation and Requirements 
- <a href="https://www.python.org/">Python 3.10+</a> or newer version.
- Execute ```pip install -r requirements.txt``` command in tool directory after installing Python.
- <a href="https://www.adobe.com/products/animate.html">Adobe Animate 2019</a> (2019 is recommended because it's more optimized than 2022!).
- <a href="https://www.codeandweb.com/texturepacker">TexturePacker</a> (for getting and saving sprite sheets/texture atlases).

## How To Use

Please **WATCH ALL THE VIDEOS BELOW** before using this tool!

1. Converting `.sc` to Adobe Animate project file.
2. Organizing your Adobe Animate project.
3. Saving your Adobe Animate project for converting it to `.sc` file.
4. Creating sprite sheets/texture atlases in TexturePacker.
5. Converting Adobe Animate project to `.sc` file.

## TODO
- Add TexturePacker projects support.
- Refactor some code in ```lib/sc```.
- Write code in ```lib/fla```.
- Add ```sc_export.py``` functional.
- Rewrite it with C++ or C# in future...

## Credits
Tool created by <a href="https://github.com/Fred-31">Fred-31</a> and <a href="https://github.com/Daniil-SV">DaniilSV</a>. Inspired by <a href="https://github.com/Vorono4ka/XCoder">XCoder</a> and <a href="https://github.com/baraklevy20/Supercell-Extractor">Supercell-Extractor</a>.
