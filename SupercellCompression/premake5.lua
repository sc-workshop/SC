
project "SupercellCompression"
    kind "StaticLib"

    language "C++"
    cppdialect "C++17"

    targetdir "%{wks.location}/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
        "src/**.h",
        "src/**.hpp",
        "src/**.cpp"
    }

    includedirs {
        "src",
        
        "external/LZMA/include",
        "external/LZHAM/include",
        "external/Zstandard/include"
	}
	
	links {
        "LZMA",
		"LZHAM",
		"Zstandard"
    }

    filter "configurations:Debug"
        runtime "Debug"

        defines {
            "SC_DEBUG",
            "USE_CUSTOM_TEMP_PATH"
        }

        symbols "on"
    
    filter "configurations:Release"
        runtime "Release"

        defines {
            "SC_RELEASE",
            "_CRT_SECURE_NO_WARNINGS"
        }

        optimize "on"


include "external/LZMA"
include "external/LZHAM"
include "external/Zstandard"
