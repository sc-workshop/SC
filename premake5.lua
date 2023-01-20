
include "dependencies.lua"

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
    startproject "SupercellEditor"

OutputDir = "%{wks.location}/build/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}"
InterDir = "%{wks.location}/build/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}"

group "Dependencies"
    include "external/LZMA"
    include "external/LZHAM"
    include "external/Zstandard"
    include "external/GLFW"
    include "external/GLAD"
    include "external/ImGui"
group ""

group "Tool"
    include "SupercellCompression"
    include "SupercellFlash"
    include "SupercellEditor"
group ""

group "Tool Testing"
	include "SupercellFlashCli"
	include "SupercellCompressionCli"	
