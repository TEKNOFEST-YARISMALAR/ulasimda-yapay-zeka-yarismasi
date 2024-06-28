import json
import logging
import requests
import time
import os

class ConnectionHandler:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.auth_token = None
        self.classes = None
        self.frames = None
        self.translations = None
        self.frames_file = "frames.json"  # Kaydedilen frames dosyası
        self.translations_file = "translations.json"  # Kaydedilen translations dosyası

        # URL'leri tanımla
        self.url_login = self.base_url + "auth/"
        self.url_frames = self.base_url + "frames/"
        self.url_translations = self.base_url + "translation/"
        self.url_prediction = self.base_url + "prediction/"

        if username and password:
            self.login(username, password)

    def login(self, username, password):
        payload = {'username': username, 'password': password}
        files = []
        try:
            response = requests.post(self.url_login, data=payload, files=files, timeout=10)
            response_json = json.loads(response.text)
            if response.status_code == 200:
                self.auth_token = response_json['token']
                logging.info("Login Successfully Completed : {}".format(payload))
            else:
                logging.error("Login Failed : {}".format(response.text))
        except requests.exceptions.RequestException as e:
            logging.error(f"Login request failed: {e}")

    def save_frames_to_file(self, frames):
        with open(self.frames_file, 'w') as f:
            json.dump(frames, f)
        logging.info(f"Frames saved to {self.frames_file}")

    def load_frames_from_file(self):
        if os.path.exists(self.frames_file):
            with open(self.frames_file, 'r') as f:
                frames = json.load(f)
            logging.info(f"Frames loaded from {self.frames_file}")
            return frames
        logging.warning(f"{self.frames_file} does not exist.")
        return None

    def get_frames(self, retries=3, initial_wait_time=0.1):
        """
        Dikkat: Bir dakika içerisinde bir takım maksimum 5 adet get_frames isteği atabilmektedir.
        Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
        engellemek için tanımlanmıştır. get_frames fonksiyonunu kullanırken bu kısıtı göz önünde
        bulundurmak yarışmacıların sorumluluğundadır.
        """

        if os.path.exists(self.frames_file):
            logging.info("Frames file exists. Loading frames from file.")
            return self.load_frames_from_file()

        payload = {}
        headers = {'Authorization': 'Token {}'.format(self.auth_token)}
        wait_time = initial_wait_time

        for attempt in range(retries):
            try:
                response = requests.get(self.url_frames, headers=headers, data=payload, timeout=60)
                self.frames = json.loads(response.text)
                if response.status_code == 200:
                    logging.info("Successful : get_frames : {}".format(self.frames))
                    self.save_frames_to_file(self.frames)
                    return self.frames
                else:
                    logging.error("Failed : get_frames : {}".format(response.text))
            except requests.exceptions.RequestException as e:
                logging.error(f"Get frames request failed: {e}")

            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2

        logging.error("Failed to get frames after multiple retries. Loading frames from file.")
        return self.load_frames_from_file()

    def save_translations_to_file(self, translations):
        with open(self.translations_file, 'w') as f:
            json.dump(translations, f)
        logging.info(f"Translations saved to {self.translations_file}")

    def load_translations_from_file(self):
        if os.path.exists(self.translations_file):
            with open(self.translations_file, 'r') as f:
                translations = json.load(f)
            logging.info(f"Translations loaded from {self.translations_file}")
            return translations
        logging.warning(f"{self.translations_file} does not exist.")
        return None

    def get_translations(self, retries=3, initial_wait_time=0.1):
        """
          Dikkat: Bir dakika içerisinde bir takım maksimum 5 adet get_frames isteği atabilmektedir.
          Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
          engellemek için tanımlanmıştır. get_frames fonksiyonunu kullanırken bu kısıtı göz önünde
          bulundurmak yarışmacıların sorumluluğundadır.
          """

        if os.path.exists(self.translations_file):
            logging.info("Translations file exists. Loading translations from file.")
            return self.load_translations_from_file()

        payload = {}
        headers = {'Authorization': 'Token {}'.format(self.auth_token)}
        wait_time = initial_wait_time

        for attempt in range(retries):
            try:
                response = requests.get(self.url_translations, headers=headers, data=payload, timeout=60)
                self.translations = json.loads(response.text)
                if response.status_code == 200:
                    logging.info("Successful : get_translations : {}".format(self.translations))
                    self.save_translations_to_file(self.translations)
                    return self.translations
                else:
                    logging.error("Failed : get_translations : {}".format(response.text))
            except requests.exceptions.RequestException as e:
                logging.error(f"Get translations request failed: {e}")

            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2

        logging.error("Failed to get translations after multiple retries. Loading translations from file.")
        return self.load_translations_from_file()

    def send_prediction(self, prediction, retries=3, initial_wait_time=0.1):
        """
        Dikkat: Bir dakika içerisinde bir takım maksimum 80 frame için tahmin gönderebilecektir.
        Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
        engellemek için tanımlanmıştır. send_prediction fonksiyonunu kullanırken bu kısıtı göz
        önünde bulundurmak yarışmacıların sorumluluğundadır.

        Öneri: Bir dakika içerisinde gönderilen istek sayısı tutularak sistem hızlı çalışıyorsa
        bekletilebilir (wait() vb). Azami istek sınırı aşıldığında sunucu gönderilen tahmini
        veritabanına yazmamaktadır. Dolayısı ile bu durumu gözardı eden takımların istek sınır
        aşımı yapan gönderimleri değerlendirilMEyecektir. İstek sınırı aşıldığında sunucu aşağıdaki
        cevabı dönmektedir:
            {"detail":"You do not have permission to perform this action."}
        Ayrıca yarışmacılar sunucudan bu gibi başarısız bir gönderimi işaret eden cevap alındığında
        gönderilemeyen tahmini sunucuya tekrar göndermek üzere bir mekanizma tasarlayabilir.
        """


        payload = json.dumps(prediction.create_payload(self.base_url))
        files = []
        headers = {
            'Authorization': 'Token {}'.format(self.auth_token),
            'Content-Type': 'application/json',
        }
        wait_time = initial_wait_time

        for attempt in range(retries):
            try:
                response = requests.post(self.url_prediction, headers=headers, data=payload, files=files, timeout=60)
                if response.status_code == 201:
                    logging.info("Prediction sent successfully. \n\t{}".format(payload))
                    return response
                else:
                    logging.error("Prediction send failed. \n\t{}".format(response.text))
                    response_json = json.loads(response.text)
                    if "You do not have permission to perform this action." in response_json.get("detail", ""):
                        logging.info("Limit exceeded. 80frames/min \n\t{}".format(response.text))
                        return response
            except requests.exceptions.RequestException as e:
                logging.error(f"Prediction request failed: {e}")

            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2

        logging.error("Failed to send prediction after multiple retries.")
        return None
