#pragma once

namespace sc
{
	class SupercellSWF;

	class SWFTexture
	{
	public:
		void load(SupercellSWF* swf, uint8_t tag, bool useExternalTexture);

	private:
		uint8_t m_pixelFormatIndex = 0;
		uint8_t m_filterIndex = 1;

		uint16_t m_width = 0;
		uint16_t m_height = 0;

		uint8_t* m_data;
	};
}
