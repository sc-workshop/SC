
project "SupercellCompression"
    kind "StaticLib"

    language "C++"
    cppdialect "C++17"

    targetdir "%{wks.location}/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
        "src/**.h",
        "src/**.cpp",
		"lib/**.h",
		"lib/**.c"
    }

    includedirs {
        "src",
		"lib",
    }
	
    filter "configurations:Debug"
        defines "SC_DEBUG;USE_CUSTOM_TEMP_PATH;"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
        defines "SC_RELEASE;_CRT_SECURE_NO_WARNINGS;"
        runtime "Release"
        optimize "on"

