#pragma once

namespace sc
{

	class SupercellSWF;

	class SWFTexture
	{
	public:
		void load(SupercellSWF* swf, uint8_t tag, bool useExternalTexture);
		/* Defines */
		enum class Filter : uint8_t
		{
			LINEAR,
			NEAREST,
			LINEAR_MIPMAP_NEAREST
		};

		enum class PixelFormat : uint8_t
		{
			RGBA8,
			RGBA4,
			RGB5_A1,
			RGB565,
			LUMINANCE8_ALPHA8,
			LUMINANCE8
		};

		static const std::vector<PixelFormat> pixelFormatTable;
		static const std::vector<uint8_t> pixelByteSizeTable;

		/* Getters */

		PixelFormat pixelFormat() { return m_pixelFormat; }

		Filter magFilter() { return m_magFilter; }
		Filter minFilter() { return m_minFilter; }

		uint16_t width() { return m_width; }
		uint16_t height() { return m_height; }

		bool blocks() { return m_blocks; }
		bool downscaling() { return m_downscaling; }

		/* Setters */

		void pixelFormat(PixelFormat type) { m_pixelFormat = type; }

		void magFilter(Filter filter) { m_magFilter = filter; }
		void minFilter(Filter filter) { m_minFilter = filter; }

		void width(uint16_t width) { m_width = width; } //TODO: make a custom limit here?
		void height(uint16_t height) { m_height = height; }

		void blocks(bool status) { m_blocks = status; }
		void downscaling(bool status) { m_downscaling = status; }

		/* Image data */
		std::vector<uint8_t> data;

	private:
		PixelFormat m_pixelFormat = PixelFormat::RGBA8;

		Filter m_magFilter = Filter::LINEAR;
		Filter m_minFilter = Filter::NEAREST;

		uint16_t m_width = 0;
		uint16_t m_height = 0;

		bool m_blocks = false;
		bool m_downscaling = true;
	};
}
