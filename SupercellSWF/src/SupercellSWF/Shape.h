#pragma once

#include "SupercellSWF/SupercellSWF.h"

namespace sc
{
	class Shape
	{
	public:
		void load(SupercellSWF* swf, int tag);

	private:
		int id;

		int m_commandsCount;
		int m_pointsCount;
		ShapeDrawBitmapCommand* m_commands;

		ShapeDrawBitmapCommandVertex* m_twips;
		ShapeDrawBitmapCommandVertex* m_texcoords;
	};

	struct ShapeDrawBitmapCommandVertex
	{
		union
		{
			struct
			{
				float x;
				float y;
			};

			struct
			{
				float u;
				float v;
			};
		};
	};

	class ShapeDrawBitmapCommand
	{
	public:
		void load(SupercellSWF* swf, int tag, int* pointsOffset, ShapeDrawBitmapCommandVertex* twips, ShapeDrawBitmapCommandVertex* texcoords);

	private:
		int m_textureIndex;
		int m_pointsCount;
	};
}
