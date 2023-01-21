#include "SupercellFlash/SupercellSWF.h"
#include "SupercellFlash/tag/Shape.h"

namespace sc
{
	void ShapeDrawBitmapCommand::load(SupercellSWF* swf, uint8_t tag)
	{
		m_textureIndex = swf->readUnsignedByte();

		uint8_t pointsCount = tag == 4 ? 4 : swf->readUnsignedByte();
		m_vertices = std::vector<ShapeDrawBitmapCommandVertex>(pointsCount);

		for (uint8_t i = 0; i < pointsCount; i++)
		{
			m_vertices[i].x = swf->readTwip();
			m_vertices[i].y = swf->readTwip();
		}

		for (uint8_t i = 0; i < pointsCount; i++)
		{
			m_vertices[i].u = (float)swf->readUnsignedShort() / 65535.0f;
			m_vertices[i].v = (float)swf->readUnsignedShort() / 65535.0f;
		}
	}

	void Shape::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		uint16_t m_commandsCount = swf->readUnsignedShort();
		m_commands = std::vector<ShapeDrawBitmapCommand>(m_commandsCount);

		if (tag == 18)
			swf->readUnsignedShort(); // total vertices count

		uint16_t commandsLoaded = 0;
		while (true)
		{
			uint8_t commandTag = swf->readUnsignedByte();
			int32_t commandTagLength = swf->readInt();

			if (commandTagLength < 0)
				throw std::runtime_error("Negative draw command tag length in .sc file");

			if (commandTag == 0)
				break;

			switch (commandTag)
			{
			case 4:
			case 17:
			case 22:
				m_commands[commandsLoaded].load(swf, commandTag);
				commandsLoaded++;
				break;

			default:
				swf->skip(commandTagLength);
				break;
			}
		}
	}
}