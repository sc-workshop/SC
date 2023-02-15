#pragma once

#include "SupercellFlash/common/DisplayObject.h"

namespace sc
{
	class SupercellSWF;

	class TextField : public DisplayObject
	{
	public:
		TextField() { }
		virtual ~TextField() { }

		/* Getters */
	public:
		std::string text() { return m_text; }

		std::string fontName() { return m_fontName; }
		int32_t fontColor() { return m_fontColor; }
		uint8_t fontSize() { return m_fontSize; }
		uint8_t fontAlign() { return m_fontAlign; }

		int16_t left() { return m_left; }
		int16_t top() { return m_top; }
		int16_t right() { return m_right; }
		int16_t bottom() { return m_bottom; }

		bool isBold() { return m_isBold; }
		bool isItalic() { return m_isItalic; }
		bool isMultiline() { return m_isMultiline; }
		bool isOutlined() { return m_isOutlined; }

		bool useDeviceFont() { return m_useDeviceFont; }
		bool adjustFontBounds() { return m_adjustFontBounds; }

	public:
		void load(SupercellSWF* swf, uint8_t tag);

	private:
		std::string m_text = "";

		std::string m_fontName = "";
		int32_t m_fontColor = 0xFFFFFF;
		uint8_t m_fontSize = 0;
		uint8_t m_fontAlign = 0;

		int16_t m_left = 0;
		int16_t m_top = 0;
		int16_t m_right = 0;
		int16_t m_bottom = 0;

		bool m_isBold = false;
		bool m_isItalic = false;
		bool m_isMultiline = false;
		bool m_isOutlined = false;

		bool m_useDeviceFont = false;
		bool m_adjustFontBounds = false;
	};
}
