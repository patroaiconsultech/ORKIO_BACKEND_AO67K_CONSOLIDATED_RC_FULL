--- AppConsole_RTB02_PATCHED.txt
+++ AppConsole_ASP01A_REALTIME_SELECTED_AGENT_MIN_PATCHED.txt
@@ -2074,26 +2074,27 @@
   return msg ? `${base} Mensagem do usuário: ${msg}` : base;
 }
 
-function buildRealtimeActivationProbeInstruction(languageProfile) {
+function buildRealtimeActivationProbeInstruction(languageProfile, agentName = "Orkio") {
   const lang = normalizeRealtimeLanguageProfile(languageProfile);
+  const safeAgentName = String(agentName || "Orkio").trim() || "Orkio";
 
   if (lang === "en") {
     return {
-      inputText: "Say only: Hello, I am Orkio in real time.",
-      instructions: "Answer by audio in English, saying only: Hello, I am Orkio in real time.",
+      inputText: `Say only: Hello, I am ${safeAgentName} in real time.`,
+      instructions: `Answer by audio in English, saying only: Hello, I am ${safeAgentName} in real time.`,
     };
   }
 
   if (lang === "es") {
     return {
-      inputText: "Di solamente: Hola, soy Orkio en tiempo real.",
-      instructions: "Responde en audio en español, diciendo solamente: Hola, soy Orkio en tiempo real.",
+      inputText: `Di solamente: Hola, soy ${safeAgentName} en tiempo real.`,
+      instructions: `Responde en audio en español, diciendo solamente: Hola, soy ${safeAgentName} en tiempo real.`,
     };
   }
 
   return {
-    inputText: "Diga apenas: Olá, eu sou o Orkio em tempo real.",
-    instructions: "Responda em áudio em português, dizendo apenas: Olá, eu sou o Orkio em tempo real.",
+    inputText: `Diga apenas: Olá, eu sou ${safeAgentName} em tempo real.`,
+    instructions: `Responda em áudio em português, dizendo apenas: Olá, eu sou ${safeAgentName} em tempo real.`,
   };
 }
 
@@ -3828,6 +3829,81 @@
     }
 
     return fallbackAgent?.id || null;
+  }
+
+  // ASP-01A_REALTIME_SELECTED_AGENT_PARITY
+  // Minimal parity bridge: Realtime must speak as the agent selected in the console.
+  // This intentionally does not touch thread loading, layout, context carryover, DB, or backend routing.
+  function resolveRealtimeSelectedAgentIdentity(agentIdOverride = null) {
+    const resolvedId = agentIdOverride || resolveHostAgentId();
+    const agent =
+      (agents || []).find((a) => String(a?.id || "") === String(resolvedId || "")) ||
+      (agents || []).find((a) => String(a?.name || "").trim().toLowerCase() === "orkio") ||
+      (agents || []).find((a) => a?.is_default) ||
+      (agents || [])[0] ||
+      null;
+
+    const rawName =
+      agent?.name ||
+      agent?.agent_name ||
+      agent?.display_name ||
+      agent?.slug ||
+      "Orkio";
+    const name = canonicalizeSpeakerLabel(rawName) || String(rawName || "Orkio").trim() || "Orkio";
+    const role =
+      String(
+        agent?.role ||
+        agent?.title ||
+        agent?.specialty ||
+        agent?.description ||
+        ""
+      ).trim();
+
+    return {
+      id: agent?.id || resolvedId || null,
+      slug: String(agent?.slug || agent?.key || name || "").trim().toLowerCase(),
+      name,
+      role,
+      agent,
+    };
+  }
+
+  function buildRealtimeSelectedAgentInstructions(agentIdentity, preferredLang = "auto") {
+    const identity = agentIdentity || resolveRealtimeSelectedAgentIdentity();
+    const agentName = String(identity?.name || "Orkio").trim() || "Orkio";
+    const role = String(identity?.role || "").trim();
+    const roleHint = role ? ` Papel/função do agente selecionado: ${role}.` : "";
+
+    if (preferredLang === "pt") {
+      return (
+        `Você é ${agentName} em tempo real. Responda como ${agentName}, o agente selecionado no console.` +
+        roleHint +
+        ` Não se apresente como Orkio quando o agente selecionado for ${agentName}.` +
+        " Comece falando primeiro. Mantenha a conversa focada na última resposta clara do usuário." +
+        " Faça uma pergunta curta por vez. Se o áudio estiver confuso, peça para o usuário repetir." +
+        " Não use saudações privadas ou marcadores internos."
+      );
+    }
+
+    if (preferredLang === "es") {
+      return (
+        `Eres ${agentName} en tiempo real. Responde como ${agentName}, el agente seleccionado en la consola.` +
+        roleHint +
+        ` No te presentes como Orkio cuando el agente seleccionado sea ${agentName}.` +
+        " Empieza hablando primero. Mantén la conversación enfocada en la última respuesta clara del usuario." +
+        " Haz una pregunta corta por vez. Si el audio no está claro, pide que el usuario repita." +
+        " No uses saludos privados ni marcadores internos."
+      );
+    }
+
+    return (
+      `You are ${agentName} in real time. Respond as ${agentName}, the agent selected in the console.` +
+      (role ? ` Selected agent role: ${role}.` : "") +
+      ` Do not introduce yourself as Orkio when the selected agent is ${agentName}.` +
+      " Start by speaking first. Keep the conversation focused on the user's last clear answer." +
+      " Ask one short question at a time. If the audio is unclear, ask the user to repeat." +
+      " Do not use private greetings or internal markers."
+    );
   }
 
 
