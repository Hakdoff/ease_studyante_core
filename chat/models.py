import json
from django.db import models
from base.models import BaseModelWithUUID, User
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


class ChatSession(BaseModelWithUUID):
    room_name = models.CharField(max_length=255)
    person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sessions_student')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sessions_teacher')

    class Meta:
        ordering = ["-updated_at"]


class ChatMessage(BaseModelWithUUID):
    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}: {self.message}"
    
    def save(self, *args, **kwargs) -> None:
        receiver = self.user
        sender = self.chat_session.person if self.chat_session.person.username != receiver.username else self.chat_session.teacher


        for device in FCMDevice.objects.all().filter(user=receiver):
            data = {
                "title": "EaseStudyante",
                "body": self.message,
                "full_name": sender.get_full_name(),
            }
            device.send_message(
                Message(
                    notification=Notification(
                        title="New Message", body=self.message
                    ),
                    data={
                        "json": json.dumps(data)
                    },
                )
            )

        
        super(ChatMessage, self).save(*args, **kwargs)


