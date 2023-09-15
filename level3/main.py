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


    for local_holiday in local_holidays:
        local_holiday = datetime.strptime(local_holiday['day'], "%Y-%m-%d")
        if local_holiday.weekday() not in {5,6} and local_holiday not in ITALIAN_HOLIDAYS and start_date<=local_holiday<=end_date:
            holidays_count+=1


    return holidays_count

def process_projects(projects, local_holidays):
    project_availabilities = []

    for project in projects:
        try:
            project_start = dateutil.parser.parse(project["since"])
            project_end = dateutil.parser.parse(project["until"])
        except (ValueError, KeyError):
            print(f"Invalid project data: {project}")
            continue

        total_days = (project_end - project_start).days + 1

        work_days = sum(1 for tmp_day in (project_start + timedelta(days=i) for i in range(total_days)) if tmp_day.weekday() < 5)
        weekend_days = total_days - work_days

        holidays = holiday_count(project_start, project_end, local_holidays)


        
        work_days -= holidays



        project_availabilities.append(
            {
                "project_id": project["id"],
                "start":project["since"],
                "end":project["until"],
                "effort_days":project["effort_days"],
                "total_days": total_days,
                "workdays": work_days,
                "weekend_days": weekend_days,
                "holidays": holidays,

            }
        )

    return project_availabilities

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


def whole_workdays_for_each_project(availabilities):

    output_dict = {}

    for availability in availabilities:
        project_id = availability['project_id']
        workdays= availability['workdays']
       
        
        if project_id in output_dict:
            output_dict[project_id] += workdays
        else:
            output_dict[project_id] = workdays
            
    
    # output_list = [{'project_id': k, 'whole_work_days': v} for k, v in output_dict.items()]
    return output_dict

def feasibility_of_each_project(whole_work_days_dict, project_availabilities ):
    feasibilties_of_projects=[]
    # whole_work_days_dict = {item['project_id']: item['whole_work_days'] for item in whole_workdays}

    for project in project_availabilities:
        project_id = project['project_id']
        effort_days = project['effort_days']

        if project_id in whole_work_days_dict:
            whole_work_days = whole_work_days_dict[project_id]
            feasibility = False
            if effort_days<=whole_work_days:
                feasibility = True
            
            feasibilties_of_projects.append(
                {
                    "project_id": project["project_id"],
                    "total_days": project['total_days'],
                    "workdays": project['workdays'],
                    "weekend_days": project['weekend_days'],
                    "holidays": project['holidays'],
                    "feasibility":feasibility
                }
            )
                
        else:
            print(f"Project {project_id} not found in the second list")
        
    print(feasibilties_of_projects)
    return feasibilties_of_projects

  

def main():
    try:
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    except (IOError, json.JSONDecodeError):
        print("Error Reading input file")
        return
    availabilities = []
    projects = data.get("projects", [])
    if not projects:
        print("The input file doesn't have the \"projects\" key")
        return
    
    developers = data.get("developers", [])

    local_holidays = data.get("local_holidays", [])
   
    project_availabilities  = process_projects(projects, local_holidays)

    # print(project_availabilities)
    
    for project in project_availabilities:
        for developer in developers:
            bd_holidays = birthday_holidays(developer["birthday"], project['start'], project['end'], local_holidays)
            # print(project['holidays'])
            availabilities.append({
                "developer_id": developer['id'],
                "project_id": project['project_id'],
                "effort_days":project["effort_days"],
                "total_days": project['total_days'],
                "workdays": project['workdays'] - bd_holidays,
                "weekend_days": project['weekend_days'],
                "holidays": project['holidays']+bd_holidays,
            })
    
    whole_workdays = whole_workdays_for_each_project(availabilities)

    feasibility_of_projects = feasibility_of_each_project(whole_workdays, project_availabilities )



    write_availabilities_to_file(feasibility_of_projects)
    

    # 


if __name__ == "__main__":
    main()