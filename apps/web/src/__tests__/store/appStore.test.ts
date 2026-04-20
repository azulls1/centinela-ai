import { describe, it, expect, beforeEach } from 'vitest'
import { useAppStore } from '../../store/appStore'

describe('appStore', () => {
  beforeEach(() => {
    useAppStore.setState(useAppStore.getInitialState())
  })

  it('has correct initial config defaults', () => {
    const state = useAppStore.getState()
    expect(state.config.personDetection.enabled).toBe(true)
    expect(state.config.faceDetection.enabled).toBe(true)
    expect(state.config.objectDetection.enabled).toBe(true)
    expect(state.config.cameraResolution).toBe('medium')
  })

  it('updates config correctly', () => {
    const { updateConfig } = useAppStore.getState()
    updateConfig({ anonymizeData: true })
    expect(useAppStore.getState().config.anonymizeData).toBe(true)
  })

  it('accepts privacy', () => {
    const { setPrivacyAccepted } = useAppStore.getState()
    expect(useAppStore.getState().privacyAccepted).toBe(false)
    setPrivacyAccepted(true)
    expect(useAppStore.getState().privacyAccepted).toBe(true)
  })

  it('activates and deactivates cameras', () => {
    const state = useAppStore.getState()
    state.setAvailableDevices([{ deviceId: 'test-device', label: 'Test Camera', groupId: '' }])
    const cameraId = useAppStore.getState().activateCamera('test-device')
    expect(cameraId).toBeTruthy()
    expect(useAppStore.getState().activeCameraIds).toContain(cameraId)

    if (cameraId) {
      useAppStore.getState().deactivateCamera(cameraId)
      expect(useAppStore.getState().activeCameraIds).not.toContain(cameraId)
    }
  })

  it('sets performance preset', () => {
    const { setPerformancePreset } = useAppStore.getState()
    setPerformancePreset('performance')
    expect(useAppStore.getState().performancePreset).toBe('performance')
  })
})
