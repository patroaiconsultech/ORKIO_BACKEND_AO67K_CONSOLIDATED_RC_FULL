// PATCH_23_AGENT_REGISTRY_CANONICO
// PATCH_24_TURN_ROUTER
// PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL
// Canonical agent registry shared by frontend routing code.
//
// Purpose:
// - Keep aliases, display names and canonical slugs in one place.
// - Avoid frontend/backend drift such as "Orion" vs "ORION_CTO".
// - Keep Direct Agent Addressing deterministic in Team Mode.
//
// This module is intentionally dependency-free so it can be unit-tested in
// isolation and imported by AppConsole without creating runtime cycles.

export const AGENT_REGISTRY_VERSION = "PATCH_31_AGENT_REGISTRY_VOICE_PROFILE_V1";
export const TURN_ROUTER_VERSION = "PATCH_28_PERSONA_ISOLATION_TEAM_PANEL_V1";
export const AGENT_VOICE_PROFILE_VERSION = "PATCH_31_CANONICAL_AGENT_VOICE_PROFILE_V1";
export const AGENT_REALTIME_IDENTITY_VERSION = "PATCH_31_REGISTRY_DRIVEN_REALTIME_IDENTITY_V1";
export const AGENT_VOICE_PRECEDENCE_VERSION = "PATCH_31_FINAL_CANONICAL_VOICE_PRECEDENCE_V1";
export const AGENT_REALTIME_CONTRACT_VERSION = "PATCH_31_FINAL_PREMIUM_REALTIME_PERSONA_VOICE_CONTRACT_V1";
export const AGENT_VOICE_OVERRIDE_POLICY = "db_voice_requires_explicit_override_flag_and_never_overrides_env_or_registry";

