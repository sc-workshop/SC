
project "SupercellEditor"
    kind "ConsoleApp"

    language "C++"
    cppdialect "C++17"

    targetdir "%{OutputDir}/Tools/%{prj.name}"
    objdir "%{InterDir}/%{prj.name}"

    files {
        "src/**.h",
        "src/**.hpp",
		"src/**.cpp"
    }

    includedirs {
        "src",
        
        "%{wks.location}/SupercellFlash/src",

        "%{IncludeDir.GLFW}",
        "%{IncludeDir.GLAD}",
        "%{IncludeDir.ImGui}"
    }

    links {
        "SupercellFlash",

        "GLFW",
        "GLAD",
        "ImGui",

        "opengl32.lib"
    }

    filter "configurations:Debug"
        defines { "SC_DEBUG" }
        runtime "Debug"
        symbols "on"

    filter "configurations:Release"
        defines { "SC_RELEASE" }
        runtime "Release"
        optimize "on"
