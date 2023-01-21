
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

group "Libraries"
    include "SupercellCompression"
	include "SupercellFlash"
    
group "Tools"
	include "SupercellEditor"
	include "SupercellFlashCli"
	include "SupercellCompressionCli"	
