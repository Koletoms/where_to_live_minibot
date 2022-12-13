import requests
import json
from bot_state import LowAndHighPrice, BestDeal


class Hotel:
    """
    Класс отель. Ищет и содержит данные об отеле.
    """
    def __init__(self, name, id, price_day, price_total, distance) -> None:
        self.name: str = name
        self.id: int = id
        self.price_day: str = price_day
        self.price_total: str = price_total
        self.adress_hotel: None | str = None
        self.distance_to_center: str = distance
        self.photo_list: list = list()

    def find_details(self) -> None:
        """
        Ищет адрес и url на фото отеля по его id.
        :return:
        """
        url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "propertyId": f"{self.id}"
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "0dd6bbf5f7msheacb85befeee218p175c26jsn7fe7257c83e6",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        hotel_details = json.loads(response.text)

        self.adress_hotel = hotel_details['data']['propertyInfo']['summary']['location']['address']['addressLine']
        list_images = hotel_details['data']['propertyInfo']['propertyGallery']['images']
        for image in list_images:
            self.photo_list.append(image['image']['url'])


class SearchHotels:
    """
    Формирует необходимые данные для поиска отелей.
    Формирует список отелей.
    """

    def __init__(self) -> None:
        # запрашиваются у пользователя
        self.command: str = 'lowprice'
        self.state_set = LowAndHighPrice
        self.place: str = 'париж'
        self.location_id: int = 2114  # Пользователь выбирает из self.location.
        self.number_hotels: int = 5
        self.number_photo: None | int = None
        self.distance: int = 10
        self.arrival: tuple = (22, 2, 2023)
        self.departure: tuple = (20, 2, 2023)
        self.max_price: int = 200
        self.min_price: int = 20

        # формируются методами
        self.locations: list = list()
        self.hotels: list = list()

    def find_locations(self) -> None:
        """
        Функция для определения локации при поиске отелей.
        Формирует список с названием и id локаций исходя из названия города и соседних районов.
        """

        url = "https://hotels4.p.rapidapi.com/locations/v3/search"
        querystring = {
            "q": f"{self.place}",
            "locale": "ru_RU",
            "siteid": "300000001"
        }
        headers = {
            "X-RapidAPI-Key": "0dd6bbf5f7msheacb85befeee218p175c26jsn7fe7257c83e6",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).text
        # убрать
        if not response:
            print("Произошла ошибка.\nПопробуйте снова.")

        else:
            result = json.loads(response)

            for found_object in result.get('sr'):
                if found_object.get('type') in ('CITY', 'NEIGHBORHOOD'):
                    id_location = found_object.get('gaiaId')
                    name_location = found_object.get('regionNames').get('displayName')

                    self.locations.append((name_location, id_location))  # Добавление локации в список.

    def find_hotels(self) -> None:
        """
        Производит запрос на API, формирует список экземпляров класса Hotel.
        """

        d_in, m_in, y_in = self.arrival
        d_out, m_out, y_out = self.departure

        url = "https://hotels4.p.rapidapi.com/properties/v2/list"
        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "destination": {"regionId": f"{self.location_id}"},
            "checkInDate": {"day": d_in, "month": m_in, "year": y_in},
            "checkOutDate": {"day": d_out, "month": m_out, "year": y_out},
            "rooms": [{"adults": 2}],
            "resultsStartingIndex": 0,
            "resultsSize": 25
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "0dd6bbf5f7msheacb85befeee218p175c26jsn7fe7257c83e6",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        match self.command:  # Дополняет запрос в зависимости от команды пользователя.
            case 'lowprice':
                payload['sort'] = 'PRICE_LOW_TO_HIGH'
            case 'bestdeal':
                payload['sort'] = 'DISTANCE'
                payload['filters'] = {'price': {'max': self.max_price, 'min': self.min_price}}

        response = requests.request("POST", url, json=payload, headers=headers)
        data_hotels = json.loads(response.text)

        for hotel in data_hotels['data']['propertySearch']['properties']:  # Формирует список отелей.
            try:  # Подправить
                distance_to_cent = hotel['destinationInfo']['distanceFromDestination']['value']
                if distance_to_cent <= self.distance:
                    new_hotel = Hotel(
                        name=hotel.get('name'),
                        id=int(hotel.get('id')),
                        price_day=hotel['price']['lead']['formatted'],
                        price_total=hotel['price']['displayMessages'][1]['lineItems'][0]['value'],
                        distance=distance_to_cent
                    )
                    self.hotels.append(new_hotel)
            except :
                print('ошибка в добавение отеля')
                continue


user_request = SearchHotels()
