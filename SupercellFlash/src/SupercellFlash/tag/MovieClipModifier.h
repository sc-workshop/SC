#pragma once

#include "SupercellFlash/SupercellSWF.h"

#include "SupercellFlash/common/DisplayObject.h"

namespace sc
{
	class MovieClipModifier : public DisplayObject
	{
	public:
		enum Type : uint8_t
		{
			Mask = 38,
			Masked,
			Unmasked,
		};

		void load(SupercellSWF* swf, uint8_t tag)
		{
			m_id = swf->readUnsignedShort();
			
			m_type = (Type)tag;
		}

		Type getType() { return m_type; }

	private:
		Type m_type = Type::Mask;
	};
}
