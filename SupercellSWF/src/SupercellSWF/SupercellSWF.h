#pragma once

#include <cstdio>
#include <string>

#include "SupercellSWF/Shape.h"
#include "SupercellSWF/MovieClip.h"
#include "SupercellSWF/SWFTexture.h"
#include "SupercellSWF/TextField.h"
#include "SupercellSWF/MovieClipModifier.h"

#include "SupercellSWF/Export.h"

namespace sc
{
	class SupercellSWF
	{
	public:
		SupercellSWF();
		~SupercellSWF();

	public:
		void skip(int length);
		bool readBool();
		int readByte();
		int readUnsignedByte();
		int readShort();
		int readUnsignedShort();
		int readInt();
		std::string readAscii();
		float readTwip();

	public:
		void load(const std::string& filePath);

	private:
		bool loadInternal(const std::string& filePath, bool isTexture);
		bool loadTags();

		void initMatrixBank(int matricesCount, int colorTransformsCount);

	private:
		FILE* m_file;

		int m_shapesCount;
		int m_movieClipsCount;
		int m_texturesCount;
		int m_textFieldsCount;
		int m_movieClipModifiersCount;

		int m_exportsCount;

		Shape* m_shapes;
		MovieClip* m_movieClips;
		SWFTexture* m_textures;
		TextField* m_textFields;
		MovieClipModifier* m_movieClipModifiers;

		Export* m_exports;
	};
}
