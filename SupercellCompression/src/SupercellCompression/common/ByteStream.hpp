#pragma once

#include <vector>

#include "SupercellCompression/common/Utils.h"

namespace sc
{
	class BinaryStream
	{
	public:
		virtual ~BinaryStream() {};

		/* Virtual functions */

		virtual size_t read(void* data, size_t dataSize) = 0;
		virtual size_t write(void* data, size_t dataSize) = 0;

		virtual uint32_t tell() = 0;
		virtual int set(uint32_t pos) = 0;

		virtual uint32_t size() = 0;

		virtual bool eof() = 0;
		virtual void setEof(uint32_t pos) = 0;

		virtual void close() = 0;

		/* Some common functions */

		void skip(uint32_t length)
		{
			if (length + tell() > size())
				set(size());
			else
				set(tell() + length);
		}

		/* Read/Write functions for integers */

		/* 8-bit integer */

		uint8_t readUInt8()
		{
			uint8_t data;
			size_t readRes = read(&data, sizeof(uint8_t));

			if (sizeof(uint8_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		int8_t readInt8()
		{
			int8_t data;
			size_t readRes = read(&data, sizeof(int8_t));

			if (sizeof(int8_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		void writeUInt8(uint8_t number)
		{
			write(&number, sizeof(uint8_t));
		};

		void writeInt8(int8_t number)
		{
			write(&number, sizeof(int8_t));
		};

		/* 16-bit integer */

		uint16_t readUInt16()
		{
			uint16_t data;
			size_t readRes = read(&data, sizeof(uint16_t));

			if (sizeof(uint16_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		uint16_t readUInt16BE()
		{
			uint16_t data = readUInt16();
			data = SwapEndian<uint16_t>(data);
			return data;
		};

		int16_t readInt16()
		{
			int16_t data;
			size_t readRes = read(&data, sizeof(int16_t));

			if (sizeof(int16_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		int16_t readInt16BE()
		{
			int16_t data = readInt16();
			data = SwapEndian<int16_t>(data);
			return data;
		};

		void writeUInt16(uint16_t number)
		{
			write(&number, sizeof(uint16_t));
		};

		void writeUInt16BE(uint16_t number)
		{
			writeUInt16(SwapEndian<uint16_t>(number));
		};

		void writeInt16(int16_t number)
		{
			write(&number, sizeof(int16_t));
		};

		void writeInt16BE(int16_t number)
		{
			writeInt16(SwapEndian<int16_t>(number));
		};

		/* 32-bit integer */

		uint32_t readUInt32()
		{
			uint32_t data;
			size_t readRes = read(&data, sizeof(uint32_t));

			if (sizeof(uint32_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		uint32_t readUInt32BE()
		{
			uint32_t data = readUInt32();
			data = SwapEndian<uint32_t>(data);
			return data;
		};

		int32_t readInt32()
		{
			int32_t data;
			size_t readRes = read(&data, sizeof(int32_t));

			if (sizeof(int32_t) == readRes)
			{
				return data;
			}
			else
			{
				return 0;
			}
		};

		int32_t readInt32BE()
		{
			uint32_t data = readInt32();
			data = SwapEndian<int32_t>(data);
			return data;
		};

		void writeUInt32(uint32_t number)
		{
			write(&number, sizeof(uint32_t));
		};

		void writeUInt32BE(uint32_t number)
		{
			writeUInt32(SwapEndian<uint32_t>(number));
		};

		void writeInt32(int32_t number)
		{
			write(&number, sizeof(int32_t));
		};

		void writeInt32BE(int32_t number)
		{
			writeInt32(SwapEndian<int32_t>(number));
		};

	};

	// Implementation for file binary stream
	class FileStream : public BinaryStream {
	public:
		explicit FileStream(FILE* file) : file(file) { 
			fileSize = Utils::fileSize(file);
		}

	private:
		FILE* file;
		uint32_t fileSize = 0;
		uint32_t readEofOffset = 0;

	public:

		size_t read(void* buff, size_t buffSize) override
		{
			size_t toRead = (tell() + buffSize) > size() ? size() - tell() : buffSize;
			return fread(
				buff,
				1,
				toRead,
				file
			);
		};

		size_t write(void* buff, size_t buffSize) override
		{
			size_t result = fwrite(
				buff,
				1,
				buffSize,
				file
			);
			fileSize += static_cast<uint32_t>(result);
			return result;
		};

		uint32_t tell() override
		{
			return static_cast<uint32_t>(ftell(file));
		};

		int set(uint32_t pos) override
		{
			return fseek(file, pos, SEEK_SET);
		};

		uint32_t size() override
		{
			return fileSize - readEofOffset;
		};

		bool eof() override
		{
			return size() <= tell() - readEofOffset;
		};

		void setEof(uint32_t pos) override {
			if (fileSize >= pos)
				readEofOffset = pos;
		};

		void close() override {
			fclose(file);
		};
	};

	// Implementation for buffer binary stream
	class BufferStream : public BinaryStream {
	public:
		explicit BufferStream(std::vector<uint8_t>* buffer) : buffer(buffer) { }

	private:
		std::vector<uint8_t>* buffer; // FIXME: Why is this pointer?? // because it can be easily used in the future. there is no need to create additional functions.

		size_t position = 0;
		size_t readEofOffset = 0;

	public:
		size_t read(void* data, size_t dataSize) override
		{
			if (dataSize == 0 || position >= size())
			{
				return 0;
			}

			size_t toRead = size() - position;
			if (toRead > dataSize)
			{
				toRead = dataSize;
			}

			memcpy(data, buffer->data() + position, toRead);

			position += toRead;
			return toRead;
		};

		size_t write(void* data, size_t dataSize) override
		{
			auto oldSize = buffer->size();
			buffer->resize(oldSize + dataSize);
			memcpy(&(*buffer)[oldSize], data, dataSize);

			position += dataSize;

			return dataSize;
		};

		uint32_t tell() override
		{
			return static_cast<uint32_t>(position);
		};

		int set(uint32_t pos) override
		{
			if (size() > pos)
			{
				position = pos;
				return 0;
			}
			else
			{
				return 1;
			}
		};

		uint32_t size() override
		{
			return static_cast<uint32_t>(buffer->size() - readEofOffset);
		};

		bool eof() override
		{
			return size() <= tell() - readEofOffset;
		};

		void setEof(uint32_t pos) override
		{
			readEofOffset = pos;
		};

		void close() override
		{
			buffer = nullptr;
			position = 0;
		};
	};
}