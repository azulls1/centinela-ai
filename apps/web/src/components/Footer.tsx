export function Footer() {
  return (
    <footer id="footer" className="mt-auto py-8 border-t border-gray-200 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">
        {/* Brand header */}
        <div className="flex items-center gap-3 mb-6">
          <img
            src="/images/logo-iagentek.webp"
            alt="IAGENTEK"
            className="h-8 w-auto brightness-0"
          />
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold text-forest font-display">Vision Human Insight</span>
            <span className="text-xs text-moss">Plataforma de IA con visión por computadora</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <h6 className="uppercase text-forest font-semibold mb-3 text-xs tracking-wider">Protección y Sensibilidad</h6>
            <p className="text-moss text-sm mb-2">
              Vision Human Insight procesa vídeo en el navegador del usuario. No almacenamos ni enviamos imágenes sin consentimiento explícito.
            </p>
            <p className="text-moss text-sm mb-0">
              El rendimiento y la precisión dependen directamente de la calidad de la cámara, iluminación adecuada y estabilidad del dispositivo.
            </p>
          </div>

          <div>
            <h6 className="uppercase text-forest font-semibold mb-3 text-xs tracking-wider">Tecnologías Principales</h6>
            <ul className="list-none text-moss text-sm mb-0">
              <li className="mb-2">React + Vite + TypeScript</li>
              <li className="mb-2">TensorFlow.js (COCO-SSD), MediaPipe Face &amp; Pose, clasificadores de emociones</li>
              <li className="mb-2">Machine learning en tiempo real con IA generativa</li>
              <li className="mb-2">Forest Design System + Tailwind CSS v4</li>
              <li className="mb-2">Zustand para estado global, Supabase para eventos</li>
              <li>Web APIs: WebRTC, Canvas, requestIdleCallback</li>
            </ul>
          </div>

          <div>
            <h6 className="uppercase text-forest font-semibold mb-3 text-xs tracking-wider">Políticas y Cumplimiento</h6>
            <ul className="list-none text-moss text-sm mb-0">
              <li className="mb-2">
                <a href="#politica-privacidad" className="text-pine hover:text-forest underline-offset-2">
                  Política de privacidad &amp; consentimiento
                </a>
              </li>
              <li className="mb-2">
                <a href="#politica-seguridad" className="text-pine hover:text-forest underline-offset-2">
                  Seguridad de datos biométricos
                </a>
              </li>
              <li>
                <a href="#politica-uso" className="text-pine hover:text-forest underline-offset-2">
                  Uso responsable de IA y sensibilidad
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h6 className="uppercase text-forest font-semibold mb-3 text-xs tracking-wider">Contacto</h6>
            <p className="text-moss text-sm mb-2">
              Escríbeme a <a className="text-pine hover:text-forest underline-offset-2" href="mailto:azull.samael@gmail.com">azull.samael@gmail.com</a>.
            </p>
            <p className="text-moss text-sm mb-0">
              Creador: Samael Hernández
            </p>
          </div>
        </div>

        <div className="border-t border-gray-200 mt-6 pt-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <span className="text-moss text-sm">
            © {new Date().getFullYear()} IAGENTEK Vision Human Insight. Todos los derechos reservados.
          </span>
          <span className="text-moss text-sm">
            Clasificación de sensibilidad: Alta. Se recomienda evaluar riesgos y habilitar zonas de privacidad en producción.
          </span>
        </div>
      </div>
    </footer>
  )
}
