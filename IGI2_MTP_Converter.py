import os,struct,sys,time
try:
    def ReadSettings():
        settings = []
        if os.path.exists("mtpconvertersettings.bin"):
            with open("mtpconvertersettings.bin","rb") as f:
                f_read = f.read()
            if len(f_read) == 0:
                return [False,False]
            for i in range(2):
                if f_read[i] == 0:
                    settings.append(False)
                else:
                    settings.append(True)
        else:
            settings.extend([False,False])
        return settings
    def BANM():
        animations.extend(getStrings(4,struct.unpack("I",Header_data[:4])[0]))
    def SNDS():
        sounds.extend(getStrings(4,struct.unpack("I",Header_data[:4])[0]))
    def SVOL():
        shadowVolumes.extend(getStrings(4,struct.unpack("I",Header_data[:4])[0]))
    def MODS():
        models.extend(getStrings(4,struct.unpack("I",Header_data[:4])[0]))
    def VNAM():
        chunkLength = struct.unpack("I",Header_data[:4])[0]
        for i in range(chunkLength):
            chunks.append(struct.unpack("I",Header_data[4+i*4:8+i*4])[0])
        VNAM_list.extend(getStrings(4+chunkLength*4,chunkLength))
    def INST():
        offset = 0
        i = 0
        while offset < Header_len:
            INST_list.append([-1,[]])
            INST_list[i][0] = struct.unpack("I",Header_data[offset:offset+4])[0]
            model_tex_count = struct.unpack("I",Header_data[offset+4:offset+8])[0]
            offset += 8
            for n in range(model_tex_count):
                INST_list[i][1].append(struct.unpack("I",Header_data[offset:offset+4])[0])
                offset += 4
            i += 1
    def TEXF():
        textures.extend(getStrings(4,struct.unpack("I",Header_data[:4])[0]))
    def getStrings(start,stringCount):
        strings = []
        for i in range(stringCount):
            strings.append(Header_data[start:Header_data.index(b'\x00',start)].decode())
            start = Header_data.index(b'\x00',start)+1
        return strings
    def getUsableModelCount():
        x = 0
        for model in VNAM_list:
            if model in models:
                x += 1
        return x
    def Decode(filename):
        VNAM_indexes = []
        if replaceName == True:
            filename = "{} decoded".format(filename)
        with open("{}.dat".format(filename),"w") as export:
            export.write("*** This file is machine generated\n*** DO NOT EDIT!\n\n")
            #Models
            export.write("// Models\n{}\n".format(getUsableModelCount()))
            for index, link in enumerate(INST_list):
                if VNAM_list[index] in models:
                    export.write("{}\n".format(models[link[0]]))
                    export.write("{}\n".format(len(link[1])))
                    for textureIndex in link[1]:
                        export.write("{}\n".format(textures[textureIndex]))
                else:
                    VNAM_indexes.append(index)
            #Textures
            export.write("\n//Textures\n{}\n".format(len(textures)))
            for textureName in textures:
                export.write("{}\n".format(textureName))
            #VNAM Models
            export.write("\n//VNAM\n{}\n".format(len(VNAM_indexes)))
            for INST_index in VNAM_indexes:
                export.write("{}\n".format(models[INST_list[INST_index][0]]))
                export.write("{}\n".format(VNAM_list[INST_index]))
                export.write("{}\n".format(len(INST_list[INST_index][1])))
                for textureIndex in INST_list[INST_index][1]:
                    export.write("{}\n".format(textures[textureIndex]))
            #Bone Animations
            export.write("\n//Bone Animations\n{}\n".format(len(animations)))
            for anim in animations:
                export.write("{}\n".format(anim))
            #Shadow models
            export.write("\n//Shadow Models\n{}\n".format(len(shadowVolumes)))
            for shadowModel in shadowVolumes:
                export.write("{}\n".format(shadowModel))
    def ReadDAT(fileData):
        lineIndex = 0
        isSection = False
        sectionIndex = -1
        sectionItems2Read = -1
        while lineIndex < len(fileData):
            if not isSection and fileData[lineIndex].replace("\n","").isdigit():
                isSection = True
                sectionIndex += 1
                sectionItems2Read = int(fileData[lineIndex])
                lineIndex += 1
            elif isSection and sectionIndex == 0: #Model section
                for i in range(sectionItems2Read):
                    models.append(fileData[lineIndex].replace("\n",""))
                    INST_models.append(fileData[lineIndex].replace("\n",""))
                    INST_list.append([i,[]])
                    textureCount = int(fileData[lineIndex+1])
                    for textureIndex in range(textureCount):
                        curTexture = fileData[lineIndex+2+textureIndex].replace("\n","")
                        if curTexture not in textures:
                            textures.append(curTexture)
                        INST_list[i][1].append(textures.index(curTexture))
                    lineIndex += 2+textureCount
                isSection = False
            elif isSection and sectionIndex == 1: #Texture section
                for i in range(sectionItems2Read):
                    lineIndex += 1
                isSection = False
            elif isSection and sectionIndex == 2: #VNAM section
                for i in range(sectionItems2Read):
                    mainModelName = fileData[lineIndex].replace("\n","")
                    virModelName = fileData[lineIndex+1].replace("\n","")
                    VNAM_list.append(virModelName)
                    if mainModelName not in models:
                        models.append(mainModelName)
                    INST_list.append([models.index(mainModelName),[]])
                    textureCount = int(fileData[lineIndex+2])
                    for textureIndex in range(textureCount):
                        curTexture = fileData[lineIndex+3+textureIndex].replace("\n","")
                        if curTexture not in textures:
                            textures.append(curTexture)
                        INST_list[-1][1].append(textures.index(curTexture))
                    lineIndex += 3+textureCount
                isSection = False
            elif isSection and sectionIndex == 3: #Bone animations section
                for i in range(sectionItems2Read):
                    animations.append(fileData[lineIndex].replace("\n",""))
                    lineIndex += 1
                isSection = False
            elif isSection and sectionIndex == 4: #Shadow models section
                for i in range(sectionItems2Read):
                    shadowVolumes.append(fileData[lineIndex].replace("\n",""))
                    lineIndex += 1
                isSection = False
            else:
                lineIndex += 1
    def getTotalStringSectionLength(varList):
        length = 0
        for item in varList:
            length += len(item)
        if length == 0:
            return 0
        else:
            return length+len(varList)
    def getPaddingLength(size):
        if size == 0 or size % 4 == 0:
            return 0
        else:
            return 4 - (size % 4)
    def Compile(filename):
        sectionLengths = []
        if replaceName == True:
            filename = "{} compiled".format(filename)
        with open("{}.mtp".format(filename),"wb") as f:
            f.write(b'\x00'*12)
            #Write animation header
            animationStringsLength = getTotalStringSectionLength(animations)
            f.write(b'BANM')
            f.write(struct.pack(">I",4+animationStringsLength+getPaddingLength(animationStringsLength))) #Write header length
            f.write(struct.pack("I",len(animations))) #Write animation filecount
            for anim in animations:
                f.write(anim.encode() + b'\x00')
            f.write(b'\x00' * getPaddingLength(animationStringsLength))
            sectionLengths.append(12+animationStringsLength)

            #Write sounds header
            soundStringsLength = getTotalStringSectionLength(sounds)
            f.write(b'SNDS')
            f.write(struct.pack(">I",4+soundStringsLength+getPaddingLength(soundStringsLength))) #Write header length
            f.write(struct.pack("I",len(sounds))) #Write sound filecount
            for sound in sounds:
                f.write(sound.encode()+b'\x00')
            f.write(b'\x00' * getPaddingLength(soundStringsLength))
            sectionLengths.append(12+soundStringsLength)

            #Write ShadowVolume header
            shadowVolumeStringsLength = getTotalStringSectionLength(shadowVolumes)
            f.write(b'SVOL')
            f.write(struct.pack(">I",4+shadowVolumeStringsLength+getPaddingLength(shadowVolumeStringsLength))) #Write header length
            f.write(struct.pack("I",len(shadowVolumes))) #Write shadowmodel filecount
            for shadowModel in shadowVolumes:
                f.write(shadowModel.encode() + b'\x00')
            f.write(b'\x00' * getPaddingLength(shadowVolumeStringsLength))
            sectionLengths.append(12+shadowVolumeStringsLength)

            #Write Models header
            modelStringsLength = getTotalStringSectionLength(models)
            f.write(b'MODS')
            f.write(struct.pack(">I",4+modelStringsLength+getPaddingLength(modelStringsLength))) #Write header length
            f.write(struct.pack("I",len(models))) #Write model filecount
            for model in models:
                f.write(model.encode() + b'\x00')
            f.write(b'\x00' * getPaddingLength(modelStringsLength))
            sectionLengths.append(12+modelStringsLength+getPaddingLength(modelStringsLength))

            #Write VNAM header
            VNAMStringsLength = getTotalStringSectionLength(INST_models+VNAM_list)
            f.write(b'VNAM')
            f.write(struct.pack(">I",4+4*(len(INST_models)+len(VNAM_list))+VNAMStringsLength+getPaddingLength(VNAMStringsLength))) #Write header length
            f.write(struct.pack("I",len(INST_models)+len(VNAM_list))) #Write chunkcount
            f.write(b'\x00\x00\x00\x00'*(len(INST_models)+len(VNAM_list))) #Chunks are filled with zeros because we are unsure about their behaviour.
            for modelName in (INST_models+VNAM_list):
                f.write(modelName.encode()+b'\x00')
            f.write(b'\x00' * getPaddingLength(VNAMStringsLength))
            sectionLengths.append(12+VNAMStringsLength+4*(len(INST_models)+len(VNAM_list))+getPaddingLength(VNAMStringsLength))

            #Write INST header
            f.write(b'INST')
            INST_size = 0
            for i in range(len(INST_list)):
                INST_size += (8+len(INST_list[i][1])*4)
            f.write(struct.pack(">I",INST_size)) #Write header length
            for item in INST_list:
                f.write(struct.pack("I",item[0])) #Write model index
                f.write(struct.pack("I",len(item[1]))) #Write texture count of model
                for textureIndex in item[1]:
                    f.write(struct.pack("I",textureIndex)) #Write texture index
            sectionLengths.append(8+INST_size)

            #Write Textures header
            textureStringsLength = getTotalStringSectionLength(textures)
            f.write(b'TEXF')
            f.write(struct.pack(">I",4+textureStringsLength+getPaddingLength(textureStringsLength))) #Write header length
            f.write(struct.pack("I",len(textures))) #Write texture filecount
            for texture in textures:
                f.write(texture.encode() + b'\x00')
            f.write(b'\x00' * getPaddingLength(textureStringsLength))
            sectionLengths.append(12+textureStringsLength+getPaddingLength(textureStringsLength))

            #Write Palette header (Unused)
            f.write(b'PALF\x00\x00\x00\x04\x00\x00\x00\x00')
            sectionLengths.append(12)

            #Write GTT header
            f.write(b'GTT ')
            f.write(struct.pack(">I",len(textures)*8+4)) #Write header length
            f.write(struct.pack("I",len(textures))) #Write texture filecount
            for i in range(len(textures)):
                f.write(struct.pack("I",i) + b'\xFF\xFF\xFF\xFF')
            sectionLengths.append(12+len(textures)*8)

            #Write main FORM header
            f.seek(0)
            f.write(b'FORM')
            totalLength = 4
            for sectionLength in sectionLengths:
                totalLength += sectionLength
            f.write(struct.pack(">I",totalLength))
            f.write(b'MTP ')
    settings = ReadSettings()
    replaceName = settings[0]
    autoClose = settings[1]
    animations = []
    sounds = []
    shadowVolumes = []
    models = []
    VNAM_list = []
    INST_list = []
    INST_models = [] #Models that associated with textures instead of definition only
    textures = []
    chunks = []
    args = sys.argv[1:]
    settingTexts = ["Change filename after process?","Auto close program after process?"]
    if len(args) == 0: #If no argument is provided ask user for command selection
        fileList = os.listdir()
        os.system("color 0A")
        while True:
            print("IGI2 MTP Converter V.1.0\nFeritCoderTR, 2024.\n------------------------\n<Current Settings>\nReplace Filename: {} | Auto Close Program: {}\n".format(replaceName,autoClose))
            commandType = input("Please select the command type.\nC - Compile .dat files\nD - Decode .mtp files\nE - Exit program\nS - Settings\n")
            if commandType.lower() == "c":
                filesToRead = [i for i in fileList if i[-4:] == ".dat"]
                break
            elif commandType.lower() == "d":
                filesToRead = [i for i in fileList if i[-4:] == ".mtp"]
                break
            elif commandType.lower() == "e":
                exit()
            elif commandType.lower() == "s":
                option = ""
                settingIndex = 0
                with open("mtpconvertersettings.bin","wb") as f:
                    while settingIndex < 2:
                        option = input("{}\nY - Yes\nN - No\n".format(settingTexts[settingIndex]))
                        if option.lower() != "y" and option.lower() != "n":
                            print("Invalid selection!")
                        else:
                            if option.lower() == "y":
                                f.write(b'\xFF')
                            else:
                                f.write(b'\x00')
                            f.flush()
                            settingIndex += 1
                    print("Setting saved!")
                    settings = ReadSettings()
                    replaceName = settings[0]
                    autoClose = settings[1]
            else:
                print("Invalid conversion type.")
                time.sleep(1)
                exit()
            os.system("cls")
    else:
        print("IGI2 MTP Converter V.1.0\nFeritCoderTR, 2024.\n------------------------")
        filesToRead = [arg for arg in args]
    for file in filesToRead:
        if file[-4:] == ".dat":
            with open(file,"r") as f:
                ReadDAT(f.readlines())
            Compile(file[:-4])
            print("Compiled file {}".format(os.path.basename(file)))
        elif file[-4:] == ".mtp":
            with open(file,"rb") as f:
                f_read = f.read()
            #First 4 bytes are FORM which is .mtp header
            if f_read[:4] != b'FORM':
                print("Error: File {} is not innerloop .mtp file format.".format(os.path.basename(file)))
                continue
            fileLength = struct.unpack(">I",f_read[4:8])[0]
            offset = 12
            while True:
                Header = f_read[offset:offset+4]
                Header_len = struct.unpack(">I",f_read[offset+4:offset+8])[0]
                Header_data = f_read[offset+8:offset+8+Header_len]
                offset += 8+Header_len
                if Header == b'BANM':
                    BANM()
                elif Header == b'SNDS':
                    SNDS()
                elif Header == b'SVOL':
                    SVOL()
                elif Header == b'MODS':
                    MODS()
                elif Header == b'VNAM':
                    VNAM()
                elif Header == b'INST':
                    INST()
                elif Header == b'TEXF':
                    TEXF()
                if offset >= fileLength:
                    break
            Decode(file[:-4])
            print("Decoded file {}".format(os.path.basename(file)))
        else:
            print("Invalid file to process.")
            time.sleep(1)
            exit()
        animations.clear(),sounds.clear(),shadowVolumes.clear(),models.clear(),VNAM_list.clear(),INST_models.clear(),INST_list.clear(),textures.clear()
        chunks.clear()
    print("Done!\n------------------------")
    if autoClose == False:
        input("Press enter to close the program...")
except Exception:
    print("ERROR: Unknown error happened in program code! Program is going to close now.")
    time.sleep(3)
    exit()