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

#define MATRIX_BANKS_MAX_COUNT 255

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

		// some funny trics
		void loadAsset(const std::string& filePath);

	// Getters for class members
	public:
		bool useExternalTexture() { return m_useExternalTexture; }

		bool useMultiResTexture() { return m_useMultiResTexture; }
		bool useLowResTexture() { return m_useLowResTexture; }

		std::string multiResFileSuffix() { return m_multiResFileSuffix; }
		std::string lowResFileSuffix() { return m_lowResFileSuffix; }

	// Setters for class members
	public:
		void setUseExternalTexture(bool status) { m_useExternalTexture = status; }

		void setUseMultiResTexture(bool status) { m_useMultiResTexture = status; }
		void SetUseLowResTexture(bool status) { m_useLowResTexture = status; }

		void setMultiResFileSuffix(std::string postfix) { m_multiResFileSuffix = postfix; }
		void setLowResFileSuffix(std::string postfix) { m_lowResFileSuffix = postfix; }
	
	// Helper functions
	public:
		// we can make the SupercellSWF class inherit the ByteStream class, but I think this solution will be better (wrapping) (yea, wrap around wrap.)
		uint8_t* read(uint32_t length)
		{
			uint8_t* result = new unsigned char[length]();
			m_buffer->read(result, length);
			return result;
		}

		void skip(uint32_t length) { m_buffer->skip(length); }

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

	private:
		bool loadInternal(bool isTexture);
		bool loadTags();

		void initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount);

	private:
		BinaryStream* m_buffer = nullptr;

		bool m_useExternalTexture = false;

		bool m_useMultiResTexture = false;
		bool m_useLowResTexture = false;

		std::string m_multiResFileSuffix = ""; // _highres
		std::string m_lowResFileSuffix = ""; // _lowres
	};
}
