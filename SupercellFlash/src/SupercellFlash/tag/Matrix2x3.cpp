#include "SupercellFlash/tag/Matrix2x3.h"

#include "SupercellFlash/SupercellSWF.h"

namespace sc {
	void Matrix2x3::load(SupercellSWF* swf, uint8_t tag) {
		float divider = tag == 8 ? 1024.0f : 65535.0f;

		a = (float)swf->readInt() / divider;
		b = (float)swf->readInt() / divider;
		c = (float)swf->readInt() / divider;
		d = (float)swf->readInt() / divider;

		tx = swf->readTwip();
		ty = swf->readTwip();
	}

	void Matrix2x3::save(SupercellSWF* swf)
	{
		std::vector<uint8_t> tagBuffer;
		BufferStream tagStream(&tagBuffer);

		uint8_t tag = 8; // TODO: tag 36 support (https://github.com/danila-schelkov/sc-editor/blob/master/src/com/vorono4ka/swf/Matrix2x3.java#L61)
		float multiplier = 1024.0f;

		tagStream.writeInt32((int)(a * multiplier));
		tagStream.writeInt32((int)(b * multiplier));
		tagStream.writeInt32((int)(c * multiplier));
		tagStream.writeInt32((int)(d * multiplier));

		tagStream.writeInt32((int)(tx * 20.0f));
		tagStream.writeInt32((int)(ty * 20.0f));

		swf->writeTag(tag, tagBuffer);
	}
}