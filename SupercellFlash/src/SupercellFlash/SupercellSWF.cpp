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

		FILE* file = fopen(cachePath.c_str(), "rb");
		if (file == NULL)
		{
			throw std::runtime_error("Failed to open .sc file");
		}

		std::vector<uint8_t> fileBuffer(Utils::fileSize(file));
		fread(fileBuffer.data(), 1, fileBuffer.size(), file);
		fclose(file);

		m_buffer = new BufferStream(&fileBuffer);

		// Reading .sc file
		if (!isTexture)
		{
			m_shapesCount = readUnsignedShort();
			m_shapes = std::vector<Shape>(m_shapesCount);

			m_movieClipsCount = readUnsignedShort();
			m_movieClips = std::vector<MovieClip>(m_movieClipsCount);

			m_texturesCount = readUnsignedShort();
			m_textures = std::vector<SWFTexture>(m_texturesCount);

			m_textFieldsCount = readUnsignedShort();
			m_textFields = std::vector<TextField>(m_textFieldsCount);

			uint16_t matricesCount = readUnsignedShort();
			uint16_t colorTransformsCount = readUnsignedShort();
			m_matrixBanks = std::vector<MatrixBank>(0);
			initMatrixBank(matricesCount, colorTransformsCount);

			skip(5); // unused

			m_exportsCount = readUnsignedShort();
			m_exports = std::vector<Export>(m_exportsCount);

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
				m_movieClipModifiers = std::vector<MovieClipModifier>(m_movieClipModifiersCount);//new MovieClipModifier[m_movieClipModifiersCount];
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
				matricesLoaded = 0;
				colorTransformsLoaded = 0;
				matrixBanksLoaded++;
				{
				uint16_t matrixCount = readUnsignedShort();
				uint16_t colorTransformCount = readUnsignedShort();
				initMatrixBank(matrixCount, colorTransformCount);
				}
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

	void SupercellSWF::initMatrixBank(uint16_t matricesCount, uint16_t colorTransformsCount)
	{
		MatrixBank bank;
		bank.matrices = std::vector<Matrix2x3>(matricesCount);
		bank.colorTransforms = std::vector<ColorTransform>(colorTransformsCount);
		m_matrixBanks.push_back(bank);
	}
}