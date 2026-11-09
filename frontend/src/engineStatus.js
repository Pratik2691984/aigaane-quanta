import { API_URL } from "./config";

export async function probeEngine() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(`${API_URL}/api/v3/quanta/health", {
      signal: controller.signal,
    });
    if (!res.ok) return { status: "degraded" };
    return { status: "ok", data: await res.json() };
  } catch (err) {
    return { status: "unreachable" };
  } finally {
    clearTimeout(timer);
  }
}