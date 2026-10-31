# Discord webhook

Addons that post to Discord (like [[Herald]]) need a **webhook link**: a private address that lets a program
post messages into one specific channel. One person, whoever runs the Discord server, makes it once and
shares it with the group.

## Making the webhook (channel owner)

1. In Discord, hover over the channel → ⚙️ **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**.
   You need the *Manage Webhooks* permission on the server.
2. Optionally give it a name and picture. Herald sets its own name ("Herald") when it posts.
3. Click **Copy Webhook URL**. It looks like `https://discord.com/api/webhooks/123456789/AbCdEf...`.
4. Send it to your friends **privately**, e.g. in a DM. Everyone uses the **same** link, and each card
   shows whose character it's about.

## Keep it private

Anyone with the link can post in the channel. So don't paste it in public channels, screenshots, or on GitHub.

**If it leaks:** delete the webhook in the same Integrations menu, make a new one, and send the new link
around. Everyone then runs `Herald Setup.bat` (Windows) or `herald setup` (Linux) and pastes the new link.
