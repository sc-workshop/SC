#include "Shape.h"

#include <Bytestream.h>
#include <cstdint>

namespace sc
{
	void Shape::loadTag(IBinaryStream* stream, uint8_t tag)
	{
		id = stream->readUInt16();

		uint16_t commandsCount = stream->readUInt16();

		uint16_t m_pointsCount = 4 * commandsCount;
		if (tag == 18)
			m_pointsCount = stream->readUInt16();

		commands.resize(commandsCount);
		vertices.resize(m_pointsCount);

#ifdef SC_DEBUG
		printf("[Shape] Tag %u loading. Id: %u. Commands count: %u. Points count: %u.\n", tag, id, commandsCount, m_pointsCount);
#endif // SC_DEBUG

		int commandsLoaded = 0;
		int pointsOffset = 0;
		while (true)
		{
			uint8_t commandTag = stream->readUInt8();
			uint32_t commandTagLength = stream->readUInt32();

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
				commands[commandsLoaded].loadTag(stream, commandTag, &pointsOffset, vertices);
				commandsLoaded++;
				break;
			default:
				stream->skip(commandTagLength);
				break;
			}
		}
	}

	uint16_t Shape::getTag()
	{
		int maxRectCommands = 0;

		for (int i = 0; commands.size() > i; i++)
			if (commands[i].rectangle())
				maxRectCommands++;

		return commands.size() == maxRectCommands ? 2 : 18;
	}

	void ShapeDrawBitmapCommand::loadTag(IBinaryStream* stream, uint8_t tag, int* pointsOffset, std::vector<ShapeDrawBitmapCommandVertex>& vertices)
	{
		m_textureIndex = stream->readUInt8();
		m_normalized = tag == 22;
		m_rectangle = tag == 4;

		m_pointsCount = m_rectangle ? 4 : stream->readUInt8();

		for (int i = 0; i < m_pointsCount; i++)
		{
			float x = stream->readTwip();
			float y = stream->readTwip();

			int idx = *pointsOffset + i;

			vertices[*pointsOffset + i].x = x;
			vertices[*pointsOffset + i].y = y;
		}

		for (int i = 0; i < m_pointsCount; i++)
		{
			float u = stream->readUInt16();
			float v = stream->readUInt16();

			if (m_normalized) {
				u = u / 0xFFFF;
				v = v / 0xFFFF;
			}

			vertices[*pointsOffset + i].u = u;
			vertices[*pointsOffset + i].v = v;
		}

#ifdef SC_DEBUG
		printf("Texture index: %u. Points count: %u.\n", m_textureIndex, m_pointsCount);
#ifdef DEEP_SC_DEBUG
		for (int i = 0; m_pointsCount > i; i++) {
			printf("		{\n		\"vert\":[%f,%f],\n		\"texcoord\":[%f,%f]\n		}\n", vertices[*pointsOffset + i].x, vertices[*pointsOffset + i].y, vertices[*pointsOffset + i].u, vertices[*pointsOffset + i].v);
		}
#endif // DEEP_SC_DEBUG

#endif // SC_DEBUG

		* pointsOffset += m_pointsCount;
	}
	uint16_t ShapeDrawBitmapCommand::getTag()
	{
		return m_normalized ? (m_rectangle ? 4 : 22) : 17;
	}
}