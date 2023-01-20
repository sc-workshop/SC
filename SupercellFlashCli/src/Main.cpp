#include <SupercellFlash.h>

#include <string>
#include <iostream>

int main(int argc, char* argv[])
{
	if (argv[1]) {
		sc::SupercellSWF swf;
		swf.load(std::string(argv[1]));
	}
}