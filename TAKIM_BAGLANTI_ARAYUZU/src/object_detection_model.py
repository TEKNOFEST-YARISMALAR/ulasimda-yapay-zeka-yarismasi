import logging
import time
import random
import requests

from .constants import classes, landing_statuses
from .detected_object import DetectedObject
from .detected_translation import DetectedTranslation


class ObjectDetectionModel:
    # Takımların modelleri icin tanimlanmis sinif

    def __init__(self, evaluation_server_url):
        logging.info('Created Object Detection Model')
        self.evaulation_server = evaluation_server_url
        # Modelinizi bu kısımda init edebilirsiniz.
        # self.model = get_keras_model() # Örnektir!

    @staticmethod
    def download_image(img_url, images_folder):
        t1 = time.perf_counter()
        img_bytes = requests.get(img_url).content
        image_name = img_url.split("/")[-1]  # frame_x.jpg

        with open(images_folder + image_name, 'wb') as img_file:
            img_file.write(img_bytes)

        t2 = time.perf_counter()

        logging.info(f'{img_url} - Download Finished in {t2 - t1} seconds to {images_folder + image_name}')

    def process(self, prediction,evaluation_server_url,health_status):
        # Yarışmacılar resim indirme, pre ve post process vb işlemlerini burada gerçekleştirebilir.
        # Download image (Example)
        self.download_image(evaluation_server_url + "media" + prediction.image_url, "./_images/")
        # Örnek: Burada OpenCV gibi bir tool ile preprocessing işlemi yapılabilir. (Tercihe Bağlı)
        # ...
        # Nesne tespiti ve pozisyon kestirim modelinin bulunduğu fonksiyonun (self.detect() ) çağırılması burada olmalıdır.
        frame_results = self.detect(prediction,health_status)
        # Tahminler objesi FramePrediction sınıfında return olarak dönülmelidir.
        return frame_results

    def detect(self, prediction,health_status):
        # Modelinizle bu fonksiyon içerisinde tahmin yapınız.
        # results = self.model.evaluate(...) # Örnektir.

        # Burada örnek olması amacıyla 2 adet tahmin yapıldığı simüle edilmiştir.
        # Yarışma esnasında modelin tahmin olarak ürettiği sonuçlar kullanılmalıdır.
        # Örneğin :
        # for i in results: # gibi
        for i in range(1, 3):
            cls = classes["UAP"],  # Tahmin edilen nesnenin sınıfı classes sözlüğü kullanılarak atanmalıdır.
            landing_status = landing_statuses["Inilebilir"]  # Tahmin edilen nesnenin inilebilir durumu landing_statuses sözlüğü kullanılarak atanmalıdır.
            top_left_x = 12 * i  # Örnek olması için rastgele değer atanmıştır. Modelin sonuçları kullanılmalıdır.
            top_left_y = 12 * i  # Örnek olması için rastgele değer atanmıştır. Modelin sonuçları kullanılmalıdır.
            bottom_right_x = 12 * i  # Örnek olması için rastgele değer atanmıştır. Modelin sonuçları kullanılmalıdır.
            bottom_right_y = 12 * i  # Örnek olması için rastgele değer atanmıştır. Modelin sonuçları kullanılmalıdır.

            # Modelin tespit ettiği herbir nesne için bir DetectedObject sınıfına ait nesne oluşturularak
            # tahmin modelinin sonuçları parametre olarak verilmelidir.
            d_obj = DetectedObject(cls,
                                   landing_status,
                                   top_left_x,
                                   top_left_y,
                                   bottom_right_x,
                                   bottom_right_y
                                        )

            # Modelin tahmin ettiği her nesne prediction nesnesi içerisinde bulunan detected_objects listesine eklenmelidir.
            prediction.add_detected_object(d_obj)

        # Health Status biti hava aracinin uydu haberlesmesinin saglikli olup olmadigini gosterir.
        # Health Status 0 ise sistem calismali 1 ise gelen verinin aynisini gondermelidir.

        if health_status == '0':
            # Takimlar buraya kendi gelistirdikleri algoritmalarin sonuclarini entegre edebilirler.
            pred_translation_x = random.randint(1, 10) # Ornek olmasi icin rastgele degerler atanmistir takimlar kendi sonuclarini kullanmalidirlar.
            pred_translation_y = random.randint(1, 10) # Ornek olmasi icin rastgele degerler atanmistir takimlar kendi sonuclarini kullanmalidirlar.
        else :
            pred_translation_x = prediction.gt_translation_x
            pred_translation_y = prediction.gt_translation_y

        # Translation icin hesaplanilan degerleri sunucuya gondermek icin ilgili objeye dolduralim.
        trans_obj = DetectedTranslation(pred_translation_x, pred_translation_y)
        prediction.add_translation_object(trans_obj)

        return prediction