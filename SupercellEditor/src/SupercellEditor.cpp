#include "SupercellEditor.h"

// Crap, for example

#include <cstdio>
#include <cmath>

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include "SupercellEditor/render/pipline/Shader.h"
#include "SupercellEditor/render/pipline/VertexArray.h"
#include "SupercellEditor/render/pipline/VertexBuffer.h"
#include "SupercellEditor/render/pipline/ElementBuffer.h"

using namespace sc;

// vertices
GLfloat vertices[] = {
	-0.5f, -0.5f * float(std::sqrt(3)) / 3, 0.0f,
	0.5f, -0.5f * float(std::sqrt(3)) / 3, 0.0f,
	0.0f, 0.5f * float(std::sqrt(3)) * 2 / 3, 0.0f,
};

// indices
GLuint indices[] = {
	0, 1, 2
};


void glfw_error_callback(int error, const char* description)
{
	fprintf(stderr, "GLFW Error: %s\n", description);
}

int main(int argc, char** argv)
{
	glfwSetErrorCallback(glfw_error_callback);

	if (!glfwInit())
		throw ("Failed to initialize GLFW!");

	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

	
	GLFWwindow* window = glfwCreateWindow(800, 600, "Supercell Editor", nullptr, nullptr);
	if (!window)
	{
		glfwTerminate();
		throw ("Failed to initialize GLFWwindow!");
	}
	
	glfwMakeContextCurrent(window);
	
	if (!gladLoadGL())
	{
		glfwTerminate();
		throw ("Failed to create OpenGL context (load GLAD)!");
	}

	// shaders
	Shader shader;

	// vertex array
	VertexArray vertexArray;
	vertexArray.bind();

	// buffers
	VertexBuffer vertexBuffer(vertices);
	ElementBuffer elementBuffer(indices);

	vertexArray.linkVertexBuffer(vertexBuffer, 3, 0);

	vertexArray.unbind();

	vertexBuffer.unbind();
	elementBuffer.unbind();
	
	// Main loop

	glfwSwapInterval(1); // V-Sync on

	while (!glfwWindowShouldClose(window))
	{
		glfwPollEvents();

		/* User input and draw here */

		glClear(GL_COLOR_BUFFER_BIT);
		glClearColor(0.10f, 0.11f, 0.20f, 1.0f);

		shader.bind();
		vertexArray.bind();

		glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, 0);

		/* User input and draw here */

		glfwSwapBuffers(window);
	}

	vertexArray.release();
	vertexBuffer.release();
	elementBuffer.release();
	shader.release();

	glfwDestroyWindow(window);

	glfwTerminate();

	return 0;
}
