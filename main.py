import csv
import time
import requests
from datetime import datetime, date, timedelta


output_file = 'eurojackpot_data.csv'


def get_fridays_and_tuesdays(start_year, end_date):
    draw_dates = []
    current_date = date(start_year, 1, 1)

    while current_date <= end_date:
        if current_date.weekday() in [1, 4]:
            draw_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return draw_dates


def get_all_draw_dates():
    start_year = 2012
    end_date = date.today()
    return get_fridays_and_tuesdays(start_year, end_date)

with open(output_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Date', 'Main Numbers', 'Bonus Numbers'])

    for draw_date in get_all_draw_dates():
        if datetime.strptime(draw_date, '%Y-%m-%d').date() > date.today():
            break

        r = requests.get(f"https://www.eurojackpot.com/wlinfo/WL_InfoService?client=jsn&gruppe=ZahlenUndQuoten&ewGewsum=ja&historie=ja&spielart=EJ&adg=ja&lang=en&datum={draw_date}")

        if r.status_code != 200:
            print(f"Error fetching data for date {draw_date}: HTTP {r.status_code}")
            continue

        try:
            data = r.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Error decoding JSON for date {draw_date}")
            continue

        main_numbers = []
        bonus_numbers = []

        for draw in data.get("zahlen", {}).get("hauptlotterie", {}).get("ziehungen", []):
            if draw['bezeichnung'] == "5 of 50":
                main_numbers = draw.get('zahlenSortiert', [])
            elif draw['bezeichnung'] in ["2 of 8", "2 of 10", "2 of 12"]:
                bonus_numbers = draw.get('zahlenSortiert', [])

        if not main_numbers or not bonus_numbers:
            continue

        csv_writer.writerow([draw_date, ','.join(map(str, main_numbers)), ','.join(map(str, bonus_numbers))])

        print(f"Date: {draw_date}, Main numbers: {main_numbers}, Bonus numbers: {bonus_numbers}")

print(f"\nData has been written to {output_file}")
