function constantTimeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}

const NOT_FOUND = () =>
  new Response("Not found", {
    status: 404,
    headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
  });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== "GET" && request.method !== "HEAD") return NOT_FOUND();

    const match = url.pathname.match(/^\/s\/([A-Za-z0-9_-]{40,})\/calendar\.ics$/);
    if (!match || !constantTimeEqual(match[1], env.SUBSCRIPTION_TOKEN || "")) return NOT_FOUND();

    const calendar = await env.CALENDAR.get("calendar.ics");
    if (calendar === null) {
      return new Response("Calendar temporarily unavailable", {
        status: 503,
        headers: { "Cache-Control": "no-store", "Retry-After": "300" },
      });
    }

    return new Response(request.method === "HEAD" ? null : calendar, {
      status: 200,
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "Content-Disposition": 'inline; filename="calendar.ics"',
        "Cache-Control": "private, no-cache, max-age=0, must-revalidate",
        "X-Content-Type-Options": "nosniff",
      },
    });
  },
};
