#include "SupercellFlash/tag/Shape.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc
{
	void Shape::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();

		uint16_t m_commandsCount = swf->readUnsignedShort();
		commands = std::vector<ShapeDrawBitmapCommand>(m_commandsCount);

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
				commands[commandsLoaded].load(swf, commandTag);
				commandsLoaded++;
				break;

			default:
				swf->skip(commandTagLength);
				break;
			}
		}
	}

	void Shape::save(SupercellSWF* swf)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt16(m_id);
		tagStream.writeUInt16(commands.size());

		uint8_t tag = 2;

		uint16_t totalVerticesCount = 0;
		for (ShapeDrawBitmapCommand command : commands)
		{
			if (command.vertices.size() > 4)
			{
				tag = 18;
			}

			totalVerticesCount += command.vertices.size();
		}

		if (tag == 18)
			tagStream.writeUInt16(totalVerticesCount);

		for (ShapeDrawBitmapCommand command : commands)
		{
			command.save(tagStream, tag);
		}

		// End tag
		tagStream.writeUInt8(0);
		tagStream.writeInt32(0);

		tagStream.close();

		// TODO: tag 2 support
		swf->writeTag(tag, tagBuffer);
	}
}