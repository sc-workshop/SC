#include "SupercellFlash/tag/MovieClipFrame.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc
{
	void MovieClipFrame::load(SupercellSWF* swf)
	{
		elementsCount = swf->readUnsignedShort();
		label = swf->readAscii();
	}

	void MovieClipFrame::save(BufferStream& movieClipStream)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt16(elementsCount);

		tagStream.writeUInt8(label.length());
		const char* c_label = label.c_str();
		tagStream.write(&c_label, label.length());

		tagStream.close();

		movieClipStream.writeUInt8(11);
		movieClipStream.writeInt32(tagBuffer.size());
		movieClipStream.write(tagBuffer.data(), tagBuffer.size());
	}
}
