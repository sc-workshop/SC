#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/SWFTexture.h"
#include <math.h>

#define SWFTEXTURE_BLOCK_SIZE 32

namespace sc
{
	const std::vector<SWFTexture::PixelFormat> SWFTexture::pixelFormatTable({ 
		SWFTexture::PixelFormat::RGBA8,
		SWFTexture::PixelFormat::RGBA8,
		SWFTexture::PixelFormat::RGBA4,
		SWFTexture::PixelFormat::RGB5_A1,
		SWFTexture::PixelFormat::RGB565,
		SWFTexture::PixelFormat::RGBA8,
		SWFTexture::PixelFormat::LUMINANCE8_ALPHA8,
		SWFTexture::PixelFormat::RGBA8,
		SWFTexture::PixelFormat::RGBA8,
		SWFTexture::PixelFormat::RGBA4,
		SWFTexture::PixelFormat::LUMINANCE8
	});

	const std::vector<uint8_t> SWFTexture::pixelByteSizeTable({ 
		4, 
		4, 
		2, 
		2, 
		2, 
		4, 
		2, 
		4, 
		4, 
		2, 
		1 
	});

	void SWFTexture::load(sc::SupercellSWF* swf, uint8_t tag, bool useExternalTexture)
	{
		/* Tag processing */

		if (tag == 16 || tag == 19 || tag == 29) {
			m_magFilter = Filter::LINEAR;
			m_minFilter = Filter::LINEAR_MIPMAP_NEAREST;
		}
		else if (tag == 34) {
			m_magFilter = Filter::LINEAR;
			m_minFilter = Filter::LINEAR;
		}
		else {
			m_magFilter = Filter::LINEAR;
			m_minFilter = Filter::NEAREST;
		}

		if (tag == 27 || tag == 28 || tag == 29) {
			m_blocks = false;
		}
		else {
			m_blocks = true;
		}

		if (tag == 1 || tag == 16 || tag == 28 || tag == 29) {
			m_downscaling = true;
		}
		else {
			m_downscaling = false;
		}

		/* Binary data processing */

		uint8_t pixelFormatIndex = swf->readUnsignedByte();
		m_pixelFormat = SWFTexture::pixelFormatTable.at(pixelFormatIndex);

		m_width = swf->readUnsignedShort();
		m_height = swf->readUnsignedShort();

		if (!useExternalTexture)
		{
			uint8_t pixelByteSize = pixelByteSizeTable.at(pixelFormatIndex);
			uint32_t dataSize = ((m_width * m_height) * pixelByteSize);
			data = std::vector<uint8_t>(*swf->read(dataSize), dataSize);

			/* Maybe use it in blocking setter*/
			/*if (m_blocking) {
				for (uint16_t w = 0; m_width > w; w++) {
					for (uint16_t h = 0; m_height > h; h++) {
						for (uint8_t i = 0; pixelByteSize > i; i++) {
							data.push_back(swf->readUnsignedByte());
						}
					}
				}
			}
			else {
				data = std::vector<uint8_t>((m_width * m_height) * pixelByteSize);

				const uint16_t x_blocks = static_cast<uint16_t>(floor(m_width / SWFTEXTURE_BLOCK_SIZE));
				const uint16_t y_blocks = static_cast<uint16_t>(floor(m_height / SWFTEXTURE_BLOCK_SIZE));

				for (uint16_t x_block = 0; x_blocks > x_block; x_block++) {
					for (uint16_t y_block = 0; y_blocks > y_block; y_block++) {
						for (uint8_t y = 0; SWFTEXTURE_BLOCK_SIZE > y; y++) {
							uint16_t pixel_y = (y_block * SWFTEXTURE_BLOCK_SIZE) + y;
							if (pixel_y >= m_height) {
								break;
							}

							for (uint8_t x = 0; SWFTEXTURE_BLOCK_SIZE > x; x++) {
								uint16_t pixel_x = (x_block * SWFTEXTURE_BLOCK_SIZE) + x;
								if (pixel_x >= m_width) {
									break;
								}

								for (uint8_t i = 0; pixelByteSize > i; i++) {
									data[((pixel_x * pixel_y) * pixelByteSize) + i] = swf->readUnsignedByte();
								}
							}
						}
					}
				}
			}*/
		}
	}
}