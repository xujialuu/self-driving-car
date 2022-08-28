import paddle
import numpy as np
import matplotlib.pyplot as plt
from paddle.vision.transforms import transforms as T
import cv2
from model.RoadNet import RoadNet
from model.PredictDataset import PredictDataset
from urllib.request import urlopen
import threading
import time
from pure_pursuit.utils import car_controllor, VehicleState, pure_pursuit_control
from path_plan.utils import find_path
from traffic_sign.traffic_sign import detection
import requests


def read_ip_camera(stream):

    global url
    global img
    global bts
    global is_exit

    count = 0
    while not is_exit:
        try:
            bts += stream.read(CAMERA_BUFFRER_SIZE)
            jpghead=bts.find(b'\xff\xd8')
            jpgend=bts.find(b'\xff\xd9')
            
            if jpghead > -1 and jpgend > -1:
                print(count)
                count += 1
                jpg = bts[jpghead:jpgend + 2]
                bts = bts[jpgend + 2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype = np.uint8), cv2.IMREAD_UNCHANGED)

        except Exception as e:
            print("Error:" + str(e))
            bts = b''
            stream = urlopen(url)
            continue

# 主程序
if __name__ == '__main__':

    SHOW_IMAGE = True

    url = 'http://192.168.4.5:80/'
    stream = urlopen(url)
    CAMERA_BUFFRER_SIZE = 4096
    bts = b''
    img = None
    is_exit = False
    signs = open('./traffic_sign/label.txt', encoding='gbk')

    # 开始 imu 读取线程
    t1 = threading.Thread(target=read_ip_camera, args=(stream, ))
    t1.setDaemon(True)
    t1.start()

    time.sleep(3)

    ctrller = car_controllor()

    for i in range(10):

        if SHOW_IMAGE:
            plt.imshow(img[:, :, [2, 1, 0]])
            plt.show()
        output = detection(img)
        if output in signs:
            r = requests.post('http://192.168.4.1/find_sign?state='+str(output))#触发蜂鸣器
            # img=cv.resize(img,(640,480))
            imgzi = cv2.putText(img, 'Traffic signs detected' + output, (50, 300), 1, 1.2, (255, 255, 255), 2)

            plt.imshow(imgzi)
            plt.show()

        IMAGE_SIZE = (224, 224)
        # 修改图片分辨率
        width = 224
        height = 224

        # pic = cv2.resize(np.asarray(img_Image), (width, height))
        pic = cv2.resize(img, (width, height))
        cv2.imwrite('./your_predict/' + '1.jpg', pic)
        with open('./your_predict.txt', 'w') as f:
            f.write('your_predict/' + '1.jpg' + '\n')

        # 加载模型进行预测
        num_classes = 3
        network = RoadNet(num_classes)
        model = paddle.Model(network)

        optim = paddle.optimizer.RMSProp(learning_rate=0.001,
                                         rho=0.9,
                                         momentum=0.0,
                                         epsilon=1e-07,
                                         centered=False,
                                         parameters=model.parameters())
        model.prepare(optim, paddle.nn.CrossEntropyLoss(axis=1))

        model.load('model/checkpoints/final.pdparams')
        predict_dataset = PredictDataset(IMAGE_SIZE, mode='your_predict')
        predict_results = model.predict(predict_dataset)

        image_path = './your_predict/1.jpg'
        resize_t = T.Compose([
            T.Resize(IMAGE_SIZE)
        ])
        data = predict_results[0][0][0].transpose((1, 2, 0))
        mask = np.argmax(data, axis=-1)
        mask = mask.astype(np.float32)
        if SHOW_IMAGE:
            plt.figure()
            plt.imshow(mask.astype('float32'), cmap='gray')
            plt.axis("off")
            plt.show()

        try:
            path = find_path(mask, time_limit=5, SHOW_IMAGE=SHOW_IMAGE)
        except:
            ctrller.motor_control(-50)
            time.sleep(4)
            ctrller.motor_control(0)
            continue

        path_array = np.array(path)
        path_array = np.vstack((path_array[:, 1], path_array[:, 0])).T
        path_array[:, 1] = 29 - path_array[:, 1]
        path_array = path_array * 40
        print(path_array)

        if path_array[0][0] == path_array[len(path_array[0])-1][0]:  # 是否转弯
            flag = False
        else:
            flag = True

        if SHOW_IMAGE:
            plt.figure()
            plt.scatter(path_array[:, 0], path_array[:, 1], s=20, c='red', alpha=0.6)
            plt.show()


        # 路线跟踪常量
        Lf = 100.0  # look-ahead distance
        dt = 1.0  # [s]
        d = 144.0  # [mm] wheel base of vehicle
        timeout = 4.5  # time limit
        delta_candicate = np.array([-28, -16.2, 0.0, 16.2, 28]) / 180 * np.pi
        delta_cmd = np.array([90, 60, 0, -60, -90], np.int16) + 90

        ctrller.servo_control(90)
        ctrller.motor_control(50)
        state = VehicleState(x=800, y=0, delta=0.0, yaw=0, v=0)

        pure_pursuit_control(state, path_array, ctrller, flag, timeout)

    is_exit = True
    t1.join()