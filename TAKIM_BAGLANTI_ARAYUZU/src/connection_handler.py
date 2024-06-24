import json
import logging
import requests


class ConnectionHandler:
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.auth_token = None
        self.classes = None
        self.frames = None

        # Define URLs
        self.url_login = self.base_url + "auth/"
        self.url_frames = self.base_url + "frames/"
        self.url_translations = self.base_url + "translation/"
        self.url_prediction = self.base_url + "prediction/"

        if username and password:
            self.login(username, password)

    def login(self, username, password):
        payload = {'username': username,
                   'password': password}
        files = []
        response = requests.request("POST", self.url_login, data=payload, files=files, timeout=3)
        response_json = json.loads(response.text)
        if response.status_code == 200:
            self.auth_token = response_json['token']
            logging.info("Login Successfully Completed : {}".format(payload))
        else:
            logging.info("Login Failed : {}".format(response.text))

    def get_frames(self):
        """
        Dikkat: Bir dakika içerisinde bir takım maksimum 5 adet get_frames isteği atabilmektedir.
        Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
        engellemek için tanımlanmıştır. get_frames fonsiyonunu kullanırken bu kısıtı göz önünde
        bulundurmak yarışmacıların sorumluluğundadır.
        """
        payload = {}
        headers = {
            'Authorization': 'Token {}'.format(self.auth_token)
        }

        response = requests.request("GET", self.url_frames, headers=headers, data=payload)
        self.frames = json.loads(response.text)

        if response.status_code == 200:
            logging.info("Successful : get_frames : {}".format(self.frames))
        else:
            logging.info("Failed : get_frames : {}".format(response.text))

        return self.frames

    def get_translations(self):
        """
        Dikkat: Bir dakika içerisinde bir takım maksimum 5 adet get_frames isteği atabilmektedir.
        Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
        engellemek için tanımlanmıştır. get_translations fonsiyonunu kullanırken bu kısıtı göz önünde
        bulundurmak yarışmacıların sorumluluğundadır.
        """
        payload = {}
        headers = {
            'Authorization': 'Token {}'.format(self.auth_token)
        }

        response = requests.request("GET", self.url_translations, headers=headers, data=payload)
        self.frames = json.loads(response.text)

        if response.status_code == 200:
            logging.info("Successful : get_translations : {}".format(self.frames))
        else:
            logging.info("Failed : get_translations : {}".format(response.text))

        return self.frames

    def send_prediction(self, prediction):
        """
        Dikkat: Bir dakika içerisinde bir takım maksimum 80 frame için tahmin gönderebilecektir.
        Bu kısıt yarışma esnasında yarışmacıların gereksiz istek atarak sunucuya yük binmesini
        engellemek için tanımlanmıştır. send_prediction fonsiyonunu kullanırken bu kısıtı göz
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
        response = requests.request("POST", self.url_prediction, headers=headers, data=payload, files=files)
        if response.status_code == 201:
            logging.info("Prediction send successfully. \n\t{}".format(payload))
        else:
            logging.info("Prediction send failed. \n\t{}".format(response.text))
            response_json = json.loads(response.text)
            if "You do not have permission to perform this action." in response_json["detail"]:
                logging.info("Limit exceeded. 80frames/min \n\t{}".format(response.text))
        return response
