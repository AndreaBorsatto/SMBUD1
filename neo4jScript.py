from Household import *
from Person import *
from Vaccine import *
from random import *
from Test import *
from randomuser import RandomUser
import time as time

def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d/%m/%Y', prop)

def random_date_hour(start, end, prop):
    return str_time_prop(start, end, '%d/%m/%Y %H:%M', prop)


households = []
persons = []
test = [Test("Sierologico"), Test("Molecolare"), Test("Rapido")]  #TODO: DA TRADURRE
vaccines = [Vaccine("PfizerBioNTech", 180, 2), Vaccine("Moderna", 180, 2), Vaccine("AstraZeneca", 84, 2),
            Vaccine("JohnsonAndJohnson", 240, 1)]

complete_query = ""
house_id = 0

# Generates nodes for the vaccines
for vaccine in vaccines:
    complete_query = complete_query + 'CREATE(' + str(
        vaccine.name) + ': Vaccine{Name:"' + vaccine.name + '", Coverage:' + str(vaccine.coverage) + ', MinDoses:' + str(vaccine.minDoses) + '})\n'

# Generates 30 households nodes with associated the number of members
for fam_id in range(30):
    members = randint(1, 7)
    address = RandomUser().get_street()
    household = Household(house_id, members, address)
    households.append(household)
    complete_query = complete_query + 'CREATE(h' + str(house_id) + ': Huosehold {Id: ' + str(
        house_id) + ', Members: ' + str(members) + ', Address:"' + household.address +'"})\n'
    house_id += 1

# Generates people for each household with random data taken from randomuser library
i = 0
for house in households:
    user_list = RandomUser.generate_users(house.members, {'nat': 'it'})
    for user in user_list:
        # POTREBBE NON SERVIRE SALVARE TUTTI I DATI NELLA CLASSE PERSON
        persons.append(
            Person(i, house.id, user.get_first_name(), user.get_last_name(), user.get_gender(), user.get_cell(),
                   user.get_city(), user.get_email()))
        # Creates the query to generate the Person node
        complete_query = complete_query + 'CREATE(p' + str(
            i) + ': Person {FirstName: "' + user.get_first_name() + '", LastName: "' + user.get_last_name() + '", Gender: "' + user.get_gender() + '", Cell: "' + user.get_cell() + '", City: "' + user.get_city() + '", Email: "' + user.get_email() + '"})\n'
        # Creates the query to generate the relation between the Person and its household
        complete_query = complete_query + 'CREATE (p' + str(i) + ')-[:PART_OF]->(h' + str(house.id) + ')\n'
        i += 1

# Takes 80% of the people in the db and assigns a vaccine to them
persons_copy = persons.copy()
vaccinatedNum = int(len(persons) * 0.8)

for i in range(1, vaccinatedNum):
    vaccinated = persons_copy.pop(randint(0, len(persons_copy) - 1))
    #vaccine_type = randint(0, len(vaccines))
    vaccine = choice(vaccines)
    date = random_date("1/1/2021", "14/11/2021", random())
    complete_query = complete_query + 'CREATE (p' + str(vaccinated.id) + ')-[:GETS{Dose:1, Datetime:"' + date + '"}]->(' + vaccine.name + ')\n'
    #People that took a vaccine with a possible 2nd dose, have 50% to have already done it
    if vaccine.minDoses > 1 and random() > 0.5:
        complete_query = complete_query + 'CREATE (p' + str(vaccinated.id) + ')-[:GETS{Dose:2, Datetime:"' + random_date(date, "14/11/2021", random()) + '"}]->(' + vaccine.name + ')\n'

#Generates contacts between random people
contactNum = len(persons)
for i in range(1, contactNum):
    p1 = choice(persons)
    p2 = choice(persons)

    if p1 != p2:
        date = random_date_hour("1/1/2021 00:00", "14/11/2021 23:59", random())
        complete_query = complete_query + 'CREATE (p' + str(p1.id) + ')-[:CONTACT{Datetime:"'+ date + '"}]->(p' + str(p2.id) + ')\n'


print(complete_query)


