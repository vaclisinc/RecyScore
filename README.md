# RecyScore

vaclis 日誌：
## Pi 前提綱要
- 我有設一個環境變數，$CONNECT_PACKAGE_PATH裡面有我們iot core跑start.sh裝那些套件的venv，可以用：
source $CONNECT_PACKAGE_PATH/venv/bin/activate
- 我有在樹莓派上暫時的用了一個ssh key連到我的github，所以可以自由自在的上傳到這個repo，學期末提醒我刪掉XD
- 我有開ssh權限，ssh vaclis@vaclishome.local，密碼vaclis
- 我有開vpc權限，推薦本機端可用RealVNC，然後host打vaclishome.local，密碼同上

## Pi to iot core to s3
### 在樹莓派端
- 每秒鐘拍照的在cam.py
- 先sudo apt install -y python3-libcamera libcamera-apps
- iot core最一開始會需要初始化，先創一個python venv：
python3 -m venv venv --system-site-packages
source venv/bin/activate
- 跑start.sh，他example就會開始傳垃圾上去給你測試，你有看到就可以終止了
- 跑cam.py，跑之前要先pip install AWSIoTPythonSDK picamera2 ===> cam.py是每兩秒拍一張照片上傳到s3
- 跑screen.py，一定要用樹莓派的terminal跑，可用vpc遠端控制==>screen.py會打開GUI，讓你可以按了觸控螢幕就拍照
- 跑realtime_camera.py，要先裝：
pip install --upgrade --force-reinstall --no-cache-dir pillow
### 在amazon端
- 在AWS IoT左側Message Routing/rules中的RaspberryPi_to_S3改成用lambda，lambda的程式碼在lambda/ImageHandler_vaclis.py
- 在AWS IoT左側All Devices/Things中的RaspberryPi_Cam中的b555123197747ec6327a53bf46c85636106f00b514b01e9a7b3fbc96fa730b81中的vaclis_home-Policy暫時改成iot有所有權限，程式碼在policy/vaclis_home-Policy.json