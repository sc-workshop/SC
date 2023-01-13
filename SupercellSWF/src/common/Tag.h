#pragma once
#include <cstdint>

namespace sc {
	/*
	* Abstract class for tags with id in SC-SWF file.
	*/
	class ScTag {
	public:
		/* Tag load function from file stream */
		virtual void loadTag(IBinaryStream* stream, uint8_t tag) = 0;
		/* Function to get tag to write it to file stream */
		virtual uint16_t getTag() = 0;

		/* Tag identifer */
		uint16_t id;
	};
}