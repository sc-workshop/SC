#include "SupercellCompression/backend/LzhamCompression.h"

#include <lzham_static_lib.h>

#include "SupercellCompression/common/Utils.h"
#include "SupercellCompression/common/ByteStream.hpp"

#define DICT_SIZE 18

#define LZHAM_COMP_INPUT_BUFFER_SIZE 65536*4
#define LZHAM_COMP_OUTPUT_BUFFER_SIZE 65536*4

#define LZHAM_DECOMP_INPUT_BUFFER_SIZE 65536*4
#define LZHAM_DECOMP_OUTPUT_BUFFER_SIZE 65536*4

typedef unsigned char uint8;
typedef unsigned int uint;
typedef unsigned int uint32;

#define my_max(a,b) (((a) > (b)) ? (a) : (b))
#define my_min(a,b) (((a) < (b)) ? (a) : (b))

namespace sc
{
	CompressionError LZHAM::compress(BinaryStream& inStream, BinaryStream& outStream)
	{
		uint64_t fileSize = inStream.size();

		const uint inBufferSize = LZHAM_COMP_INPUT_BUFFER_SIZE;
		const uint outBufferSize = LZHAM_COMP_OUTPUT_BUFFER_SIZE;

		uint8* inBuffer = static_cast<uint8*>(_aligned_malloc(inBufferSize, 16));
		uint8* outBuffer = static_cast<uint8*>(_aligned_malloc(outBufferSize, 16));
		if ((!inBuffer) || (!outBuffer))
		{
			return CompressionError::ALLOC_ERROR;
		}

		uint64_t srcLeft = fileSize;

		uint32_t inBufferPos = 0;
		uint32_t inBufferOffset = 0;

		uint64_t totalOutBytes = 0;

		lzham_compress_params params;
		memset(&params, 0, sizeof(params));
		params.m_struct_size = sizeof(lzham_compress_params);
		params.m_dict_size_log2 = DICT_SIZE;
		// params.m_max_helper_threads = 2;

		lzham_compress_state_ptr lzhamState = lzham_compress_init(&params);

		if (!lzhamState)
		{
			_aligned_free(inBuffer);
			_aligned_free(outBuffer);
			return CompressionError::INIT_ERROR;
		}

		lzham_compress_status_t status = LZHAM_COMP_STATUS_FAILED;

		outStream.writeUInt32(0x5A4C4353);
		outStream.writeUInt8(DICT_SIZE);
		outStream.writeUInt32(static_cast<uint32_t>(fileSize));

		for (;;) // FIXME: Again
		{
			if (inBufferOffset == inBufferPos)
			{
				inBufferPos = static_cast<uint>(my_min(inBufferSize, srcLeft));
				if (inStream.read(inBuffer, inBufferPos) != inBufferPos)
				{
					_aligned_free(inBuffer);
					_aligned_free(outBuffer);
					lzham_compress_deinit(lzhamState);
					return CompressionError::DATA_ERROR;
				}

				srcLeft -= inBufferPos;

				inBufferOffset = 0;
			}

			uint8* inBytes = &inBuffer[inBufferOffset];
			size_t inBytesCount = inBufferPos - inBufferOffset;
			uint8* outBytes = outBuffer;
			size_t outBytesCount = outBufferSize;

			status = lzham_compress(lzhamState, inBytes, &inBytesCount, outBytes, &outBytesCount, srcLeft == 0);

			if (inBytesCount)
			{
				inBufferOffset += (uint)inBytesCount;
			}

			if (outBytesCount)
			{
				if (outStream.write(outBuffer, outBytesCount) != outBytesCount)
				{
					_aligned_free(inBuffer);
					_aligned_free(outBuffer);
					lzham_compress_deinit(lzhamState);
					return CompressionError::DATA_ERROR;
				}

				totalOutBytes += outBytesCount;
			}

			if (status >= LZHAM_COMP_STATUS_FIRST_SUCCESS_OR_FAILURE_CODE)
				break;
		}

		_aligned_free(inBuffer);
		inBuffer = NULL;
		_aligned_free(outBuffer);
		outBuffer = NULL;

		return CompressionError::OK;
	}

	CompressionError LZHAM::decompress(BinaryStream& inStream, BinaryStream& outStream)
	{
		uint32_t magic = inStream.readUInt32();

		if (magic != 0x5A4C4353)
			return CompressionError::DATA_ERROR;

		uint8_t dictSize = inStream.readUInt8();
		uint32_t fileSize = inStream.readUInt32();

		if ((dictSize < LZHAM_MIN_DICT_SIZE_LOG2) || (dictSize > LZHAM_MAX_DICT_SIZE_LOG2_X64))
		{
			return CompressionError::DATA_ERROR;
		}

		int total_header_bytes = static_cast<int>(inStream.tell());

		const uint32_t inputBufferSize = LZHAM_DECOMP_INPUT_BUFFER_SIZE;
		uint8* inputBuffer = static_cast<uint8*>(_aligned_malloc(inputBufferSize, 16));

		uint32_t outputBufferSize = LZHAM_DECOMP_OUTPUT_BUFFER_SIZE;
		uint8* outputBuffer = static_cast<uint8*>(_aligned_malloc(outputBufferSize, 16));
		if (!outputBuffer)
		{
			_aligned_free(inputBuffer);
			return CompressionError::ALLOC_ERROR;
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
			return CompressionError::INIT_ERROR;
		}

		lzham_decompress_status_t lzham_status;
		for (;;) // FIXME: Again
		{
			if (decompressBufferOffset == decompressBufferSize)
			{
				decompressBufferSize = static_cast<uint>(inputBufferSize < inputLeft ? inputBufferSize : inputLeft);
				if (inStream.read(inputBuffer, decompressBufferSize) != decompressBufferSize)
				{
					_aligned_free(inputBuffer);
					_aligned_free(outputBuffer);
					lzham_decompress_deinit(decompressState);
					return CompressionError::DATA_ERROR;
				}

				inputLeft -= decompressBufferSize;

				decompressBufferOffset = 0;
			}

			uint8* inBytes = &inputBuffer[decompressBufferOffset];
			size_t inBytesCount = decompressBufferSize - decompressBufferOffset;
			uint8* outBytes = outputBuffer;
			size_t outBytesCount = outputBufferSize;

			lzham_status = lzham_decompress(decompressState, inBytes, &inBytesCount, outBytes, &outBytesCount, inputLeft == 0);

			if (inBytesCount)
			{
				decompressBufferOffset += (uint)inBytesCount;
			}

			if (outBytesCount)
			{
				if (outStream.write(outputBuffer, static_cast<uint>(outBytesCount)) != outBytesCount)
				{
					_aligned_free(inputBuffer);
					_aligned_free(outputBuffer);
					lzham_decompress_deinit(decompressState);
					return CompressionError::DATA_ERROR;
				}

				if (outBytesCount > outputLeft)
				{
					_aligned_free(inputBuffer);
					_aligned_free(outputBuffer);
					lzham_decompress_deinit(decompressState);
					return CompressionError::DATA_ERROR;
				}
				outputLeft -= outBytesCount;
			}

			if (lzham_status >= LZHAM_DECOMP_STATUS_FIRST_SUCCESS_OR_FAILURE_CODE)
				break;
		}

		_aligned_free(inputBuffer);
		inputBuffer = NULL;

		_aligned_free(outputBuffer);
		outputBuffer = NULL;

		lzham_decompress_deinit(decompressState);
		decompressState = NULL;

		return CompressionError::OK;
	}
}