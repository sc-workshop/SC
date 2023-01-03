#include "Cache.h"
#include "Utils.h"

#include <cstdlib>
#include <stdlib.h>
#include <stdio.h>

#include <iostream>
#include <fstream>

#include <string>
#include <direct.h>

#include <assert.h>

#include <filesystem>

namespace fs = std::filesystem;

#define TEMP_PATH "./"
#define CACHE_FOLDER "swf_cache"

namespace sc {
	std::string SwfCache::getInfoFilepath(std::string filepath) {
		fs::path tempDir = getTempPath();
		fs::path filename = Utils::fileBasename(filepath);

		std::string infoFilePath = (tempDir / filename.replace_extension("info")).string();

		return infoFilePath;
	}

	// Path to swf TEMP folder
	std::string SwfCache::getTempPath() {
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
		if (stat(cPath, &info) != 0 || !(info.st_mode & S_IFDIR)) {
			if (!fs::create_directory(filepath)) {
				throw std::runtime_error("Failed to create cache folder!");
				exit(1);
			}
		}

		return filepath;
	}

	// Path to swf TEMP folder with filename
	std::string SwfCache::getTempPath(std::string filepath) {
		fs::path tempPath = getTempPath();
		fs::path filename = filepath;
		filename = filename.filename();

		return (tempPath / filename).string();
	}

	// Check if file exists in swf TEMP folder
	bool SwfCache::exist(std::string filepath, char* hash, uint32_t fileSize)
	{
		fs::path tempDir = getTempPath();
		fs::path file(filepath);
		file = file.filename();

		std::string scFilepath = (tempDir / file).string();
		std::string infoFilepath = getInfoFilepath(scFilepath);

		// If one of files does not exist, then file is not in cache
		if (!Utils::fileExist(scFilepath) || !Utils::fileExist(infoFilepath)) {
			return false;
		}

		char* infoFileHash = new char[0]();
		uint32_t infoFileSize = 0;
		getData(filepath, infoFileHash, infoFileSize);

		if (fileSize == infoFileSize) {
			for (uint32_t i = 0; infoFileHash[i] != '\0'; i++) {
				if (hash[i] != infoFileHash[i])
					return false;
			}

			return true;
		}

		return false;
	}

	// Gets data from info file in swf TEMP folder
	void SwfCache::getData(std::string filepath, char* hash, uint32_t& fileSize) {
		const std::string infoFilePath = getInfoFilepath(filepath);
		FILE* infoFile = fopen(infoFilePath.c_str(), "rb");

		char Char;
		int count = 0;
		while (fread(&Char, sizeof(Char), 1, infoFile) != 0) {
			hash[count] = Char;
			if (Char == '\0')
				break;
			count++;
		}

		fread(&fileSize, sizeof(fileSize), 1, infoFile);
	}

	void SwfCache::addData(std::string filepath, char* hash, uint32_t hashSize, uint32_t fileSize) {
		std::string infoFilePath = getInfoFilepath(filepath);
		FILE* file = fopen(infoFilePath.c_str(), "wb");

		fwrite(hash, hashSize, 1, file);
		const char nt[1]{};
		fwrite(nt, sizeof(nt), 1, file);
		fwrite(&fileSize, sizeof(fileSize), 1, file);
	}
}