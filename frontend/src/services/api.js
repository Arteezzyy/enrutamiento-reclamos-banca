const API_BASE = 'http://localhost:8000'

export const clasificarReclamo = async (texto) => {
  const response = await fetch(`${API_BASE}/clasificar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texto }),
  })
  if (!response.ok) throw new Error('Error al clasificar el reclamo')
  return await response.json()
}

export const asignarReclamos = async (reclamos) => {
  const response = await fetch(`${API_BASE}/asignar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reclamos }),
  })
  if (!response.ok) throw new Error('Error al asignar los reclamos')
  return await response.json()
}

export const listarReclamos = async () => {
  const response = await fetch(`${API_BASE}/reclamos`)
  if (!response.ok) throw new Error('Error al listar reclamos')
  return await response.json()
}

export const obtenerInfo = async () => {
  const response = await fetch(`${API_BASE}/info`)
  if (!response.ok) throw new Error('Error al obtener información')
  return await response.json()
}