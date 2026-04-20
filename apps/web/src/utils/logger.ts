/**
 * Utilidades de logging seguras para el navegador.
 * En producción no se emiten mensajes a la consola para evitar filtraciones.
 */

const isDevEnvironment = typeof import.meta !== 'undefined' && import.meta.env?.DEV

export function logDebug(message: string, ...optionalParams: unknown[]): void {
  if (isDevEnvironment) {
    console.debug(message, ...optionalParams)
  }
}

export function logInfo(message: string, ...optionalParams: unknown[]): void {
  if (isDevEnvironment) {
    console.info(message, ...optionalParams)
  }
}

export function logWarn(message: string, ...optionalParams: unknown[]): void {
  if (isDevEnvironment) {
    console.warn(message, ...optionalParams)
  }
}

export function logError(message: string, ...optionalParams: unknown[]): void {
  if (isDevEnvironment) {
    console.error(message, ...optionalParams)
  }
}

