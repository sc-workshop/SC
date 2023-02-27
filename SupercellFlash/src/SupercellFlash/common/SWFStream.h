#pragma once

#include <SupercellCompression.h>
#include <stdexcept>
#include <cstdarg>

namespace sc {
	class SupercellSWF;

	class SWFStream {
		std::vector<uint8_t> m_buffer;
		BufferStream m_stream = BufferStream(&m_buffer);

	public:
		SWFStream() {}
		~SWFStream() {}

		std::vector<uint8_t>* buffer() {
			return &m_buffer;
		}

		BufferStream* stream() {
			return &m_stream;
		}

		void set(uint32_t pos) {
			m_stream.set(pos);
		}

		uint32_t tell() {
			return m_stream.tell();
		}

		void newBuffer() {
			newBuffer(0);
		}

		void newBuffer(size_t size) {
			m_buffer = std::vector<uint8_t>(size);
			m_stream.set(0);
		}

		void close() {
			newBuffer();
		}

		void skip(uint32_t size) {
			m_stream.set(m_stream.tell() + size);
		}

		/* Read */

		void read(void* data, size_t size) {
			m_stream.read(data, size);
		}

		int8_t readByte() { return m_stream.readInt8(); }
		uint8_t readUnsignedByte() { return m_stream.readUInt8(); }

		int16_t readShort() { return m_stream.readInt16(); }
		uint16_t readUnsignedShort() { return m_stream.readUInt16(); }

		int32_t readInt() { return m_stream.readInt32(); }

		bool readBool() { return (readUnsignedByte() > 0); }

		std::string readAscii()
		{
			uint8_t length = readUnsignedByte();
			if (length == 0xFF)
				return {};

			char* str = new char[length]();
			m_stream.read(str, length);

			return std::string(str, length);
		}

		float readTwip() { return (float)readInt() * 0.05f; }

		/* Write */

		void write(void* data, size_t size) {
			m_stream.write(data, size);
		}

		void writeTag(uint8_t tag) {
			writeUnsignedByte(tag);
			writeInt(0);
		}

		void writeTag(uint8_t tag, SWFStream* stream) {
			writeTag(tag, stream->buffer());
		}

		// More classic and slow way
		void writeTag(uint8_t tag, std::vector<uint8_t>* buffer) {
			int32_t tagSize = static_cast<int32_t>(buffer->size());

			if (tagSize > 0) {
				writeUnsignedByte(tag);
				writeInt(tagSize);
				write(buffer->data(), static_cast<uint32_t>(tagSize));
			}
		}

		void write(void* data, uint32_t size) {
			m_stream.write(data, size);
		}

		void writeByte(int8_t integer) {
			m_stream.writeInt8(integer);
		}
		void writeUnsignedByte(uint8_t integer) {
			m_stream.writeUInt8(integer);
		}

		void writeShort(int16_t integer) {
			m_stream.writeInt16(integer);
		}
		void writeUnsignedShort(uint16_t integer) {
			m_stream.writeUInt16(integer);
		}

		void writeInt(int32_t integer) {
			m_stream.writeInt32(integer);
		}

		void writeBool(bool status) {
			m_stream.writeUInt8(status ? 1 : 0);
		}

		void writeAscii(std::string ascii) {
			uint8_t size = static_cast<uint8_t>(ascii.size());

			writeUnsignedByte(size);
			if (size > 0) {
				m_stream.write(ascii.data(), size);
			}
		}

		void writeTwip(float twip) {
			writeInt((int)(twip / 0.05f));
		}

		void writeTag(uint8_t tag, int32_t size) {
			uint32_t target = static_cast<uint32_t>(m_stream.tell() - size);
			memcpy(m_buffer.data() + target, &tag, sizeof(tag));
			memcpy(m_buffer.data() + (target + sizeof(tag)), &size, sizeof(size));
		}

		uint32_t initTag() {
			uint32_t res = tell();
			writeUnsignedByte(0xFF);
			writeInt(-1);

			return res;
		}

		void finalizeTag(uint8_t tag, uint32_t position) {
			int32_t tagSize = static_cast<int32_t>(tell() - position - (sizeof(tag) + sizeof(position)));

			memcpy(buffer()->data() + position, &tag, sizeof(tag));
			memcpy(buffer()->data() + (position + sizeof(tag)), &tagSize, sizeof(tagSize));
		}
	};
}