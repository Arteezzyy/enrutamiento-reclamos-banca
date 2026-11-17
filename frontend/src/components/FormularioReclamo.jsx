import { useState } from 'react'

export default function FormularioReclamo({ onSubmit, loading }) {
  const [texto, setTexto] = useState('')
  const [error, setError] = useState('')

  const manejarSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!texto.trim()) {
      setError('Por favor, escribe el texto del reclamo')
      return
    }

    await onSubmit(texto)
    setTexto('')
  }

  return (
    <form onSubmit={manejarSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Texto del reclamo
        </label>
        <textarea
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          rows={5}
          placeholder="Ej: No puedo acceder a la aplicación móvil, se cierra cada vez que intento iniciar sesión..."
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          disabled={loading}
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !texto.trim()}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-6 py-3 rounded-lg font-medium transition-colors flex justify-center items-center gap-2"
      >
        {loading ? 'Clasificando...' : 'Clasificar Reclamo'}
      </button>
    </form>
  )
}