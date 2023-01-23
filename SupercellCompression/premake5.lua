
project "SupercellCompression"
    kind "StaticLib"

    language "C++"
    cppdialect "C++17"

    targetdir "%{OutputLibsDir}/%{prj.name}"
    objdir "%{InterLibsDir}/%{prj.name}"

    files {
        "src/**.h",
        "src/**.hpp",
        "src/**.cpp"
    }

    includedirs {
        "src",
        
        "%{IncludeDir.LZMA}",
        "%{IncludeDir.LZHAM}",
        "%{IncludeDir.Zstandard}"
	}
	
	links {
        "LZMA",
		"LZHAM",
		"Zstandard"
    }
	
	defines { "_CRT_SECURE_NO_WARNINGS" }

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
