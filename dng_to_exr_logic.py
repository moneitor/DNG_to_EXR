# This tool converts DNG to EXR using the next command line tools
#~ dcraw (http://www.guillermoluijk.com/tutorial/dcraw/index_en.htm)
#~ imagemagick (https://www.lifewire.com/convert-linux-command-unix-command-4097060)

# install dcraw by
#    sudo apt-get update -y
#    sudo apt-get install -y dcraw

# install imagemagick by
#    sudo apt install imagemagick


#cmd = 'dcraw -c -w -H 0 -o 1 -4'
#cmd = 'dcraw -c -w -H 0 -g 1.1 0 -q 3 -o 1 -6'
#cmd = 'dcraw -c -v -w -H 0 -k 256 -b 7 -q 3 -o 1 -4' NO GAMMA
#cmd = 'dcraw -c -w -H 0 -g 0.7 0 -b 1 -q 3 -o 1 -6' GAMMA WORKING
#cmd = 'dcraw -c -v -w -H 0 -n 1 -k 256 -b 10 -q 3 -o 1 -4'


import os
import subprocess
import glob



def get_files_of_type(dir, fileType):
    """
    Return files of the given filetype in a location (dir)
    """
    fils = []
    for x in os.walk(dir):		
        for y in glob.glob(os.path.join(x[0], "*.{}".format(fileType))):
            fils.append(os.path.normpath(y))

    if fils:
        return fils
    else:
        return "No files of type: {}".format(fileType)
    


def dng_to_exr(dng_path, output_folder, c_space, high_m, use_wb, use_gamma, black, white, gamma):
    """
    Converts a DNG file into an EXR file by using dcraw to Imagemagick's convert comand line tools
    """
    
    if os.path.isdir(output_folder):
        print ("Folder already exists.")
    else:
        os.makedirs(output_folder)
    
    if os.path.isfile(dng_path):
    
        file_name = os.path.splitext(os.path.basename(dng_path))[0] + ".exr"
        #cmd = 'dcraw -c -v -w -H 0 -n 1 -k 256 -b 10 -q 3 -o 1 -4
        cmd = 'dcraw -c '
        
        if use_wb:
            cmd += '-w '            

        cmd += ' -H {} '.format(high_m) # Clipping method
        cmd += '-n 1 ' # Noie reduction
        
        if not use_gamma:
            cmd += '-k {} '.format(str(black)) # K for black level
            
        cmd += '-b {} '.format(str(white)) # B for brightness
            
        if use_gamma:
            cmd += '-g {} 1 '.format(str(gamma))           

        cmd += '-q 3 ' # Filtering Quality
        
        if not use_gamma:
            cmd += '-o {} -4'.format(c_space) # Color Space -4
            
        if use_gamma:
            cmd += '-o {} -6'.format(c_space) # Color Space -4
        
        
        cmd += ' {} '.format(dng_path)
        cmd += '| convert - -depth 16 {}'.format(os.path.join(output_folder, file_name))
            
        

        subprocess.run(cmd, shell=True)        


def convert_all_dngs_to_exr(folder_input, folder_output, bar, c_space, high_m, use_wb, use_gamma, black, white, gamma):
    """
    Runs over all DNG file in the folder_input and saves an exr file for each one on the folder_output
    """
    folders = get_files_of_type(folder_input, "dng")
    files_total = len(folders)
    
    counter = 0
    
    for folder in folders:
        full_path = os.path.join(folder_input, folder)
        if os.path.isfile(full_path):
            print(full_path)
            dng_to_exr(full_path, folder_output, c_space, high_m, use_wb, use_gamma, black, white, gamma)    
            counter += 1       
            
            percentage = (counter / float(files_total) ) * 100
            
            bar.setValue(percentage)
            
            
    print("\n**************** Converting finished. ****************************\n\n")
            
    
    
if __name__ == "__main__":
    pass
    #convert_all_dngs_to_exr(folder_input, folder_output)
    
