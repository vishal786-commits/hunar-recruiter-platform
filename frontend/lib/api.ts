const API = process.env.NEXT_PUBLIC_API_BASE_URL!

async function request(path: string, options?: RequestInit) {
  const response = await fetch(`${API}${path}`, options)

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || "Request failed")
  }

  const data = await response.json()

  function clean(value: any): any {
    if (typeof value === "string") {
      let result = value
      for (let i = 0; i < 4; i++) {
        if (!/[ÃÂâ]/.test(result)) break
        try {
          const fixed = decodeURIComponent(escape(result))
          if (fixed === result) break
          result = fixed
        } catch { break }
      }
      return result
    }
    if (Array.isArray(value)) return value.map(clean)
    if (value && typeof value === "object") {
      return Object.fromEntries(Object.entries(value).map(([key, val]) => [key, clean(val)]))
    }
    return value
  }

  return clean(data)
}

export function analyzeJob(file: File) {
  const form = new FormData()
  form.append("file", file)

  return request("/jobs/analyze", {
    method: "POST",
    body: form,
  })
}

export function approveCandidates(
  jobId: string,
  candidateIds: string[]
) {
  return request(
    `/jobs/${jobId}/candidates/approve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        candidate_ids: candidateIds,
      }),
    }
  )
}

export function startScreenings(
  jobId: string,
  candidateIds: string[]
) {
  return request(
    `/jobs/${jobId}/screenings/start`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        candidate_ids: candidateIds,
      }),
    }
  )
}

export function getScreening(screeningId: string) {
  return request(
    `/jobs/screenings/${screeningId}`
  )
}

export function syncScreening(screeningId: string) {
  return request(
    `/jobs/screenings/${screeningId}/sync`,
    {
      method: "POST",
    }
  )
}