@@ -7104,7 +7180,10 @@
           marker: ORKIO_AO66R_HF4_BUILD_MARKER,
         });
 
-        const probe = buildRealtimeActivationProbeInstruction(rtcLanguageProfileRef.current);
+        const probe = buildRealtimeActivationProbeInstruction(
+          rtcLanguageProfileRef.current,
+          resolveRealtimeSelectedAgentIdentity()?.name || "Orkio"
+        );
         requestRealtimeSpokenResponse(currentDc, {
           reason: "activation_probe",
           conversationItem: true,
@@ -7130,6 +7209,8 @@
     const durationLabel = formatRealtimeDurationLabel(maxSeconds);
     const lang = normalizeRealtimeLanguageProfile(rtcLanguageProfileRef.current);
     const limited = Boolean(isRealtimeTimeboxLimitedUser());
+    const realtimeAgentIdentity = resolveRealtimeSelectedAgentIdentity();
+    const realtimeAgentName = String(realtimeAgentIdentity?.name || "Orkio").trim() || "Orkio";
 
     // AO72D-HF1: greeting first, timer phrase second. The countdown starts only
     // when the assistant transcript reaches "two minutes", after the greeting.
@@ -7137,19 +7218,19 @@
       lang === "en"
         ? (
           limited
-            ? `Hello, I am Orkio. It is a pleasure to speak with you in real time. We have ${durationLabel} of conversation starting now. Where would you like to begin?`
-            : "Hello, I am Orkio. It is a pleasure to speak with you in real time. Where would you like to begin?"
+            ? `Hello, I am ${realtimeAgentName}. It is a pleasure to speak with you in real time. We have ${durationLabel} of conversation starting now. Where would you like to begin?`
+            : `Hello, I am ${realtimeAgentName}. It is a pleasure to speak with you in real time. Where would you like to begin?`
         )
         : lang === "es"
           ? (
             limited
-              ? `Hola, soy Orkio. Es un placer hablar contigo en tiempo real. Tenemos ${durationLabel} de conversación a partir de ahora. ¿Por dónde quieres empezar?`
-              : "Hola, soy Orkio. Es un placer hablar contigo en tiempo real. ¿Por dónde quieres empezar?"
+              ? `Hola, soy ${realtimeAgentName}. Es un placer hablar contigo en tiempo real. Tenemos ${durationLabel} de conversación a partir de ahora. ¿Por dónde quieres empezar?`
+              : `Hola, soy ${realtimeAgentName}. Es un placer hablar contigo en tiempo real. ¿Por dónde quieres empezar?`
           )
           : (
             limited
-              ? `Olá, eu sou Orkio. Prazer em falar com você em tempo real. Temos ${durationLabel} de conversa a partir de agora. Por onde você quer começar?`
-              : "Olá, eu sou Orkio. Prazer em falar com você em tempo real. Por onde você quer começar?"
+              ? `Olá, eu sou ${realtimeAgentName}. Prazer em falar com você em tempo real. Temos ${durationLabel} de conversa a partir de agora. Por onde você quer começar?`
+              : `Olá, eu sou ${realtimeAgentName}. Prazer em falar com você em tempo real. Por onde você quer começar?`
           );
 
     const activationInput =
@@ -7167,6 +7248,8 @@
       hf6_2Marker: ORKIO_HF6_2_BUILD_MARKER,
       nonAdminPublicTimebox: Boolean(limited),
       greetingBeforeTimer: true,
+      selectedAgentName: realtimeAgentName,
+      selectedAgentId: realtimeAgentIdentity?.id || null,
     });
 
     if (limited && !rtcTimeboxStartedRef.current) {
@@ -7299,8 +7382,9 @@
       const magicEnabled = (ORKIO_ENV.VITE_REALTIME_MAGICWORDS || import.meta.env.VITE_REALTIME_MAGICWORDS || "true").toString().trim().toLowerCase() !== "false";
       rtcMagicEnabledRef.current = magicEnabled;
 
-      // Voice priority: agent.voice_id (Admin) > env default > fallback Orkio warmth preset
-      const selectedAgentObj = (agents || []).find(a => String(a.id) === String(agentIdToSend));
+      // Voice priority: selected agent voice_id (Admin) > env default > fallback voice preset
+      const realtimeAgentIdentity = resolveRealtimeSelectedAgentIdentity(agentIdToSend);
+      const selectedAgentObj = realtimeAgentIdentity?.agent || null;
       const agentVoice = ((selectedAgentObj?.voice_id || selectedAgentObj?.voice || selectedAgentObj?.tts_voice || selectedAgentObj?.voiceId || "")).toString().trim();
       const rtVoice = coerceVoiceId(agentVoice || envVoice || ORKIO_DEFAULT_VOICE_ID);
       rtcVoiceRef.current = rtVoice;
@@ -7343,7 +7427,11 @@
         onboardingLanguage,
         languageProfile,
       });
