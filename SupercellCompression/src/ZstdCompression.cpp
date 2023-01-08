#include "Utils.h"
#include "ZstdCompression.h"

#include <zstd.h>
#include <thread>

namespace sc {
	CompressionErrs ZSTD::decompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		const size_t buffInSize = ZSTD_DStreamInSize();
		const size_t buffOutSize = ZSTD_DStreamOutSize();

		void* buffIn = malloc(buffInSize);
		void* buffOut = malloc(buffOutSize);

        if (!buffIn || !buffOut) return CompressionErrs::ALLOC_ERROR;

		ZSTD_DStream* const dStream = ZSTD_createDStream();

		if (!dStream)
		{
			return CompressionErrs::INIT_ERROR;
		}

		const size_t initResult = ZSTD_initDStream(dStream);

		if (ZSTD_isError(initResult))
		{
			ZSTD_freeDStream(dStream);
			return CompressionErrs::INIT_ERROR;
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
					return CompressionErrs::DATA_ERROR;
				}
				outStream.write(buffOut, output.pos);
			}
		}

		ZSTD_freeDStream(dStream);
		free(buffIn);
		free(buffOut);

		return CompressionErrs::OK;
	}
	CompressionErrs ZSTD::compress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		size_t const buffInSize = ZSTD_CStreamInSize();
		size_t const buffOutSize = ZSTD_CStreamOutSize();

		void* buffIn = malloc(buffInSize);
		void* buffOut = malloc(buffOutSize);

		if (!buffIn || !buffOut) return CompressionErrs::ALLOC_ERROR;

        ZSTD_CCtx* const cctx = ZSTD_createCCtx();
        if (cctx == NULL) return CompressionErrs::INIT_ERROR;

        ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 16);
        ZSTD_CCtx_setParameter(cctx, ZSTD_c_checksumFlag, 0);

        ZSTD_CCtx_setParameter(cctx, ZSTD_c_contentSizeFlag, 1);
		ZSTD_CCtx_setPledgedSrcSize(cctx, inStream.size());

        size_t const toRead = buffInSize;
        for (;;) {
            size_t read = inStream.read(buffIn, toRead);

            int const lastChunk = (read < toRead);
            ZSTD_EndDirective const mode = lastChunk ? ZSTD_e_end : ZSTD_e_continue;
            ZSTD_inBuffer input = { buffIn, read, 0 };
            int finished;
            do {
                ZSTD_outBuffer output = { buffOut, buffOutSize, 0 };
                size_t const remaining = ZSTD_compressStream2(cctx, &output, &input, mode);
				outStream.write(buffOut, output.pos);
                finished = lastChunk ? (remaining == 0) : (input.pos == input.size);
            } while (!finished);
			if (input.pos != input.size) return CompressionErrs::DATA_ERROR;

            if (lastChunk) {
                break;
            }
        }

        ZSTD_freeCCtx(cctx);
        free(buffIn);
        free(buffOut);

        return CompressionErrs::OK;
	}
}