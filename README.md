# LifeLine — Android + iOS (Capacitor)

This wraps your live LifeLine web app (`https://lifelineemergency.replit.app`) into native
**Android and iOS** apps using [Capacitor](https://capacitorjs.com). One codebase, both stores.
It includes your heart-EKG icon as a proper launcher/app icon on both platforms, a branded
splash screen, an offline fallback page, and location + network permissions for the
emergency/SOS features.

The app loads your hosted site in a native WebView, so anything you ship on Replit shows up in
the app instantly — no rebuild needed for content changes.

> **The honest short version on effort:**
> - **Android** → you can get a real, installable APK for **free**, with no tools installed, via
>   the included cloud build. See below.
> - **iOS** → Apple only allows iOS apps to be built on **macOS**, and putting one on a real
>   iPhone requires an **Apple ID** (free, for your own device) or an **Apple Developer account**
>   ($99/year, for TestFlight / the App Store). There is no fully-free, no-Mac path to an
>   installable iPhone app. The project here is 100% ready — you just need a Mac (or a paid
>   cloud-Mac service) for the final compile.

---

# ANDROID

## Fastest way to get an APK — build in the cloud (no tools to install)

A GitHub Actions workflow (`.github/workflows/android-build.yml`) compiles the APK on GitHub's
servers automatically.

1. Create a new repository on GitHub (private is fine).
2. Upload this entire folder to it. Either:
   - drag-and-drop the files into the GitHub web "Add file → Upload files" screen, **or**
   - from a terminal:
     ```bash
     git init
     git add .
     git commit -m "LifeLine"
     git branch -M main
     git remote add origin https://github.com/<you>/<repo>.git
     git push -u origin main
     ```
3. The build starts automatically. Open the **Actions** tab → the running job → wait ~5–8 min.
4. When it finishes, scroll to **Artifacts** and download **`LifeLine-debug-apk`**.
   Inside is `app-debug.apk`.
5. Copy the APK to your Android phone, tap it, and allow "install unknown apps" when prompted.

> This produces a **debug** APK — perfect for installing and testing on your own devices.
> For the Play Store you need a signed **release** build (see "Publishing to Google Play" below).

## Build Android locally instead

**Requirements:** Node.js 18+, JDK 21, and Android Studio (which brings the Android SDK).

```bash
npm install
npx cap sync android
npx cap open android      # opens the project in Android Studio
```

In Android Studio: let Gradle finish syncing, then **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
The APK lands in `android/app/build/outputs/apk/debug/app-debug.apk`.

**Or from the command line** (SDK must be installed and `ANDROID_HOME` set):

```bash
npm install
npx cap sync android
cd android
./gradlew assembleDebug
```

## Publishing to Google Play (release build)

1. Generate a keystore (once, keep it safe — losing it means you can't update the app):
   ```bash
   keytool -genkey -v -keystore lifeline.keystore -alias lifeline -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Add a signing config to `android/app/build.gradle` (`signingConfigs` + reference it in the
   `release` build type), or sign in Android Studio via **Build → Generate Signed Bundle / APK**.
3. Build an **app bundle**: `cd android && ./gradlew bundleRelease` →
   `android/app/build/outputs/bundle/release/app-release.aab`.
4. Upload the `.aab` in the [Google Play Console](https://play.google.com/console) (one-time
   $25 developer registration).

> Do **not** commit your keystore or passwords to GitHub. `*.keystore` / `*.jks` are already
> in `.gitignore`.

---

# iOS

The iOS project lives in **`ios/`** and is fully set up: your app icon (1024px), splash,
the bundle id `com.lifeline.emergency`, and the location permission prompt are all in place.
It uses **Swift Package Manager** (no CocoaPods), so there is no `.xcworkspace` — you open the
`.xcodeproj` directly and Xcode resolves the packages for you.

## Build & run on a Mac (the normal path)

**Requirements:** a Mac with **Xcode 15+** and Node.js 18+.

```bash
npm install
npx cap sync ios
npx cap open ios          # opens ios/App/App.xcodeproj in Xcode
```

In Xcode:
1. Wait for "Resolving Package Dependencies" to finish (first open only).
2. Select the **App** target → **Signing & Capabilities** → set **Team** to your Apple ID.
   (Add a free Apple ID in Xcode → Settings → Accounts if you don't have one.)
3. Pick a destination:
   - **A simulator** (e.g. iPhone 15) → press ▶︎ Run. No Apple account needed.
   - **Your own iPhone** (plugged in) → press ▶︎ Run. A free Apple ID works; the app stays
     valid for 7 days, then just re-run to refresh it.
4. To distribute beyond your own device, you need a paid **Apple Developer** account
   ($99/year) — then **Product → Archive → Distribute** for TestFlight or the App Store.

## No Mac? Your options

- **Cloud Mac / CI:** [Ionic Appflow](https://ionic.io/appflow) (Capacitor's own build service),
  or rent a Mac from [MacStadium](https://www.macstadium.com) / [MacinCloud](https://www.macincloud.com)
  and follow the Xcode steps above. All of these still require an Apple account to sign.
- **PWABuilder:** https://www.pwabuilder.com can package your PWA for iOS, but the output is
  still an Xcode project you must build and submit from a Mac with an Apple Developer account.
- **GitHub Actions compile check:** the included `.github/workflows/ios-build.yml` runs on a
  macOS runner and confirms the project **compiles** (unsigned, simulator only). Run it manually
  from the **Actions** tab → *iOS Build (compile check)* → **Run workflow**. It does **not**
  produce an installable app — signing an `.ipa` for a real device needs your Apple credentials.

## Publishing to the App Store

1. Enroll in the [Apple Developer Program](https://developer.apple.com/programs/) ($99/year).
2. In [App Store Connect](https://appstoreconnect.apple.com), create an app record with the
   bundle id `com.lifeline.emergency`.
3. In Xcode: bump the version/build, then **Product → Archive → Distribute App** to upload to
   TestFlight (beta testers) or submit for App Store review.

---

# Push notifications (emergency alerts)

The app is set up to receive **emergency push notifications that fire even when it's closed**,
with sound, via Firebase Cloud Messaging. The native side is done; to switch it on you create a
free Firebase project, drop one file (`google-services.json`) into `android/app/`, and rebuild.
Full step-by-step instructions — including how to send a test alert from the Firebase console
and how to trigger alerts from your own server — are in **[PUSH-NOTIFICATIONS.md](PUSH-NOTIFICATIONS.md)**.

---

# Shared configuration

All cross-platform settings live in **`capacitor.config.json`**. After **any** change, run the
sync for the platform(s) you build:

```bash
npx cap sync android
npx cap sync ios
```

### Point at a different URL
```json
"server": { "url": "https://your-new-url.com", "errorPath": "index.html" }
```

### Bundle the app to work fully offline (instead of loading the live URL)
Right now the app loads your hosted site. To ship the web build *inside* the app:

1. Build your web app on Replit and copy its output (the `dist` / `build` folder contents)
   into the **`www/`** folder here, replacing the placeholder `index.html`.
2. **Remove** the `"server"` block from `capacitor.config.json`.
3. `npx cap sync android` and/or `npx cap sync ios`, then rebuild.

### App name / ID
- **Name:** `appName` in `capacitor.config.json`; Android also has it in
  `android/app/src/main/res/values/strings.xml`; iOS in `ios/App/App/Info.plist`
  (`CFBundleDisplayName`).
- **ID (bundle id):** `appId` in `capacitor.config.json`. Android mirrors it as `namespace` /
  `applicationId` in `android/app/build.gradle`; iOS as `PRODUCT_BUNDLE_IDENTIFIER` in the Xcode
  project. Keep them identical across all three.

### Version
- **Android:** `android/app/build.gradle` — bump `versionCode` (integer, +1 each upload) and
  `versionName` (e.g. `"1.0.1"`).
- **iOS:** in Xcode (target → General), or `MARKETING_VERSION` / `CURRENT_PROJECT_VERSION` in the
  project settings.

### Icons / splash
Assets were generated from your heart-EKG mark for both platforms (Android: `mipmap-*` +
`drawable-*`; iOS: `ios/App/App/Assets.xcassets`). To regenerate from a new image, the easiest
tool is `@capacitor/assets`:
```bash
npm i -D @capacitor/assets
# put a 1024x1024 icon at assets/icon.png and a 2732x2732 splash at assets/splash.png
npx capacitor-assets generate            # both platforms
```
The generator scripts used here are in `tools/` (`gen_assets.py` for Android, `gen_ios_assets.py`
for iOS) if you'd rather tweak them directly.

---

## Note on emergency location

Location permissions are declared on both platforms (Android manifest; iOS
`NSLocationWhenInUseUsageDescription` in `Info.plist`). When your web app calls the browser's
geolocation API inside the WebView, the OS prompts the user to allow location on first use.
For rock-solid native location, switch to the included `@capacitor/geolocation` plugin from your
web code:
```js
import { Geolocation } from '@capacitor/geolocation';
const pos = await Geolocation.getCurrentPosition();
```
(That requires bundling the web app — see "Bundle the app to work fully offline" above — so your
code can import the plugin.)

---

## Troubleshooting

**Android**
- **"SDK location not found" locally** — open the project once in Android Studio so it writes
  `android/local.properties`, or set the `ANDROID_HOME` environment variable.
- **Gradle/JDK errors locally** — this project needs **JDK 21**. Check with `java -version`.
- **Cloud build failed** — open the failed step's logs in the Actions tab; the error is usually a
  missing SDK package, which the install step handles on a re-run.

**iOS**
- **"Signing requires a development team"** — select your Apple ID under the target's
  Signing & Capabilities tab.
- **Packages won't resolve** — File → Packages → Reset Package Caches, then build again. Make
  sure you ran `npm install` (the local plugins resolve from `node_modules`).
- **Wrong file opened** — open `ios/App/App.xcodeproj` (this project is SPM-based; there is no
  `.xcworkspace`).

**Both**
- **Web assets look stale** — always run `npx cap sync android` / `npx cap sync ios` after editing
  `www/` or the config, then rebuild.

---

Built with Capacitor 8. App ID `com.lifeline.emergency` · Android minSdk 24 (needs JDK 21) ·
iOS deployment target 15.0 (needs Xcode 15+ on macOS).
