#include <string>

#include "SupercellSWF.h"

#include "common/Export.h"

#include <Bytestream.h>
#include <Decompressor.h>
#include <Utils.h>

namespace sc
{
	SupercellSWF::SupercellSWF()
	{

	}

	SupercellSWF::~SupercellSWF()
	{

	}

	void SupercellSWF::load(const std::string& filePath)
	{
		bool useExternalTexture = loadInternal(filePath, false);
	}

	bool SupercellSWF::loadInternal(const std::string& filePath, bool isTexture)
	{
		// Opening and decompressing .sc file
		std::string cachePath;

		CompressorError decompressResult = Decompressor::decompress(filePath, cachePath);
		if (decompressResult != CompressorError::OK)
		{
			throw std::runtime_error("Failed to decompress .sc file");
		}

		FILE* file;
		fopen_s(&file, cachePath.c_str(), "rb");
		if (!file)
		{
			throw std::runtime_error("Failed to open .sc file");
		}

		m_buffer = new ScFileStream(file);

		// Reading .sc file
		if (!isTexture)
		{
			m_shapesCount = readUnsignedShort();
			for (int i = 0; i < m_shapesCount; i++) m_shapes.push_back(Shape());

			m_movieClipsCount = readUnsignedShort();
			for (int i = 0; i < m_movieClipsCount; i++) m_movieClips.push_back(MovieClip());

			m_texturesCount = readUnsignedShort();
			for (int i = 0; i < m_texturesCount; i++) m_textures.push_back(SWFTexture());

			m_textFieldsCount = readUnsignedShort();
			for (int i = 0; i < m_textFieldsCount; i++) m_textFields.push_back(TextField());

			uint16_t matricesCount = readUnsignedShort();
			uint16_t colorTransformsCount = readUnsignedShort();
			initMatrixBank(matricesCount, colorTransformsCount);

			skip(5); // unused

			m_exportsCount = readUnsignedShort();
			for (int i = 0; i < m_exportsCount; i++) m_exports.push_back(Export());

			for (int i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].id = readUnsignedShort();
			}

			for (int i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].name = readAscii();
			}
		}

		return loadTags();
	}

	bool SupercellSWF::loadTags()
	{
		bool useExternalTexture = false;

		int shapesLoaded = 0;
		int movieClipsLoaded = 0;
		int texturesLoaded = 0;
		int textFieldsLoaded = 0;
		int movieClipModifiersLoaded = 0;

		while (true)
		{
			uint8_t tag = readUnsignedByte();
			int32_t tagLength = readInt();

			if (tagLength < 0)
				throw std::runtime_error("Negative tag length in .sc file");

			if (tag == 0)
				break;

			switch (tag)
			{
			case 23:
				m_useLowResTexture = true;
				break;

			case 26:
				useExternalTexture = true;
				break;

			case 30:
				m_useMultiResTexture = true;
				break;

			case 32:
				m_multiResFileSuffix = readAscii();
				m_lowResFileSuffix = readAscii();
				break;

			case 1:
			case 16:
			case 19:
			case 24:
			case 27:
			case 28:
			case 29:
			case 34:
				m_textures[texturesLoaded].load(this, tag, useExternalTexture);
				texturesLoaded++;
				break;

			case 37:
				m_movieClipModifiersCount = readUnsignedShort();
				for (int i = 0; i < m_movieClipModifiersCount; i++) m_movieClipModifiers.push_back(MovieClipModifier());
				break;

			case 38:
			case 39:
			case 40:
				movieClipModifiersLoaded++;
				break;

			case 2:
			case 18:
				shapesLoaded++;
				break;

			case 7:
			case 15:
			case 20:
			case 21:
			case 25:
			case 33:
			case 43:
			case 44:
				textFieldsLoaded++;
				break;

			case 42:
				int matricesCount = readUnsignedShort();
				int colorTransformsCount = readUnsignedShort();
				break;

			case 8:
			case 36:
				readInt();
				readInt();
				readInt();
				readInt();

				readTwip();
				readTwip();
				break;

			case 9:
				readUnsignedByte();
				readUnsignedByte();
				readUnsignedByte();

				readUnsignedByte();
				readUnsignedByte();
				readUnsignedByte();
				readUnsignedByte();
				break;

			case 3:
			case 10:
			case 12:
			case 14:
			case 35:
				movieClipsLoaded++;
				break;

			default:
				skip(tagLength);
				break;
			}
		}

		return useExternalTexture;
	}

	void SupercellSWF::initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount)
	{
	}
}