const formatarReais = (valor) =>
  valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

// Avisos: fechar no botão e sumir sozinhos depois de alguns segundos
document.querySelectorAll(".aviso").forEach((aviso) => {
  const fechar = () => {
    aviso.classList.add("saindo");
    setTimeout(() => aviso.remove(), 300);
  };
  aviso.querySelector(".aviso-fechar").addEventListener("click", fechar);
  setTimeout(fechar, 4000);
});

// Busca instantânea: filtra as linhas enquanto digita
const busca = document.getElementById("busca");
const tabela = document.getElementById("tabela-produtos");
if (busca && tabela) {
  const semResultados = document.getElementById("sem-resultados");
  busca.addEventListener("input", () => {
    const termo = busca.value.trim().toLowerCase();
    let visiveis = 0;
    tabela.querySelectorAll("tbody tr").forEach((linha) => {
      const mostra = linha.dataset.nome.includes(termo);
      linha.hidden = !mostra;
      if (mostra) visiveis++;
    });
    semResultados.hidden = visiveis > 0;
  });
}

// Ordenação ao clicar no cabeçalho da tabela
if (tabela) {
  const cabecalhos = tabela.querySelectorAll("th[data-ordenar]");
  cabecalhos.forEach((th) => {
    th.addEventListener("click", () => {
      const indice = th.cellIndex;
      const numerico = th.dataset.ordenar === "numero";
      const direcao = th.dataset.direcao === "asc" ? "desc" : "asc";
      cabecalhos.forEach((outro) => delete outro.dataset.direcao);
      th.dataset.direcao = direcao;

      const corpo = tabela.tBodies[0];
      const linhas = Array.from(corpo.rows);
      linhas.sort((a, b) => {
        const va = a.cells[indice].dataset.valor;
        const vb = b.cells[indice].dataset.valor;
        const comparacao = numerico
          ? Number(va) - Number(vb)
          : va.localeCompare(vb, "pt-BR", { sensitivity: "base" });
        return direcao === "asc" ? comparacao : -comparacao;
      });
      linhas.forEach((linha) => corpo.appendChild(linha));
    });
  });
}

// Confirmação antes de remover
const dialogo = document.getElementById("dialogo-remover");
if (dialogo) {
  let formPendente = null;
  document.querySelectorAll(".form-remover").forEach((form) => {
    form.addEventListener("submit", (evento) => {
      evento.preventDefault();
      formPendente = form;
      document.getElementById("dialogo-nome").textContent = form.dataset.nome;
      dialogo.showModal();
    });
  });
  dialogo.addEventListener("close", () => {
    if (dialogo.returnValue === "confirmar" && formPendente) formPendente.submit();
    formPendente = null;
  });
}

// Formulário: botões + / − do estoque e prévia do valor total
const estoque = document.getElementById("estoque");
const preco = document.getElementById("preco");
if (estoque && preco) {
  const previa = document.getElementById("previa-total");
  const atualizarPrevia = () => {
    const p = parseFloat(preco.value.replace(",", ".")) || 0;
    const e = parseInt(estoque.value, 10) || 0;
    previa.textContent = formatarReais(Math.max(p, 0) * Math.max(e, 0));
  };
  document.querySelectorAll("[data-passo]").forEach((botao) => {
    botao.addEventListener("click", () => {
      const atual = parseInt(estoque.value, 10) || 0;
      estoque.value = Math.max(0, atual + Number(botao.dataset.passo));
      atualizarPrevia();
    });
  });
  preco.addEventListener("input", atualizarPrevia);
  estoque.addEventListener("input", atualizarPrevia);
  atualizarPrevia();
}
