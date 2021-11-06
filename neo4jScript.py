from Household import *
from Person import *
from random import randint
from randomuser import RandomUser

households = []
persons = []
complete_query = ""
house_id = 0
#Generates 30 households nodes with associated the number of members
for fam_id in range(30):
    members = randint(1, 7)
    household = Household(house_id, members)
    households.append(household)
    complete_query = complete_query + 'CREATE(h' + str(house_id) + ': Huosehold {Id: ' + str(
        house_id) + ', Members: ' + str(members) + '})\n'
    house_id += 1

#Generates people for each household with random data taken from randomuser library
i = 0
for house in households:
    user_list = RandomUser.generate_users(house.members, {'nat': 'it'})
    for user in user_list:

        #POTREBBE NON SERVIRE SALVARE TUTTI I DATI NELLA CLASSE PERSON
        persons.append(Person(i, house.id, user.get_first_name(), user.get_last_name(), user.get_gender(), user.get_cell(),
                              user.get_city(), user.get_email()))
        #Creates the query to generate the Person node
        complete_query = complete_query + 'CREATE(p' + str(i) + ': Person {FirstName: "' + user.get_first_name() + '", LastName: "' + user.get_last_name() + '", Gender: "' + user.get_gender() + '", Cell: "' + user.get_cell() + '", City: "' + user.get_city() + '", Email: "' + user.get_email() + '"})\n'
        #Creates the query to generate the relation between the Person and its household
        complete_query = complete_query + 'CREATE (p' + str(i) + ')-[:PART_OF]->(h' + str(house.id) + ')\n'
        i += 1

# print(households.__repr__())
print(complete_query)
