from urllib.request import urlopen
from ppdet.modeling.backbones.mobilenet import MobileNet
from ppdet.modeling.anchor_heads.yolo_head import YOLOv3Head
from ppdet.modeling.architectures.yolo import YOLOv3
import paddle.fluid as fluid
import numpy as np
import cv2
 
url = 'http://192.168.4.5/'
CAMERA_BUFFRER_SIZE = 4096
stream = urlopen(url)
bts=b''
i=0
f=open('label.txt', encoding='gbk')

def detection(image) :
    image = cv2.resize(image, dsize=(512, 512)).astype(np.float32)
    image = image/255
    mean = np.array([0.485, 0.456, 0.406]).astype(np.float32)
    image = image - mean[np.newaxis, np.newaxis, :]
    image = image.transpose((2,0,1))
    image = image[np.newaxis, :, :, :]
    image_size = np.array([512, 512])
    image_size = image_size[np.newaxis, :]
    
    #定义设备和program
    place = fluid.core.CPUPlace()
    exe = fluid.Executor(place)
    startup_program = fluid.Program()
    inference_program = fluid.Program()

    #搭建网络结构
    backbone = MobileNet()
    head = YOLOv3Head(num_classes=3)
    model = YOLOv3(backbone = backbone, yolo_head=head)
    with fluid.program_guard(inference_program, startup_program):
        data = fluid.layers.data(name = 'image', shape=[-1, 3, 512, 512], dtype='float32')
        im_size = fluid.layers.data(name = 'im_size', shape=[-1, 2], dtype='float32')
        test_fetches = model.test({'image':data, 'im_size':im_size})
    inference_program = inference_program.clone(for_test=True)

    #加载预训练模型
    fluid.io.load_persistables(executor=exe, dirname='C:\\Users\\Administrator\\.cache\\paddle\\weights\\, main_program = inference_program')

    #前项预测并输出结果
    output = exe.run(inference_program, fetch_list = [test_fetches['bbox']], feed={'image': image, 'im_size':image_size}, return_numpy=False)
    output = np.array(output[0])
    return output

'''while True:    
    try:
        bts+=stream.read(CAMERA_BUFFRER_SIZE)
        jpghead=bts.find(b'\xff\xd8')
        jpgend=bts.find(b'\xff\xd9')
        if jpghead>-1 and jpgend>-1:
            jpg=bts[jpghead:jpgend+2]
            bts=bts[jpgend+2:]
            img=cv.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv.IMREAD_UNCHANGED)
            cv.imshow("a",img)
            #cv.imwrite(str(i) + ".jpg", img)
            output = detection(img)
            if output in f:
                r = requests.post('http://192.168.4.1/control?state=0')#触发蜂鸣器
                #img=cv.resize(img,(640,480))
                imgzi = cv.putText(img, 'Traffic signs detected'+output, (50, 300), font, 1.2, (255, 255, 255), 2)
            
    except Exception as e:
        print("Error:" + str(e))
        bts=b''
        stream=urlopen(url)
        continue
    
    k=cv.waitKey(1)
    if k & 0xFF == ord('p'):#将图片保存在本地
        cv.imwrite(str(i) + ".jpg", img)
        i=i+1
    if k & 0xFF == ord(' '):
        break
cv.destroyAllWindows()'''
