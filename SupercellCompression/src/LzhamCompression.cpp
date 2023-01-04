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

		const uint cInBufSize = LZHAM_DECOMP_INPUT_BUFFER_SIZE;
		uint8* in_file_buf = static_cast<uint8*>(_aligned_malloc(cInBufSize, 16));

		uint out_buf_size = LZHAM_DECOMP_OUTPUT_BUFFER_SIZE;
		uint8* out_file_buf = static_cast<uint8*>(_aligned_malloc(out_buf_size, 16));
		if (!out_file_buf)
		{
			_aligned_free(in_file_buf);
			return CompressErrs::ALLOC_ERROR;
		}

		uint32_t src_bytes_left = inStream.size() - inStream.tell();
		uint32_t dst_bytes_left = fileSize;

		uint in_file_buf_size = 0;
		uint in_file_buf_ofs = 0;

		lzham_decompress_params params;
		memset(&params, 0, sizeof(params));
		params.m_struct_size = sizeof(lzham_decompress_params);
		params.m_dict_size_log2 = dictSize;
		params.m_table_update_rate = 8;

		lzham_decompress_state_ptr pDecomp_state = lzham_decompress_init(&params);
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
                in_file_buf_size = static_cast<uint>(cInBufSize < src_bytes_left ? cInBufSize : src_bytes_left);
                if ( inStream.read(in_file_buf, in_file_buf_size) != in_file_buf_size)
                {
                    _aligned_free(in_file_buf);
                    _aligned_free(out_file_buf);
                    lzham_decompress_deinit(pDecomp_state);
                    return CompressErrs::DATA_ERROR;
                }

                src_bytes_left -= in_file_buf_size;

                in_file_buf_ofs = 0;
            }

            uint8* pIn_bytes = &in_file_buf[in_file_buf_ofs];
            size_t num_in_bytes = in_file_buf_size - in_file_buf_ofs;
            uint8* pOut_bytes = out_file_buf;
            size_t out_num_bytes = out_buf_size;

			{
				status = lzham_decompress(pDecomp_state, pIn_bytes, &num_in_bytes, pOut_bytes, &out_num_bytes, src_bytes_left == 0);
			}

            if (num_in_bytes)
            {
                in_file_buf_ofs += (uint)num_in_bytes;
            }

            if (out_num_bytes)
            {
                if (outStream.write(out_file_buf, static_cast<uint>(out_num_bytes)) != out_num_bytes)
                {
                    _aligned_free(in_file_buf);
                    _aligned_free(out_file_buf);
                    lzham_decompress_deinit(pDecomp_state);
					return CompressErrs::DATA_ERROR;
                }

                if (out_num_bytes > dst_bytes_left)
                {
                    _aligned_free(in_file_buf);
                    _aligned_free(out_file_buf);
                    lzham_decompress_deinit(pDecomp_state);
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

		lzham_decompress_deinit(pDecomp_state);
		pDecomp_state = NULL;

		return CompressErrs::OK;
	}
}