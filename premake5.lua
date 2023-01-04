

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
	platforms {"Win64", "Linux" }
	
    startproject "SupercellSWF"


include "SupercellCompression"
include "SupercellCompressionCli"

