#pragma once

#include "SupercellFlash/common/DisplayObject.h"
#include <SupercellFlash/common/TagMap.h>

namespace sc
{
	class SupercellSWF;

	class MovieClipModifier : public DisplayObject
	{
	public:
		enum class Type : uint8_t
		{
			Mask = TAG_MOVIE_CLIP_MODIFIER,
			Masked,
			Unmasked,
		};

		void load(SupercellSWF* swf, uint8_t tag);
		void save(SupercellSWF* swf);

	public:
		Type type() { return m_type; }; // Getter
		void type(Type type) { m_type = type; } // Setter

	private:
		Type m_type = Type::Mask;
	};
}
