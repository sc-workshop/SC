
project "LZMA"
    kind "StaticLib"

    language "C"

    targetdir "%{OutputDir}/Deps/%{prj.name}"
    objdir "%{InterDir}/%{prj.name}"

    files {
		"src/**.c"
    }

    includedirs {
        "include"
	}

    filter "configurations:Debug"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
        runtime "Release"
        optimize "on"

