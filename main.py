from typing import NamedTuple
import logging
import time

import requests
import play_sounds

import config


logger = logging.getLogger(__name__)


class AvailableCash(NamedTuple):
    currency: str
    amount: int


class ATM(NamedTuple):
    id: str
    location: str
    lat: float
    lng: float
    available_cash: list[AvailableCash]


def alert_cash_available():
    play_sounds.play_file(config.ALERT_PATH)


def alert_exc():
    play_sounds.play_file(play_sounds.DEFAULT_SOUND)


def get_atms_info() -> list[dict]:
    result = {}
    for currency in config.CURRENCY_FILTERS_AMOUNT_GT:
        response = requests.post(
            url=config.API_URL,
            json={
                'bounds': {
                    'bottomLeft': {'lat': config.QUERY_BOTTOM_LEFT_LAT, 'lng': config.QUERY_BOTTOM_LEFT_LNG},
                    'topRight': {'lat': config.QUERY_TOP_RIGHT_LAT, 'lng': config.QUERY_TOP_RIGHT_LNG},
                },
                'filters': {
                    'showUnavailable': True,
                    'currencies': [currency],
                },
                'zoom': config.QUERY_ZOOM,
            },
        )
        assert response.status_code == 200, (response.status_code, response.text)
        response = response.json()

        for cluster in response['payload']['clusters']:
            for atm_info in cluster['points']:
                result[atm_info['id']] = atm_info

    return list(result.values())


def get_suitable_atms() -> list[ATM]:
    result = []
    atms_info = get_atms_info()
    for atm_info in atms_info:
        if (
            (atm_id := atm_info['id']) in config.SKIP_ATMS_IDS
            or atm_info['pointType'] != 'ATM'
            or atm_info['brand']['name'].lower() != 'тинькофф банк'
        ):
            continue

        curr_amounts = {
            curr_name: AvailableCash(
                currency=curr_name,
                amount=limit['amount'],
            )
            for limit in atm_info['limits']
            if (curr_name := limit['currency']) in config.CURRENCY_FILTERS_AMOUNT_GT
        }

        if any(
            (avail_curr := curr_amounts.get(curr_name)) and avail_curr.amount >= expected_amount
            for curr_name, expected_amount in config.CURRENCY_FILTERS_AMOUNT_GT.items()
        ):
            location = atm_info['location']
            result.append(ATM(
                id=atm_id,
                location=atm_info['address'],
                lat=location['lat'],
                lng=location['lng'],
                available_cash=list(curr_amounts.values()),
            ))

    return result


def get_report(atms: list[ATM]) -> str:
    return '\n\n'.join(
        '\n'.join((
            f'ID: {atm.id}',
            f'Location: {atm.location}',
            ', '.join(
                f'{avail_curr.currency}: {avail_curr.amount}'
                for avail_curr in atm.available_cash
            ),
            (
                f'Link: https://www.tinkoff.ru/maps/atm/'
                f'?latitude={atm.lat}'
                f'&longitude={atm.lng}'
                f'&zoom={config.QUERY_ZOOM}'
                f'&currency={next(iter(curr.currency for curr in atm.available_cash))}'
            ),
        ))
        for atm in atms
    )


def try_find_cash():
    logger.info(f'searching for suitable atms')
    suitable_atms = get_suitable_atms()
    if not suitable_atms:
        logger.info(f'no suitable atms found')
        return

    report = get_report(suitable_atms)
    logger.info(f'cash found\n{report}')
    alert_cash_available()


def main():
    while True:
        try:
            try:
                try_find_cash()
            except Exception as e:
                logger.exception(e)
                alert_exc()

            time.sleep(config.POLL_DELAY_SECONDS)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
