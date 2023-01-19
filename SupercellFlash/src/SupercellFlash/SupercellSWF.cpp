#include "SupercellSWF.h"

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
				m_movieClipModifiers = new MovieClipModifier[m_movieClipModifiersCount];
				break;

			case 38:
			case 39:
			case 40:
				m_movieClipModifiers[movieClipModifiersLoaded].load(this, tag);
				movieClipModifiersLoaded++;
				break;

			case 2:
			case 18:
				m_shapes[shapesLoaded].load(this, tag);
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
				skip(tagLength); // TODO: TextField's loading
				textFieldsLoaded++;
				break;

			case 42:
				initMatrixBank(readUnsignedShort(), readUnsignedShort(), matrixBanksLoaded);

				matricesLoaded = 0;
				colorTransformsLoaded = 0;

				matrixBanksLoaded++;
				break;

			case 8:
			case 36:
				m_matrixBanks[matrixBanksLoaded].matrices[matricesLoaded].load(this, tag);
				matricesLoaded++;
				break;

			case 9:
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].redAdd = readUnsignedByte();
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].greenAdd = readUnsignedByte();
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].blueAdd = readUnsignedByte();

				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].alphaMul = (float)readUnsignedByte() / 255.0f;
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].redMul = (float)readUnsignedByte() / 255.0f;
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].greenMul = (float)readUnsignedByte() / 255.0f;
				m_matrixBanks[matrixBanksLoaded].colorTransforms[colorTransformsLoaded].blueMul = (float)readUnsignedByte() / 255.0f;

				colorTransformsLoaded++;
				break;

			case 3:
			case 10:
			case 12:
			case 14:
			case 35:
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