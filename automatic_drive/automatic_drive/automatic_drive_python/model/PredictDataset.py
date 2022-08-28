import numpy as np
from paddle.io import Dataset
from PIL import Image as PilImage
from paddle.vision.transforms import transforms as T
import io

class PredictDataset(Dataset):
    # 数据集定义
    def __init__(self, IMAGE_SIZE, mode='train'):
        # 构造函数
        self.image_size = IMAGE_SIZE
        self.mode = mode.lower()
        self.train_images = []

        with open('./{}.txt'.format(self.mode), 'r') as f:
            for line in f.readlines():
                image = line.strip().split('\t')[0]
                self.train_images.append(image)

    def _load_img(self, path, color_mode='rgb', transforms=[]):
        # 统一的图像处理接口封装，用于规整图像大小和通道
        with open(path, 'rb') as f:
            img = PilImage.open(io.BytesIO(f.read()))
            if color_mode == 'grayscale':
                # if image is not already an 8-bit, 16-bit or 32-bit grayscale image
                # convert it to an 8-bit grayscale image.
                if img.mode not in ('L', 'I;16', 'I'):
                    img = img.convert('L')
            elif color_mode == 'rgba':
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
            elif color_mode == 'rgb':
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            else:
                raise ValueError('color_mode must be "grayscale", "rgb", or "rgba"')

            return T.Compose([
                                 T.Resize(self.image_size)
                             ] + transforms)(img)

    def __getitem__(self, idx):
        # 返回 image
        train_image = self._load_img(self.train_images[idx],
                                     transforms=[
                                         T.Transpose(),
                                         T.Normalize(mean=127.5, std=127.5)
                                     ])

        train_image = np.array(train_image, dtype='float32')
        return train_image

    def __len__(self):
        return len(self.train_images)
