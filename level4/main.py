from datetime import datetime
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
import holidays 
import json

ITALIAN_HOLIDAYS = holidays.IT()

def developer_birthdays(birthday, start, end):
    birthday_parts = birthday.split('-')
    start_year = start.split('-')[0]
    end_year = end.split('-')[0]
    birthdays=[]
    for year in range(int(start_year), int(end_year)+1):
        birthday = datetime(int(year), int(birthday_parts[1]), int(birthday_parts[2]))
        birthdays.append(birthday)
    
    return birthdays

def write_schedule_to_file(schedule, filename="output.json"):
    try:
        with open(filename, "w") as json_file:
            json.dump(schedule, json_file, indent=2)
    except IOError:
        print(f"Error writing to file: {filename}")


def assign_developers_to_projects(projects, developers, local_holidays):
    # Create the model.
    model = cp_model.CpModel()

    # Calculate the total number of days in the project period.
    total_days = (datetime.strptime(max(project['until'] for project in projects), '%Y-%m-%d').date() - datetime.strptime(min(project['since'] for project in projects), '%Y-%m-%d').date()).days

    # Create variables.
    assignments = {}
    project_selections = {}
    for project in projects:
        project_selections[project['id']] = model.NewBoolVar('y_{}'.format(project['id']))
        for developer in developers:
            for day in range(total_days):
                birthdays=developer_birthdays(developer["birthday"], project["since"], project["until"])
                # Check if the day is not a weekend
                current_date = datetime.strptime(min(project['since'] for project in projects), '%Y-%m-%d').date() + timedelta(days=day)
                if current_date.weekday() < 5 and current_date not in ITALIAN_HOLIDAYS and current_date not in birthdays and current_date not in local_holidays:  # 0-4 denotes Monday to Friday
                    if day >= (datetime.strptime(project['since'], '%Y-%m-%d').date() - datetime.strptime(min(project['since'] for project in projects), '%Y-%m-%d').date()).days and day < (datetime.strptime(project['until'], '%Y-%m-%d').date() - datetime.strptime(min(project['since'] for project in projects), '%Y-%m-%d').date()).days:
                        assignments[(developer['id'], day, project['id'])] = model.NewBoolVar('x_{}_{}_{}'.format(developer['id'], day, project['id']))

    # Create constraints.
    for project in projects:
        model.Add(sum(assignments[(developer['id'], day, project['id'])] for developer in developers for day in range(total_days) if (developer['id'], day, project['id']) in assignments) >= project['effort_days'] * project_selections[project['id']])

    for developer in developers:
        for day in range(total_days):
            model.Add(sum(assignments[(developer['id'], day, project['id'])] for project in projects if (developer['id'], day, project['id']) in assignments) <= 1)

    # Create objective function.
    model.Maximize(sum(project_selections.values()))

    # Solve the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print solution.
    if status == cp_model.OPTIMAL:
        feasible_projects = [project['id'] for project in projects if solver.Value(project_selections[project['id']]) == 1]
        schedule = []
        for developer in developers:
            for day in range(total_days):
                for project in projects:
                    if (developer['id'], day, project['id']) in assignments and solver.Value(assignments[(developer['id'], day, project['id'])]) == 1:
                        work_date = datetime.strptime(min(project['since'] for project in projects), '%Y-%m-%d').date() + timedelta(days=day)
                        schedule.append({"Developer": developer['id'], "Project": project['id'], "date": work_date.strftime('%Y-%m-%d')})

        output = {"feasible_projects": feasible_projects, "schedule": schedule}

        write_schedule_to_file(output)


def main():
    try:
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
    except (IOError, json.JSONDecodeError):
        print("Error Reading input file")
        return
    local_holidays = data.get("local_holidays", [])
    developers = data.get("developers", [])

    projects = data.get("projects", [])
    if not projects:
        print("The input file doesn't have the \"projects\" key")
        return
    
    local_holidays_list = []
    for local_holiday in local_holidays:
        local_holiday = datetime.strptime(local_holiday['day'], "%Y-%m-%d")
        if local_holiday.weekday() not in {5,6} and local_holiday not in ITALIAN_HOLIDAYS:
            local_holidays_list.append(local_holiday)

    assign_developers_to_projects(projects, developers, local_holidays_list)


if __name__ == "__main__":
    main()