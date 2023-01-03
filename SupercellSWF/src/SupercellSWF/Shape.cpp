#include "SupercellSWF/Shape.h"

namespace sc
{
	void Shape::load(SupercellSWF* swf, int tag)
	{
		id = swf->readUnsignedShort();

		m_commandsCount = swf->readUnsignedShort();
		m_commands = new ShapeDrawBitmapCommand[m_commandsCount];

		m_pointsCount = 4 * m_commandsCount;
		if (tag == 18)
			m_pointsCount = swf->readUnsignedShort();

		m_twips = new ShapeDrawBitmapCommandVertex[m_pointsCount];
		m_texcoords = new ShapeDrawBitmapCommandVertex[m_pointsCount];

		int commandsLoaded = 0;
		int pointsOffset = 0;
		while (true)
		{
			int commandTag = swf->readByte();
			int commandTagLength = swf->readInt();

			if (commandTag == 0)
				break;

			switch (commandTag)
			{
			case 4:
			case 17:
			case 22:
				m_commands[commandsLoaded].load(swf, commandTag, &pointsOffset, m_twips, m_texcoords);
				commandsLoaded++;
				break;
			default:
				swf->skip(commandTagLength);
				break;
			}
		}
	}

	void ShapeDrawBitmapCommand::load(SupercellSWF* swf, int tag, int* pointsOffset, ShapeDrawBitmapCommandVertex* twips, ShapeDrawBitmapCommandVertex* texcoords)
	{
		m_textureIndex = swf->readUnsignedByte();

		m_pointsCount = tag == 4 ? 4 : swf->readUnsignedByte();

		for (int i = 0; i < m_pointsCount; i++)
		{
			float x = swf->readTwip();
			float y = swf->readTwip();

			twips[*pointsOffset + i].x = x;
			twips[*pointsOffset + i].y = y;
		}

		for (int i = 0; i < m_pointsCount; i++)
		{
			float u = (float)swf->readUnsignedShort() / 0xFFFF;
			float v = (float)swf->readUnsignedShort() / 0xFFFF;

			twips[*pointsOffset + i].u = u;
			twips[*pointsOffset + i].v = v;
		}

		*pointsOffset += m_pointsCount;
	}
}
