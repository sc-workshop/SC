#include "Lzma.h"
#include "Utils.h"

#include <LZMA/Alloc.h>
#include <LZMA/LzmaDec.h>

#define LZMA_IN_BUF_SIZE (1 << 16)
#define LZMA_OUT_BUF_SIZE (1 << 16)

namespace sc {
	CompressErrs LZMA::decompressStream(CLzmaDec* state, SizeT unpackSize, IBinaryStream& inStream, IBinaryStream& outStream) {
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
				CompressErrs res;
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
					inBuf + inPos, &inProcessed, finishMode, &status) == 0 ? CompressErrs::OK : CompressErrs::DATA_ERROR;
				inPos += inProcessed;
				outPos += outProcessed;
				unpackSize -= outProcessed;

				if (outStream.write(outBuf, outPos) != outPos)
					return CompressErrs::DATA_ERROR;

				outPos = 0;

				if (res != CompressErrs::OK || (thereIsSize && unpackSize == 0))
					return res;

				if (inProcessed == 0 && outProcessed == 0)
				{
					if (thereIsSize || status != LZMA_STATUS_FINISHED_WITH_MARK)
						return CompressErrs::DATA_ERROR;

					return res;
				}
			}
		}
	}

	CompressErrs LZMA::decompress(IBinaryStream& inStream, IBinaryStream& outStream)
	{
		CLzmaDec state;
		Byte header[LZMA_PROPS_SIZE];
		inStream.read(header, LZMA_PROPS_SIZE);

		unsigned int unpackSize = 0;
		inStream.read(&unpackSize, sizeof(unpackSize));

		LzmaDec_Construct(&state);
		LzmaDec_Allocate(&state, header, LZMA_PROPS_SIZE, &g_Alloc);

		CompressErrs res = decompressStream(&state, unpackSize, inStream, outStream);

		LzmaDec_Free(&state, &g_Alloc);

		return res;
	}
}