
include "dependencies.lua"

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
	startproject "SupercellFlashCli"
	startproject "SupercellCompressionCli"
	--startproject "SupercellEditor"

OutputDir = "%{wks.location}/build/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}"
InterDir = "%{wks.location}/build/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}"

OutputDepsDir = "%{OutputDir}/dependencies"
InterDepsDir = "%{InterDir}/dependencies"

OutputLibsDir = "%{OutputDir}/libraries"
InterLibsDir = "%{InterDir}/libraries"

OutputToolsDir = "%{OutputDir}/tools"
InterToolsDir = "%{InterDir}/tools"

group "Dependencies"
    include "external/LZMA"
    include "external/LZHAM"
    include "external/Zstandard"
	
	--include "external/ImGui"
	--include "external/GLFW"
	--include "external/GLAD"

group "Libraries"
    include "SupercellCompression"
	include "SupercellFlash"
    
group "Tools"
	include "SupercellFlashCli"
	include "SupercellCompressionCli"

	--include "SupercellEditor"
