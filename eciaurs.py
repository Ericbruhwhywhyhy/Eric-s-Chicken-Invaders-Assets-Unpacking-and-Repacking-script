import struct
import os
import sys
import zlib
import urllib.request
import ast

print('Fetching table from https://gist.githubusercontent.com/Ericbruhwhywhyhy/757d3de19042070f70add54c180f81c1/raw/4537c2c7e1d232349cd00fd089abc69c0d367017/map.txt')

#table was made from ravenDS's table: https://github.com/RavenDS/Chicken-Extractor/blob/main/CIUTable.txt'
table = 'https://gist.githubusercontent.com/Ericbruhwhywhyhy/757d3de19042070f70add54c180f81c1/raw/4537c2c7e1d232349cd00fd089abc69c0d367017/map.txt'
s = urllib.request.build_opener()
#reimu my beloved :3
s.addheaders = [('User-Agent', "reimu/1.0")]
urllib.request.install_opener(s)

with urllib.request.urlopen(table) as response:
    data = response.read().decode()
    c = ast.literal_eval(data)

print("ECIAURS/Eric's Chicken Invaders Assets Unpacking and Repacking Script\n2025 Ericbruh")

mode = input('Chose a mode (1: unpack | 2: repack): ')
def read_u32(f):
    return struct.unpack("<I", f.read(4))[0]

def get_u32(input):
	return struct.pack('<I', input)

def process_tga(data):
    with open(data, 'rb+') as f:

        f.seek(0) 
        width = struct.unpack('<L', f.read(4))[0]

        height = struct.unpack('<L', f.read(4))[0]

        file_type = struct.unpack('<L', f.read(4))[0]

        offset = f.tell()

        f.seek(0, os.SEEK_END)
        size = f.tell() - offset

        f.seek(offset)
        image_data = f.read(size)
        header = bytearray()
        if file_type == 0x8:
        	header += struct.pack('<H', 0)          # id length
        	header += struct.pack('<H', 3)          # color map type
        	header += struct.pack('<L', 0)          # image type
        	header += struct.pack('<L', 0)          # color map specification
        	header += struct.pack('<H', width)      # width
        	header += struct.pack('<H', height)     # height
        	header += struct.pack('<B', 8)          # pixel depth
        	header += struct.pack('<B', 8)          # image descriptor
        elif file_type == 0x20:
        		header += struct.pack('<H', 0)          # id length
        		header += struct.pack('<H', 2)          # color map type
        		header += struct.pack('<L', 0)          # image type
        		header += struct.pack('<L', 0)          # color map specification
        		header += struct.pack('<H', width)      # width
        		header += struct.pack('<H', height)     # height
        		header += struct.pack('<B', 32)         # pixel depth
        		header += struct.pack('<B', 0)          # image descriptor
        else:
        		raise ValueError("Processing failed")
        f.seek(0, 0)
        f.write(header)
        f.write(image_data)

def unpack(filename, output_dir="."):
    unpacked = 0
    try:
    	open(filename)
    except Exception as e:
    	print(e)
    	return
    print(output_dir)
    with open(filename, "rb") as f:
        test = f.read(4)
        #legacy hq2x support coming soon...?
        if test != b"UVE ":
            raise ValueError("fuxk you this is not valid uve wad4 dule or smth")
        f.read(4)
        f.read(4)
        
        #number of files, very obvious lmao
        num_files = read_u32(f)
        #list of files and their offset, compressed size and actual size
        e = []
        for _ in range(num_files):
            name_crc = read_u32(f)
            name = f"{name_crc:08x}"
            name.replace('.', '')
            #print(name)
            if c.get(str(name).lower()) != None and c.get(str(name).lower()) != ' ':
            	#print('replacing name...')
            	#makeoffset(name, f) no longer necessary as the new repacking function reconstruct 222x from scratch
            	name = c.get(str(name).lower())
            	#print(name)
            offset = read_u32(f)
            zsize = read_u32(f)
            size = read_u32(f)
            e.append((name, offset, zsize, size))
            
       
        for name, offset, zsize, size in e:
            f.seek(offset)
            data = f.read(zsize)
            
            #decompress the data as a lot of them are compressed
            if size != zsize:
                try:
                    data = zlib.decompress(data)
                except zlib.error as e:
                    pass
                    continue
            #cursed way to strip name
            output_file = str(name).replace("[", "").replace("'", '').replace("]", "")
            output_path = os.path.dirname(output_file)
            #print(output_file)
            #print(name)
            #hacky way of actually make this work on Android
            if output_path != '/sdcard':
            	os.makedirs(os.path.join(output_dir, output_path), exist_ok=True)
            	try:
            		with open(os.path.join(output_dir, output_file), "wb") as out_file:
            			out_file.write(data)
            			unpacked  = unpacked + 1
            			#print(f"Extracted: {name}")
            			if '.tga' in str(name).replace("[", "").replace("'", '').replace("]", ""):
            					process_tga(os.path.join(output_dir, output_file))
            	except:
            		pass
            else:
            	print('skipping...')
            	
            sys.stdout.write('\r'f"Unpacked {unpacked}/{num_files} files")
            sys.stdout.flush()
    print('Done unpacking! Now restarting script...')
    print('\n')
    os.execl(sys.executable, sys.executable, *sys.argv)
            
            	
