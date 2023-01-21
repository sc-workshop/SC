#include "SupercellCompression/cache/Cache.h"

#include <iostream>
#include <string>
#include <filesystem>

#include "SupercellCompression/common/Utils.h"

namespace fs = std::filesystem;

#define TEMP_PATH "./"
#define CACHE_FOLDER "swf_cache"

namespace sc {
	std::string SwfCache::getInfoFilepath(const std::string& filepath)
	{
		fs::path tempDir = getTempPath();
		fs::path filename = Utils::fileBaseName(filepath);

		std::string infoFilePath = (tempDir / filename.replace_extension("info")).string();

		return infoFilePath;
	}

	// Path to swf TEMP folder
	std::string SwfCache::getTempPath()
	{
		fs::path path;
#ifdef USE_CUSTOM_TEMP_PATH
		path = fs::absolute(TEMP_PATH);
#else
		path = fs::temp_directory_path();
#endif
		path = path / std::string(CACHE_FOLDER);

		std::string filepath = path.string();

		const char* cPath = filepath.c_str();
		struct stat info;
		if (stat(cPath, &info) != 0 || !(info.st_mode & S_IFDIR))
		{
			if (!fs::create_directory(filepath))
			{
				throw std::runtime_error("Failed to create cache folder!");
				exit(1); // FIXME: I think exit() is bad practice, I think..
			}
		}

		return filepath;
	}

	// Path to swf TEMP folder with filename
	std::string SwfCache::getTempPath(const std::string& filepath)
	{
		fs::path tempPath = getTempPath();
		fs::path filename = filepath;
		filename = filename.filename();

		return (tempPath / filename).string();
	}

	// Check if file exists in swf TEMP folder
	bool SwfCache::exist(const std::string& filepath, std::vector<uint8_t> hash, uint32_t fileSize)
	{
		fs::path tempDir = getTempPath();
		fs::path file(filepath);
		file = file.filename();

		std::string scFilepath = (tempDir / file).string();
		std::string infoFilepath = getInfoFilepath(scFilepath);

		// If one of files does not exist, then file is not in cache
		if (!Utils::fileExist(scFilepath) || !Utils::fileExist(infoFilepath))
		{
			return false;
		}

		uint32_t infoFileSize = 0;
		std::vector<uint8_t> infoFileHash;
		getData(filepath, infoFileHash, infoFileSize);
		
		if (infoFileSize != fileSize)
			return false;

		if (infoFileHash != hash)
			return false;

		return true;
	}

	// Gets data from info file in swf TEMP folder
	void SwfCache::getData(const std::string& filepath, std::vector<uint8_t>& hash, uint32_t& fileSize)
	{
		const std::string infoFilePath = getInfoFilepath(filepath);
		FILE* infoFile;
		fopen_s(&infoFile, infoFilePath.c_str(), "rb");
		if (!infoFile)
			return;

		uint8_t Char;
		while (fread(&Char, sizeof(Char), 1, infoFile) != 0)
		{
			if (Char == '\0')
				break;
			hash.push_back(Char);
		}

		fread(&fileSize, sizeof(fileSize), 1, infoFile);

		fclose(infoFile);
	}

	void SwfCache::addData(const std::string& filepath, CompressedSwfProps header, uint32_t fileSize)
	{
		std::string infoFilePath = getInfoFilepath(filepath);

		FILE* file;
		fopen_s(&file, infoFilePath.c_str(), "wb");
		if (!file)
			return;

		fwrite(header.id.data(), header.id.size(), 1, file);
		fwrite("\0", 1, 1, file);
		fwrite(&fileSize, sizeof(fileSize), 1, file);

		fclose(file);
	}
}