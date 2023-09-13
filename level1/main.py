import holidays
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import dateutil.parser

ITALIAN_HOLIDAYS = holidays.IT()

def holiday_count(start_date, end_date):
    holidays_count = 0
    current_date = start_date
    interval = timedelta(days=1)

    while current_date <= end_date:
        
        if current_date.weekday() not in {5, 6} and current_date in ITALIAN_HOLIDAYS:
            holidays_count += 1
        current_date += interval

    return holidays_count

def process_periods(periods):
    availabilities = []

    for period in periods:
        try:
            period_start = dateutil.parser.parse(period["since"])
            period_end = dateutil.parser.parse(period["until"])
        except (ValueError, KeyError):
            print(f"Invalid period data: {period}")
            continue

        total_days = (period_end - period_start).days + 1

        work_days = sum(1 for tmp_day in (period_start + timedelta(days=i) for i in range(total_days)) if tmp_day.weekday() < 5)
        weekend_days = total_days - work_days

        holidays = holiday_count(period_start, period_end)
        work_days -= holidays

        availabilities.append(
            {
                "period_id": period["id"],
                "total_days": total_days,
                "workdays": work_days,
                "weekend_days": weekend_days,
                "holidays": holidays,
            }
        )

    return availabilities

def write_availabilities_to_file(availabilities, filename="output.json"):
    try:
        with open(filename, "w") as json_file:
            json.dump({"availabilities": availabilities}, json_file, indent=2)
    except IOError:
        print(f"Error writing to file: {filename}")

def main():
    try:
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    except (IOError, json.JSONDecodeError):
        print("Error Reading input file")
        return

    periods = data.get("periods", [])
    if not periods:
        print("The input file doesn't have the \"periods\" key")
        return

    availabilities = process_periods(periods)
    write_availabilities_to_file(availabilities)

    output_data = json.dumps({"availabilities": availabilities}, indent=2)
    print(output_data)

if __name__ == "__main__":
    main()