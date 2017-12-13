import random
import yaml
import requests

with open("config.yml", 'r') as f:
    config = yaml.load(f)

auth = config['auth']
api_url = config['api_url']
gift_url = config['gift_url']
password = config['password']

participants = config['participants']
ornament_list = [participant for participant in participants.keys()]
santee_list = [santee for santee in ornament_list if santee not in ['mom', 'dad']]


def random_santee(participant, santees):
    """
    Chooses a random person and compares to make sure it isnt the same as the participant and it is not the
    participants spouse

    Args:
        participant(str): The participant to pair with
        santees(list): Santees to choose from

    Returns:
        Santee(str): Name of the Santee to pair

    """
    # FIXME There is a random max depth recursive error that occurs occasionaly, but is resolved by running again
    santee = random.choice(santees)
    if santee != participant and santee != participants[participant]['spouse']:
        santees.remove(santee)
        return santee
    else:
        return random_santee(participant, santees)


def pick_santee():
    """
    Runs through the participant list and picks a partner for secret santa. If it is "mom" or "dad", they participate
    in the ornament exchange, but not secret santa

    """
    for participant in participants:
        if participant not in ['mom', 'dad']:
            participants[participant]['santee'] = random_santee(participant, santee_list)
        participants[participant]['ornament'] = random_santee(participant, ornament_list)


def send_simple_message(to, message):
    """
    Builds and sends the API post to the mailgun server

    Args:
        to(str): email address to send to
        message(str): the message that was generated to be sent

    Returns:
        response from request

    """
    return requests.post(
        api_url,
        auth=("api", auth),
        data={"from": "Secret Santa <santa@northpole.org>",
              "to": [to],
              "subject": "Merry Christmas",
              "text": message})


def kid_message(santa, santee, ornament):
    """
    Builds the message for the kids which includes their secret santa and ornament pick as well as a link to the website

    Args:
        santa(str): Name of the santa
        santee(str): Name of the santee
        ornament(str): Name of the ornament recipient

    Returns:
        message string

    """
    return ('Dear {santa},\n\n'
            '  This year you are {santee}\'s Secret Santa!. Ho Ho Ho!'
            ' The maximum spending limit is 50.00. To be as fair as possible, please make sure the total gift value'
            ' gets close to this amount. \n\n'
            '  You were also picked to get an ornament for {ornament} to help decorate their tree.\n\n'
            '  Go to {website} and fill out your form. You can also use this site to review '
            '{santee}\'s form.\n'
            'The password for the site is {password}\n\n\n '
            'Merry Christmas!\n\n'
            '  Secret Santa Bot\n\n\n'
            'This message was automagically generated from a computer.'
            ' Nothing could possibly go wrong...').format(password=password,
                                                          santa=santa.title(),
                                                          santee=santee.title(),
                                                          ornament=ornament.title(),
                                                          website=gift_url)


def parent_message(santa, ornament, participant_list):
    """
    Builds the message for the parents which includes their a full list of all the secret santa pairs and ornament
    pick as well as a link to the website

    Args:
        santa(str): Name of the santa
        ornament(str): Name of the ornament recipient
        participant_list(dict): Dictionary of the participants to build the santa/santee list

    Returns:
        message string

    """
    secret_santas = ''
    for participant in participant_list:
        if participant not in ['mom', 'dad']:
            secret_santas += ('    {santa} was picked to get a gift for {santee} '
                              '\n').format(santee=participant_list[participant]['santee'].title(),
                                           santa=participant.title())
    return ('Dear {santa},\n\n'
            '  You were picked to get an ornament for {ornament} to help decorate their tree.\n\n'
            '  This year the Secret Santa list is:\n\n'
            '{santa_list}\n\n'
            '  Go to {website} and fill out your form. You can also use this site to review '
            'everyone\'s form.\n'
            'The password for the site is {password}\n\n\n '
            'Merry Christmas!\n\n'
            '  Secret Santa Bot\n\n\n'

            'This message was automagically generated from a computer.'
            ' Nothing could possibly go wrong...').format(santa=santa.title(),
                                                          password=password,
                                                          santa_list=secret_santas,
                                                          ornament=ornament.title(),
                                                          website=gift_url)


def create_messages():
    """
    Build the messages to be sent.
    """
    for participant in participants:
        if participant in ['mom', 'dad']:
            participants[participant]['message'] = parent_message(santa=participant,
                                                                  participant_list=participants,
                                                                  ornament=participants[participant]['ornament'])
        else:
            participants[participant]['message'] = kid_message(santa=participant,
                                                               santee=participants[participant]['santee'],
                                                               ornament=participants[participant]['ornament'])


if __name__ == '__main__':
    # run the santa randomizer
    pick_santee()

    # create the message strings
    create_messages()

    # send out the emails
    for participant in participants:
        sent = send_simple_message(to=participants[participant]['email'],
                                   message=participants[participant]['message'])

        print(sent.text)
