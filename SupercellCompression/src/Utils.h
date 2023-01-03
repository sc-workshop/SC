#pragma once
#include <stdlib.h>
#include <string>

namespace sc {
    // Small helper functions
	class Utils {
	public:
		static bool fileExist(std::string path);
		static std::string fileBasename(std::string filepath);
        static unsigned int Utils::fileSize(FILE*& file);
		static bool endsWith(std::string const& value, std::string const& ending);
	};

    // Buffer/File streams
    class IBinaryStream {
    public:
        virtual ~IBinaryStream() {};

        virtual size_t read(void* buff, size_t buffSize) = 0;
        virtual size_t write(void* buff, size_t buffSize) = 0;
        virtual long tell() = 0;
        virtual size_t set(int pos) = 0;
        virtual size_t size() = 0;
        virtual bool eof() = 0;
        virtual void setEof(size_t pos) = 0;
        virtual void close() = 0;
    };

    class ScFileStream: public IBinaryStream {
    public:
        ScFileStream(FILE* input) {
            file = input;
        }

    private:
        FILE* file;
        size_t readEofOffset = 0;

    public:
        size_t read(void* buff, size_t buffSize) override { 
            size_t finalPos = tell() + buffSize;
            const size_t readSize = fread(buff, 1, buffSize - (finalPos > size() ? finalPos - size() : 0), file);
            return readSize;
        };
        size_t write(void* buff, size_t buffSize) override { 
            return fwrite(buff, 1, buffSize, file);
        };
        long tell() override { return ftell(file); }
        size_t set(int pos) override { return fseek(file, pos, SEEK_SET); }
        size_t size() override { return Utils::fileSize(file) - readEofOffset; }
        bool eof() override { return size() <= tell() - readEofOffset; };
        void setEof(size_t pos) override { readEofOffset = pos; };
        void close() override { fclose(file); }

    };

    // Error enums
    enum class DecompressorErrs {
        OK = 0,
        FILE_READ_ERROR = 1,
        FILE_WRITE_ERROR = 2,
        WRONG_FILE_ERROR = 3,
        DECOMPRESS_ERROR = 4
    };

    enum class CompressErrs {
        OK = 0,
        INIT_ERROR = 10,
        DATA_ERROR = 11,
        ALLOC_ERROR = 12
    };
}