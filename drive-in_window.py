# Hi, welcome to Drive-In Window Interpreter. Here is the menu.
#
# to know more about this programming language: $0
#
# Here are your sides.
#
# Interpreter Author 3snoW:  $2019
# Language Creator JWinslow23: $2013
# Marshmallows: $5
#
# May I take your order?
#
# Person 1 would like to know more about this programming language.
#
# OK, that will be https://esolangs.org/wiki/Drive-In_Window. Thanks for coming!

import sys

showWarnings = False #Change to true to display warning messages!

def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()

def printErrorMessage(filename,line_number,line,message):
    errorMessage = "\n"+'Error while parsing \''+filename+'\' at line '+str(line_number) + ' : ' + line
    errorMessage += "\n\t" + message
    print errorMessage

def printWarningMessage(filename,line_number,line,message):
    errorMessage = 'Warning while parsing \''+filename+'\' at line '+str(line_number) + ' : ' + line
    errorMessage += "\n\t" + message
    print errorMessage

if(len(sys.argv) > 1):
    filename = sys.argv[1]
else:
    print 'File to parse: '
    filename = raw_input().strip()

commands = []
f = open(filename,'r')
for line in f:
    commands.append(line.strip())
f.close()

people = {}
menu = {}
for_dict = {}
end_for_dict = {}

declarationState = 'start'
errorMessage = ''
line_number = 0
success = True
digits = '0123456789'

