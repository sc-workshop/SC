#include "SupercellFlash/SupercellSWF.h"

#include "SupercellFlash/tag/MovieClip.h"

namespace sc
{
	void MovieClip::load(SupercellSWF* swf, uint8_t tag)
	{
		m_id = swf->readUnsignedShort();
		m_frameRate = swf->readUnsignedByte();

		uint16_t framesCount = swf->readUnsignedShort();
		frames = std::vector<MovieClipFrame>(framesCount);

		if (tag == 3 || tag == 14)
			throw std::runtime_error("TAG_MOVIE_CLIP and TAG_MOVIE_CLIP_4 is unsupported");

		int32_t frameElementsCount = swf->readInt();
		frameElements = std::vector<MovieClipFrameElement>(frameElementsCount);

		for (int32_t i = 0; i < frameElementsCount; i++)
		{
			frameElements[i].instanceIndex = swf->readUnsignedShort();
			frameElements[i].matrixIndex = swf->readUnsignedShort();
			frameElements[i].colorTransformIndex = swf->readUnsignedShort();
		}

		uint16_t instancesCount = swf->readUnsignedShort();
		instances = std::vector<DisplayObjectInstance>(instancesCount);

		for (int16_t i = 0; i < instancesCount; i++)
		{
			instances[i].id = swf->readUnsignedShort();
		}

		if (tag == 12 || tag == 35)
		{
			for (int16_t i = 0; i < instancesCount; i++)
			{
				instances[i].blend = swf->readUnsignedByte();
			}
		}

		for (int16_t i = 0; i < instancesCount; i++)
		{
			instances[i].name = swf->readAscii();
		}

		uint16_t framesLoaded = 0;
		while (true)
		{
			uint8_t frameTag = swf->readUnsignedByte();
			int32_t frameTagLength = swf->readInt();

			if (frameTagLength < 0)
				throw std::runtime_error("Negative frame tag length in .sc file");

			if (frameTag == 0)
				break;

			switch (frameTag)
			{
			case 11:
				frames[framesLoaded].load(swf);
				framesLoaded++;
				break;

			case 31:
				m_scalingGrid = new ScalingGrid();
				m_scalingGrid->x = swf->readTwip();
				m_scalingGrid->y = swf->readTwip();
				m_scalingGrid->width = swf->readTwip();
				m_scalingGrid->height = swf->readTwip();
				break;

			case 41:
				m_matrixBankIndex = swf->readUnsignedByte();
				break;

			default:
				swf->skip(frameTagLength);
				break;
			}
		}
	}

	void MovieClip::save(SupercellSWF* swf)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt16(m_id);
		tagStream.writeUInt8(m_frameRate);
		tagStream.writeUInt16(frames.size());

		uint8_t tag = 12; // idk how to add tag 35 support bcs we don't know difference between them

		tagStream.writeInt32(frameElements.size());
		for (MovieClipFrameElement element : frameElements)
		{
			tagStream.writeUInt16(element.instanceIndex);
			tagStream.writeUInt16(element.matrixIndex);
			tagStream.writeUInt16(element.colorTransformIndex);
		}

		tagStream.writeInt16(instances.size());

		for (DisplayObjectInstance instance : instances)
		{
			tagStream.writeUInt16(instance.id);
		}

		for (DisplayObjectInstance instance : instances)
		{
			tagStream.writeUInt8(instance.blend);
		}

		for (DisplayObjectInstance instance : instances)
		{
			tagStream.writeUInt8(instance.name.length());

			// FIXME: I think we should rework some methods in ByteStream
			const char* c_instanceName = instance.name.c_str();
			tagStream.write(&c_instanceName, instance.name.length());
		}

		for (MovieClipFrame frame : frames)
		{
			frame.save(tagStream);
		}

		if (m_scalingGrid)
		{
			tagStream.writeUInt8(31);
			tagStream.writeInt32(16);

			tagStream.writeInt32((int32_t)(m_scalingGrid->x * 20.0f));
			tagStream.writeInt32((int32_t)(m_scalingGrid->y * 20.0f));
			tagStream.writeInt32((int32_t)(m_scalingGrid->width * 20.0f));
			tagStream.writeInt32((int32_t)(m_scalingGrid->height * 20.0f));
		}

		if (m_matrixBankIndex != 0)
		{
			tagStream.writeUInt8(41);
			tagStream.writeInt32(1);
			tagStream.writeUInt8(m_matrixBankIndex);
		}

		tagStream.close();

		swf->writeTag(tag, tagBuffer);
	}
}