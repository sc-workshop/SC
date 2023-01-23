#include "SupercellEditor/render/pipline/Shader.h"

#include "SupercellEditor/render/internal/Shaders.h"

namespace
{
	std::string readFileAsString(const std::string& filePath)
	{
		std::ifstream file(filePath, std::ios::binary);
		if (!file)
			throw ("Failed to open shader file!");

		std::string result;

		file.seekg(0, std::ios::end);
		result.resize(file.tellg());
		file.seekg(0, std::ios::beg);

		file.read(&result[0], result.size());
		file.close();

		return result;
	}
}

namespace sc
{
	Shader::Shader()
	{
		// shaders
		GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
		glShaderSource(vertexShader, 1, &vertexShaderSource, nullptr);
		glCompileShader(vertexShader);

		GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
		glShaderSource(fragmentShader, 1, &fragmentShaderSource, nullptr);
		glCompileShader(fragmentShader);

		// shader program
		m_id = glCreateProgram();
		glAttachShader(m_id, vertexShader);
		glAttachShader(m_id, fragmentShader);
		glLinkProgram(m_id);

		glDeleteShader(vertexShader);
		glDeleteShader(fragmentShader);
	}

	Shader::~Shader()
	{
		release();
	}

	void Shader::bind()
	{
		glUseProgram(m_id);
	}

	void Shader::unbind()
	{
		glUseProgram(0);
	}

	void Shader::release()
	{
		glDeleteProgram(m_id);
	}

}
