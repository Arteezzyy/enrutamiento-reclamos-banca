import { useState } from 'react'
import { AlertTriangle, Loader2, Send, Wand2 } from 'lucide-react'

const EJEMPLOS = [
  {
    etiqueta: 'Acceso a la app',
    texto: 'No puedo acceder a la aplicación móvil, se cierra cada vez que intento iniciar sesión.',
  },
  {
    etiqueta: 'Transferencia',
    texto: 'Hice una transferencia pero el dinero no llegó a la cuenta del destinatario.',
  },
  {
    etiqueta: 'Comisión',
    texto: 'Me cobraron una comisión que no correspondía en mi cuenta de ahorros.',
  },
]

export default function FormularioReclamo({ onSubmit, loading }) {
  const [texto, setTexto] = useState('')
  const [error, setError] = useState('')

  const manejarSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!texto.trim()) {
      setError('Escribe el texto del reclamo para poder clasificarlo.')
      return
    }

    await onSubmit(texto)
    setTexto('')
  }

  const usarEjemplo = (valor) => {
    setError('')
    setTexto(valor)
  }

  return (
    <form onSubmit={manejarSubmit} className="space-y-5">
      <div>
        <div className="mb-2 flex items-end justify-between gap-3">
          <label htmlFor="texto-reclamo" className="text-sm font-semibold text-ink">
            Texto del reclamo
          </label>
          <span className="text-xs tabular-nums text-muted/70">{texto.length} caracteres</span>
        </div>
        <textarea
          id="texto-reclamo"
          className="input min-h-[150px] resize-none leading-relaxed"
          rows={6}
          maxLength={1000}
          placeholder="Ej: No puedo acceder a la aplicación móvil, se cierra cada vez que intento iniciar sesión..."
          value={texto}
          onChange={(e) => {
            setTexto(e.target.value)
            if (error) setError('')
          }}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') manejarSubmit(e)
          }}
          disabled={loading}
        />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted/70">
            <Wand2 className="h-3.5 w-3.5 text-gold" />
            Ejemplos
          </span>
          {EJEMPLOS.map((ejemplo) => (
            <button
              key={ejemplo.etiqueta}
              type="button"
              onClick={() => usarEjemplo(ejemplo.texto)}
              disabled={loading}
              className="rounded-full border border-line bg-white px-3 py-1 text-xs font-medium text-muted transition-colors hover:border-accent/40 hover:bg-accent-soft hover:text-accent-dark disabled:opacity-50"
            >
              {ejemplo.etiqueta}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2.5 rounded-xl border border-[#FDE8E8] bg-[#FDE8E8]/60 px-4 py-3 text-sm text-[#D64545]">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="flex flex-col gap-3 border-t border-line pt-5 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs leading-relaxed text-muted">
          El modelo analiza el texto con TF-IDF y predice área y prioridad.
          <span className="ml-1 hidden text-muted/60 sm:inline">Atajo: Ctrl + Enter</span>
        </p>
        <button type="submit" disabled={loading || !texto.trim()} className="btn-primary sm:min-w-[210px]">
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Clasificando...
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              Clasificar reclamo
            </>
          )}
        </button>
      </div>
    </form>
  )
}
