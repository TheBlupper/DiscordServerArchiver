import requests
import shutil
from discord import Webhook, RequestsWebhookAdapter, File

def send_webhook(url, avatar_url, name, content, attachments):
    webhook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
    webhook.send(content, username=name, avatar_url=avatar_url)

    if len(attachments) > 0:
        for a in attachments:
            filename = a.split('/')[-1]
            r = requests.get(a, stream=True)
            path = 'files/' + filename
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)
            webhook.send(file=File(path), username=name, avatar_url=avatar_url)