while line_number < len(commands):
    line = commands[line_number]
    warningMessage = ''
    line = line.strip()
    if not line:
        line_number += 1
        continue
    if declarationState == 'start':
        split_line = line.split('Hi, welcome to ')
        if len(split_line)<2:
            success = False
        else:
            split_line = split_line[1]
            split_line = split_line.split('. Here is a menu.')[0]
            split_line = split_line.strip()
            if not split_line:
                success = False
        if not success:
            errorMessage = 'Invalid Restaurant declaration. First sentence must be in the form of "Hi, welcome to __RESTAURANT_NAME__. Here is a menu."'
        else:
            declarationState = 'menu'
    elif declarationState == 'menu':
        split_line = line.split(':')
        if not len(split_line) == 2:
            if line == 'Here are your sides.' or line == 'May I take your order?':
                if not menu:
                    success = False
                    errorMessage = 'Menu can\'t be empty!'
                elif line == 'Here are your sides.':
                    declarationState = 'sides'
                else:
                    declarationState = 'main'
            else:
                success = False
                errorMessage = 'Menu entries must be in the form of "__MENU_ENTRY__: $__PRICE__".'
        else:
            menu_entry = split_line[0].strip()
            price = split_line[1].strip()
            if not price[0] == '$':
                success = False
                errorMessage = 'Menu prices must be in dollars.'
            elif not price[-1] == '0':
                success = False
                errorMessage = 'Menu prices must be multiples of 10 dollars.'
            else:
                price = price[1:]
                for digit in price:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Menu prices must be whole numbers.'
                        break
            if success:
                if menu_entry in menu:
                    warningMessage = 'Menu entry "'+menu_entry+'" was already declared with a value of $'+str(menu[menu_entry])
                menu[menu_entry] = int(price)
    elif declarationState == 'sides':
        split_line = line.split(':')
        if not len(split_line) == 2:
            if line == 'May I take your order?':
                declarationState = 'main'
            else:
                success = False
                errorMessage = 'Menu entries must be in the form of "__MENU_ENTRY__: $__PRICE__".'
        else:
            menu_entry = split_line[0].strip()
            price = split_line[1].strip()
            if not price[0] == '$':
                success = False
                errorMessage = 'Menu prices must be in dollars.'
            else:
                price = price[1:]
                for digit in price:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Menu prices must be whole numbers.'
                        break
            if success:
                if menu_entry in menu:
                    warningMessage = 'Menu entry "'+menu_entry+'" was already declared with a value of $'+str(menu[menu_entry]+'. Old value was replaced.')
                menu[menu_entry] = int(price)
    elif declarationState == 'main':

        #Person N would (not|also) like what Person Y has.
        if ' would ' in line and ' like what Person ' in line:
            split_line = line.split('Person ')
            if split_line[0] or (not line[-5:] == ' has.') or (not len(split_line)==3):
                success = False
                errorMessage = 'Invalid syntax.'
            else:
                person1 = split_line[1].split(' would ')[0].strip()
                person2 = split_line[2].split(' has.')[0].strip()
                modifier = split_line[1].split(' would ')[1].split(' like ')[0].strip()

                for digit in person1:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
                for digit in person2:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
                #Parse people:
                if success:
                    person1 = int(person1)
                    person2 = int(person2)
                    if person1 == 0 or person2==0:
                        success = False
                        errorMessage = 'Person must be greater than 0'
                    elif person1 not in people:
                        people[person1] = 0
                    elif person2 not in people:
                        people[person2] = 0
                #Assign people:
                if success:
                    if not modifier:
                        people[person1] = people[person2]
                    elif modifier == 'not':
                        people[person1] -= people[person2]
                    elif modifier == 'also':
                        people[person1] += people[person2]
                    else:
                        success = False
                        errorMessage = '"' + modifier + '" is not a valid modifier for a "would like" command. Valid modifiers are "would not like" and "would also like".'
                    people[person1] %= 256

        #Person N would (not|also) like menu_item( with side_item|, hold the side_item).
        elif 'Person ' in line and ' would ' in line and ' like ' in line:
            split_line = line.split('Person ')
            if split_line[0] or not line[-1] == '.':
                success = False
                errorMessage = 'Invalid syntax.'
            else:
                split_line = split_line[1].split(' would ')
                person = split_line[0].strip()
                split_line = split_line[1].split('like ')
                item = split_line[1]
                for digit in person:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
                #Parse person
                if success:
                    person = int(person)
                    if person == 0:
                        success = False
                        errorMessage = 'Person must be greater than 0'
                    elif person not in people:
                        people[person] = 0
                #Parse menu item and side dish
                if success:
                    side_price = 0
                    if ' with ' in item or ', hold the ' in item:
                        if ' with ' in item:
                            mod_with = True
                            split_item = item.split(' with ')
                        else:
                            mod_with = False
                            split_item = item.split(', hold the ')
                        item = split_item[0].strip()
                        if item[0:3] == 'the':
                            item = item[3:].lstrip()
                        side = split_item[1]
                        if side[0:3] == 'the':
                            side = side[3:].lstrip()
                        side = side[0:-1].strip()
                        if side not in menu:
                            success = False
                            errorMessage = 'Side dish "'+side+'" was not declared in the menu.'
                        else:
                            if mod_with:
                                side_price = menu[side]
                            else:
                                side_price = -menu[side]
                    else:
                        if item[0:3] == 'the':
                            item = item[3:].lstrip()
                        item = item[0:-1].strip()
                    if not item in menu:
                        success = False
                        errorMessage = 'Menu item "'+item+'" was not declared in the menu.'
                    else:
                        dish_price = menu[item]+side_price
                #Assign value to person
                if success:
                    modifier = split_line[0].strip()
                    if not modifier:
                        people[person] = dish_price
                    elif modifier == 'not':
                        people[person] -= dish_price
                    elif modifier == 'also':
                        people[person] += dish_price
                    else:
                        success = False
                        errorMessage = '"' + modifier + '" is not a valid modifier for a "would like" command. Valid modifiers are "would not like" and "would also like".'
                    people[person] %= 256

        #Person N will pay for his order!
        elif 'Person ' in line and ' will pay for his order!' in line:
            split_line = line.split('Person ')
            if split_line[0]:
                success = False
                errorMessage = 'Invalid syntax.'
            else:
                split_line = split_line[1].split(' will pay for his order!')
                person = split_line[0].strip()
                for digit in person:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
                #Parse person
                if success:
                    person = int(person)
                    if person == 0:
                        success = False
                        errorMessage = 'Person must be greater than 0'
                    elif person not in people:
                        people[person] = 0
                #Print person value:
                if success:
                    sys.stdout.write(str(unichr(people[person])))
        #Person N needs X dollars more/less for his order!
        elif 'Person 'in line and ' needs ' in line and (' dollars ' in line or ' dollar ' in line) and ' for his order!' in line and (' more ' in line or ' less 'in line):
            split_line = line.split('Person ')
            if split_line[0]:
                success = False
                errorMessage = 'Invalid syntax.'
            else:
                adding = ' more ' in line
                split_line[1] = split_line[1].replace(' more ',' ').replace(' less ',' ')
                person = split_line[1].split(' needs ')[0].strip()
                if ' dollars ' in line:
                    money = split_line[1].split(' needs ')[1].split(' dollars ')[0].strip()
                else:
                    money = split_line[1].split(' needs ')[1].split(' dollar ')[0].strip()

                for digit in person:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
                for digit in money:
                    if not digit in digits:
                        success = False
                        errorMessage = 'dollars must be a positive whole number.'
                        break
                #Parse person
                if success:
                    person = int(person)
                    if person == 0:
                        success = False
                        errorMessage = 'Person must be greater than 0'
                    elif person not in people:
                        people[person] = 0
                #Parse money and assign value
                if success:
                    if adding:
                        money = int(money)
                    else:
                        money = -1 * int(money)
                    if ' dollar ' in line and not money == 1:
                        warningMessage = 'Using "dollar" to reference a non singular amount of money.'
                    elif ' dollars ' in line and money == 1:
                        warningMessage = 'Using "dollars" to reference a single dollar.'
                    people[person] += money

        elif 'OK, what should Person ' in line and ' get?' in line:
            person = line.replace('OK, what should Person ','').replace(' get?','').strip()
            for digit in person:
                if not digit in digits:
                    success = False
                    errorMessage = 'Person must be a positive whole number.'
                    break
            if success:
                person = int(person)
                if person == 0:
                    success = False
                    errorMessage = 'Person must be greater than 0'
            if success:
                people[person] = ord(getch())
        elif 'OK, how much money should Person ' in line and ' have?' in line:
            person = line.replace('OK, how much money should Person ','').replace(' have?','').strip()
            for digit in person:
                if not digit in digits:
                    success = False
                    errorMessage = 'Person must be a positive whole number.'
                    break
            if success:
                person = int(person)
                if person == 0:
                    success = False
                    errorMessage = 'Person must be greater than 0'
            if success:
                people[person] = int(raw_input().strip())
        elif 'Let\'s just do this until Person ' in line and ' has no more money!' in line:
            if line_number not in for_dict:
                for_stack = []
                for cur_line_number in range(line_number,len(commands)):
                    cur_line = commands[cur_line_number]
                    if 'Let\'s just do this until Person ' in cur_line and ' has no more money!' in cur_line:
                        for_stack.append(cur_line_number)
                    elif 'Person ' in cur_line and ' has no more money!' in cur_line:
                        for_start = for_stack.pop()
                        for_end = cur_line_number
                        for_dict[for_start] = for_end
                        end_for_dict[for_end] = for_start
                        if not for_stack:
                            break
                if for_stack:
                    success = False
                    errorMessage = 'This loop has no end!'
            if success:
                person = line.replace('Let\'s just do this until Person ','').replace(' has no more money!','').strip()
                for digit in person:
                    if not digit in digits:
                        success = False
                        errorMessage = 'Person must be a positive whole number.'
                        break
            if success:
                person = int(person)
                if person == 0:
                    success = False
                    errorMessage = 'Person must be greater than 0'
            if success and people[person] == 0:
                line_number = for_dict[line_number]

        elif 'Person ' in line and ' has no more money!' in line:
            if line_number not in end_for_dict:
                success = False
                errorMessage = 'This loop has no start!'
            else:
                line_number = end_for_dict[line_number]-1
        elif line == 'Just wait while we decide...':
            raw_input()

        elif 'OK, that will be ' in line and '. Thanks for coming!' in line:
            declarationState = 'finished'
        else:
            success = False
            errorMessage = 'Unknown command, check the syntax.'
    else:
        break
    if not success:
        declarationState = 'error'
        break
    if showWarnings and warningMessage:
        printWarningMessage(filename,line_number,line,warningMessage)
    line_number += 1
#end while

if declarationState == 'error':
    printErrorMessage(filename,line_number,line,errorMessage)
