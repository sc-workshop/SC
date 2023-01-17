#include "Shape.h"
#include "SupercellSWF.h"

namespace sc
{
	uint16_t ShapeDrawBitmapCommand::getTag()
	{
		return m_normalized ? (m_rectangle ? 4 : 22) : 17;
	}

	void ShapeDrawBitmapCommand::load(SupercellSWF* swf, uint8_t tag, int* pointsOffset, std::vector<ShapeDrawBitmapCommandVertex>& m_vertices)
	{
		uint8_t m_textureIndex = swf->readUnsignedByte();
		bool m_normalized = tag == 22;
		bool m_rectangle = tag == 4;

		uint8_t m_pointsCount = m_rectangle ? 4 : swf->readUnsignedByte();

		for (int i = 0; i < m_pointsCount; i++)
		{
			float x = swf->readTwip();
			float y = swf->readTwip();

			int idx = *pointsOffset + i;

			m_vertices[*pointsOffset + i].x = x;
			m_vertices[*pointsOffset + i].y = y;
		}

		for (int i = 0; i < m_pointsCount; i++)
		{
			float u = swf->readUnsignedShort();
			float v = swf->readUnsignedShort();

			if (m_normalized) {
				u = u / 0xFFFF;
				v = v / 0xFFFF;
			}

			m_vertices[*pointsOffset + i].u = u;
			m_vertices[*pointsOffset + i].v = v;
		}

#ifdef SC_DEBUG
		printf("Texture index: %u. Points count: %u.\n", m_textureIndex, m_pointsCount);
#ifdef DEEP_SC_DEBUG
		for (int i = 0; m_pointsCount > i; i++) {
			printf("		{\n		\"vert\":[%f,%f],\n		\"texcoord\":[%f,%f]\n		}\n", m_vertices[*pointsOffset + i].x, m_vertices[*pointsOffset + i].y, m_vertices[*pointsOffset + i].u, m_vertices[*pointsOffset + i].v);
		}
#endif // DEEP_SC_DEBUG

#endif // SC_DEBUG

		* pointsOffset += m_pointsCount;
	}

	uint8_t Shape::getTag()
	{
		int maxRectCommands = 0;

		for (int i = 0; m_commands.size() > i; i++)
			if (m_commands[i].rectangle())
				maxRectCommands++;

		return m_commands.size() == maxRectCommands ? 2 : 18;
	}

	void Shape::load(SupercellSWF* swf, uint8_t tag)
	{
		id = swf->readUnsignedShort();

		uint16_t m_commandsCount = swf->readUnsignedShort();

		uint16_t m_pointsCount = 4 * m_commandsCount;
		if (tag == 18)
			m_pointsCount = swf->readUnsignedShort();

		for (int i = 0; i < m_commandsCount; i++)
			m_commands.push_back(ShapeDrawBitmapCommand());

		for (int i = 0; i < m_pointsCount; i++)
			m_vertices.push_back(ShapeDrawBitmapCommandVertex());

#ifdef SC_DEBUG
		printf("[Shape] Tag %u loading. Id: %u. Commands count: %u. Points count: %u.\n", tag, id, m_commandsCount, m_pointsCount);
#endif // SC_DEBUG

		int m_commandsLoaded = 0;
		int pointsOffset = 0;
		while (true)
		{
			uint8_t commandTag = swf->readUnsignedByte();
			uint32_t commandTagLength = swf->readInt();

			if (commandTagLength < 0)
				throw std::runtime_error("Negative draw command tag length in .sc file");

			if (commandTag == 0)
				break;

#ifdef SC_DEBUG
			printf("	Tag %u loading. Length: %u. ", commandTag, commandTagLength);
#endif // SC_DEBUG

			switch (commandTag)
			{
			case 4:
			case 17:
			case 22:
				m_commands[m_commandsLoaded].load(swf, commandTag, &pointsOffset, m_vertices);
				m_commandsLoaded++;
				break;
			default:
				swf->skip(commandTagLength);
				break;
			}
		}
	}
}