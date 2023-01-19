#include "SupercellFlash/SupercellSWF.h"

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

		// TODO: loading *_tex.sc files
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

		m_buffer = new FileStream(file);

		// Reading .sc file
		if (!isTexture)
		{
			m_shapesCount = readUnsignedShort();
			m_shapes = new Shape[m_shapesCount];

			m_movieClipsCount = readUnsignedShort();
			m_movieClips = new MovieClip[m_movieClipsCount];

			m_texturesCount = readUnsignedShort();
			m_textures = new SWFTexture[m_texturesCount];

			m_textFieldsCount = readUnsignedShort();
			m_textFields = new TextField[m_textFieldsCount];

			// TODO: rework it, maybe return to std::vector's
			m_matrixBanks = new MatrixBank[255];

			uint16_t matricesCount = readUnsignedShort();
			uint16_t colorTransformsCount = readUnsignedShort();
			initMatrixBank(matricesCount, colorTransformsCount, 0);

			skip(5); // unused

			m_exportsCount = readUnsignedShort();
			m_exports = new Export[m_exportsCount];

			for (uint16_t i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].id = readUnsignedShort();
			}

			for (uint16_t i = 0; i < m_exportsCount; i++)
			{
				m_exports[i].name = readAscii();
			}
		}

		return loadTags();
	}

	bool SupercellSWF::loadTags()
	{
		bool useExternalTexture = false;

		uint16_t shapesLoaded = 0;
		uint16_t movieClipsLoaded = 0;
		uint16_t texturesLoaded = 0;
		uint16_t textFieldsLoaded = 0;
		uint8_t matrixBanksLoaded = 0;
		uint16_t matricesLoaded = 0;
		uint16_t colorTransformsLoaded = 0;
		uint16_t movieClipModifiersLoaded = 0;

		while (true)
		{
			uint8_t tag = readUnsignedByte();
			int32_t tagLength = readInt();

			if (tagLength < 0)
				throw std::runtime_error("Negative tag length in .sc file");

			if (tag == TAG_END)
				break;

			switch (tag)
			{
			case TAG_USE_LOW_RES_TEXTURE:
				m_useLowResTexture = true;
				break;

			case TAG_USE_EXTERNAL_TEXTURE:
				useExternalTexture = true;
				break;

			case TAG_USE_MULTI_RES_TEXTURE:
				m_useMultiResTexture = true;
				break;

			case TAG_TEXTURE_FILE_SUFFIXES:
				m_multiResFileSuffix = readAscii();
				m_lowResFileSuffix = readAscii();
				break;

			case TAG_TEXTURE:
			case TAG_TEXTURE_2:
			case TAG_TEXTURE_3:
			case TAG_TEXTURE_4:
			case TAG_TEXTURE_5:
			case TAG_TEXTURE_6:
			case TAG_TEXTURE_7:
			case TAG_TEXTURE_8:
				m_textures[texturesLoaded].load(this, tag, useExternalTexture);
				texturesLoaded++;
				break;

			case TAG_MOVIE_CLIP_MODIFIERS_COUNT:
				m_movieClipModifiersCount = readUnsignedShort();
				m_movieClipModifiers = new MovieClipModifier[m_movieClipModifiersCount];
				break;

			case TAG_MOVIE_CLIP_MODIFIER:
			case TAG_MOVIE_CLIP_MODIFIER_2:
			case TAG_MOVIE_CLIP_MODIFIER_3:
				m_movieClipModifiers[movieClipModifiersLoaded].load(this, tag);
				movieClipModifiersLoaded++;
				break;

			case TAG_SHAPE:
			case TAG_SHAPE_2:
				m_shapes[shapesLoaded].load(this, tag);
				shapesLoaded++;
				break;

			case TAG_TEXT_FIELD:
			case TAG_TEXT_FIELD_2:
			case TAG_TEXT_FIELD_3:
			case TAG_TEXT_FIELD_4:
			case TAG_TEXT_FIELD_5:
			case TAG_TEXT_FIELD_6:
			case TAG_TEXT_FIELD_7:
			case TAG_TEXT_FIELD_8:
				m_textFields[textFieldsLoaded].load(this, tag);
				textFieldsLoaded++;
				break;

			case TAG_MATRIX_BANK:
				initMatrixBank(readUnsignedShort(), readUnsignedShort(), matrixBanksLoaded);

				matricesLoaded = 0;
				colorTransformsLoaded = 0;

				matrixBanksLoaded++;
				break;

			case TAG_MATRIX_2x3:
			case TAG_MATRIX_2x3_2:
				m_matrixBanks[matrixBanksLoaded].matrices[matricesLoaded].load(this, tag);
				matricesLoaded++;
				break;

			case TAG_COLOR_TRANSFORM:
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].load(this);
				colorTransformsLoaded++;
				break;

			case TAG_MOVIE_CLIP:
			case TAG_MOVIE_CLIP_2:
			case TAG_MOVIE_CLIP_3:
			case TAG_MOVIE_CLIP_4:
			case TAG_MOVIE_CLIP_5:
				m_movieClips[movieClipsLoaded].load(this, tag);
				movieClipsLoaded++;
				break;

			default:
				skip(tagLength);
				break;
			}
		}

		return useExternalTexture;
	}

	void SupercellSWF::initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount, uint8_t matrixBanksLoaded)
	{
		m_matrixBanks[matrixBanksLoaded].matrices = new Matrix2x3[matricesCount];
		m_matrixBanks[matrixBanksLoaded].colorTransforms = new ColorTransform[colorTransformsCount];;
	}
}