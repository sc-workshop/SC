#include "SupercellFlash/tag/ColorTransform.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc
{
	void ColorTransform::load(SupercellSWF* swf)
	{
		redAdd = swf->readUnsignedByte();
		greenAdd = swf->readUnsignedByte();
		blueAdd = swf->readUnsignedByte();

		alpha = (float)swf->readUnsignedByte() / 255.0f;

		redMul = (float)swf->readUnsignedByte() / 255.0f;
		greenMul = (float)swf->readUnsignedByte() / 255.0f;
		blueMul = (float)swf->readUnsignedByte() / 255.0f;
	}

	void ColorTransform::save(SupercellSWF* swf)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		tagStream.writeUInt8(redAdd);
		tagStream.writeUInt8(greenAdd);
		tagStream.writeUInt8(blueAdd);

		tagStream.writeUInt8((uint8_t)(alpha * 255.0f));

		tagStream.writeUInt8((uint8_t)(redMul * 255.0f));
		tagStream.writeUInt8((uint8_t)(greenMul * 255.0f));
		tagStream.writeUInt8((uint8_t)(blueMul * 255.0f));

		swf->writeTag(9, tagBuffer);
	}
}