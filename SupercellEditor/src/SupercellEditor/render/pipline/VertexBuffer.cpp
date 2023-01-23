#include "SupercellEditor/render/pipline/VertexBuffer.h"

namespace sc
{
	VertexBuffer::VertexBuffer(GLfloat* data)
	{
		glGenBuffers(1, &m_id);

		bind();

		glBufferData(GL_ARRAY_BUFFER, sizeof(data), data, GL_STATIC_DRAW);
	}

	VertexBuffer::~VertexBuffer()
	{
		release();
	}

	void VertexBuffer::bind()
	{
		glBindBuffer(GL_ARRAY_BUFFER, m_id);
	}

	void VertexBuffer::unbind()
	{
		glBindBuffer(GL_ARRAY_BUFFER, 0);
	}

	void VertexBuffer::release()
	{
		glDeleteBuffers(1, &m_id);
	}
}
