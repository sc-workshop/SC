

project "SupercellSWF"
    kind "ConsoleApp"

    language "C++"
    cppdialect "C++17"

    targetdir "%{wks.location}/bin/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"
    objdir "%{wks.location}/obj/%{cfg.buildcfg}/%{cfg.system}/%{cfg.architecture}/%{prj.name}"

    files {
        "src/**.h",
        "src/**.cpp"
    }

    includedirs {
        "src",
        "external/include",

        "%{wks.location}/SupercellCompression/src"
    }

    filter "architecture:x86"
        libdirs {
            "external/lib/x86"
        }

    filter "architecture:x64"
        libdirs {
            "external/lib/x64"
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

