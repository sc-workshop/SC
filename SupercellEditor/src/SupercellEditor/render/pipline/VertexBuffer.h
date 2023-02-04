#pragma once

#include <glad.h>

namespace sc
{
	class VertexBuffer
	{
	public:
		VertexBuffer(GLfloat* data);
		~VertexBuffer();

	public:
		void bind();
		void unbind();

		void release();

	private:
		GLuint m_id;
	};
}
