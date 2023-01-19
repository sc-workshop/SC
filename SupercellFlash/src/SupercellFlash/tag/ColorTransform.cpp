#include "SupercellFlash/tag/ColorTransform.h"
#include "SupercellFlash/SupercellSWF.h"

namespace sc
{
	void ColorTransform::load(SupercellSWF* swf)
	{
		redAdd = swf->readUnsignedByte();
		greenAdd = swf->readUnsignedByte();
		blueAdd = swf->readUnsignedByte();

		alphaMul = (float)swf->readUnsignedByte() / 255.0f;
		redMul = (float)swf->readUnsignedByte() / 255.0f;
		greenMul = (float)swf->readUnsignedByte() / 255.0f;
		blueMul = (float)swf->readUnsignedByte() / 255.0f;
	}
}
