// Cloudflare Worker — Groq API 프록시 (무료)
// 환경변수: GROQ_API_KEY = gsk_... 값으로 Secret 추가

export default {
  async fetch(request, env) {
    const ALLOWED_ORIGIN = 'https://chan63078-dot.github.io';

    const corsHeaders = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: corsHeaders });
    }

    if (!env.GROQ_API_KEY) {
      return new Response(JSON.stringify({ error: 'GROQ_API_KEY not set in Worker environment' }), {
        status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    try {
      const body = await request.json();

      const messages = [];
      if (body.system) messages.push({ role: 'system', content: body.system });
      messages.push(...(body.messages || []));

      const groqRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.GROQ_API_KEY}`,
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages,
          max_tokens: body.max_tokens || 8192,
          temperature: 0.7,
        }),
      });

      const data = await groqRes.json();

      // Anthropic 응답 형식으로 변환 (사이트 코드 호환)
      if (data.choices?.[0]?.message?.content) {
        const converted = {
          content: [{ type: 'text', text: data.choices[0].message.content }],
        };
        return new Response(JSON.stringify(converted), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      return new Response(JSON.stringify(data), {
        status: groqRes.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};
