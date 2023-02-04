#pragma once

#include <glad.h>

#include <string>
#include <fstream>
#include <sstream>

namespace sc
{
	class Shader
	{
	public:
		Shader();
		~Shader();

	public:
		void bind();
		void unbind();

		void release();

	private:
		GLuint m_id;
	};
}
