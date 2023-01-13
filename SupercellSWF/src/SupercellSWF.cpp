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

	void SupercellSWF::load(const std::string& filePath) {
		std::string cachePath;

		CompressorErrs decompressResult = sc::Decompressor::decompress(filePath, cachePath);

		if (decompressResult != CompressorErrs::OK) {
			throw std::runtime_error("Failed to decompress file");
			return;
		}

		FILE* file;
		fopen_s(&file, cachePath.c_str(), "rb");

		if (!file) {
			throw std::runtime_error("Failed to open .sc file");
			return;
		}

		ScFileStream filestream(file);

		loadInternal(&filestream, false);

		filestream.close();
	}

	bool SupercellSWF::loadInternal(IBinaryStream* stream, bool isTexture)
	{
		if (!isTexture)
		{
			m_shapesCount = stream->readUInt16();
			m_movieClipsCount = stream->readUInt16();
			m_texturesCount = stream->readUInt16();
			m_textFieldsCount = stream->readUInt16();

			uint16_t matricesCount = stream->readUInt16();
			uint16_t colorTransformsCount = stream->readUInt16();
			initMatrixBank(matricesCount, colorTransformsCount);

			stream->skip(5);

			m_exportsCount = stream->readUInt16();
			m_exports = new Export[m_exportsCount];

			for (int i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].id = stream->readUInt16();
			}

			for (int i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].name = stream->readAscii();
			}

			// Shape shape = new Shape();

			m_shapes = new Shape[m_shapesCount]();

			/*m_movieClips = new MovieClip[m_movieClipsCount];

			m_textures = new SWFTexture[m_texturesCount];
			m_textFields = new TextField[m_textFieldsCount]; */
		}

#ifdef SC_DEBUG
		printf("Asset header info:\n");
		printf("Shape count: %u\n", m_shapesCount);
		printf("MovieClip count: %u\n", m_movieClipsCount);
		printf("Texture count: %u\n", m_texturesCount);
		printf("TextField count: %u\n\n", m_textFieldsCount);

		for (uint16_t i = 0; m_exportsCount > i; i++)
			printf("[Export] Name: %s. Id: %u.\n", m_exports[i].name.c_str(), m_exports[i].id);
#endif // SC_DEBUG

		return loadTags(stream);
	}

	bool SupercellSWF::loadTags(IBinaryStream* stream)
	{
		bool hasExternalTexture = false;

		int shapesLoaded = 0;
		int movieClipsLoaded = 0;
		int texturesLoaded = 0;
		int textFieldsLoaded = 0;
		int movieClipModifiersLoaded = 0;

		while (true)
		{
			uint8_t tag = stream->readUInt8();
			int32_t tagLength = stream->readInt32();

			if (tag == 0)
				break;

			switch (tag)
			{
			case 26:
				hasExternalTexture = true;
#ifdef SC_DEBUG
				printf("[Tag] Has external texture tag.\n");
#endif // SC_DEBUG

				break;

			case 2:
			case 18:
				m_shapes[shapesLoaded].loadTag(stream, tag);
				shapesLoaded++;
				break;

				/*case 3:
				case 10:
				case 12:
				case 14:
				case 35:
					m_movieClips[movieClipsLoaded].load(this, tag);
					movieClipsLoaded++;
					break;

				case 1:
				case 16:
				case 19:
				case 24:
				case 27:
				case 28:
				case 29:
				case 34:
					m_textures[texturesLoaded].load(this, tag, hasExternalTexture);
					texturesLoaded++;
					break;

				case 7:
				case 15:
				case 20:
				case 21:
				case 25:
				case 33:
				case 43:
				case 44:
					m_textFields[textFieldsLoaded].load(this, tag);
					textFieldsLoaded++;
					break;

				case 37:
					m_movieClipModifiersCount = readUnsignedShort();
					m_movieClipModifiers = new MovieClipModifier[m_movieClipModifiersCount];
					break;

				case 38:
				case 39:
				case 40:
					m_movieClipModifiers[movieClipModifiersLoaded].load(this, tag);
					movieClipModifiersLoaded++;
					break;

				case 42:
					int matricesCount = readUnsignedShort();
					int colorTransformsCount = readUnsignedShort();
					break;

				case 8:
				case 36:

				case 9:*/

			default:
				stream->skip(tagLength);
#ifdef SC_DEBUG
				printf("[INFO] Unknown tag %u. Length: %u.\n", tag, tagLength);
#endif // SC_DEBUG
				break;
			}
		}

		return hasExternalTexture;
	}

	void SupercellSWF::initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount)
	{
	}
}