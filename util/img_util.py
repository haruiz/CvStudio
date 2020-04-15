import cv2
import numpy as np


class ImageUtilities:
    # @staticmethod
    # def color_functions(backend="kornia"):
    #     if backend == "kornia":
    #         return {fname: fpy for fname, fpy in
    #                 inspect.getmembers(kornia.color,inspect.isfunction)
    #                     if fname.split("_")[0] == "rgb" and fname is not "rgb_to_rgba"}
    #     else:
    #         #i for i in dir(cv2) if i.startswith('COLOR_')
    #         return {k:v for k,v in  vars(cv2).items()
    #                     if k.startswith("COLOR_RGB2")}

    @staticmethod
    def adjust_brightness(src: np.ndarray, brightness_factor):
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        hsv[..., 2] = hsv[..., 2] * brightness_factor
        dst = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        dst = np.clip(dst, 0, 255)
        return dst

    # contrast : 1,100, brightness  = 50, 100

    @staticmethod
    def adjust_gamma(image, gamma=1.0):
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        # apply gamma correction using the lookup table
        return np.clip(cv2.LUT(image, table), 0, 255)

    @staticmethod
    def histogram_equalization(img: np.ndarray):
        if len(np.shape(img)) == 3:
            b, g, r = cv2.split(img)
            red = cv2.equalizeHist(r)
            green = cv2.equalizeHist(g)
            blue = cv2.equalizeHist(b)
            img = cv2.merge((blue, green, red))
        elif len(np.shape(img)) == 1:
            img = cv2.equalizeHist(img)
        return img

    @staticmethod
    def histogram_equalization2(img: np.ndarray):
        if len(np.shape(img)) == 3:
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            # equalize the histogram of the Y channel
            img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
            # convert the YUV image back to RGB format
            img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        return img

    @staticmethod
    def correct_lightness(img: np.ndarray):
        if len(np.shape(img)) == 3:
            img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(img_lab)
            clahe = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(4, 4))
            l = clahe.apply(l)
            img = cv2.merge((l, a, b))
            img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
        return img

    @staticmethod
    def kmeans(array: np.ndarray, k: int = 3):
        n_channels = 3 if len(np.shape(array)) == 3 else 1
        arr_values = array.reshape((-1, n_channels))
        arr_values = np.float32(arr_values)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, (centers) = cv2.kmeans(arr_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        clustered_arr = centers[labels.flatten()]
        clustered_arr = clustered_arr.reshape(array.shape)
        return clustered_arr

    @staticmethod
    def adjust_image(src, contrast, brightness) -> np.ndarray:
        return np.clip(cv2.addWeighted(src, contrast, np.zeros_like(src), 0, brightness - 50), 0, 255)
