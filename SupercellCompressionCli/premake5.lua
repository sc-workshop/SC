
project "SupercellCompressionCli"
    kind "ConsoleApp"

    language "C++"
    cppdialect "C++17"

    targetdir "%{OutputDir}/Tools/%{prj.name}"
    objdir "%{InterDir}/%{prj.name}"

    files {
        "src/**.cpp"
    }

    includedirs {
        "src",
		
		"%{wks.location}/SupercellCompression/src"
    }
	
	links {
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

