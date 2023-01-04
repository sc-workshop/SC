
project "LZHAM"
    kind "StaticLib"

    language "C++"
	cppdialect "C++14"

    targetdir "%{wks.location}/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
		"lzham_lib.cpp",
		"lzhamcomp/**.cpp",
		"lzhamcomp/**.h",
		"lzhamdecomp/**.cpp"
    }

    includedirs {
        "include",
		"lzhamcomp",
		"lzhamdecomp"
	}


    filter "configurations:Debug"
		defines "WIN32;_DEBUG;_LIB;"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
		defines "WIN32;NDEBUG;_LIB;"
        runtime "Release"
        optimize "on"
		
	filter "architecture:x86_64"
		defines "LZHAM_64BIT"
		
	filter "system:windows"
		defines "WIN32"