-      logRealtimeStep('start:session_ok', start);
+      logRealtimeStep('start:session_ok', {
+        ...(start || {}),
+        selected_agent_id: realtimeAgentIdentity?.id || agentIdToSend || null,
+        selected_agent_name: realtimeAgentIdentity?.name || null,
+      });
       // ORKIO_AO60K_HF5B_FRONTEND_ENDED_AT_SECONDS_TIMEBOX_VERIFY
       // Runtime proof: confirms the active bundle received backend timebox policy.
       try {
@@ -7709,7 +7797,7 @@
           }
           setRtcTimeboxRemaining(rtcPendingTimeboxSecondsRef.current || activeTimeboxSeconds);
         } else {
-          setUploadStatus('⚡ Orkio em tempo real ativo.');
+          setUploadStatus(`⚡ ${realtimeAgentIdentity?.name || "Agente"} em tempo real ativo.`);
           setTimeout(() => setUploadStatus(''), 1500);
           rtcPendingTimeboxSecondsRef.current = null;
           clearRealtimeTimeboxTimer();
@@ -7746,14 +7834,10 @@
           const transcription = { model: transcriptionModel };
           if (langHint) transcription.language = langHint;
 
-          const realtimeInstructions =
-            preferredLang === "en"
-              ? "You are Orkio in real time. Start by speaking first. Keep the conversation focused on the user's last clear answer. Ask one short question at a time. If the audio is unclear, ask the user to repeat."
-              : preferredLang === "es"
-                ? "Eres Orkio en tiempo real. Empieza hablando primero. Mantén la conversación enfocada en la última respuesta clara del usuario. Haz una pregunta corta por vez. Si el audio no está claro, pide que el usuario repita."
-                : preferredLang === "pt"
-                  ? "Você é Orkio em tempo real. Comece falando primeiro. Mantenha a conversa focada na última resposta clara do usuário. Faça uma pergunta curta por vez. Se o áudio estiver confuso, peça para o usuário repetir."
-                  : "You are Orkio in real time. Start by speaking first. Answer in the same language the user is using. Keep the conversation focused and ask one short question at a time.";
+          const realtimeInstructions = buildRealtimeSelectedAgentInstructions(
+            realtimeAgentIdentity,
+            preferredLang
+          );
 
           try {
             console.log("REALTIME_TRANSCRIPTION_LANGUAGE", {
@@ -7765,6 +7849,8 @@
               vadThreshold: REALTIME_SERVER_VAD_THRESHOLD,
               vadSilenceMs: REALTIME_SERVER_VAD_SILENCE_MS,
               vadPrefixMs: REALTIME_SERVER_VAD_PREFIX_MS,
+              selectedAgentId: realtimeAgentIdentity?.id || null,
+              selectedAgentName: realtimeAgentIdentity?.name || null,
             });
           } catch {}
 
@@ -8830,11 +8916,13 @@
     queueRealtimeEvent({ event_type: 'response.final', role: 'assistant', content: finalText, is_final: true, meta: { source, hf4: true, upgraded: isMeaningfulUpgrade } });
 
     try {
-      const selectedAgentObj2 = (agents || []).find(a => String(a.id) === String(destSingle || ""));
-      // AO64D-HF5_PUBLIC_REALTIME_SPEAKER_ORKIO
+      const agentIdentity2 = resolveRealtimeSelectedAgentIdentity();
+      const selectedAgentObj2 = agentIdentity2?.agent || (agents || []).find(a => String(a.id) === String(destSingle || ""));
+      // ASP-01A_REALTIME_SELECTED_AGENT_PARITY:
       // Runtime source labels like "response.done:longest" are telemetry, not public speaker names.
-      const agentName2 = "Orkio";
-      const agentId2 = selectedAgentObj2?.id || (destSingle || null);
+      // The visible assistant speaker must follow the selected console agent.
+      const agentName2 = agentIdentity2?.name || selectedAgentObj2?.name || "Orkio";
+      const agentId2 = selectedAgentObj2?.id || agentIdentity2?.id || (destSingle || null);
 
       if (isMeaningfulUpgrade && existingMessageId) {
         setMessages((prev) => (prev || []).map((m) => (
