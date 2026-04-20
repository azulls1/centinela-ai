# SKILL Mobile Security

> **Version:** 3.8.0
> **Trigger:** Seguridad de aplicaciones moviles, auditoria MASVS, proteccion de datos en device
> **Agente:** nxt-cybersec, nxt-mobile
> **Track:** mobile

## OWASP MASVS - Mobile Application Security Verification Standard

### Niveles de Verificacion

| Nivel | Nombre | Cuando Aplicar |
|-------|--------|---------------|
| MASVS-L1 | Standard Security | Toda app que maneja datos de usuario |
| MASVS-L2 | Defense-in-Depth | Apps financieras, salud, enterprise |
| MASVS-R | Resiliency | Apps con DRM, pagos, anti-tampering |

### Categorias MASVS

| Categoria | Que Cubre |
|-----------|-----------|
| MASVS-STORAGE | Almacenamiento seguro de datos |
| MASVS-CRYPTO | Uso correcto de criptografia |
| MASVS-AUTH | Autenticacion y gestion de sesiones |
| MASVS-NETWORK | Seguridad de comunicaciones de red |
| MASVS-PLATFORM | Interaccion segura con la plataforma |
| MASVS-CODE | Calidad de codigo y protecciones |
| MASVS-RESILIENCE | Anti-tampering y anti-reversing |

## Secure Storage

### iOS - Keychain

```swift
// Swift - Guardar token en Keychain
import Security

func saveToKeychain(key: String, value: String) -> Bool {
    let data = value.data(using: .utf8)!
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    ]
    SecItemDelete(query as CFDictionary)
    return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
}

func readFromKeychain(key: String) -> String? {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecReturnData as String: true,
        kSecMatchLimit as String: kSecMatchLimitOne
    ]
    var result: AnyObject?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess, let data = result as? Data else { return nil }
    return String(data: data, encoding: .utf8)
}

func deleteFromKeychain(key: String) {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key
    ]
    SecItemDelete(query as CFDictionary)
}
```

### Android - EncryptedSharedPreferences

```kotlin
// Kotlin - Almacenamiento encriptado
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Guardar
securePrefs.edit().putString("auth_token", token).apply()

// Leer
val token = securePrefs.getString("auth_token", null)

// Borrar
securePrefs.edit().remove("auth_token").apply()
```

### React Native - react-native-keychain

```typescript
import * as Keychain from 'react-native-keychain';

// Guardar
await Keychain.setGenericPassword('auth', token, {
  accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  securityLevel: Keychain.SECURITY_LEVEL.SECURE_HARDWARE,
});

// Leer
const credentials = await Keychain.getGenericPassword();
if (credentials) {
  const token = credentials.password;
}

// Borrar
await Keychain.resetGenericPassword();
```

### Flutter - flutter_secure_storage

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.unlocked_this_device),
);

// Guardar
await storage.write(key: 'auth_token', value: token);

// Leer
final token = await storage.read(key: 'auth_token');

// Borrar
await storage.delete(key: 'auth_token');

// Borrar todo
await storage.deleteAll();
```

### Anti-patron: Almacenamiento Inseguro

```
NUNCA usar para datos sensibles:
├── AsyncStorage (React Native) - texto plano, accesible con root
├── SharedPreferences (Android) - texto plano en XML
├── UserDefaults (iOS) - plist sin encriptar
├── localStorage (WebView) - accesible via JS injection
├── SQLite sin encriptar - archivo legible con root
└── Archivos en almacenamiento externo (Android)

SIEMPRE usar:
├── iOS: Keychain Services (kSecAttrAccessibleWhenUnlockedThisDeviceOnly)
├── Android: EncryptedSharedPreferences o Android Keystore
├── React Native: react-native-keychain (usa Keychain/Keystore nativos)
└── Flutter: flutter_secure_storage (usa Keychain/EncryptedSharedPrefs)
```

## Certificate Pinning

### iOS (Native) - URLSession

```swift
class PinningDelegate: NSObject, URLSessionDelegate {
    let pinnedCertHash = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        let serverCertData = SecCertificateCopyData(certificate) as Data
        let serverHash = sha256(data: serverCertData)

