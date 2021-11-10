from Household import *
from Person import *
from Vaccine import *
from random import *
from Test import *
from Location import *
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
people = []
tests = [Test("Sierologico"), Test("Molecolare"), Test("Rapido")]  # TODO: DA TRADURRE
vaccines = [Vaccine("PfizerBioNTech", 180, 2), Vaccine("Moderna", 180, 2), Vaccine("AstraZeneca", 84, 2),
            Vaccine("JohnsonAndJohnson", 240, 1)]
locations = [Location("Cinema1", 2), Location("Cinema2", 2), Location("Cinema3", 2), Location("Restaurant1", 1.5),
             Location("Restaurant2", 1.5), Location("Restaurant3", 1.5), Location("Restaurant4", 1.5),
             Location("Restaurant5", 1.5), Location("Restaurant6", 1.5), Location("Restaurant7", 1.5),
             Location("Restaurant8", 1.5), Location("Restaurant9", 1.5), Location("Restaurant10", 1.5),
             Location("Pub1", 1), Location("Pub2", 1), Location("Pub3", 1), Location("Pub4", 1), Location("Pub5", 1),
             Location("Hairdresser1", 0.5), Location("Hairdresser2", 0.5)]

complete_query = ""
house_id = 0

# Generates nodes for the vaccines
for vaccine in vaccines:
    complete_query = complete_query + 'CREATE(' + str(
        vaccine.name) + ': Vaccine{name:"' + vaccine.name + '", coverage:' + str(
        vaccine.coverage) + ', minDoses:' + str(vaccine.minDoses) + '})\n'

# Generates nodes for tests
for test in tests:
    complete_query = complete_query + 'CREATE(' + test.type + ': Test{type:"' + test.type + '"})\n'

# Generates nodes for locations
for location in locations:
    complete_query = complete_query + 'CREATE(' + location.name + ': Location{name:"' + location.name + '", avgStayTime:'+ str(location.averageStay) + '})\n'

# Generates 30 households nodes with associated the number of members
for fam_id in range(30):
    members = randint(1, 7)
    address = RandomUser().get_street()
    household = Household(house_id, members, address)
    households.append(household)
    complete_query = complete_query + 'CREATE(h' + str(house_id) + ': Huosehold {Id: ' + str(
        house_id) + ', Members: ' + str(members) + ', Address:"' + household.address + '"})\n'
    house_id += 1

# Generates people for each household with random data taken from randomuser library
i = 0
for house in households:
    user_list = RandomUser.generate_users(house.members, {'nat': 'it'})
    for user in user_list:
        # POTREBBE NON SERVIRE SALVARE TUTTI I DATI NELLA CLASSE PERSON
        people.append(
            Person(i, house.id, user.get_first_name(), user.get_last_name(), user.get_gender(), user.get_cell(),
                   user.get_city(), user.get_email()))
        # Creates the query to generate the Person node
        complete_query = complete_query + 'CREATE(p' + str(
            i) + ': Person {FirstName: "' + user.get_first_name() + '", LastName: "' + user.get_last_name() + '", Gender: "' + user.get_gender() + '", Cell: "' + user.get_cell() + '", City: "' + user.get_city() + '", Email: "' + user.get_email() + '"})\n'
        # Creates the query to generate the relation between the Person and its household
        complete_query = complete_query + 'CREATE (p' + str(i) + ')-[:PART_OF]->(h' + str(house.id) + ')\n'
        i += 1

# Takes 80% of the people in the db and assigns a vaccine to them
people_copy = people.copy()
vaccinatedNum = int(len(people) * 0.8)

for i in range(0, vaccinatedNum):
    vaccinated = people_copy.pop(randint(0, len(people_copy) - 1))
    # vaccine_type = randint(0, len(vaccines))
    vaccine = choice(vaccines)
    date = random_date("1/1/2021", "14/11/2021", random())
    complete_query = complete_query + 'CREATE (p' + str(
        vaccinated.id) + ')-[:GETS{Dose:1, Datetime:"' + date + '"}]->(' + vaccine.name + ')\n'
    # People that took a vaccine with a possible 2nd dose, have 50% to have already done it
    if vaccine.minDoses > 1 and random() > 0.5:
        complete_query = complete_query + 'CREATE (p' + str(
            vaccinated.id) + ')-[:GETS{Dose:2, Datetime:"' + random_date(date, "14/11/2021",
                                                                         random()) + '"}]->(' + vaccine.name + ')\n'

# Generates contacts between random people
contactNum = len(people)
for i in range(contactNum):
    p1 = choice(people)
    p2 = choice(people)

    if p1 != p2:
        date = random_date_hour("1/1/2021 00:00", "14/11/2021 23:59", random())
        complete_query = complete_query + 'CREATE (p' + str(p1.id) + ')-[:CONTACT{Datetime:"' + date + '"}]->(p' + str(
            p2.id) + ')\n'

# Associates tests with people
for i in range(100):
    tested_person = choice(people)
    test_type = choice(tests)
    test_date = random_date("1/2/2020", "14/11/2021", random())
    # 40% probability to be positive after a test
    test_result = "Negative" if random() > 0.4 else "Positive"

    complete_query = complete_query + 'CREATE(p' + str(
        tested_person.id) + ')-[:TAKES{datetime:"' + test_date + '" , result:"' + test_result + '"}]->(' + test_type.type + ')\n'

# Associates locations with people
for i in range(100):
    location = choice(locations)
    person = choice(people)
    test_date = random_date("1/2/2020", "14/11/2021", random())

    complete_query = complete_query + 'CREATE(p' + str(person.id) + ')-[:VISITS{datetime:"' + date + '"}]->(' + location.name + ')\n'


print(complete_query)
