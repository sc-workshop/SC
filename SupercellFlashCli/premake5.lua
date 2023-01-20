
project "SupercellFlashCli"
    kind "ConsoleApp"

    language "C++"
    cppdialect "C++17"

    targetdir "%{wks.location}/build/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/build/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
        "src/**.cpp"
    }

    includedirs {
        "src",
		"%{wks.location}/SupercellFlash/src",
		"%{wks.location}/SupercellCompression/src"
    }
	
	links {
        "SupercellFlash",
		"SupercellCompression"
    }
    
    filter "configurations:Debug"
        defines "SC_DEBUG"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
        defines "SC_RELEASE"
        runtime "Release"
        optimize "on"

