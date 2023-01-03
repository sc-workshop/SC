#include "Utils.h"
#include "LZHAM/include/lzham_static_lib.h"

#define LZHAM_BUF_SIZE (1024 * 1024)
static uint8_t s_inbuf[LZHAM_BUF_SIZE];
static uint8_t s_outbuf[LZHAM_BUF_SIZE];

#define DICT_SIZE 18

namespace sc {
	int decompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		return 0;
	}
}