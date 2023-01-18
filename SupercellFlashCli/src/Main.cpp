#include <SupercellSWF.h>

#include <string>
#include <iostream>

int main(int argc, char* argv[])
{
	if (argv[1]) {
		std::cout << argv[1] << std::endl;
		sc::SupercellSWF swf;
		swf.load(std::string(argv[1]));
	}
}