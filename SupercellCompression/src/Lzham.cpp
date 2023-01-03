#include "Utils.h"
#include "Lzham.h"

// #include <lzham_static_lib.h>

#define DICT_SIZE 18

#define LZHAM_DECOMP_INPUT_BUFFER_SIZE 65536*4
#define LZHAM_DECOMP_OUTPUT_BUFFER_SIZE 65536*4

#define my_max(a,b) (((a) > (b)) ? (a) : (b))
#define my_min(a,b) (((a) < (b)) ? (a) : (b))

namespace sc {
	CompressErrs LZHAM::decompress(IBinaryStream& inStream, IBinaryStream& outStream) {
		/*lzham_static_lib lzham_lib;
		lzham_lib.load();

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

		const uint32_t cInBufSize = LZHAM_DECOMP_INPUT_BUFFER_SIZE;
		uint8_t* in_file_buf = static_cast<uint8_t*>(_aligned_malloc(cInBufSize, 16));

		const uint32_t out_buf_size = LZHAM_DECOMP_OUTPUT_BUFFER_SIZE;
		uint8_t* out_file_buf = static_cast<uint8_t*>(_aligned_malloc(out_buf_size, 16));

		if (!out_file_buf)
		{
			return CompressErrs::ALLOC_ERROR;
		}

		uint64_t src_bytes_left = inStream.size() - inStream.tell();
		uint64_t dst_bytes_left = inStream.size();

		uint32_t in_file_buf_size = 0;
		uint32_t in_file_buf_ofs = 0;

		lzham_decompress_params params;
		memset(&params, 0, sizeof(params));
		params.m_struct_size = sizeof(lzham_decompress_params);
		params.m_dict_size_log2 = dictSize;

		lzham_decompress_state_ptr pDecomp_state = lzham_lib.lzham_decompress_init(&params);
		if (!pDecomp_state)
		{
			_aligned_free(in_file_buf);
			_aligned_free(out_file_buf);
			return CompressErrs::INIT_ERROR;
		}

		lzham_decompress_status_t status;
		for (; ; )
		{
			if (in_file_buf_ofs == in_file_buf_size)
			{
				in_file_buf_size = static_cast<uint32_t>(my_min(cInBufSize, src_bytes_left));

				if (inStream.read(in_file_buf, in_file_buf_size) != in_file_buf_size)
				{
					lzham_lib.lzham_decompress_deinit(pDecomp_state);
					return CompressErrs::DATA_ERROR;
				}

				src_bytes_left -= in_file_buf_size;

				in_file_buf_ofs = 0;
			}

			uint8_t* pIn_bytes = &in_file_buf[in_file_buf_ofs];
			size_t num_in_bytes = in_file_buf_size - in_file_buf_ofs;
			uint8_t* pOut_bytes = out_file_buf;
			size_t out_num_bytes = out_buf_size;

			if (out_num_bytes)
			{
				if (inStream.write(out_file_buf, static_cast<uint32_t>(out_num_bytes)) != out_num_bytes)
				{
					_aligned_free(in_file_buf);
					_aligned_free(out_file_buf);
					lzham_lib.lzham_decompress_deinit(pDecomp_state);
					return CompressErrs::DATA_ERROR;
				}

				if (out_num_bytes > dst_bytes_left)
				{
					_aligned_free(in_file_buf);
					_aligned_free(out_file_buf);
					lzham_lib.lzham_decompress_deinit(pDecomp_state);
					return CompressErrs::DATA_ERROR;
				}
				dst_bytes_left -= out_num_bytes;
			}

			if (status >= LZHAM_DECOMP_STATUS_FIRST_SUCCESS_OR_FAILURE_CODE)
				break;
		}
		_aligned_free(in_file_buf);
		in_file_buf = NULL;

		_aligned_free(out_file_buf);
		out_file_buf = NULL;

		src_bytes_left += (in_file_buf_size - in_file_buf_ofs);

		return status == LZHAM_DECOMP_STATUS_SUCCESS ? CompressErrs::OK : CompressErrs::DATA_ERROR;*/

		return CompressErrs::DATA_ERROR;
	}
}