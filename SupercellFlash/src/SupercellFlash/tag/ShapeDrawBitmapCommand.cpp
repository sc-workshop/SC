#include "SupercellFlash/tag/ShapeDrawBitmapCommand.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc
{
	void ShapeDrawBitmapCommand::load(SupercellSWF* swf, uint8_t tag)
	{
		m_textureIndex = swf->readUnsignedByte();

		uint8_t pointsCount = tag == 4 ? 4 : swf->readUnsignedByte();
		vertices = std::vector<ShapeDrawBitmapCommandVertex>(pointsCount);

		for (uint8_t i = 0; i < pointsCount; i++)
		{
			vertices[i].x = swf->readTwip();
			vertices[i].y = swf->readTwip();
		}

		for (uint8_t i = 0; i < pointsCount; i++)
		{
			vertices[i].u = (float)swf->readUnsignedShort() / 65535.0f;
			vertices[i].v = (float)swf->readUnsignedShort() / 65535.0f;
		}
	}

	void ShapeDrawBitmapCommand::save(BufferStream& shapeStream, uint8_t shapeTag)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt8(m_textureIndex);

		uint8_t tag = 4;
		if (shapeTag == 18)
			tag = 22; // TODO: tag 17 support

		if (tag != 4)
			tagStream.writeUInt8(vertices.size());

		for (ShapeDrawBitmapCommandVertex vertex : vertices)
		{
			tagStream.writeInt32((int32_t)(vertex.x * 20.0f));
			tagStream.writeInt32((int32_t)(vertex.y * 20.0f));
		}

		for (ShapeDrawBitmapCommandVertex vertex : vertices)
		{
			tagStream.writeUInt16((uint16_t)(vertex.u * 65535.0f));
			tagStream.writeUInt16((uint16_t)(vertex.v * 65535.0f));
		}

		tagStream.close();

		shapeStream.writeUInt8(tag);
		shapeStream.write(tagBuffer.data(), tagBuffer.size());
	}
}
