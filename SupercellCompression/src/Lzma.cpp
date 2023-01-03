#include "Lzma.h"
#include "Utils.h"

#include "LZMA/Alloc.h"
#include "LZMA/LzmaDec.h"

#define LZMA_IN_BUF_SIZE (1 << 16)
#define LZMA_OUT_BUF_SIZE (1 << 16)

namespace sc {
	COMPRESSION_ERROR LZMA::decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream) {
		int thereIsSize = (unpackSize != (UInt32)(Int32)-1);
		Byte inBuf[LZMA_IN_BUF_SIZE];
		Byte outBuf[LZMA_OUT_BUF_SIZE];
		size_t inPos = 0, inSize = 0, outPos = 0;
		LzmaDec_Init(state);
		for (;;)
		{
			if (inPos == inSize)
			{
				inSize = LZMA_IN_BUF_SIZE;
				inStream.read(&inBuf, inSize);
				inPos = 0;
			}
			{
				COMPRESSION_ERROR res;
				SizeT inProcessed = inSize - inPos;
				SizeT outProcessed = LZMA_OUT_BUF_SIZE - outPos;
				ELzmaFinishMode finishMode = LZMA_FINISH_ANY;
				ELzmaStatus status;
				if (thereIsSize && outProcessed > unpackSize)
				{
					outProcessed = (SizeT)unpackSize;
					finishMode = LZMA_FINISH_END;
				}

				res = LzmaDec_DecodeToBuf(state, outBuf + outPos, &outProcessed,
					inBuf + inPos, &inProcessed, finishMode, &status) == 0 ? COMPRESSION_ERROR::OK : COMPRESSION_ERROR::DATA_ERROR;
				inPos += inProcessed;
				outPos += outProcessed;
				unpackSize -= outProcessed;

				if (outStream.write(outBuf, outPos) != outPos)
					return COMPRESSION_ERROR::DATA_ERROR;

				outPos = 0;

				if (res != COMPRESSION_ERROR::OK || (thereIsSize && unpackSize == 0))
					return res;

				if (inProcessed == 0 && outProcessed == 0)
				{
					if (thereIsSize || status != LZMA_STATUS_FINISHED_WITH_MARK)
						return COMPRESSION_ERROR::DATA_ERROR;

					return res;
				}
			}
		}
	}

	COMPRESSION_ERROR LZMA::decompress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		CLzmaDec state;
		Byte header[LZMA_PROPS_SIZE];
		inStream.read(header, LZMA_PROPS_SIZE);

		unsigned int unpackSize = 0;
		inStream.read(&unpackSize, sizeof(unpackSize));

		LzmaDec_Construct(&state);
		LzmaDec_Allocate(&state, header, LZMA_PROPS_SIZE, &g_Alloc);

		COMPRESSION_ERROR res = decompressStream(&state, unpackSize, inStream, outStream);

		LzmaDec_Free(&state, &g_Alloc);

		return res;
	}
}