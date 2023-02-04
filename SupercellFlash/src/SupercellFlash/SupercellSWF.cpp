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
		loadAsset(filePath);

		// TODO: loading *_tex.sc files
	}

	void SupercellSWF::loadAsset(const std::string& filePath) {
		// Opening and decompressing .sc file
		std::string cachePath;

		CompressedSwfProps props;
		CompressorError decompressResult = Decompressor::decompress(filePath, cachePath, &props);
		if (decompressResult != CompressorError::OK)
		{
			throw std::runtime_error("Failed to decompress .sc file");
		}
		compression = static_cast<CompressionSignature>(props.signature);

		FILE* decompressedFile = fopen(cachePath.c_str(), "rb");
		if (decompressedFile == NULL)
		{
			throw std::runtime_error("Failed to open decompressed .sc file");
		}

		std::vector<uint8_t> fileBuffer(Utils::fileSize(decompressedFile));
		fread(fileBuffer.data(), 1, fileBuffer.size(), decompressedFile);
		fclose(decompressedFile);

		m_buffer = new BufferStream(&fileBuffer);

		m_useExternalTexture = loadInternal(false);
	}

	bool SupercellSWF::loadInternal(bool isTexture)
	{
		// Reading .sc file
		if (!isTexture)
		{
			uint16_t shapesCount = readUnsignedShort();
			shapes = std::vector<Shape>(shapesCount);

			uint16_t movieClipsCount = readUnsignedShort();
			movieClips = std::vector<MovieClip>(movieClipsCount);

			uint16_t texturesCount = readUnsignedShort();
			textures = std::vector<SWFTexture>(texturesCount);

			uint16_t textFieldsCount = readUnsignedShort();
			textFields = std::vector<TextField>(textFieldsCount);

			uint16_t matricesCount = readUnsignedShort();
			uint16_t colorTransformsCount = readUnsignedShort();
			matrixBanks = std::vector<MatrixBank>(0);
			initMatrixBank(matricesCount, colorTransformsCount);

			skip(5); // unused

			uint16_t exportsCount = readUnsignedShort();
			exports = std::vector<Export>(exportsCount);

			for (uint16_t i = 0; i < exportsCount; i++)
			{
				exports[i].id = readUnsignedShort();
			}

			for (uint16_t i = 0; i < exportsCount; i++)
			{
				exports[i].name = readAscii();
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
				textures[texturesLoaded].load(this, tag, useExternalTexture);
				texturesLoaded++;
				break;

			case TAG_MOVIE_CLIP_MODIFIERS_COUNT: {
				uint16_t movieClipModifiersCount = readUnsignedShort();
				movieClipModifiers = std::vector<MovieClipModifier>(movieClipModifiersCount);
				break;
			}

			case TAG_MOVIE_CLIP_MODIFIER:
			case TAG_MOVIE_CLIP_MODIFIER_2:
			case TAG_MOVIE_CLIP_MODIFIER_3:
				movieClipModifiers[movieClipModifiersLoaded].load(this, tag);
				movieClipModifiersLoaded++;
				break;

			case TAG_SHAPE:
			case TAG_SHAPE_2:
				shapes[shapesLoaded].load(this, tag);
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
				textFields[textFieldsLoaded].load(this, tag);
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
				matrixBanks[matrixBanksLoaded].matrices[matricesLoaded].load(this, tag);
				matricesLoaded++;
				break;

			case TAG_COLOR_TRANSFORM:
				matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].load(this);
				colorTransformsLoaded++;
				break;

			case TAG_MOVIE_CLIP:
			case TAG_MOVIE_CLIP_2:
			case TAG_MOVIE_CLIP_3:
			case TAG_MOVIE_CLIP_4:
			case TAG_MOVIE_CLIP_5:
				movieClips[movieClipsLoaded].load(this, tag);
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
		matrixBanks.push_back(bank);
	}
}