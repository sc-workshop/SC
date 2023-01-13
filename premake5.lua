

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
    startproject "SupercellSWF"

include "SupercellSWF"
include "SupercellSWF_Test"
include "SupercellCompression"
include "SupercellCompressionCli"
