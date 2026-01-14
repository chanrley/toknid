// ### Script principal ToknId – clientes
// cuida do menu mobile, painel lateral do cliente e placeholders das ações

window.toknUI = (function () {
  // ---------- PAINEL LATERAL (DETALHES CLIENTE) ----------
  const overlaySel = ".tokn-overlay";
  const panelSel = ".tokn-panel";
  const avatarSel = "#tokn-avatar";
  const titleSel = "#tokn-panel-title";

  function togglePanel(open) {
    const overlay = document.querySelector(overlaySel);
    const panel = document.querySelector(panelSel);
    if (!overlay || !panel) return;

    const shouldOpen =
      typeof open === "boolean" ? open : !panel.classList.contains("is-open");

    if (shouldOpen) {
      panel.classList.add("is-open");
      overlay.classList.add("is-open");
      panel.setAttribute("aria-hidden", "false");
    } else {
      panel.classList.remove("is-open");
      overlay.classList.remove("is-open");
      panel.setAttribute("aria-hidden", "true");
    }
  }

  function openPanel(nome) {
    const avatar = document.querySelector(avatarSel);
    const title = document.querySelector(titleSel);

    if (title && nome) {
      title.textContent = nome;
    }

    if (avatar && nome) {
      const iniciais = nome
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((p) => p[0].toUpperCase())
        .join("");
      avatar.textContent = iniciais || "CL";
    }

    togglePanel(true);
  }

  function closePanel() {
    togglePanel(false);
  }

  // ---------- AÇÕES DE BOTÃO (PLACEHOLDER) ----------
  function newClient() {
    console.log("Novo Cliente – conectar depois com o form real.");
    alert("Ação 'Novo Cliente' ainda será conectada ao backend.");
  }

  function exportCsv() {
    console.log("Exportar CSV – conectar depois com backend.");
    alert("Ação 'Exportar CSV' ainda será conectada ao backend.");
  }

  function search(form) {
    const q = form.q?.value || "";
    console.log("Buscar clientes:", q);
    // impede submit real por enquanto
    return false;
  }

  function filter(tipo) {
    console.log("Filtro selecionado:", tipo);
  }

  // ---------- MENU MOBILE (HAMBÚRGUER) ----------
  function setupNav() {
    const shell = document.querySelector(".tokn-shell");
    const toggle = document.getElementById("toknNavToggle");
    const avatarSm = document.querySelector(".tokn-nav-avatar-sm");

    if (!shell || (!toggle && !avatarSm)) return;

    const handler = function () {
      const isOpen = shell.classList.toggle("is-nav-open");
      if (toggle) {
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      }
    };

    if (toggle) toggle.addEventListener("click", handler);
    if (avatarSm) avatarSm.addEventListener("click", handler);
  }

  // ============================================================
  // MODAIS GERAIS
  // ============================================================

  function getModals() {
    return {
      overlay: document.getElementById("toknModalOverlay"),
      credit: document.getElementById("toknCreditModal"),
      novo: document.getElementById("toknNewClientModal"),
      campaign: document.getElementById("toknCampaignModal"),
      success: document.getElementById("toknSuccessModal"),
    };
  }

  function openCreditModal() {
    const { overlay, credit, novo, campaign, success } = getModals();
    if (!overlay || !credit) return;

    // garante que só um modal fique aberto
    if (novo) novo.classList.remove("is-open");
    if (campaign) campaign.classList.remove("is-open");
    if (success) success.classList.remove("is-open");

    overlay.classList.add("is-open");
    credit.classList.add("is-open");
  }

  function openNewClientModal() {
    const { overlay, credit, novo, campaign, success } = getModals();
    if (!overlay || !novo) return;

    if (credit) credit.classList.remove("is-open");
    if (campaign) campaign.classList.remove("is-open");
    if (success) success.classList.remove("is-open");

    overlay.classList.add("is-open");
    novo.classList.add("is-open");
  }

  // 🔥 novo: modal de Criar campanha
  function openCampaignModal() {
    const { overlay, credit, novo, campaign, success } = getModals();
    if (!overlay || !campaign) return;

    if (credit) credit.classList.remove("is-open");
    if (novo) novo.classList.remove("is-open");
    if (success) success.classList.remove("is-open");

    overlay.classList.add("is-open");
    campaign.classList.add("is-open");
  }

  function openSuccessModal(signature, explorerUrl) {
    const { overlay, credit, novo, campaign, success } = getModals();
    if (!overlay || !success) return;

    // Fechar outros modais
    if (credit) credit.classList.remove("is-open");
    if (novo) novo.classList.remove("is-open");
    if (campaign) campaign.classList.remove("is-open");

    // Atualizar conteúdo do modal
    const signatureEl = document.getElementById("tokn-success-signature");
    const explorerEl = document.getElementById("tokn-success-explorer");
    if (signatureEl) signatureEl.textContent = signature || "-";
    if (explorerEl) {
      if (explorerUrl) {
        explorerEl.href = explorerUrl;
        explorerEl.style.display = "inline-flex";
      } else {
        explorerEl.style.display = "none";
      }
    }

    // Abrir modal
    overlay.classList.add("is-open");
    success.classList.add("is-open");
  }

  function closeModals() {
    const { overlay, credit, novo, campaign, success } = getModals();
    if (overlay) overlay.classList.remove("is-open");
    if (credit) credit.classList.remove("is-open");
    if (novo) novo.classList.remove("is-open");
    if (campaign) campaign.classList.remove("is-open");
    if (success) success.classList.remove("is-open");
  }

  // Tabs do modal "Novo Cliente"
  function initNewClientTabs() {
    const tabs = document.querySelectorAll("[data-newclient-tab]");
    const panes = document.querySelectorAll("[data-newclient-pane]");

    if (!tabs.length || !panes.length) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const target = tab.getAttribute("data-newclient-tab");

        tabs.forEach((t) => t.classList.toggle("is-active", t === tab));
        panes.forEach((p) =>
          p.classList.toggle(
            "is-active",
            p.getAttribute("data-newclient-pane") === target
          )
        );
      });
    });
  }

  // Helper bonitão de "em breve"
  function soon(feature) {
    console.log("Tokn.id – em breve:", feature);
    alert(feature + " será ativado nas próximas versões.");
  }

  // ============================================================
  // CREDITAR MOEDAS – INTEGRAÇÃO COM API
  // ============================================================

  // Configuração da API - usa variável injetada pelo Django ou fallback
  // Prioridade: window.API_BASE_URL (injetado pelo Django) > window.location.origin (inclui porta)
  const API_BASE_URL = window.API_BASE_URL || window.location.origin;

  // Chave privada temporária (será movida para configuração do Flask)
  const CHAVE_PRIVADA_TEMP = '5kFHkRRJe4Zqu7zsuVmokgWsDMGaAi4yi6A6DFeKfh6qNqaT5KJmsVY6v8Wz93H5mjaBtovnr9Q9PZ7cHjd8sPVk';

  // Taxa de conversão: moedas para SOL (1 moeda = 0.001 SOL)
  // TODO: Definir regra de conversão real conforme regra de negócio
  const MOEDAS_POR_SOL = 1000; // 1 SOL = 1000 moedas

  async function creditarMoedas() {
    console.log('creditarMoedas() chamada');
    const walletInput = document.getElementById('tokn-wallet-input');
    const moedasInput = document.getElementById('tokn-moedas');
    
    const carteiraDestino = walletInput?.value?.trim();
    const moedas = parseFloat(moedasInput?.value);
    
    // Validações
    if (!carteiraDestino) {
      alert('Por favor, informe o endereço da carteira Phantom do cliente.');
      if (walletInput) walletInput.focus();
      return;
    }
    
    if (!moedas || moedas <= 0 || isNaN(moedas)) {
      alert('Por favor, informe a quantidade de moedas a creditar (valor maior que zero).');
      if (moedasInput) moedasInput.focus();
      return;
    }
    
    // Converter moedas para SOL
    const valorSOL = moedas / MOEDAS_POR_SOL;
    
    // Desabilitar botão durante requisição
    const confirmBtn = document.querySelector('#toknCreditModal .tokn-btn--primary');
    const originalText = confirmBtn?.textContent;
    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.textContent = 'Processando...';
    }
    
    try {
      const requestBody = {
        chave_privada: CHAVE_PRIVADA_TEMP,
        carteira_destino: carteiraDestino,
        valor_minimo: false,
        valor: valorSOL
      };
      const requestUrl = `${API_BASE_URL}/creditar-moedas/`;
      
      // #region agent log
      fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:234',message:'Antes da requisição fetch',data:{API_BASE_URL,requestUrl,requestBody:{...requestBody,chave_privada:'[REDACTED]'}},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      // #region agent log
      fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:243',message:'Resposta recebida',data:{status:response.status,statusText:response.statusText,ok:response.ok,headers:Object.fromEntries(response.headers.entries())},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      
      // Verificar content-type antes de fazer parse
      const contentType = response.headers.get('content-type') || '';
      let data;
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        // Se não for JSON, ler como texto para ver o erro
        const textResponse = await response.text();
        // #region agent log
        fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:252',message:'Resposta não é JSON',data:{contentType,textPreview:textResponse.substring(0,2000)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
        // Tentar extrair mensagem de erro do HTML do Django
        const errorTitleMatch = textResponse.match(/<title>(.*?)<\/title>/);
        const errorTypeMatch = textResponse.match(/<h1>(.*?)<\/h1>/);
        const errorValueMatch = textResponse.match(/<pre[^>]*>(.*?)<\/pre>/s);
        const errorTraceMatch = textResponse.match(/<pre[^>]*class="python"[^>]*>(.*?)<\/pre>/s);
        
        let errorDetails = {
          title: errorTitleMatch ? errorTitleMatch[1] : 'Erro desconhecido',
          type: errorTypeMatch ? errorTypeMatch[1] : 'Erro interno',
          value: errorValueMatch ? errorValueMatch[1].substring(0, 500) : 'Sem detalhes',
          trace: errorTraceMatch ? errorTraceMatch[1].substring(0, 1000) : 'Sem traceback'
        };
        
        // #region agent log
        fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:265',message:'Detalhes do erro extraídos do HTML',data:errorDetails,timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
        
        throw new Error(`Erro do servidor: ${errorDetails.type} - ${errorDetails.value.substring(0, 200)}`);
      }
      
      // #region agent log
      fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:260',message:'Dados parseados da resposta',data,timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      if (response.ok && data.sucesso) {
        closeModals();
        // Limpar campos
        if (walletInput) walletInput.value = '';
        if (moedasInput) moedasInput.value = '';
        // Abrir modal de sucesso
        openSuccessModal(data.signature, data.explorer);
      } else {
        const erroMsg = data.erro || data.message || 'Erro desconhecido';
        // #region agent log
        fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:254',message:'Resposta com erro',data:{status:response.status,erroMsg,data},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        alert(`Erro ao creditar moedas: ${erroMsg}`);
      }
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7249/ingest/dab86f37-fc48-474b-a390-aff1ce5adac2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'clientes.js:257',message:'Erro capturado no catch',data:{errorName:error?.name,errorMessage:error?.message,errorStack:error?.stack,API_BASE_URL,requestUrl:`${API_BASE_URL}/creditar-moedas`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      console.error('Erro ao creditar moedas:', error);
      alert('Erro ao conectar com a API. Verifique se o servidor está rodando em ' + API_BASE_URL);
    } finally {
      // Reabilitar botão
      if (confirmBtn) {
        confirmBtn.disabled = false;
        if (originalText) confirmBtn.textContent = originalText;
      }
    }
  }

  // ============================================================
  // CLIENTE IDENTIFICADO – BLOCO NO MODAL DE CRÉDITO
  // ============================================================

  function setFoundClient(data) {
    const block = document.getElementById("toknFoundClient");
    const avatar = document.getElementById("toknFoundAvatar");
    const nameEl = document.getElementById("toknFoundName");
    const metaEl = document.getElementById("toknFoundMeta");
    const extraEl = document.getElementById("toknFoundExtra");
    const statusEl = document.getElementById("toknFoundStatus");

    if (!block) return;

    const nome = data?.nome || "Cliente sem nome";
    const telefone = data?.telefone || "";
    const email = data?.email || "";
    const canal = data?.canal || "";
    const vip = !!data?.vip;
    const idTokn = data?.idTokn || "";

    // Nome
    if (nameEl) nameEl.textContent = nome;

    // Contato
    const metaParts = [];
    if (telefone) metaParts.push(telefone);
    if (email) metaParts.push(email);
    if (metaEl) {
      metaEl.textContent =
        metaParts.join(" · ") || "Dados de contato não informados";
    }

    // Extra
    const extraParts = [];
    if (canal) extraParts.push(`Canal principal: ${canal}`);
    if (vip) extraParts.push("Cliente VIP");
    if (idTokn) extraParts.push(`ID Tokn: ${idTokn}`);
    if (extraEl) extraEl.textContent = extraParts.join(" · ");

    // Avatar com iniciais
    if (avatar) {
      const iniciais = nome
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((p) => p[0].toUpperCase())
        .join("");
      avatar.textContent = iniciais || "CL";
    }

    // Status
    if (statusEl) {
      statusEl.textContent = "✓ Cliente identificado com sucesso";
    }

    // Exibe bloco
    block.classList.remove("is-hidden");
  }

  function clearFoundClient() {
    const block = document.getElementById("toknFoundClient");
    const nameEl = document.getElementById("toknFoundName");
    const metaEl = document.getElementById("toknFoundMeta");
    const extraEl = document.getElementById("toknFoundExtra");

    if (!block) return;

    block.classList.add("is-hidden");

    if (nameEl) nameEl.textContent = "Nome do cliente";
    if (metaEl)
      metaEl.textContent = "+55 (11) 98888-0000 · cliente@email.com";
    if (extraEl)
      extraEl.textContent =
        "Canal principal: WhatsApp · Cliente VIP · ID Tokn: CLT-000123";
  }

  // DEBUG: simula um cliente encontrado (pra você testar visualmente)
  function debugShowFoundClient() {
    setFoundClient({
      nome: "João Silva",
      telefone: "+55 (11) 98888-1111",
      email: "joao@email.com",
      canal: "PDV",
      vip: true,
      idTokn: "CLT-000123",
    });
  }

  // ============================================================
  // CAMPANHAS – PAINEL LATERAL (já existia, mantido)
  // ============================================================

  const campOverlaySel = ".tokn-camp-overlay";
  const campPanelSel = ".tokn-camp-panel";

  function toggleCampaignPanel(open) {
    const overlay = document.querySelector(campOverlaySel);
    const panel = document.querySelector(campPanelSel);
    if (!overlay || !panel) return;

    const shouldOpen =
      typeof open === "boolean" ? open : !panel.classList.contains("is-open");

    if (shouldOpen) {
      panel.classList.add("is-open");
      overlay.classList.add("is-open");
      panel.setAttribute("aria-hidden", "false");
    } else {
      panel.classList.remove("is-open");
      overlay.classList.remove("is-open");
      panel.setAttribute("aria-hidden", "true");
    }
  }

  function openCampaignPanel(nomeCampanha) {
    const titleEl = document.getElementById("tokn-camp-title");
    if (titleEl && nomeCampanha) {
      titleEl.textContent = nomeCampanha;
    }
    toggleCampaignPanel(true);
  }

  function closeCampaignPanel() {
    toggleCampaignPanel(false);
  }

  // Busca de campanhas (placeholder só para logar no console)
  function searchCampaigns(form) {
    const q = form.q?.value || "";
    console.log("Buscar campanhas:", q);
    return false;
  }

  // ---------- INIT ----------
  document.addEventListener("DOMContentLoaded", function () {
    setupNav();
    initNewClientTabs();
    
    // Adicionar event listener ao botão de confirmar crédito
    // Usar delegação de eventos para garantir que funcione mesmo se o modal não estiver no DOM
    document.addEventListener('click', function(e) {
      const target = e.target;
      if (target && target.id === 'tokn-confirm-credit-btn') {
        e.preventDefault();
        creditarMoedas();
      }
    });
  });

  // Expor API global usada no HTML
  const api = {
    openPanel,
    closePanel,
    newClient,
    exportCsv,
    search,
    filter,

    // Modais
    openCreditModal,
    openNewClientModal,
    openCampaignModal, // <- novo
    closeModals,
    soon,
    creditarMoedas,

    // Cliente identificado
    setFoundClient,
    clearFoundClient,
    debugShowFoundClient,

    // Campanhas – painel lateral
    openCampaignPanel,
    closeCampaignPanel,
    searchCampaigns,
  };
  
  return api;
})();
