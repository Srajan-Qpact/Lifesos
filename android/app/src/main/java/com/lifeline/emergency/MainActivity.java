package com.lifeline.emergency;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;

import androidx.core.app.ActivityCompat;

import com.getcapacitor.BridgeActivity;
import com.google.firebase.messaging.FirebaseMessaging;

public class MainActivity extends BridgeActivity {

    /** Channel used for emergency pushes. Must be HIGH importance + have a sound
     *  so notifications buzz and pop up even when the app is closed. */
    public static final String EMERGENCY_CHANNEL_ID = "emergency_alerts";

    /** Every device subscribes to this topic so the server can broadcast one
     *  alert to all installs without tracking individual tokens. */
    public static final String EMERGENCY_TOPIC = "emergencies";

    private static final String TAG = "LifeLine";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        createEmergencyChannel();
        requestNotificationPermission();
        setupFirebaseMessaging();
    }

    private void createEmergencyChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm =
                    (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;

            NotificationChannel channel = new NotificationChannel(
                    EMERGENCY_CHANNEL_ID,
                    "Emergency Alerts",
                    NotificationManager.IMPORTANCE_HIGH);
            channel.setDescription("Urgent emergency notifications");
            channel.enableLights(true);
            channel.enableVibration(true);
            channel.setVibrationPattern(new long[]{0, 400, 200, 400});

            Uri sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            AudioAttributes attrs = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();
            channel.setSound(sound, attrs);

            nm.createNotificationChannel(channel);
        }
    }

    private void requestNotificationPermission() {
        // Android 13+ requires the user to grant notification permission at runtime.
        if (Build.VERSION.SDK_INT >= 33) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(
                        this,
                        new String[]{android.Manifest.permission.POST_NOTIFICATIONS},
                        1001);
            }
        }
    }

    private void setupFirebaseMessaging() {
        // Guarded: before google-services.json is added, Firebase isn't initialized
        // and these calls would throw. The try/catch keeps the app running until then.
        try {
            FirebaseMessaging fm = FirebaseMessaging.getInstance();
            fm.subscribeToTopic(EMERGENCY_TOPIC);
            fm.getToken().addOnCompleteListener(task -> {
                if (task.isSuccessful() && task.getResult() != null) {
                    // Visible via `adb logcat -s LifeLine` for testing a single device.
                    Log.d(TAG, "FCM registration token: " + task.getResult());
                } else {
                    Log.w(TAG, "Fetching FCM token failed", task.getException());
                }
            });
        } catch (Throwable t) {
            Log.w(TAG, "Firebase not configured yet (add google-services.json). " + t.getMessage());
        }
    }
}
