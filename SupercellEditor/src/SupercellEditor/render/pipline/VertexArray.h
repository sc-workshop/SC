#pragma once

#include <glad.h>

#include "SupercellEditor/render/pipline/VertexBuffer.h"

namespace sc
{
	class VertexArray
	{
	public:
		VertexArray();
		~VertexArray();

	public:
		void linkVertexBuffer(VertexBuffer& buffer, GLint size, GLuint layout);

		void bind();
		void unbind();

		void release();

	private:
		GLuint m_id;
	};
}
