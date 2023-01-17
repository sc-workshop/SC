

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
    startproject "SupercellSWF"


include "SupercellCompression"
include "SupercellCompressionCli"
include "SupercellSWF"
include "SupercellSWF_Test"
