#pragma once
#include <ByteStream.hpp>

namespace sc {
	class SupercellSWF;
	/*
	* Abstract class for tags with id in SC-SWF file.
	*/
	class ScTag {
	public:
		/* Tag load function from file stream */
		virtual void load(SupercellSWF* swf, uint8_t tag) = 0;
		/* Tag write function to stream */
		// virtual std::vector<uint8_t> saveTag() = 0;
		/* Function to get tag to write it to file stream */
		virtual uint8_t getTag() = 0;

		/* Tag identifer */
		uint16_t id;
	};
}