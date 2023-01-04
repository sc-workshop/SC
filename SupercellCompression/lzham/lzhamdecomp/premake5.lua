
project "lzhamdecomp"
    kind "StaticLib"

    language "C++"
	cppdialect "C++14"

    targetdir "%{wks.location}/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
		"./**.cpp",
		"../include/lzham_exports.inc"
    }

    includedirs {
        "../include",
		"./",
		"../lzhamcomp"
	}


    filter "configurations:Debug"
		defines "WIN32;_DEBUG;_LIB;"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
		defines "WIN32;NDEBUG;_LIB;"
        runtime "Release"
        optimize "on"

