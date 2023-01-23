#include "SupercellEditor/render/pipline/VertexArray.h"

namespace sc
{
	VertexArray::VertexArray()
	{
		glGenVertexArrays(1, &m_id);
	}

	VertexArray::~VertexArray()
	{
		release();
	}

	void VertexArray::linkVertexBuffer(VertexBuffer& buffer, GLint size, GLuint layout)
	{
		buffer.bind();

		glVertexAttribPointer(layout, size, GL_FLOAT, GL_FALSE, 0, nullptr);
		glEnableVertexAttribArray(layout);

		buffer.unbind();
	}

	void VertexArray::bind()
	{
		glBindVertexArray(m_id);
	}

	void VertexArray::unbind()
	{
		glBindVertexArray(0);
	}

	void VertexArray::release()
	{
		glDeleteVertexArrays(1, &m_id);
	}
}