#repack function rewritten from scratch! No offset table required!
def repack(f):
    replacing_list = {}
    try:
    	open(f)
    except Exception as e:
    	print(e)
    	return
    with open(f, 'rb') as j:
        test = j.read(4)
        #legacy .hq2x support coming soon...?
        if test != b"UVE ":
            print('my brother i told you to give me a WAD4 file')
            return

        header = test + j.read(8)  #skip the first 12 bytes (UVE WAD + static)
        file_num = read_u32(j)
        
        #list of every file and their offset, compressed size and actual size
        entries = []

        #read every file in .222x file
        for _ in range(file_num):
            name_crc = read_u32(j)
            offset = read_u32(j)
            zsize = read_u32(j)
            size = read_u32(j)
            entries.append({
                'name_crc': name_crc,
                'offset': offset,
                'zsize': zsize,
                'size': size,
            })

        #now yeet them files into ram
        files_data = []
        for entry in entries:
            j.seek(entry['offset'])
            data = j.read(entry['zsize'])
            files_data.append(data)

    
    #inputted_file = "/sdcard/Download/aerial_city.mp3"
    replacing = input("Type out the file path in your .222x that you want to replace(ex: music/intense.ogg)\n(if you're confused please restart, then type 1 to get all files in your .222x file): ")
    inputted_file = input("Type out the file path that you want to replace the file in your .222x file with: ")
    #hex-ed replacing name (that is converting human readable name to gibberish that can then be read by the game)
    target_crc = None
    
    #browse through every file found in archive
    for crc, name in c.items():
        #if match found, convert the name of the file that's being replaced to stuff that again can be read by the game (ex: music/intense.ogg to 7c1ab6d6)'
        if name[0] == replacing:
            target_crc = int(crc, 16)
            break
    if target_crc is None:
        print(f'{replacing} not found! Try again')
        return
    
    #read data of the file that will replace the targeted file in .222x (i suck at writing comment)
    with open(inputted_file, "rb") as t:
        new_data = t.read()
        
    #this is here so that as soon as we found the file that we want to replace after browsing through each file, this will set to true which will immediately get straight to writing new reconstructed .222x file
    replaced = False
    for idx, entry in enumerate(entries):
        if entry['name_crc'] == target_crc:
            print(f"replacing {replacing} data with {inputted_file} data")
            files_data[idx] = new_data
            entry['zsize'] = len(new_data)
            entry['size'] = len(new_data)
            replaced = True
            break


    with open(f, "wb") as new:
        #since we are essentially reconstructing a brand new .222x file, we'll need to make sure that we have stuff like WAD signature written to our new .222x file so that the game doesn't say fuck you
        print("writing headers...")
        new.write(header)
        new.write(get_u32(file_num))

        entries_offset = new.tell()
        new.seek(entries_offset + file_num * 16)

        new_offsets = []
        print("writing old data...")
        #writing mostly old data into ram before actually yeeting it to our .222x file
        for data in files_data:
            current_offset = new.tell()
            new.write(data)
            new_offsets.append(current_offset)
        new.seek(entries_offset)
        print("writing new data...")
        #now we are actually getting into writing the new data by browsing through all files and their new offset inside our brand new file
        for idx, entry in enumerate(entries):
            new.write(get_u32(entry['name_crc']))
            new.write(get_u32(new_offsets[idx]))
            new.write(get_u32(entry['zsize']))
            new.write(get_u32(entry['size']))

    print("Done repacking! Now restarting script...")
    print('\n')
    os.execl(sys.executable, sys.executable, *sys.argv)
if mode == '1':
	path = input('Type out path to your 222x archive: ')
	#path = "/sdcard/CIU.dat.122x.standard.mp3"
	os.makedirs(os.path.join(os.path.dirname(path), 'extracted/'), exist_ok=True)
	out = os.path.join(os.path.dirname(path), 'extracted/')
	print(f"extracting to {out}")
	unpack(path, out)
	
elif mode == '2':
	path = input('Type out path to your 222x archive 222x archive: ')
	#path = "/sdcard/experiment/CIU.dat.122x.standard.mp3"
	repack(path)
else:
	print('Invalid. Chose again')
