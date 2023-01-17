#pragma once

namespace sc
{
	class SupercellSWF;

	class SWFTexture
	{
	public:
		SWFTexture() { }
		~SWFTexture() { }

	public:
		void load(SupercellSWF* swf, uint8_t tag, bool useExternalTexture);

	private:
		uint16_t m_width = 0;
		uint16_t m_height = 0;
	};
}
