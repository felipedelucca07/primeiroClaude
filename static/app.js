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

const grade = document.getElementById("grade-produtos");

// Busca instantânea: na página de produtos, filtra os cartões enquanto digita
const busca = document.getElementById("busca");
if (busca && grade) {
  const semResultados = document.getElementById("sem-resultados");
  const contagem = document.getElementById("contagem");
  busca.addEventListener("input", () => {
    const termo = busca.value.trim().toLowerCase();
    let visiveis = 0;
    grade.querySelectorAll(".produto").forEach((cartao) => {
      const mostra = cartao.dataset.nome.includes(termo);
      cartao.hidden = !mostra;
      if (mostra) visiveis++;
    });
    semResultados.hidden = visiveis > 0;
    contagem.textContent = `${visiveis} resultado${visiveis === 1 ? "" : "s"}`;
  });
}

// Ordenação pelo seletor "Ordenar por"
const ordenar = document.getElementById("ordenar");
if (ordenar && grade) {
  const criterios = {
    recentes: (a, b) => b.dataset.id - a.dataset.id,
    "menor-preco": (a, b) => a.dataset.preco - b.dataset.preco,
    "maior-preco": (a, b) => b.dataset.preco - a.dataset.preco,
    nome: (a, b) =>
      a.dataset.nome.localeCompare(b.dataset.nome, "pt-BR", { sensitivity: "base" }),
    estoque: (a, b) => a.dataset.estoque - b.dataset.estoque,
  };
  const aplicarOrdem = () => {
    const cartoes = Array.from(grade.children);
    cartoes.sort(criterios[ordenar.value]);
    cartoes.forEach((cartao) => grade.appendChild(cartao));
  };
  ordenar.addEventListener("change", aplicarOrdem);
  aplicarOrdem();
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

// Formulário: prévia da foto escolhida (clique ou arrastar e soltar)
const campoImagem = document.getElementById("imagem");
if (campoImagem) {
  const area = document.getElementById("upload");
  const previaFoto = document.getElementById("upload-previa");
  const textoUpload = document.getElementById("upload-texto");
  const removerFoto = document.getElementById("remover-imagem");
  const fotoOriginal = previaFoto.getAttribute("src");

  const mostrar = (src) => {
    previaFoto.src = src || "";
    previaFoto.hidden = !src;
    textoUpload.hidden = Boolean(src);
  };

  campoImagem.addEventListener("change", () => {
    const arquivo = campoImagem.files[0];
    if (arquivo) {
      mostrar(URL.createObjectURL(arquivo));
      if (removerFoto) removerFoto.checked = false;
    } else {
      mostrar(fotoOriginal);
    }
  });

  if (removerFoto) {
    removerFoto.addEventListener("change", () => {
      if (removerFoto.checked) {
        campoImagem.value = "";
        mostrar("");
      } else {
        mostrar(fotoOriginal);
      }
    });
  }

  ["dragenter", "dragover"].forEach((tipo) =>
    area.addEventListener(tipo, () => area.classList.add("arrastando"))
  );
  ["dragleave", "drop"].forEach((tipo) =>
    area.addEventListener(tipo, () => area.classList.remove("arrastando"))
  );
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