export const CANONICAL_AGENT_REGISTRY = Object.freeze({
  orkio: Object.freeze({
    slug: "orkio",
    display_name: "Orkio",
    role_label: "Copiloto executivo",
    route_role: "host",
    public_beta_allowed: true,
    internal: false,
    public_agent: true,
    internal_agent: false,
    team_default: true,
    team_optional: false,
    aliases: Object.freeze(["orkio", "orquio", "archio", "workio", "workq"]),
    domain_keywords: Object.freeze(["copiloto", "patroai", "contexto", "continuidade", "estrategia", "estratégia"]),
    voice_profile: Object.freeze({
      profile_id: "orkio",
      voice_id: "cedar",
      env_key: "VITE_ORKIO_VOICE_ID",
      provider: "openai_realtime",
      label: "Orkio — voz oficial",
    }),
    realtime_role_line: "Você é Orkio, agente executivo principal da plataforma Patroai.",
    realtime_priority_line: "Organize contexto, continuidade, decisões, riscos e próximos passos.",
    persona_scope: "Orkio organiza a sala, sintetiza contexto, prioriza próximos passos e preserva continuidade operacional.",
    persona_guardrails: Object.freeze([
      "Não assuma a identidade de Orion, Chris, Laura ou Auditor quando outro agente for o speaker ativo.",
      "Quando outro agente for chamado diretamente, não aja como intermediário visível."
    ]),
  }),
  team: Object.freeze({
    slug: "team",
    display_name: "Team",
    role_label: "Sala executiva",
    route_role: "room",
    public_beta_allowed: true,
    internal: false,
    public_agent: true,
    internal_agent: false,
    team_default: false,
    team_optional: false,
    aliases: Object.freeze(["team", "time", "equipe", "todos", "sala", "war room", "warroom", "squad"]),
    domain_keywords: Object.freeze(["reuniao", "reunião", "sala executiva", "painel", "mesa", "orquestracao", "orquestração"]),
    voice_profile: Object.freeze({
      profile_id: "team",
      voice_id: "cedar",
      env_key: "VITE_TEAM_VOICE_ID",
      provider: "openai_realtime",
      label: "Team — coordenação",
    }),
    realtime_role_line: "Você está no modo Team, atuando como coordenador de sala executiva multiagente da Patroai.",
    realtime_priority_line: "Coordene turnos, responsáveis, riscos e próximos passos sem sobrepor vozes.",
    persona_scope: "Team é a sala, não um agente especialista; ele coordena turnos e painéis de resposta.",
    persona_guardrails: Object.freeze([
      "Não trate Team como speaker especializado quando houver agente ativo definido.",
      "Use o Team apenas para coordenação da sala e resposta em painel."
    ]),
  }),
  orion: Object.freeze({
    slug: "orion",
    display_name: "Orion",
    role_label: "CTO técnico",
    route_role: "specialist",
    public_beta_allowed: false,
    internal: true,
    public_agent: false,
    internal_agent: true,
    team_default: true,
    team_optional: true,
    aliases: Object.freeze([
      "orion", "oria", "orlan", "auria", "aurya", "arian", "aryan", "warren", "cto"
    ]),
    domain_keywords: Object.freeze([
      "tecnico", "técnico", "technical", "diagnostico", "diagnóstico",
      "arquitetura", "arquiteto", "devops", "backend", "frontend", "logs",
      "deploy", "rollback", "realtime", "build", "bug", "erro"
    ]),
    voice_profile: Object.freeze({
      profile_id: "orion",
      voice_id: "echo",
      env_key: "VITE_ORION_VOICE_ID",
      provider: "openai_realtime",
      label: "Orion — CTO técnico",
    }),
    realtime_role_line: "Você é Orion, agente interno CTO técnico da Patroai.",
    realtime_priority_line: "Diagnóstico técnico, runtime, backend, frontend, realtime, agentes, logs, deploy, rollback, arquitetura, estabilidade e validação.",
    persona_scope: "Orion responde como CTO técnico: arquitetura, código, bugs, logs, realtime, deploy, rollback, estabilidade e validação.",
    persona_guardrails: Object.freeze([
      "Não responda como Orkio, Chris, Laura ou Auditor.",
      "Separe fato confirmado, hipótese provável, patch sugerido, validação pendente e risco residual quando analisar problemas técnicos.",
      "Não declare deploy, commit, push, PR, migration ou validação real sem evidência."
    ]),
  }),
  chris: Object.freeze({
    slug: "chris",
    display_name: "Chris",
    role_label: "Financeiro e estratégia",
    route_role: "specialist",
    public_beta_allowed: false,
    internal: true,
    public_agent: false,
    internal_agent: true,
    team_default: true,
    team_optional: true,
    aliases: Object.freeze([
      "chris", "cris", "criz", "crys", "c h r i s", "c-h-r-i-s", "cfo"
    ]),
    domain_keywords: Object.freeze([
      "financeiro", "financial", "comercial", "vendas", "valuation",
      "captação", "captacao", "pricing", "go-to-market", "receita", "funil"
    ]),
    voice_profile: Object.freeze({
      profile_id: "chris",
      voice_id: "coral",
      env_key: "VITE_CHRIS_VOICE_ID",
      provider: "openai_realtime",
      label: "Chris — financeiro e estratégia",
    }),
    realtime_role_line: "Você é Chris, agente interno financeiro/estratégico da Patroai.",
    realtime_priority_line: "Viabilidade, valuation, captação, funil, pricing, receita, análise financeira e estratégia comercial.",
    persona_scope: "Chris responde pela ótica financeira, comercial, estratégica, de receita, valuation, captação e viabilidade.",
    persona_guardrails: Object.freeze([
      "Não responda como Orion em diagnóstico técnico profundo.",
      "Não responda como Laura em narrativa institucional quando a demanda for storytelling ou pitch.",
      "Não prometa captação, investimento ou resultado financeiro garantido."
    ]),
  }),
  laura: Object.freeze({
    slug: "laura",
    display_name: "Laura",
    role_label: "Narrativa e investidores",
    route_role: "specialist",
    public_beta_allowed: false,
    internal: true,
    public_agent: false,
    internal_agent: true,
    team_default: true,
    team_optional: true,
    aliases: Object.freeze(["laura"]),
    domain_keywords: Object.freeze([
      "investidor", "investidores", "pitch", "business plan", "narrativa",
      "storytelling", "deck", "plano de negocios", "plano de negócios", "sumario executivo", "sumário executivo"
    ]),
    voice_profile: Object.freeze({
      profile_id: "laura",
      voice_id: "shimmer",
      env_key: "VITE_LAURA_VOICE_ID",
      provider: "openai_realtime",
      label: "Laura — narrativa e investidores",
    }),
    realtime_role_line: "Você é Laura, agente interno de narrativa, business plan, pitch, investidores e comunicação executiva da Patroai.",
    realtime_priority_line: "Clareza institucional, storytelling, apresentação para investidores, pitch, business plan, sumário executivo e posicionamento.",
    persona_scope: "Laura responde pela ótica de narrativa, investidores, pitch, business plan, clareza institucional e storytelling executivo.",
    persona_guardrails: Object.freeze([
      "Não responda como Orion em execução técnica.",
      "Não invente dados de mercado, valuation ou métricas sem fonte ou evidência.",
      "Quando a informação for proposta narrativa, marque como proposta e não como fato comprovado."
    ]),
  }),
  auditor: Object.freeze({
    slug: "auditor",
    display_name: "Auditor",
    role_label: "Auditoria externa",
    route_role: "specialist",
    public_beta_allowed: false,
    internal: true,
    public_agent: false,
    internal_agent: true,
    team_default: false,
    team_optional: true,
    aliases: Object.freeze(["auditor", "auditor externo", "ao-01", "ao01"]),
    domain_keywords: Object.freeze(["auditoria", "red team", "red-team", "riscos", "validacao", "validação", "go/no-go"]),
    voice_profile: Object.freeze({
      profile_id: "auditor",
      voice_id: "ash",
      env_key: "VITE_AUDITOR_VOICE_ID",
      provider: "openai_realtime",
      label: "Auditor — revisão crítica",
    }),
    realtime_role_line: "Você é Auditor, agente/função de auditoria externa e red-team da Patroai.",
    realtime_priority_line: "Revisão crítica, evidências, riscos, validação, rollback e vereditos GO/NO-GO.",
    persona_scope: "Auditor responde como revisão externa/read-only: evidências, riscos, validação, rollback e GO/NO-GO.",
    persona_guardrails: Object.freeze([
      "Não trate proposta como validação.",
      "Não aprove produção sem evidências de build, staging e teste end-to-end quando aplicável.",
      "Separe achado documental de achado prático."
    ]),
  }),
});

