import sys, socket, time, bitstring, numpy, cv2, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="port")
parser.add_argument("-ip", "--ip", help="ip")

def agw_connect(s):
    s.send(b'\x00\x00\x00\x00k\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    return

def start_socket(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        time.sleep(5)
        sys.exit()
    host = str(ip)
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        time.sleep(5)
        sys.exit()
    s.connect((remote_ip , port))
    print("--------------------------------------------------------")
    print("                                                        ")
    print("       RoseyCubesat-1 Image Frames Reader/Decoder       ")
    print("                     by Egor UB1QBJ                     ")
    print("                                                        ")
    print("--------------------------------------------------------")
    print('Connected to ' + str(remote_ip) + ":" + str(port))
    print("")
    print("To stop receiving and saving photos, press the key combination (CTRL + C) in this window!")
    print("")
    s.settimeout(0.5)
    return s

def create_dict():
    frames_dict={}
    i=0
    while(i!=2160):
        frames_dict[i]=str("0"*160)
        i+=1
    return frames_dict

def main(s, frames_dict):
    while True:
        try:
            try:
                frame = s.recv(2048).hex()
                frame = frame[104:]
                sync=frame[:12]
                if(sync=='f05701a40c00'):
                    frame_number=bitstring.BitStream(hex=str(str(frame[12:20]))).read('uint')
                    if(int(frame_number)<2160):
                        print('Normal image data! Frame number: '+str(frame_number)+' of 2159.'+str(' '*20), end='\r')
                        frames_dict.update({int(frame_number):str(frame[20:])})
                    if(int(frame_number)>2160):
                        print('Image preview data! Frame number: '+str(frame_number)+str(' '*20), end='\r')
            except socket.timeout:
                None
        except KeyboardInterrupt:
            out=open('out_data.bin', 'ab')
            key=0
            while(key!=2160):
                bitstring.BitArray(hex=str(frames_dict[key])).tofile(out)
                key+=1
            out.close()
            with open('out_data.bin', 'rb') as file:
                f=file.read()
                bbyteArray = bytearray(f)
                grayImage = numpy.array(bbyteArray).reshape(int(360), int(480))
                print("")
                print("Saving...")
                cv2.imwrite('image.png', grayImage)
                rgb= cv2.cvtColor(grayImage, cv2.COLOR_BayerGR2RGB)
                cv2.imwrite('image_rgb.png', rgb)
            os.remove('out_data.bin')
            sys.exit()

if(__name__=='__main__'):
    ip=parser.parse_args().ip
    port=parser.parse_args().port
    s=start_socket(ip=ip, port=int(port))
    agw_connect(s=s)
    frames_dict=create_dict()
    main(s=s, frames_dict=frames_dict)