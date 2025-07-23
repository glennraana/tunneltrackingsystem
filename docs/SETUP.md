# 🛠️ Setup og Installasjon - Tunnel Tracking System

Dette dokumentet viser deg hvordan du setter opp hele Tunnel Tracking System fra bunnen av.

## 🔥 Firebase Setup

### 1. Opprett Firebase Prosjekt

1. Gå til [Firebase Console](https://console.firebase.google.com/)
2. Klikk "Create a project" eller "Legg til prosjekt"
3. Gi prosjektet navnet: `tunnel-tracking-system`
4. Aktiver Google Analytics (valgfritt)
5. Velg standardregion: `europe-west` (for Norge)

### 2. Aktiver Firebase Tjenester

#### Authentication
```bash
# I Firebase Console:
1. Gå til Authentication > Sign-in method
2. Aktiver "Anonymous" authentication
3. Legg til admin-brukere ved behov
```

#### Firestore Database
```bash
# I Firebase Console:
1. Gå til Firestore Database
2. Klikk "Create database"
3. Velg "Start in test mode" (vi setter security rules senere)
4. Velg region: europe-west1 (eller nærmeste)
```

#### Cloud Functions
```bash
# I Firebase Console:
1. Gå til Functions
2. Klikk "Get started"
3. Oppgrader til Blaze plan (kreves for outbound networking)
```

### 3. Firebase CLI Installasjon

```bash
# Installer Firebase CLI (anbefalt metode for macOS)
brew install firebase-cli

# Alternativt med npm (kan kreve sudo på noen systemer)
# npm install -g firebase-tools

# Logg inn
firebase login

# Velg prosjekt
firebase use --add
# Velg tunnel-tracking-system og gi det alias "default"
```

### 4. Firebase Konfigurasjon

Kopier Firebase config fra Firebase Console:

#### For Mobile App (`mobile_app/lib/firebase_options.dart`):
```dart
import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for platform - '
          'only Android, iOS and Web are supported.'
        );
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'DIN_WEB_API_KEY',
    authDomain: 'tunnel-tracking-system.firebaseapp.com',
    projectId: 'tunnel-tracking-system',
    storageBucket: 'tunnel-tracking-system.appspot.com',
    messagingSenderId: '123456789',
    appId: 'DIN_WEB_APP_ID',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'DIN_ANDROID_API_KEY',
    appId: 'DIN_ANDROID_APP_ID',
    messagingSenderId: '123456789',
    projectId: 'tunnel-tracking-system',
    storageBucket: 'tunnel-tracking-system.appspot.com',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'DIN_IOS_API_KEY',
    appId: 'DIN_IOS_APP_ID',
    messagingSenderId: '123456789',
    projectId: 'tunnel-tracking-system',
    storageBucket: 'tunnel-tracking-system.appspot.com',
    iosBundleId: 'com.example.tunnelTracker',
  );
}
```

## 📱 Mobile App Setup

### 1. Flutter Installasjon

```bash
# Installer Flutter (hvis ikke allerede installert)
# Følg instruksjoner på https://flutter.dev/docs/get-started/install

# Verifiser installasjon
flutter doctor
```

### 2. Bygg Mobile App

```bash
cd mobile_app

# Installer dependencies
flutter pub get

# For Android
flutter build apk --release

# For iOS (krever macOS og Xcode)
flutter build ios --release

# For testing i emulator
flutter run
```

### 3. Firebase App Configuration

#### Android (`mobile_app/android/app/google-services.json`):
Last ned fra Firebase Console > Project Settings > Your apps > Android app

#### iOS (`mobile_app/ios/Runner/GoogleService-Info.plist`):
Last ned fra Firebase Console > Project Settings > Your apps > iOS app

## 🖥️ Admin Dashboard Setup

### 1. Flutter Web Dependencies

```bash
cd admin_dashboard

# Installer dependencies
flutter pub get

# Bygg for web
flutter build web --release

# For utvikling
flutter run -d chrome
```

### 2. Web Hosting Setup

```bash
# I firebase_config/ mappen
cd ../firebase_config

# Deploy til Firebase Hosting
firebase deploy --only hosting
```

## ☁️ Cloud Functions Setup

### 1. Installer Dependencies

```bash
cd cloud_functions

# Installer npm packages
npm install

# Bygg TypeScript
npm run build
```

### 2. Deploy Functions

```bash
# Deploy alle functions
firebase deploy --only functions

# Deploy spesifikk function
firebase deploy --only functions:api
```

### 3. Test API Endpoints

```bash
# Test health endpoint
curl https://YOUR_REGION-tunnel-tracking-system.cloudfunctions.net/api/health

# Test node logging (erstatt URL med din egen)
curl -X POST https://YOUR_REGION-tunnel-tracking-system.cloudfunctions.net/api/log-position \
  -H "Content-Type: application/json" \
  -d '{
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "node_id": "node_001",
    "timestamp": "2024-01-15T10:30:00Z",
    "signal_strength": -45
  }'
```

## 🔐 Security Rules Setup

### 1. Deploy Firestore Rules

```bash
cd firebase_config

# Deploy security rules
firebase deploy --only firestore:rules

# Deploy indexes
firebase deploy --only firestore:indexes
```

### 2. Admin Bruker Setup

```javascript
// Kjør i Firebase Console > Functions > Shell eller lage egen function
const admin = require('firebase-admin');

// Gi admin claims til en bruker
admin.auth().setCustomUserClaims('USER_UID', { admin: true })
  .then(() => console.log('Admin claims set'))
  .catch(console.error);
```

## 📊 Database Initialisering

### 1. Opprett Initial Data

```javascript
// Sample nodes - kjør i Firestore Console eller function
const sampleNodes = [
  {
    node_id: 'entrance_01',
    name: 'Hovedinngang',
    location: { x: 100, y: 200 },
    active_status: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    node_id: 'section_a1',
    name: 'Seksjon A1',
    location: { x: 300, y: 200 },
    active_status: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    node_id: 'exit_01',
    name: 'Utgang Nord',
    location: { x: 500, y: 200 },
    active_status: true,
    created_at: new Date(),
    updated_at: new Date()
  }
];

// Legg til i Firestore 'nodes' collection
```

## 🚀 Deployment

### 1. Full Deploy

```bash
# Fra root directory
cd firebase_config

# Deploy alt
firebase deploy

# Eller deploy komponenter separat
firebase deploy --only firestore:rules,firestore:indexes
firebase deploy --only functions
firebase deploy --only hosting
```

### 2. CI/CD Setup (GitHub Actions)

Opprett `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Firebase
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
          
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.13.x'
          
      - name: Install dependencies
        run: |
          cd cloud_functions && npm install
          cd ../admin_dashboard && flutter pub get
          
      - name: Build admin dashboard
        run: |
          cd admin_dashboard
          flutter build web --release
          
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          projectId: tunnel-tracking-system
```

## 🔧 Konfigurering for Produksjon

### 1. Environment Variables

Opprett `.env` filer for ulike miljøer:

```bash
# cloud_functions/.env.production
FIREBASE_PROJECT_ID=tunnel-tracking-system
CORS_ORIGIN=https://tunnel-admin.web.app
MAX_POSITIONS_PER_MAC=1000
CLEANUP_RETENTION_DAYS=30
```

### 2. Performance Optimizing

#### Firestore Indexes
```bash
# Optimaliser indexes i firebase_config/firestore.indexes.json
# Deploy med:
firebase deploy --only firestore:indexes
```

#### Function Memory og Timeout
```javascript
// I cloud_functions/src/index.ts
export const api = functions
  .runWith({
    memory: '256MB',
    timeoutSeconds: 60
  })
  .https.onRequest(app);
```

## 🧪 Testing

### 1. Emulator Testing

```bash
cd firebase_config

# Start emulators
firebase emulators:start

# Test med emulator
export FIREBASE_AUTH_EMULATOR_HOST="localhost:9099"
export FIRESTORE_EMULATOR_HOST="localhost:8080"

# Kjør app mot emulator
cd ../mobile_app
flutter run --debug
```

### 2. End-to-End Testing

```bash
# Test full workflow:
1. Registrer bruker i mobile app
2. Send node log via curl/Postman
3. Verifiser data i admin dashboard
4. Test unauthorized MAC detection
5. Verifiser alerts
```

## 📋 Maintenance

### 1. Monitoring

- Sett opp Firebase Performance Monitoring
- Aktiver Crashlytics for mobile app  
- Overvåk Cloud Functions logs
- Sett opp billing alerts

### 2. Backup

```bash
# Automatisk Firestore backup (sett opp i Firebase Console)
# Eller manuell export:
gcloud firestore export gs://YOUR-BUCKET/backups/$(date +%Y%m%d_%H%M%S)/
```

### 3. Updates

```bash
# Oppdater Flutter dependencies
flutter pub upgrade

# Oppdater Firebase libraries  
firebase tools:update

# Oppdater Cloud Functions dependencies
cd cloud_functions && npm update
```

## 🚨 Troubleshooting

### Vanlige Problemer

1. **CORS errors**: Sjekk Firebase Functions cors config
2. **Permission denied**: Verifiser Firestore security rules
3. **MAC detection fails**: Sjekk device permissions på mobile
4. **Functions timeout**: Øk timeout i function config
5. **Build failures**: Sjekk Flutter/Firebase SDK versjoner

### Debug Tips

```bash
# Firebase Functions logs
firebase functions:log

# Flutter verbose logging
flutter run --verbose

# Test specific function locally
cd cloud_functions && npm run serve
```

## 📞 Support

For teknisk support eller spørsmål:
- Sjekk Firebase dokumentasjon
- Flutter community på Discord/Reddit
- Internal dev team på Slack/Teams

---

**Lykke til med Tunnel Tracking System! 🚇✨** 