export function normalizeAgentLookupValue(value = "") {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/^@+/, "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[“”"']/g, " ")
    .replace(/[\s\-/]+/g, "_")
    .replace(/[^a-z0-9_]+/g, "")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
}

export function normalizeAgentText(value = "") {
  return String(value || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[“”"']/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function compactAgentLookupValue(value = "") {
  return normalizeAgentLookupValue(value).replace(/_/g, "");
}

function aliasMatchesValue(alias = "", value = "") {
  const a = normalizeAgentLookupValue(alias);
  const v = normalizeAgentLookupValue(value);
  if (!a || !v) return false;
  if (a === v) return true;
  const ac = compactAgentLookupValue(alias);
  const vc = compactAgentLookupValue(value);
  return Boolean(ac && vc && (ac === vc || vc.includes(ac)));
}

export function canonicalAgentProfile(value = "") {
  const raw = normalizeAgentLookupValue(value);
  if (!raw) return null;

  if (CANONICAL_AGENT_REGISTRY[raw]) {
    return CANONICAL_AGENT_REGISTRY[raw];
  }

  for (const profile of Object.values(CANONICAL_AGENT_REGISTRY)) {
    if (aliasMatchesValue(profile.slug, raw)) return profile;
    if (aliasMatchesValue(profile.display_name, raw)) return profile;
    if ((profile.aliases || []).some((alias) => aliasMatchesValue(alias, raw))) {
      return profile;
    }
  }

  return null;
}

export function canonicalAgentSlug(value = "", { allowUnknown = true } = {}) {
  const profile = canonicalAgentProfile(value);
  if (profile?.slug) return profile.slug;
  return allowUnknown ? normalizeAgentLookupValue(value) : "";
}

export function canonicalAgentDisplayNameFromSlug(value = "") {
  const profile = canonicalAgentProfile(value);
  if (profile?.display_name) return profile.display_name;
  const slug = normalizeAgentLookupValue(value);
  return slug ? slug.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase()) : "";
}

export function canonicalAgentAliases(value = "") {
  const profile = canonicalAgentProfile(value);
  if (!profile) return [];
  return Array.from(new Set([profile.slug, profile.display_name, ...(profile.aliases || [])].filter(Boolean)));
}

export function escapeRegExpLiteral(value = "") {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function aliasPatternForProfile(profile) {
  return canonicalAgentAliases(profile.slug)
    .map((alias) => escapeRegExpLiteral(alias).replace(/\\\s+/g, "\\s*[- ]?\\s*"))
    .join("|");
}

function keywordPatternForProfile(profile) {
  return Array.from(profile?.domain_keywords || [])
    .map((keyword) => escapeRegExpLiteral(keyword).replace(/\\\s+/g, "\\s+"))
    .join("|");
}

function routerProfiles({ includeInternal = true } = {}) {
  return Object.values(CANONICAL_AGENT_REGISTRY)
    .filter((profile) => includeInternal || !Boolean(profile.internal_agent ?? profile.internal));
}

function classifyProfileMention(normalized, profile) {
  const aliasPattern = aliasPatternForProfile(profile);
  if (!aliasPattern) return null;

  const aliasBoundary = new RegExp(`(?:^|\\b)(?:${aliasPattern})(?=$|\\b|[\\s,.:;!?—-])`, "iu");
  if (!aliasBoundary.test(normalized)) return null;

  return {
    slug: profile.slug,
    display_name: profile.display_name,
    match_type: "mention_reference",
    confidence: 0.35,
  };
}

function classifyProfileTopic(normalized, profile) {
  const keywordPattern = keywordPatternForProfile(profile);
  if (!keywordPattern) return null;

  const topicBoundary = new RegExp(`(?:^|\\b)(?:${keywordPattern})(?=$|\\b|[\\s,.:;!?—-])`, "iu");
  if (!topicBoundary.test(normalized)) return null;

  return {
    slug: profile.slug,
    display_name: profile.display_name,
    match_type: "topic_classification",
    confidence: 0.25,
  };
}


function uniqueAgentSlugs(values = []) {
  const out = [];
  const seen = new Set();
  for (const value of values || []) {
    const slug = canonicalAgentSlug(value, { allowUnknown: false });
    if (!slug || seen.has(slug)) continue;
    seen.add(slug);
    out.push(slug);
  }
  return out;
}

function slugsMentionedInSegment(segment = "", profiles = []) {
  const normalized = normalizeAgentText(segment);
  const out = [];
  for (const profile of profiles || []) {
    const aliasPattern = aliasPatternForProfile(profile);
    if (!aliasPattern) continue;
    const mention = new RegExp(`(?:^|\\b)(?:${aliasPattern})(?=$|\\b|[\\s,.:;!?—+\\-])`, "iu");
    if (mention.test(normalized)) out.push(profile.slug);
  }
  return uniqueAgentSlugs(out);
}

function payloadForMany(slugs = [], { matchType, confidence, routeReason } = {}) {
  const clean = uniqueAgentSlugs(slugs);
  const displayNames = clean
    .map((slug) => CANONICAL_AGENT_REGISTRY[slug]?.display_name || canonicalAgentDisplayNameFromSlug(slug))
    .filter(Boolean);
  return {
    slug: clean[0] || null,
    display_name: displayNames.join(" + "),
    display_names: displayNames,
    match_type: matchType,
    route_reason: routeReason,
    confidence,
    target_agent_slug: clean[0] || null,
    target_agent_slugs: clean,
    multi_agent_turn: clean.length > 1 || matchType === "team_panel",
    response_control: "sequenced_team_turns",
  };
}

export function teamDefaultMemberSlugs({ includeInternal = true } = {}) {
  // PATCH_28: Team Panel membership is registry-driven. Do not hard-code
  // panel members in the router/tests; set team_default on each agent profile.
  return Object.values(CANONICAL_AGENT_REGISTRY)
    .filter((profile) => profile.slug !== "team")
    .filter((profile) => Boolean(profile.team_default))
    .filter((profile) => includeInternal || !Boolean(profile.internal_agent ?? profile.internal))
    .map((profile) => profile.slug);
}

export function teamOptionalMemberSlugs({ includeInternal = true } = {}) {
  return Object.values(CANONICAL_AGENT_REGISTRY)
    .filter((profile) => profile.slug !== "team")
    .filter((profile) => Boolean(profile.team_optional))
    .filter((profile) => includeInternal || !Boolean(profile.internal_agent ?? profile.internal))
    .map((profile) => profile.slug);
}

export function personaIsolationContract(value = "") {
  const profile = canonicalAgentProfile(value);
  if (!profile) {
    return {
      slug: null,
      display_name: "",
      role_label: "",
      persona_scope: "",
      persona_guardrails: [],
    };
  }
  return {
    slug: profile.slug,
    display_name: profile.display_name,
    role_label: profile.role_label,
    persona_scope: profile.persona_scope || "",
    persona_guardrails: Array.from(profile.persona_guardrails || []),
  };
}


function lookupCandidateForAgentLike(value = "") {
  if (value && typeof value === "object") {
    return (
      value.slug ||
      value.key ||
      value.agent_slug ||
      value.agent_name ||
      value.display_name ||
      value.name ||
      value.id ||
      ""
    );
  }
  return value;
}

function profileForAgentLike(value = "", fallbackSlug = "orkio") {
  const profile = canonicalAgentProfile(lookupCandidateForAgentLike(value));
  if (profile) return profile;
  return canonicalAgentProfile(fallbackSlug) || CANONICAL_AGENT_REGISTRY.orkio;
}

export function canonicalAgentVoiceProfile(value = "", { fallbackSlug = "orkio" } = {}) {
  const profile = profileForAgentLike(value, fallbackSlug);
  const rawCandidate =
    profile?.canonical_voice_profile ||
    profile?.voice_profile ||
    profile?.voice ||
    {};
  const raw = rawCandidate && typeof rawCandidate === "object" ? rawCandidate : {};
  const legacyProfileId = typeof rawCandidate === "string" ? rawCandidate.trim() : "";
  const fallbackCanonicalSlug = canonicalAgentSlug(fallbackSlug) || "orkio";
  const slug = profile?.slug || fallbackCanonicalSlug;
  return {
    version: raw.version || AGENT_VOICE_PROFILE_VERSION,
    payload_version: raw.payload_version || "PATCH_31_REV_A_CANONICAL_VOICE_PROFILE_PAYLOAD_V1",
    precedence_version: AGENT_VOICE_PRECEDENCE_VERSION,
    contract_version: raw.contract_version || AGENT_REALTIME_CONTRACT_VERSION,
    override_policy: raw.override_policy || AGENT_VOICE_OVERRIDE_POLICY,
    precedence: Array.isArray(raw.precedence) && raw.precedence.length
      ? Array.from(raw.precedence)
      : ["env", "registry", "db_override", "fallback"],
    slug,
    display_name: profile?.display_name || canonicalAgentDisplayNameFromSlug(fallbackCanonicalSlug),
    profile_id: raw.profile_id || profile?.voice_profile_id || legacyProfileId || slug,
    voice_id: raw.voice_id || profile?.voice_id || "cedar",
    env_key: raw.env_key || profile?.voice_env_key || profile?.voiceEnvKey || "",
    provider: raw.provider || profile?.voice_provider || "openai_realtime",
    label: raw.label || profile?.voice_hint || profile?.display_name || canonicalAgentDisplayNameFromSlug(fallbackCanonicalSlug),
    source: raw.source || "registry",
  };
}

export function canonicalAgentRealtimeIdentity(value = "", { fallbackSlug = "orkio" } = {}) {
  const profile = profileForAgentLike(value, fallbackSlug);
  return {
    version: AGENT_REALTIME_IDENTITY_VERSION,
    slug: profile?.slug || canonicalAgentSlug(fallbackSlug),
    display_name: profile?.display_name || canonicalAgentDisplayNameFromSlug(fallbackSlug),
    role_label: profile?.role_label || "",
    route_role: profile?.route_role || "specialist",
    realtime_role_line: profile?.realtime_role_line || "",
    realtime_priority_line: profile?.realtime_priority_line || "",
    persona_scope: profile?.persona_scope || profile?.description || "",
    persona_guardrails: Array.from(profile?.persona_guardrails || []),
    voice_profile: canonicalAgentVoiceProfile(profile?.slug || fallbackSlug, { fallbackSlug }),
    contract_version: AGENT_REALTIME_CONTRACT_VERSION,
  };
}

export function buildCanonicalRealtimeAgentInstructions(value = "", {
  fallbackSlug = "orkio",
  includeKnownAgents = true,
} = {}) {
  const identity = canonicalAgentRealtimeIdentity(value, { fallbackSlug });
  const knownAgentsLine = includeKnownAgents
    ? "Você deve reconhecer agentes internos da plataforma: Orkio, Team, Chris, Orion, Laura e Auditor."
    : "";
  const base = [
    "Você está em uma sessão de voz realtime dentro da plataforma Patroai.",
    knownAgentsLine,
    "Nunca trate agentes internos como pessoas externas, contatos externos, e-mails ou sistemas fora da plataforma.",
    "Nunca afirme que acionou, publicou, abriu auditoria, criou War Room, enviou push, chamou agente, executou integração, deploy, commit, push, PR ou migração se isso não tiver confirmação técnica no runtime.",
    "Se a orquestração real ainda não estiver confirmada, diga de forma transparente que está conduzindo a transição de fala no Realtime e registrando a pendência técnica.",
    "Regra crítica: fale apenas como o agente ativo deste turno."
  ].filter(Boolean);

  const identityLines = [
    identity.realtime_role_line,
    identity.display_name ? `Identidade ativa: você é ${identity.display_name}, ${identity.role_label || "agente interno da Patroai"}.` : "",
    identity.realtime_priority_line ? `Prioridade: ${identity.realtime_priority_line}` : "",
    identity.persona_scope ? `Escopo de persona: ${identity.persona_scope}` : "",
    ...(identity.persona_guardrails || []).map((rule) => `Guardrail: ${rule}`)
  ].filter(Boolean);

  return [
    ...base,
    "",
    `Contrato de identidade realtime: ${AGENT_REALTIME_IDENTITY_VERSION}.`,
    `Contrato premium final: ${AGENT_REALTIME_CONTRACT_VERSION}.`,
    `Contrato de voz: ${AGENT_VOICE_PROFILE_VERSION}.`,
    `Fonte canônica de voz/persona: Agent Registry. Política de override: ${AGENT_VOICE_OVERRIDE_POLICY}.`,
    ...identityLines,
    identity?.voice_profile?.voice_id ? `Voz canônica esperada: ${identity.voice_profile.voice_id}.` : "",
  ].filter((line) => line !== null && line !== undefined).join("\n");
}

function teamPanelSlugs({ includeInternal = true } = {}) {
  // PATCH_28: delegate generic Team Panel membership to registry flags.
  // This prevents router-level lists such as [orkio, orion, chris, laura].
  return teamDefaultMemberSlugs({ includeInternal });
}

function classifyTeamPanel(normalized, profiles) {
  const teamProfile = CANONICAL_AGENT_REGISTRY.team;
  const teamPattern = aliasPatternForProfile(teamProfile);
  if (!teamPattern) return null;

  const panel = new RegExp(`^\\s*(?:@|#)?\\s*(?:${teamPattern})(?=$|[\\s,.:;!?—-])`, "iu");
  if (!panel.test(normalized)) return null;

  const slugs = teamPanelSlugs({ includeInternal: true });
  if (!slugs.length) return null;

  return payloadForMany(slugs, {
    matchType: "team_panel",
    confidence: 0.91,
    routeReason: "team_alias_at_message_start",
  });
}

function sharedCommandPattern() {
  const commandPhrases = [
    "chame", "chama", "chamar",
    "acione", "aciona", "acionar",
    "inclua", "inclui", "incluir",
    "traga", "traz", "trazer",
    "convoque", "convoca", "convocar",
    "quero ouvir", "gostaria de ouvir",
    "quero falar com", "fale com", "fala com",
    "pergunte para", "pergunta para", "pergunte ao", "pergunte a",
    "passa para", "passe para",
    "direciona para", "direcione para",
    "coloca", "coloque",
    "peça para", "peca para"
  ];
  return commandPhrases
    .map((word) => escapeRegExpLiteral(word).replace(/\\\s+/g, "\\s+"))
    .join("|");
}

function classifyMultiCommandAddress(normalized, profiles) {
  const commandPattern = sharedCommandPattern();
  const command = new RegExp(
    `(?:^|[\\s,.:;!?—-])(?:por\\s+favor\\s+)?(?:${commandPattern})\\s+(?<segment>[^.!?;\\n]{1,180})`,
    "iu"
  );
  const match = command.exec(normalized);
  if (!match) return null;

  const beforeMatch = normalized.slice(0, match.index).trim();
  if (/\b(?:nao|não)\s*$/.test(beforeMatch)) return null;

  const segment = match.groups?.segment || "";
  const slugs = slugsMentionedInSegment(segment, profiles).filter((slug) => slug !== "team");
  if (slugs.length < 2) return null;

  return payloadForMany(slugs, {
    matchType: "multi_command_address",
    confidence: 0.96,
    routeReason: "explicit_multi_agent_handoff_command",
  });
}

function classifyMultiDirectAddress(normalized, profiles) {
  const prefix = /^\s*(?<segment>[^.!?;\n]{1,120}?)(?:[,:\u2014-]|\s+(?:por\s+favor|avaliem|respondam|revisem|analisem|analise|entrem|assumam|podem)\b)/iu.exec(normalized);
  if (!prefix) return null;

  const segment = prefix.groups?.segment || "";
  if (!/\b(?:e|com|junto|juntos|mais)\b|\+/iu.test(segment)) return null;

  const slugs = slugsMentionedInSegment(segment, profiles).filter((slug) => slug !== "team");
  if (slugs.length < 2) return null;

  const startsWithAgent = slugs.some((slug) => classifyProfileDirectAddress(normalized, CANONICAL_AGENT_REGISTRY[slug]));
  if (!startsWithAgent) return null;

  return payloadForMany(slugs, {
    matchType: "multi_agent_address",
    confidence: 0.94,
    routeReason: "multi_agent_vocative_at_message_start",
  });
}


function classifyProfileCommandAddress(normalized, profile) {
  const aliasPattern = aliasPatternForProfile(profile);
  if (!aliasPattern) return null;

  // PATCH_24_REV_A:
  // Handoff commands must beat an initial speaker vocative.
  // Example: "Orion, chame a Chris" must route to Chris, not Orion.
  // This is intentionally restricted to explicit routing commands so passive
  // references like "o backend precisa do CTO?" remain mention_reference.
  const commandPhrases = [
    "chame", "chama", "chamar",
    "acione", "aciona", "acionar",
    "inclua", "inclui", "incluir",
    "traga", "traz", "trazer",
    "convoque", "convoca", "convocar",
    "quero ouvir", "gostaria de ouvir",
    "quero falar com", "fale com", "fala com",
    "pergunte para", "pergunta para", "pergunte ao", "pergunte a",
    "passa para", "passe para",
    "direciona para", "direcione para",
    "coloca", "coloque",
    "peça para", "peca para"
  ];
  const commandPattern = commandPhrases
    .map((word) => escapeRegExpLiteral(word).replace(/\\\s+/g, "\\s+"))
    .join("|");

  const optionalArticle = "(?:o|a|ao|pro|pra|para|para\\s+o|para\\s+a)?";

  const commandAddress = new RegExp(
    `(?:^|[\\s,.:;!?—-])(?:por\\s+favor\\s+)?(?:${commandPattern})\\s+${optionalArticle}\\s*(?:@|#)?\\s*(?:${aliasPattern})(?=$|\\b|[\\s,.:;!?—-])`,
    "iu"
  );

  const match = commandAddress.exec(normalized);
  if (!match) return null;

  const beforeMatch = normalized.slice(0, match.index).trim();
  if (/\b(?:nao|não)\s*$/.test(beforeMatch)) {
    return null;
  }

  return {
    slug: profile.slug,
    display_name: profile.display_name,
    match_type: "command_address",
    route_reason: match.index > 0 ? "explicit_handoff_command_after_vocative" : "explicit_routing_command",
    confidence: match.index > 0 ? 0.95 : 0.94,
  };
}

function classifyProfileDirectAddress(normalized, profile) {
  const aliasPattern = aliasPatternForProfile(profile);
  if (!aliasPattern) return null;

  // PATCH_24_TURN_ROUTER:
  // Direct addressing is intentionally narrower than "alias appears anywhere".
  // It only routes when the alias is a vocative at the beginning of the message,
  // after a greeting, or after an explicit routing command. This prevents cases
  // like "o backend precisa do CTO?" from becoming an Orion handoff.
  const greetingWords = [
    "oi", "ola", "olá", "hey", "bom dia", "boa tarde", "boa noite", "fala", "escuta", "ouve"
  ];
  const greetingPattern = greetingWords
    .map((word) => escapeRegExpLiteral(word).replace(/\\\s+/g, "\\s+"))
    .join("|");

  const commandPhrases = [
    "chame", "chama", "chamar",
    "acione", "aciona", "acionar",
    "inclua", "inclui", "incluir",
    "traga", "traz", "trazer",
    "convoque", "convoca", "convocar",
    "quero ouvir", "gostaria de ouvir",
    "quero falar com", "fale com", "fala com",
    "pergunte para", "pergunta para", "pergunte ao", "pergunte a",
    "passa para", "passe para",
    "direciona para", "direcione para",
    "coloca", "coloque",
    "peça para", "peca para"
  ];
  const commandPattern = commandPhrases
    .map((word) => escapeRegExpLiteral(word).replace(/\\\s+/g, "\\s+"))
    .join("|");

  const optionalArticle = "(?:o|a|ao|a|pro|pra|para|para\\s+o|para\\s+a)?";

  const prefixAddress = new RegExp(
    `^\\s*(?:@|#)?\\s*(?:${aliasPattern})(?=$|[\\s,.:;!?—-])`,
    "iu"
  );
  const greetingAddress = new RegExp(
    `^\\s*(?:${greetingPattern})\\s+(?:@|#)?\\s*(?:${aliasPattern})(?=$|[\\s,.:;!?—-])`,
    "iu"
  );
  const commandAddress = new RegExp(
    `^\\s*(?:por\\s+favor\\s+)?(?:${commandPattern})\\s+${optionalArticle}\\s*(?:@|#)?\\s*(?:${aliasPattern})(?=$|\\b|[\\s,.:;!?—-])`,
    "iu"
  );

  if (prefixAddress.test(normalized)) {
    return {
      slug: profile.slug,
      display_name: profile.display_name,
      match_type: "direct_address",
      route_reason: "alias_at_message_start",
      confidence: 0.98,
    };
  }
  if (greetingAddress.test(normalized)) {
    return {
      slug: profile.slug,
      display_name: profile.display_name,
      match_type: "direct_address",
      route_reason: "alias_after_greeting",
      confidence: 0.96,
    };
  }
  if (commandAddress.test(normalized)) {
    return {
      slug: profile.slug,
      display_name: profile.display_name,
      match_type: "command_address",
      route_reason: "explicit_routing_command",
      confidence: 0.94,
    };
  }

  return null;
}

export function classifyAgentTurnFromMessage(rawMessage = "", { includeInternal = true } = {}) {
  const raw = String(rawMessage || "").trim();
  if (!raw) {
    return {
      match_type: "none",
      target_agent_slug: null,
      display_name: "",
      confidence: 0,
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  const normalized = normalizeAgentText(raw);
  if (!normalized) {
    return {
      match_type: "none",
      target_agent_slug: null,
      display_name: "",
      confidence: 0,
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  const profiles = routerProfiles({ includeInternal });

  // PATCH_27_MULTI_AGENT_RESPONSE_CONTROL:
  // Multi-agent/team requests must be evaluated before single-agent routing so
  // "Orion e Chris, ..." does not collapse to only Orion.
  const teamPanel = classifyTeamPanel(normalized, profiles);
  if (teamPanel) {
    return {
      ...teamPanel,
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  const multiCommand = classifyMultiCommandAddress(normalized, profiles);
  if (multiCommand) {
    return {
      ...multiCommand,
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  const multiDirect = classifyMultiDirectAddress(normalized, profiles);
  if (multiDirect) {
    return {
      ...multiDirect,
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  // PATCH_24_REV_A:
  // Explicit handoff commands must be evaluated before direct vocatives.
  // "Orion, chame a Chris" means Chris receives the turn; Orion is the addressed
  // current speaker, not the response target.
  for (const profile of profiles) {
    const command = classifyProfileCommandAddress(normalized, profile);
    if (command) {
      return {
        ...command,
        target_agent_slug: command.slug,
        registry_version: AGENT_REGISTRY_VERSION,
        router_version: TURN_ROUTER_VERSION,
      };
    }
  }

  for (const profile of profiles) {
    const direct = classifyProfileDirectAddress(normalized, profile);
    if (direct) {
      return {
        ...direct,
        target_agent_slug: direct.slug,
        registry_version: AGENT_REGISTRY_VERSION,
        router_version: TURN_ROUTER_VERSION,
      };
    }
  }

  const mentions = [];
  for (const profile of profiles) {
    const mention = classifyProfileMention(normalized, profile);
    if (mention) mentions.push(mention);
  }
  if (mentions.length) {
    return {
      ...mentions[0],
      target_agent_slug: null,
      mentioned_agent_slug: mentions[0].slug,
      mentioned_agents: mentions.map((item) => item.slug),
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  const topics = [];
  for (const profile of profiles) {
    const topic = classifyProfileTopic(normalized, profile);
    if (topic) topics.push(topic);
  }
  if (topics.length) {
    return {
      ...topics[0],
      target_agent_slug: null,
      topic_agent_slug: topics[0].slug,
      topic_agents: topics.map((item) => item.slug),
      registry_version: AGENT_REGISTRY_VERSION,
      router_version: TURN_ROUTER_VERSION,
    };
  }

  return {
    match_type: "none",
    target_agent_slug: null,
    display_name: "",
    confidence: 0,
    registry_version: AGENT_REGISTRY_VERSION,
    router_version: TURN_ROUTER_VERSION,
  };
}

export function resolveAgentTurnRouteFromMessage(rawMessage = "", { includeInternal = true } = {}) {
  const classified = classifyAgentTurnFromMessage(rawMessage, { includeInternal });
  if (![
    "direct_address",
    "command_address",
    "multi_agent_address",
    "multi_command_address",
    "team_panel",
  ].includes(classified?.match_type)) {
    return null;
  }

  const slugs = uniqueAgentSlugs(
    classified.target_agent_slugs ||
    [classified.target_agent_slug || classified.slug].filter(Boolean)
  );

  return {
    slug: slugs[0] || classified.target_agent_slug || classified.slug || null,
    display_name: classified.display_name,
    display_names: classified.display_names || (classified.display_name ? [classified.display_name] : []),
    match_type: classified.match_type,
    route_reason: classified.route_reason,
    confidence: classified.confidence,
    target_agent_slug: slugs[0] || classified.target_agent_slug || null,
    target_agent_slugs: slugs,
    multi_agent_turn: Boolean(classified.multi_agent_turn || slugs.length > 1 || classified.match_type === "team_panel"),
    response_control: classified.response_control || (slugs.length > 1 ? "sequenced_team_turns" : "single_turn"),
    registry_version: AGENT_REGISTRY_VERSION,
    router_version: classified.router_version,
  };
}

export function resolveDirectAgentAddressFromMessage(rawMessage = "", { includeInternal = true } = {}) {
  const route = resolveAgentTurnRouteFromMessage(rawMessage, { includeInternal });
  if (!route) return null;
  return {
    slug: route.target_agent_slug || route.slug,
    display_name: route.display_name,
    display_names: route.display_names,
    match_type: route.match_type,
    route_reason: route.route_reason,
    confidence: route.confidence,
    target_agent_slug: route.target_agent_slug,
    target_agent_slugs: route.target_agent_slugs,
    multi_agent_turn: route.multi_agent_turn,
    response_control: route.response_control,
    registry_version: AGENT_REGISTRY_VERSION,
    router_version: route.router_version,
  };
}

export function findAgentByCanonicalSlug(agents = [], value = "") {
  const wantedSlug = canonicalAgentSlug(value, { allowUnknown: false });
  if (!wantedSlug) return null;

  return (agents || []).find((agent) => {
    const candidates = [
      agent?.id,
      agent?.name,
      agent?.slug,
      agent?.key,
      agent?.code,
      agent?.agent_id,
      agent?.agent_slug,
    ].filter(Boolean);

    return candidates.some((candidate) => canonicalAgentSlug(candidate, { allowUnknown: true }) === wantedSlug);
  }) || null;
}

export function serializeAgentRegistryForDiagnostics({ includeInternal = true } = {}) {
  return Object.values(CANONICAL_AGENT_REGISTRY)
    .filter((profile) => includeInternal || !profile.internal)
    .map((profile) => ({
      slug: profile.slug,
      display_name: profile.display_name,
      role_label: profile.role_label,
      route_role: profile.route_role,
      public_beta_allowed: Boolean(profile.public_beta_allowed),
      internal: Boolean(profile.internal),
      public_agent: Boolean(profile.public_agent),
      internal_agent: Boolean(profile.internal_agent ?? profile.internal),
      team_default: Boolean(profile.team_default),
      team_optional: Boolean(profile.team_optional),
      persona_scope: profile.persona_scope || "",
      persona_guardrails: Array.from(profile.persona_guardrails || []),
      aliases: Array.from(profile.aliases || []),
      domain_keywords: Array.from(profile.domain_keywords || []),
    }));
}
