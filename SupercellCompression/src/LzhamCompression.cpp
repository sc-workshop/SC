#include "Utils.h"
#include "LzhamCompression.h"

#include "lzham_static_lib.h"

#define DICT_SIZE 18

#define LZHAM_DECOMP_INPUT_BUFFER_SIZE 65536*4
#define LZHAM_DECOMP_OUTPUT_BUFFER_SIZE 65536*4

typedef unsigned char uint8;
typedef unsigned int uint;
typedef unsigned int uint32;

#define my_max(a,b) (((a) > (b)) ? (a) : (b))
#define my_min(a,b) (((a) < (b)) ? (a) : (b))

namespace sc {
	CompressErrs LZHAM::decompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		uint32_t magic;
		inStream.read(&magic, sizeof(magic));

		if (magic != 0x5A4C4353)
			return CompressErrs::DATA_ERROR;

		uint8_t dictSize;
		inStream.read(&dictSize, sizeof(dictSize));

		uint32_t fileSize;
		inStream.read(&fileSize, sizeof(fileSize));

		if ((dictSize < LZHAM_MIN_DICT_SIZE_LOG2) || (dictSize > LZHAM_MAX_DICT_SIZE_LOG2_X64))
		{
			return CompressErrs::DATA_ERROR;
		}

		int total_header_bytes = static_cast<int>(inStream.tell());

		const uint32_t inputBufferSize = LZHAM_DECOMP_INPUT_BUFFER_SIZE;
		uint8* inputBuffer = static_cast<uint8*>(_aligned_malloc(inputBufferSize, 16));

		uint32_t outputBufferSize = LZHAM_DECOMP_OUTPUT_BUFFER_SIZE;
		uint8* outputBuffer = static_cast<uint8*>(_aligned_malloc(outputBufferSize, 16));
		if (!outputBuffer)
		{
			_aligned_free(inputBuffer);
			return CompressErrs::ALLOC_ERROR;
		}

		uint32_t inputLeft = inStream.size() - inStream.tell();
		uint32_t outputLeft = fileSize;

		uint decompressBufferSize = 0;
		uint decompressBufferOffset = 0;

		lzham_decompress_params params;
		memset(&params, 0, sizeof(params));
		params.m_struct_size = sizeof(lzham_decompress_params);
		params.m_dict_size_log2 = dictSize;
		params.m_table_update_rate = 8;

		lzham_decompress_state_ptr decompressState = lzham_decompress_init(&params);
		if (!decompressState)
		{
			_aligned_free(inputBuffer);
			_aligned_free(outputBuffer);
			return CompressErrs::INIT_ERROR;
		}

		lzham_decompress_status_t lzham_status;
        for (; ; )
        {
            if (decompressBufferOffset == decompressBufferSize)
            {
                decompressBufferSize = static_cast<uint>(inputBufferSize < inputLeft ? inputBufferSize : inputLeft);
                if ( inStream.read(inputBuffer, decompressBufferSize) != decompressBufferSize)
                {
                    _aligned_free(inputBuffer);
                    _aligned_free(outputBuffer);
                    lzham_decompress_deinit(decompressState);
                    return CompressErrs::DATA_ERROR;
                }

                inputLeft -= decompressBufferSize;

                decompressBufferOffset = 0;
            }

            uint8* pIn_bytes = &inputBuffer[decompressBufferOffset];
            size_t num_in_bytes = decompressBufferSize - decompressBufferOffset;
            uint8* pOut_bytes = outputBuffer;
            size_t out_num_bytes = outputBufferSize;

			lzham_status = lzham_decompress(decompressState, pIn_bytes, &num_in_bytes, pOut_bytes, &out_num_bytes, inputLeft == 0);

            if (num_in_bytes)
            {
                decompressBufferOffset += (uint)num_in_bytes;
            }

            if (out_num_bytes)
            {
                if (outStream.write(outputBuffer, static_cast<uint>(out_num_bytes)) != out_num_bytes)
                {
                    _aligned_free(inputBuffer);
                    _aligned_free(outputBuffer);
                    lzham_decompress_deinit(decompressState);
					return CompressErrs::DATA_ERROR;
                }

                if (out_num_bytes > outputLeft)
                {
                    _aligned_free(inputBuffer);
                    _aligned_free(outputBuffer);
                    lzham_decompress_deinit(decompressState);
                    return CompressErrs::DATA_ERROR;
                }
                outputLeft -= out_num_bytes;
            }

            if (lzham_status >= LZHAM_DECOMP_STATUS_FIRST_SUCCESS_OR_FAILURE_CODE)
                break;
        }

		_aligned_free(inputBuffer);
		inputBuffer = NULL;

		_aligned_free(outputBuffer);
		outputBuffer = NULL;

		inputLeft += (decompressBufferSize - decompressBufferOffset);

		lzham_decompress_deinit(decompressState);
		decompressState = NULL;

		return CompressErrs::OK;
	}
}