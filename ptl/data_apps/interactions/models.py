from django.db import models

from ..profiles.models import Profile


class Reminder(models.Model):
    profile = models.ForeignKey(Profile, related_name='reminders')
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        If the profile is confirmed, send the reminder and save.
        """

        # Are they cleared to receive reminders? If not, complain.
        if not self.profile.confirmed:
            raise Exception("Profile for user {} hasn't been confirmed, so we "
                            "shouldn't send a reminder to them!".
                            format(self.profile.user.username))

        # Send the reminder message.
        content = ("Hey {}, have a llama! How have things been since your "
                   "last check-in? Respond with good, bad, or ugly.".
                   format(self.profile.name))
        self.profile.contact.send_sms(content)

        # Save as usual.
        return super(Reminder, self).save(*args, **kwargs)


def send_reminders():
    """
    Send SMS reminders to all the users/profiles that should get them.
    """
    profiles = Profile.objects.confirmed_for_reminders()
    for p in profiles:
        Reminder.objects.create(profile=p)
