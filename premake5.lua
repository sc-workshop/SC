

workspace "SupercellSWF"
    architecture "x86_64"

    configurations {
        "Debug",
        "Release"
    }
	
    startproject "SupercellEditor"


include "SupercellCompression"
-- include "SupercellCompressionCli"
include "SupercellFlash"
-- include "SupercellSWF_Test"
include "SupercellEditor"
