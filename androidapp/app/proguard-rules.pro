# Add project specific ProGuard rules here.
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.facebook.client.data.** { *; }
-dontwarn okhttp3.**
-dontwarn retrofit2.**
