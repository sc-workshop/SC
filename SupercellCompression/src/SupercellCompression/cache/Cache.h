#include <string>
#include <vector>

#include "SupercellCompression/common/Utils.h"

namespace sc {
	class SwfCache
	{
	public:
		static std::string getInfoFilepath(const std::string& filepath);
		static std::string getTempPath();
		static std::string getTempPath(const std::string& filepath);

		static bool exist(const std::string& filepath, std::vector<uint8_t> hash, uint32_t fileSize);
		static void getData(const std::string& filepath, std::vector<uint8_t>& hash , uint32_t& fileSize);
		static void addData(const std::string& filepath, CompressedSwfProps header, uint32_t fileSize);
	};
}