#include "SupercellEditor/render/pipline/ElementBuffer.h"

namespace sc
{
	ElementBuffer::ElementBuffer(GLuint* data)
	{
		glGenBuffers(1, &m_id);

		bind();

		glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(data), data, GL_STATIC_DRAW);
	}

	ElementBuffer::~ElementBuffer()
	{
		release();
	}

	void ElementBuffer::bind()
	{
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m_id);
	}

	void ElementBuffer::unbind()
	{
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
	}

	void ElementBuffer::release()
	{
		glDeleteBuffers(1, &m_id);
	}
}
