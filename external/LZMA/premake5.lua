
project "LZMA"
    kind "StaticLib"

    language "C"

    targetdir "%{OutputDepsDir}/%{prj.name}"
    objdir "%{InterDepsDir}/%{prj.name}"

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

