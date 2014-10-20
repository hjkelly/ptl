
from ..interactions.models import Checkin, Reminder
from ..profiles.models import Profile
from ..sms.models import Contact


def send_reminders():
    """
    Send SMS reminders to all the users/profiles that should get them.
    """
    profiles = Profile.objects.confirmed_for_reminders()
    for p in profiles:
        Reminder.objects.create(profile=p)


def route_incoming_sms(from_number, body):
    """
    Is this SMS a checkin or partner confirmation? Get it to the right place.
    """

    # Do we know this contact?
    try:
        contact = Contact.objects.get(phone_number=from_number)
    # If we haven't contacted them before...
    except Contact.DoesNotExist:
        # ... ignore them.
        return None

    # Try on a checkin for size and see if it makes sense.
    checkin = Checkin(contact=contact,
                      raw_body=body)
    if checkin.is_valid():
        # If it had a discernible status, save it and return it!
        checkin.save()
        return checkin

    # TODO: If not a checkin, could it be a confirmation from a partner?
    #elif ____:
    #    ____

    # If we didn't know what to do with the SMS:
    return None  # TODO: raise an error? Log an error?