        if serverHash == pinnedCertHash {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### Android - Network Security Config

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.myapp.com</domain>
        <pin-set expiration="2027-01-01">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin (OBLIGATORIO para rotacion de certificados) -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application android:networkSecurityConfig="@xml/network_security_config" />
```

### React Native - react-native-ssl-pinning o TrustKit

```typescript
// Con react-native-ssl-pinning
import { fetch as sslFetch } from 'react-native-ssl-pinning';

const response = await sslFetch('https://api.myapp.com/data', {
  method: 'GET',
  sslPinning: {
    certs: ['my_cert'],  // .cer en android/app/src/main/assets/ y iOS bundle
  },
  headers: { Authorization: `Bearer ${token}` },
});
```

### Flutter - dio + certificate pinning

```dart
// Con Dio
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:crypto/crypto.dart';

final dio = Dio();
(dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
  final client = HttpClient();
  client.badCertificateCallback = (cert, host, port) {
    final validHash = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=';
    final certHash = sha256.convert(cert.der).toString();
    return certHash == validHash;
  };
  return client;
};
```

### Pinning: Buenas Practicas

```
Certificate Pinning - Consideraciones:
├── SIEMPRE incluir pin de backup (rotacion de certificados sin deploy)
├── SIEMPRE definir fecha de expiracion del pin-set
├── NUNCA pinear el certificado leaf (cambia frecuentemente)
├── PREFERIR pinear la public key del intermediate CA
├── TENER plan de emergencia si el pin falla (kill switch remoto)
├── MONITOREAR fallos de pinning en produccion (report-uri)
└── PROBAR rotacion de certificados en staging antes de produccion
```

## Jailbreak / Root Detection

### Multi-platform con freeRASP

```yaml
# pubspec.yaml (Flutter)
dependencies:
  freerasp: ^6.0.0
```

```dart
// Flutter - freeRASP
import 'package:freerasp/freerasp.dart';

final config = TalsecConfig(
  androidConfig: AndroidConfig(
    packageName: 'com.myapp',
    signingCertHashes: ['HASH_OF_YOUR_SIGNING_CERT'],
  ),
  iosConfig: IOSConfig(
    bundleIds: ['com.myapp'],
    teamId: 'YOUR_TEAM_ID',
  ),
  watcherMail: 'security@myapp.com',
);

final callback = ThreatCallback(
  onRootDetected: () => handleThreat('rooted'),
  onDebuggerDetected: () => handleThreat('debugger'),
  onTamperDetected: () => handleThreat('tampered'),
  onHookDetected: () => handleThreat('hooked'),
  onDeviceBindingDetected: () => handleThreat('cloned'),
);

Talsec.instance.start(config, callback);

void handleThreat(String type) {
  // Opciones segun severidad:
  // 1. Log + continuar (informativo)
  // 2. Deshabilitar features sensibles
  // 3. Forzar logout y borrar datos locales
  // 4. Bloquear la app completamente
  logSecurityEvent(type);
  disableSensitiveFeatures();
}
```

### React Native - jail-monkey

```typescript
import JailMonkey from 'jail-monkey';

function performSecurityChecks(): SecurityReport {
  return {
    isJailbroken: JailMonkey.isJailBroken(),
    isDebugged: JailMonkey.isDebuggedMode(),
    canMockLocation: JailMonkey.canMockLocation(),
    isOnExternalStorage: JailMonkey.isOnExternalStorage(), // Android only
    hookDetected: JailMonkey.hookDetected(),
  };
}

const report = performSecurityChecks();

if (report.isJailbroken) {
  // Device is jailbroken/rooted
  showSecurityWarning();
  disableSensitiveFeatures();
}

if (report.isDebugged) {
  // App is being debugged
  logSecurityEvent('debugger_detected');
}
```

### iOS (Native)

```swift
func isJailbroken() -> Bool {
    #if targetEnvironment(simulator)
    return false
    #else
    // 1. Verificar paths sospechosos
    let paths = [
        "/Applications/Cydia.app",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/bin/bash", "/usr/sbin/sshd", "/etc/apt",
        "/private/var/lib/apt/"
    ]
    for path in paths {
        if FileManager.default.fileExists(atPath: path) { return true }
    }

    // 2. Verificar si se puede escribir fuera del sandbox
    let testPath = "/private/jailbreak_test.txt"
    do {
        try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
        try FileManager.default.removeItem(atPath: testPath)
        return true
    } catch { }

    // 3. Verificar si se pueden abrir URLs de Cydia
    if let url = URL(string: "cydia://package/com.example.package") {
        if UIApplication.shared.canOpenURL(url) { return true }
    }

    // 4. Verificar integridad del sandbox
    let stringToWrite = "Jailbreak Test"
    do {
        try stringToWrite.write(toFile: "/private/jailbreak.txt",
                                atomically: true, encoding: .utf8)
        return true
    } catch { }

    return false
    #endif
}
```

### Android (Native) - Kotlin

```kotlin
fun isRooted(context: Context): Boolean {
    // 1. Verificar binarios de su
    val suPaths = arrayOf(
        "/system/app/Superuser.apk", "/sbin/su",
        "/system/bin/su", "/system/xbin/su",
        "/data/local/xbin/su", "/data/local/bin/su",
        "/system/sd/xbin/su", "/system/bin/failsafe/su",
        "/data/local/su"
    )
    for (path in suPaths) {
        if (File(path).exists()) return true
    }

    // 2. Verificar si se puede ejecutar su
    try {
        Runtime.getRuntime().exec("su")
        return true
    } catch (e: Exception) { }

    // 3. Verificar build tags
    val buildTags = android.os.Build.TAGS
    if (buildTags != null && buildTags.contains("test-keys")) return true

    // 4. Verificar apps de root management
    val rootApps = arrayOf(
        "com.topjohnwu.magisk", "eu.chainfire.supersu",
        "com.koushikdutta.superuser"
    )
    for (pkg in rootApps) {
        try {
            context.packageManager.getPackageInfo(pkg, 0)
            return true
        } catch (e: Exception) { }
    }

    return false
}
```

## API Key Protection

```
REGLAS CRITICAS:
├── NUNCA hardcodear API keys en el codigo fuente
├── NUNCA incluir keys en el bundle/binary
├── NUNCA commitear keys a git
├── SIEMPRE usar variables de entorno o config remota
├── SIEMPRE validar keys del lado del servidor
└── CONSIDERAR App Attest (iOS) / Play Integrity (Android)
```

### React Native - react-native-config

```bash
# .env (gitignored)
API_URL=https://api.myapp.com
API_KEY=sk_live_xxxxx
```

```typescript
import Config from 'react-native-config';

// Inyectado en build time, NO visible en el bundle JS
const apiUrl = Config.API_URL;
```

### Flutter - --dart-define

```bash
# Build con variables de entorno
flutter run --dart-define=API_KEY=sk_live_xxxxx
flutter build apk --dart-define=API_KEY=sk_live_xxxxx
flutter build ipa --dart-define=API_KEY=sk_live_xxxxx
```

```dart
// Acceder en el codigo
const apiKey = String.fromEnvironment('API_KEY');
```

### iOS (Native) - xcconfig

```bash
# Config/Debug.xcconfig (gitignored)
API_KEY = sk_live_xxxxx

# Config/Release.xcconfig (gitignored)
API_KEY = sk_live_yyyyy
```

```swift
// Info.plist
// <key>API_KEY</key>
// <string>$(API_KEY)</string>

// Acceder en codigo
let apiKey = Bundle.main.infoDictionary?["API_KEY"] as? String ?? ""
```

### Android (Native) - local.properties + BuildConfig

```properties
# local.properties (gitignored)
API_KEY=sk_live_xxxxx
```

```groovy
// build.gradle
def localProperties = new Properties()
localProperties.load(new FileInputStream(rootProject.file("local.properties")))

android {
    defaultConfig {
        buildConfigField "String", "API_KEY", "\"${localProperties['API_KEY']}\""
    }
}
```

```kotlin
// Acceder en codigo
val apiKey = BuildConfig.API_KEY
```

### Server-side validation (SIEMPRE como capa adicional)

```
ARQUITECTURA RECOMENDADA:

App --> Server (con app attest/play integrity token) --> Server valida --> Server llama API con key real
                                                                             |
                                                             La key NUNCA esta en el device

FLUJO:
1. App solicita attest token del OS (App Attest iOS / Play Integrity Android)
2. App envia request al backend con el attest token
3. Backend valida el attest token contra Apple/Google
4. Backend realiza la llamada a la API externa con la key real
5. Backend retorna resultado a la app

BENEFICIO: Incluso si el APK/IPA es decompilado, no hay keys que robar
```

## Code Obfuscation

### Android - ProGuard/R8 (build.gradle)

```groovy
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

```
# proguard-rules.pro - Reglas importantes
-keepattributes SourceFile,LineNumberTable  # Para crash reports legibles
-renamesourcefileattribute SourceFile

# Mantener modelos de datos (si usan reflection/serialization)
-keep class com.myapp.models.** { *; }

# Mantener clases de Retrofit/Gson si se usan
-keepclassmembers class * { @com.google.gson.annotations.SerializedName <fields>; }
```

### iOS - Swift Compilation

```
Swift ya compila a codigo nativo (no bytecode), lo que dificulta la ingenieria inversa.
Medidas adicionales:
├── Activar Bitcode en Xcode (si el target lo soporta)
├── Strip Debug Symbols en Release
├── Usar @inline(__always) para funciones criticas de seguridad
└── Considerar herramientas de terceros (iXGuard, Arxan)
```

### Flutter

```bash
# Obfuscation nativa de Flutter
flutter build apk --obfuscate --split-debug-info=build/debug-info/
flutter build ipa --obfuscate --split-debug-info=build/debug-info/

# IMPORTANTE: Guardar build/debug-info/ para poder symbolicate crash reports
# Subir a Firebase Crashlytics o Sentry para traducir stack traces
```

### React Native - Hermes bytecode

```json
// app.json (Expo) - Hermes compila a bytecode (no JS legible)
{
  "expo": {
    "jsEngine": "hermes"
  }
}
```

```javascript
// react-native.config.js (bare React Native)
module.exports = {
  // Hermes esta activo por defecto en RN 0.70+
  // Verificar en android/app/build.gradle:
  // hermesEnabled: true
};
```

```
Verificar que Hermes esta activo:
├── El bundle debe ser bytecode (binario), NO texto JS legible
├── Descomprimir APK y verificar: file assets/index.android.bundle
│   ├── Correcto: "data" (bytecode Hermes)
│   └── PROBLEMA: "ASCII text" (JavaScript legible)
└── En iOS: verificar que el .jsbundle no es texto plano
```

## Biometric Authentication

### React Native - expo-local-authentication

```typescript
import * as LocalAuthentication from 'expo-local-authentication';

async function authenticate(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();

  if (!hasHardware || !isEnrolled) {
    return fallbackToPin();
  }

  const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();
  // FINGERPRINT = 1, FACIAL_RECOGNITION = 2, IRIS = 3

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Confirma tu identidad',
    cancelLabel: 'Cancelar',
    disableDeviceFallback: false,
    fallbackLabel: 'Usar PIN',
  });

  return result.success;
}
```

### Flutter - local_auth

```dart
import 'package:local_auth/local_auth.dart';

final auth = LocalAuthentication();

Future<bool> authenticate() async {
  final canAuth = await auth.canCheckBiometrics || await auth.isDeviceSupported();
  if (!canAuth) return false;

  final availableBiometrics = await auth.getAvailableBiometrics();
  // BiometricType.fingerprint, BiometricType.face, BiometricType.iris

  return await auth.authenticate(
    localizedReason: 'Confirma tu identidad',
    options: const AuthenticationOptions(
      stickyAuth: true,        // No cancelar si la app va a background
      biometricOnly: false,    // Permitir fallback a PIN/pattern
      useErrorDialogs: true,
    ),
  );
}
```

### iOS (Native) - LocalAuthentication

```swift
import LocalAuthentication

func authenticateWithBiometrics(completion: @escaping (Bool, Error?) -> Void) {
    let context = LAContext()
    context.localizedCancelTitle = "Cancelar"
    context.localizedFallbackTitle = "Usar PIN"

    var error: NSError?
    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
        completion(false, error)
        return
    }

    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                           localizedReason: "Confirma tu identidad") { success, error in
        DispatchQueue.main.async {
            completion(success, error)
        }
    }
}
```

### Android (Native) - BiometricPrompt

```kotlin
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat

fun showBiometricPrompt(activity: FragmentActivity, onSuccess: () -> Unit) {
    val executor = ContextCompat.getMainExecutor(activity)

    val callback = object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            onSuccess()
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            // Manejar error (usuario cancelo, lockout, etc.)
        }

        override fun onAuthenticationFailed() {
            // Biometrico no reconocido (intentar de nuevo)
        }
    }

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Autenticacion requerida")
        .setSubtitle("Confirma tu identidad")
        .setAllowedAuthenticators(
            BiometricPrompt.Authenticators.BIOMETRIC_STRONG or
            BiometricPrompt.Authenticators.DEVICE_CREDENTIAL
        )
        .build()

    BiometricPrompt(activity, executor, callback).authenticate(promptInfo)
}
```

## Secure Network Communication

### Request Signing

```typescript
// React Native / TypeScript - HMAC request signing
import CryptoJS from 'crypto-js';

function signRequest(method: string, path: string, body: object, secret: string): string {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const payload = `${method}|${path}|${JSON.stringify(body)}|${timestamp}`;
  const signature = CryptoJS.HmacSHA256(payload, secret).toString(CryptoJS.enc.Hex);

  return signature;
}

// Uso en interceptor de Axios
axios.interceptors.request.use((config) => {
  const signature = signRequest(
    config.method!.toUpperCase(),
    config.url!,
    config.data || {},
    deviceSecret
  );
  config.headers['X-Signature'] = signature;
  config.headers['X-Timestamp'] = Math.floor(Date.now() / 1000).toString();
  return config;
});
```

### Prevent Man-in-the-Middle

```
Checklist de seguridad de red:
├── HTTPS obligatorio en toda comunicacion (no HTTP)
├── Certificate pinning en endpoints criticos
├── HSTS headers en el servidor
├── TLS 1.2 minimo (preferir TLS 1.3)
├── No aceptar certificados self-signed en produccion
├── Request signing con HMAC para APIs criticas
├── Rate limiting del lado del servidor
├── Tokens con expiracion corta (15 min access, 7 dias refresh)
└── Mutual TLS (mTLS) para apps enterprise
```

## Data Leak Prevention

### Prevenir Screenshots y Screen Recording

```swift
// iOS - Prevenir capturas de pantalla en vistas sensibles
class SecureViewController: UIViewController {
    private var secureField: UITextField?

    override func viewDidLoad() {
        super.viewDidLoad()
        makeSecure()
    }

    private func makeSecure() {
        let field = UITextField()
        field.isSecureTextEntry = true
        self.view.addSubview(field)
        field.centerYAnchor.constraint(equalTo: view.centerYAnchor).isActive = true
        field.centerXAnchor.constraint(equalTo: view.centerXAnchor).isActive = true
        self.view.layer.superlayer?.addSublayer(field.layer)
        field.layer.sublayers?.first?.addSublayer(self.view.layer)
        secureField = field
    }
}
```

```kotlin
// Android - FLAG_SECURE para prevenir screenshots
window.setFlags(
    WindowManager.LayoutParams.FLAG_SECURE,
    WindowManager.LayoutParams.FLAG_SECURE
)
```

```typescript
// React Native - react-native-prevent-screenshot
import RNPreventScreenshot from 'react-native-prevent-screenshot';

// Activar proteccion
RNPreventScreenshot.enabled(true);

// Desactivar cuando no es necesario
RNPreventScreenshot.enabled(false);
```

### Limpiar Datos en Background

```swift
// iOS - Ocultar contenido sensible cuando la app va a background
func applicationDidEnterBackground(_ application: UIApplication) {
    let blurEffect = UIBlurEffect(style: .light)
    let blurView = UIVisualEffectView(effect: blurEffect)
    blurView.frame = window?.frame ?? .zero
    blurView.tag = 999
    window?.addSubview(blurView)
}

func applicationWillEnterForeground(_ application: UIApplication) {
    window?.viewWithTag(999)?.removeFromSuperview()
}
```

### Prevenir Data Leaks via Logs

```
REGLA: NUNCA loggear datos sensibles

Datos que NUNCA deben aparecer en logs:
├── Tokens de autenticacion (JWT, refresh tokens)
├── Passwords o PINs
├── Datos de tarjetas de credito
├── Numeros de seguro social / identificacion
├── Datos biometricos
├── API keys o secrets
├── PII (Personally Identifiable Information)
└── PHI (Protected Health Information)
```

```typescript
// React Native - Deshabilitar logs en produccion
if (!__DEV__) {
  console.log = () => {};
  console.warn = () => {};
  console.error = () => {};
  console.debug = () => {};
  console.info = () => {};
}
```

```dart
// Flutter - Solo loggear en debug
import 'package:flutter/foundation.dart';

void secureLog(String message) {
  if (kDebugMode) {
    debugPrint(message);
  }
}
```

## Session Management

### Secure Token Handling

```typescript
// Patron recomendado para manejo de tokens (React Native / TypeScript)
class SecureTokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private static readonly TOKEN_EXPIRY_KEY = 'token_expiry';

  static async saveTokens(accessToken: string, refreshToken: string, expiresIn: number) {
    const expiry = Date.now() + expiresIn * 1000;
    await Keychain.setGenericPassword(
      this.ACCESS_TOKEN_KEY,
      JSON.stringify({ accessToken, refreshToken, expiry }),
      { accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY }
    );
  }

  static async getAccessToken(): Promise<string | null> {
    const credentials = await Keychain.getGenericPassword();
    if (!credentials) return null;

    const { accessToken, refreshToken, expiry } = JSON.parse(credentials.password);

    // Token expirado? Refrescar
    if (Date.now() >= expiry) {
      return this.refreshAccessToken(refreshToken);
    }

    return accessToken;
  }

  static async logout() {
    // Limpiar TODOS los datos sensibles del device
    await Keychain.resetGenericPassword();
    await AsyncStorage.clear(); // Limpiar datos no sensibles tambien
    // Revocar tokens en el servidor
    await api.post('/auth/revoke');
  }

  private static async refreshAccessToken(refreshToken: string): Promise<string | null> {
    try {
      const response = await api.post('/auth/refresh', { refreshToken });
      await this.saveTokens(
        response.data.accessToken,
        response.data.refreshToken,
        response.data.expiresIn
      );
      return response.data.accessToken;
    } catch {
      await this.logout(); // Refresh fallo, forzar re-login
      return null;
    }
  }
}
```

### Session Timeout

```
Recomendaciones de timeout por tipo de app:
├── App general: 30 min inactivity, 24h absolute
├── App financiera: 5 min inactivity, 15 min absolute
├── App salud (HIPAA): 15 min inactivity, 8h absolute
├── App enterprise: Configurable por politica IT
└── App con biometrics: Re-autenticar en cada apertura desde background > 5 min
```

## Decision Tree: Nivel de Seguridad por Tipo de App

```
Tipo de app
├── App informativa / contenido publico
│   └── MASVS-L1 basico: HTTPS, no hardcode keys, secure storage para tokens
│
├── App con login y datos de usuario
│   └── MASVS-L1 completo: + cert pinning, biometric auth, session management
│
├── App financiera / pagos / salud
│   └── MASVS-L2: + jailbreak detection, obfuscation, anti-debugging, audit trail
│
├── App con DRM / contenido premium / juego con economia
│   └── MASVS-L2 + R: + anti-tampering, RASP, integrity checks
│
├── App enterprise / gobierno / military
│   └── MASVS-L2 + R + auditoria externa + penetration testing
```

## Security Audit Checklist Pre-Release

```
MASVS-STORAGE:
[ ] Datos sensibles NO en logs (console.log, print, NSLog)
[ ] Tokens en secure storage (Keychain/EncryptedSharedPrefs), NO en AsyncStorage/SharedPrefs
[ ] Backups excluyen datos sensibles (android:allowBackup="false" o exclude rules)
[ ] Clipboard limpio despues de pegar datos sensibles
[ ] Keyboard cache deshabilitado en campos sensibles (secureTextEntry)
[ ] Datos sensibles ocultos cuando la app va a background (blur/overlay)

MASVS-CRYPTO:
[ ] No se usan algoritmos deprecados (MD5, SHA1, DES, RC4)
[ ] Keys generadas con random seguro (SecRandomCopyBytes, SecureRandom)
[ ] No se reusan IVs/nonces en encriptacion
[ ] Keys almacenadas en Keystore/Keychain, no hardcodeadas

MASVS-NETWORK:
[ ] Todo el trafico es HTTPS (no HTTP)
[ ] Certificate pinning implementado para APIs criticas
[ ] No se aceptan certificados invalidos/self-signed en produccion
[ ] TLS 1.2 minimo configurado
[ ] cleartextTrafficPermitted="false" en Android

MASVS-AUTH:
[ ] Tokens tienen expiracion y refresh
[ ] Biometric auth disponible para operaciones sensibles
[ ] Session timeout implementado (inactivity + absolute)
[ ] Logout limpia TODOS los datos sensibles del device
[ ] Re-autenticacion para operaciones criticas (cambiar password, pagos)

MASVS-CODE:
[ ] Sin API keys hardcodeadas en el codigo
[ ] Obfuscation activa en release builds
[ ] Debug mode deshabilitado en release
[ ] Sin console.log/print en release
[ ] ProGuard/R8 activo (Android)
[ ] Hermes bytecode activo (React Native)
[ ] --obfuscate flag usado (Flutter)

MASVS-PLATFORM:
[ ] Deep links validados (no open redirect)
[ ] WebViews con JavaScript deshabilitado si no es necesario
[ ] Permisos minimos necesarios declarados
[ ] Export compliance configurado (iOS)
[ ] Intent filters restrictivos (Android)
[ ] Universal Links con apple-app-site-association correcto (iOS)

MASVS-RESILIENCE (si L2/R):
[ ] Jailbreak/root detection activo
[ ] Anti-debugging implementado
[ ] Integrity verification del binary
[ ] Anti-hook detection
[ ] Emulator detection
[ ] Screenshot prevention en vistas sensibles
[ ] RASP (Runtime Application Self-Protection) activo
```

## Comandos de Auditoria

```bash
# MobSF - Analisis estatico automatico (open source)
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf
# Subir APK/IPA a http://localhost:8000

# Android - Verificar permisos excesivos
aapt dump permissions app-release.apk

# Android - Buscar strings sensibles en APK
apktool d app-release.apk -o decompiled/
grep -r "api_key\|password\|secret\|token" decompiled/

# Android - Verificar que no hay cleartext traffic
grep -r "cleartextTrafficPermitted" decompiled/AndroidManifest.xml

# Android - Verificar ProGuard activo
unzip -l app-release.apk | grep "classes.dex"
# Si las clases estan ofuscadas, jadx mostrara nombres como a.b.c

# iOS - Verificar entitlements
codesign -d --entitlements :- MyApp.app

# iOS - Verificar que no hay strings sensibles
strings MyApp.app/MyApp | grep -i "api_key\|password\|secret"

# React Native - Verificar que Hermes esta activo (bytecode, no JS legible)
unzip app-release.apk -d extracted/
file extracted/assets/index.android.bundle
# Debe decir "data" (bytecode), NO "ASCII text" (JS legible)

# Flutter - Verificar obfuscation
# Si se uso --obfuscate, los symbols no seran legibles
# Verificar que build/debug-info/ existe (para crash reports)

# Dependency audit
# React Native
npx audit-ci --moderate
npm audit --production

# Flutter
flutter pub outdated
dart pub audit

# Buscar vulnerabilidades conocidas en dependencias nativas
# Android: dependencyCheck gradle plugin
# iOS: pod audit (si se usa CocoaPods)
```

## Herramientas Recomendadas

| Herramienta | Tipo | Plataforma | Uso |
|-------------|------|------------|-----|
| MobSF | SAST + DAST | Android, iOS | Analisis estatico y dinamico automatizado |
| Frida | Dynamic Analysis | Android, iOS | Instrumentacion runtime, testing de seguridad |
| objection | Runtime Exploration | Android, iOS | Bypass SSL pinning, jailbreak detection (testing) |
| apktool | Reverse Engineering | Android | Decompilacion de APK para auditoria |
| jadx | Decompiler | Android | Leer codigo Java/Kotlin decompilado |
| Hopper/Ghidra | Disassembler | iOS | Analisis de binarios iOS |
| Burp Suite | Proxy | Ambas | Interceptar trafico HTTPS para testing |
| nuclei | Vulnerability Scanner | Backend | Escanear APIs que consume la app |
| semgrep | SAST | Codigo fuente | Buscar patrones inseguros en el codigo |

## Referencias

- OWASP MASVS: https://mas.owasp.org/MASVS/
- OWASP MASTG (Mobile Application Security Testing Guide): https://mas.owasp.org/MASTG/
- OWASP Mobile Top 10: https://owasp.org/www-project-mobile-top-10/
- Apple App Security: https://developer.apple.com/documentation/security
- Android Security Best Practices: https://developer.android.com/privacy-and-security/security-tips
