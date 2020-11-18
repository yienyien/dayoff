# Dayoff
Employee vacation handling system to manage leave.


## Data model

All employees belong to a team. There can be many teams.

Employee vacations can be of two types:
* Unpaid leave
* Paid leave

Paid leave can then be of two types:
* RTT (overtime compensation in France)
* Normal paid leave (by default)

A vacation has:
* A type of vacation (as explained above)
* A start date
* An end date

#### Notes

For this project:
* There is no half-day leaves, only complete days.
* There is no employee balance.
* Employees work a typical work week of 5/7 with weekends being on Saturday-Sunday


## The API

The API helps manage vacations including:
* Models and relationships for the various entities
* Features logic (see below)
* Endpoints to interact with features

The API features are:
* Create employees
* Create, update and delete vacations
* Search for employees on vacation given various parameters
* When creating or updating a vacation, if it overlaps (or is contiguous to) another one, merge them into one.
  Only works with vacations of the same type, else it will fail.
* Searching should also return the number of vacation days for each employee (given the search parameters).
* Compare two employees and return the days they will be both on vacation
