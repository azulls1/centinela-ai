# SKILL Mobile Testing

> **Version:** 3.8.0
> **Trigger:** Testing de apps moviles (React Native, Flutter, iOS, Android)
> **Agente:** nxt-mobile, nxt-qa

## Herramientas por Framework

| Framework | Unit Tests | Integration | E2E | Visual |
|-----------|-----------|-------------|-----|--------|
| React Native | Jest + RTL | Detox | Maestro | Storybook RN |
| Flutter | flutter_test | integration_test | patrol | golden tests |
| iOS Native | XCTest | XCUITest | XCUITest | snapshot testing |
| Android | JUnit + Mockk | Espresso | UI Automator | screenshot tests |

## Detox Setup (React Native)

```javascript
// e2e/firstTest.e2e.js
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  it('should login successfully', async () => {
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();
    await expect(element(by.id('home-screen'))).toBeVisible();
  });

  it('should show error on invalid credentials', async () => {
    await element(by.id('email-input')).typeText('wrong@email.com');
    await element(by.id('login-button')).tap();
    await expect(element(by.text('Invalid credentials'))).toBeVisible();
  });
});
```

## Maestro (Cross-platform, YAML)

```yaml
# .maestro/login-flow.yaml
appId: com.myapp
---
- launchApp
- tapOn: "Email"
- inputText: "test@example.com"
- tapOn: "Password"
- inputText: "password123"
- tapOn: "Login"
- assertVisible: "Welcome"
```

## Flutter Integration Test

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('login flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(Key('email')), 'test@example.com');
    await tester.enterText(find.byKey(Key('password')), 'pass123');
    await tester.tap(find.byKey(Key('login_btn')));
    await tester.pumpAndSettle();

    expect(find.text('Welcome'), findsOneWidget);
  });
}
```

## React Native Component Test (RTL)

```javascript
// __tests__/LoginScreen.test.js
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import LoginScreen from '../src/screens/LoginScreen';

test('disables button while loading', async () => {
  const { getByTestId, getByText } = render(<LoginScreen />);

  fireEvent.changeText(getByTestId('email-input'), 'user@test.com');
  fireEvent.changeText(getByTestId('password-input'), 'pass123');
  fireEvent.press(getByText('Login'));

  await waitFor(() => {
    expect(getByTestId('login-button')).toBeDisabled();
  });
});
```

## iOS Snapshot Testing (Swift)

```swift
// Tests/LoginViewSnapshotTests.swift
import XCTest
import SnapshotTesting
@testable import MyApp

final class LoginViewSnapshotTests: XCTestCase {
  func testLoginView_default() {
    let vc = LoginViewController()
    vc.loadViewIfNeeded()
    assertSnapshot(of: vc, as: .image(on: .iPhone13))
  }

  func testLoginView_withError() {
    let vc = LoginViewController()
    vc.loadViewIfNeeded()
    vc.showError("Invalid credentials")
    assertSnapshot(of: vc, as: .image(on: .iPhone13))
  }
}
```

## Decision Tree

```
Tipo de test necesario
|
+-- Logica de negocio sin UI
|   +-- React Native --> Jest + mocks
|   +-- Flutter -------> flutter_test (unit)
|   +-- iOS -----------> XCTest
|   +-- Android -------> JUnit5 + Mockk
|
+-- Componente individual
|   +-- React Native --> React Native Testing Library
|   +-- Flutter -------> Widget test (testWidgets)
|   +-- iOS -----------> XCUITest (unit scope)
|   +-- Android -------> Espresso (fragment)
|
+-- Flujo completo en simulador
|   +-- Multi-plataforma -> Maestro (YAML, rapido)
|   +-- React Native ----> Detox
|   +-- Flutter ----------> patrol / integration_test
|   +-- iOS nativo -------> XCUITest
|   +-- Android nativo ---> UI Automator 2
|
+-- Verificar que UI no cambio
|   +-- React Native --> Storybook RN + Chromatic
|   +-- Flutter -------> Golden tests (matchesGoldenFile)
|   +-- iOS -----------> swift-snapshot-testing
|   +-- Android -------> Paparazzi / Shot
|
+-- Probar en dispositivo real (cloud)
|   +-- Firebase Test Lab (Android + iOS)
|   +-- AWS Device Farm
|   +-- BrowserStack App Automate
|   +-- Sauce Labs Real Devices
```

## Comandos

```bash
# React Native + Detox
npx detox build --configuration ios.sim.debug
npx detox test --configuration ios.sim.debug
npx detox test --configuration android.emu.debug

# React Native + Jest
npx jest --coverage
npx jest --watch src/screens/

# Flutter
flutter test                              # Unit + widget tests
flutter test integration_test/            # Integration tests
flutter test --update-goldens             # Regenerar golden files

# Maestro (cualquier framework)
maestro test .maestro/login-flow.yaml
maestro test --device=ios .maestro/       # Suite completa iOS
maestro test --format junit --output report.xml .maestro/

# iOS nativo
xcodebuild test -workspace MyApp.xcworkspace \
  -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15'

# Android nativo
./gradlew testDebugUnitTest               # Unit tests
./gradlew connectedAndroidTest            # Instrumented tests
```

## Coverage Minima Recomendada

| Capa | Minimo | Ideal |
|------|--------|-------|
| Logica de negocio | 80% | 95% |
| Componentes UI | 60% | 80% |
| Navegacion/Flows | 40% | 70% |
| E2E criticos | Happy paths | Happy + error paths |

## Flutter Patrol (E2E nativo)

```dart
// integration_test/login_test.dart
import 'package:patrol/patrol.dart';

void main() {
  patrolTest('login flow works', ($) async {
    await $.pumpWidgetAndSettle(const MyApp());

    // Interactuar con widgets Flutter
    await $(#emailField).enterText('test@example.com');
    await $(#passwordField).enterText('password123');
    await $(#loginButton).tap();

    // Verificar navegacion
    expect($(#homeScreen), findsOneWidget);

    // Interactuar con elementos nativos (permisos, alerts)
    await $.native.grantPermissionWhenInUse();  // Location permission
    await $.native.tap(Selector(text: 'Allow'));  // Native alert
  });
}
```

```bash
# Ejecutar patrol tests
patrol test --target integration_test/login_test.dart
patrol test --target integration_test/ --device-id emulator-5554
```

> **Cuando usar Patrol vs integration_test:**
> - `integration_test` → Solo widgets Flutter (no puede tocar alerts nativos)
> - `patrol` → Widgets Flutter + dialogs nativos (permisos, alerts del OS)
