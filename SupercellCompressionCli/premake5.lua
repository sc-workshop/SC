
project "SupercellCompressionCli"
    kind "ConsoleApp"

    language "C++"
    cppdialect "C++17"

    targetdir "%{OutputToolsDir}/%{prj.name}"
    objdir "%{InterToolsDir}/%{prj.name}"

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
	
	defines { "_CRT_SECURE_NO_WARNINGS" }
    
    filter "configurations:Debug"
        defines "SC_DEBUG"
        runtime "Debug"
        symbols "on"
    
    filter "configurations:Release"
        defines "SC_RELEASE"
        runtime "Release"
        optimize "on"

