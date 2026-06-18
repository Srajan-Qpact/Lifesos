# Push Notifications (Emergency Alerts)

This adds notifications that arrive **even when the app is closed or the phone is locked**,
with **sound** and a heads-up "Emergency Alert" banner. It uses **Firebase Cloud Messaging
(FCM)** — your server (or the Firebase console) sends a push, Google delivers it to every
phone instantly.

## What's already wired up in the app

You don't need to touch the native code — it's done:

- The `@capacitor/push-notifications` plugin is installed.
- A high-importance notification channel **`emergency_alerts`** is created on app start, with
  sound + vibration. (High importance is what makes it pop up and play a sound when the app is
  closed.)
- Every device automatically **subscribes to the topic `emergencies`**, so you can alert all
  users at once without tracking individual devices.
- The notification permission (Android 13+) is requested on first launch.
- A white status-bar icon and the brand red color are set as the notification defaults.

What's left is the part only you can do: create a Firebase project, drop one file into the
app, and trigger the sends.

---

## Step 1 — Create a Firebase project (free, ~5 min)

1. Go to https://console.firebase.google.com and click **Add project**. Give it any name
   (e.g. "LifeLine"). You can skip Google Analytics.
2. Inside the project, click the **Android** icon ( </> → Android ) to add an Android app.
3. For **Android package name**, enter exactly:
   ```
   com.lifeline.emergency
   ```
4. Click **Register app**, then **Download `google-services.json`**.

## Step 2 — Add the file to the project

Put the downloaded `google-services.json` here:

```
android/app/google-services.json
```

That's it. The project is already set up to detect this file and switch Firebase on
automatically (until it's there, the app builds and runs fine, just without push).

> If you're building in the cloud (GitHub Actions), commit this file to your repo at
> `android/app/google-services.json` and push. The next build will include push support.
> `google-services.json` is safe to commit (it's a client config, not a secret).

## Step 3 — Rebuild

Rebuild the APK the same way you did before (push to GitHub → download from Actions, or
`./gradlew assembleDebug` locally). Install it on your phone and **open it once** so it
registers and subscribes.

---

## Step 4 — Send a test alert (no code needed)

The fastest way to confirm it works, straight from the Firebase console:

1. In Firebase, open **Run** → **Messaging** (a.k.a. Cloud Messaging) → **Create your first
   campaign** → **Firebase Notification messages**.
2. Enter a **title** (e.g. `Emergency Alert`) and **text**, then click **Next**.
3. **Target:** choose **Topic** → `emergencies` (or send to a single device using its token —
   see below).
4. Under **Additional options (Android)** set **Android Notification Channel** to
   `emergency_alerts` so it uses the loud channel.
5. **Review** → **Publish**.

Now **close the app completely** (swipe it away) or lock the phone. The notification should
arrive within a few seconds, with sound. 🎉

> Finding a single device's token for a targeted test: connect the phone, open the app, and run
> `adb logcat -s LifeLine` — it prints `FCM registration token: …`. Use that token as the
> target in the console instead of the topic.

---

## Step 5 — Send alerts from your own server

When an emergency is created in your backend (e.g. your Replit server), call FCM to broadcast.
The easiest way is the **Firebase Admin SDK**.

### Get a server key
In Firebase: **Project settings** (gear) → **Service accounts** → **Generate new private key**.
This downloads a JSON file — **keep it secret**, it's server-only (never put it in the app or
a public repo).

### Node.js example (works on Replit)

```bash
npm install firebase-admin
```

```js
// send-alert.js
const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json'); // the secret key from above

admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });

async function sendEmergencyAlert(bodyText) {
  const response = await admin.messaging().send({
    topic: 'emergencies',                 // every install is subscribed to this
    notification: {
      title: '🚨 Emergency Alert',
      body: bodyText,
    },
    android: {
      priority: 'high',                   // wake the device
      notification: {
        channelId: 'emergency_alerts',    // the loud channel created in the app
        sound: 'default',
        defaultSound: true,
      },
    },
  });
  console.log('Alert sent:', response);
}

// call this whenever an incident is created:
sendEmergencyAlert('Someone near you needs help. Open LifeLine to respond.');
```

To alert **one specific device** instead of everyone, replace `topic: 'emergencies'` with
`token: '<that-device-FCM-token>'`. (You'd collect tokens from devices and store them in your
database — for that, have your web app read the token via the Push Notifications plugin and POST
it to your server.)

### Carrying data (e.g. an incident id)

Add a `data` block so a tapped notification can deep-link into the right screen:

```js
data: { incidentId: '0034', type: 'emergency' },
```

Your web app can read this when the app opens from the notification.

---

## iOS note

iOS push needs a few extra things that require a **paid Apple Developer account ($99/yr)**:
an APNs Authentication Key uploaded to Firebase, the **Push Notifications** capability enabled
in Xcode, and Background Modes → Remote notifications turned on. The same `emergencies` topic
and server code above then work for iPhones too. Tell me when you're ready and I'll walk through
the iOS-specific setup.

---

## Troubleshooting

- **No notification when closed** — make sure you opened the app at least once after installing
  (so it subscribed), and that notifications aren't disabled for the app in Android Settings.
- **Notification shows but no sound** — confirm the send used `channelId: 'emergency_alerts'`.
  Android decides sound from the *channel*, and that channel is the loud one. Also check the
  phone isn't on silent/Do Not Disturb.
- **Build error about `google-services.json`** — the file must be valid and at
  `android/app/google-services.json`, with package name `com.lifeline.emergency`.
- **Gray square icon** — that's expected for the small status-bar icon on some phones; the full
  color + heart shows in the expanded notification.
