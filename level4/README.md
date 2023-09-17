# Level 4

This is a real challenge, there is not a single output...
Tractus distributes the effort between developers.

Do you best finding a sub-optimal clean and simple but useful solution.

  "projects": [
    { "id": 1, "since": "2017-01-01", "until": "2017-12-31", "effort_days": 250 },
    { "id": 2, "since": "2017-03-17", "until": "2017-05-31", "effort_days": 150 },
    { "id": 3, "since": "2017-04-17", "until": "2017-05-31", "effort_days": 44 }

  "developers": [
    { "id": 1, "name": "Mi", "available_days_p1": 249,"available-days_p2": 50,"available_days_p3": 20},
    { "id": 2, "name": "Ti", "available_days_p1":248,"available-days_p2": 51,"available_days_p3": 15 },
    { "id": 3, "name": "Tony", "available_days_p1": 248,"available-days_p2": 51,"available_days_p3": 17 }
  ]

  I have the following json string file as in put, in here there are two lists "projects" and "developers". in projects list there are list of project with their, id, "since" which shows when the project would be initiated and the "until" which shows the deadline of each project there is another key called "effort_days" which shows the number of working days that special projects needed get done. in the develoeprs list we have list of developer that contains "id", "name" and "available_days_p1", "available-days_p2","available_days_p3" which theses three shows how many working days the special developer is available for a project. for example "available_days_p1" means the available working days for the project 1 on the project list. now I want a method which can distribute the projects in the most optimal way the goal is to finish a more tasks in the short amount of time. of course there could be overlapping of the project. but each project could be done by more than one developer to complete the whole tasks as quickly as possible. NO IDLE WORKER should be in the method. if the developer is idle should be assigned a task if the task is available.

  "Projects" list in which the elements are like the following:
 { "id": 1, "since": "2017-01-01", "until": "2017-12-31", "effort_days": 250 }
 "since" shows from when the project is defined. "until" shows the deadline for the project (the due) and "effort_days" shows how many working hours the project needed to get done. 
 there is another list "Developers" which contain the elements like the following:
 { "id": 1, "name": "Mi"}
 which shows "name" of the developer.

this project should find the available working hours of the each developer then assign the proejcts depend on the availability of the developer.
  I need an scheduling algorithm to work like the following:
1)first sort the project by their "since" elements, so the first one in the list should be the one which starts earlies.
2)iterate through projects in the list 
3) for each project allocate the maximum number of developers available to finish that ASAP.
4) check if the assigned "project"s could be halted and resume in another time because the newly arrived project should be started ASAP otherwise not feasible.
(So it is a good idea that for each newly project the available time for any developers calculated then to see if they can do the proejct in its due time or not if yes how many of the developers should be assigned )
5) if a project assigned the name of the developers and from when to estimed until time should be tracked in a list of map.



no the alogrithm should no allow tasks to get started befor the "since" and nor delivered after "until" dates. the project should be done between "since" and "until. on the other hand to handle larger efforts day, the algorithm should apply more developers to that project if by applying all available developers still it could not be done then it should be labeled as not feasible


for example for the following:
project = {
    "id": 2,
    "since": "2017-03-17",
    "until": "2017-05-31",
    "effort_days": 150
}
it is obvious that it could not be done in the period because 150 days of working days are not between the period. but by assigning the project to 3 developers we can make it done