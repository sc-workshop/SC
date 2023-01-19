
project "Zstandard"
    kind "StaticLib"

    language "C"

    targetdir "%{OutputDir}/%{prj.name}"
    objdir "%{InterDir}/%{prj.name}"

    files {
		"src/**.c"
    }

    includedirs {
        "include",
		"include/common",
		"include/compress",
		"include/decompress"
	}


    filter "configurations:Debug"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
        runtime "Release"
        optimize "on"

