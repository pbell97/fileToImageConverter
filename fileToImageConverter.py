from PIL import Image
import os
from pathlib import Path

# TODO: Make this streaming/iterator?
# TODO: Look into garbage collection/memory management


def getBytesArray(path):
    bytesArray = []
    with open(path, 'rb') as f:
        byte = f.read(1)
        while byte:
            bytesArray.append(byte)
            byte = f.read(1)
    return bytesArray


def convertBytesToEightBitInts(bytesArray):
    intsArray = [ord(byte) for byte in bytesArray]
    return intsArray


class BytesPixel:
    def __init__(self):
        self.intValues = ()
        None

    def LoadPixelFromBytes(self):
        None

    def LoadPixelFromRGB(self, pixel):
        self.intValues = pixel
        None

    def LoadPixelFromInts(self, intsArray):
        if len(intsArray) > 3:
            raise Exception("ERROR: Pixel cannot have more than 3 values")
        itsArray = intsArray + (3-len(intsArray))*[0]
        self.intValues = tuple(itsArray)

    def GetPixelRGB(self):
        return self.intValues

    def GetBytes(self):
        None


class ImageConverter:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def CanFileFitInImage(self, path):
        fileSizeInBytes = os.path.getsize(path)
        maxFileSizeForImage = self.width*self.height*3 - 111
        return fileSizeInBytes <= maxFileSizeForImage

    # Creates the header, returns list of ints which are the bytes
    def CreateInputFileMetadataInInts(self, path):
        # 9 bytes (3 pixels) reserved for # of bytes to read -> Allows for up to 8k image size w/ 1 digit to spare
        # 102 bytes (34 pixels) reserved for filename
        # Total reserved = 111 bytes == 37 pixels

        # TODO: Check if file exists and print error if so
        fileSize = os.path.getsize(path)
        fileSizeInBytes = [i for i in str.encode(str(fileSize))]
        fileSizeInBytes = (9 - len(fileSizeInBytes))*[0] + fileSizeInBytes

        filename = os.path.basename(path)
        filenameInBytes = [i for i in str.encode(filename)]
        filenameInBytes = (102 - len(filenameInBytes))*[0] + filenameInBytes
        headerMetadata = fileSizeInBytes + filenameInBytes
        return headerMetadata

    def ExtractInputFileMetadata(self, subIntsArray):
        # 9 bytes (3 pixels) reserved for # of bytes to read -> Allows for up to 8k image size w/ 1 digit to spare
        # 102 bytes (34 pixels) reserved for filename
        # Total reserved = 111 bytes == 37 pixels
        numOfBytes = subIntsArray[:9]
        filename = subIntsArray[9:111]
        while True:
            if numOfBytes[0] == 0:
                del numOfBytes[0]
            else:
                break

        while True:
            if filename[0] == 0:
                del filename[0]
            else:
                break

        numOfBytes = b''.join([i.to_bytes(1, 'big') for i in numOfBytes])
        filename = b''.join([i.to_bytes(1, 'big') for i in filename])
        print("NUM OF BYTES: " + str(numOfBytes))
        print("FILENAME: " + str(filename))
        return int(numOfBytes), filename.decode('ascii')

    def SaveImage(self):
        None

    def LoadExistingImage(self, path):
        None

    def ConvertFileToImage(self, filePath, imagePath):
        # Check if it can fit within given image size
        if (not self.CanFileFitInImage(filePath)):
            raise Exception("ERROR: Filesize too large")

        # Create header metadata
        headerMetadataArray = self.CreateInputFileMetadataInInts(filePath)

        # Convert to bytes
        bytesArray = getBytesArray(filePath)

        # Convert to ints
        intArray = convertBytesToEightBitInts(bytesArray)

        # Header plus file data
        allIntsArray = headerMetadataArray + intArray

        # Create list of pixels
        pixelLists = []
        for i in range(0, len(allIntsArray), 3):
            newPixel = BytesPixel()
            values = []
            for j in range(3):
                if i+j < len(allIntsArray):
                    values.append(allIntsArray[i+j])
            newPixel.LoadPixelFromInts(values)
            pixelLists.append(newPixel.GetPixelRGB())

        # Save pixels to new image
        img = Image.new('RGB', (self.width, self.height))
        imgPixels = img.load()
        widthCounter = 0
        heightCounter = 0
        for pixel in pixelLists:
            if heightCounter == self.height:
                raise Exception(
                    "Tried to save pixel outside of image boundary")

            imgPixels[widthCounter, heightCounter] = pixel
            widthCounter += 1
            if widthCounter == self.width:
                widthCounter = 0
                heightCounter += 1

        # Save image to path
        img.save(imagePath)

    def ConvertImageToFile(self, imagePath, saveDirectory):
        # Extract all pixels that aren't metadata
        img = Image.open(imagePath)

        # TODO: Extract just metadata pixels first
        intsArray = self.ConvertImageToIntsArray(img)

        # Extract header metadata
        numOfBytes, filename = self.ExtractInputFileMetadata(intsArray)

        # Convert pixels to ints then to bytes
        finalFilePath = os.path.join(saveDirectory, filename)
        with open(finalFilePath, 'wb') as f:
            for i in range(111, 111+numOfBytes):
                f.write(intsArray[i].to_bytes(1, 'big'))

        print("Saved to : " + finalFilePath)

        # Reconstruct file

        # Save file
        None

    def ConvertImageToIntsArray(self, image):
        imgPixels = image.load()
        intsArray = []
        widthCounter = 0
        heightCounter = 0
        for i in range(0, self.width*self.height):
            if heightCounter == self.height:
                raise Exception(
                    "Tried to load pixel outside of image boundary")

            intsArray += imgPixels[widthCounter, heightCounter]
            widthCounter += 1
            if widthCounter == self.width:
                widthCounter = 0
                heightCounter += 1
        return intsArray


path = "/Users/patrickbell/Downloads/Universal's Endless Summer Resort - Dockside Inn and Suites.pdf"
savedFilePath = "/Users/patrickbell/Downloads/convertedImage.png"
IC = ImageConverter(1920, 1080)
IC.ConvertFileToImage(path, savedFilePath)
IC.ConvertImageToFile(savedFilePath, "/Users/patrickbell/Downloads/")
