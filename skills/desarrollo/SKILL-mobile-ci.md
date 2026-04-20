# SKILL Mobile CI/CD & App Distribution

> **Version:** 3.8.0
> **Trigger:** CI/CD para apps moviles, firma, publicacion en stores
> **Agente:** nxt-mobile, nxt-devops

## Herramientas

| Herramienta | Funcion | Plataforma |
|-------------|---------|-----------|
| Fastlane | Build + Sign + Deploy | iOS + Android |
| EAS Build | Build en la nube | React Native (Expo) |
| Codemagic | CI/CD managed | Flutter + RN |
| GitHub Actions | CI custom | Cualquiera |
| App Center | Distribution beta | Cualquiera |
| Firebase App Distribution | Beta testing | Android + iOS |

## Fastlane (iOS)

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Sync certificates with Match"
  lane :sync_certs do
    match(type: "appstore", readonly: true)
    match(type: "development", readonly: true)
  end

  desc "Build and deploy to TestFlight"
  lane :beta do
    sync_certs
    increment_build_number(xcodeproj: "MyApp.xcodeproj")
    build_app(
      workspace: "MyApp.xcworkspace",
      scheme: "MyApp",
      export_method: "app-store",
      clean: true
    )
    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
    slack(message: "New iOS beta uploaded to TestFlight!")
  end

  desc "Deploy to App Store"
  lane :release do
    sync_certs
    build_app(scheme: "MyApp", export_method: "app-store")
    upload_to_app_store(
      submit_for_review: true,
      automatic_release: false,
      precheck_include_in_app_purchases: false
    )
  end
end
```

## Fastlane (Android)

```ruby
# fastlane/Fastfile
platform :android do
  desc "Build and upload to Play Store internal track"
  lane :beta do
    gradle(task: "clean bundleRelease")
    upload_to_play_store(
      track: "internal",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      skip_upload_metadata: true,
      skip_upload_images: true
    )
  end

  desc "Promote internal to production"
  lane :promote do
    upload_to_play_store(
      track: "internal",
      track_promote_to: "production",
      skip_upload_aab: true,
      rollout: "0.1"
    )
  end
end
```

## EAS Build (Expo/React Native)

```json
// eas.json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" },
      "channel": "preview"
    },
    "production": {
      "autoIncrement": true,
      "channel": "production"
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "123456789",
        "appleTeamId": "TEAMID"
      },
      "android": {
        "serviceAccountKeyPath": "./google-sa.json",
        "track": "production"
      }
    }
  }
}
```

```bash
# Build
eas build --platform ios --profile production
eas build --platform android --profile production
eas build --platform all --profile preview    # Ambas plataformas

# Submit to stores
eas submit --platform ios --latest
eas submit --platform android --latest

# OTA Update (sin rebuild)
eas update --branch production --message "Fix crash on login"
```

## GitHub Actions (React Native)

```yaml
# .github/workflows/mobile-ci.yml
name: Mobile CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build-ios:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2' }
      - run: bundle install
        working-directory: ios
      - run: bundle exec fastlane ios beta
        working-directory: ios
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_TOKEN }}
          FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}

  build-android:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: |
          echo "${{ secrets.ANDROID_KEYSTORE }}" | base64 -d > android/app/release.keystore
      - run: bundle exec fastlane android beta
        working-directory: android
        env:
          PLAY_STORE_JSON_KEY: ${{ secrets.PLAY_STORE_JSON_KEY }}
```

## GitHub Actions (Flutter)

```yaml
# .github/workflows/flutter-ci.yml
name: Flutter CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.27.x' }
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test --coverage

  build-android:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.27.x' }
      - run: flutter build appbundle --release
      - uses: actions/upload-artifact@v4
        with:
          name: android-release
          path: build/app/outputs/bundle/release/

  build-ios:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.27.x' }
      - run: flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
```

## App Signing Decision Tree

```
Como firmar la app
|
+-- iOS
|   +-- Desarrollo local ---------> Automatic signing (Xcode)
|   +-- TestFlight ---------------> Distribution cert + provisioning profile
|   +-- App Store -----------------> Distribution cert + App Store profile
|   +-- CI/CD --------------------> Fastlane Match (certs en repo Git encriptado)
|   +-- Expo/EAS -----------------> EAS maneja certs automaticamente
|
+-- Android
|   +-- Debug ---------------------> debug.keystore (auto-generado)
|   +-- Release (local) ----------> upload key (.jks) + gradle signing config
|   +-- Release (CI) -------------> Keystore en base64 como GitHub Secret
|   +-- Play Store ----------------> Play App Signing (Google gestiona key de distribucion)
|   +-- Expo/EAS -----------------> EAS genera y gestiona keystores
```

## Beta Distribution Decision Tree

```
Como distribuir beta
|
+-- Internal team (< 20 personas)
|   +-- iOS --> TestFlight internal group
|   +-- Android --> Play Store internal track
|   +-- Cross --> Firebase App Distribution
|
+-- External testers (20-1000)
|   +-- iOS --> TestFlight external (requiere review)
|   +-- Android --> Play Store closed testing
|   +-- Cross --> Firebase App Distribution + grupos
|
+-- Public beta (1000+)
|   +-- iOS --> TestFlight public link (10K max)
|   +-- Android --> Play Store open testing
|
+-- Expo/React Native
|   +-- Dev builds --> EAS Build (internal distribution)
|   +-- Preview --> EAS Build preview profile
|   +-- OTA hotfix --> EAS Update (sin rebuild)
```

## Codemagic (Flutter CI/CD managed)

```yaml
# codemagic.yaml
workflows:
  flutter-release:
    name: Flutter Release
    max_build_duration: 60
    environment:
      flutter: stable
      xcode: latest
    scripts:
      - name: Tests
        script: flutter test
      - name: Build iOS
        script: flutter build ipa --release
      - name: Build Android
        script: flutter build appbundle --release
    artifacts:
      - build/ios/ipa/*.ipa
      - build/app/outputs/bundle/**/*.aab
    publishing:
      app_store_connect:
        api_key: $APP_STORE_CONNECT_PRIVATE_KEY
        key_id: $APP_STORE_CONNECT_KEY_IDENTIFIER
        issuer_id: $APP_STORE_CONNECT_ISSUER_ID
        submit_to_testflight: true
      google_play:
        credentials: $GCLOUD_SERVICE_ACCOUNT_CREDENTIALS
        track: internal
```

## Decision Tree: Que CI/CD Usar

```
¿Que framework usas?
├── Flutter → Codemagic (integrado, zero config, iOS+Android en 1 pipeline)
├── React Native + Expo → EAS Build (nativo del ecosistema Expo)
├── React Native sin Expo → Fastlane + GitHub Actions
├── Nativo (Swift/Kotlin) → Fastlane + Xcode Cloud / GitHub Actions
├── Necesito control total → Fastlane (mas flexible, mas setup)
```

## Comandos Rapidos

```bash
# Fastlane
fastlane init && fastlane match init   # Setup
fastlane ios beta                      # Build + TestFlight
fastlane android beta                  # Build + Play internal

# EAS (Expo)
eas build --platform all               # Build iOS + Android
eas submit --platform all              # Submit a stores

# Codemagic
# Configurar en codemagic.yaml y conectar repo en app.codemagic.io

# Firebase App Distribution
firebase appdistribution:distribute app-release.apk \
  --app 1:123:android:abc --groups "qa-team"

# Verificar firma
jarsigner -verify -verbose app.apk
apksigner verify --print-certs app.apk
```
