#include "Utils.h"

#include <stdlib.h>
#include <string>

#include <sys/types.h>
#include <sys/stat.h>

#include <filesystem>

namespace fs = std::filesystem;

namespace sc {
	bool Utils::endsWith(std::string const& value, std::string const& ending)
	{
		if (ending.size() > value.size()) return false;
		return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
	}

	bool Utils::fileExist(std::string path) {
		struct stat fileInfo;
		return stat(path.c_str(), &fileInfo) == 0;
	}

	std::string Utils::fileBasename(std::string filepath) {
		fs::path filename = filepath;
		return filename.filename().string();
	}

	unsigned int Utils::fileSize(FILE*& file) {
		long orig_pos = ftell(file);
		fseek(file, 0, SEEK_END);
		long size = ftell(file);
		fseek(file, orig_pos, SEEK_SET);
		return static_cast<unsigned int>(size);
	}
}