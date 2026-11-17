/**
 * Utilidades visuales compartidas: normaliza etiquetas del backend y expone
 * las clases de color de la paleta institucional.
 */

export const TONO_AREA = {
  azul: {
    pill: 'bg-[#E6EEF9] text-[#2F6FDE]',
    soft: 'bg-[#E6EEF9]',
    text: 'text-[#2F6FDE]',
    dot: 'bg-[#2F6FDE]',
    bar: 'bg-[#2F6FDE]'
  },
  dorado: {
    pill: 'bg-[#FBF5E2] text-[#A07E14]',
    soft: 'bg-[#FBF5E2]',
    text: 'text-[#A07E14]',
    dot: 'bg-[#C9A227]',
    bar: 'bg-[#C9A227]'
  },
  verde: {
    pill: 'bg-[#E3F6EC] text-[#1E8E5A]',
    soft: 'bg-[#E3F6EC]',
    text: 'text-[#1E8E5A]',
    dot: 'bg-[#1B998B]',
    bar: 'bg-[#1B998B]'
  }
}

const AREA_META = {
  'Soporte Tecnico': { label: 'Soporte Técnico', tone: 'azul' },
  'Gerencia de Operaciones/Riesgo': { label: 'Gerencia de Operaciones / Riesgo', tone: 'dorado' },
  'Atencion al Cliente': { label: 'Atención al Cliente', tone: 'verde' }
}

const sinAcentos = (valor) =>
  String(valor ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()

export function normalizarArea(area) {
  const clave = sinAcentos(area)
  if (clave.includes('soporte')) return 'Soporte Tecnico'
  if (clave.includes('gerencia') || clave.includes('riesgo'))
    return 'Gerencia de Operaciones/Riesgo'
  if (clave.includes('atencion') || clave.includes('cliente')) return 'Atencion al Cliente'
  return area || 'Sin área'
}

export function areaMeta(area) {
  const clave = normalizarArea(area)
  const meta = AREA_META[clave] ?? { label: area || 'Sin área', tone: 'azul' }
  return { key: clave, ...meta, tono: TONO_AREA[meta.tone] }
}

export const PRIORIDAD_META = {
  Alta: {
    label: 'Alta',
    pill: 'bg-[#FDE8E8] text-[#D64545]',
    dot: 'bg-[#D64545]',
    bar: 'bg-[#D64545]'
  },
  Media: {
    label: 'Media',
    pill: 'bg-[#FFF4DB] text-[#B7791F]',
    dot: 'bg-[#B7791F]',
    bar: 'bg-[#B7791F]'
  },
  Baja: {
    label: 'Baja',
    pill: 'bg-[#E3F6EC] text-[#1E8E5A]',
    dot: 'bg-[#1E8E5A]',
    bar: 'bg-[#1E8E5A]'
  }
}

export function prioridadMeta(prioridad) {
  const clave = sinAcentos(prioridad)
  const encontrada = Object.keys(PRIORIDAD_META).find((k) => sinAcentos(k) === clave)
  return { key: encontrada ?? 'Media', ...PRIORIDAD_META[encontrada] }
}

export const SLA_POR_PRIORIDAD = { Alta: 2, Media: 8, Baja: 24 }

export const TONO_PRIORIDAD = {
  Alta: { soft: 'bg-[#FDE8E8]', text: 'text-[#D64545]' },
  Media: { soft: 'bg-[#FFF4DB]', text: 'text-[#B7791F]' },
  Baja: { soft: 'bg-[#E3F6EC]', text: 'text-[#1E8E5A]' }
}

export const CAPACIDADES_DEFAULT = {
  'Soporte Tecnico': 50,
  'Gerencia de Operaciones/Riesgo': 30,
  'Atencion al Cliente': 40
}

export function formatFecha(fecha) {
  if (!fecha) return '—'
  const valor = new Date(fecha)
  if (Number.isNaN(valor.getTime())) return '—'
  return valor.toLocaleString('es-BO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function porcentaje(valor) {
  return `${Math.round((Number(valor) || 0) * 100)}%`
}
