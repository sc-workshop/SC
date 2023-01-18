#pragma once

#include "SupercellFlash/tag/Matrix2x3.h"
#include "SupercellFlash/tag/ColorTransform.h"

namespace sc
{
	struct MatrixBank
	{
		Matrix2x3* matrices;
		ColorTransform* colorTransforms;
	};
}
