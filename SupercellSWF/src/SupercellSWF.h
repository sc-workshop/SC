#ifndef SC_SWF
#define SC_SWF

#include <cstdio>
#include <string>
#include <vector>

#include <ByteStream.hpp>

#include "Export.h"
#include "tag/Shape.h"
#include "tag/MovieClip.h"
#include "tag/SWFTexture.h"
#include "tag/TextField.h"
#include "tag/MatrixBank.h"
#include "tag/MovieClipModifier.h"

namespace sc
{
	class Shape;

	class SupercellSWF
	{
	public:
		SupercellSWF();
		~SupercellSWF();

	public:
		// we can make the SupercellSWF class inherit the ByteStream class, but I think this solution will be better (wrapping)
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

	public:
		void load(const std::string& filePath);

		bool useLowResTexture() { return m_useLowResTexture; }
		void setUseLowResTexture(bool use) { m_useLowResTexture = use; }

		bool useMultiResTexture() { return m_useMultiResTexture; }
		void setUseMultiResTexture(bool use) { m_useMultiResTexture = use; }

	private:
		bool loadInternal(const std::string& filePath, bool isTexture);
		bool loadTags();

		void initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount);

	private:
		IBinaryStream* m_buffer;

		int m_shapesCount = 0;
		int m_movieClipsCount = 0;
		int m_texturesCount = 0;
		int m_textFieldsCount = 0;
		int m_movieClipModifiersCount = 0;
		int m_exportsCount = 0;

		std::vector<Shape> m_shapes;
		std::vector<MovieClip> m_movieClips;
		std::vector<SWFTexture> m_textures;
		std::vector<TextField> m_textFields;
		std::vector<MatrixBank> m_matrixBanks;
		std::vector<MovieClipModifier> m_movieClipModifiers;

		std::vector<Export> m_exports;

		bool m_useLowResTexture = false;
		bool m_useMultiResTexture = false;

		std::string m_lowResFileSuffix = "_lowres";
		std::string m_multiResFileSuffix = "_highres";
	};
}
#endif // !SC_SWF
