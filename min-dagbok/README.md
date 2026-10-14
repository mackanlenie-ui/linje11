# Min Dagbok

En separat Android-app i Kotlin och Jetpack Compose. Projektet ligger i en egen mapp och egen GitHub-branch så att den befintliga **Mina arbetspass**-appen på `main` inte ändras.

## Funktioner i den första testversionen
- Mörkt gränssnitt med lila accent
- Skapa, redigera och radera dagboksinlägg
- Sökning, humörmarkering och favoriter
- PIN-lås samt fingeravtryck/enhetens autentisering
- Lokal krypterad lagring
- Export av inlägg som JSON via Androids delningsmeny

## Bygga APK
Kräver JDK 17 och Android SDK Platform 35. Kör `gradle assembleDebug` från den här mappen.
APK: `app/build/outputs/apk/debug/app-debug.apk`.

Kalendervy, bilder, import/återställning och påminnelser är ännu inte implementerade. Detta är en testversion, inte en Play Store-release.
