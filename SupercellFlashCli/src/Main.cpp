#include <SupercellFlash.h>

#include <string>
#include <iostream>
#include <chrono>
#include <SupercellCompression/Signature.h>

int main(int argc, char* argv[])
{
	if (argv[1]) {
		using std::chrono::high_resolution_clock;
		using std::chrono::duration_cast;
		using std::chrono::duration;
		using std::chrono::milliseconds;
		using std::chrono::seconds;

		std::chrono::time_point startTime = high_resolution_clock::now();
		std::string filename(argv[1]);
		sc::SupercellSWF swf;
		swf.load(filename);

		auto endTime = high_resolution_clock::now();
		std::cout << "Operation took: ";

		milliseconds msTime = duration_cast<milliseconds>(endTime - startTime);
		if (msTime.count() < 1000) {
			std::cout << msTime.count() << " miliseconds.";
		}
		else {
			seconds secTime = duration_cast<seconds>(msTime);
			std::cout << secTime.count() << " seconds." << std::endl;
		}
	}

	return 0;
}