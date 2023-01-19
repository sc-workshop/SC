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
}