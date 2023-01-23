#pragma once

#include <glad/glad.h>

namespace sc
{
	class ElementBuffer
	{
	public:
		ElementBuffer(GLuint* data);
		~ElementBuffer();

	public:
		void bind();
		void unbind();

		void release();

	private:
		GLuint m_id;
	};
}
