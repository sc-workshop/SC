#pragma once

#include <cstdio>
#include <string>

#include <Bytestream.h>

#include "common/Export.h"

#include "Shape.h"

//
//#include "SupercellSWF/MovieClip.h"
//#include "SupercellSWF/SWFTexture.h"
//#include "SupercellSWF/TextField.h"
//#include "SupercellSWF/MovieClipModifier.h"
//

namespace sc
{
	class SupercellSWF
	{
	public:
		SupercellSWF();
		~SupercellSWF();

	public:
		void load(const std::string& filePath);

	private:
		bool loadInternal(IBinaryStream* stream, bool isTexture);
		bool loadTags(IBinaryStream* stream);

		void initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount);

	private:
		IBinaryStream* m_buffer;

		int m_shapesCount;
		int m_movieClipsCount;
		int m_texturesCount;
		int m_textFieldsCount;
		int m_movieClipModifiersCount;

		int m_exportsCount;
		Export* m_exports;

		Shape* m_shapes;
		/*MovieClip* m_movieClips;
		SWFTexture* m_textures;
		TextField* m_textFields;
		MovieClipModifier* m_movieClipModifiers;*/
	};
}
