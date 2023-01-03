#include "Utils.h"
#include "Zstd.h"

#include "ZSTD/zstd.h"

namespace sc {
	COMPRESSION_ERROR ZSTD::decompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		const size_t buffInSize = ZSTD_DStreamInSize();
		const size_t buffOutSize = ZSTD_DStreamOutSize();

		void* buffIn = malloc(buffInSize);
		void* buffOut = malloc(buffOutSize);

		ZSTD_DStream* const dStream = ZSTD_createDStream();

		if (!dStream)
		{
			return COMPRESSION_ERROR::INIT_ERROR;
		}

		const size_t initResult = ZSTD_initDStream(dStream);

		if (ZSTD_isError(initResult))
		{
			ZSTD_freeDStream(dStream);
			return COMPRESSION_ERROR::INIT_ERROR;
		}

		size_t toRead = initResult;

		while (const size_t read = inStream.read(buffIn, toRead)) {
			ZSTD_inBuffer input = { buffIn, read, 0 };
			
			while (input.pos < input.size)
			{
				ZSTD_outBuffer output = { buffOut, buffOutSize, 0 };
				toRead = ZSTD_decompressStream(dStream, &output, &input);

				if (ZSTD_isError(toRead))
				{
					ZSTD_freeDStream(dStream);
					return COMPRESSION_ERROR::DATA_ERROR;
				}
				outStream.write(buffOut, output.pos);
			}
		}

		ZSTD_freeDStream(dStream);
		free(buffIn);
		free(buffOut);

		return COMPRESSION_ERROR::OK;
	}
}