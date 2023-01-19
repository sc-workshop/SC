#include "SupercellEditor.h"

// Crap, for example

#include <cstdio>

#include <glad/glad.h>
#include <GLFW/glfw3.h>

void glfw_error_callback(int error, const char* description)
{
	fprintf(stderr, "GLFW Error: %s\n", description);
}

int main(int argc, char** argv)
{
	glfwSetErrorCallback(glfw_error_callback);

	if (!glfwInit())
		throw ("Failed to initialize GLFW!");

	
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

	glfwSwapInterval(1); // V-Sync on

	// Main loop
	while (!glfwWindowShouldClose(window))
	{
		glfwPollEvents();

		/* User input and draw here */

		glClear(GL_COLOR_BUFFER_BIT);
		glClearColor(0.10f, 0.11f, 0.20f, 1.0f);

		/* User input and draw here */

		glfwSwapBuffers(window);
	}

	glfwDestroyWindow(window);

	glfwTerminate();

	return 0;
}
