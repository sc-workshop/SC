#include "SupercellSWF/SupercellSWF.h"

namespace sc
{
    SupercellSWF::SupercellSWF()
    {

    }

    SupercellSWF::~SupercellSWF()
    {

    }

    void SupercellSWF::skip(int length)
    {
        fpos_t pos;
        fgetpos(m_file, &pos);

        pos += length;
        fsetpos(m_file, &pos);
    }

    bool SupercellSWF::readBool()
    {
        return (readUnsignedByte() > 0);
    }

    int SupercellSWF::readByte()
    {
        int result;
        fread(&result, 1, 1, m_file);
        return result;
    }

    int SupercellSWF::readUnsignedByte()
    {
        return (unsigned int)readByte();
    }

    int SupercellSWF::readShort()
    {
        int result;
        fread(&result, 2, 1, m_file);
        return result;
    }

    int SupercellSWF::readUnsignedShort()
    {
        return (unsigned int)readShort();
    }

    int SupercellSWF::readInt()
    {
        int result;
        fread(&result, 4, 1, m_file);
        return result;
    }

    std::string SupercellSWF::readAscii()
    {
        int length = readUnsignedByte();
        if (length == 0xFF)
            return;

        char* temp;
        fread(temp, sizeof(char), length, m_file);
        return temp;
    }

    float SupercellSWF::readTwip()
    {
        return (float)readInt() * 0.05f;
    }

    void SupercellSWF::load(const std::string& filePath)
    {
        bool hasExternalTexture;

        hasExternalTexture = loadInternal(filePath, false);
    }

    bool SupercellSWF::loadInternal(const std::string& filePath, bool isTexture)
    {
        m_file = fopen(filePath.c_str(), "rb");

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

            int matricesCount = readUnsignedShort();
            int colorTransformsCount = readUnsignedShort();
            initMatrixBank(matricesCount, colorTransformsCount);

            readByte();
            readInt();

            m_exportsCount = readUnsignedShort();
            m_exports = new Export[m_exportsCount];

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
        bool hasExternalTexture = false;

        int shapesLoaded = 0;
        int movieClipsLoaded = 0;
        int texturesLoaded = 0;
        int textFieldsLoaded = 0;
        int movieClipModifiersLoaded = 0;

        while (true)
        {
            int tag = readByte();
            int tagLength = readInt();

            if (tag == 0)
                break;

            switch (tag)
            {
            case 26:
                hasExternalTexture = true;
                break;

            case 2:
            case 18:
                m_shapes[shapesLoaded].load(this, tag);
                shapesLoaded++;
                break;

            case 3:
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

            case 9:

            default:
                skip(tagLength);
                break;
            }
        }

        return hasExternalTexture;
    }

    void SupercellSWF::initMatrixBank(int matricesCount, int colorTransformsCount)
    {

    }

}
