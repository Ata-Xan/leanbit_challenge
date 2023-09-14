import json
from datetime import date, timedelta, datetime
import holidays 
from dateutil.relativedelta import relativedelta
import dateutil.parser

ITALIAN_HOLIDAYS = holidays.IT()


def holiday_count(start_date, end_date, local_holidays):
    holidays_count = 0
    current_date = start_date
    interval = timedelta(days=1)

    while current_date <= end_date:
        
        if current_date.weekday() not in {5, 6} and current_date in ITALIAN_HOLIDAYS:
            holidays_count += 1
        current_date += interval

    # print(local_holidays)

    for local_holiday in local_holidays:
        local_holiday = datetime.strptime(local_holiday['day'], "%Y-%m-%d")
        if local_holiday.weekday() not in {5,6} and local_holiday not in ITALIAN_HOLIDAYS and start_date<=local_holiday<=end_date:
            holidays_count+=1


    return holidays_count

def process_periods(periods, local_holidays):
    period_availabilities = []

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

        holidays = holiday_count(period_start, period_end, local_holidays)


        
        work_days -= holidays



        period_availabilities.append(
            {
                "period_id": period["id"],
                "start":period["since"],
                "end":period["until"],
                "total_days": total_days,
                "workdays": work_days,
                "weekend_days": weekend_days,
                "holidays": holidays,
            }
        )

    return period_availabilities

def write_availabilities_to_file(availabilities, filename="output.json"):
    try:
        with open(filename, "w") as json_file:
            json.dump({"availabilities": availabilities}, json_file, indent=2)
    except IOError:
        print(f"Error writing to file: {filename}")


def birthday_is_count(start_date, end_date, birthday_date):
    if start_date<=birthday_date<=end_date:
        return True


def birthday_holidays(birthday, start_date, end_date, local_holidays):
    birthday_parts = birthday.split('-')
    start_date_split = start_date.split('-')
    end_date_split = end_date.split('-')
    
    start_date_year = int(start_date_split[0])
    end_date_year = int(end_date_split[0])

    # print("start date", start_date)
    start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
    end_date = datetime.strptime(str(end_date), "%Y-%m-%d")

    birthdays_counts = 0
    
    for i in range(start_date_year, end_date_year+1):
        
        birthday_date_of_the_year = datetime(int(i), int(birthday_parts[1]), int(birthday_parts[2]))
        # Check to see if the birthday is a week day or in italian holidays
        if birthday_date_of_the_year.weekday() in {5,6} or birthday_date_of_the_year in ITALIAN_HOLIDAYS:
            continue;
        # Check to see if the birthday is in the local holidays
        birthday_is_local_holiday = False
        for local_holiday in local_holidays:
            local_holiday = datetime.strptime(local_holiday['day'], "%Y-%m-%d")
            if birthday_date_of_the_year == local_holiday:
                birthday_is_local_holiday = True
                break
        if birthday_is_local_holiday:
            continue
        
        if i==start_date_year and i==end_date_year:
            
            if birthday_is_count(start_date, end_date, birthday_date_of_the_year):  
                birthdays_counts +=1
        elif i==start_date_year and i<end_date_year:
            
            end_of_the_year_i = datetime.strptime(f"{i}-12-31", "%Y-%m-%d")
            if birthday_is_count(start_date, end_of_the_year_i, birthday_date_of_the_year):  
                birthdays_counts +=1
                
        elif i>start_date_year and i==end_date_year:
            
            start_of_the_year_i = datetime.strptime(f"{i}-01-01", "%Y-%m-%d")
            if birthday_is_count(start_of_the_year_i, end_date, birthday_date_of_the_year):  
                birthdays_counts +=1

        elif start_date_year<i<end_date_year:
            
            start_of_the_year_i = datetime.strptime(f"{i}-01-01", "%Y-%m-%d")
            end_of_the_year_i = datetime.strptime(f"{i}-12-31", "%Y-%m-%d")
            if birthday_is_count(start_of_the_year_i, end_of_the_year_i, birthday_date_of_the_year):
                birthdays_counts +=1

    
    return birthdays_counts 

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
    availabilities = []
    periods = data.get("periods", [])
    if not periods:
        print("The input file doesn't have the \"periods\" key")
        return
    
    developers = data.get("developers", [])

    local_holidays = data.get("local_holidays", [])
   
    period_availabilities  = process_periods(periods, local_holidays)

    # print(period_availabilities)
    
    for period in period_availabilities:
        for developer in developers:
            bd_holidays = birthday_holidays(developer["birthday"], period['start'], period['end'], local_holidays)
            # print(period['holidays'])
            availabilities.append({
                "developer_id": developer['id'],
                "period_id": period['period_id'],
                "total_days": period['total_days'],
                "workdays": period['workdays'] - bd_holidays,
                "weekend_days": period['weekend_days'],
                "holidays": period['holidays']+bd_holidays,
            })
    


    write_availabilities_to_file(availabilities)

    output_data = json.dumps({"availabilities": availabilities}, indent=2)


if __name__ == "__main__":
    main()
