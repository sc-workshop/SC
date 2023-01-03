#include <string>

namespace sc {
	class SwfCache {
	public:
		static std::string getInfoFilepath(std::string filepath);
		static std::string getTempPath();
		static std::string getTempPath(std::string filepath);

		static bool exist(std::string filepath, char* hash, uint32_t fileSize);
		static void getData(std::string filepath, char* hash, uint32_t& fileSize);
		static void addData(std::string filepath, char* hash, uint32_t hashSize, uint32_t fileSize);
	};
}