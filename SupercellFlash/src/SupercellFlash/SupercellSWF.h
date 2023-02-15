#pragma once

#include <cstdio>
#include <string>
#include <vector>
#include <stdexcept>

#include <SupercellCompression.h>

#include "SupercellFlash/common/Export.h"

#include "SupercellFlash/tag/Shape.h"
#include "SupercellFlash/tag/MovieClip.h"
#include "SupercellFlash/tag/SWFTexture.h"
#include "SupercellFlash/tag/TextField.h"
#include "SupercellFlash/tag/MatrixBank.h"
#include "SupercellFlash/tag/MovieClipModifier.h"

#include "SupercellFlash/common/TagMap.h"

#define MULTIRES_DEFAULT_SUFFIX "_highres"
#define LOWRES_DEFAULT_SUFFIX "_lowres"

namespace sc
{
	class SupercellSWF
	{
	public:
		SupercellSWF();
		~SupercellSWF();

		// Vectors with objects
	public:
		std::vector<SWFTexture> textures;
		std::vector<Shape> shapes;
		std::vector<MovieClip> movieClips;
		std::vector<TextField> textFields;
		std::vector<MatrixBank> matrixBanks;
		std::vector<MovieClipModifier> movieClipModifiers;
		std::vector<Export> exports;

		// Common class members
	public:
		CompressionSignature compression = CompressionSignature::NONE;

		// Class functions
	public:
		void load(const std::string& filePath);
		void loadTexture(const std::string& filePath);

		// void save(const std::string& filepath);
		void saveTexture(const std::string& filepath, bool isLowres);

		// Getters for class members
	public:
		bool useExternalTexture() { return m_useExternalTexture; }

		bool useMultiResTexture() { return m_useMultiResTexture; }
		bool useLowResTexture() { return m_useLowResTexture; }

		std::string multiResFileSuffix() { return m_multiResFileSuffix; }
		std::string lowResFileSuffix() { return m_lowResFileSuffix; }

		// Setters for class members
	public:
		void useExternalTexture(bool status) { m_useExternalTexture = status; }

		void useMultiResTexture(bool status) { m_useMultiResTexture = status; }
		void useLowResTexture(bool status) { m_useLowResTexture = status; }

		void multiResFileSuffix(std::string postfix) { m_multiResFileSuffix = postfix; }
		void lowResFileSuffix(std::string postfix) { m_lowResFileSuffix = postfix; }

		// Helper functions
	public:
		// we can make the SupercellSWF class inherit the ByteStream class, but I think this solution will be better (wrapping) (yea, wrap around wrap.)
		/* Write functions  */

		void skip(uint32_t length) { m_buffer->skip(length); }

		void read(void* data, uint32_t size)
		{
			m_buffer->read(data, size);
		}

		int8_t readByte() { return m_buffer->readInt8(); }
		uint8_t readUnsignedByte() { return m_buffer->readUInt8(); }

		int16_t readShort() { return m_buffer->readInt16(); }
		uint16_t readUnsignedShort() { return m_buffer->readUInt16(); }

		int32_t readInt() { return m_buffer->readInt32(); }

		bool readBool() { return (readUnsignedByte() > 0); }

		std::string readAscii()
		{
			uint8_t length = readUnsignedByte();
			if (length == 0xFF)
				return {};

			char* str = new char[length]();
			m_buffer->read(str, length);

			return std::string(str, length);
		}

		float readTwip() { return (float)readInt() * 0.05f; }

		/* Write function */

		void writeTag(uint8_t tag) {
			writeUnsignedByte(tag);
			writeInt(0);
		}

		void writeTag(uint8_t tag, std::vector<uint8_t> buffer) {
			int32_t tagSize = static_cast<int32_t>(buffer.size());
			if (tagSize > 0) {
				writeUnsignedByte(tag);
				writeInt(tagSize);
				write(buffer.data(), static_cast<uint32_t>(tagSize));
			}
		}

		void write(void* data, uint32_t size) {
			m_buffer->write(data, size);
		}

		void writeByte(int8_t integer) {
			m_buffer->writeInt8(integer);
		}
		void writeUnsignedByte(uint8_t integer) {
			m_buffer->writeUInt8(integer);
		}

		void writeShort(int16_t integer) {
			m_buffer->writeInt16(integer);
		}
		void writeUnsignedShort(uint16_t integer) {
			m_buffer->writeUInt16(integer);
		}

		void writeInt(int32_t integer) {
			m_buffer->writeInt32(integer);
		}

		void writeBool(bool status) {
			m_buffer->writeUInt8(status ? 1 : 0);
		}

		void writeAscii(std::string ascii) {
			uint8_t size = static_cast<uint8_t>(ascii.size());

			writeUnsignedByte(size);
			if (size > 0) {
				m_buffer->write(ascii.data(), size);
			}
		}

		void writeTwip(float twip) {
			writeInt((int)(twip / 0.05f));
		}

	private:
		bool loadTags();
		bool loadInternal(bool isTexture);

		void openFile(const std::string& filePath, std::vector<uint8_t>* buffer, CompressionSignature* signature);
		void writeFile(const std::string& filePath, std::vector<uint8_t>* buffer);

		void initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount);

	private:
		BinaryStream* m_buffer = nullptr;

		bool m_useExternalTexture = false;

		bool m_useMultiResTexture = false;
		bool m_useLowResTexture = false;

		std::string m_multiResFileSuffix = MULTIRES_DEFAULT_SUFFIX;
		std::string m_lowResFileSuffix = LOWRES_DEFAULT_SUFFIX;
	};
}
